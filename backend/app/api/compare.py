from fastapi import APIRouter
from app.analyzers.diff import compare_objects
from app.models.diff import CompareRequest, CompareResult
from app.risk.engine import calculate_risk

router = APIRouter(prefix="/api/v1/compare", tags=["compare"])

@router.post("", response_model=CompareResult)
def compare_scans(request: CompareRequest) -> CompareResult:
    diff = compare_objects(request.baseline, request.current)
    return CompareResult(diff=diff, risk=calculate_risk(diff))
