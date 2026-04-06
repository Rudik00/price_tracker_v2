import asyncio
import logging

from playwright.async_api import async_playwright
from rich.progress import Progress
from .load_products_db import _load_products
from .database_entry import check_price


logger = logging.getLogger(__name__)


async def parser_products_main(products: list[dict]) -> None:
    """Точка входа: загрузка продуктов и одновременное выполнение всех проверок."""
    logger.info("Found %s products to check", len(products))

    # Ограничьте количество одновременно работающих сайтов
    semaphore = asyncio.Semaphore(10)

    with Progress() as progress:
        task = progress.add_task("Checking prices", total=len(products))

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)

            async def guarded_check(product: dict):
                async with semaphore:
                    await check_price(product, browser)
                    progress.update(task, advance=1)

            # Создаем задачи
            tasks = [guarded_check(p) for p in products]

            await asyncio.gather(*tasks)


if __name__ == "__main__":
    products = _load_products()
    asyncio.run(parser_products_main(products))
