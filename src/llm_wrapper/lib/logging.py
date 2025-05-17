import logging
import os
import json
from pathlib import Path
from typing import Optional

def setup_logger(
    name: str = "app",
    log_file: str = "logs/app.log",
    level: int = logging.DEBUG,
    console: bool = False
) -> logging.Logger:
    """
    Sets up and returns a logger that writes to a specified file (and optionally console).

    Parameters:
    - name (str): Name of the logger.
    - log_file (str): File path where logs will be written.
    - level (int): Logging level, e.g., logging.DEBUG.
    - console (bool): If True, also log to stdout.

    Returns:
    - logging.Logger: Configured logger instance.
    """
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    # Prevent duplicate handlers when setup_logger is called multiple times
    if logger.handlers:
        # Reset level override only, do not add handlers again
        env_level = os.getenv("LOG_LEVEL")
        if env_level:
            try:
                level = int(env_level)
            except ValueError:
                lvl_name = env_level.strip().upper()
                if lvl_name in logging._nameToLevel:
                    level = logging._nameToLevel[lvl_name]
        logger.setLevel(level)
        return logger
    # Apply log level override from environment if provided
    env_level = os.getenv("LOG_LEVEL")
    if env_level:
        try:
            level = int(env_level)
        except ValueError:
            lvl_name = env_level.strip().upper()
            if lvl_name in logging._nameToLevel:
                level = logging._nameToLevel[lvl_name]
    logger.setLevel(level)
    logger.propagate = False  # Prevent duplicate logs if root logger is used elsewhere

    # Define structured formatters (JSON or key-value)
    fmt_type = os.getenv("LOG_FORMAT", "json").strip().lower()
    class JSONFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            log_record = {
                "timestamp": self.formatTime(record, self.datefmt),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
            return json.dumps(log_record)
    class KVFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            ts = self.formatTime(record, self.datefmt)
            msg = record.getMessage()
            return f'timestamp="{ts}" level={record.levelname} logger={record.name} message="{msg}"'
    if fmt_type in ("kv", "keyvalue"):
        formatter = KVFormatter()
    else:
        formatter = JSONFormatter()

    # File handler
    file_handler = logging.FileHandler(log_file, mode="a")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Optional console handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger