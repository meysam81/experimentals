from app.config import config
from prometheus_client import start_http_server
from py_grpc_prometheus.prometheus_client_interceptor import (
    PromClientInterceptor,  # isort: skip
)
from app.logger import get_logger


logger = get_logger(__name__)


def serve():
    logger.info("Starting Prometheus ...")
    start_http_server(config.METRICS_PORT)
    logger.info(f"Prometheus started, listening on {config.METRICS_PORT}")
