from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.llm.factory import get_llm_provider
from app.models.ai import AIAnalysisResponse
from app.services.ai_analysis import analyze
from app.services.projects import compare_latest, get_project

router=APIRouter(prefix="/api/v1/projects",tags=["ai"])

@router.post("/{project_id}/ai-analysis",response_model=AIAnalysisResponse)
async def ai_analysis(project_id:int,db:Session=Depends(get_db))->AIAnalysisResponse:
    if not get_project(db,project_id):
        raise HTTPException(status_code=404,detail="Project not found")
    comparison=compare_latest(db,project_id)
    if comparison is None:
        raise HTTPException(status_code=409,detail="Baseline and current scans are required")
    try:
        provider=get_llm_provider()
        return await analyze(comparison,provider)
    except RuntimeError as exc:
        raise HTTPException(status_code=503,detail=str(exc)) from exc
