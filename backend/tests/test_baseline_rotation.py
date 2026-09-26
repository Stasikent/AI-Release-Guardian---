import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models.db_models import Scan
from app.models.project import ProjectCreate, ProjectScanRequest
from app.models.scan import ScanResult, TestableObject as DomObject
from app.services.projects import create_project, run_project_scan


def _result(label: str) -> ScanResult:
    obj = DomObject(index=0, object_type="button", tag_name="button", id="save", text=label, locator="#save")
    return ScanResult(
        url="https://example.com",
        title=label,
        total_testable_objects=1,
        object_counts={"button": 1},
        testable_objects=[obj],
    )


@pytest.mark.asyncio
async def test_new_baseline_archives_previous_baseline(monkeypatch) -> None:
    responses = iter([_result("Baseline 1"), _result("Baseline 2")])

    async def fake_scan_page(_request):
        return next(responses)

    monkeypatch.setattr("app.services.projects.scan_page", fake_scan_page)

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    with Session() as db:
        project = create_project(db, ProjectCreate(name="Baseline Rotation"))
        first = await run_project_scan(
            db, project, ProjectScanRequest(url="https://example.com", role="baseline")
        )
        second = await run_project_scan(
            db, project, ProjectScanRequest(url="https://example.com", role="baseline")
        )

        scans = list(db.scalars(select(Scan).where(Scan.project_id == project.id).order_by(Scan.id)))
        assert len(scans) == 2
        assert scans[0].id == first.id
        assert scans[0].role == "history"
        assert scans[1].id == second.id
        assert scans[1].role == "baseline"
