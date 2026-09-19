"""Column measurements, bounded distribution summaries and anomaly candidates."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Any

import polars as pl

from data_maturity.config import Config
from data_maturity.evidence.store import EvidenceStore
from data_maturity.models.core import ColumnProfile, Dataset, DatasetProfile, PhysicalType
from data_maturity.profiling.statistics import (
    missing,
    numeric,
    parse_date,
    physical_type,
    value_key,
)
from data_maturity.util import primitive


def _scalar(value: Any) -> float:
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("Invalid numerical summary; check finite input range")
    return float(value)


def column_profile(
    values: list[Any], field_id: str, name: str, config: Config, lexical: bool
) -> ColumnProfile:
    n = len(values)
    valid = [v for v in values if not missing(v)]
    counts = Counter(value_key(v) for v in valid)
    types = Counter(physical_type(v, lexical) for v in valid)
    dominant: PhysicalType = max(types, key=lambda key: types[key]) if types else "unknown"
    logical_types = set(types) - {"unknown"}
    if logical_types <= {"integer", "float"} and logical_types:
        inferred: PhysicalType = "float" if "float" in types else "integer"
        mixed = 0.0
    elif len(logical_types) > 1:
        inferred = "mixed"
        mixed = 1 - types[dominant] / len(valid)
    else:
        inferred, mixed = dominant, 0.0
    strings = [v for v in valid if isinstance(v, str)]
    normalized: dict[str, set[str]] = defaultdict(set)
    for value in strings:
        normalized[value.strip().casefold()].add(value.strip())
    casing = sum(1 for v in strings if len(normalized[v.strip().casefold()]) > 1)
    parsed_dates = [parse_date(v) for v in valid]
    formats = Counter(fmt for _, fmt in parsed_dates if fmt)
    date_expected = (
        any(token in name for token in ("date", "epoch", "timestamp", "created_at", "updated_at"))
        or sum(formats.values()) > len(valid) / 2
    )
    stats: dict[str, Any] = {}
    raw_numbers = [numeric(v) for v in valid if physical_type(v, lexical) in {"integer", "float"}]
    numbers = [v for v in raw_numbers if v is not None]
    anomalies: dict[str, int] = {}
    if numbers:
        series = pl.Series("value", numbers, dtype=pl.Float64)
        q1, q2, q3 = (
            _scalar(series.quantile(q, interpolation="linear")) for q in (0.25, 0.5, 0.75)
        )
        iqr = q3 - q1
        mad = _scalar((series - q2).abs().median())
        anomalies["iqr"] = (
            sum(v < q1 - 1.5 * iqr or v > q3 + 1.5 * iqr for v in numbers)
            if len(numbers) >= 4
            else 0
        )
        anomalies["mad"] = sum(abs(v - q2) * 0.67448975 / mad > 3.5 for v in numbers) if mad else 0
        stats.update(
            minimum=min(numbers),
            maximum=max(numbers),
            mean=_scalar(series.mean()),
            median=q2,
            standard_deviation=_scalar(series.std(ddof=0)),
            quantiles={"q25": q1, "q50": q2, "q75": q3},
        )
    dates = [value.isoformat() for value, _ in parsed_dates if value is not None]
    if dates and not numbers:
        stats.update(minimum=min(dates), maximum=max(dates))
    if strings:
        lengths = [len(v) for v in strings]
        stats.update(min_length=min(lengths), max_length=max(lengths))
        series = pl.Series(lengths)
        q1, q3 = (_scalar(series.quantile(q, interpolation="linear")) for q in (0.25, 0.75))
        anomalies["length_iqr"] = (
            sum(x < q1 - 1.5 * (q3 - q1) or x > q3 + 1.5 * (q3 - q1) for x in lengths)
            if len(lengths) >= 4
            else 0
        )
    anomalies["rare_categories"] = (
        sum(c for c in counts.values() if c / len(valid) < 0.01)
        if 1 < len(counts) <= 30 and len(valid) >= 100
        else 0
    )
    representatives = {value_key(v): primitive(v) for v in valid}
    common = (
        [
            {"value": representatives[k], "count": c}
            for k, c in counts.most_common(config.profiling.top_values)
        ]
        if config.profiling.include_value_summaries
        else []
    )
    likely_enum = (
        [representatives[k] for k in counts]
        if config.profiling.include_value_summaries
        and 0 < len(counts) <= 20
        and len(counts) < len(valid) / 2
        else []
    )
    return ColumnProfile(
        field_id=field_id,
        row_count=n,
        null_count=n - len(valid),
        null_percentage=100 * (n - len(valid)) / n if n else 0,
        unique_count=len(counts),
        uniqueness_ratio=len(counts) / len(valid) if valid else 0,
        duplicate_count=len(valid) - len(counts),
        duplicate_frequency=(len(valid) - len(counts)) / len(valid) if valid else 0,
        physical_type=inferred,
        type_counts={str(k): v for k, v in types.items()},
        mixed_type_rate=mixed,
        invalid_date_count=sum(value is None for value, _ in parsed_dates) if date_expected else 0,
        date_format_counts=dict(formats),
        whitespace_count=sum(v != v.strip() for v in strings),
        casing_variation_count=casing,
        numeric_string_count=sum(numeric(v) is not None for v in strings),
        nonfinite_count=sum(isinstance(v, float) and not math.isfinite(v) for v in valid),
        common_values=common,
        likely_enum=likely_enum,
        anomaly_counts=anomalies,
        **stats,
    )


class DatasetProfiler:
    def profile(self, dataset: Dataset, config: Config, store: EvidenceStore) -> DatasetProfile:
        columns = []
        for index, field in enumerate(dataset.fields):
            profile = column_profile(
                [r[index] for r in dataset.rows],
                field.field_id,
                field.canonical_name,
                config,
                dataset.source.format in {"csv", "tsv"},
            )
            field.physical_type = profile.physical_type
            evidence = store.add(
                dataset,
                "column_profile",
                profile.model_dump(exclude={"evidence_refs"}),
                field.field_id,
            )
            profile.evidence_refs = [evidence.evidence_id]
            field.provenance = [evidence.evidence_id]
            columns.append(profile)
        duplicates = len(dataset.rows) - len(
            {tuple(value_key(v) for v in row) for row in dataset.rows}
        )
        summary = store.add(
            dataset, "record_profile", {"rows": len(dataset.rows), "duplicate_records": duplicates}
        )
        return DatasetProfile(
            row_count=len(dataset.rows),
            source_row_count=dataset.structure.source_row_count,
            sampled=dataset.structure.sampled,
            scope="sample" if dataset.structure.sampled else "full",
            duplicate_record_count=duplicates,
            columns=columns,
            evidence_refs=[summary.evidence_id],
        )
