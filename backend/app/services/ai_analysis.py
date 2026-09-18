from app.llm.base import LLMProvider
from app.models.ai import AIAnalysisResponse
from app.models.diff import CompareResult
from app.models.evidence import EvidenceBundle,EvidenceItem
from app.rag.hybrid import hybrid_retrieve

def _compact(obj):
    return {"object_type":obj.object_type,"display_name":obj.display_name,"locator":obj.locator,"type":obj.type,"href":obj.href}

def retrieval_query(comparison:CompareResult)->str:
    parts=[comparison.risk.summary]
    parts += [x.display_name or x.locator for x in comparison.diff.added+comparison.diff.removed]
    parts += [x.after.display_name or x.after.locator for x in comparison.diff.changed]
    return " ".join(filter(None,parts))

def build_evidence(comparison:CompareResult,documents:list|None=None)->EvidenceBundle:
    observed=[]
    for i,obj in enumerate(comparison.diff.added):
        observed.append(EvidenceItem(id=f"OBS-A{i+1}",kind="observed",statement=f"Added {obj.object_type}: {obj.display_name or obj.locator}",source="deterministic-diff"))
    for i,obj in enumerate(comparison.diff.removed):
        observed.append(EvidenceItem(id=f"OBS-R{i+1}",kind="observed",statement=f"Removed {obj.object_type}: {obj.display_name or obj.locator}",source="deterministic-diff"))
    for i,ch in enumerate(comparison.diff.changed):
        observed.append(EvidenceItem(id=f"OBS-C{i+1}",kind="observed",statement=f"Changed {ch.after.object_type}: {ch.after.display_name or ch.after.locator}; fields: {', '.join(ch.changed_fields)}",source="deterministic-diff"))
    retrieved=[]
    for i,item in enumerate(hybrid_retrieve(retrieval_query(comparison),documents or [])):
        retrieved.append(EvidenceItem(id=f"CTX-{i+1}",kind="retrieved",statement=item.excerpt,source=item.source,score=item.score))
    return EvidenceBundle(observed=observed,retrieved=retrieved)

def build_release_facts(comparison:CompareResult,evidence:EvidenceBundle|None=None)->dict:
    evidence=evidence or EvidenceBundle()
    return {
      "deterministic_risk":{"score":comparison.risk.score,"level":comparison.risk.level,"summary":comparison.risk.summary,"factors":[f.model_dump() for f in comparison.risk.factors]},
      "diff":{"added":[_compact(x) for x in comparison.diff.added],"removed":[_compact(x) for x in comparison.diff.removed],"changed":[{"element":_compact(x.after),"changed_fields":x.changed_fields} for x in comparison.diff.changed],"unchanged_count":comparison.diff.unchanged_count},
      "evidence":evidence.model_dump(),
      "reasoning_contract":"Cite evidence IDs when possible. Observed evidence is fact. Retrieved context is project documentation. Likely impact remains inference until tested."
    }

async def analyze(comparison:CompareResult,provider:LLMProvider,documents:list|None=None)->AIAnalysisResponse:
    evidence=build_evidence(comparison,documents)
    analysis=await provider.analyze_release(build_release_facts(comparison,evidence))
    return AIAnalysisResponse(provider=provider.name,model=provider.model,analysis=analysis,evidence=evidence)
