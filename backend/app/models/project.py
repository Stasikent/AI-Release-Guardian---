from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=2000)
    base_url: HttpUrl | None = None

class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    base_url: str | None = None
    created_at: datetime

class ProjectScanRequest(BaseModel):
    url: HttpUrl
    route: str | None = Field(default=None, max_length=500)
    role: str = Field(default="current", pattern="^(baseline|current)$")
    wait_until: str = Field(default="networkidle", pattern="^(load|domcontentloaded|networkidle|commit)$")
    timeout_ms: int = Field(default=30000, ge=1000, le=120000)

class StoredScanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int
    url: str
    route: str | None = None
    title: str
    role: str
    total_testable_objects: int
    created_at: datetime
