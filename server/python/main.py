from app.logger import get_logger

logger = get_logger(__name__)


if __name__ == "__main__":
    try:
        logger.info("Starting server ...")
        from app.server import serve

        serve()
    except KeyboardInterrupt:
        print("Shutting down server ...")
        exit(0)
