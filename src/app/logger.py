import sys
from pathlib import Path

from loguru import logger


BASE_DIR = Path(__file__).parent.absolute()
LOGGING_LEVEL = "DEBUG"
LOG_FILE = BASE_DIR / "logs" / "app.log"
LOG_FILE_SIZE = 1024 * 5
LOG_FORMAT = (
    "{extra[logger_name]} - {time:YYYY-MM-DD HH:mm:ss,SSS} - {level} - {message}"
)

logger.remove()
logger.add(
    sink=LOG_FILE,
    level=LOGGING_LEVEL,
    format=LOG_FORMAT,
    mode="a",
    rotation=LOG_FILE_SIZE,
)
logger.add(
    sink=sys.stderr,
    level=LOGGING_LEVEL,
    format=LOG_FORMAT,
)

logger_app = logger.bind(logger_name="app_logger")
