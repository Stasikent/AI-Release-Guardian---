from fastapi import APIRouter
from app.evaluation.dataset import EXTENDED_CASES
from app.evaluation.metrics import summarize
from app.evaluation.mutations import CASES,evaluate_mutation
from app.evaluation.retrieval import evaluate_retrieval

router=APIRouter(prefix="/api/v1/evaluation",tags=["evaluation"])

@router.get("/mutations")
def mutation_evaluation()->dict:
    results=[evaluate_mutation(case) for case in CASES+EXTENDED_CASES]
    return {"summary":summarize(results),"results":results}

@router.get("/retrieval")
def retrieval_evaluation()->dict:
    return evaluate_retrieval()
