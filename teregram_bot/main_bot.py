import os
import asyncio

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from adding_products import adding_by_link_handler
from show_product import show_products_by_id_or_url_handler
from show_all_products import display_of_all_products_handler
from delete_product import deleting_product_by_id_or_url_handler


dp = Dispatcher()


def get_token() -> str:
    load_dotenv()  # читает .env
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env")
    return token


async def main_tg_bot(token: str):
    bot = Bot(token=token)
    await dp.start_polling(bot)


@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Привет! Я бот 👋")


@dp.message(Command("adding_by_link"))
async def adding_by_link(message: Message):
    await adding_by_link_handler(message)


@dp.message(Command("show_one_products"))
async def show_one_products(message: Message):
    await show_products_by_id_or_url_handler(message)


@dp.message(Command("show_all_products"))
async def show_all_products(message: Message):
    await display_of_all_products_handler(message)


@dp.message(Command("delete_product_by_id_or_url"))
async def delete_product_by_id_or_url(message: Message):
    await deleting_product_by_id_or_url_handler(message)


if __name__ == "__main__":
    token = get_token()
    asyncio.run(main_tg_bot(token))
