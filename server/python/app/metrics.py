from app.config import config
from prometheus_client import start_http_server
from py_grpc_prometheus.prometheus_server_interceptor import (
    PromServerInterceptor,  # isort: skip
)


def serve():
    server_addr = f"{config.SERVER_HOST}:{config.PORT}"

    start_http_server(config.METRICS_PORT)
