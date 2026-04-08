import hashlib
import hmac
import json
import os
import time
from decimal import Decimal
from pathlib import Path
from urllib.parse import parse_qsl

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import select

from database.create_db import SessionLocal, init_db
from database.models_db import Product, User


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"

app = FastAPI(title="Price Tracker Mini App API")
router = APIRouter(prefix="/api", tags=["mini-app"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InitDataPayload(BaseModel):
    init_data: str = Field(min_length=1)


class ProductOut(BaseModel):
    local_id: int
    url: str
    currency: str | None
    img: str | None
    price_now: str | None
    price_start: str | None
    price_max: str | None
    price_min: str | None
    time_added: str | None


class ProductsResponse(BaseModel):
    telegram_id: str
    products: list[ProductOut]


def _decimal_to_str(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return str(value)


def _validate_telegram_init_data(init_data: str) -> str:
    if not BOT_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="TELEGRAM_BOT_TOKEN is not configured",
        )

    data_pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = data_pairs.pop("hash", None)

    if not received_hash:
        raise HTTPException(status_code=401, detail="Missing hash in initData")

    auth_date = data_pairs.get("auth_date")
    if auth_date and auth_date.isdigit():
        now = int(time.time())
        if now - int(auth_date) > 60 * 60 * 24:
            raise HTTPException(status_code=401, detail="initData is too old")

    data_check_string = "\n".join(
        f"{key}={value}"
        for key, value in sorted(data_pairs.items(), key=lambda item: item[0])
    )

    secret_key = hmac.new(
        key=b"WebAppData",
        msg=BOT_TOKEN.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()

    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid initData signature",
        )

    user_raw = data_pairs.get("user")
    if not user_raw:
        raise HTTPException(
            status_code=401,
            detail="No user field in initData",
        )

    try:
        user_data = json.loads(user_raw)
        telegram_id = str(user_data["id"])
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid user payload",
        ) from exc

    return telegram_id


@app.on_event("startup")
async def _startup() -> None:
    await init_db()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/products", response_model=ProductsResponse)
async def get_products(payload: InitDataPayload) -> ProductsResponse:
    telegram_id = _validate_telegram_init_data(payload.init_data)

    async with SessionLocal() as session:
        stmt = (
            select(
                User.local_id,
                User.url,
                Product.currency,
                Product.img,
                Product.price_now,
                Product.price_start,
                Product.price_max,
                Product.price_min,
                Product.time_added,
            )
            .outerjoin(Product, Product.id_product == User.id)
            .where(User.telegram_id == telegram_id)
            .order_by(User.local_id)
        )
        result = await session.execute(stmt)
        rows = result.all()

    products = [
        ProductOut(
            local_id=local_id,
            url=url,
            currency=currency,
            img=img,
            price_now=_decimal_to_str(price_now),
            price_start=_decimal_to_str(price_start),
            price_max=_decimal_to_str(price_max),
            price_min=_decimal_to_str(price_min),
            time_added=time_added.isoformat() if time_added else None,
        )
        for (
            local_id,
            url,
            currency,
            img,
            price_now,
            price_start,
            price_max,
            price_min,
            time_added,
        ) in rows
    ]

    return ProductsResponse(telegram_id=telegram_id, products=products)


app.include_router(router)

if FRONTEND_DIR.exists():
    app.mount(
        "/frontend",
        StaticFiles(directory=str(FRONTEND_DIR), html=True),
        name="frontend",
    )


@app.get("/")
async def mini_app_index() -> FileResponse:
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(
            status_code=404,
            detail="frontend/index.html not found",
        )
    return FileResponse(index_path)
