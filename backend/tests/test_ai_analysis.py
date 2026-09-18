import asyncio
from app.models.ai import AIAnalysis
from app.models.diff import CompareResult, DiffReport, RiskReport
from app.services.ai_analysis import analyze, build_release_facts

class FakeProvider:
    name="fake"
    model="test-model"
    async def analyze_release(self,facts):
        assert facts["deterministic_risk"]["score"] == 12
        return AIAnalysis(
            release_summary="One observed UI change.",
            regression_focus=["Changed control"],
            suggested_tests=["Verify changed control behavior."],
            confidence="high",
        )

def comparison():
    return CompareResult(
        diff=DiffReport(added=[],removed=[],changed=[],unchanged_count=3),
        risk=RiskReport(score=12,raw_score=12,level="LOW",factors=[],summary="facts"),
    )

def test_fact_payload_is_deterministic():
    facts=build_release_facts(comparison())
    assert facts["diff"]["unchanged_count"] == 3
    assert facts["deterministic_risk"]["level"] == "LOW"

def test_provider_is_replaceable():
    result=asyncio.run(analyze(comparison(),FakeProvider()))
    assert result.provider == "fake"
    assert result.analysis.confidence == "high"
