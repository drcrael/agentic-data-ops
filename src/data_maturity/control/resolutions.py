"""Apply attributed human knowledge as new versions, preserving old assertions."""

from __future__ import annotations

from data_maturity.models.assessment import WorkbookAssessment
from data_maturity.models.control import Resolution
from data_maturity.models.core import Evidence, SemanticAssertion
from data_maturity.util import now, stable_id


def apply_resolutions(workbook: WorkbookAssessment, resolutions: list[Resolution]) -> set[str]:
    changed: set[str] = set()
    for resolution in resolutions:
        matched = False
        if resolution.resolution_type == "RULE_UPDATE":
            raise ValueError(
                "Rule updates must be supplied through validated configuration and --prior reassessment"
            )
        if resolution.resolution_type == "ACCEPTED_RISK" and (
            resolution.review_at is None or resolution.review_at <= now()
        ):
            raise ValueError("Risk acceptance review date must be in the future and timezone-aware")
        for d in workbook.datasets:
            questions = [
                q for q in d.unresolved_questions if q.question_id == resolution.question_id
            ]
            assertion_ids = {resolution.assertion_id} if resolution.assertion_id else set()
            assertion_ids.update(a for q in questions for a in q.resolves_assertion_refs)
            targets = [a for a in d.assertions if a.assertion_id in assertion_ids]
            target_findings = [f for f in d.findings if f.finding_id == resolution.finding_id]
            if not questions and not targets and not target_findings:
                continue
            matched = True
            evidence = Evidence(
                evidence_id=stable_id("evidence", resolution.resolution_id),
                evidence_type="human_resolution",
                dataset_id=d.dataset_id,
                description="Attributed resolution; observation is of human-provided knowledge, not independent verification",
                value=resolution.model_dump(mode="json"),
                generated_by="human_resolution",
                scope="human",
            )
            if evidence.evidence_id not in {e.evidence_id for e in d.evidence}:
                d.evidence.append(evidence)
            if resolution.resolution_type in {
                "ACCEPTED_RISK",
                "ACKNOWLEDGED",
                "REMEDIATION_PLANNED",
            }:
                for question in questions:
                    target_findings.extend(
                        f for f in d.findings if f.finding_id in question.related_finding_refs
                    )
                    if resolution.resolution_type == "ACCEPTED_RISK":
                        question.status = "ACCEPTED_RISK"
                for f in target_findings:
                    f.status = resolution.resolution_type
                    f.evidence_refs = list(dict.fromkeys([*f.evidence_refs, evidence.evidence_id]))
                    changed.add(f.finding_id)
                continue
            if target_findings and not targets:
                raise ValueError(
                    "A human answer cannot erase deterministic quality violations; remediate data or accept risk"
                )
            for original in targets:
                if original.superseded_by:
                    raise ValueError(
                        "Resolution targets a superseded assertion; answer the current version"
                    )
                if resolution.value is None or resolution.value == "":
                    raise ValueError("An answer must contain a nonempty value")
                aid = stable_id("assertion", original.assertion_id, resolution.resolution_id)
                revised = SemanticAssertion(
                    assertion_id=aid,
                    dataset_id=d.dataset_id,
                    field_ids=original.field_ids,
                    assertion_type=original.assertion_type,
                    statement=f"{'Authoritative' if resolution.authoritative else 'Unconfirmed'} answer supplied by {resolution.provided_by}",
                    value=resolution.value,
                    state="OBSERVED" if resolution.authoritative else "INFERRED",
                    confidence=None if resolution.authoritative else 0.5,
                    evidence_refs=[evidence.evidence_id],
                    reasoning="Attributed human response"
                    if resolution.authoritative
                    else "Non-authoritative response requires owner confirmation",
                    alternatives=[]
                    if resolution.authoritative
                    else ["Owner may provide a different authoritative definition"],
                    requires_sme_confirmation=not resolution.authoritative,
                    supersedes=original.assertion_id,
                    resolved_by=resolution.resolution_id,
                    origin="human",
                )
                original.superseded_by = aid
                d.assertions.append(revised)
                changed.update({original.assertion_id, aid})
                linked = [
                    q
                    for q in d.unresolved_questions
                    if original.assertion_id in q.resolves_assertion_refs
                ]
                for question in linked:
                    question.resolves_assertion_refs = [
                        aid if x == original.assertion_id else x
                        for x in question.resolves_assertion_refs
                    ]
                    question.status = "ANSWERED" if resolution.authoritative else "OPEN"
                    if resolution.authoritative:
                        for f in d.findings:
                            if f.finding_id in question.related_finding_refs:
                                f.status = "RESOLVED"
                                f.evidence_refs = list(
                                    dict.fromkeys([*f.evidence_refs, evidence.evidence_id])
                                )
        if not matched:
            raise ValueError(f"Resolution target not found: {resolution.resolution_id}")
    return changed


def expire_risks(workbook: WorkbookAssessment, resolutions: list[Resolution]) -> None:
    for resolution in resolutions:
        if (
            resolution.resolution_type != "ACCEPTED_RISK"
            or not resolution.review_at
            or resolution.review_at > now()
        ):
            continue
        for d in workbook.datasets:
            for q in d.unresolved_questions:
                if q.question_id == resolution.question_id and q.status == "ACCEPTED_RISK":
                    q.status = "OPEN"
                    for f in d.findings:
                        if f.finding_id in q.related_finding_refs and f.status == "ACCEPTED_RISK":
                            f.status = "OPEN"
            for f in d.findings:
                if f.finding_id == resolution.finding_id and f.status == "ACCEPTED_RISK":
                    f.status = "OPEN"
