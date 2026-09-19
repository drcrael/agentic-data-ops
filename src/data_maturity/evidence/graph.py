"""Typed relationship export and dependency traversal, without a graph service."""

from __future__ import annotations

from collections import defaultdict, deque

from data_maturity.models.assessment import WorkbookAssessment
from data_maturity.models.core import EvidenceEdge


def build_graph(workbook: WorkbookAssessment) -> list[EvidenceEdge]:
    triples: set[tuple[str, str, str]] = set()

    def add(source: str, relation: str, target: str) -> None:
        triples.add((source, relation, target))

    for d in workbook.datasets:
        for field in d.physical_schema.fields:
            add(d.dataset_id, "HAS_FIELD", field.field_id)
        for assertion in [*d.assertions, *d.analyst_notes]:
            for ref in assertion.evidence_refs:
                add(assertion.assertion_id, "SUPPORTED_BY", ref)
                add(ref, "INFORMS", assertion.assertion_id)
            for fid in assertion.field_ids:
                add(fid, "HAS_ASSERTION", assertion.assertion_id)
            if assertion.supersedes:
                add(assertion.assertion_id, "SUPERSEDES", assertion.supersedes)
            if assertion.superseded_by:
                add(assertion.assertion_id, "SUPERSEDED_BY", assertion.superseded_by)
            if assertion.resolved_by:
                add(assertion.assertion_id, "RESOLVED_BY", assertion.resolved_by)
            if d.proposed_contract:
                add(assertion.assertion_id, "INFORMS", d.proposed_contract.contract_id)
        for f in d.findings:
            for fid in f.field_ids or [d.dataset_id]:
                add(fid, "HAS_FINDING", f.finding_id)
            for ref in f.evidence_refs:
                add(f.finding_id, "SUPPORTED_BY", ref)
            for ref in f.recommendation_refs:
                add(f.finding_id, "LEADS_TO", ref)
        for question in d.unresolved_questions:
            for ref in question.resolves_assertion_refs:
                add(question.question_id, "RESOLVES", ref)
        for rule in d.quality.rules:
            for field in d.physical_schema.fields:
                if rule.field in {field.field_id, field.canonical_name, field.source_name}:
                    add(field.field_id, "HAS_RULE", rule.rule_id)
        for rel in d.relationships:
            add(rel.source_field_id, "CANDIDATE_REFERENCE", rel.target_field_id)
        for recommendation in d.recommendations:
            for ref in recommendation.mission_requirement_refs:
                add(ref, "REQUIRES_ACTION", recommendation.recommendation_id)
        for key in d.keys:
            for fid in key.field_ids:
                add(fid, "IN_CANDIDATE_KEY", key.key_id)
    for req in workbook.mission_fitness:
        for fid in req.field_ids:
            add(req.requirement_id, "REQUIRES", fid)
        for ref in req.evidence_refs:
            add(ref, "INFORMS", req.requirement_id)
        for ref in req.finding_refs:
            add(req.requirement_id, "HAS_GAP", ref)
    return [EvidenceEdge(source_id=s, relationship=r, target_id=t) for s, r, t in sorted(triples)]


def downstream(edges: list[EvidenceEdge], changed: set[str]) -> set[str]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        if edge.relationship in {"INFORMS", "LEADS_TO", "REQUIRES_ACTION", "RESOLVES", "HAS_GAP"}:
            adjacency[edge.source_id].add(edge.target_id)
    seen = set(changed)
    queue = deque(changed)
    while queue:
        for target in adjacency[queue.popleft()] - seen:
            seen.add(target)
            queue.append(target)
    return seen
