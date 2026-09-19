"""Readiness requires semantics, governance and intended-use evidence, not cleanliness."""

from __future__ import annotations

from data_maturity.maturity.evaluator import criterion_facts
from data_maturity.models.assessment import (
    AIReadinessAssessment,
    DatasetAssessment,
    ReadinessCriterion,
)


def evaluate_readiness(
    assessment: DatasetAssessment, mission_fit: bool | None
) -> AIReadinessAssessment:
    facts = criterion_facts(assessment)
    mapping = {
        "accessibility": "machine_accessible",
        "structure": "stable_tabular_structure",
        "semantics": "semantics_resolved",
        "quality": "quality_controlled",
        "provenance": "provenance_documented",
        "lineage": "lineage_documented",
        "governance": "governance_defined",
        "documentation": "field_definitions_present",
        "contracts": "contract_authoritative",
        "stability": "schema_versioned",
        "observability": "monitoring_operational",
    }
    refs = [e.evidence_id for e in assessment.evidence]
    criteria = [
        ReadinessCriterion(
            criterion=name,
            status="SATISFIED" if facts[criterion] else "BLOCKED",
            reason=f"Explicit criterion '{criterion}' {'satisfied' if facts[criterion] else 'not established'}",
            evidence_refs=refs,
            finding_refs=[f.finding_id for f in assessment.findings if f.status == "OPEN"],
        )
        for name, criterion in mapping.items()
    ]
    criteria.append(
        ReadinessCriterion(
            criterion="suitability",
            status="UNDETERMINED"
            if mission_fit is None
            else "SATISFIED"
            if mission_fit
            else "BLOCKED",
            reason="Requires explicit intended-use requirements and their evidence-backed evaluation",
            evidence_refs=refs,
        )
    )
    blockers = [c.criterion for c in criteria if c.status != "SATISFIED"]
    return AIReadinessAssessment(
        status="READY"
        if not blockers
        else "NOT_READY"
        if any(c.status == "BLOCKED" for c in criteria)
        else "UNDETERMINED",
        criteria=criteria,
        blockers=blockers,
    )
