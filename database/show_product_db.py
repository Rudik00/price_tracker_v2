from sqlalchemy import select
from database.models_db import Product, User
from .create_db import SessionLocal


async def get_product_by_id(
    user_tg_id: str,
    local_id: int,
) -> tuple[Product | str, bool]:
    async with SessionLocal() as session:
        stmt = (
            select(Product, User.url, User.local_id)
            .join(User, User.id == Product.id_product)
            .where(
                User.telegram_id == user_tg_id,
                User.local_id == local_id,
            )
        )

        result = await session.execute(stmt)
        row = result.first()
        if row:
            product, url, user_local_id = row
            product.url = url
            product.local_id = user_local_id
            return product, True
        else:
            return (
                "Товар с таким ID не найден. "
                "Пожалуйста, проверьте ID и попробуйте снова.",
                False,
            )


async def get_product_by_url(
    user_id: str,
    url: str,
) -> tuple[Product | str, bool]:
    async with SessionLocal() as session:
        stmt = (
            select(Product, User.url, User.local_id)
            .join(User, User.id == Product.id_product)
            .where(
                User.telegram_id == user_id,
                User.url == url
            )
        )

        result = await session.execute(stmt)
        row = result.first()
        if row:
            product, url, user_local_id = row
            product.url = url
            product.local_id = user_local_id
            return product, True
        else:
            return (
                "Товар с такой ссылкой не найден. "
                "Пожалуйста, проверьте ссылку и попробуйте снова.",
                False,
            )
