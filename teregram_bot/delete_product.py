from aiogram.types import Message

from database.deleting_product_db import deleting_product_by_id, deleting_product_by_url


async def deleting_product_(message: Message):
    await message.answer(
        "Вы выбрали удаление продукта по ссылке или id. "
        "Пожалуйста, отправьте ссылку или id товара который хотите удалить."
    )


async def deleting_product_id_or_url(message: Message) -> None:
    text = message.text.strip()

    if text.isdigit():
        text = int(text)
        result = await deleting_product_by_id(str(message.from_user.id), text)
        await message.answer(result)

    else:
        # здесь проверяем валидность ссылки
        if "wildberries" in text.lower():
            result = await deleting_product_by_url(
                str(message.from_user.id),
                text,
            )
            await message.answer(result)

        else:
            await message.answer(
                "Такой ссылки нет в базе данных."
                "\nНажмите на команду /adding_by_link и добавь эту ссылку"
                "\nИли отправьте другую ссылку."
            )
            return
