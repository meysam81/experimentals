import os

from app.logger import get_logger

import dramatiq

logger = get_logger(__name__)


@dramatiq.actor(store_results=True, queue_name=os.getenv("QUEUE_NAME", "default"))
def add(x, y):
    return x + y


@dramatiq.actor(
    store_results=True,
    queue_name=os.getenv("QUEUE_NAME", "default"),
    throws=ZeroDivisionError,
)
def divide(x, y):
    return x / y


@dramatiq.actor(store_results=True, queue_name=os.getenv("QUEUE_NAME", "default"))
def count_words(text):
    logger.info(f"Counting words in {text}")
    return len(text.split()) if isinstance(text, str) else -1
