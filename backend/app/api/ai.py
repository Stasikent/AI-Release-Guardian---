from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import get_db
from app.llm.errors import LLMAuthenticationError,LLMConfigurationError,LLMInvalidResponseError,LLMRateLimitError,LLMTimeoutError,LLMUpstreamError
from app.llm.factory import get_llm_provider
from app.models.ai import AIAnalysisResponse
from app.models.db_models import KnowledgeDocument
from app.services.ai_analysis import analyze
from app.services.projects import compare_latest,get_project

router=APIRouter(prefix="/api/v1/projects",tags=["ai"])

@router.post("/{project_id}/ai-analysis",response_model=AIAnalysisResponse)
async def ai_analysis(project_id:int,db:Session=Depends(get_db))->AIAnalysisResponse:
    if not get_project(db,project_id): raise HTTPException(404,"Project not found")
    comparison=compare_latest(db,project_id)
    if comparison is None: raise HTTPException(409,"Baseline and current scans are required")
    documents=list(db.scalars(select(KnowledgeDocument).where(KnowledgeDocument.project_id==project_id)))
    try: return await analyze(comparison,get_llm_provider(),documents)
    except LLMConfigurationError as exc: raise HTTPException(503,str(exc)) from exc
    except LLMAuthenticationError as exc: raise HTTPException(502,"LLM provider authentication failed") from exc
    except LLMRateLimitError as exc: raise HTTPException(429,"LLM provider rate limit reached") from exc
    except LLMTimeoutError as exc: raise HTTPException(504,"LLM provider timed out") from exc
    except LLMInvalidResponseError as exc: raise HTTPException(502,"LLM provider returned invalid structured output") from exc
    except LLMUpstreamError as exc: raise HTTPException(502,"LLM provider is unavailable") from exc
