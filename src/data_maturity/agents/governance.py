"""Governance comes from explicit metadata or resolutions, never guesses."""

from __future__ import annotations

from typing import Literal

from data_maturity.agents.semantic import add_gap, metadata_evidence
from data_maturity.config import Config
from data_maturity.models.assessment import DatasetAssessment, GovernanceAssessment, GovernanceItem
from data_maturity.models.core import SemanticAssertion
from data_maturity.util import stable_id

GOVERNANCE_PROPERTIES = [
    "owner",
    "steward",
    "authoritative_source",
    "source_system",
    "provenance",
    "lineage",
    "sensitivity",
    "security_classification",
    "access_constraints",
    "retention",
    "update_cadence",
    "version",
    "licensing",
    "quality_accountability",
]


class GovernanceAnalyst:
    def assess(self, assessment: DatasetAssessment, config: Config) -> None:
        metadata = dict(config.governance_metadata.get("*", {}))
        for key in (
            assessment.structure.worksheet,
            assessment.structure.table,
            assessment.dataset_id,
        ):
            metadata.update(config.governance_metadata.get(key or "", {}))
        items = []
        status: Literal["PRESENT", "UNRESOLVED"]
        for prop in GOVERNANCE_PROPERTIES:
            ev = metadata_evidence(
                assessment,
                "governance_metadata",
                {"property": prop, "supplied": prop in metadata, "value": metadata.get(prop)},
            )
            kind = f"governance_{prop}"
            aid = stable_id("assertion", assessment.dataset_id, kind, [])
            if prop in metadata and metadata[prop] is not None:
                assertion = SemanticAssertion(
                    assertion_id=aid,
                    dataset_id=assessment.dataset_id,
                    assertion_type=kind,
                    statement=f"User-supplied governance metadata documents {prop}",
                    value=metadata[prop],
                    state="OBSERVED",
                    evidence_refs=[ev.evidence_id],
                )
                assessment.assertions.append(assertion)
                status = "PRESENT"
            else:
                add_gap(
                    assessment,
                    kind,
                    [],
                    f"Who can authoritatively document {prop.replace('_', ' ')} for '{assessment.structure.worksheet or assessment.structure.table}', and provide a source reference?",
                    [ev.evidence_id],
                    blocking=prop in {"owner", "authoritative_source", "security_classification"},
                )
                status = "UNRESOLVED"
            items.append(
                GovernanceItem(
                    property=prop,
                    status=status,
                    value=metadata.get(prop),
                    evidence_refs=[ev.evidence_id],
                    assertion_id=aid,
                )
            )
        assessment.governance = GovernanceAssessment(items=items)

    def refresh(self, assessment: DatasetAssessment) -> None:
        current = {
            a.assertion_type: a
            for a in assessment.assertions
            if not a.superseded_by and a.assertion_type.startswith("governance_")
        }
        for item in assessment.governance.items:
            assertion = current.get(f"governance_{item.property}")
            if assertion:
                item.assertion_id = assertion.assertion_id
                item.value = assertion.value if assertion.state == "OBSERVED" else None
                item.status = "PRESENT" if assertion.state == "OBSERVED" else "UNRESOLVED"
                item.evidence_refs = assertion.evidence_refs
