from typing import Literal
from pydantic import BaseModel, Field
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
    risk_points: int = 0
    field_risk_points: dict[str, int] = Field(default_factory=dict)

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

class RegressionFocusItem(BaseModel):
    priority: int
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    target: str
    locator: str
    reason: str
    risk_points: int
    suggested_check: str

class RegressionTestCase(BaseModel):
    id: str
    priority: int
    severity: Literal["LOW","MEDIUM","HIGH","CRITICAL"]
    title: str
    locator: str
    preconditions: list[str]
    steps: list[str]
    expected_results: list[str]
    source: Literal["deterministic"] = "deterministic"
    risk_points: int

class CompareRequest(BaseModel):
    baseline: list[TestableObject]
    current: list[TestableObject]

class CompareResult(BaseModel):
    diff: DiffReport
    risk: RiskReport
    regression_focus: list[RegressionFocusItem] = Field(default_factory=list)\n    regression_tests: list[RegressionTestCase] = Field(default_factory=list)
