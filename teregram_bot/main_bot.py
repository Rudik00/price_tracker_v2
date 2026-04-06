import os
import asyncio
import logging

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from database.create_db import init_db
from .adding_products import adding_by_link_handler, add_user_url_handler
from .show_product import show_products_by_id_or_url_handler
from .show_all_products import display_of_all_products_handler
from .delete_product import deleting_product_by_id_or_url_handler


class AddProductState(StatesGroup):
    waiting_url = State()


dp = Dispatcher(storage=MemoryStorage())

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


def get_token() -> str:
    load_dotenv()  # читает .env
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env")
    return token


async def main_tg_bot(token: str):
    await init_db()
    bot = Bot(token=token)
    await dp.start_polling(bot)


@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Привет! Я бот 👋")


@dp.message(Command("info"))
async def info_handler(message: Message):
    await message.answer(
        "Я бот для отслеживания цен на товары которые ты добавишь.\n"
        "Сейчас я могу следить за ценой на Wildberries.\n"
        "Скоро будет больше!💪"
    )

#                         добавление товара по ссылке
# ________________________________________________________________________________________

# при вызове команды /adding_by_link
# бот попросит пользователя отправить ссылку на товар


@dp.message(Command("adding_by_link"))
async def adding_by_link(message: Message, state: FSMContext):
    await adding_by_link_handler(message)
    await state.set_state(AddProductState.waiting_url)


# ловит сообщение с ссылкой на товар


@dp.message(AddProductState.waiting_url)
async def add_user_url(message: Message, state: FSMContext):
    await add_user_url_handler(message)
    await state.clear()


# ________________________________________________________________________________________

#                       показать товар по id или url

@dp.message(Command("show_one_products"))
async def show_one_products(message: Message):
    await show_products_by_id_or_url_handler(message)


# ________________________________________________________________________________________

#                       показать все товары

@dp.message(Command("show_all_products"))
async def show_all_products(message: Message):
    await display_of_all_products_handler(message)


# ________________________________________________________________________________________

#                       удалить товар по id или url

@dp.message(Command("delete_product_by_id_or_url"))
async def delete_product_by_id_or_url(message: Message):
    await deleting_product_by_id_or_url_handler(message)


if __name__ == "__main__":
    token = get_token()
    asyncio.run(main_tg_bot(token))
