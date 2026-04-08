import logging

from sqlalchemy import select
from .models_db import Product, User
from .create_db import SessionLocal


logger = logging.getLogger(__name__)


async def _renumber_local_ids(session, telegram_id: str) -> None:
    """Reassign local_id sequentially (1, 2, 3...) for a user's remaining rows.

    Called inside an already-open transaction.
    """
    stmt = (
        select(User)
        .where(User.telegram_id == telegram_id)
        .order_by(User.local_id)
    )
    result = await session.execute(stmt)
    remaining = result.scalars().all()

    for new_id, row in enumerate(remaining, start=1):
        if row.local_id != new_id:
            row.local_id = new_id

    logger.info(
        "Renumbered local_ids for telegram_id=%s count=%s",
        telegram_id,
        len(remaining),
    )


async def deleting_product_by_id(
    user_id: str,
    product_id: int,
) -> str:
    """Delete product and user row by telegram_id + local_id.

    1. Find users.id using (telegram_id, local_id).
    2. Delete from products where id_product == users.id.
    3. Delete from users.
    """
    async with SessionLocal() as session:
        async with session.begin():
            user_stmt = select(User).where(
                User.telegram_id == user_id,
                User.local_id == product_id,
            )
            user = await session.scalar(user_stmt)

            if user is None:
                logger.warning(
                    "Product not found telegram_id=%s local_id=%s",
                    user_id,
                    product_id,
                )
                return (
                    "Товар с таким ID не найден. "
                    "Пожалуйста, проверьте ID и попробуйте снова."
                )

            # 1. Найти запись в products по users.id
            product_stmt = select(Product).where(
                Product.id_product == user.id,
            )
            product = await session.scalar(product_stmt)

            # 2. Удалить из products
            if product is not None:
                await session.delete(product)

            # 3. Удалить из users
            await session.delete(user)
            await session.flush()

            # 4. Перенумеровать local_id у оставшихся товаров
            await _renumber_local_ids(session, user_id)

            logger.info(
                "Deleted telegram_id=%s local_id=%s users.id=%s",
                user_id,
                product_id,
                user.id,
            )
            return "Товар успешно удален."


async def deleting_product_by_url(
    user_id: str,
    url: str,
) -> str:
    """Delete product and user row by telegram_id + url.

    1. Find users.id using (telegram_id, url).
    2. Delete from products where id_product == users.id.
    3. Delete from users.
    """
    async with SessionLocal() as session:
        async with session.begin():
            user_stmt = select(User).where(
                User.telegram_id == user_id,
                User.url == url,
            )
            user = await session.scalar(user_stmt)

            if user is None:
                logger.warning(
                    "Product not found telegram_id=%s url=%s",
                    user_id,
                    url,
                )
                return (
                    "Товар с такой ссылкой не найден. "
                    "Пожалуйста, проверьте ссылку и попробуйте снова."
                )

            # 1. Найти запись в products по users.id
            product_stmt = select(Product).where(
                Product.id_product == user.id,
            )
            product = await session.scalar(product_stmt)

            # 2. Удалить из products
            if product is not None:
                await session.delete(product)

            # 3. Удалить из users
            await session.delete(user)
            await session.flush()

            # 4. Перенумеровать local_id у оставшихся товаров
            await _renumber_local_ids(session, user_id)

            logger.info(
                "Deleted telegram_id=%s url=%s users.id=%s",
                user_id,
                url,
                user.id,
            )
            return "Товар успешно удален."
