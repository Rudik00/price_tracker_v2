from aiogram.types import Message
from database.show_product_db import get_product_by_id, get_product_by_url


# вывод текста пользователю
async def _message_show_product(message: Message):
    await message.answer(
        "Вы выбрали показать товар по id или url.\n"
        "Пожалуйста, отправьте id или url товара."
    )


# ловит сообщение с id или url товара и показывает его пользователю
async def show_products_by_id_or_url_handler(message: Message):
    text = message.text.strip()

    if text.isdigit():
        text = int(text)
        product, _ = await get_product_by_id(str(message.from_user.id), text)

        if _:
            await message.answer(
                f"ID: {product.id_product}\n"
                f"Текущая цена: {product.price_now}\n"
                f"Макс. цена: {product.price_max}\n"
                f"Мин. цена: {product.price_min}\n"
                f"Цена при добавлении: {product.price_start}\n"
                f"{product.url}"
            )
        else:
            await message.answer(product)

    else:
        # здесь проверяем валидность ссылки
        if "wildberries" in text.lower():
            product, _ = await get_product_by_url(
                str(message.from_user.id), text
            )

            if _:
                await message.answer(
                    f"ID: {product.id_product}\n"
                    f"Текущая цена: {product.price_now}\n"
                    f"Макс. цена: {product.price_max}\n"
                    f"Мин. цена: {product.price_min}\n"
                    f"Цена при добавлении: {product.price_start}\n"
                    f"{product.url}"
                )
            else:
                await message.answer(product)

        else:
            await message.answer(
                "Такой ссылки нет в базе данных."
                "\nНажмите на команду /adding_by_link и добавь эту ссылку"
                "\nИли отправьте другую ссылку."
            )
            return
