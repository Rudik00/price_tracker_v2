from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(String, nullable=False)
    local_id = Column(Integer, nullable=False)
    url = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("telegram_id", "url", name="uq_telegram_id_url"),
        UniqueConstraint(
            "telegram_id",
            "local_id",
            name="uq_telegram_id_local_id",
        ),
    )

    product = relationship(
        "Product",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Product(Base):
    __tablename__ = "products"

    # products.id_product хранит тот же id, что и users.id
    id_product = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    price_now = Column(Numeric(10, 2), nullable=True)
    price_start = Column(Numeric(10, 2), nullable=True)
    price_max = Column(Numeric(10, 2), nullable=True)
    price_min = Column(Numeric(10, 2), nullable=True)
    currency = Column(String, nullable=True)
    img = Column(String, nullable=True)
    time_added = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="product")
