"""
Logging Configuration Module

This module provides a centralized configuration for application logging,
including formatters, handlers, and logging levels for different environments.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import json
from typing import Any, Dict

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Include exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Include extra fields if present
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


def setup_logging(level: str = "INFO") -> None:
    """
    Set up application logging with both console and file handlers.

    Args:
        level: The logging level to use (default: "INFO")
    """
    # Create logger
    logger = logging.getLogger("app")
    logger.setLevel(level)

    # Clear any existing handlers
    logger.handlers.clear()

    # Create formatters
    json_formatter = JSONFormatter()
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (JSON)
    file_handler = RotatingFileHandler(
        LOGS_DIR / "app.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)

    # Set propagation to False to avoid duplicate logs
    logger.propagate = False

    logger.info("Logging setup completed", extra={"setup": "success"})


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: The name for the logger instance

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(f"app.{name}")
