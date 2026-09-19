"""Extensible adapters and bounded deterministic reservoir sampling."""

from __future__ import annotations

import random
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Protocol

from data_maturity.config import Config
from data_maturity.models.core import Dataset, DatasetStructure, FieldDefinition, SourceMetadata
from data_maturity.util import file_hash, stable_id, unique_names


class IngestionError(ValueError):
    """Fatal source validation/ingestion failure with no partially trusted result."""


class IngestionAdapter(Protocol):
    def read(self, path: Path, config: Config) -> tuple[SourceMetadata, list[Dataset]]: ...


def source_metadata(path: Path, config: Config) -> SourceMetadata:
    if not path.is_file():
        raise IngestionError("Input is not a regular file")
    size = path.stat().st_size
    if size > config.profiling.max_file_bytes:
        raise IngestionError("Input exceeds max_file_bytes")
    return SourceMetadata(
        name=path.name, sha256=file_hash(path), format=path.suffix.lower()[1:], size_bytes=size
    )


def collect(
    rows: Iterable[tuple[int, list[Any]]], config: Config
) -> tuple[list[list[Any]], list[int], int, int]:
    rng = random.Random(config.runtime.random_seed)
    sample: list[tuple[int, list[Any]]] = []
    total = scanned = 0
    for row_number, row in rows:
        total += 1
        if total > config.profiling.max_rows:
            continue
        scanned += 1
        if any(isinstance(v, str) and len(v) > config.profiling.max_field_chars for v in row):
            raise IngestionError("Cell exceeds max_field_chars")
        if len(sample) < config.profiling.sample_rows:
            sample.append((row_number, row))
        else:
            index = rng.randrange(scanned)
            if index < len(sample):
                sample[index] = (row_number, row)
    sample.sort(key=lambda pair: pair[0])
    return [r for _, r in sample], [n for n, _ in sample], total, scanned


def make_dataset(
    source: SourceMetadata,
    structure: DatasetStructure,
    headers: list[Any],
    rows: list[list[Any]],
    row_numbers: list[int],
) -> Dataset:
    dataset_id = stable_id("dataset", source.name, structure.worksheet, structure.table)
    names, collisions = unique_names(headers)
    structure.collisions = collisions
    fields = [
        FieldDefinition(
            field_id=stable_id("field", dataset_id, name),
            source_name=str(raw or ""),
            canonical_name=name,
        )
        for raw, name in zip(headers, names, strict=True)
    ]
    return Dataset(
        dataset_id=dataset_id,
        source=source,
        structure=structure,
        fields=fields,
        rows=rows,
        source_rows=row_numbers,
    )


def ingest(path: Path, config: Config) -> tuple[SourceMetadata, list[Dataset]]:
    from data_maturity.ingestion.csv import DelimitedAdapter
    from data_maturity.ingestion.excel import ExcelAdapter

    adapters: dict[str, IngestionAdapter] = {
        ".csv": DelimitedAdapter(),
        ".tsv": DelimitedAdapter(),
        ".xlsx": ExcelAdapter(),
        ".xlsm": ExcelAdapter(),
    }
    adapter = adapters.get(path.suffix.lower())
    if adapter is None:
        raise IngestionError("Supported formats: XLSX, XLSM, CSV and TSV")
    return adapter.read(path, config)
