import logging

from sqlalchemy import select
from .models_db import User
from .create_db import SessionLocal


logger = logging.getLogger(__name__)


async def deleting_product_by_id(
    user_id: str,
    product_id: int,
) -> str:
    """Delete user product and associated price data by product ID.

    Deletes User row, which cascades to Product deletion.
    """
    async with SessionLocal() as session:
        async with session.begin():
            stmt = select(User).where(
                User.telegram_id == user_id,
                User.id == product_id,
            )

            user = await session.scalar(stmt)
            if user:
                await session.delete(user)
                logger.info(
                    "Deleted user product telegram_id=%s product_id=%s",
                    user_id,
                    product_id,
                )
                return "Товар успешно удален."
            else:
                logger.warning(
                    "Product not found telegram_id=%s product_id=%s",
                    user_id,
                    product_id,
                )
                return (
                    "Товар с таким ID не найден. "
                    "Пожалуйста, проверьте ID и попробуйте снова."
                )


async def deleting_product_by_url(
    user_id: str,
    url: str,
) -> str:
    """Delete user product and associated price data by URL.

    Deletes User row, which cascades to Product deletion.
    """
    async with SessionLocal() as session:
        async with session.begin():
            stmt = select(User).where(
                User.telegram_id == user_id,
                User.url == url,
            )

            user = await session.scalar(stmt)
            if user:
                await session.delete(user)
                logger.info(
                    "Deleted user product telegram_id=%s url=%s",
                    user_id,
                    url,
                )
                return "Товар успешно удален."
            else:
                logger.warning(
                    "Product not found telegram_id=%s url=%s",
                    user_id,
                    url,
                )
                return (
                    "Товар с такой ссылкой не найден. "
                    "Пожалуйста, проверьте ссылку и попробуйте снова."
                )
