"""Per-dimension deltas and baseline-linked regression evidence."""

from __future__ import annotations

from typing import Literal

from data_maturity.agents.semantic import metadata_evidence
from data_maturity.models.assessment import WorkbookAssessment
from data_maturity.models.control import AssessmentDelta, Change
from data_maturity.profiling.quality import finding
from data_maturity.util import digest


def compare(
    previous: WorkbookAssessment, current: WorkbookAssessment, iteration: int
) -> AssessmentDelta:
    old_findings = {
        f.finding_id: f
        for d in previous.datasets
        for f in d.findings
        if f.status not in {"RESOLVED", "SUPERSEDED"}
    }
    new_findings = {
        f.finding_id: f
        for d in current.datasets
        for f in d.findings
        if f.status not in {"RESOLVED", "SUPERSEDED"}
    }
    delta = AssessmentDelta(
        from_iteration=iteration - 1,
        to_iteration=iteration,
        findings={
            "new": sorted(new_findings.keys() - old_findings.keys()),
            "resolved": sorted(old_findings.keys() - new_findings.keys()),
            "unchanged": sorted(old_findings.keys() & new_findings.keys()),
            "regressed": [],
        },
    )
    old_datasets = {d.dataset_id: d for d in previous.datasets}
    for d in current.datasets:
        old = old_datasets.get(d.dataset_id)
        if old is None:
            continue
        old_cols = {c.field_id: c for c in old.profile.columns}
        for col in d.profile.columns:
            prior = old_cols.get(col.field_id)
            if not prior:
                continue
            for metric in ("null_percentage", "duplicate_frequency", "mixed_type_rate"):
                before, after = getattr(prior, metric), getattr(col, metric)
                classification: Literal[
                    "IMPROVED", "UNCHANGED", "REGRESSED", "NEW_ISSUE", "CHANGED"
                ] = "REGRESSED" if after > before else "IMPROVED" if after < before else "UNCHANGED"
                if old.profile.sampled or d.profile.sampled:
                    classification = "CHANGED" if after != before else "UNCHANGED"
                delta.quality.append(
                    Change(
                        subject=f"{col.field_id}:{metric}",
                        previous=before,
                        current=after,
                        classification=classification,
                    )
                )
                if classification == "REGRESSED":
                    ev = metadata_evidence(
                        d,
                        "baseline_comparison",
                        {
                            "baseline_assessment": previous.assessment_id,
                            "baseline_source_sha256": previous.source.sha256,
                            "metric": metric,
                            "previous": before,
                            "current": after,
                            "baseline_evidence_refs": prior.evidence_refs,
                        },
                        col.field_id,
                    )
                    # Preserve actual baseline evidence as well as comparison provenance.
                    for ref in prior.evidence_refs:
                        if ref not in {e.evidence_id for e in d.evidence}:
                            d.evidence.append(
                                next(
                                    e.model_copy(deep=True)
                                    for e in old.evidence
                                    if e.evidence_id == ref
                                )
                            )
                    f = finding(
                        d.dataset_id,
                        f"regression_{metric}",
                        "data_quality",
                        [ev.evidence_id, *prior.evidence_refs, *col.evidence_refs],
                        [col.field_id],
                        severity="high",
                    )
                    d.findings = [item for item in d.findings if item.finding_id != f.finding_id]
                    d.findings.append(f)
                    delta.findings["regressed"].append(f.finding_id)
        old_schema = {f.canonical_name: f.physical_type for f in old.physical_schema.fields}
        new_schema = {f.canonical_name: f.physical_type for f in d.physical_schema.fields}
        if old_schema != new_schema:
            regression = any(
                k not in new_schema or new_schema[k] != v for k, v in old_schema.items()
            )
            delta.schema_changes.append(
                Change(
                    subject=d.dataset_id,
                    previous=old_schema,
                    current=new_schema,
                    classification="REGRESSED" if regression else "CHANGED",
                )
            )
            if regression:
                ev = metadata_evidence(
                    d,
                    "schema_baseline_comparison",
                    {
                        "baseline": previous.assessment_id,
                        "previous": old_schema,
                        "current": new_schema,
                    },
                )
                d.findings.append(
                    finding(
                        d.dataset_id,
                        "schema_regression",
                        "schema_definition",
                        [ev.evidence_id],
                        severity="high",
                    )
                )
        for target, old_value, new_value in [
            (
                delta.semantic_changes,
                [
                    (a.assertion_type, a.field_ids, a.state, a.value)
                    for a in old.assertions
                    if not a.superseded_by
                ],
                [
                    (a.assertion_type, a.field_ids, a.state, a.value)
                    for a in d.assertions
                    if not a.superseded_by
                ],
            ),
            (
                delta.governance_changes,
                [(i.property, i.status) for i in old.governance.items],
                [(i.property, i.status) for i in d.governance.items],
            ),
            (delta.contract_changes, old.proposed_contract, d.proposed_contract),
        ]:
            if digest(old_value) != digest(new_value):
                target.append(
                    Change(
                        subject=d.dataset_id, previous=digest(old_value), current=digest(new_value)
                    )
                )
        old_levels = {m.dimension: m.current_level for m in old.maturity.dimensions}
        for m in d.maturity.dimensions:
            before = old_levels.get(m.dimension, 0)
            delta.maturity.append(
                Change(
                    subject=f"{d.dataset_id}:{m.dimension}",
                    previous=before,
                    current=m.current_level,
                    classification="IMPROVED"
                    if m.current_level > before
                    else "REGRESSED"
                    if m.current_level < before
                    else "UNCHANGED",
                )
            )
        if d.ai_readiness.status != old.ai_readiness.status:
            delta.ai_readiness_changes.append(
                Change(
                    subject=d.dataset_id,
                    previous=old.ai_readiness.status,
                    current=d.ai_readiness.status,
                    classification="REGRESSED" if old.ai_readiness.status == "READY" else "CHANGED",
                )
            )
    old_mission = {m.requirement_id: m for m in previous.mission_fitness}
    ranks = {"FIT": 3, "PARTIALLY_FIT": 2, "NOT_FIT": 1, "UNDETERMINED": 0}
    for mission in current.mission_fitness:
        before_mission = old_mission.get(mission.requirement_id)
        if before_mission:
            delta.mission_fitness.append(
                Change(
                    subject=mission.requirement_id,
                    previous=before_mission.status,
                    current=mission.status,
                    classification="REGRESSED"
                    if ranks[mission.status] < ranks[before_mission.status]
                    else "IMPROVED"
                    if ranks[mission.status] > ranks[before_mission.status]
                    else "UNCHANGED",
                )
            )
    return delta
