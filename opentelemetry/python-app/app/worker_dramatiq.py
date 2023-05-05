from app.dramatiq_app import broker
from app.otel import get_meter_provider, get_propagator, get_trace_provider, instrument
from app.settings import settings
from meysam_utils import get_logger

import dramatiq

trace = get_trace_provider(settings.WORKER_DRAMATIQ_NAME).get_tracer(__name__)
meter = get_meter_provider(settings.WORKER_DRAMATIQ_NAME).get_meter(__name__)
propagator = get_propagator()
instrument()

logger = get_logger(__name__)

total_requests = meter.create_counter(
    name="total_requests",
    description="Total requests",
    unit="1",
)


@dramatiq.actor(broker=broker)
def hello(name: str, context: dict = None):
    total_requests.add(1, {"name": name})
    ctx = None
    if context:
        ctx = propagator.extract(context)

    with trace.start_as_current_span("dramatiq.hello", context=ctx) as span:
        span.set_attribute("name", name)

        logger.info(f"Hello, {name}!")

        return f"Hello, {name}!"
