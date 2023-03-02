import dramatiq
from app.settings import settings
from dramatiq.brokers.redis import RedisBroker
from dramatiq.message import Message

broker = RedisBroker(url=settings.DRAMATIQ_BROKER_URL)
dramatiq.set_broker(broker)
