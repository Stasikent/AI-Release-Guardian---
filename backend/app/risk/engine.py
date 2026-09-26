from collections import Counter
from app.models.diff import DiffReport, RiskFactor, RiskReport

INTERACTIVE_TYPES={"input","button","form","select","textarea","link"}
FIELD_WEIGHTS={
 "disabled":14,"required":10,"readonly":10,"checked":8,"selected":8,
 "href":10,"src":6,"type":8,"role":7,"aria_checked":6,"aria_selected":6,
 "aria_expanded":5,"aria_label":4,"aria_describedby":3,
 "placeholder":3,"value":4,"text":2,"css_class":1,"title":2,
}
def _factor(code,description,weight,count):
    return RiskFactor(code=code,description=description,weight=weight,count=count,points=weight*count)

def calculate_risk(diff:DiffReport)->RiskReport:
    removed_interactive=sum(o.object_type in INTERACTIVE_TYPES for o in diff.removed)
    added_interactive=sum(o.object_type in INTERACTIVE_TYPES for o in diff.added)
    removed_other=len(diff.removed)-removed_interactive
    field_counts=Counter(field for change in diff.changed for field in change.changed_fields)
    for change in diff.changed:
        change.field_risk_points = {field: FIELD_WEIGHTS.get(field, 3) for field in change.changed_fields}
        change.risk_points = sum(change.field_risk_points.values())
    factors=[
      _factor("removed_interactive","Interactive elements removed",12,removed_interactive),
      _factor("added_interactive","Interactive elements added",4,added_interactive),
      _factor("removed_other","Non-interactive elements removed",4,removed_other),
    ]
    for field,count in sorted(field_counts.items()):
        weight=FIELD_WEIGHTS.get(field,3)
        factors.append(_factor(f"field_{field}",f"Element field changed: {field}",weight,count))
    factors=[f for f in factors if f.count>0]
    raw=sum(f.points for f in factors);score=min(raw,100)
    level="LOW" if score<15 else "MEDIUM" if score<40 else "HIGH" if score<70 else "CRITICAL"
    top=sorted(factors,key=lambda f:f.points,reverse=True)[:3]
    reasons=", ".join(f"{f.code} (+{f.points})" for f in top) or "no material deterministic changes"
    summary=f"{len(diff.added)} added, {len(diff.removed)} removed, {len(diff.changed)} changed; {diff.unchanged_count} unchanged. Main drivers: {reasons}."
    return RiskReport(score=score,raw_score=raw,level=level,factors=factors,summary=summary)
