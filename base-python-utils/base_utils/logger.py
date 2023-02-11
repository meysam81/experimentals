def get_logger(name=__name__, level="INFO"):
    import logging

    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    line = "*" * 80
    formatter = logging.Formatter(
        line
        + "\n[%(levelname)s] %(asctime)s (%(pathname)s:%(lineno)d): \n%(message)s\n"
        + line,
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
