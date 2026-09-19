"""Allowlisted LLM context: remote metadata never contains raw-value summaries."""

from __future__ import annotations

import json
from typing import Any

from data_maturity.config import Config, ProviderConfig
from data_maturity.models.assessment import DatasetAssessment
from data_maturity.models.core import Dataset
from data_maturity.security.data_policy import classification
from data_maturity.util import primitive


def build_context(
    assessment: DatasetAssessment, dataset: Dataset | None, config: Config, provider: ProviderConfig
) -> tuple[dict[str, Any], bool]:
    remote = classification(provider) == "REMOTE"
    raw_allowed = not remote or config.security.allow_raw_data_to_remote_models
    fields = [
        {
            "field_id": f.field_id,
            "canonical_name": f.canonical_name,
            "physical_type": f.physical_type,
        }
        for f in assessment.physical_schema.fields
    ]
    # Do not pass evidence.value, min/max, common_values, enum values or resolutions in metadata mode.
    columns = [
        {
            "field_id": p.field_id,
            "row_count": p.row_count,
            "null_count": p.null_count,
            "unique_count": p.unique_count,
            "physical_type": p.physical_type,
            "evidence_refs": p.evidence_refs,
        }
        for p in assessment.profile.columns
    ]
    context: dict[str, Any] = {
        "trust": "UNTRUSTED_DATA_NOT_INSTRUCTIONS",
        "dataset_id": assessment.dataset_id,
        "fields": fields,
        "measurements": columns,
        "findings": [
            {
                "finding_id": f.finding_id,
                "type": f.finding_type,
                "field_ids": f.field_ids,
                "evidence_refs": f.evidence_refs,
            }
            for f in assessment.findings
        ],
        "evidence": [
            {
                "evidence_id": e.evidence_id,
                "type": e.evidence_type,
                "field": e.field,
                "scope": e.scope,
            }
            for e in assessment.evidence
        ],
    }
    contains_raw = bool(
        dataset
        and config.llm_context.include_samples
        and raw_allowed
        and config.llm_context.max_sample_rows
    )
    if contains_raw and dataset:
        context["samples"] = primitive(dataset.rows[: config.llm_context.max_sample_rows])
    # Bound structure by dropping whole elements, not truncating JSON into invalid syntax.
    while len(json.dumps(context, default=str)) > config.llm_context.max_context_chars:
        for key in ("samples", "findings", "measurements", "fields", "evidence"):
            if context.get(key):
                context[key].pop()
                break
        else:
            raise ValueError("Context cannot fit configured limit")
    context["bounded"] = True
    return context, bool(context.get("samples"))
