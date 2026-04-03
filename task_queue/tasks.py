import asyncio

from playwright.async_api import async_playwright

from database.create_db import add_or_update_product_price
from task_queue.celery_app import celery_app
from website.wildberries.browser import _fetch_html_with_browser
from website.wildberries.parser import _parse_price_from_html



async def _parse_wb_price(url: str) -> int:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            html = await _fetch_html_with_browser(browser, url)
            price = _parse_price_from_html(html)
            if price is None:
                raise ValueError(f"Не удалось извлечь цену из {url}")
            return int(round(price))
        finally:
            await browser.close()


async def _process_one_product(user_id: int, url: str) -> dict:
    price_now = await _parse_wb_price(url)
    product = await add_or_update_product_price(
        user_id=user_id,
        price_now=price_now,
    )
    return {
        "user_id": user_id,
        "id_product": product.id_product,
        "price_now": product.price_now,
        "price_start": product.price_start,
        "price_max": product.price_max,
        "price_min": product.price_min,
    }


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def parse_and_store_price(self, user_id: int, url: str) -> dict:
    """Фоновая задача: проанализировать страницу товара и обновить таблицу товаров."""
    return asyncio.run(_process_one_product(user_id=user_id, url=url))
