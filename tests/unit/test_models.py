import pytest
from pydantic import ValidationError

from data_maturity.models.core import SemanticAssertion
from data_maturity.util import unique_names

pytestmark = pytest.mark.unit


def test_names_preserve_collisions():
    names, collisions = unique_names(["Customer ID", "Customer-ID", "customer_id_2", ""])
    assert len(set(names)) == 4
    assert collisions == ["customer_id", "customer_id_2"]


@pytest.mark.parametrize(
    "state,confidence,refs,origin",
    [
        ("OBSERVED", None, [], "deterministic"),
        ("OBSERVED", None, ["e"], "llm"),
        ("INFERRED", None, ["e"], "llm"),
        ("INFERRED", 1.1, ["e"], "llm"),
        ("UNRESOLVED", 0.5, [], "deterministic"),
    ],
)
def test_invalid_knowledge(state, confidence, refs, origin):
    with pytest.raises(ValidationError):
        SemanticAssertion(
            assertion_id="a",
            dataset_id="d",
            assertion_type="unit",
            statement="test",
            state=state,
            confidence=confidence,
            evidence_refs=refs,
            origin=origin,
        )


def test_dependency_scope():
    from data_maturity.control.dependencies import affected_stages

    semantic = affected_stages(["resolutions"])
    assert {"semantics", "contract", "mission_assessment", "maturity_assessment"} <= semantic
    assert "profile_measurement" not in semantic and "ingestion" not in semantic
    assert "profile_measurement" in affected_stages(["source"])
