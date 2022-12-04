from app.logger import get_logger
from app.config import config

logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("Starting client ...")

    from app.client import run

    run(infinite=config.INFINITE)
