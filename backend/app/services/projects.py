import json
from urllib.parse import urlsplit
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.db_models import Project, Scan
from app.models.diff import CompareResult, ProjectReleaseOverview, RouteReleaseSummary
from app.models.project import ProjectCreate, ProjectScanRequest
from app.models.scan import ScanRequest, ScanResult
from app.services.scanner import scan_page
from app.analyzers.diff import compare_objects
from app.risk.engine import calculate_risk
from app.risk.focus import build_regression_focus
from app.risk.regression_tests import build_regression_tests


def _route(url: str, explicit: str | None = None) -> str:
    if explicit:
        return explicit if explicit.startswith("/") else f"/{explicit}"
    parsed = urlsplit(url)
    return parsed.path or "/"


def latest_comparison_scans(db: Session, project_id: int, route: str | None = None) -> tuple[Scan | None, Scan | None]:
    baseline = db.scalars(
        select(Scan).where(Scan.project_id == project_id, Scan.role == "baseline", *((Scan.route == route,) if route else ()))
        .order_by(Scan.created_at.desc()).limit(1)
    ).first()
    current = db.scalars(
        select(Scan).where(Scan.project_id == project_id, Scan.role == "current", *((Scan.route == route,) if route else ()))
        .order_by(Scan.created_at.desc()).limit(1)
    ).first()
    return baseline, current

def create_project(db: Session, data: ProjectCreate) -> Project:
    project = Project(name=data.name, description=data.description, base_url=str(data.base_url) if data.base_url else None)
    db.add(project)
    try:
        db.commit()
        db.refresh(project)
    except Exception:
        db.rollback()
        raise
    return project


def list_projects(db: Session) -> list[Project]:
    return list(db.scalars(select(Project).order_by(Project.created_at.desc())))


def get_project(db: Session, project_id: int) -> Project | None:
    return db.get(Project, project_id)


async def run_project_scan(db: Session, project: Project, data: ProjectScanRequest) -> Scan:
    # Browser work happens before opening the database mutation. A failed scan
    # must never archive an existing baseline.
    result = await scan_page(ScanRequest(
        url=data.url, wait_until=data.wait_until, timeout_ms=data.timeout_ms
    ))

    try:
        route = _route(result.url, data.route)
        if data.role in {"baseline", "current"}:
            for previous in db.scalars(
                select(Scan).where(
                    Scan.project_id == project.id,
                    Scan.role == data.role,
                    Scan.route == route,
                )
            ):
                previous.role = "history"

        scan = Scan(
            project_id=project.id,
            url=result.url,
            route=route,
            title=result.title,
            role=data.role,
            total_testable_objects=result.total_testable_objects,
            payload_json=result.model_dump_json(),
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)
        return scan
    except Exception:
        db.rollback()
        raise


def list_scans(db: Session, project_id: int) -> list[Scan]:
    return list(db.scalars(
        select(Scan).where(Scan.project_id == project_id).order_by(Scan.created_at.desc())
    ))


def list_routes(db: Session, project_id: int) -> list[str]:
    routes = db.scalars(
        select(Scan.route).where(Scan.project_id == project_id).distinct().order_by(Scan.route)
    )
    return [route for route in routes if route]


def compare_latest(db: Session, project_id: int, route: str | None = None) -> CompareResult | None:
    baseline, current = latest_comparison_scans(db, project_id, route)
    if not baseline or not current:
        return None
    old = ScanResult.model_validate_json(baseline.payload_json)
    new = ScanResult.model_validate_json(current.payload_json)
    diff = compare_objects(old.testable_objects, new.testable_objects)
    risk=calculate_risk(diff)
    focus=build_regression_focus(diff)
    return CompareResult(diff=diff, risk=risk, regression_focus=focus, regression_tests=build_regression_tests(focus))


def build_release_overview(db: Session, project_id: int) -> ProjectReleaseOverview:
    summaries: list[RouteReleaseSummary] = []
    for route in list_routes(db, project_id):
        baseline, current = latest_comparison_scans(db, project_id, route)
        if not baseline or not current:
            summaries.append(RouteReleaseSummary(
                route=route,
                comparable=False,
                baseline_scan_id=baseline.id if baseline else None,
                current_scan_id=current.id if current else None,
            ))
            continue
        result = compare_latest(db, project_id, route)
        summaries.append(RouteReleaseSummary(
            route=route,
            comparable=True,
            baseline_scan_id=baseline.id,
            current_scan_id=current.id,
            risk_score=result.risk.score,
            risk_level=result.risk.level,
            added_count=len(result.diff.added),
            removed_count=len(result.diff.removed),
            changed_count=len(result.diff.changed),
            regression_tests_count=len(result.regression_tests),
        ))
    comparable = [item for item in summaries if item.comparable and item.risk_score is not None]
    overall = max((item.risk_score for item in comparable), default=0)
    level = "CRITICAL" if overall >= 75 else "HIGH" if overall >= 50 else "MEDIUM" if overall >= 25 else "LOW"
    return ProjectReleaseOverview(
        project_id=project_id,
        routes=summaries,
        comparable_routes=len(comparable),
        incomplete_routes=len(summaries) - len(comparable),
        overall_risk_score=overall,
        overall_risk_level=level,
    )
