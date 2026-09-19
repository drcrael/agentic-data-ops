"""Integrity-checked, atomic output bundles. Reports never calculate facts."""

from __future__ import annotations

import html
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field

from data_maturity.evidence.validation import validate_assessment
from data_maturity.models.control import AssessmentRun
from data_maturity.models.core import Model
from data_maturity.util import digest


class RunManifest(Model):
    application_version: str
    assessment_id: str
    started_at: str
    completed_at: str
    source_file: str
    source_sha256: str
    configuration_hash: str
    quality_rules_version: str
    maturity_model_version: str
    llm_enabled: bool
    models: dict[str, Any]
    prompt_versions: dict[str, str]
    sampling: dict[str, Any]
    security_mode: str
    component_status: list[dict[str, Any]]
    artifact_sha256: dict[str, str] = Field(default_factory=dict)


def safe(value: Any) -> str:
    text = html.escape(str(value)).replace("\n", " ")
    for char in ("\\", "`", "*", "_", "[", "]", "|", "#"):
        text = text.replace(char, "\\" + char)
    return text


def markdown(run: AssessmentRun) -> str:
    w = run.assessment
    lines = [
        "# Data Maturity Assessment",
        "",
        "## Executive Summary",
        "",
        f"Analyzed **{len(w.datasets)} datasets** from {safe(w.source.name)}.",
        f"Control outcome: **{run.iterations[-1].outcome}**.",
        "Findings distinguish OBSERVED measurements, INFERRED interpretations, and UNRESOLVED knowledge. Proposed contracts require owner review.",
        "",
        "## Dataset Inventory",
        "",
    ]
    for d in w.datasets:
        lines.append(
            f"- {safe(d.structure.worksheet or d.structure.table)}: {d.structure.source_row_count} source rows; {d.profile.row_count} measured rows; scope **{d.profile.scope}**; {len(d.physical_schema.fields)} fields."
        )
    for heading, getter in [
        (
            "Structural Assessment",
            lambda d: [
                f"Region {safe(d.structure.cell_range)}, confidence {d.structure.confidence}, method {d.structure.detection_method}.",
                *[safe(x) for x in d.structure.warnings],
            ],
        ),
        (
            "Schema Assessment",
            lambda d: [
                f"{safe(f.source_name)} → {safe(f.canonical_name)} ({f.physical_type}); candidate key membership remains unconfirmed."
                for f in d.physical_schema.fields
            ],
        ),
        (
            "Data Quality",
            lambda d: [
                f"{m.dimension}/{safe(m.name)}: {m.value if m.value is not None else 'UNDETERMINED'} ({m.status}, {m.scope}); evidence {', '.join(m.evidence_refs)}."
                for m in d.quality.metrics
            ],
        ),
        (
            "Semantic Assessment",
            lambda d: [
                f"**{a.state}** {safe(a.statement)}; evidence {', '.join(a.evidence_refs)}."
                for a in d.assertions
                if not a.superseded_by and not a.assertion_type.startswith("governance_")
            ],
        ),
        (
            "Relationships",
            lambda d: [
                f"INFERRED {r.cardinality}; candidate orphans {r.orphan_count}; scope {r.scope}; evidence {', '.join(r.evidence_refs)}."
                for r in d.relationships
            ],
        ),
        (
            "Governance Assessment",
            lambda d: [
                f"{i.property}: {i.status}; evidence {', '.join(i.evidence_refs)}."
                for i in d.governance.items
            ],
        ),
        (
            "AI Readiness",
            lambda d: [
                f"{c.criterion}: {c.status} — {safe(c.reason)}" for c in d.ai_readiness.criteria
            ],
        ),
        (
            "Maturity Assessment",
            lambda d: [
                f"{m.dimension}: Level {m.current_level} ({m.current_level_name}); satisfied: {', '.join(m.satisfied_criteria) or 'none'}; next: {', '.join(m.next_level_requirements) or 'none'}; missing: {', '.join(m.missing_criteria) or 'none'}."
                for m in d.maturity.dimensions
            ],
        ),
        (
            "Critical Findings",
            lambda d: [
                f"{f.finding_id}: [{f.severity}/{f.state}/{f.status}] {safe(f.description)} Evidence: {', '.join(f.evidence_refs)}."
                for f in d.findings
                if f.severity in {"high", "critical"}
            ],
        ),
        (
            "Unresolved Questions",
            lambda d: [
                f"{q.question_id}: {safe(q.question)} ({q.status})"
                for q in d.unresolved_questions
                if q.status != "ANSWERED"
            ],
        ),
        (
            "Recommended Target State",
            lambda d: [
                "Proposed schema and contract are in schema.json and data_contract.yaml. Unknown units, authority and constraints remain explicit."
            ],
        ),
        (
            "Prioritized Remediation Roadmap",
            lambda d: [
                f"{r.priority_score:.1f} [{r.priority}] {safe(r.description)} Finding: {', '.join(r.finding_refs)}; evidence: {', '.join(r.evidence_refs)}."
                for r in d.recommendations
            ],
        ),
    ]:
        lines.extend(["", f"## {heading}", ""])
        for d in w.datasets:
            lines.extend([f"### {safe(d.structure.worksheet or d.structure.table)}", ""])
            lines.extend(f"- {line}" for line in getter(d))
    if w.mission_context:
        lines.extend(["", "## Mission Fitness", ""])
        lines.extend(
            f"- {safe(m.requirement_id)}: {m.status}. {safe(m.reason)} Evidence: {', '.join(m.evidence_refs)}."
            for m in w.mission_fitness
        )
    if any(s.status == "FAILED" for s in w.component_status):
        lines.extend(["", "## Component Failures", ""])
        lines.extend(
            f"- {s.component}: {safe(s.reason)}" for s in w.component_status if s.status == "FAILED"
        )
    return "\n".join(lines) + "\n"


