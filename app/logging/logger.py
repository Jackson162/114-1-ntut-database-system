import logging
from app.core.config import settings


def get_logger() -> logging.Logger:
    """Get seasalt logger and support additional custom handers in different classes."""
    logger = logging.getLogger(name="logger-0")
    logger.propagate = False
    logger.setLevel(settings.LOG_LEVEL)

    return logger
