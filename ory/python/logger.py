import logging

from config import settings


def get_logger(name=None):
    logger = logging.getLogger(name or __name__)
    logger.setLevel(settings.LOG_LEVEL)

    ch = logging.StreamHandler()
    ch.setLevel(settings.LOG_LEVEL)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger
