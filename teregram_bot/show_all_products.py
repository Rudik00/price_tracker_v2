from aiogram.types import Message
from database.show_all_products_db import get_all_products_for_user


async def display_of_all_products_handler(message: Message) -> None:
    # Здесь будет логика для отображения всех продуктов, добавленных пользователем.
    # получаем из базы данных все товары для данного пользователя
    products = await get_all_products_for_user(str(message.from_user.id))

    if not isinstance(products, str):
        await message.answer("Вот товары которые ты добавил:\n")
        for product in products:
            await message.answer(
                f"ID: {product.id_product}\n"
                f"Текущая цена: {product.price_now}\n"
                f"Макс. цена: {product.price_max}\n"
                f"Мин. цена: {product.price_min}\n"
                f"Цена при добавлении: {product.price_start}\n"
                f"{product.url}"
            )

    else:
        await message.answer(products)

    return
