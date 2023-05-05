# flake8: noqa

from app.settings import settings
from meysam_utils import get_logger
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.dbapi import DatabaseApiIntegration
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor
from opentelemetry.instrumentation.urllib import URLLibInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor
from opentelemetry.instrumentation.wsgi import OpenTelemetryMiddleware
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter as _ConsoleMetricExporter,
)
from opentelemetry.sdk.metrics.export import (
    MetricExportResult,
    MetricsData,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from opentelemetry import metrics, trace

logger = get_logger(__name__, level=settings.LOG_LEVEL)


class ConsoleMetricExporter(_ConsoleMetricExporter):
    def export(
        self, metrics: MetricsData, timeout_millis: int = None
    ) -> MetricExportResult:
        logger.debug(metrics)
        return MetricExportResult.SUCCESS


def get_trace_provider(service_name: str):
    tracer_provider = TracerProvider(
        resource=Resource.create({SERVICE_NAME: service_name}),
        active_span_processor=BatchSpanProcessor(
            OTLPSpanExporter(endpoint=settings.OTLP_EXPORTER_ENDPOINT)
        ),
    )
    trace.set_tracer_provider(tracer_provider)

    return tracer_provider


def get_meter_provider(service_name: str):
    # exporter = PrometheusRemoteWriteMetricsExporter(
    #     endpoint="http://localhost:9090/api/prom/push",
    #     headers={"X-Scope-Org-ID": "1"},
    # )
    # meter_reader = PeriodicExportingMetricReader(exporter, 1000)
    # meter_provider = MeterProvider(
    #     metric_readers=[meter_reader],
    #     resource=Resource.create({SERVICE_NAME: service_name}),
    # )

    PeriodicExportingMetricReader(ConsoleMetricExporter(), 60_000)
    meter_provider = MeterProvider(
        # metric_readers=[],
        resource=Resource.create({SERVICE_NAME: service_name}),
    )
    metrics.set_meter_provider(meter_provider)

    return meter_provider


def get_propagator():
    return TraceContextTextMapPropagator()


_system_metrics_config = {
    "system.memory.usage": ["used", "free", "cached"],
    "system.cpu.time": ["idle", "user", "system", "irq"],
    "system.network.io": ["transmit", "receive"],
    "runtime.memory": ["rss", "vms"],
    "runtime.cpu.time": ["user", "system"],
}


def _strip_query_params(url: str) -> str:
    return url.split("?")[0]


_instrumentations = (
    (settings.CELERY_INSTRUMENTATION, CeleryInstrumentor),
    (settings.DATABASE_API_INSTRUMENTATION, DatabaseApiIntegration),
    (settings.FASTAPI_INSTRUMENTATION, FastAPIInstrumentor),
    (settings.FLASK_INSTRUMENTATION, FlaskInstrumentor),
    (settings.HTTPX_INSTRUMENTATION, HTTPXClientInstrumentor),
    (
        settings.LOGGING_INSTRUMENTATION,
        (
            LoggingInstrumentor,
            {"set_logging_format": True},
        ),
    ),
    (settings.PYMONGO_INSTRUMENTATION, PymongoInstrumentor),
    (settings.REDIS_INSTRUMENTATION, RedisInstrumentor),
    (settings.REQUESTS_INSTRUMENTATION, RequestsInstrumentor),
    (
        settings.SYSTEM_METRICS_INSTRUMENTATION,
        (
            SystemMetricsInstrumentor,
            _system_metrics_config,
        ),
    ),
    (settings.URLLIB_INSTRUMENTATION, URLLibInstrumentor),
    (
        settings.URLLIB3_INSTRUMENTATION,
        (
            URLLib3Instrumentor,
            {"strip_query_params": _strip_query_params},
        ),
    ),
    (settings.WSGI_INSTRUMENTATION, OpenTelemetryMiddleware),
)


def instrument():
    for enabled, instrumentation in _instrumentations:
        kwargs = {}
        if isinstance(instrumentation, tuple):
            instrumentation, kwargs = instrumentation

        if not enabled:
            continue

        try:
            instrumentation().instrument(**kwargs)
        except Exception as e:
            logger.error(f"Failed to instrument: {instrumentation.__name__}", e)
