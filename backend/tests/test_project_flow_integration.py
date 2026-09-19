import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models.project import ProjectCreate, ProjectScanRequest
from app.models.scan import ScanResult, TestableObject
from app.services.projects import compare_latest, create_project, run_project_scan


def _result(*objects: TestableObject) -> ScanResult:
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
        TestableObject(index=0, object_type="button", tag_name="button", id="save", text="Save", locator="#save"),
        TestableObject(index=1, object_type="input", tag_name="input", id="email", type="email", required=False, locator="#email"),
    )
    current = _result(
        TestableObject(index=0, object_type="button", tag_name="button", id="save", text="Save", disabled=True, locator="#save"),
        TestableObject(index=1, object_type="input", tag_name="input", id="email", type="email", required=True, locator="#email"),
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
