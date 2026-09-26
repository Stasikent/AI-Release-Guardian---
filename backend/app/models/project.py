from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=2000)
    base_url: HttpUrl | None = None

class ReleasePolicy(BaseModel):
    block_on: str = Field(default="CRITICAL", pattern="^(HIGH|CRITICAL)$")
    max_risk_score: int = Field(default=100, ge=0, le=100)
    require_all_routes: bool = True

class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    base_url: str | None = None
    block_on: str = "CRITICAL"
    max_risk_score: int = 100
    require_all_routes: bool = True
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


class RouteDiscoveryRequest(BaseModel):
    url: HttpUrl
    max_routes: int = Field(default=20, ge=1, le=100)
    wait_until: str = Field(default="networkidle", pattern="^(load|domcontentloaded|networkidle|commit)$")
    timeout_ms: int = Field(default=30000, ge=1000, le=120000)

class RouteDiscoveryResult(BaseModel):
    source_url: str
    routes: list[str] = Field(default_factory=list)
    discovered_count: int = 0


class BatchScanRequest(BaseModel):
    base_url: HttpUrl
    routes: list[str] = Field(min_length=1, max_length=100)
    role: str = Field(default="current", pattern="^(baseline|current)$")
    wait_until: str = Field(default="networkidle", pattern="^(load|domcontentloaded|networkidle|commit)$")
    timeout_ms: int = Field(default=30000, ge=1000, le=120000)

class BatchScanItem(BaseModel):
    route: str
    status: str
    scan_id: int | None = None
    error: str | None = None
    error_code: str | None = None

class BatchScanResult(BaseModel):
    role: str
    requested_count: int
    succeeded_count: int
    failed_count: int
    results: list[BatchScanItem] = Field(default_factory=list)
