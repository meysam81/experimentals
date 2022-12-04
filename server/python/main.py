from app.logger import get_logger

logger = get_logger(__name__)


if __name__ == "__main__":
    try:
        from app.metrics import PromServerInterceptor
        from app.metrics import serve as metrics
        from app.server import serve

        metrics()
        serve(
            {
                PromServerInterceptor(),
            }
        )
    except KeyboardInterrupt:
        print("Shutting down server ...")
        exit(0)
