from app.celery_app import celery_app as app
from app.mongo import db
from app.otel import (
    RedisInstrumentor,
    get_meter_provider,
    get_propagator,
    get_trace_provider,
)
from app.settings import settings
from meysam_utils import get_logger

RedisInstrumentor().instrument()

tracer = get_trace_provider(settings.WORKER_CELERY_NAME).get_tracer(__name__)
meter = get_meter_provider(settings.WORKER_CELERY_NAME).get_meter(__name__)
propagator = get_propagator()

logger = get_logger(__name__, level=settings.LOG_LEVEL)

total_requests = meter.create_counter(
    name="total_requests",
    description="Total requests",
    unit="1",
)


@app.task(name="hello")
def hello(name: str, *, context: dict = None) -> str:
    ctx = None
    if context:
        ctx = propagator.extract(context)

    total_requests.add(1, {"name": name})
    with tracer.start_as_current_span("worker.hello", context=ctx) as span:
        span.set_attribute("name", name)

        info = {"name": name}
        meta = {"$inc": {"count": 1}, "$set": {**info}}

        update_result = db.names.update_one(info, meta, upsert=True)

        span.set_attribute("update_result", update_result.acknowledged)

        logger.info(f"Hello {name}!")

        return f"Hello {name}!"
