import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ai import router as ai_router
from app.api.compare import router as compare_router
from app.api.projects import router as projects_router
from app.api.knowledge import router as knowledge_router
from app.api.evaluation import router as evaluation_router
from app.api.scans import router as scans_router

def _cors_origins() -> list[str]:
    raw=os.getenv("CORS_ORIGINS","http://localhost:3000")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]

app=FastAPI(title="AI Release Guardian API",version="2.0.0-dev",description="Backend API for AI-assisted release risk analysis.")

app.add_middleware(CORSMiddleware,allow_origins=_cors_origins(),allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(scans_router)
app.include_router(ai_router)
app.include_router(compare_router)
app.include_router(projects_router)
app.include_router(knowledge_router)
app.include_router(evaluation_router)

@app.get("/health",tags=["system"])
def health()->dict[str,str]:
    return {"status":"ok","version":"2.0.0-dev"}
