import logging

from app.config import config


def get_logger(name=None):
    logger = logging.getLogger(name or __name__)
    logger.setLevel(config.LOG_LEVEL)

    ch = logging.StreamHandler()
    ch.setLevel(config.LOG_LEVEL)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger
