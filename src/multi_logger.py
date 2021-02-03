import logging

LOG_LEVEL = logging.DEBUG
LOG_FORMATTER = logging.Formatter(
    '%(asctime)-15s - %(filename)s - %(levelname)s - %(message)s'
)

def setup_logger(name, log_file, level=LOG_LEVEL):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(LOG_FORMATTER)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger