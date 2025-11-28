import logging
from enum import StrEnum

LOG_FORMAT_DEBUG = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"


class LoggingLevels(StrEnum):
    info = "INFO"
    warn = "WARN"
    error = "ERROR"
    debug = "DEBUG"


def configure_logging(logging_level: str = LoggingLevels.error) -> None:
    # Sanitize string
    logging_level = str(logging_level).upper()

    available_levels = [level.value for level in LoggingLevels]
    if logging_level not in available_levels:
        logging.basicConfig(level=LoggingLevels.error)
        return

    if logging_level == LoggingLevels.debug:
        logging.basicConfig(level=LoggingLevels.debug, format=LOG_FORMAT_DEBUG)
        return

    logging.basicConfig(level=logging_level)
    return
