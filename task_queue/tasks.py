import asyncio
import logging

from database.add_or_update_price_db import add_or_update_product_price
from task_queue.celery_app import celery_app
from parser.wildberries.parser import _parse_price_from_html

from parser.wildberries.browser_2 import run

from dotenv import load_dotenv
from aiogram import Bot
import os


logger = logging.getLogger(__name__)


async def _parse_wb_price(url: str) -> tuple[float, str | None, str | None]:
    logger.info("Start parsing WB price for url=%s", url)
    # достаём HTML с помощью браузера
    html = await run(url)
    # парсим цену из HTML
    price, currency, img = _parse_price_from_html(html)
    if price is None:
        logger.warning("Price not found in html for url=%s", url)
        raise ValueError(f"Не удалось извлечь цену из {url}")
    logger.info("Parsed WB price=%s %s for url=%s", price, currency, url)
    return float(price), currency, img


async def _process_one_product(user_id: int, url: str) -> dict:
    logger.info("Process product started user_id=%s url=%s", user_id, url)
    price_now, currency, img = await _parse_wb_price(url)
    product, price_dropped, telegram_id, local_id, img = (
        await add_or_update_product_price(
            user_id=user_id,
            price_now=price_now,
            currency=currency,
            img=img
        )
    )

    if price_dropped:
        # Если цена снизилась, отправляем уведомление пользователю.
        await show_message(
            telegram_id=telegram_id,
            url=url,
            local_id=local_id,
            img=img
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
        "price_now": str(product.price_now),
        "price_start": str(product.price_start),
        "price_max": str(product.price_max),
        "price_min": str(product.price_min),
        "currency": currency,
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
    result = asyncio.run(_process_one_product(user_id=user_id, url=url))
    return result


async def show_message(telegram_id: str, url: str, local_id: int, img: str | None) -> None:
    load_dotenv()  # читает .env
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env")
    bot = Bot(token=token)
    await bot.send_message(
        chat_id=telegram_id,
        text=(
            f"{img}\n"
            f"Твой товар c ID = {local_id} подешевел.\n"
            f"{url}"
        )
    )
    await bot.close()
