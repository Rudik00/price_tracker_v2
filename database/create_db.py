import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from database.models import Base, Product, User


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL не найден в .env")


# NullPool предотвращает повторное использование соединений asyncpg в разных циклах событий
# в задачах рабочих процессов Celery.
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    # Создайте таблицы users/products, если они еще не существуют.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def add_user_link(
    telegram_id: str,
    user_url: str,
) -> int:
    """
    Создайте новую строку пользователя и верните сгенерированный users.id.

    Вызовите ValueError, если у пользователя уже есть этот URL.
    """
    async with SessionLocal() as session:
        async with session.begin():
            existing_stmt = select(User).where(
                (User.telegram_id == telegram_id)
                & (User.url == user_url)
            )
            existing = await session.scalar(existing_stmt)
            if existing is not None:
                raise ValueError(
                    "У вас уже есть такой товар\n" \
                    f"Его ID для отслеживания = {existing.id}\n"
                )

            local_id_stmt = select(func.max(User.local_id)).where(
                User.telegram_id == telegram_id
            )
            current_max_local_id = await session.scalar(local_id_stmt)
            next_local_id = (current_max_local_id or 0) + 1

            user = User(
                telegram_id=telegram_id,
                local_id=next_local_id,
                url=user_url,
            )
            session.add(user)
            await session.flush()  # get user.id before commit
        return user.id


async def add_or_update_product_price(user_id: int, price_now: int) -> Product:
    """
    Создать или обновить строку товаров для заданного пользователя с указанным идентификатором.

    Правила:
    - id_product = users.id
    - price_now is always updated
    - if price_start is empty -> set price_start = price_now
    - if price_now > price_max -> price_max = price_now
    - if price_now < price_min -> price_min = price_now
    - time_added is updated to current time
    """
    async with SessionLocal() as session:
        async with session.begin():
            user = await session.get(User, user_id)
            if user is None:
                raise ValueError(
                    f"Пользователь с id={user_id} не найден в users"
                )

            stmt = select(Product).where(Product.id_product == user_id)
            existing = await session.scalar(stmt)
            # Если продукта еще нет, создаем новый. Иначе обновляем существующий.
            if existing is None:
                existing = Product(
                    id_product=user_id,
                    price_now=price_now,
                    price_start=price_now,
                    price_max=price_now,
                    price_min=price_now,
                    time_added=datetime.utcnow(),
                )
                session.add(existing)
                await session.flush()
                return existing
            # обновляем существующий продукт
            existing.price_now = price_now
            if existing.price_start is None:
                existing.price_start = price_now
            if existing.price_max is None or price_now > existing.price_max:
                existing.price_max = price_now
            if existing.price_min is None or price_now < existing.price_min:
                existing.price_min = price_now
            existing.time_added = datetime.utcnow()
            await session.flush()
            return existing
