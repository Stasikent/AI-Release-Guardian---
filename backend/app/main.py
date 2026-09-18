from fastapi import FastAPI

from app.api.compare import router as compare_router
from app.api.scans import router as scans_router

app = FastAPI(
    title="AI Release Guardian API",
    version="2.0.0-dev",
    description="Backend API for AI-assisted release risk analysis.",
)

app.include_router(scans_router)
app.include_router(compare_router)

@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "version": "2.0.0-dev"}
