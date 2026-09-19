"""Persistent iterations, immutable knowledge versions, and human decisions."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field, field_validator, model_validator

from data_maturity.models.assessment import WorkbookAssessment
from data_maturity.models.core import Model
from data_maturity.util import now

Lifecycle = Literal[
    "INITIALIZED",
    "DISCOVERING",
    "PROFILING",
    "ASSESSING",
    "REASONING",
    "WAITING_FOR_HUMAN",
    "REASSESSING",
    "REMEDIATION_REQUIRED",
    "BASELINE_ESTABLISHED",
    "DEGRADED",
    "FAILED",
]
Trigger = Literal[
    "INITIAL_ASSESSMENT",
    "SOURCE_DATA_CHANGED",
    "MISSION_CONTEXT_CHANGED",
    "SME_RESPONSE_RECEIVED",
    "QUALITY_RULE_CHANGED",
    "MATURITY_MODEL_CHANGED",
    "DATA_CONTRACT_CHANGED",
    "GOVERNANCE_METADATA_CHANGED",
    "MODEL_CONFIGURATION_CHANGED",
    "MANUAL_REASSESSMENT",
    "SCHEDULED_REASSESSMENT",
]


class Resolution(Model):
    resolution_id: str
    question_id: str | None = None
    assertion_id: str | None = None
    finding_id: str | None = None
    resolution_type: Literal[
        "SME_ANSWER",
        "DATA_OWNER_DECISION",
        "GOVERNANCE_DECISION",
        "AUTHORITATIVE_REFERENCE",
        "USER_OVERRIDE",
        "RULE_UPDATE",
        "ACCEPTED_RISK",
        "ACKNOWLEDGED",
        "REMEDIATION_PLANNED",
    ] = "SME_ANSWER"
    value: Any
    provided_by: str = Field(min_length=1)
    authority: str | None = None
    authoritative: bool = False
    source_reference: str | None = None
    timestamp: datetime = Field(default_factory=now)
    rationale: str | None = None
    scope: str | None = None
    review_at: datetime | None = None

    @field_validator("timestamp", "review_at")
    @classmethod
    def timezone_required(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("Resolution timestamps must be timezone-aware")
        return value

    @model_validator(mode="after")
    def authority_required(self) -> Resolution:
        if not any((self.question_id, self.assertion_id, self.finding_id)):
            raise ValueError("Resolution requires a question, assertion, or finding target")
        if self.authoritative and not self.authority:
            raise ValueError("Authoritative resolutions require an authority")
        if self.resolution_type == "ACCEPTED_RISK" and not all(
            (self.authoritative, self.authority, self.rationale, self.scope, self.review_at)
        ):
            raise ValueError("Risk acceptance requires authority, rationale, scope and review date")
        return self


class ControlDecision(Model):
    decision: Literal[
        "CONTINUE_AUTOMATICALLY",
        "WAIT_FOR_HUMAN",
        "REMEDIATION_REQUIRED",
        "BASELINE_ESTABLISHED",
        "DEGRADED",
        "FAILED",
    ]
    reasons: list[str]
    blocking_question_refs: list[str] = Field(default_factory=list)
    blocking_finding_refs: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)


class Change(Model):
    subject: str
    previous: Any = None
    current: Any = None
    classification: Literal["IMPROVED", "UNCHANGED", "REGRESSED", "NEW_ISSUE", "CHANGED"] = (
        "CHANGED"
    )


class AssessmentDelta(Model):
    from_iteration: int
    to_iteration: int
    findings: dict[str, list[str]] = Field(default_factory=dict)
    quality: list[Change] = Field(default_factory=list)
    maturity: list[Change] = Field(default_factory=list)
    mission_fitness: list[Change] = Field(default_factory=list)
    schema_changes: list[Change] = Field(default_factory=list)
    semantic_changes: list[Change] = Field(default_factory=list)
    governance_changes: list[Change] = Field(default_factory=list)
    ai_readiness_changes: list[Change] = Field(default_factory=list)
    contract_changes: list[Change] = Field(default_factory=list)


class AssessmentIteration(Model):
    iteration_id: str
    assessment_id: str
    iteration_number: int
    trigger: Trigger
    started_at: datetime = Field(default_factory=now)
    completed_at: datetime | None = None
    changed_inputs: list[str]
    components_executed: list[str]
    components_skipped: list[str]
    new_evidence_refs: list[str] = Field(default_factory=list)
    new_finding_refs: list[str] = Field(default_factory=list)
    resolved_finding_refs: list[str] = Field(default_factory=list)
    changed_assertion_refs: list[str] = Field(default_factory=list)
    maturity_changes: list[Change] = Field(default_factory=list)
    mission_fitness_changes: list[Change] = Field(default_factory=list)
    unresolved_question_refs: list[str] = Field(default_factory=list)
    outcome: Lifecycle
    transitions: list[Lifecycle]
    decision: ControlDecision


class Baseline(Model):
    name: str
    assessment_id: str
    iteration_number: int
    created_at: datetime = Field(default_factory=now)
    fingerprints: dict[str, str]
    assessment_hash: str


class AssessmentRun(Model):
    assessment: WorkbookAssessment
    iterations: list[AssessmentIteration]
    resolutions: list[Resolution] = Field(default_factory=list)
    delta: AssessmentDelta | None = None
    baselines: list[Baseline] = Field(default_factory=list)
    snapshots: list[WorkbookAssessment] = Field(default_factory=list)
