from dataclasses import dataclass
from app.analyzers.dom import extract_testable_objects
from app.analyzers.diff import compare_objects
from app.risk.engine import calculate_risk

@dataclass(frozen=True)
class MutationCase:
    name:str
    baseline_html:str
    current_html:str
    expected_added:int
    expected_removed:int
    expected_changed:int
    expected_min_risk:int=0

CASES=[
 MutationCase("button_text_change",'<button id="buy">Buy</button>','<button id="buy">Pay now</button>',0,0,1,1),
 MutationCase("critical_button_removed",'<button id="submit">Submit</button>','<div>Done</div>',0,1,0,10),
 MutationCase("input_added",'<form id="checkout"></form>','<form id="checkout"><input id="coupon" name="coupon"></form>',1,0,0,1),
 MutationCase("link_target_changed",'<a id="help" href="/help">Help</a>','<a id="help" href="/support">Help</a>',0,0,1,10),
 MutationCase("unchanged",'<input id="email" placeholder="Email">','<input id="email" placeholder="Email">',0,0,0,0),
]

def evaluate_mutation(case:MutationCase)->dict:
    baseline=extract_testable_objects(case.baseline_html)
    current=extract_testable_objects(case.current_html)
    diff=compare_objects(baseline,current)
    risk=calculate_risk(diff)
    passed=(len(diff.added)==case.expected_added and len(diff.removed)==case.expected_removed and len(diff.changed)==case.expected_changed and risk.score>=case.expected_min_risk)
    return {"name":case.name,"passed":passed,"added":len(diff.added),"removed":len(diff.removed),"changed":len(diff.changed),"risk_score":risk.score}
