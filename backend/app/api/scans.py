from fastapi import APIRouter, HTTPException
from playwright.async_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError
from app.models.scan import ScanRequest, ScanResult
from app.security.urls import UnsafeTargetError
from app.services.scanner import scan_page

router=APIRouter(prefix="/api/v1/scans",tags=["scans"])

@router.post("",response_model=ScanResult)
async def create_scan(request:ScanRequest)->ScanResult:
    try:
        return await scan_page(request)
    except UnsafeTargetError as exc:
        raise HTTPException(status_code=400,detail=str(exc)) from exc
    except PlaywrightTimeoutError as exc:
        raise HTTPException(status_code=504,detail="Target page timed out") from exc
    except PlaywrightError as exc:
        raise HTTPException(status_code=502,detail="Browser scan failed") from exc
