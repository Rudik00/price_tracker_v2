import logging
from decimal import Decimal, ROUND_HALF_UP

from .create_db import SessionLocal
from sqlalchemy import select
from datetime import datetime
from database.models_db import Product, User


logger = logging.getLogger(__name__)


def _to_money(value: float | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


async def add_or_update_product_price(
    user_id: int,
    price_now: float | Decimal,
    currency: str | None = None,
    img: str | None = None,
) -> tuple[Product, bool, str, int]:
    """
    Создать или обновить строку товаров
    для заданного пользователя с указанным идентификатором.

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
            normalized_price = _to_money(price_now)
            logger.info(
                "DB upsert started user_id=%s price_now=%s",
                user_id,
                normalized_price,
            )
            user = await session.get(User, user_id)
            if user is None:
                logger.error(
                    "User not found in users table user_id=%s",
                    user_id,
                )
                raise ValueError(
                    f"Пользователь с id={user_id} не найден в users"
                )

            stmt = select(Product).where(Product.id_product == user_id)
            existing = await session.scalar(stmt)
            # Если продукта еще нет, создаем новый.
            # Иначе обновляем существующий.
            if existing is None:
                existing = Product(
                    id_product=user_id,
                    price_now=normalized_price,
                    price_start=normalized_price,
                    price_max=normalized_price,
                    price_min=normalized_price,
                    currency=currency,
                    img=img,
                    time_added=datetime.utcnow(),
                )
                session.add(existing)
                await session.flush()
                logger.info(
                    "DB upsert created id_product=%s price_now=%s",
                    existing.id_product,
                    existing.price_now,
                )
                return existing, False, user.telegram_id, user.local_id
            # обновляем существующий продукт
            previous_price = existing.price_now
            price_dropped = (
                previous_price is not None
                and normalized_price < previous_price
            )
            existing.price_now = normalized_price
            if currency is not None:
                existing.currency = currency
            if existing.price_start is None:
                existing.price_start = normalized_price
            if (
                existing.price_max is None
                or normalized_price > existing.price_max
            ):
                existing.price_max = normalized_price
            if (
                existing.price_min is None
                or normalized_price < existing.price_min
            ):
                existing.price_min = normalized_price
            existing.time_added = datetime.utcnow()
            await session.flush()
            logger.info(
                (
                    "DB upsert updated id_product=%s "
                    "price_now=%s price_min=%s price_max=%s"
                ),
                existing.id_product,
                existing.price_now,
                existing.price_min,
                existing.price_max,
                existing.currency,
                existing.img,
            )
            return existing, price_dropped, user.telegram_id, user.local_id, img
