def get_logger(name=__name__, level="INFO"):
    import logging

    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    sharp = "#" * 80
    formatter = logging.Formatter(
        sharp
        + "\n[%(levelname)s] %(asctime)s (%(pathname)s:%(lineno)d): \n%(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
