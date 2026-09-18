import json
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.db_models import Project, Scan
from app.models.diff import CompareResult
from app.models.project import ProjectCreate, ProjectScanRequest
from app.models.scan import ScanRequest, ScanResult
from app.services.scanner import scan_page
from app.analyzers.diff import compare_objects
from app.risk.engine import calculate_risk

def create_project(db: Session, data: ProjectCreate) -> Project:
    project = Project(name=data.name, description=data.description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def list_projects(db: Session) -> list[Project]:
    return list(db.scalars(select(Project).order_by(Project.created_at.desc())))

def get_project(db: Session, project_id: int) -> Project | None:
    return db.get(Project, project_id)

async def run_project_scan(db: Session, project: Project, data: ProjectScanRequest) -> Scan:
    result = await scan_page(ScanRequest(
        url=data.url, wait_until=data.wait_until, timeout_ms=data.timeout_ms
    ))
    if data.role == "baseline":
        for previous in db.scalars(
            select(Scan).where(Scan.project_id == project.id, Scan.role == "baseline")
        ):
            previous.role = "history"
    scan = Scan(
        project_id=project.id,
        url=result.url,
        title=result.title,
        role=data.role,
        total_testable_objects=result.total_testable_objects,
        payload_json=result.model_dump_json(),
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan

def list_scans(db: Session, project_id: int) -> list[Scan]:
    return list(db.scalars(
        select(Scan).where(Scan.project_id == project_id).order_by(Scan.created_at.desc())
    ))

def compare_latest(db: Session, project_id: int) -> CompareResult | None:
    baseline = db.scalars(
        select(Scan).where(Scan.project_id == project_id, Scan.role == "baseline")
        .order_by(Scan.created_at.desc()).limit(1)
    ).first()
    current = db.scalars(
        select(Scan).where(Scan.project_id == project_id, Scan.role == "current")
        .order_by(Scan.created_at.desc()).limit(1)
    ).first()
    if not baseline or not current:
        return None
    old = ScanResult.model_validate_json(baseline.payload_json)
    new = ScanResult.model_validate_json(current.payload_json)
    diff = compare_objects(old.testable_objects, new.testable_objects)
    return CompareResult(diff=diff, risk=calculate_risk(diff))
