"""Bounded interpretation of existing findings; never calculates measurements."""

from __future__ import annotations

from data_maturity.llm.gateway import LLMGateway
from data_maturity.models.assessment import DatasetAssessment
from data_maturity.models.core import Dataset, SemanticAssertion
from data_maturity.util import stable_id


class QualityAnalyst:
    def reason(
        self,
        assessment: DatasetAssessment,
        gateway: LLMGateway,
        dataset: Dataset | None,
        role: str = "quality_reasoning",
    ) -> list[SemanticAssertion]:
        response = gateway.generate(role, assessment, dataset)
        return [
            SemanticAssertion(
                assertion_id=stable_id("note", assessment.dataset_id, role, note.model_dump()),
                dataset_id=assessment.dataset_id,
                assertion_type=f"{role}_interpretation",
                statement=note.explanation,
                state="INFERRED",
                confidence=note.confidence,
                evidence_refs=note.evidence_refs,
                reasoning="Model interpretation of supplied findings; not an authoritative measurement",
                origin="llm",
                alternatives=["Operational significance requires domain confirmation"],
            )
            for note in response.interpretations
        ]
