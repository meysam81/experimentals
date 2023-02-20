from app.config import config
from celery import Celery
from meysam_utils import get_logger

logger = get_logger(__name__)

app = Celery(
    __name__,
    broker=config.CELERY_BROKER,
    backend=config.CELERY_BACKEND,
    broker_transport_options=config.broker_transport_options,
)
app.config_from_object(config)


@app.task(name="greet")
def greet(name):
    logger.info(f"Greeting {name}")
    return f"Hello {name}!"
