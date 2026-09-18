from fastapi import APIRouter, HTTPException
from playwright.async_api import Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError

from app.models.scan import ScanRequest, ScanResult
from app.services.scanner import scan_page

router = APIRouter(prefix="/api/v1/scans", tags=["scans"])

@router.post("", response_model=ScanResult)
async def create_scan(request: ScanRequest) -> ScanResult:
    try:
        return await scan_page(request)
    except PlaywrightTimeoutError as exc:
        raise HTTPException(status_code=504, detail="Target page timed out") from exc
    except PlaywrightError as exc:
        raise HTTPException(status_code=502, detail=f"Browser scan failed: {exc}") from exc
