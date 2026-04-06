from sqlalchemy import select
from database.models import Product, User
from .create_db import SessionLocal


async def get_product_by_id(user_id: str, id_product: int) -> list[Product] | str:
    async with SessionLocal() as session:
        stmt = select(Product, User.url).join(
            User, User.id == Product.id_product
            ).where(
                User.telegram_id == user_id,
                Product.id_product == id_product
            )

        result = await session.execute(stmt)
        row = result.first()
        if row:
            product, url = row
            product.url = url
            return product, True
        else:
            return "Товар с таким ID не найден. Пожалуйста, проверьте ID и попробуйте снова.", False


async def get_product_by_url(user_id: str, url: str) -> list[Product] | str:
    async with SessionLocal() as session:
        stmt = select(Product, User.url).join(
            User, User.id == Product.id_product
            ).where(
                User.telegram_id == user_id,
                User.url == url
            )

        result = await session.execute(stmt)
        row = result.first()
        if row:
            product, url = row
            product.url = url
            return product, True
        else:
            return "Товар с такой ссылкой не найден. Пожалуйста, проверьте ссылку и попробуйте снова.", False
