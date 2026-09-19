import pytest

from data_maturity.agents.orchestrator import AssessmentOrchestrator
from data_maturity.config import load_config
from data_maturity.evidence.validation import validate_assessment

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "name,count",
    [
        ("clean_customers", 1),
        ("dirty_customers", 1),
        ("semi_structured", 3),
        ("relational", 4),
        ("ambiguous_manufacturing", 1),
        ("anomalies", 1),
        ("prompt_injection", 1),
    ],
)
def test_complete_assessment(fixtures, name, count):
    result = AssessmentOrchestrator(load_config()).assess(fixtures / f"{name}.xlsx")
    assert len(result.datasets) == count
    validate_assessment(result)
    assert all(d.proposed_contract and d.maturity.dimensions for d in result.datasets)
    if name == "ambiguous_manufacturing":
        unresolved = {
            a.assertion_type for a in result.datasets[0].assertions if a.state == "UNRESOLVED"
        }
        assert {"coordinate_unit", "coordinate_reference_frame", "code_definitions"} <= unresolved
        assert all(f.unit is None for f in result.datasets[0].target_schema.fields)
