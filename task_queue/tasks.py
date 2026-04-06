import asyncio
import logging

from playwright.async_api import async_playwright

from database.add_or_update_price_db import add_or_update_product_price
from task_queue.celery_app import celery_app
from parser.wildberries.browser import _fetch_html_with_browser
from parser.wildberries.parser import _parse_price_from_html


logger = logging.getLogger(__name__)


async def _parse_wb_price(url: str) -> float:
    logger.info("Start parsing WB price for url=%s", url)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            html = await _fetch_html_with_browser(browser, url)
            price = _parse_price_from_html(html)
            if price is None:
                logger.warning("Price not found in html for url=%s", url)
                raise ValueError(f"Не удалось извлечь цену из {url}")
            logger.info("Parsed WB price=%s for url=%s", price, url)
            return float(price)
        finally:
            await browser.close()


async def _process_one_product(user_id: int, url: str) -> dict:
    logger.info("Process product started user_id=%s url=%s", user_id, url)
    price_now = await _parse_wb_price(url)
    product, flag = await add_or_update_product_price(
        user_id=user_id,
        price_now=price_now,
    )
    if flag:
        await user_id.send_message(
            chat_id=user_id,
            text=(
                f"Твой товар с id: {product.id_product} подешевел до {product.price_now} руб.\n"
                f"{product.url}"
            )
        )
    logger.info(
        "Process product finished user_id=%s id_product=%s price_now=%s",
        user_id,
        product.id_product,
        product.price_now,
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
    """Фоновая задача: проанализировать страницу товара
    и обновить таблицу товаров.
    """
    logger.info(
        "Celery task parse_and_store_price started task_id=%s user_id=%s",
        self.request.id,
        user_id,
    )
    return asyncio.run(_process_one_product(user_id=user_id, url=url))