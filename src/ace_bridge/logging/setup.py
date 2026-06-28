"""Logging setup — console, file, JSON, and rotating log handlers."""

from __future__ import annotations

import json
import logging
import logging.handlers
from pathlib import Path
from typing import Optional


class JSONFormatter(logging.Formatter):
    """Format log records as single-line JSON for structured log ingestion."""

    def format(self, record: logging.LogRecord) -> str:
        data = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            data["exc"] = self.formatException(record.exc_info)
        return json.dumps(data, separators=(",", ":"))


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    json_output: bool = False,
) -> None:
    """Configure root logger with console and optional file handler.

    Args:
        level: Log level name (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to rotating log file
        json_output: If True, format logs as JSON
    """
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Console handler
    console = logging.StreamHandler()
    if json_output:
        console.setFormatter(JSONFormatter())
    else:
        console.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)-8s %(name)-30s %(message)s",
                datefmt="%H:%M:%S",
            )
        )
    root.addHandler(console)

    # File handler (rotating, 10MB max, 5 backups)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(JSONFormatter())
        root.addHandler(file_handler)
        logging.getLogger(__name__).info("File logging to: %s", log_file)
