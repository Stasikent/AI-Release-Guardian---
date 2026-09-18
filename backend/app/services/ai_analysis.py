from app.llm.base import LLMProvider
from app.models.ai import AIAnalysisResponse
from app.models.diff import CompareResult

def build_release_facts(comparison: CompareResult) -> dict:
    def compact(obj):
        return {
            "object_type":obj.object_type,
            "display_name":obj.display_name,
            "locator":obj.locator,
            "type":obj.type,
            "href":obj.href,
        }
    return {
        "deterministic_risk":{
            "score":comparison.risk.score,
            "level":comparison.risk.level,
            "summary":comparison.risk.summary,
            "factors":[f.model_dump() for f in comparison.risk.factors],
        },
        "diff":{
            "added":[compact(x) for x in comparison.diff.added],
            "removed":[compact(x) for x in comparison.diff.removed],
            "changed":[{
                "element":compact(x.after),
                "changed_fields":x.changed_fields,
            } for x in comparison.diff.changed],
            "unchanged_count":comparison.diff.unchanged_count,
        },
    }

async def analyze(comparison: CompareResult, provider: LLMProvider) -> AIAnalysisResponse:
    analysis=await provider.analyze_release(build_release_facts(comparison))
    return AIAnalysisResponse(provider=provider.name,model=provider.model,analysis=analysis)
