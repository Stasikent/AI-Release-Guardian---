from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.diff import CompareResult
from app.models.project import ProjectCreate, ProjectRead, ProjectScanRequest, StoredScanRead
from app.services.projects import (
    compare_latest, create_project, get_project, list_projects, list_scans, run_project_scan,
)

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])

@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create(data: ProjectCreate, db: Session = Depends(get_db)) -> ProjectRead:
    try:
        return create_project(db, data)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Project name already exists") from exc

@router.get("", response_model=list[ProjectRead])
def all_projects(db: Session = Depends(get_db)) -> list[ProjectRead]:
    return list_projects(db)

@router.post("/{project_id}/scans", response_model=StoredScanRead, status_code=status.HTTP_201_CREATED)
async def scan(project_id: int, data: ProjectScanRequest, db: Session = Depends(get_db)) -> StoredScanRead:
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await run_project_scan(db, project, data)

@router.get("/{project_id}/scans", response_model=list[StoredScanRead])
def scans(project_id: int, db: Session = Depends(get_db)) -> list[StoredScanRead]:
    if not get_project(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return list_scans(db, project_id)

@router.get("/{project_id}/compare", response_model=CompareResult)
def compare(project_id: int, db: Session = Depends(get_db)) -> CompareResult:
    if not get_project(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    result = compare_latest(db, project_id)
    if result is None:
        raise HTTPException(status_code=409, detail="Baseline and current scans are required")
    return result
