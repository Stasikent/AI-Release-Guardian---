from typing import Literal
from pydantic import BaseModel
from app.models.scan import TestableObject

class RepresentativeObject(BaseModel):
    object_type: str
    count: int
    representative: TestableObject

class ElementChange(BaseModel):
    fingerprint: str
    before: TestableObject
    after: TestableObject
    changed_fields: list[str]

class DiffReport(BaseModel):
    added: list[TestableObject]
    removed: list[TestableObject]
    changed: list[ElementChange]
    unchanged_count: int

class RiskFactor(BaseModel):
    code: str
    description: str
    weight: int
    count: int
    points: int

class RiskReport(BaseModel):
    score: int
    raw_score: int
    level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    factors: list[RiskFactor]
    summary: str

class CompareRequest(BaseModel):
    baseline: list[TestableObject]
    current: list[TestableObject]

class CompareResult(BaseModel):
    diff: DiffReport
    risk: RiskReport
