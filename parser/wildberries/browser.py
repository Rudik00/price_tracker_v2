import logging

from playwright.async_api import async_playwright


logger = logging.getLogger(__name__)


async def run(url: str) -> str:
    async with async_playwright() as p:
        # для отладки можно запускать с headless=False, slow_mo=100
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            # открыть для отладки
            # await page.set_viewport_size({"width": 1280, "height": 800})
            await page.goto(url)
            await page.wait_for_timeout(5000)
            return await page.content()
        finally:
            await page.close()
            await browser.close()
