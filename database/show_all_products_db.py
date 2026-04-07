from sqlalchemy import select
from database.models_db import Product, User
from .create_db import SessionLocal


async def get_all_products_for_user(user_id: str):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Product, User.url, User.local_id)
            .join(User, User.id == Product.id_product)
            .where(User.telegram_id == user_id)
        )
        rows = result.all()

        # Attach url to each Product object
        products = []
        if rows:
            for product, url, local_id in rows:
                product.url = url
                product.local_id = local_id
                products.append(product)

            return products

        else:
            return (
                "У вас пока нет добавленных товаров. "
                "Нажмите на команду /adding_by_link и добавьте товар "
                "по ссылке."
            )
