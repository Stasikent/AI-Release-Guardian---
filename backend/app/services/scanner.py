from app.analyzers.dom import count_by_type, extract_testable_objects
from app.models.scan import ScanRequest, ScanResult
from app.services.browser import capture_page

async def scan_page(request: ScanRequest) -> ScanResult:
    url = str(request.url)
    html, title = await capture_page(url, request.wait_until, request.timeout_ms)
    objects = extract_testable_objects(html)
    return ScanResult(
        url=url,
        title=title,
        total_testable_objects=len(objects),
        object_counts=count_by_type(objects),
        testable_objects=objects,
    )
