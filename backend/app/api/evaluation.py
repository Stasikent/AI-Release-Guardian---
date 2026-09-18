from fastapi import APIRouter
from app.evaluation.metrics import summarize
from app.evaluation.mutations import CASES,evaluate_mutation

router=APIRouter(prefix="/api/v1/evaluation",tags=["evaluation"])

@router.get("/mutations")
def mutation_evaluation()->dict:
    results=[evaluate_mutation(case) for case in CASES]
    return {"summary":summarize(results),"results":results}
