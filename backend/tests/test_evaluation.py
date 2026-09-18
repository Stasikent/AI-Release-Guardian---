from app.evaluation.dataset import EXTENDED_CASES
from app.evaluation.metrics import summarize
from app.evaluation.mutations import CASES,evaluate_mutation

def test_known_mutations_are_detected():
    results=[evaluate_mutation(case) for case in CASES+EXTENDED_CASES]
    summary=summarize(results)
    assert summary["cases"]>=30
    assert summary["failed"]==0
    assert summary["pass_rate"]==1.0
