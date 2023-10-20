import logging, sys

from pathlib import Path
from constants import *

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_FILE = "activity.log"
DEBUG_LOG_FILE = "debug.log"
ERROR_LOG_FILE = "error.log"

SIMPLE_LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
DEBUG_LOG_FORMAT = (
    "%(asctime)s.%(msecs)03d %(levelname)s %(filename)s:%(lineno)d"
    " %(message)s"
)

def configure_logging(log_dir: Path = LOG_DIR) -> None:
    """Configure the native logging module."""

    # create log directory if it doesn't exist
    if not log_dir.exists():
        log_dir.mkdir()
        
    log_level = logging.DEBUG if DEBUG_MODE else logging.INFO
    log_format = DEBUG_LOG_FORMAT if DEBUG_MODE else SIMPLE_LOG_FORMAT
    
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # INFO log file handler
    activity_log_handler = logging.FileHandler(log_dir / LOG_FILE, "a", "utf-8")
    activity_log_handler.setLevel(logging.INFO)
    activity_log_handler.setFormatter(logging.Formatter(SIMPLE_LOG_FORMAT))
    
    if DEBUG_MODE:
        # DEBUG log file handler
        debug_log_handler = logging.FileHandler(log_dir / DEBUG_LOG_FILE, "a", "utf-8")
        debug_log_handler.setLevel(logging.DEBUG)
        debug_log_handler.setFormatter(logging.Formatter(DEBUG_LOG_FORMAT))
    
    # ERROR log file handler
    error_log_handler = logging.FileHandler(log_dir / ERROR_LOG_FILE, "a", "utf-8")
    error_log_handler.setLevel(logging.ERROR)
    error_log_handler.setFormatter(logging.Formatter(DEBUG_LOG_FORMAT))
    
    # Configure the root logger
    logging.basicConfig(
        format=log_format,
        level=log_level,
        handlers=(
            [console_handler, activity_log_handler, error_log_handler]
            + ([debug_log_handler] if DEBUG_MODE else [])
        ),
    )