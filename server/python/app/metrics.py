from app.config import config
from prometheus_client import start_http_server


def serve():
    server_addr = f"{config.SERVER_HOST}:{config.PORT}"

    start_http_server(config.METRICS_PORT)
