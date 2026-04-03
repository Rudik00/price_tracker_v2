from aiogram.types import Message


async def deleting_product_by_id_or_url_handler(message: Message):
    # Здесь будет логика для удаления продукта по ID или URL
    await message.answer("Ты и тут нажимаешь?🥺")
    # await message.answer("Вы выбрали удаление товара по ID или URL. Пожалуйста, введите ID или URL товара, который вы хотите удалить.")
