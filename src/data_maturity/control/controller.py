"""Event-driven assessment feedback controller with explicit human gates."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import cast

from data_maturity import __version__
from data_maturity.agents.orchestrator import AssessmentOrchestrator
from data_maturity.config import Config
from data_maturity.control.comparison import compare
from data_maturity.control.dependencies import affected_stages
from data_maturity.control.history import enrich_regressions, retain_resolved_findings
from data_maturity.control.resolutions import apply_resolutions, expire_risks
from data_maturity.evidence.graph import build_graph, downstream
from data_maturity.evidence.validation import validate_assessment
from data_maturity.llm.gateway import LLMGateway
from data_maturity.models.assessment import MissionContext, WorkbookAssessment
from data_maturity.models.control import (
    AssessmentIteration,
    AssessmentRun,
    Baseline,
    ControlDecision,
    Lifecycle,
    Resolution,
    Trigger,
)
from data_maturity.util import digest, file_hash, now, stable_id

STAGES = [
    "ingestion",
    "discovery",
    "profiling",
    "quality",
    "relationships",
    "semantics",
    "governance",
    "reasoning",
    "mission",
    "maturity",
    "recommendations",
    "contract",
]

FINGERPRINT_FORMAT = "canonical-json-v2"


def structured_fingerprints(config: Config, resolutions: list[Resolution]) -> dict[str, str]:
    """Inputs containing nested models; also used to compare legacy saved histories."""
    return {
        "quality_rules": digest(config.quality_rules),
        "resolutions": digest(resolutions),
        "models": digest(
            {
                "models": config.models,
                "enabled": config.llm_enabled,
                "context": config.llm_context,
                "security": config.security,
            }
        ),
    }


def decide(workbook: WorkbookAssessment) -> ControlDecision:
    questions = [
        q.question_id
        for d in workbook.datasets
        for q in d.unresolved_questions
        if q.blocking and q.status == "OPEN"
    ]
    findings = [
        f.finding_id
        for d in workbook.datasets
        for f in d.findings
        if f.status == "OPEN" and f.severity in {"high", "critical"}
    ]
    failures = [s.component for s in workbook.component_status if s.status == "FAILED"]
    if questions:
        return ControlDecision(
            decision="WAIT_FOR_HUMAN",
            reasons=[
                "Authoritative knowledge is missing; further model calls cannot establish it",
                *(["Optional reasoning degraded"] if failures else []),
            ],
            blocking_question_refs=questions,
            blocking_finding_refs=findings,
            next_actions=[
                "Answer or explicitly accept risk for blocking SME questions, then resolve and reassess"
            ],
        )
    if failures:
        return ControlDecision(
            decision="DEGRADED",
            reasons=["Deterministic evidence is valid but optional reasoning failed"],
            next_actions=["Review recorded component failures"],
        )
    if findings:
        return ControlDecision(
            decision="REMEDIATION_REQUIRED",
            reasons=["Trustworthy current-state baseline established; material findings remain"],
            blocking_finding_refs=findings,
            next_actions=["Remediate prioritized findings and reassess changed inputs"],
        )
    return ControlDecision(
        decision="BASELINE_ESTABLISHED",
        reasons=["Evidence integrity, deterministic evaluation and authoritative gates passed"],
        next_actions=["Optionally name this baseline and compare future data"],
    )


class AssessmentController:
    def __init__(self, config: Config, gateway: LLMGateway | None = None) -> None:
        self.config = config
        self.orchestrator = AssessmentOrchestrator(config, gateway)

    def fingerprints(
        self, source: Path, mission: MissionContext | None, resolutions: list[Resolution]
    ) -> dict[str, str]:
        prompts = {
            p.name: p.read_text()
            for p in files("data_maturity.prompts").iterdir()
            if p.name.endswith(".txt")
        }
        structured = structured_fingerprints(self.config, resolutions)
        return {
            "source": file_hash(source),
            "profiling": digest(self.config.profiling),
            "sampling_seed": digest(self.config.runtime.random_seed),
            "quality_rules": structured["quality_rules"],
            "maturity_model": digest(self.config.maturity_model),
            "mission": digest(mission),
            "resolutions": structured["resolutions"],
            "governance": digest(self.config.governance_metadata),
            "models": structured["models"],
            "prompts": digest(prompts),
        }

    def run(
        self,
        source: Path,
        mission_context: MissionContext | None = None,
        prior_assessment: AssessmentRun | WorkbookAssessment | None = None,
        resolutions: list[Resolution] | None = None,
        trigger: Trigger | None = None,
        baseline: str | None = None,
        compare_baseline: str | None = None,
    ) -> AssessmentRun:
        started = now()
        self.orchestrator.gateway.preflight()
        previous_run = prior_assessment if isinstance(prior_assessment, AssessmentRun) else None
        previous = (
            previous_run.assessment
            if previous_run
            else prior_assessment
            if isinstance(prior_assessment, WorkbookAssessment)
            else None
        )
        previous_resolutions = list(previous_run.resolutions) if previous_run else []
        incoming = resolutions or []
        existing = {r.resolution_id: r for r in previous_resolutions}
        for r in incoming:
            if r.resolution_id in existing and existing[r.resolution_id] != r:
                raise ValueError("Resolution ID cannot be reused with different content")
        new_resolutions = [r for r in incoming if r.resolution_id not in existing]
        all_resolutions = [*previous_resolutions, *new_resolutions]
        if mission_context is None and previous:
            mission_context = previous.mission_context
        fingerprints = self.fingerprints(source, mission_context, all_resolutions)
        previous_inputs = dict(previous.fingerprints) if previous else {}
        if previous and previous_inputs.get("fingerprint_format") != FINGERPRINT_FORMAT:
            # Compare persisted input values using the new encoding, without rewriting
            # historical snapshots or their baseline hashes. Keep stored source/prompt
            # hashes so real external changes still invalidate the appropriate stages.
            legacy_inputs = structured_fingerprints(
                Config.model_validate(previous.configuration), previous_resolutions
            )
            if not previous_run:
                # A standalone assessment cannot recover its prior resolution ledger.
                legacy_inputs.pop("resolutions")
            previous_inputs.update(legacy_inputs)
        changed = [
            k for k, v in fingerprints.items() if not previous or previous_inputs.get(k) != v
        ]
        iterations = list(previous_run.iterations) if previous_run else []
        number = len(iterations) + 1
        transitions: list[Lifecycle] = ["INITIALIZED" if previous is None else "REASSESSING"]
        triggers: dict[str, Trigger] = {
            "source": "SOURCE_DATA_CHANGED",
            "mission": "MISSION_CONTEXT_CHANGED",
            "resolutions": "SME_RESPONSE_RECEIVED",
            "quality_rules": "QUALITY_RULE_CHANGED",
            "maturity_model": "MATURITY_MODEL_CHANGED",
            "governance": "GOVERNANCE_METADATA_CHANGED",
            "models": "MODEL_CONFIGURATION_CHANGED",
        }
        actual_trigger = cast(
            Trigger,
            trigger
            or (
                "INITIAL_ASSESSMENT"
                if previous is None
                else next((triggers[k] for k in changed if k in triggers), "MANUAL_REASSESSMENT")
            ),
        )
        planned = affected_stages(changed)
        full = (
            previous is None
            or "ingestion" in planned
            or bool(set(changed) & {"quality_rules", "governance"})
        )
        if full:
            transitions.extend(["DISCOVERING", "PROFILING", "ASSESSING"])
            reuse = (
                previous
                if previous and not set(changed) & {"source", "profiling", "sampling_seed"}
                else None
            )
            workbook = self.orchestrator.assess(source, mission_context, reuse_measurements=reuse)
            executed = [s for s in STAGES if not (reuse and s == "profiling")]
            # Same-source rule/config changes may reuse attributed answers safely. Source changes
            # require explicit re-confirmation; previous resolutions remain in the audit trail.
            applicable = (
                all_resolutions
                if previous and previous.source.sha256 == workbook.source.sha256
                else new_resolutions
            )
        else:
            assert previous is not None
            workbook = previous.model_copy(deep=True)
            workbook.assessment_id = stable_id("assessment", fingerprints, number)
            workbook.created_at = now()
            workbook.mission_context = mission_context
            workbook.configuration = self.config.model_dump(mode="json")
            executed = []
            applicable = new_resolutions
            if "reasoning" in planned:
                for d in workbook.datasets:
                    d.assertions = [a for a in d.assertions if a.origin != "llm"]
                    d.analyst_notes = []
                workbook.component_status = [
                    c for c in workbook.component_status if c.stage != "reasoning"
                ]
                if self.config.llm_enabled:
                    self.orchestrator.reason(workbook)
                executed.append("reasoning")
        changed_nodes = apply_resolutions(workbook, applicable) if applicable else set()
        affected_nodes = downstream(workbook.graph, changed_nodes)
        risk_states = [(f.finding_id, f.status) for d in workbook.datasets for f in d.findings]
        expire_risks(workbook, all_resolutions)
        if risk_states != [(f.finding_id, f.status) for d in workbook.datasets for f in d.findings]:
            changed.append("risk_review")
        if changed or changed_nodes or not self.config.assessment_control.stop_on_no_change:
            self.orchestrator.derive(workbook)
            executed.extend(
                s
                for s in (
                    "semantics",
                    "governance",
                    "mission",
                    "maturity",
                    "recommendations",
                    "contract",
                )
                if s not in executed
            )
        workbook.application_version = __version__
        workbook.fingerprints = {
            **fingerprints,
            "fingerprint_format": FINGERPRINT_FORMAT,
            "dataset_fingerprints": digest([(d.dataset_id, d.profile) for d in workbook.datasets]),
            "schema": digest([d.physical_schema for d in workbook.datasets]),
            "contract": digest([d.proposed_contract for d in workbook.datasets]),
            "affected_dependencies": digest(sorted(affected_nodes)),
        }
        comparison = previous
        baseline_iteration = number - 1
        if compare_baseline:
            if not previous_run:
                raise ValueError("Named baseline comparison requires prior assessment history")
            selected = next((b for b in previous_run.baselines if b.name == compare_baseline), None)
            if selected is None:
                raise ValueError("Named baseline was not found")
            comparison = next(
                (
                    snapshot
                    for snapshot in [previous_run.assessment, *previous_run.snapshots]
                    if snapshot.assessment_id == selected.assessment_id
                    and digest(snapshot) == selected.assessment_hash
                ),
                None,
            )
            if comparison is None:
                raise ValueError("Baseline snapshot is missing or has failed integrity validation")
            baseline_iteration = selected.iteration_number
        delta = compare(comparison, workbook, number) if comparison else None
        if delta and comparison:
            delta.from_iteration = baseline_iteration
            enrich_regressions(comparison, workbook, delta)
            if previous:
                retain_resolved_findings(previous, workbook)
            if (
                changed
                or changed_nodes
                or compare_baseline
                or not self.config.assessment_control.stop_on_no_change
            ):
                self.orchestrator.derive(workbook)
        workbook.fingerprints["contract"] = digest([d.proposed_contract for d in workbook.datasets])
        workbook.graph = build_graph(workbook)
        validate_assessment(workbook, {r.resolution_id for r in all_resolutions})
        decision = decide(workbook)
        outcome = cast(
            Lifecycle,
            ("WAITING_FOR_HUMAN" if decision.decision == "WAIT_FOR_HUMAN" else decision.decision),
        )
        transitions.append(outcome)
        old_evidence = (
            {e.evidence_id for d in previous.datasets for e in d.evidence} if previous else set()
        )
        old_findings = (
            {f.finding_id for d in previous.datasets for f in d.findings} if previous else set()
        )
        iteration = AssessmentIteration(
            iteration_id=stable_id("iteration", workbook.assessment_id, number),
            assessment_id=workbook.assessment_id,
            iteration_number=number,
            trigger=actual_trigger,
            started_at=started,
            completed_at=now(),
            changed_inputs=changed,
            components_executed=list(dict.fromkeys(executed)),
            components_skipped=[s for s in STAGES if s not in executed],
            new_evidence_refs=[
                e.evidence_id
                for d in workbook.datasets
                for e in d.evidence
                if e.evidence_id not in old_evidence
            ],
            new_finding_refs=[
                f.finding_id
                for d in workbook.datasets
                for f in d.findings
                if f.finding_id not in old_findings
            ],
            resolved_finding_refs=delta.findings["resolved"] if delta else [],
            changed_assertion_refs=sorted(
                changed_nodes & {a.assertion_id for d in workbook.datasets for a in d.assertions}
            ),
            maturity_changes=delta.maturity if delta else [],
            mission_fitness_changes=delta.mission_fitness if delta else [],
            unresolved_question_refs=[
                q.question_id
                for d in workbook.datasets
                for q in d.unresolved_questions
                if q.status == "OPEN"
            ],
            outcome=outcome,
            transitions=transitions,
            decision=decision,
        )
        baselines = list(previous_run.baselines) if previous_run else []
        if baseline:
            if any(b.name == baseline for b in baselines):
                raise ValueError("Named baselines are immutable; choose a new name")
            if decision.decision not in {"BASELINE_ESTABLISHED", "REMEDIATION_REQUIRED"}:
                raise ValueError(
                    "Cannot establish a baseline before integrity and authoritative gates pass"
                )
            baselines.append(
                Baseline(
                    name=baseline,
                    assessment_id=workbook.assessment_id,
                    iteration_number=number,
                    fingerprints=workbook.fingerprints,
                    assessment_hash=digest(workbook),
                )
            )
        # One automatic measurement/reasoning pass per event. A subsequent pass needs new
        # input; never spend max_iterations repeatedly asking models for missing authority.
        snapshots = [
            *(previous_run.snapshots if previous_run else []),
            *([previous.model_copy(deep=True)] if previous else []),
        ]
        return AssessmentRun(
            assessment=workbook,
            iterations=[*iterations, iteration],
            resolutions=all_resolutions,
            delta=delta,
            baselines=baselines,
            snapshots=snapshots,
        )
