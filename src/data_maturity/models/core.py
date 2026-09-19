"""Canonical measured data and evidence. Raw rows never enter serialized assessments."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from data_maturity.util import now

State = Literal["OBSERVED", "INFERRED", "UNRESOLVED"]
Severity = Literal["info", "low", "medium", "high", "critical"]
PhysicalType = Literal[
    "integer", "float", "boolean", "string", "date", "datetime", "categorical", "mixed", "unknown"
]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, allow_inf_nan=False)


class SourceLocation(Model):
    workbook: str
    worksheet: str | None = None
    table: str | None = None
    column: str | None = None
    row: int | None = None
    cell_range: str | None = None
    calculation: str | None = None


class SourceMetadata(Model):
    name: str
    sha256: str
    format: str
    size_bytes: int = Field(ge=0)
    inspection: dict[str, Any] = Field(default_factory=dict)


class DatasetStructure(Model):
    worksheet: str | None = None
    table: str
    cell_range: str
    header_row: int = Field(ge=1)
    confidence: float = Field(ge=0, le=1)
    detection_method: str
    alternatives: list[str] = Field(default_factory=list)
    collisions: list[str] = Field(default_factory=list)
    source_row_count: int = Field(ge=0)
    rows_scanned: int = Field(ge=0)
    rows_retained: int = Field(ge=0)
    sampled: bool = False
    truncated: bool = False
    sampling_method: str = "full"
    seed: int = 42
    formula_count: int = 0
    formula_locations: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class FieldDefinition(Model):
    field_id: str
    source_name: str
    canonical_name: str
    physical_type: PhysicalType = "unknown"
    semantic_type: str | None = None
    description: str | None = None
    nullable: bool | None = None
    unit: str | None = None
    format: str | None = None
    enum: list[Any] | None = None
    constraints: dict[str, Any] = Field(default_factory=dict)
    key_membership: list[str] = Field(default_factory=list)
    provenance: list[str] = Field(default_factory=list)
    unresolved_properties: list[str] = Field(default_factory=lambda: ["definition", "nullable"])
    status: Literal["observed", "proposed", "authoritative"] = "observed"


class DatasetSchema(Model):
    fields: list[FieldDefinition]
    status: Literal["observed", "proposed", "authoritative"] = "observed"


class Dataset(Model):
    dataset_id: str
    source: SourceMetadata
    structure: DatasetStructure
    fields: list[FieldDefinition]
    rows: list[list[Any]] = Field(exclude=True)
    source_rows: list[int] = Field(exclude=True)


class Evidence(Model):
    evidence_id: str
    evidence_type: str
    dataset_id: str
    field: str | None = None
    description: str
    value: Any = None
    source_location: SourceLocation | None = None
    generated_by: str
    timestamp: datetime = Field(default_factory=now)
    state: Literal["OBSERVED"] = "OBSERVED"
    scope: Literal["full", "sample", "metadata", "human"] = "full"


class EvidenceEdge(Model):
    source_id: str
    relationship: str
    target_id: str


class ColumnProfile(Model):
    field_id: str
    row_count: int = Field(ge=0)
    null_count: int = Field(ge=0)
    null_percentage: float = Field(ge=0, le=100)
    unique_count: int = Field(ge=0)
    uniqueness_ratio: float = Field(ge=0, le=1)
    duplicate_count: int = Field(ge=0)
    duplicate_frequency: float = Field(ge=0, le=1)
    physical_type: PhysicalType
    type_counts: dict[str, int]
    mixed_type_rate: float = Field(ge=0, le=1)
    minimum: Any = None
    maximum: Any = None
    mean: float | None = None
    median: float | None = None
    standard_deviation: float | None = None
    quantiles: dict[str, float] = Field(default_factory=dict)
    min_length: int | None = None
    max_length: int | None = None
    common_values: list[dict[str, Any]] = Field(default_factory=list)
    likely_enum: list[Any] = Field(default_factory=list)
    invalid_date_count: int = 0
    date_format_counts: dict[str, int] = Field(default_factory=dict)
    whitespace_count: int = 0
    casing_variation_count: int = 0
    numeric_string_count: int = 0
    nonfinite_count: int = 0
    anomaly_counts: dict[str, int] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)


class DatasetProfile(Model):
    row_count: int
    source_row_count: int
    sampled: bool
    scope: Literal["full", "sample"]
    duplicate_record_count: int
    columns: list[ColumnProfile]
    evidence_refs: list[str] = Field(default_factory=list)


class SemanticAssertion(Model):
    assertion_id: str
    dataset_id: str
    field_ids: list[str] = Field(default_factory=list)
    assertion_type: str
    statement: str
    value: Any = None
    state: State
    confidence: float | None = Field(default=None, ge=0, le=1)
    evidence_refs: list[str] = Field(default_factory=list)
    reasoning: str = ""
    alternatives: list[str] = Field(default_factory=list)
    requires_sme_confirmation: bool = False
    supersedes: str | None = None
    superseded_by: str | None = None
    resolved_by: str | None = None
    origin: Literal["deterministic", "llm", "human"] = "deterministic"

    @model_validator(mode="after")
    def knowledge_state(self) -> SemanticAssertion:
        if self.state == "UNRESOLVED" and self.confidence is not None:
            raise ValueError("Unresolved assertions cannot carry confidence")
        if self.state == "INFERRED" and (
            self.confidence is None or not self.evidence_refs or not self.reasoning
        ):
            raise ValueError("Inference requires confidence, evidence and reasoning")
        if self.state == "OBSERVED" and not self.evidence_refs:
            raise ValueError("Observed assertions require evidence")
        if self.origin == "llm" and self.state == "OBSERVED":
            raise ValueError("A model cannot create observed facts")
        return self


class Finding(Model):
    finding_id: str
    dataset_id: str
    field_ids: list[str] = Field(default_factory=list)
    finding_type: str
    dimension: str
    title: str
    description: str
    severity: Severity
    severity_basis: str
    state: State = "OBSERVED"
    confidence: float | None = Field(default=None, ge=0, le=1)
    reasoning: str = ""
    alternatives: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(min_length=1)
    recommendation_refs: list[str] = Field(default_factory=list)
    mission_requirement_refs: list[str] = Field(default_factory=list)
    affected_count: int | None = None
    affected_percentage: float | None = Field(default=None, ge=0, le=100)
    status: Literal[
        "OPEN", "ACKNOWLEDGED", "REMEDIATION_PLANNED", "RESOLVED", "ACCEPTED_RISK", "SUPERSEDED"
    ] = "OPEN"

    @model_validator(mode="after")
    def inference_support(self) -> Finding:
        if self.state == "INFERRED" and (self.confidence is None or not self.reasoning):
            raise ValueError("Inferred findings require confidence and reasoning")
        if self.state == "UNRESOLVED" and self.confidence is not None:
            raise ValueError("Unresolved findings cannot carry confidence")
        return self


class SMEQuestion(Model):
    question_id: str
    dataset_id: str
    field_ids: list[str] = Field(default_factory=list)
    question: str
    rationale: str
    priority: Severity
    resolves_assertion_refs: list[str]
    related_finding_refs: list[str] = Field(default_factory=list)
    blocking: bool = True
    status: Literal["OPEN", "ANSWERED", "ACCEPTED_RISK"] = "OPEN"


class Relationship(Model):
    relationship_id: str
    source_dataset_id: str
    source_field_id: str
    target_dataset_id: str
    target_field_id: str
    cardinality: Literal["ONE_TO_ONE", "ONE_TO_MANY", "MANY_TO_ONE", "MANY_TO_MANY"]
    containment: float = Field(ge=0, le=1)
    orphan_count: int = Field(ge=0)
    null_count: int = Field(ge=0)
    confidence: float = Field(ge=0, le=1)
    state: Literal["INFERRED"] = "INFERRED"
    reasoning: str
    alternatives: list[str] = Field(
        default_factory=lambda: ["Coincidental overlap; not an authoritative foreign key"]
    )
    evidence_refs: list[str] = Field(min_length=1)
    scope: Literal["full", "sample"]


class KeyCandidate(Model):
    key_id: str
    field_ids: list[str]
    kind: Literal["primary", "composite", "natural", "surrogate"]
    confidence: float = Field(ge=0, le=1)
    state: Literal["INFERRED"] = "INFERRED"
    reasoning: str
    alternatives: list[str] = Field(
        default_factory=lambda: ["Uniqueness may not persist across future records"]
    )
    evidence_refs: list[str] = Field(min_length=1)
    scope: Literal["full", "sample"]
