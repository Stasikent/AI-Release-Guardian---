from app.models.diff import DiffReport, RegressionFocusItem

def _severity(points:int)->str:
    return "CRITICAL" if points>=15 else "HIGH" if points>=10 else "MEDIUM" if points>=5 else "LOW"

def _check(fields:list[str])->str:
    state={"disabled","required","readonly","checked","selected"}
    navigation={"href","src"}
    accessibility={"role","aria_checked","aria_selected","aria_expanded","aria_label","aria_describedby"}
    if state.intersection(fields): return "Verify the element state and complete its primary user interaction."
    if navigation.intersection(fields): return "Verify navigation/resource target and the resulting user flow."
    if accessibility.intersection(fields): return "Verify keyboard/screen-reader semantics and interaction state."
    if "type" in fields: return "Verify input semantics, validation, and submission behavior."
    return "Verify the changed element in its primary regression flow."

def build_regression_focus(diff:DiffReport)->list[RegressionFocusItem]:
    candidates=[]
    for change in diff.changed:
        candidates.append((change.risk_points,change.after.display_name or change.after.locator,change.after.locator,
            f"Changed fields: {', '.join(change.changed_fields)}.",_check(change.changed_fields)))
    for obj in diff.removed:
        points=12 if obj.object_type in {"input","button","form","select","textarea","link"} else 4
        candidates.append((points,obj.display_name or obj.locator,obj.locator,"Element removed from the current DOM.","Verify dependent user flows and confirm the removal is intentional."))
    for obj in diff.added:
        if obj.object_type in {"input","button","form","select","textarea","link"}:
            candidates.append((4,obj.display_name or obj.locator,obj.locator,"Interactive element added to the current DOM.","Verify the new interaction and surrounding regression flow."))
    candidates.sort(key=lambda item:item[0],reverse=True)
    return [RegressionFocusItem(priority=i,severity=_severity(points),target=target,locator=locator,reason=reason,risk_points=points,suggested_check=check)
            for i,(points,target,locator,reason,check) in enumerate(candidates,1)]
