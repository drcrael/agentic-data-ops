"""Evidence-linked semantic candidates and targeted authoritative questions."""

from __future__ import annotations

from typing import Any

from data_maturity.llm.gateway import LLMGateway
from data_maturity.models.assessment import DatasetAssessment
from data_maturity.models.core import (
    Dataset,
    Evidence,
    SemanticAssertion,
    SMEQuestion,
    SourceLocation,
)
from data_maturity.profiling.quality import finding
from data_maturity.util import stable_id


def metadata_evidence(
    assessment: DatasetAssessment, kind: str, value: Any, field: str | None = None
) -> Evidence:
    ev = Evidence(
        evidence_id=stable_id(
            "evidence", assessment.dataset_id, assessment.source.sha256, kind, field, value
        ),
        evidence_type=kind,
        dataset_id=assessment.dataset_id,
        field=field,
        value=value,
        description=kind.replace("_", " "),
        generated_by="assessment_metadata/0.1.1",
        scope="metadata",
        source_location=SourceLocation(
            workbook=assessment.source.name,
            worksheet=assessment.structure.worksheet,
            table=assessment.structure.table,
        ),
    )
    if ev.evidence_id not in {e.evidence_id for e in assessment.evidence}:
        assessment.evidence.append(ev)
    return ev


def add_gap(
    assessment: DatasetAssessment,
    kind: str,
    field_ids: list[str],
    question: str,
    refs: list[str],
    alternatives: list[str] | None = None,
    blocking: bool = True,
) -> None:
    aid = stable_id("assertion", assessment.dataset_id, kind, field_ids)
    if aid in {a.assertion_id for a in assessment.assertions}:
        return
    assertion = SemanticAssertion(
        assertion_id=aid,
        dataset_id=assessment.dataset_id,
        field_ids=field_ids,
        assertion_type=kind,
        statement=f"{kind.replace('_', ' ')} cannot be established from supplied evidence",
        state="UNRESOLVED",
        evidence_refs=refs,
        alternatives=alternatives or [],
        requires_sme_confirmation=True,
    )
    assessment.assertions.append(assertion)
    f = finding(
        assessment.dataset_id,
        f"unresolved_{kind}",
        "governance" if kind.startswith("governance_") else "semantic_clarity",
        refs,
        field_ids,
        severity="high" if blocking else "medium",
        description=assertion.statement,
    )
    f.state = "UNRESOLVED"
    assessment.findings.append(f)
    assessment.unresolved_questions.append(
        SMEQuestion(
            question_id=stable_id("question", aid),
            dataset_id=assessment.dataset_id,
            field_ids=field_ids,
            question=question,
            rationale="Required to replace uncertainty with an attributable definition or contract decision",
            priority="high" if blocking else "medium",
            resolves_assertion_refs=[aid],
            related_finding_refs=[f.finding_id],
            blocking=blocking,
        )
    )


class SemanticAnalyst:
    def deterministic(self, assessment: DatasetAssessment) -> None:
        coordinate_fields: list[str] = []
        coordinate_refs: list[str] = []
        for field, profile in zip(
            assessment.physical_schema.fields, assessment.profile.columns, strict=True
        ):
            name = field.canonical_name
            semantic = None
            if name == "id" or name.endswith("_id"):
                semantic = "identifier"
            elif name in {"x", "y", "z", "position_x", "position_y", "position_z"}:
                semantic = "coordinate"
                coordinate_fields.append(field.field_id)
                coordinate_refs.extend(profile.evidence_refs)
            elif any(t in name for t in ("epoch", "timestamp", "created_at", "updated_at")):
                semantic = "timestamp"
            elif name in {"status", "state", "category"}:
                semantic = "status" if name == "status" else "category"
            elif "email" in name:
                semantic = "email"
            elif "name" in name:
                semantic = "name"
            if semantic:
                assessment.assertions.append(
                    SemanticAssertion(
                        assertion_id=stable_id("assertion", field.field_id, "semantic_type"),
                        dataset_id=assessment.dataset_id,
                        field_ids=[field.field_id],
                        assertion_type="semantic_type",
                        statement=f"{name} likely represents {semantic}",
                        value=semantic,
                        state="INFERRED",
                        confidence=0.75,
                        evidence_refs=profile.evidence_refs,
                        reasoning="Field name heuristic; profile supports structural inspection, not business authority",
                        alternatives=["Domain-specific meaning may differ"],
                        requires_sme_confirmation=True,
                    )
                )
            add_gap(
                assessment,
                "definition",
                [field.field_id],
                f"What is the authoritative business definition of '{field.source_name}' in {assessment.structure.worksheet or assessment.structure.table}?",
                profile.evidence_refs,
                blocking=False,
            )
            if semantic == "timestamp":
                add_gap(
                    assessment,
                    "temporal_semantics",
                    [field.field_id],
                    f"Does '{field.source_name}' record event, processing or publication time, and what timezone/time scale and freshness limit apply?",
                    profile.evidence_refs,
                )
            if semantic == "status":
                add_gap(
                    assessment,
                    "code_definitions",
                    [field.field_id],
                    f"'{field.source_name}' has {profile.unique_count} distinct non-null values in measured scope. What is the authoritative code dictionary and permitted vocabulary?",
                    profile.evidence_refs,
                )
            if semantic == "email":
                assessment.findings.append(
                    finding(
                        assessment.dataset_id,
                        "potential_sensitive_data",
                        "governance",
                        profile.evidence_refs,
                        [field.field_id],
                        description="Field naming suggests possible contact information; this is not a formal security or legal classification",
                        inferred=True,
                    )
                )
        if coordinate_fields:
            add_gap(
                assessment,
                "coordinate_unit",
                coordinate_fields,
                "What are the authoritative units for the coordinate fields? Provide the source definition.",
                coordinate_refs,
                ["millimeters", "meters", "other"],
            )
            add_gap(
                assessment,
                "coordinate_reference_frame",
                coordinate_fields,
                "What coordinate frame and realization apply, including origin, axis directions and definition version?",
                coordinate_refs,
                ["documented local frame", "documented global frame", "other"],
            )
        if assessment.keys:
            refs = list(dict.fromkeys(e for k in assessment.keys for e in k.evidence_refs))
            add_gap(
                assessment,
                "authoritative_key",
                [],
                "Which candidate key is authoritative, and what entity/time granularity and future uniqueness guarantees apply?",
                refs,
            )

    def reason(
        self, assessment: DatasetAssessment, gateway: LLMGateway, dataset: Dataset | None
    ) -> list[SemanticAssertion]:
        response = gateway.generate("semantic_inference", assessment, dataset)
        assertions = []
        for proposal in response.proposals:
            assertions.append(
                SemanticAssertion(
                    assertion_id=stable_id(
                        "assertion", assessment.dataset_id, "llm", proposal.model_dump()
                    ),
                    dataset_id=assessment.dataset_id,
                    field_ids=proposal.field_ids,
                    assertion_type="semantic_type",
                    statement=f"Model proposes semantic type '{proposal.semantic_type}'; human confirmation required",
                    value=proposal.semantic_type,
                    state="INFERRED",
                    confidence=proposal.confidence,
                    evidence_refs=proposal.evidence_refs,
                    reasoning=proposal.reasoning,
                    alternatives=proposal.alternatives,
                    requires_sme_confirmation=True,
                    origin="llm",
                )
            )
        return assertions
