"""Graph-based stage invalidation used by the assessment controller."""

from data_maturity.evidence.graph import downstream
from data_maturity.models.core import EvidenceEdge


def affected_stages(changed_inputs: list[str]) -> set[str]:
    dependencies = {
        "source": ["ingestion"],
        "profiling": ["ingestion"],
        "sampling_seed": ["ingestion"],
        "quality_rules": ["quality"],
        "governance": ["governance_assessment"],
        "models": ["reasoning"],
        "prompts": ["reasoning"],
        "mission": ["mission_assessment"],
        "maturity_model": ["maturity_assessment"],
        "resolutions": ["semantics"],
        "ingestion": ["discovery"],
        "discovery": ["profile_measurement"],
        "profile_measurement": ["quality", "relationships"],
        "quality": ["semantics", "reasoning", "mission_assessment"],
        "relationships": ["semantics"],
        "semantics": ["governance_assessment", "mission_assessment", "contract"],
        "governance_assessment": ["mission_assessment", "contract"],
        "reasoning": ["mission_assessment", "contract"],
        "mission_assessment": ["maturity_assessment", "recommendations"],
        "maturity_assessment": ["recommendations"],
        "recommendations": ["contract"],
    }
    edges = [
        EvidenceEdge(source_id=source, relationship="INFORMS", target_id=target)
        for source, targets in dependencies.items()
        for target in targets
    ]
    return downstream(edges, set(changed_inputs)) - set(changed_inputs)
