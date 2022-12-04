from app.config import config
from app.logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("Starting client ...")

    from app.client import run
    from app.metrics import serve as prometheus, PromClientInterceptor

    prometheus()
    run(infinite=config.INFINITE, interceptors={PromClientInterceptor(),})
