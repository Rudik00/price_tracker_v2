from aiogram.types import Message


async def adding_by_link_handler(message: Message):
    # Здесь будет логика для добавления продукта по ссылке или ID
    await message.answer("Вы выбрали добавление продукта по ссылке или ID. Пожалуйста, отправьте ссылку или ID продукта.")
