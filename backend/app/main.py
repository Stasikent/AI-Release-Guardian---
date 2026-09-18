from fastapi import FastAPI

app = FastAPI(
    title="AI Release Guardian API",
    version="2.0.0-dev",
    description="Backend API for AI-assisted release risk analysis.",
)

@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "version": "2.0.0-dev"}
