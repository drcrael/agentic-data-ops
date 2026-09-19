"""Mission-specific acceptance checks, distinct from general dataset health."""

from __future__ import annotations

from typing import Literal

from data_maturity.agents.semantic import add_gap, metadata_evidence
from data_maturity.models.assessment import (
    DatasetAssessment,
    MissionContext,
    MissionRequirementAssessment,
)
from data_maturity.profiling.quality import finding


def evaluate_mission(
    datasets: list[DatasetAssessment], mission: MissionContext | None
) -> list[MissionRequirementAssessment]:
    if mission is None:
        return []
    results = []
    for req in mission.data_requirements:
        selected = [
            d
            for d in datasets
            if not req.dataset
            or req.dataset in {d.dataset_id, d.structure.table, d.structure.worksheet}
        ]
        evidence_refs: list[str] = []
        fields: list[str] = []
        outcomes: list[bool | None] = []
        for d in selected:
            ev = metadata_evidence(d, "mission_requirement", req.model_dump())
            evidence_refs.append(ev.evidence_id)
            matches = [
                f
                for f in d.physical_schema.fields
                if f.canonical_name in req.fields
                or f.source_name in req.fields
                or f.field_id in req.fields
            ]
            fields.extend(f.field_id for f in matches)
            if req.fields and len(matches) != len(req.fields):
                outcomes.append(False)
                continue
            if req.check in {"completeness", "uniqueness"}:
                if not matches:
                    outcomes.append(None)
                for f in matches:
                    col = next(c for c in d.profile.columns if c.field_id == f.field_id)
                    evidence_refs.extend(col.evidence_refs)
                    if not col.row_count or d.profile.sampled:
                        outcomes.append(None)
                    else:
                        ratio = (
                            1 - col.null_count / col.row_count
                            if req.check == "completeness"
                            else col.uniqueness_ratio
                        )
                        outcomes.append(ratio >= req.threshold)
            elif req.check == "semantic":
                candidates = [
                    a
                    for a in d.assertions
                    if not a.superseded_by
                    and a.assertion_type == req.property
                    and (not matches or set(a.field_ids) & {f.field_id for f in matches})
                ]
                outcomes.append(
                    True if candidates and all(a.state == "OBSERVED" for a in candidates) else None
                )
                evidence_refs.extend(e for a in candidates for e in a.evidence_refs)
            elif req.check == "governance":
                items = [i for i in d.governance.items if i.property == req.property]
                outcomes.append(
                    True if items and all(i.status == "PRESENT" for i in items) else None
                )
                evidence_refs.extend(e for i in items for e in i.evidence_refs)
            elif req.check == "rule":
                metrics = [m for m in d.quality.metrics if m.rule_id == req.rule_id]
                outcomes.append(
                    None
                    if not metrics
                    or any(m.status == "UNDETERMINED" or m.scope == "sample" for m in metrics)
                    else all(m.status == "PASS" for m in metrics)
                )
                evidence_refs.extend(e for m in metrics for e in m.evidence_refs)
            elif req.check == "freshness":
                # Freshness is evaluated by explicit quality freshness rules, never inferred from column names.
                metrics = [
                    m
                    for m in d.quality.metrics
                    if m.rule_id == req.rule_id and m.dimension == "timeliness"
                ]
                outcomes.append(
                    None
                    if not metrics
                    or any(m.status == "UNDETERMINED" or m.scope == "sample" for m in metrics)
                    else all(m.status == "PASS" for m in metrics)
                )
                evidence_refs.extend(e for m in metrics for e in m.evidence_refs)
            else:
                outcomes.append(None)
        status: Literal["FIT", "PARTIALLY_FIT", "NOT_FIT", "UNDETERMINED"] = (
            "UNDETERMINED"
            if not outcomes or any(x is None for x in outcomes)
            else "FIT"
            if all(outcomes)
            else "PARTIALLY_FIT"
            if any(outcomes)
            else "NOT_FIT"
        )
        if not selected:
            status = "NOT_FIT"
            selected_for_gap = datasets[:1]
        else:
            selected_for_gap = selected
        finding_refs = []
        if status != "FIT":
            for d in selected_for_gap:
                ev = metadata_evidence(
                    d, "mission_evaluation", {"requirement": req.model_dump(), "status": status}
                )
                evidence_refs.append(ev.evidence_id)
                gap = finding(
                    d.dataset_id,
                    f"mission_gap_{req.id}",
                    "mission_fitness",
                    [
                        ev.evidence_id,
                        *[e for e in evidence_refs if e in {x.evidence_id for x in d.evidence}],
                    ],
                    [
                        fid
                        for fid in fields
                        if fid in {x.field_id for x in d.physical_schema.fields}
                    ],
                    severity=req.criticality,
                    description=f"Requirement '{req.id}' is {status}; measured scope and explicit acceptance criteria govern this result",
                )
                gap.mission_requirement_refs = [req.id]
                gap.state = "UNRESOLVED" if status == "UNDETERMINED" else "OBSERVED"
                d.findings.append(gap)
                finding_refs.append(gap.finding_id)
                if status == "UNDETERMINED":
                    add_gap(
                        d,
                        f"mission_acceptance_{req.id}",
                        [],
                        f"For mission requirement '{req.id}', provide authoritative field mappings, semantics and measurable acceptance criteria: {req.description}",
                        [ev.evidence_id],
                        blocking=req.criticality in {"critical", "high"},
                    )
        results.append(
            MissionRequirementAssessment(
                requirement_id=req.id,
                status=status,
                reason="Explicit requirement evaluated against measured fields and authoritative knowledge; missing mappings, sampled-only evidence or unresolved authority prevent a positive claim",
                dataset_ids=[d.dataset_id for d in selected],
                field_ids=list(dict.fromkeys(fields)),
                evidence_refs=list(dict.fromkeys(evidence_refs)),
                finding_refs=finding_refs,
            )
        )
    return results
