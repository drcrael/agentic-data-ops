"""Execute ordered assessment stages; lifecycle decisions belong to the controller."""

from __future__ import annotations

import logging
from pathlib import Path

from data_maturity.agents.governance import GovernanceAnalyst
from data_maturity.agents.maturation import MaturationAnalyst
from data_maturity.agents.quality import QualityAnalyst
from data_maturity.agents.semantic import SemanticAnalyst
from data_maturity.config import Config
from data_maturity.contracts.generator import generate_contract
from data_maturity.evidence.graph import build_graph
from data_maturity.evidence.store import EvidenceStore
from data_maturity.ingestion.base import ingest
from data_maturity.llm.gateway import LLMGateway, ReasoningFailure
from data_maturity.maturity.ai_readiness import evaluate_readiness
from data_maturity.maturity.evaluator import evaluate
from data_maturity.mission.evaluator import evaluate_mission
from data_maturity.models.assessment import (
    ComponentStatus,
    DatasetAssessment,
    MissionContext,
    QualityMetric,
    WorkbookAssessment,
)
from data_maturity.models.core import Dataset, DatasetSchema
from data_maturity.profiling.columns import DatasetProfiler
from data_maturity.profiling.keys import discover_keys
from data_maturity.profiling.quality import assess_quality, finding
from data_maturity.profiling.relationships import discover_relationships
from data_maturity.util import stable_id

logger = logging.getLogger(__name__)


