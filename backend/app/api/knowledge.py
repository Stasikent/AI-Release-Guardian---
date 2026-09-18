from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.db_models import KnowledgeDocument
from app.models.knowledge import KnowledgeDocumentCreate,KnowledgeDocumentRead
from app.services.projects import get_project

router=APIRouter(prefix="/api/v1/projects",tags=["knowledge"])

@router.post("/{project_id}/knowledge",response_model=KnowledgeDocumentRead,status_code=status.HTTP_201_CREATED)
def add_knowledge(project_id:int,data:KnowledgeDocumentCreate,db:Session=Depends(get_db)):
    if not get_project(db,project_id): raise HTTPException(404,"Project not found")
    doc=KnowledgeDocument(project_id=project_id,title=data.title,source=data.source,content=data.content)
    db.add(doc); db.commit(); db.refresh(doc); return doc

@router.get("/{project_id}/knowledge",response_model=list[KnowledgeDocumentRead])
def list_knowledge(project_id:int,db:Session=Depends(get_db)):
    if not get_project(db,project_id): raise HTTPException(404,"Project not found")
    return list(db.scalars(select(KnowledgeDocument).where(KnowledgeDocument.project_id==project_id).order_by(KnowledgeDocument.created_at.desc())))
