from playwright.async_api import async_playwright

async def capture_page(url: str, wait_until: str, timeout_ms: int) -> tuple[str, str]:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.goto(url, wait_until=wait_until, timeout=timeout_ms)
            return await page.content(), await page.title()
        finally:
            await browser.close()
