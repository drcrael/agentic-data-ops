"""Structured logs with an allowlist; never serialize exception bodies or dataset values."""

from __future__ import annotations

import json
import logging


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {"level": record.levelname, "event": record.getMessage(), "logger": record.name}
        for key in ("component", "dataset_id", "attempt", "error_type"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger = logging.getLogger("data_maturity")
    logger.handlers = [handler]
    logger.setLevel(level)
    logger.propagate = False
