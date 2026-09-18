from app.evaluation.dataset import EXTENDED_CASES
from app.evaluation.mutations import CASES as MUTATION_CASES, evaluate_mutation
from app.evaluation.metrics import summarize
from app.evaluation.retrieval import evaluate_retrieval
from app.evaluation.severity import evaluate_severity

def build_evaluation_report()->dict:
    mutation_results=[evaluate_mutation(c) for c in MUTATION_CASES+EXTENDED_CASES]
    mutation=summarize(mutation_results)
    retrieval=evaluate_retrieval()
    severity=evaluate_severity()
    return {
      "status":"PASS" if mutation["failed"]==0 else "FAIL",
      "mutation":mutation,
      "retrieval":{"cases":retrieval["cases"],"hit_at_3":retrieval["hit_at_3"],"mrr":retrieval["mrr"]},
      "severity":{"cases":severity["cases"],"accuracy":severity["accuracy"],"confusion_matrix":severity["confusion_matrix"]},
      "details":{"mutation_failures":[r for r in mutation_results if not r["passed"]],"severity_cases":severity["results"]},
      "disclaimer":"Controlled engineering benchmarks; metrics are not production failure probabilities."
    }
