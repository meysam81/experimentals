import pytest
from app.broker import broker

from dramatiq import Worker


@pytest.fixture()
def stub_broker():
    broker.flush_all()
    return broker


@pytest.fixture()
def stub_worker():
    worker = Worker(broker, worker_timeout=5)
    worker.start()
    yield worker
    worker.stop()
