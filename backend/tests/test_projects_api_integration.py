from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models.scan import ScanResult, TestableObject as DomObject


def _result(*objects: DomObject) -> ScanResult:
    counts: dict[str, int] = {}
    for obj in objects:
        counts[obj.object_type] = counts.get(obj.object_type, 0) + 1
    return ScanResult(
        url="https://example.com/current",
        title="API Integration Demo",
        total_testable_objects=len(objects),
        object_counts=counts,
        testable_objects=list(objects),
    )


def test_project_http_baseline_current_compare(monkeypatch) -> None:
    baseline = _result(
        DomObject(index=0, object_type="button", tag_name="button", id="save", text="Save", locator="#save"),
        DomObject(index=1, object_type="input", tag_name="input", id="email", type="email", required=False, locator="#email"),
    )
    current = _result(
        DomObject(index=0, object_type="button", tag_name="button", id="save", text="Save", disabled=True, locator="#save"),
        DomObject(index=1, object_type="input", tag_name="input", id="email", type="email", required=True, locator="#email"),
    )
    responses = iter([baseline, current])

    async def fake_scan_page(_request):
        return next(responses)

    monkeypatch.setattr("app.services.projects.scan_page", fake_scan_page)

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        with Session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            created = client.post(
                "/api/v1/projects",
                json={"name": "HTTP Integration Demo", "description": "End-to-end API flow", "base_url": "https://shop.example.com/app"},
            )
            assert created.status_code == 201
            assert created.json()["base_url"] == "https://shop.example.com/app"
            project_id = created.json()["id"]

            baseline_response = client.post(
                f"/api/v1/projects/{project_id}/scans",
                json={"url": "https://example.com", "role": "baseline"},
            )
            assert baseline_response.status_code == 201
            assert baseline_response.json()["role"] == "baseline"

            current_response = client.post(
                f"/api/v1/projects/{project_id}/scans",
                json={"url": "https://example.com", "role": "current"},
            )
            assert current_response.status_code == 201
            assert current_response.json()["role"] == "current"
            assert current_response.json()["route"] == "/current"

            routes_response = client.get(f"/api/v1/projects/{project_id}/routes")
            assert routes_response.status_code == 200
            assert routes_response.json() == ["/current"]

            overview_response = client.get(f"/api/v1/projects/{project_id}/release-overview")
            assert overview_response.status_code == 200
            overview = overview_response.json()
            assert overview["project_id"] == project_id
            assert overview["gate_status"] in {"READY", "BLOCKED"}
            assert overview["gate_reason"]
            assert overview["comparable_routes"] == 1
            assert overview["incomplete_routes"] == 0
            assert overview["routes"][0]["route"] == "/current"
            assert overview["routes"][0]["status"] == "READY"
            assert overview["routes"][0]["risk_score"] > 0

            comparison = client.get(f"/api/v1/projects/{project_id}/compare?route=/current")
            assert comparison.status_code == 200
            payload = comparison.json()
            assert len(payload["diff"]["changed"]) == 2
            assert payload["diff"]["added"] == []
            assert payload["diff"]["removed"] == []
            assert payload["risk"]["score"] > 0
            factor_codes = {factor["code"] for factor in payload["risk"]["factors"]}
            assert any("disabled" in code for code in factor_codes)
            assert any("required" in code for code in factor_codes)
            assert len(payload["regression_focus"]) == 2
            assert len(payload["regression_tests"]) == 2
            assert payload["regression_tests"][0]["id"] == "REG-001"

            json_export = client.get(f"/api/v1/projects/{project_id}/regression-tests/export?format=json&route=/current")
            assert json_export.status_code == 200
            assert "regression-tests.json" in json_export.headers["content-disposition"]
            assert len(json_export.json()) == 2

            markdown_export = client.get(f"/api/v1/projects/{project_id}/regression-tests/export?format=markdown&route=/current")
            assert markdown_export.status_code == 200
            assert "# AI Release Guardian" in markdown_export.text
            assert "REG-001" in markdown_export.text

            playwright_export = client.get(f"/api/v1/projects/{project_id}/regression-tests/export?format=playwright&route=/current")
            assert playwright_export.status_code == 200
            assert "regression.generated.spec.ts" in playwright_export.headers["content-disposition"]
            assert "import { test, expect } from '@playwright/test';" in playwright_export.text
            assert "REG-001" in playwright_export.text
            assert 'page.goto("https://example.com/current")' in playwright_export.text
            assert 'page.goto("https://shop.example.com/app")' not in playwright_export.text
            assert "toBeDisabled()" in playwright_export.text
            assert "toHaveJSProperty('required', true)" in playwright_export.text

            multi_route_export = client.get(f"/api/v1/projects/{project_id}/regression-tests/export?format=playwright")
            assert multi_route_export.status_code == 200
            assert "regression.multi-route.generated.spec.ts" in multi_route_export.headers["content-disposition"]
            assert 'test.describe("/current"' in multi_route_export.text
            assert 'page.goto("https://example.com/current")' in multi_route_export.text
            assert "toBeDisabled()" in multi_route_export.text

            invalid_export = client.get(f"/api/v1/projects/{project_id}/regression-tests/export?format=xml")
            assert invalid_export.status_code == 400
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_baseline_archiving_is_route_scoped(monkeypatch) -> None:
    def result(url: str) -> ScanResult:
        return ScanResult(
            url=url,
            title=url,
            total_testable_objects=1,
            object_counts={"button": 1},
            testable_objects=[
                DomObject(index=0, object_type="button", tag_name="button", id="save", text="Save", locator="#save")
            ],
        )

    responses = iter([
        result("https://example.com/login"),
        result("https://example.com/checkout"),
        result("https://example.com/login"),
    ])

    async def fake_scan_page(_request):
        return next(responses)

    monkeypatch.setattr("app.services.projects.scan_page", fake_scan_page)
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        with Session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            created = client.post("/api/v1/projects", json={"name": "Route Baseline Demo"})
            project_id = created.json()["id"]
            assert client.post(f"/api/v1/projects/{project_id}/scans", json={"url": "https://example.com/login", "role": "baseline"}).status_code == 201
            assert client.post(f"/api/v1/projects/{project_id}/scans", json={"url": "https://example.com/checkout", "role": "baseline"}).status_code == 201
            assert client.post(f"/api/v1/projects/{project_id}/scans", json={"url": "https://example.com/login", "role": "baseline"}).status_code == 201

            scans = client.get(f"/api/v1/projects/{project_id}/scans").json()
            login = [scan for scan in scans if scan["route"] == "/login"]
            checkout = [scan for scan in scans if scan["route"] == "/checkout"]
            assert sorted(scan["role"] for scan in login) == ["baseline", "history"]
            assert [scan["role"] for scan in checkout] == ["baseline"]
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_current_archiving_is_route_scoped(monkeypatch) -> None:
    def result(url: str) -> ScanResult:
        return ScanResult(
            url=url,
            title=url,
            total_testable_objects=1,
            object_counts={"button": 1},
            testable_objects=[
                DomObject(index=0, object_type="button", tag_name="button", id="save", text="Save", locator="#save")
            ],
        )

    responses = iter([
        result("https://example.com/login"),
        result("https://example.com/checkout"),
        result("https://example.com/login"),
    ])

    async def fake_scan_page(_request):
        return next(responses)

    monkeypatch.setattr("app.services.projects.scan_page", fake_scan_page)
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        with Session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            created = client.post("/api/v1/projects", json={"name": "Route Current Demo"})
            project_id = created.json()["id"]
            assert client.post(f"/api/v1/projects/{project_id}/scans", json={"url": "https://example.com/login", "role": "current"}).status_code == 201
            assert client.post(f"/api/v1/projects/{project_id}/scans", json={"url": "https://example.com/checkout", "role": "current"}).status_code == 201
            assert client.post(f"/api/v1/projects/{project_id}/scans", json={"url": "https://example.com/login", "role": "current"}).status_code == 201

            scans = client.get(f"/api/v1/projects/{project_id}/scans").json()
            login = [scan for scan in scans if scan["route"] == "/login"]
            checkout = [scan for scan in scans if scan["route"] == "/checkout"]
            assert sorted(scan["role"] for scan in login) == ["current", "history"]
            assert [scan["role"] for scan in checkout] == ["current"]
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_release_policy_is_persisted_and_changes_gate(monkeypatch) -> None:
    def result(url: str, disabled: bool) -> ScanResult:
        return ScanResult(
            url=url,
            title="Policy Demo",
            total_testable_objects=1,
            object_counts={"button": 1},
            testable_objects=[
                DomObject(index=0, object_type="button", tag_name="button", id="save", text="Save", locator="#save", disabled=disabled)
            ],
        )

    responses = iter([
        result("https://example.com/settings", False),
        result("https://example.com/settings", True),
    ])

    async def fake_scan_page(_request):
        return next(responses)

    monkeypatch.setattr("app.services.projects.scan_page", fake_scan_page)
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        with Session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            created = client.post("/api/v1/projects", json={"name": "Policy Demo"})
            project_id = created.json()["id"]
            assert client.post(f"/api/v1/projects/{project_id}/scans", json={"url": "https://example.com/settings", "role": "baseline"}).status_code == 201
            assert client.post(f"/api/v1/projects/{project_id}/scans", json={"url": "https://example.com/settings", "role": "current"}).status_code == 201

            updated = client.put(
                f"/api/v1/projects/{project_id}/release-policy",
                json={"block_on": "HIGH", "max_risk_score": 5, "require_all_routes": True},
            )
            assert updated.status_code == 200
            assert updated.json()["block_on"] == "HIGH"
            assert updated.json()["max_risk_score"] == 5
            assert updated.json()["require_all_routes"] is True

            loaded = client.get(f"/api/v1/projects/{project_id}")
            assert loaded.status_code == 200
            assert loaded.json()["block_on"] == "HIGH"
            assert loaded.json()["max_risk_score"] == 5

            overview = client.get(f"/api/v1/projects/{project_id}/release-overview")
            assert overview.status_code == 200
            assert overview.json()["gate_status"] == "BLOCKED"

            gate = client.get(f"/api/v1/projects/{project_id}/release-gate")
            assert gate.status_code == 200
            assert gate.json()["status"] == "BLOCKED"
            assert gate.json()["allowed"] is False
            assert gate.json()["exit_code"] == 1
            assert gate.json()["project_id"] == project_id
            assert gate.json()["reason"]
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_route_identity_preserves_query_and_ignores_fragment(monkeypatch) -> None:
    async def fake_scan_page(_request):
        return ScanResult(
            url="https://example.com/products?page=2#reviews",
            title="Products",
            total_testable_objects=1,
            object_counts={"button": 1},
            testable_objects=[
                DomObject(index=0, object_type="button", tag_name="button", id="buy", text="Buy", locator="#buy")
            ],
        )

    monkeypatch.setattr("app.services.projects.scan_page", fake_scan_page)
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        with Session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            created = client.post("/api/v1/projects", json={"name": "Query Route Demo"})
            project_id = created.json()["id"]
            scanned = client.post(
                f"/api/v1/projects/{project_id}/scans",
                json={"url": "https://example.com/products?page=2#reviews", "role": "current"},
            )
            assert scanned.status_code == 201
            assert scanned.json()["route"] == "/products?page=2"
            assert client.get(f"/api/v1/projects/{project_id}/routes").json() == ["/products?page=2"]
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_route_discovery_keeps_unique_same_origin_routes(monkeypatch) -> None:
    async def fake_capture_links(_url, _wait_until, _timeout_ms):
        return "https://example.com/", [
            "https://example.com/",
            "https://example.com/login",
            "https://example.com/products?page=2#reviews",
            "https://example.com/products?page=2#details",
            "http://example.com/insecure-downgrade",
            "https://other.example.com/external",
            "mailto:test@example.com",
        ]

    monkeypatch.setattr("app.services.projects.capture_links", fake_capture_links)
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        with Session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            created = client.post("/api/v1/projects", json={"name": "Discovery Demo"})
            project_id = created.json()["id"]
            discovered = client.post(
                f"/api/v1/projects/{project_id}/routes/discover",
                json={"url": "https://example.com/", "max_routes": 10},
            )
            assert discovered.status_code == 200
            assert discovered.json()["source_url"] == "https://example.com/"
            assert discovered.json()["routes"] == ["/", "/login", "/products?page=2"]
            assert discovered.json()["discovered_count"] == 3
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_batch_scan_continues_after_route_failure(monkeypatch) -> None:
    async def fake_scan_page(request):
        url = str(request.url)
        if "/broken" in url:
            raise RuntimeError("simulated route failure")
        return ScanResult(
            url=url,
            title="Batch Demo",
            total_testable_objects=1,
            object_counts={"button": 1},
            testable_objects=[
                DomObject(index=0, object_type="button", tag_name="button", id="ok", text="OK", locator="#ok")
            ],
        )

    monkeypatch.setattr("app.services.projects.scan_page", fake_scan_page)
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        with Session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            created = client.post("/api/v1/projects", json={"name": "Batch Scan Demo"})
            project_id = created.json()["id"]
            response = client.post(
                f"/api/v1/projects/{project_id}/scans/batch",
                json={
                    "base_url": "https://example.com/",
                    "routes": ["/login", "/broken", "/checkout"],
                    "role": "baseline",
                },
            )
            assert response.status_code == 200
            payload = response.json()
            assert payload["requested_count"] == 3
            assert payload["succeeded_count"] == 2
            assert payload["failed_count"] == 1
            assert [item["status"] for item in payload["results"]] == ["SUCCEEDED", "FAILED", "SUCCEEDED"]
            assert payload["results"][1]["error"] == "Scan failed for this route."
            assert payload["results"][1]["error_code"] == "SCAN_FAILED"
            scans = client.get(f"/api/v1/projects/{project_id}/scans").json()
            assert {scan["route"] for scan in scans} == {"/login", "/checkout"}
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_batch_scan_rejects_absolute_cross_origin_routes(monkeypatch) -> None:
    calls: list[str] = []

    async def fake_scan_page(request):
        calls.append(str(request.url))
        return ScanResult(
            url=str(request.url),
            title="Safe",
            total_testable_objects=0,
            object_counts={},
            testable_objects=[],
        )

    monkeypatch.setattr("app.services.projects.scan_page", fake_scan_page)
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        with Session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            created = client.post("/api/v1/projects", json={"name": "Batch Origin Guard"})
            project_id = created.json()["id"]
            response = client.post(
                f"/api/v1/projects/{project_id}/scans/batch",
                json={
                    "base_url": "https://example.com/",
                    "routes": ["/safe", "https://evil.example/escape"],
                    "role": "current",
                },
            )
            payload = response.json()
            assert response.status_code == 200
            assert payload["succeeded_count"] == 1
            assert payload["failed_count"] == 1
            assert payload["results"][1]["status"] == "FAILED"
            assert "relative same-origin" in payload["results"][1]["error"]
            assert calls == ["https://example.com/safe"]
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_release_gate_stays_incomplete_without_comparable_routes(monkeypatch) -> None:
    async def fake_scan_page(request):
        return ScanResult(
            url=str(request.url),
            title="Incomplete Demo",
            total_testable_objects=0,
            object_counts={},
            testable_objects=[],
        )

    monkeypatch.setattr("app.services.projects.scan_page", fake_scan_page)
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        with Session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            created = client.post("/api/v1/projects", json={"name": "Incomplete Gate Demo"})
            project_id = created.json()["id"]
            client.put(
                f"/api/v1/projects/{project_id}/release-policy",
                json={"block_on": "CRITICAL", "max_risk_score": 100, "require_all_routes": False},
            )
            assert client.post(
                f"/api/v1/projects/{project_id}/scans",
                json={"url": "https://example.com/login", "role": "baseline"},
            ).status_code == 201

            overview = client.get(f"/api/v1/projects/{project_id}/release-overview").json()
            assert overview["comparable_routes"] == 0
            assert overview["gate_status"] == "INCOMPLETE"

            gate = client.get(f"/api/v1/projects/{project_id}/release-gate").json()
            assert gate["status"] == "INCOMPLETE"
            assert gate["allowed"] is False
            assert gate["exit_code"] == 1
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()
