from datetime import UTC, datetime, timedelta

import pytest

from data_maturity.config import Config, ProfilingConfig, load_config
from data_maturity.models.assessment import QualityRule
from data_maturity.profiling.columns import column_profile
from data_maturity.profiling.quality import evaluate_rule
from data_maturity.profiling.statistics import parse_date, physical_type

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "operator,parameters,values,expected",
    [
        ("not_null", {}, [1, None, " ", 2], 2),
        ("unique", {}, [1, 1, "1", None], 1),
        ("range", {"min": 0, "max": 10}, [-1, 5, 11, "bad", None], 3),
        ("enum", {"values": ["A", "I"]}, ["A", "I", "U", "a", None], 2),
        ("pattern", {"pattern": "[A-Z]{2}"}, ["CA", "ny", "USA", None], 2),
        ("type", {"type": "integer"}, [1, "1", 2.5, None], 2),
    ],
)
def test_rule_counts(operator, parameters, values, expected):
    rule = QualityRule(
        rule_id="test", field="x", dimension="validity", operator=operator, parameters=parameters
    )
    assert evaluate_rule(rule, values)[0] == expected


@pytest.mark.parametrize("operator", ["range", "enum", "pattern", "type", "freshness"])
def test_missing_rule_parameters_fail(operator):
    rule = QualityRule(rule_id="bad", field="x", dimension="validity", operator=operator)
    with pytest.raises(ValueError):
        evaluate_rule(rule, [1])


def test_freshness_requires_timezone():
    rule = QualityRule(
        rule_id="fresh",
        field="epoch",
        dimension="timeliness",
        operator="freshness",
        parameters={"max_age_days": 2},
    )
    assert evaluate_rule(rule, ["2025-01-01"])[0] is None
    assert evaluate_rule(rule, [datetime.now(UTC) - timedelta(days=5)])[0] == 1


def test_physical_types_and_date_ambiguity():
    assert physical_type(True) == "boolean"
    assert physical_type("001", lexical=True) == "string"
    assert physical_type("3", lexical=True) == "integer"
    assert physical_type("3.5", lexical=True) == "float"
    assert physical_type("false", lexical=True) == "boolean"
    assert parse_date("01/02/2025")[0] is None
    assert parse_date("2025/01/02")[0].isoformat() == "2025-01-02"
    assert parse_date("2025-99-01")[0] is None


def test_numeric_statistics_and_sensitive_summaries():
    cfg = Config(profiling=ProfilingConfig(include_value_summaries=True))
    p = column_profile([1, 2, 3, 4, None], "f", "value", cfg, False)
    assert p.mean == 2.5 and p.median == 2.5 and p.quantiles["q25"] == 1.75
    assert p.null_percentage == 20
    assert p.common_values[0] == {"value": 1, "count": 1}
    empty = column_profile([None, ""], "f", "value", load_config(), False)
    assert empty.physical_type == "unknown" and empty.null_percentage == 100
    default = column_profile(["secret"], "f", "name", load_config(), False)
    assert default.common_values == [] and default.likely_enum == []
