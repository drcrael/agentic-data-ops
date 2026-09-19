"""Explicit deterministic rules, measured findings, and explainable severities."""

from __future__ import annotations

import re
import time
from datetime import datetime
from typing import Any

import regex

from data_maturity.config import Config
from data_maturity.evidence.store import EvidenceStore
from data_maturity.models.assessment import QualityAssessment, QualityMetric, QualityRule
from data_maturity.models.core import Dataset, DatasetProfile, Finding, Severity
from data_maturity.profiling.statistics import (
    missing,
    numeric,
    parse_date,
    physical_type,
    value_key,
)
from data_maturity.util import now, stable_id


def finding(
    dataset_id: str,
    kind: str,
    dimension: str,
    refs: list[str],
    fields: list[str] | None = None,
    count: int | None = None,
    total: int = 0,
    severity: Severity = "medium",
    description: str = "",
    inferred: bool = False,
) -> Finding:
    pct = count / total * 100 if count is not None and total else None
    return Finding(
        finding_id=stable_id("finding", dataset_id, fields or [], kind),
        dataset_id=dataset_id,
        field_ids=fields or [],
        finding_type=kind,
        dimension=dimension,
        title=kind.replace("_", " "),
        description=description
        or f"{kind.replace('_', ' ')} in measured scope; review source evidence.",
        severity=severity,
        severity_basis=f"Rule category {dimension}; affected={count}; percentage={pct}; candidate semantics={inferred}",
        state="INFERRED" if inferred else "OBSERVED",
        confidence=0.7 if inferred else None,
        reasoning="Deterministic evidence establishes the measurement; semantic or statistical interpretation requires confirmation"
        if inferred
        else "Deterministic measurement or explicit expectation",
        alternatives=["Observed variation may be legitimate for the intended use"]
        if inferred
        else [],
        evidence_refs=refs,
        affected_count=count,
        affected_percentage=pct,
    )


def evaluate_rule(
    rule: QualityRule, values: list[Any], lexical: bool = False
) -> tuple[int | None, str]:
    valid = [v for v in values if not missing(v)]
    p = rule.parameters
    if rule.operator == "not_null":
        return len(values) - len(valid), "Null values violate explicit required-field rule"
    if rule.operator == "unique":
        return len(valid) - len(
            {value_key(v) for v in valid}
        ), "Duplicates beyond first occurrence; nulls measured separately"
    if rule.operator == "range":
        if not any(k in p for k in ("min", "max")):
            raise ValueError(f"Range rule {rule.rule_id} needs min or max")
        return sum(
            numeric(v) is None
            or numeric(v) < p.get("min", float("-inf"))
            or numeric(v) > p.get("max", float("inf"))
            for v in valid
        ), "Outside explicitly supplied range or not numeric"
    if rule.operator == "enum":
        if "values" not in p:
            raise ValueError(f"Enum rule {rule.rule_id} needs values")
        allowed = {value_key(v) for v in p["values"]}
        return sum(
            value_key(v) not in allowed for v in valid
        ), "Value outside explicitly supplied vocabulary"
    if rule.operator == "pattern":
        pattern = p.get("pattern", "")
        # Only trusted configuration supplies patterns; bound complexity and input length.
        if not pattern or len(pattern) > 256 or re.search(r"[+*}]\)[+*{]", pattern):
            raise ValueError("Pattern missing or contains prohibited nested repetition")
        try:
            compiled = regex.compile(pattern)
        except regex.error as exc:
            raise ValueError("Invalid configured regular expression") from exc
        deadline = time.monotonic() + 2.0
        violations = 0
        try:
            for value in valid:
                if time.monotonic() > deadline:
                    return (
                        None,
                        "Pattern evaluation exceeded total time budget; result is undetermined",
                    )
                violations += compiled.fullmatch(str(value), timeout=0.02) is None
        except TimeoutError:
            return None, "Pattern evaluation timed out on a value; result is undetermined"
        return violations, "Does not match configured pattern; time-bounded evaluation"
    if rule.operator == "type":
        if "type" not in p:
            raise ValueError(f"Type rule {rule.rule_id} needs type")
        return sum(
            physical_type(v, lexical) != p["type"] for v in valid
        ), "Physical type differs from configured expectation"
    if rule.operator == "freshness":
        if "max_age_days" not in p:
            raise ValueError("Freshness rule requires max_age_days")
        parsed = [parse_date(v)[0] for v in valid]
        if not parsed or any(not isinstance(v, datetime) or v.tzinfo is None for v in parsed):
            return (
                None,
                "Freshness requires timezone-aware timestamps and an explicit time interpretation",
            )
        reference = now()
        return sum(
            (reference - v).total_seconds() / 86400 > p["max_age_days"]
            for v in parsed
            if isinstance(v, datetime)
        ), "Age measured against assessment time; timestamps require explicit timezone"
    raise ValueError("Unsupported rule operator")


