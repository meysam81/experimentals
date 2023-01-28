import os

from app.logger import get_logger
from dramatiq.results import Results

import dramatiq

logger = get_logger(__name__)

if os.getenv("ENV", "DEV").lower() == "test":
    logger.info("Using stub broker")
    from dramatiq.brokers.stub import StubBroker
    from dramatiq.results.backends.stub import StubBackend

    broker = StubBroker()
    broker.emit_after("process_boot")
    broker.add_middleware(Results(backend=StubBackend()))
else:
    logger.info("Using redis broker")
    from dramatiq.brokers.redis import RedisBroker
    from dramatiq.results.backends.redis import RedisBackend

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    broker = RedisBroker(url=redis_url)
    broker.add_middleware(Results(backend=RedisBackend(url=redis_url)))


dramatiq.set_broker(broker)
