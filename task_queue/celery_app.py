import os

from celery import Celery
from dotenv import load_dotenv


load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

celery_app = Celery(
    "price_tracker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["task_queue.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
