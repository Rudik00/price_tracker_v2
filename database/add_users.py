from sqlalchemy import select, func

from database.models import User
from .create_db import SessionLocal


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
