"""Streaming UTF-8 CSV/TSV ingestion; malformed rows fail explicitly."""

from __future__ import annotations

import csv
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from data_maturity.config import Config
from data_maturity.ingestion.base import IngestionError, collect, make_dataset, source_metadata
from data_maturity.models.core import Dataset, DatasetStructure, SourceMetadata


class DelimitedAdapter:
    def read(self, path: Path, config: Config) -> tuple[SourceMetadata, list[Dataset]]:
        source = source_metadata(path, config)
        delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
        try:
            with path.open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.reader(stream, delimiter=delimiter, strict=True)
                headers = next(reader, [])
                if not headers or not any(headers):
                    raise IngestionError("Delimited source has no header")
                if len(headers) > config.profiling.max_columns:
                    raise IngestionError("Input exceeds max_columns")

                def records() -> Iterator[tuple[int, list[Any]]]:
                    for row in reader:
                        if not row:
                            continue
                        if len(row) != len(headers):
                            raise IngestionError(f"Ragged record ending at line {reader.line_num}")
                        yield reader.line_num, [v if v != "" else None for v in row]

                rows, numbers, total, scanned = collect(records(), config)
        except (UnicodeError, csv.Error) as exc:
            raise IngestionError(f"Invalid UTF-8 delimited file: {type(exc).__name__}") from exc
        sampled = total > len(rows)
        structure = DatasetStructure(
            table=path.stem,
            cell_range=f"records:1:{total + 1}",
            header_row=1,
            confidence=0.9,
            detection_method="delimited_header",
            alternatives=["First record may be data; supply a header row if so"],
            source_row_count=total,
            rows_scanned=scanned,
            rows_retained=len(rows),
            sampled=sampled,
            truncated=total > scanned,
            sampling_method="reservoir over scanned prefix" if sampled else "full",
            seed=config.runtime.random_seed,
        )
        source.inspection = {
            "delimiter": delimiter,
            "encoding": "utf-8-sig",
            "header_assumption": "first_record",
        }
        return source, [make_dataset(source, structure, headers, rows, numbers)]
