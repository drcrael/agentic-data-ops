"""Deterministic identity, JSON conversion, and name normalization."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel


def now() -> datetime:
    return datetime.now(UTC)


def primitive(value: Any) -> Any:
    def encode(item: Any) -> Any:
        # json's default hook is also called for models nested in containers.
        # Their repr is not stable across JSON reloads (notably tzinfo objects).
        return item.model_dump(mode="json") if isinstance(item, BaseModel) else str(item)

    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    return json.loads(json.dumps(value, default=encode, allow_nan=False))


def digest(value: Any) -> str:
    data = json.dumps(primitive(value), sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(data.encode()).hexdigest()


def file_hash(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def stable_id(kind: str, *parts: Any) -> str:
    return f"{kind}:{digest(parts)[:24]}"


def normalize(value: Any) -> str:
    name = re.sub(r"[^\w]+", "_", str(value or "").strip().lower(), flags=re.UNICODE).strip("_")
    return name or "unnamed"


def unique_names(values: list[Any]) -> tuple[list[str], list[str]]:
    used: set[str] = set()
    names, collisions = [], []
    for value in values:
        base = normalize(value)
        name, suffix = base, 2
        while name in used:
            name = f"{base}_{suffix}"
            suffix += 1
        if name != base:
            collisions.append(base)
        names.append(name)
        used.add(name)
    return names, collisions
