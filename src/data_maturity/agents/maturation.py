"""Deterministic remediation sequencing derived from active findings."""

from __future__ import annotations

from data_maturity.models.assessment import DatasetAssessment, Recommendation
from data_maturity.util import stable_id

ACTIONS = {
    "completeness": "Confirm requiredness and obtain missing values from the authoritative source; add a not-null rule only after approval.",
    "uniqueness": "Confirm entity granularity and key authority; quarantine duplicates for owner review before deduplicating.",
    "consistency": "Review variants against original values; approve a canonical mapping and enforce it during ingestion.",
    "conformity": "Define a canonical representation with the owner and validate formatting at ingestion; preserve original values in lineage.",
    "validity": "Review failing records against the explicit rule or field definition; correct from an authoritative source and rerun validation.",
    "integrity": "Confirm the candidate relationship with owners; reconcile unmatched references against the authoritative parent dataset.",
    "accuracy_proxies": "Review potential anomalies with a domain expert; do not delete statistical extremes solely because they are outliers.",
    "semantic_clarity": "Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract.",
    "governance": "Obtain the missing governance decision from the accountable owner and record authority, source reference and review date.",
    "mission_fitness": "Resolve the linked mission requirement using its explicit acceptance criteria, then reassess fitness independently of general quality.",
}


class MaturationAnalyst:
    def recommend(self, assessment: DatasetAssessment) -> list[Recommendation]:
        results = []
        weights = {"info": 0.5, "low": 1, "medium": 2, "high": 3, "critical": 4}
        for f in assessment.findings:
            f.recommendation_refs = []
            if f.status in {"RESOLVED", "SUPERSEDED", "ACCEPTED_RISK"}:
                continue
            factors = {
                "severity": weights[f.severity] * 10,
                "affected_rows": (f.affected_percentage or 0) / 10,
                "mission_dependency": min(20, len(f.mission_requirement_refs) * 5),
                "maturity_blocker": 5
                if f.dimension in {"semantic_clarity", "governance", "schema_definition"}
                else 0,
                "effort": 0,
            }
            rid = stable_id("recommendation", f.finding_id)
            results.append(
                Recommendation(
                    recommendation_id=rid,
                    title=f"Resolve: {f.title}",
                    description=ACTIONS.get(
                        f.dimension,
                        "Review the linked evidence, agree an explicit expectation, remediate and reassess.",
                    ),
                    priority=f.severity,
                    priority_score=sum(factors.values()),
                    priority_basis=factors,
                    category=f.dimension,
                    finding_refs=[f.finding_id],
                    evidence_refs=f.evidence_refs,
                    mission_requirement_refs=f.mission_requirement_refs,
                    target_maturity_dimension=f.dimension,
                )
            )
            f.recommendation_refs = [rid]
        prerequisites = [r.recommendation_id for r in results if r.category == "semantic_clarity"]
        for recommendation in results:
            if recommendation.category in {"uniqueness", "integrity"}:
                recommendation.dependencies = prerequisites
        return sorted(results, key=lambda r: (-r.priority_score, r.recommendation_id))
