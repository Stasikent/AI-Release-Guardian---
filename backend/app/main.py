from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ai import router as ai_router
from app.api.compare import router as compare_router
from app.api.projects import router as projects_router
from app.api.knowledge import router as knowledge_router
from app.api.evaluation import router as evaluation_router
from app.api.scans import router as scans_router
from app.db import Base, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="AI Release Guardian API",
    version="2.0.0-dev",
    description="Backend API for AI-assisted release risk analysis.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scans_router)
app.include_router(ai_router)
app.include_router(compare_router)
app.include_router(projects_router)
app.include_router(knowledge_router)
app.include_router(evaluation_router)

@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "version": "2.0.0-dev"}
