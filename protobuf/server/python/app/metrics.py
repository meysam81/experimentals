from app.config import config
from meysam_utils import get_logger
from prometheus_client import start_http_server
from py_grpc_prometheus.prometheus_server_interceptor import (
    PromServerInterceptor,  # isort: skip
)

logger = get_logger(__name__)


def serve():
    logger.info("Starting Prometheus ...")
    start_http_server(config.METRICS_PORT)
    logger.info(f"Prometheus started, listening on {config.METRICS_PORT}")
