from aiogram.types import Message

from database.add_users import add_user_link
from task_queue.tasks import parse_and_store_price


# при вызове команды
async def adding_by_link_handler(message: Message):
    await message.answer(
        "Вы выбрали добавление продукта по ссылке. "
        "Пожалуйста, отправьте ссылку."
    )


# при ответе пользователя с ссылкой на товар
async def add_user_url_handler(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        await message.answer("Не удалось определить ваш user_id.")
        return

    url = message.text.strip() if message.text else None
    if not url:
        await message.answer(
            "Эта ссылка не корректна."
            "\nНажмите на команду /adding_by_link"
            "\nИ отправьте другую ссылку."
        )
        return

    # здесь проверяем валидность ссылки
    if "wildberries" not in url.lower():
        await message.answer(
            "Эта ссылка не подходит ни к одному сайту."
            "\nНажмите на команду /adding_by_link"
            "\nИ отправьте другую ссылку."
        )
        return

    # добавляем пользователя и товар в базу данных
    try:
        created_id = await add_user_link(
            telegram_id=str(user_id),
            user_url=url,
        )

        # Фоновая задача: парсинг ссылки + обновление products.
        task = parse_and_store_price.delay(created_id, url)

        await message.answer(
            "Ваша ссылка добавлена."
            f"\nID для отслеживания = {created_id}"
            f"\nИли по ссылке url={url}"
        )

        await message.answer(
            "Совсем скоро товар добавиться в список отслеживаемых"
            "\nПосле чего вы сможете использовать команду \n/show_one_products"
        )

    except ValueError as exc:
        await message.answer(str(exc))

