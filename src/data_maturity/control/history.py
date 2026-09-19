"""Preserve resolved findings and compare semantic/governance control state."""

from __future__ import annotations

from data_maturity.agents.semantic import metadata_evidence
from data_maturity.models.assessment import DatasetAssessment, WorkbookAssessment
from data_maturity.models.control import AssessmentDelta
from data_maturity.profiling.quality import finding


def record_regression(
    dataset: DatasetAssessment,
    previous: WorkbookAssessment,
    kind: str,
    dimension: str,
    before: object,
    after: object,
) -> None:
    baseline = metadata_evidence(
        dataset,
        f"baseline_{kind}",
        {
            "assessment_id": previous.assessment_id,
            "source_sha256": previous.source.sha256,
            "state": before,
        },
    )
    current = metadata_evidence(dataset, f"current_{kind}", {"state": after})
    issue = finding(
        dataset.dataset_id,
        kind,
        dimension,
        [baseline.evidence_id, current.evidence_id],
        severity="high",
        description="Regression against recorded baseline; inspect both baseline and current evidence before remediation",
    )
    dataset.findings = [f for f in dataset.findings if f.finding_id != issue.finding_id]
    dataset.findings.append(issue)


def enrich_regressions(
    previous: WorkbookAssessment, current: WorkbookAssessment, delta: AssessmentDelta
) -> None:
    prior_datasets = {d.dataset_id: d for d in previous.datasets}
    for dataset in current.datasets:
        prior = prior_datasets.get(dataset.dataset_id)
        if not prior:
            continue
        old_semantics = {
            (a.assertion_type, tuple(a.field_ids)): a.state
            for a in prior.assertions
            if not a.superseded_by
        }
        new_semantics = {
            (a.assertion_type, tuple(a.field_ids)): a.state
            for a in dataset.assertions
            if not a.superseded_by
        }
        if any(
            state == "OBSERVED" and new_semantics.get(key) != "OBSERVED"
            for key, state in old_semantics.items()
        ):
            record_regression(
                dataset,
                previous,
                "semantic_regression",
                "semantic_clarity",
                str(old_semantics),
                str(new_semantics),
            )
            for change in delta.semantic_changes:
                if change.subject == dataset.dataset_id:
                    change.classification = "REGRESSED"
        old_governance = {i.property: i.status for i in prior.governance.items}
        new_governance = {i.property: i.status for i in dataset.governance.items}
        if any(
            status == "PRESENT" and new_governance.get(key) != "PRESENT"
            for key, status in old_governance.items()
        ):
            record_regression(
                dataset,
                previous,
                "governance_regression",
                "governance",
                old_governance,
                new_governance,
            )
            for change in delta.governance_changes:
                if change.subject == dataset.dataset_id:
                    change.classification = "REGRESSED"
        old_rules = {m.rule_id: m for m in prior.quality.metrics if m.rule_id}
        violated = [
            m.rule_id
            for m in dataset.quality.metrics
            if m.rule_id in old_rules
            and old_rules[m.rule_id].status == "PASS"
            and m.status == "FAIL"
        ]
        if violated:
            record_regression(
                dataset,
                previous,
                "contract_rule_regression",
                "data_contracts",
                {key: "PASS" for key in violated},
                {key: "FAIL" for key in violated},
            )
        if prior.ai_readiness.status == "READY" and dataset.ai_readiness.status != "READY":
            record_regression(
                dataset,
                previous,
                "ai_readiness_regression",
                "ai_readiness",
                prior.ai_readiness,
                dataset.ai_readiness,
            )
    for change in delta.mission_fitness:
        if change.classification == "REGRESSED":
            mission = next(m for m in current.mission_fitness if m.requirement_id == change.subject)
            for dataset in current.datasets:
                if dataset.dataset_id in mission.dataset_ids:
                    record_regression(
                        dataset,
                        previous,
                        f"mission_regression_{change.subject}",
                        "mission_fitness",
                        change.previous,
                        change.current,
                    )
    missing = prior_datasets.keys() - {d.dataset_id for d in current.datasets}
    if missing and current.datasets:
        record_regression(
            current.datasets[0],
            previous,
            "dataset_removed",
            "structure",
            sorted(missing),
            "Absent from current discovery",
        )


def retain_resolved_findings(previous: WorkbookAssessment, current: WorkbookAssessment) -> None:
    """Keep closed findings in the current inventory when field identities still exist.

    Removed datasets/fields remain fully represented in immutable run snapshots.
    """
    for d in current.datasets:
        prior = next((x for x in previous.datasets if x.dataset_id == d.dataset_id), None)
        if prior is None:
            continue
        ids = {f.finding_id for f in d.findings}
        local_fields = {f.field_id for f in d.physical_schema.fields}
        evidence_lookup = {e.evidence_id: e for x in previous.datasets for e in x.evidence}
        for old in prior.findings:
            if old.finding_id in ids or not set(old.field_ids) <= local_fields:
                continue
            if not all(
                evidence_lookup[ref].dataset_id == d.dataset_id
                and (
                    evidence_lookup[ref].field is None or evidence_lookup[ref].field in local_fields
                )
                for ref in old.evidence_refs
            ):
                continue
            archived = old.model_copy(deep=True)
            archived.status = "RESOLVED" if old.state == "OBSERVED" else "SUPERSEDED"
            archived.recommendation_refs = []
            archived.mission_requirement_refs = []
            d.findings.append(archived)
            for ref in archived.evidence_refs:
                if ref not in {e.evidence_id for e in d.evidence}:
                    d.evidence.append(evidence_lookup[ref].model_copy(deep=True))
