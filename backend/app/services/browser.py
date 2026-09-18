from playwright.async_api import Route, async_playwright
from app.security.urls import UnsafeTargetError, validate_public_url

async def _guard_route(route: Route) -> None:
    try:
        await validate_public_url(route.request.url)
    except UnsafeTargetError:
        await route.abort("blockedbyclient")
        return
    await route.continue_()

async def capture_page(url: str, wait_until: str, timeout_ms: int) -> tuple[str, str]:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            context = await browser.new_context()
            await context.route("**/*", _guard_route)
            page = await context.new_page()
            response = await page.goto(url, wait_until=wait_until, timeout=timeout_ms)
            final_url = page.url
            await validate_public_url(final_url)
            if response is None:
                raise UnsafeTargetError("Navigation did not produce a valid public response")
            return await page.content(), await page.title()
        finally:
            await browser.close()
