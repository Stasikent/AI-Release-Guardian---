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
        url="https://example.com",
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
                json={"name": "HTTP Integration Demo", "description": "End-to-end API flow"},
            )
            assert created.status_code == 201
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

            comparison = client.get(f"/api/v1/projects/{project_id}/compare")
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

            json_export = client.get(f"/api/v1/projects/{project_id}/regression-tests/export?format=json")
            assert json_export.status_code == 200
            assert "regression-tests.json" in json_export.headers["content-disposition"]
            assert len(json_export.json()) == 2

            markdown_export = client.get(f"/api/v1/projects/{project_id}/regression-tests/export?format=markdown")
            assert markdown_export.status_code == 200
            assert "# AI Release Guardian" in markdown_export.text
            assert "REG-001" in markdown_export.text

            playwright_export = client.get(f"/api/v1/projects/{project_id}/regression-tests/export?format=playwright")
            assert playwright_export.status_code == 200
            assert "regression.generated.spec.ts" in playwright_export.headers["content-disposition"]
            assert "import { test, expect } from '@playwright/test';" in playwright_export.text
            assert "REG-001" in playwright_export.text
            assert 'page.goto("https://example.com/current")' in playwright_export.text
            assert 'page.goto("https://shop.example.com/app")' not in playwright_export.text
            assert "toBeDisabled()" in playwright_export.text
            assert "toHaveJSProperty('required', true)" in playwright_export.text

            invalid_export = client.get(f"/api/v1/projects/{project_id}/regression-tests/export?format=xml")
            assert invalid_export.status_code == 400
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()
