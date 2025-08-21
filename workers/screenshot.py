# NO LONGER USED
from playwright.async_api import async_playwright


async def screenshot(
    url: str, width: int = 1000, height: int = 750, scale: int = 1
) -> bytes:
    """
    Render a chart from a URL and return the screenshot as bytes.
    """
    async with async_playwright() as p:
        # Load URL in a headless browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=scale,  # Retina resolution
        )
        page = await context.new_page()
        await page.set_viewport_size({"width": width, "height": height})
        await page.goto(url, wait_until="networkidle")

        # Wait for the chart's canvas to be visible
        await page.wait_for_selector("#the-chart", state="visible", timeout=60000)

        # Take a screenshot of the specific chart canvas element
        chart_element = page.locator("#the-chart")
        png_bytes = await chart_element.screenshot()

        await browser.close()
        return png_bytes
