from datetime import UTC, datetime, timedelta, timezone

import pytest

from data_maturity.models.control import Resolution
from data_maturity.util import digest, primitive

pytestmark = [pytest.mark.unit, pytest.mark.regression]


@pytest.mark.parametrize("offset", [0, -7, 5.5])
def test_nested_models_hash_identically_after_json_reload(offset):
    resolution = Resolution(
        resolution_id="resolution:unit",
        question_id="question:unit",
        value={"unit": "mm", "tolerance": 0.1},
        provided_by="Synthetic fixture owner",
        timestamp=datetime(2026, 1, 2, tzinfo=timezone(timedelta(hours=offset))),
    )
    reloaded = Resolution.model_validate_json(resolution.model_dump_json())
    assert resolution.model_dump_json() == reloaded.model_dump_json()
    for wrap in (lambda x: x, lambda x: [x], lambda x: (x,), lambda x: {"nested": [x]}):
        assert digest(wrap(resolution)) == digest(wrap(reloaded))
    assert primitive({"nested": [resolution]}) == {"nested": [resolution.model_dump(mode="json")]}
    assert digest([resolution]) != digest([resolution.model_copy(update={"value": "m"})])


def test_mapping_order_is_canonical_and_scalar_types_stay_distinct():
    a = Resolution(
        resolution_id="r",
        question_id="q",
        value={"a": 1, "b": 2},
        provided_by="Owner",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
    )
    b = a.model_copy(update={"value": {"b": 2, "a": 1}})
    assert digest([a]) == digest([b])
    assert len({digest(x) for x in (1, "1", True, None, "None")}) == 5


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_container_values_still_rejected(value):
    with pytest.raises(ValueError):
        digest({"value": [value]})
