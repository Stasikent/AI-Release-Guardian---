from app.llm.base import LLMProvider
from app.models.ai import AIAnalysisResponse
from app.models.diff import CompareResult
from app.rag.retriever import retrieve

def build_release_facts(comparison: CompareResult, context: list | None = None) -> dict:
    def compact(obj):
        return {"object_type":obj.object_type,"display_name":obj.display_name,"locator":obj.locator,"type":obj.type,"href":obj.href}
    return {
        "deterministic_risk":{"score":comparison.risk.score,"level":comparison.risk.level,"summary":comparison.risk.summary,"factors":[f.model_dump() for f in comparison.risk.factors]},
        "diff":{"added":[compact(x) for x in comparison.diff.added],"removed":[compact(x) for x in comparison.diff.removed],"changed":[{"element":compact(x.after),"changed_fields":x.changed_fields} for x in comparison.diff.changed],"unchanged_count":comparison.diff.unchanged_count},
        "retrieved_project_context":[x.model_dump() for x in (context or [])],
        "reasoning_contract":"Observed facts and retrieved context are evidence. Likely impacts are hypotheses, not observed failures."
    }

def retrieval_query(comparison: CompareResult)->str:
    parts=[comparison.risk.summary]
    parts += [x.display_name or x.locator for x in comparison.diff.added+comparison.diff.removed]
    parts += [x.after.display_name or x.after.locator for x in comparison.diff.changed]
    return " ".join(filter(None,parts))

async def analyze(comparison: CompareResult, provider: LLMProvider, documents: list | None = None) -> AIAnalysisResponse:
    context=retrieve(retrieval_query(comparison),documents or [])
    analysis=await provider.analyze_release(build_release_facts(comparison,context))
    return AIAnalysisResponse(provider=provider.name,model=provider.model,analysis=analysis)
