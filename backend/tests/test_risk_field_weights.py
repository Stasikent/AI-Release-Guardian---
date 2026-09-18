from app.analyzers.diff import compare_objects
from app.analyzers.dom import extract_testable_objects
from app.risk.engine import calculate_risk

def risk(a,b):
    return calculate_risk(compare_objects(extract_testable_objects(a),extract_testable_objects(b)))

def test_disabled_is_riskier_than_button_text_change():
    text=risk('<button id="pay">Pay</button>','<button id="pay">Pay now</button>')
    disabled=risk('<button id="pay">Pay</button>','<button id="pay" disabled>Pay</button>')
    assert disabled.score>text.score
    assert any(x.code=="field_disabled" for x in disabled.factors)

def test_required_is_riskier_than_placeholder_change():
    placeholder=risk('<input id="email" placeholder="Email">','<input id="email" placeholder="Work email">')
    required=risk('<input id="email">','<input id="email" required>')
    assert required.score>placeholder.score

def test_href_change_has_specific_reason():
    report=risk('<a id="help" href="/help">Help</a>','<a id="help" href="/support">Help</a>')
    assert any(x.code=="field_href" and x.weight==10 for x in report.factors)
    assert "field_href" in report.summary
