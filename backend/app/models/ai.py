from typing import Literal
from pydantic import BaseModel, Field

class AIAnalysis(BaseModel):
    release_summary: str
    likely_impacts: list[str] = Field(default_factory=list)
    regression_focus: list[str] = Field(default_factory=list)
    suggested_tests: list[str] = Field(default_factory=list)
    confidence: Literal["low", "medium", "high"] = "medium"
    limitations: list[str] = Field(default_factory=list)

class AIAnalysisResponse(BaseModel):
    provider: str
    model: str
    analysis: AIAnalysis
