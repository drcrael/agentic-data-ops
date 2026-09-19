"""Deterministic physical type and date parsing, without guessed time zones."""

from __future__ import annotations

import math
import re
from datetime import date, datetime
from typing import Any

from data_maturity.models.core import PhysicalType


def missing(value: Any) -> bool:
    return value is None or isinstance(value, str) and not value.strip()


def parse_date(value: Any) -> tuple[date | datetime | None, str | None]:
    if isinstance(value, datetime):
        return value, "native_datetime"
    if isinstance(value, date):
        return value, "native_date"
    if not isinstance(value, str):
        return None, None
    text = value.strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", text):
        try:
            return date.fromisoformat(text), "ISO_DATE"
        except ValueError:
            return None, None
    if re.match(r"^\d{4}-\d{2}-\d{2}[T ]", text):
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00")), "ISO_DATETIME"
        except ValueError:
            return None, None
    # Ambiguous slash dates are counted as a distinct format, never assigned a timezone.
    for pattern, fmt in [(r"^\d{4}/\d{2}/\d{2}$", "%Y/%m/%d")]:
        if re.match(pattern, text):
            try:
                return datetime.strptime(text, fmt).date(), fmt
            except ValueError:
                return None, None
    return None, None


def numeric(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        parsed = float(value)
        return parsed if math.isfinite(parsed) else None
    except (TypeError, ValueError, OverflowError):
        return None


def physical_type(value: Any, lexical: bool = False) -> PhysicalType:
    if missing(value):
        return "unknown"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "float" if math.isfinite(value) else "unknown"
    parsed, _ = parse_date(value)
    if parsed is not None:
        return "datetime" if isinstance(parsed, datetime) else "date"
    if isinstance(value, str) and lexical:
        if value.lower() in {"true", "false"}:
            return "boolean"
        if re.fullmatch(r"-?(0|[1-9]\d*)", value):
            return "integer"
        if numeric(value) is not None and not re.fullmatch(r"0\d+", value):
            return "float"
    return "string"


def value_key(value: Any) -> str:
    """Type-sensitive comparison avoids conflating 1, True, and '1'."""
    return f"{type(value).__name__}:{value!s}"
