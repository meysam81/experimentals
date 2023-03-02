from functools import lru_cache

from app.settings import settings
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import Span, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


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
    meter_reader = PeriodicExportingMetricReader(ConsoleMetricExporter(), 60_000)
    meter_provider = MeterProvider(
        metric_readers=[meter_reader],
        resource=Resource.create({SERVICE_NAME: service_name}),
    )
    metrics.set_meter_provider(meter_provider)

    return meter_provider


def get_propagator():
    return TraceContextTextMapPropagator()
