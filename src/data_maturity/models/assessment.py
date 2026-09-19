"""Quality, maturity, mission, governance and product assessment contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from data_maturity.models.core import (
    DatasetProfile,
    DatasetSchema,
    DatasetStructure,
    Evidence,
    EvidenceEdge,
    Finding,
    KeyCandidate,
    Model,
    Relationship,
    SemanticAssertion,
    Severity,
    SMEQuestion,
    SourceMetadata,
)
from data_maturity.util import now


class QualityRule(Model):
    rule_id: str
    dataset: str | None = None
    field: str
    dimension: str
    operator: Literal["not_null", "unique", "range", "enum", "pattern", "type", "freshness"]
    parameters: dict[str, Any] = Field(default_factory=dict)
    severity: Severity = "high"
    origin: Literal["OBSERVED", "INFERRED", "USER_DEFINED", "MISSION_DEFINED"] = "USER_DEFINED"


class QualityMetric(Model):
    metric_id: str
    dimension: str
    name: str
    value: float | int | None
    denominator: int | None = None
    field_id: str | None = None
    status: Literal["PASS", "FAIL", "WARNING", "NOT_APPLICABLE", "UNDETERMINED"]
    evidence_refs: list[str]
    rule_id: str | None = None
    scope: Literal["full", "sample", "metadata"] = "full"
    explanation: str


class QualityAssessment(Model):
    metrics: list[QualityMetric] = Field(default_factory=list)
    rules: list[QualityRule] = Field(default_factory=list)


class GovernanceItem(Model):
    property: str
    status: Literal["PRESENT", "PARTIAL", "ABSENT", "UNRESOLVED", "NOT_APPLICABLE"]
    value: Any = None
    evidence_refs: list[str] = Field(default_factory=list)
    assertion_id: str


class GovernanceAssessment(Model):
    items: list[GovernanceItem] = Field(default_factory=list)


class MaturityDimensionAssessment(Model):
    dimension: str
    current_level: int = Field(ge=0, le=5)
    current_level_name: str
    satisfied_criteria: list[str]
    missing_criteria: list[str]
    next_level_requirements: list[str]
    blocking_findings: list[str]
    evidence_refs: list[str]


class MaturityAssessment(Model):
    model_version: str
    dimensions: list[MaturityDimensionAssessment] = Field(default_factory=list)


class ReadinessCriterion(Model):
    criterion: str
    status: Literal["SATISFIED", "BLOCKED", "UNDETERMINED"]
    reason: str
    evidence_refs: list[str]
    finding_refs: list[str] = Field(default_factory=list)


class AIReadinessAssessment(Model):
    status: Literal["READY", "NOT_READY", "UNDETERMINED"] = "UNDETERMINED"
    criteria: list[ReadinessCriterion] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)


class Recommendation(Model):
    recommendation_id: str
    title: str
    description: str
    priority: Severity
    priority_score: float
    priority_basis: dict[str, float]
    effort: Literal["low", "medium", "high", "unknown"] = "unknown"
    category: str
    finding_refs: list[str] = Field(min_length=1)
    evidence_refs: list[str] = Field(min_length=1)
    mission_requirement_refs: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    target_maturity_dimension: str


class MissionUseCase(Model):
    id: str
    description: str


class MissionWorkflow(Model):
    id: str
    description: str
    steps: list[str] = Field(default_factory=list)


class DataRequirement(Model):
    id: str
    description: str
    criticality: Severity = "high"
    dataset: str | None = None
    fields: list[str] = Field(default_factory=list)
    check: Literal[
        "completeness", "uniqueness", "semantic", "governance", "freshness", "rule", "unspecified"
    ] = "unspecified"
    property: str | None = None
    threshold: float = Field(default=1.0, ge=0, le=1)
    max_age_days: float | None = Field(default=None, ge=0)
    rule_id: str | None = None


class MissionContext(Model):
    mission_name: str | None = None
    mission_description: str | None = None
    use_cases: list[MissionUseCase] = Field(default_factory=list)
    workflows: list[MissionWorkflow] = Field(default_factory=list)
    user_types: list[str] = Field(default_factory=list)
    tooling_requirements: list[str] = Field(default_factory=list)
    data_requirements: list[DataRequirement] = Field(default_factory=list)
    criticality: Severity | None = None


class MissionRequirementAssessment(Model):
    requirement_id: str
    status: Literal["FIT", "PARTIALLY_FIT", "NOT_FIT", "UNDETERMINED"]
    reason: str
    dataset_ids: list[str]
    field_ids: list[str]
    evidence_refs: list[str]
    finding_refs: list[str] = Field(default_factory=list)


class DataContract(Model):
    contract_id: str
    contract_version: str = "0.1.1"
    status: Literal["proposed"] = "proposed"
    dataset_id: str
    name: str
    description: str | None = None
    owner: Any = None
    schema_definition: DatasetSchema
    keys: list[KeyCandidate]
    relationships: list[Relationship]
    quality_rules: list[QualityRule]
    update_expectations: Any = None
    provenance: dict[str, Any]
    governance: GovernanceAssessment
    mission_requirement_refs: list[str]
    unresolved_items: list[str]


class ComponentStatus(Model):
    component: str
    status: Literal["COMPLETE", "SKIPPED", "FAILED", "CACHED"]
    dataset_id: str | None = None
    stage: str
    reason: str | None = None
    recoverable: bool = True


class InferenceRecord(Model):
    role: str
    provider: str
    model: str | None
    prompt_version: str
    attempts: int
    status: Literal["COMPLETE", "FAILED", "CACHED"]
    context_hash: str
    error: str | None = None


class DatasetAssessment(Model):
    dataset_id: str
    source: SourceMetadata
    structure: DatasetStructure
    physical_schema: DatasetSchema
    profile: DatasetProfile
    quality: QualityAssessment
    keys: list[KeyCandidate] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    assertions: list[SemanticAssertion] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    unresolved_questions: list[SMEQuestion] = Field(default_factory=list)
    governance: GovernanceAssessment = Field(default_factory=GovernanceAssessment)
    maturity: MaturityAssessment = Field(
        default_factory=lambda: MaturityAssessment(model_version="1")
    )
    ai_readiness: AIReadinessAssessment = Field(default_factory=AIReadinessAssessment)
    recommendations: list[Recommendation] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    target_schema: DatasetSchema | None = None
    proposed_contract: DataContract | None = None
    analyst_notes: list[SemanticAssertion] = Field(default_factory=list)


class WorkbookAssessment(Model):
    assessment_id: str
    application_version: str = "0.1.2"
    source: SourceMetadata
    created_at: datetime = Field(default_factory=now)
    datasets: list[DatasetAssessment]
    mission_context: MissionContext | None = None
    mission_fitness: list[MissionRequirementAssessment] = Field(default_factory=list)
    graph: list[EvidenceEdge] = Field(default_factory=list)
    component_status: list[ComponentStatus] = Field(default_factory=list)
    inference_records: list[InferenceRecord] = Field(default_factory=list)
    fingerprints: dict[str, str] = Field(default_factory=dict)
    configuration: dict[str, Any] = Field(default_factory=dict)
