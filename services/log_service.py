import logging
from logging.handlers import RotatingFileHandler

from config import LOG_FILE

_logging_configured = False


def setup_logging() -> None:
    global _logging_configured

    if _logging_configured:
        return

    try:
        handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
    except OSError:
        return

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    _logging_configured = True
