from app.settings import settings
from dramatiq.brokers.redis import RedisBroker

import dramatiq

broker = RedisBroker(url=settings.DRAMATIQ_BROKER_URL)
dramatiq.set_broker(broker)
