import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models.project import ProjectCreate, ProjectScanRequest
from app.models.scan import ScanResult, TestableObject as DomObject
from app.services.projects import compare_latest, create_project, list_scans, run_project_scan


def _result(*objects: DomObject) -> ScanResult:
    counts: dict[str, int] = {}
    for obj in objects:
        counts[obj.object_type] = counts.get(obj.object_type, 0) + 1
    return ScanResult(
        url="https://example.com",
        title="Demo",
        total_testable_objects=len(objects),
        object_counts=counts,
        testable_objects=list(objects),
    )


@pytest.mark.asyncio
async def test_project_baseline_current_compare_risk(monkeypatch) -> None:
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

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    with Session() as db:
        project = create_project(db, ProjectCreate(name="Integration Demo"))
        await run_project_scan(db, project, ProjectScanRequest(url="https://example.com", role="baseline"))
        await run_project_scan(db, project, ProjectScanRequest(url="https://example.com", role="current"))

        comparison = compare_latest(db, project.id)

        assert comparison is not None
        assert len(comparison.diff.changed) == 2
        assert len(comparison.diff.added) == 0
        assert len(comparison.diff.removed) == 0
        assert comparison.risk.score > 0
        factor_codes = {factor.code for factor in comparison.risk.factors}
        assert any("disabled" in code for code in factor_codes)
        assert any("required" in code for code in factor_codes)


@pytest.mark.asyncio
async def test_new_baseline_archives_previous_baseline(monkeypatch) -> None:
    first = _result(
        DomObject(index=0, object_type="button", tag_name="button", id="save", text="Save", locator="#save"),
    )
    second = _result(
        DomObject(index=0, object_type="button", tag_name="button", id="save", text="Save changes", locator="#save"),
    )
    responses = iter([first, second])

    async def fake_scan_page(_request):
        return next(responses)

    monkeypatch.setattr("app.services.projects.scan_page", fake_scan_page)

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    with Session() as db:
        project = create_project(db, ProjectCreate(name="Baseline History Demo"))
        original = await run_project_scan(
            db, project, ProjectScanRequest(url="https://example.com", role="baseline")
        )
        replacement = await run_project_scan(
            db, project, ProjectScanRequest(url="https://example.com", role="baseline")
        )

        scans = list_scans(db, project.id)
        by_id = {scan.id: scan for scan in scans}

        assert by_id[original.id].role == "history"
        assert by_id[replacement.id].role == "baseline"
        assert sum(scan.role == "baseline" for scan in scans) == 1
        assert sum(scan.role == "history" for scan in scans) == 1


@pytest.mark.asyncio
async def test_failed_scan_does_not_archive_existing_baseline(monkeypatch) -> None:
    baseline = _result(
        DomObject(index=0, object_type="button", tag_name="button", id="save", text="Save", locator="#save"),
    )

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    async def successful_scan(_request):
        return baseline

    monkeypatch.setattr("app.services.projects.scan_page", successful_scan)

    with Session() as db:
        project = create_project(db, ProjectCreate(name="Failed Scan Demo"))
        original = await run_project_scan(
            db, project, ProjectScanRequest(url="https://example.com", role="baseline")
        )

        async def failed_scan(_request):
            raise RuntimeError("browser failed")

        monkeypatch.setattr("app.services.projects.scan_page", failed_scan)

        with pytest.raises(RuntimeError, match="browser failed"):
            await run_project_scan(
                db, project, ProjectScanRequest(url="https://example.com", role="baseline")
            )

        scans = list_scans(db, project.id)
        assert len(scans) == 1
        assert scans[0].id == original.id
        assert scans[0].role == "baseline"
