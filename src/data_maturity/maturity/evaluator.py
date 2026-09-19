"""Cumulative, explicit maturity criteria. Unknown criteria never pass."""

from __future__ import annotations

from typing import Any

from data_maturity.models.assessment import (
    DatasetAssessment,
    MaturityAssessment,
    MaturityDimensionAssessment,
)

LEVEL_NAMES = ["UNMANAGED", "STRUCTURED", "DEFINED", "GOVERNED", "OPERATIONALIZED", "AI_READY"]


def criterion_facts(assessment: DatasetAssessment) -> dict[str, bool]:
    current = [a for a in assessment.assertions if not a.superseded_by]
    authoritative = {a.assertion_type for a in current if a.state == "OBSERVED"}
    defined = {
        fid
        for a in current
        if a.assertion_type == "definition" and a.state == "OBSERVED"
        for fid in a.field_ids
    }
    governed = {item.property for item in assessment.governance.items if item.status == "PRESENT"}
    active = [
        f
        for f in assessment.findings
        if f.status not in {"RESOLVED", "SUPERSEDED", "ACCEPTED_RISK"}
    ]
    return {
        "stable_tabular_structure": assessment.structure.confidence >= 0.8
        and assessment.profile.row_count > 0,
        "typed_fields": all(
            f.physical_type not in {"mixed", "unknown"} for f in assessment.physical_schema.fields
        ),
        "candidate_keys_identified": bool(assessment.keys),
        "field_definitions_present": len(defined) == len(assessment.physical_schema.fields),
        "authoritative_schema": "authoritative_schema" in authoritative,
        "constraints_defined": bool(assessment.quality.rules),
        "quality_measured": bool(assessment.quality.metrics),
        "quality_controlled": bool(assessment.quality.rules)
        and not any(
            m.status in {"FAIL", "UNDETERMINED"} for m in assessment.quality.metrics if m.rule_id
        ),
        "no_high_quality_findings": not any(
            f.severity in {"high", "critical"}
            and f.dimension not in {"governance", "semantic_clarity"}
            for f in active
        ),
        "metadata_recorded": bool(assessment.source.sha256),
        "semantics_resolved": not any(
            a.state != "OBSERVED"
            for a in current
            if a.assertion_type
            in {
                "definition",
                "coordinate_unit",
                "coordinate_reference_frame",
                "code_definitions",
                "temporal_semantics",
            }
        ),
        "provenance_documented": "provenance" in governed,
        "lineage_documented": "lineage" in governed,
        "owner_known": "owner" in governed,
        "authority_known": "authoritative_source" in governed,
        "governance_defined": {"owner", "steward", "security_classification", "retention"}
        <= governed,
        "machine_accessible": True,
        "machine_readable_contract": assessment.proposed_contract is not None,
        "contract_authoritative": "authoritative_contract" in authoritative,
        "semantic_definitions_machine_readable": len(defined)
        == len(assessment.physical_schema.fields),
        # Operational adoption cannot be established merely by generating this report.
        "schema_validation_automated": "schema_validation_automated" in authoritative,
        "schema_versioned": "version" in governed and "authoritative_schema" in authoritative,
        "monitoring_operational": "monitoring_operational" in authoritative,
        "mission_fit": "mission_fit" in authoritative,
        "ai_readiness_verified": assessment.ai_readiness.status == "READY",
    }


def evaluate(assessment: DatasetAssessment, model: dict[str, Any]) -> MaturityAssessment:
    facts = criterion_facts(assessment)
    dimensions = []
    for name, levels in model["dimensions"].items():
        current = 0
        required: list[str] = []
        for level in range(1, 6):
            requirements = levels.get(f"level_{level}", {}).get("requirements", [])
            if not requirements:
                break
            required.extend(requirements)
            if all(facts.get(r, False) for r in required):
                current = level
            else:
                break
        all_requirements = list(
            dict.fromkeys(r for definition in levels.values() for r in definition["requirements"])
        )
        dimensions.append(
            MaturityDimensionAssessment(
                dimension=name,
                current_level=current,
                current_level_name=LEVEL_NAMES[current],
                satisfied_criteria=[r for r in all_requirements if facts.get(r, False)],
                missing_criteria=[r for r in all_requirements if not facts.get(r, False)],
                next_level_requirements=levels.get(f"level_{current + 1}", {}).get(
                    "requirements", []
                ),
                blocking_findings=[
                    f.finding_id
                    for f in assessment.findings
                    if f.status == "OPEN"
                    and f.dimension in {name, "semantic_clarity", "governance"}
                ],
                evidence_refs=list(dict.fromkeys(e.evidence_id for e in assessment.evidence)),
            )
        )
    return MaturityAssessment(model_version=str(model["version"]), dimensions=dimensions)