def assess_quality(
    dataset: Dataset, profile: DatasetProfile, config: Config, store: EvidenceStore
) -> tuple[QualityAssessment, list[Finding]]:
    quality = QualityAssessment()
    findings: list[Finding] = []

    def emit(
        kind: str,
        dimension: str,
        count: int,
        refs: list[str],
        field_id: str | None = None,
        inferred: bool = False,
        low: bool = False,
    ) -> None:
        metric_id = stable_id("metric", dataset.dataset_id, field_id, kind)
        quality.metrics.append(
            QualityMetric(
                metric_id=metric_id,
                dimension=dimension,
                name=kind,
                value=count,
                denominator=profile.row_count,
                field_id=field_id,
                status="WARNING" if count and inferred else "FAIL" if count else "PASS",
                evidence_refs=refs,
                scope=profile.scope,
                explanation="Calculated over measured scope; interpretation remains a candidate"
                if inferred
                else "Calculated over measured scope",
            )
        )
        if count:
            pct = 100 * count / profile.row_count if profile.row_count else 0
            severity: Severity = (
                "low"
                if low
                else "high"
                if pct >= config.severity_thresholds.get("high", 10)
                else "medium"
            )
            findings.append(
                finding(
                    dataset.dataset_id,
                    kind,
                    dimension,
                    refs,
                    [field_id] if field_id else [],
                    count,
                    profile.row_count,
                    severity,
                    inferred=inferred,
                )
            )

    emit("duplicate_records", "uniqueness", profile.duplicate_record_count, profile.evidence_refs)
    for field, col in zip(dataset.fields, profile.columns, strict=True):
        fid, refs = field.field_id, col.evidence_refs
        identifier = field.canonical_name == "id" or field.canonical_name.endswith("_id")
        emit(
            "missing_identifier" if identifier else "missing_values",
            "completeness",
            col.null_count,
            refs,
            fid,
            inferred=True,
        )
        if identifier:
            emit(
                "duplicate_candidate_identifier",
                "uniqueness",
                col.duplicate_count,
                refs,
                fid,
                inferred=True,
            )
        emit("whitespace_inconsistency", "conformity", col.whitespace_count, refs, fid)
        emit("casing_inconsistency", "consistency", col.casing_variation_count, refs, fid)
        emit(
            "invalid_or_ambiguous_dates",
            "validity",
            col.invalid_date_count,
            refs,
            fid,
            inferred=True,
        )
        emit(
            "mixed_physical_types",
            "consistency",
            round(col.mixed_type_rate * (col.row_count - col.null_count)),
            refs,
            fid,
        )
        emit("nonfinite_values", "validity", col.nonfinite_count, refs, fid)
        if len(col.date_format_counts) > 1:
            emit(
                "multiple_date_formats",
                "conformity",
                sum(col.date_format_counts.values()) - max(col.date_format_counts.values()),
                refs,
                fid,
            )
        for name, count in col.anomaly_counts.items():
            emit(
                f"potential_anomaly_{name}",
                "accuracy_proxies",
                count,
                refs,
                fid,
                inferred=True,
                low=True,
            )
    structure_ev = store.add(
        dataset, "structure_inspection", dataset.structure.model_dump(), scope="metadata"
    )
    if dataset.structure.collisions:
        findings.append(
            finding(
                dataset.dataset_id,
                "canonical_name_collision",
                "schema_definition",
                [structure_ev.evidence_id],
                description="Source names normalize identically; deterministic suffixes preserve separate fields",
            )
        )
    if dataset.structure.confidence < 0.8:
        findings.append(
            finding(
                dataset.dataset_id,
                "uncertain_table_boundary",
                "structure",
                [structure_ev.evidence_id],
                inferred=True,
            )
        )
    if dataset.structure.formula_count:
        findings.append(
            finding(
                dataset.dataset_id,
                "formula_results_unavailable",
                "validity",
                [structure_ev.evidence_id],
                description="Formulas are not evaluated. Missing formula results are included in null counts; do not interpret these as confirmed source blanks.",
            )
        )
    for rule in config.quality_rules:
        if rule.dataset and rule.dataset not in {
            dataset.structure.table,
            dataset.structure.worksheet,
            dataset.dataset_id,
        }:
            continue
        matching = [
            (i, f)
            for i, f in enumerate(dataset.fields)
            if rule.field in {f.field_id, f.canonical_name, f.source_name}
        ]
        quality.rules.append(rule)
        if not matching:
            quality.metrics.append(
                QualityMetric(
                    metric_id=stable_id("metric", dataset.dataset_id, rule.rule_id),
                    dimension=rule.dimension,
                    name=rule.rule_id,
                    value=None,
                    status="UNDETERMINED",
                    evidence_refs=[structure_ev.evidence_id],
                    rule_id=rule.rule_id,
                    scope="metadata",
                    explanation="Configured field is absent",
                )
            )
            findings.append(
                finding(
                    dataset.dataset_id,
                    f"missing_rule_field_{rule.rule_id}",
                    rule.dimension,
                    [structure_ev.evidence_id],
                    severity=rule.severity,
                )
            )
            continue
        index, field = matching[0]
        violation_count, explanation = evaluate_rule(
            rule, [r[index] for r in dataset.rows], dataset.source.format in {"csv", "tsv"}
        )
        ev = store.add(
            dataset,
            "quality_rule_result",
            {"rule": rule.model_dump(), "violations": violation_count, "rows": profile.row_count},
            field.field_id,
        )
        quality.metrics.append(
            QualityMetric(
                metric_id=stable_id("metric", dataset.dataset_id, rule.rule_id),
                dimension=rule.dimension,
                name=rule.rule_id,
                value=violation_count,
                denominator=profile.row_count,
                field_id=field.field_id,
                status="UNDETERMINED"
                if violation_count is None
                else "WARNING"
                if violation_count and rule.origin == "INFERRED"
                else "FAIL"
                if violation_count
                else "PASS",
                evidence_refs=[ev.evidence_id],
                rule_id=rule.rule_id,
                scope=profile.scope,
                explanation=explanation,
            )
        )
        if violation_count:
            findings.append(
                finding(
                    dataset.dataset_id,
                    f"rule_violation_{rule.rule_id}",
                    rule.dimension,
                    [ev.evidence_id],
                    [field.field_id],
                    violation_count,
                    profile.row_count,
                    rule.severity,
                    explanation,
                    inferred=rule.origin == "INFERRED",
                )
            )
    measured = {m.dimension for m in quality.metrics}
    for dimension in [
        "completeness",
        "validity",
        "uniqueness",
        "consistency",
        "conformity",
        "integrity",
        "accuracy_proxies",
        "timeliness",
        "semantic_clarity",
        "provenance",
        "governance",
    ]:
        if dimension not in measured:
            quality.metrics.append(
                QualityMetric(
                    metric_id=stable_id("metric", dataset.dataset_id, dimension),
                    dimension=dimension,
                    name=f"{dimension}_unresolved",
                    value=None,
                    status="UNDETERMINED",
                    evidence_refs=[structure_ev.evidence_id],
                    scope="metadata",
                    explanation="No authoritative expectation or sufficient evidence supplied; not a zero score",
                )
            )
    return quality, findings