class AssessmentOrchestrator:
    def __init__(self, config: Config, gateway: LLMGateway | None = None) -> None:
        self.config = config
        self.gateway = gateway or LLMGateway(config)

    def assess(
        self,
        source: Path,
        mission_context: MissionContext | None = None,
        reuse_measurements: WorkbookAssessment | None = None,
    ) -> WorkbookAssessment:
        self.gateway.preflight()
        logger.info("ingestion_started")
        metadata, datasets = ingest(source, self.config)
        reusable = (
            {d.dataset_id: d for d in reuse_measurements.datasets} if reuse_measurements else {}
        )
        retained_evidence = [
            e.model_copy(deep=True)
            for d in reusable.values()
            for e in d.evidence
            if e.evidence_type in {"column_profile", "record_profile", "composite_uniqueness"}
        ]
        store = EvidenceStore(retained_evidence)
        profiler = DatasetProfiler()
        profiles = {}
        for dataset in datasets:
            prior = reusable.get(dataset.dataset_id)
            if prior:
                if prior.source.sha256 != metadata.sha256:
                    raise ValueError("Cannot reuse measurements across changed source content")
                profiles[dataset.dataset_id] = prior.profile.model_copy(deep=True)
                dataset.fields = [f.model_copy(deep=True) for f in prior.physical_schema.fields]
            else:
                profiles[dataset.dataset_id] = profiler.profile(dataset, self.config, store)
        assessed = []
        for dataset in datasets:
            logger.info("profiling_complete", extra={"dataset_id": dataset.dataset_id})
            profile = profiles[dataset.dataset_id]
            quality, findings = assess_quality(dataset, profile, self.config, store)
            keys = (
                [k.model_copy(deep=True) for k in reusable[dataset.dataset_id].keys]
                if dataset.dataset_id in reusable
                else discover_keys(dataset, profile, self.config, store)
            )
            assessed.append(
                DatasetAssessment(
                    dataset_id=dataset.dataset_id,
                    source=metadata,
                    structure=dataset.structure,
                    physical_schema=DatasetSchema(fields=dataset.fields),
                    profile=profile,
                    quality=quality,
                    keys=keys,
                    findings=findings,
                )
            )
        relationships = discover_relationships(datasets, profiles, self.config, store)
        for d in assessed:
            d.relationships = [r for r in relationships if r.source_dataset_id == d.dataset_id]
            d.evidence = store.for_dataset(d.dataset_id)
            for rel in d.relationships:
                d.quality.metrics.append(
                    QualityMetric(
                        metric_id=stable_id("metric", rel.relationship_id),
                        dimension="integrity",
                        name="candidate_orphan_count",
                        value=rel.orphan_count,
                        denominator=d.profile.row_count,
                        field_id=rel.source_field_id,
                        status="WARNING" if rel.orphan_count else "PASS",
                        evidence_refs=rel.evidence_refs,
                        scope=rel.scope,
                        explanation="Candidate relationship; sample non-overlap does not prove full-source orphans",
                    )
                )
                if rel.orphan_count:
                    d.findings.append(
                        finding(
                            d.dataset_id,
                            f"candidate_orphan_{rel.target_field_id}",
                            "integrity",
                            rel.evidence_refs,
                            [rel.source_field_id],
                            rel.orphan_count,
                            d.profile.row_count,
                            "high",
                            inferred=True,
                        )
                    )
            SemanticAnalyst().deterministic(d)
            GovernanceAnalyst().assess(d, self.config)
        workbook = WorkbookAssessment(
            assessment_id=stable_id(
                "assessment", metadata.sha256, self.config.model_dump(), mission_context
            ),
            source=metadata,
            datasets=assessed,
            mission_context=mission_context,
            configuration=self.config.model_dump(mode="json"),
            component_status=[
                ComponentStatus(
                    component=c,
                    status="CACHED" if reusable and c == "profiling" else "COMPLETE",
                    stage=c,
                )
                for c in ("ingestion", "discovery", "profiling", "quality", "relationships")
            ],
        )
        if self.config.llm_enabled:
            self.reason(workbook, {d.dataset_id: d for d in datasets})
        else:
            workbook.component_status.append(
                ComponentStatus(
                    component="llm",
                    stage="reasoning",
                    status="SKIPPED",
                    reason="Disabled by configuration or --no-llm",
                )
            )
        self.derive(workbook)
        return workbook

    def reason(
        self, workbook: WorkbookAssessment, datasets: dict[str, Dataset] | None = None
    ) -> None:
        for d in workbook.datasets:
            for role in (
                "semantic_inference",
                "quality_reasoning",
                "governance_reasoning",
                "maturation_reasoning",
                "report_generation",
            ):
                if role not in self.config.models:
                    continue
                try:
                    if role == "semantic_inference":
                        d.assertions.extend(
                            SemanticAnalyst().reason(
                                d, self.gateway, (datasets or {}).get(d.dataset_id)
                            )
                        )
                    else:
                        d.analyst_notes.extend(
                            QualityAnalyst().reason(
                                d, self.gateway, (datasets or {}).get(d.dataset_id), role
                            )
                        )
                    workbook.component_status.append(
                        ComponentStatus(
                            component=role,
                            stage="reasoning",
                            dataset_id=d.dataset_id,
                            status="COMPLETE",
                        )
                    )
                except ReasoningFailure as exc:
                    workbook.component_status.append(
                        ComponentStatus(
                            component=role,
                            stage="reasoning",
                            dataset_id=d.dataset_id,
                            status="FAILED",
                            reason=str(exc),
                        )
                    )
        workbook.inference_records = list(self.gateway.records)

    def derive(self, workbook: WorkbookAssessment) -> None:
        # Derived mission findings are rebuilt; historical copies remain in run snapshots.
        for d in workbook.datasets:
            d.findings = [f for f in d.findings if not f.finding_type.startswith("mission_gap_")]
            GovernanceAnalyst().refresh(d)
        workbook.mission_fitness = evaluate_mission(workbook.datasets, workbook.mission_context)
        for d in workbook.datasets:
            d.recommendations = MaturationAnalyst().recommend(d)
            d.proposed_contract = generate_contract(d, workbook.mission_context)
            requirements = [m for m in workbook.mission_fitness if d.dataset_id in m.dataset_ids]
            mission_fit = all(m.status == "FIT" for m in requirements) if requirements else None
            d.ai_readiness = evaluate_readiness(d, mission_fit)
            d.maturity = evaluate(d, self.config.maturity_model)
        workbook.graph = build_graph(workbook)
