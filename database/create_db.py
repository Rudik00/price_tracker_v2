import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from database.models_db import Base


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
