import logging


def init_logger(name, level_name: str, filename: str = None):
    # Determine the logging level
    level = 0
    if level_name == "DEBUG":
        level = logging.DEBUG
    elif level_name == "INFO":
        level = logging.INFO
    elif level_name == "WARNING":
        level = logging.WARNING
    elif level_name == "ERROR":
        level = logging.ERROR
    elif level_name == "CRITICAL":
        level = logging.CRITICAL
    else:
        raise ValueError(f"Invalid logging level: {level}")

    # Create the logger
    logger = logging.getLogger(name)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter("%(name)s::%(levelname)s %(asctime)s: %(message)s")
    ch.setFormatter(formatter)

    # Log to file
    if filename is not None:
        fh = logging.FileHandler(filename)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    logger.addHandler(ch)
    return logger


logger = logging.getLogger("simple_example")

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
