"""Cross-reference integrity is a delivery gate, not an optional report warning."""

from __future__ import annotations

from collections.abc import Iterable

from data_maturity.models.assessment import WorkbookAssessment


class IntegrityError(ValueError):
    """Canonical assessment cannot be safely published."""


def validate_assessment(
    workbook: WorkbookAssessment, resolution_ids: set[str] | None = None
) -> None:
    # Re-validate serialized values to catch model_copy(update=...) or in-place mutations.
    WorkbookAssessment.model_validate(workbook.model_dump())
    datasets = {d.dataset_id for d in workbook.datasets}
    fields = {f.field_id for d in workbook.datasets for f in d.physical_schema.fields}
    evidence = {e.evidence_id: e for d in workbook.datasets for e in d.evidence}
    findings = {f.finding_id for d in workbook.datasets for f in d.findings}
    assertions = {
        a.assertion_id for d in workbook.datasets for a in [*d.assertions, *d.analyst_notes]
    }
    questions = {q.question_id for d in workbook.datasets for q in d.unresolved_questions}
    recommendations = {r.recommendation_id for d in workbook.datasets for r in d.recommendations}
    requirements = (
        {r.id for r in workbook.mission_context.data_requirements}
        if workbook.mission_context
        else set()
    )
    rules = {r.rule_id for d in workbook.datasets for r in d.quality.rules}
    keys = {k.key_id for d in workbook.datasets for k in d.keys}
    contracts = {d.proposed_contract.contract_id for d in workbook.datasets if d.proposed_contract}

    def refs(values: Iterable[str], namespace: Iterable[str], kind: str) -> None:
        missing = set(values) - set(namespace)
        if missing:
            raise IntegrityError(f"Dangling {kind} reference(s): {sorted(missing)}")

    def unique(values: list[str], kind: str) -> None:
        if len(values) != len(set(values)):
            raise IntegrityError(f"Duplicate {kind} IDs")

    unique([d.dataset_id for d in workbook.datasets], "dataset")
    unique([f.field_id for d in workbook.datasets for f in d.physical_schema.fields], "field")
    unique([e.evidence_id for d in workbook.datasets for e in d.evidence], "evidence")
    unique([f.finding_id for d in workbook.datasets for f in d.findings], "finding")
    unique(
        [a.assertion_id for d in workbook.datasets for a in [*d.assertions, *d.analyst_notes]],
        "assertion",
    )
    unique([q.question_id for d in workbook.datasets for q in d.unresolved_questions], "question")
    unique(
        [r.recommendation_id for d in workbook.datasets for r in d.recommendations],
        "recommendation",
    )
    if workbook.mission_context:
        unique([r.id for r in workbook.mission_context.data_requirements], "mission requirement")
    for d in workbook.datasets:
        local_fields = {f.field_id for f in d.physical_schema.fields}
        for e in d.evidence:
            refs([e.dataset_id], datasets, "dataset")
            if e.field:
                refs([e.field], local_fields, "evidence field")
        for col in d.profile.columns:
            refs([col.field_id], local_fields, "profile field")
            refs(col.evidence_refs, evidence, "profile evidence")
        refs(d.profile.evidence_refs, evidence, "profile evidence")
        for field in d.physical_schema.fields:
            refs(field.provenance, evidence, "field evidence")
        for a in [*d.assertions, *d.analyst_notes]:
            refs([a.dataset_id], datasets, "assertion dataset")
            refs(a.field_ids, local_fields, "assertion field")
            refs(a.evidence_refs, evidence, "assertion evidence")
            if a.supersedes:
                refs([a.supersedes], assertions, "superseded assertion")
            if a.superseded_by:
                refs([a.superseded_by], assertions, "superseding assertion")
            if a.resolved_by:
                refs([a.resolved_by], resolution_ids or set(), "resolution")
            if (
                a.state == "OBSERVED"
                and a.origin == "human"
                and not any(evidence[r].scope == "human" for r in a.evidence_refs)
            ):
                raise IntegrityError("Human observation has no resolution evidence")
        for f in d.findings:
            refs(f.evidence_refs, evidence, "finding evidence")
            refs(f.field_ids, local_fields, "finding field")
            refs([f.dataset_id], datasets, "finding dataset")
            refs(f.recommendation_refs, recommendations, "recommendation")
            refs(f.mission_requirement_refs, requirements, "mission requirement")
        for q in d.unresolved_questions:
            refs(q.field_ids, local_fields, "question field")
            refs(q.resolves_assertion_refs, assertions, "question assertion")
            refs(q.related_finding_refs, findings, "question finding")
        for r in d.recommendations:
            refs(r.finding_refs, findings, "recommendation finding")
            refs(r.evidence_refs, evidence, "recommendation evidence")
            refs(r.dependencies, recommendations, "recommendation dependency")
            refs(r.mission_requirement_refs, requirements, "mission requirement")
        for rel in d.relationships:
            refs([rel.source_dataset_id, rel.target_dataset_id], datasets, "relationship dataset")
            refs([rel.source_field_id, rel.target_field_id], fields, "relationship field")
            refs(rel.evidence_refs, evidence, "relationship evidence")
        for k in d.keys:
            refs(k.field_ids, local_fields, "key field")
            refs(k.evidence_refs, evidence, "key evidence")
        for m in d.quality.metrics:
            refs(m.evidence_refs, evidence, "metric evidence")
            if m.field_id:
                refs([m.field_id], local_fields, "metric field")
            if m.rule_id:
                refs([m.rule_id], rules, "metric rule")
        for item in d.governance.items:
            refs([item.assertion_id], assertions, "governance assertion")
            refs(item.evidence_refs, evidence, "governance evidence")
        for maturity in d.maturity.dimensions:
            refs(maturity.evidence_refs, evidence, "maturity evidence")
            refs(maturity.blocking_findings, findings, "maturity finding")
        for c in d.ai_readiness.criteria:
            refs(c.evidence_refs, evidence, "readiness evidence")
            refs(c.finding_refs, findings, "readiness finding")
        if d.target_schema:
            refs([f.field_id for f in d.target_schema.fields], local_fields, "target field")
        if d.proposed_contract:
            refs(
                [f.field_id for f in d.proposed_contract.schema_definition.fields],
                local_fields,
                "contract field",
            )
            refs(d.proposed_contract.unresolved_items, assertions, "contract assertion")
            refs(d.proposed_contract.mission_requirement_refs, requirements, "contract requirement")
    for mission in workbook.mission_fitness:
        refs([mission.requirement_id], requirements, "mission requirement")
        refs(mission.dataset_ids, datasets, "mission dataset")
        refs(mission.field_ids, fields, "mission field")
        refs(mission.evidence_refs, evidence, "mission evidence")
        refs(mission.finding_refs, findings, "mission finding")
    all_ids = (
        datasets
        | fields
        | set(evidence)
        | findings
        | assertions
        | questions
        | recommendations
        | requirements
        | rules
        | keys
        | contracts
        | (resolution_ids or set())
    )
    for edge in workbook.graph:
        refs([edge.source_id, edge.target_id], all_ids, "graph node")
