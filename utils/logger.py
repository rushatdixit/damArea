"""
Structured logging factory for the damArea pipeline.

Provides a centralized logger configuration with support for both
console output (human-readable) and file output (JSON-structured).
"""

import logging
import json
import sys
from datetime import datetime, timezone
from typing import Optional


class JsonFormatter(logging.Formatter):
    """
    Formats log records as single-line JSON objects for machine parsing.

    :param dam_name: Optional dam name to include in every log line.
    :type dam_name: Optional[str]
    """

    def __init__(self, dam_name: Optional[str] = None) -> None:
        super().__init__()
        self.dam_name: Optional[str] = dam_name

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a log record as a JSON string.

        :param record: The log record to format.
        :type record: logging.LogRecord
        :return: JSON-encoded log line.
        :rtype: str
        """
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "msg": record.getMessage(),
        }
        if self.dam_name:
            entry["dam"] = self.dam_name
        if record.exc_info and record.exc_info[1]:
            entry["exception"] = str(record.exc_info[1])
        return json.dumps(entry)


class ConsoleFormatter(logging.Formatter):
    """
    Human-readable console formatter with level-based prefixes.
    """

    LEVEL_PREFIXES = {
        logging.DEBUG: "[DEBUG]",
        logging.INFO: "",
        logging.WARNING: "[WARNING]",
        logging.ERROR: "[ERROR]",
        logging.CRITICAL: "[CRITICAL]",
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a log record for console display.

        :param record: The log record to format.
        :type record: logging.LogRecord
        :return: Formatted log string.
        :rtype: str
        """
        prefix = self.LEVEL_PREFIXES.get(record.levelno, "")
        msg = record.getMessage()
        if prefix:
            return f"{prefix} {msg}"
        return msg


def get_logger(module_name: str) -> logging.Logger:
    """
    Returns a logger for the given module under the 'damArea' namespace.

    :param module_name: Name of the calling module (typically ``__name__``).
    :type module_name: str
    :return: Configured logger instance.
    :rtype: logging.Logger
    """
    return logging.getLogger(f"damArea.{module_name}")


def configure_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    dam_name: Optional[str] = None,
) -> None:
    """
    Configures the root 'damArea' logger with console and optional file handlers.

    :param level: Log level string (DEBUG, INFO, WARNING, ERROR).
    :type level: str
    :param log_file: Optional path to a JSON log file.
    :type log_file: Optional[str]
    :param dam_name: Optional dam name to embed in JSON log entries.
    :type dam_name: Optional[str]
    """
    root_logger = logging.getLogger("damArea")
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ConsoleFormatter())
    root_logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file, mode="a")
        file_handler.setFormatter(JsonFormatter(dam_name=dam_name))
        root_logger.addHandler(file_handler)