def write_reports(run: AssessmentRun, output: Path) -> Path:
    validate_assessment(run.assessment, {r.resolution_id for r in run.resolutions})
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise FileExistsError(
            "Output directory must be new or empty; use a separate directory per iteration"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    assessment = run.assessment
    artifacts: dict[str, Any] = {
        "assessment.json": assessment,
        "schema.json": {
            d.dataset_id: {"observed": d.physical_schema, "proposed": d.target_schema}
            for d in assessment.datasets
        },
        "quality_report.json": {d.dataset_id: d.quality for d in assessment.datasets},
        "evidence.json": [e for d in assessment.datasets for e in d.evidence],
        "evidence_graph.json": assessment.graph,
        "assessment_history.json": run,
    }
    if assessment.mission_context:
        artifacts["mission_fitness.json"] = assessment.mission_fitness
    if run.delta:
        artifacts["assessment_delta.json"] = run.delta

    # json roundtrip uses model serializers for nested Pydantic values.
    def encoded(value: Any) -> str:
        return (
            json.dumps(
                value,
                default=lambda obj: (
                    obj.model_dump(mode="json") if isinstance(obj, Model) else str(obj)
                ),
                indent=2,
                allow_nan=False,
            )
            + "\n"
        )

    with tempfile.TemporaryDirectory(prefix=".data-maturity-", dir=output.parent) as tmp:
        staging = Path(tmp) / "bundle"
        staging.mkdir(mode=0o700)
        for name, value in artifacts.items():
            (staging / name).write_text(encoded(value), encoding="utf-8")
        contracts = {
            "format": "data-maturity-proposed-contract/v1",
            "contracts": [
                d.proposed_contract.model_dump(mode="json")
                for d in assessment.datasets
                if d.proposed_contract
            ],
        }
        (staging / "data_contract.yaml").write_text(
            yaml.safe_dump(contracts, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )
        questions = [
            "# SME Questions",
            "",
            "Answer using question IDs; include provided_by, authority and source_reference.",
            "",
        ]
        for d in assessment.datasets:
            for q in d.unresolved_questions:
                questions.extend(
                    [
                        f"## {q.question_id}",
                        "",
                        f"**{q.priority}/{q.status}** — {safe(q.question)}",
                        f"Rationale: {safe(q.rationale)}",
                        f"Assertion references: {', '.join(q.resolves_assertion_refs)}",
                        "",
                    ]
                )
        (staging / "sme_questions.md").write_text("\n".join(questions), encoding="utf-8")
        (staging / "maturity_report.md").write_text(markdown(run), encoding="utf-8")
        manifest = RunManifest(
            application_version=assessment.application_version,
            assessment_id=assessment.assessment_id,
            started_at=run.iterations[-1].started_at.isoformat(),
            completed_at=str(run.iterations[-1].completed_at),
            source_file=assessment.source.name,
            source_sha256=assessment.source.sha256,
            configuration_hash=digest(assessment.configuration),
            quality_rules_version=str(assessment.configuration.get("quality_rules_version", "1")),
            maturity_model_version=assessment.datasets[0].maturity.model_version,
            llm_enabled=bool(assessment.configuration.get("llm_enabled")),
            models=assessment.configuration.get("models", {}),
            prompt_versions={r.role: r.prompt_version for r in assessment.inference_records},
            sampling={
                d.dataset_id: {
                    "scope": d.profile.scope,
                    "seed": d.structure.seed,
                    "method": d.structure.sampling_method,
                    "source_rows": d.structure.source_row_count,
                    "measured_rows": d.profile.row_count,
                    "truncated": d.structure.truncated,
                }
                for d in assessment.datasets
            },
            security_mode=assessment.configuration.get("security", {}).get("mode", "local_only"),
            component_status=[s.model_dump(mode="json") for s in assessment.component_status],
        )
        from data_maturity.util import file_hash

        manifest.artifact_sha256 = {p.name: file_hash(p) for p in staging.iterdir()}
        (staging / "run_manifest.json").write_text(
            manifest.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        for p in staging.iterdir():
            p.chmod(0o600)
        if output.exists():
            output.rmdir()  # Only an empty directory is eligible.
        os.replace(staging, output)
    return output
