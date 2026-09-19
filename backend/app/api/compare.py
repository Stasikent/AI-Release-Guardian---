from fastapi import APIRouter
from app.analyzers.diff import compare_objects
from app.models.diff import CompareRequest, CompareResult
from app.risk.engine import calculate_risk
from app.risk.focus import build_regression_focus

router = APIRouter(prefix="/api/v1/compare", tags=["compare"])

@router.post("", response_model=CompareResult)
def compare_scans(request: CompareRequest) -> CompareResult:
    diff = compare_objects(request.baseline, request.current)
    risk=calculate_risk(diff)
    return CompareResult(diff=diff, risk=risk, regression_focus=build_regression_focus(diff))
