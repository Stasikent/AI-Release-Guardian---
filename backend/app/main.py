from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.compare import router as compare_router
from app.api.projects import router as projects_router
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

app.include_router(scans_router)
app.include_router(compare_router)
app.include_router(projects_router)

@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "version": "2.0.0-dev"}
