from app.config import config
from app.logger import get_logger

logger = get_logger(__name__)


if __name__ == "__main__":
    try:
        from app.metrics import PromServerInterceptor
        from app.server import serve

        if config.PROMETHEUS_ENABLED:
            from app.metrics import serve as metrics

            metrics()
        serve({PromServerInterceptor()})
    except KeyboardInterrupt:
        print("Shutting down server ...")
        exit(0)
