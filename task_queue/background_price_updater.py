import asyncio
import logging

from sqlalchemy import select

from database.create_db import SessionLocal
from database.models_db import User
from task_queue.tasks import parse_and_store_price

logger = logging.getLogger(__name__)

UPDATE_INTERVAL_SECONDS = 2 * 60 * 60


async def enqueue_all_price_updates() -> None:
    """Read all tracked URLs from Users and enqueue Celery tasks."""
    async with SessionLocal() as session:
        stmt = select(User.id, User.url)
        result = await session.execute(stmt)
        rows = result.all()

    if not rows:
        logger.info("Background update skipped: no users found")
        return

    logger.info("Background update started for %s tracked products", len(rows))

    for user_id, url in rows:
        parse_and_store_price.delay(user_id=user_id, url=url)
        logger.info(
            "Queued background price update user_id=%s url=%s",
            user_id,
            url,
        )

    logger.info("Background update queued %s tasks", len(rows))


async def run_periodic_price_updates(
    interval_seconds: int = UPDATE_INTERVAL_SECONDS,
) -> None:
    """Run background price refresh forever with a fixed interval."""
    while True:
        try:
            await enqueue_all_price_updates()
        except asyncio.CancelledError:
            logger.info("Background price updater cancelled")
            raise
        except Exception:
            logger.exception("Background price updater failed")

        await asyncio.sleep(interval_seconds)

