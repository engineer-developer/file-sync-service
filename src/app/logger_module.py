import sys
from pathlib import Path

from loguru import logger

import config


LOG_FILE: Path = config.get_settings().log_file_path.absolute()
LOG_FILE_SIZE: int = 5 * 1024 * 1024
LOG_FORMAT: str = (
    "{extra[logger_name]} - {time:YYYY-MM-DD HH:mm:ss,SSS} - {level} - {module} - {message}"
)

logger.remove()
logger.add(
    sink=LOG_FILE,
    level="INFO",
    format=LOG_FORMAT,
    mode="a",
    rotation=LOG_FILE_SIZE,
)
logger.add(
    sink=sys.stderr,
    level="DEBUG",
    format=LOG_FORMAT,
)

logger_app = logger.bind(logger_name="logger_app")
