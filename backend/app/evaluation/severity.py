from dataclasses import dataclass
from app.analyzers.diff import compare_objects
from app.analyzers.dom import extract_testable_objects
from app.risk.engine import calculate_risk

@dataclass(frozen=True)
class SeverityCase:
    name:str; baseline:str; current:str; expected:str

CASES=[
 SeverityCase("cosmetic_class",'<button id="x" class="a">Go</button>','<button id="x" class="b">Go</button>',"LOW"),
 SeverityCase("button_text",'<button id="x">Go</button>','<button id="x">Continue</button>',"LOW"),
 SeverityCase("placeholder",'<input id="x" placeholder="Email">','<input id="x" placeholder="Work email">',"LOW"),
 SeverityCase("aria_label",'<button id="x" aria-label="Open">X</button>','<button id="x" aria-label="Open menu">X</button>',"LOW"),
 SeverityCase("href_target",'<a id="x" href="/a">A</a>','<a id="x" href="/b">A</a>',"LOW"),
 SeverityCase("required_field",'<input id="x">','<input id="x" required>',"LOW"),
 SeverityCase("disabled_control",'<button id="x">Pay</button>','<button id="x" disabled>Pay</button>',"LOW"),
 SeverityCase("removed_button",'<button id="x">Pay</button>','',"LOW"),
 SeverityCase("two_removed_controls",'<button id="a">A</button><input id="b">','',"MEDIUM"),
 SeverityCase("disabled_plus_required",'<button id="a">Pay</button><input id="b">','<button id="a" disabled>Pay</button><input id="b" required>',"MEDIUM"),
 SeverityCase("three_removed_controls",'<button id="a">A</button><input id="b"><select id="c"></select>','',"MEDIUM"),
 SeverityCase("four_removed_controls",'<button id="a">A</button><input id="b"><select id="c"></select><textarea id="d"></textarea>','',"HIGH"),
 SeverityCase("six_removed_controls",'<button id="a">A</button><input id="b"><select id="c"></select><textarea id="d"></textarea><form id="e"></form><a id="f" href="/">F</a>','',"CRITICAL"),
]

LEVELS=["LOW","MEDIUM","HIGH","CRITICAL"]

def evaluate_severity()->dict:
    matrix={a:{p:0 for p in LEVELS} for a in LEVELS};rows=[];correct=0
    for case in CASES:
        diff=compare_objects(extract_testable_objects(case.baseline),extract_testable_objects(case.current))
        report=calculate_risk(diff);pred=report.level
        matrix[case.expected][pred]+=1;correct+=pred==case.expected
        rows.append({"name":case.name,"expected":case.expected,"predicted":pred,"score":report.score})
    n=len(CASES)
    return {"cases":n,"accuracy":round(correct/n,4) if n else 0.0,"confusion_matrix":matrix,"results":rows}
