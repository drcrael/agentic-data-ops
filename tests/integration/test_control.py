from datetime import timedelta

import pytest

from data_maturity.config import load_config
from data_maturity.control.controller import AssessmentController
from data_maturity.evidence.validation import validate_assessment
from data_maturity.models.control import Resolution
from data_maturity.util import now

pytestmark = pytest.mark.integration


def unit_answer(run, authoritative=True):
    d = run.assessment.datasets[0]
    assertion = next(
        a for a in d.assertions if a.assertion_type == "coordinate_unit" and not a.superseded_by
    )
    return Resolution(
        resolution_id="resolution:units",
        assertion_id=assertion.assertion_id,
        value="mm",
        provided_by="Test owner",
        authority="Synthetic dataset owner" if authoritative else None,
        authoritative=authoritative,
        source_reference="test-fixture-spec",
    )


def test_selective_resolution_and_history(fixtures, monkeypatch):
    controller = AssessmentController(load_config())
    source = fixtures / "ambiguous_manufacturing.xlsx"
    first = controller.run(source)
    before = first.assessment.model_dump_json()
    from data_maturity.profiling.columns import DatasetProfiler

    def forbidden(*args, **kwargs):
        raise AssertionError("Unchanged data must not be reprofiled")

    monkeypatch.setattr(DatasetProfiler, "profile", forbidden)
    second = controller.run(source, prior_assessment=first, resolutions=[unit_answer(first)])
    assert first.assessment.model_dump_json() == before
    assert second.iterations[-1].trigger == "SME_RESPONSE_RECEIVED"
    assert "profiling" in second.iterations[-1].components_skipped
    units = [
        a for a in second.assessment.datasets[0].assertions if a.assertion_type == "coordinate_unit"
    ]
    assert len(units) == 2
    assert units[0].state == "UNRESOLVED" and units[0].superseded_by == units[1].assertion_id
    assert units[1].state == "OBSERVED" and units[1].resolved_by == "resolution:units"
    assert [f.unit for f in second.assessment.datasets[0].target_schema.fields][2:5] == ["mm"] * 3
    validate_assessment(second.assessment, {"resolution:units"})
    third = controller.run(source, prior_assessment=second)
    assert third.iterations[-1].components_executed == []
    assert len(third.snapshots) == 2


def test_nonauthoritative_answer_does_not_close_gate(fixtures):
    controller = AssessmentController(load_config())
    source = fixtures / "ambiguous_manufacturing.xlsx"
    first = controller.run(source)
    second = controller.run(source, prior_assessment=first, resolutions=[unit_answer(first, False)])
    unit = next(
        a
        for a in second.assessment.datasets[0].assertions
        if a.assertion_type == "coordinate_unit" and not a.superseded_by
    )
    assert unit.state == "INFERRED"
    assert second.iterations[-1].outcome == "WAITING_FOR_HUMAN"
    assert all(f.unit is None for f in second.assessment.datasets[0].target_schema.fields)


def test_changed_source_regression_preserves_baseline_evidence(tmp_path):
    source = tmp_path / "records.csv"
    source.write_text("customer_id,name\n1,A\n2,B\n3,C\n")
    controller = AssessmentController(load_config())
    first = controller.run(source)
    source.write_text("customer_id,name\n1,A\n,B\n,C\n")
    second = controller.run(source, prior_assessment=first)
    assert second.iterations[-1].trigger == "SOURCE_DATA_CHANGED"
    assert any(c.classification == "REGRESSED" for c in second.delta.quality)
    regressions = [
        f
        for f in second.assessment.datasets[0].findings
        if f.finding_type.startswith("regression_")
    ]
    assert regressions
    validate_assessment(second.assessment)
    assert second.snapshots[0].source.sha256 != second.assessment.source.sha256


def test_risk_acceptance_and_immutable_baseline(fixtures):
    controller = AssessmentController(load_config())
    source = fixtures / "clean_customers.xlsx"
    first = controller.run(source)
    resolutions = [
        Resolution(
            resolution_id=f"risk:{q.question_id}",
            question_id=q.question_id,
            resolution_type="ACCEPTED_RISK",
            value="Deferred for sandbox demonstration",
            provided_by="Owner",
            authority="Fixture owner",
            authoritative=True,
            rationale="Synthetic test only",
            scope="fixture assessment",
            review_at=now() + timedelta(days=7),
        )
        for q in first.assessment.datasets[0].unresolved_questions
        if q.blocking
    ]
    second = controller.run(source, prior_assessment=first, resolutions=resolutions, baseline="v1")
    assert second.iterations[-1].outcome in {"BASELINE_ESTABLISHED", "REMEDIATION_REQUIRED"}
    assert second.baselines[0].name == "v1"
    assert any(f.status == "ACCEPTED_RISK" for f in second.assessment.datasets[0].findings)
    with pytest.raises(ValueError, match="immutable"):
        controller.run(source, prior_assessment=second, baseline="v1")


def test_invalid_resolution_rejected(fixtures):
    controller = AssessmentController(load_config())
    source = fixtures / "clean_customers.xlsx"
    first = controller.run(source)
    with pytest.raises(ValueError, match="target not found"):
        controller.run(
            source,
            prior_assessment=first,
            resolutions=[
                Resolution(
                    resolution_id="bad", assertion_id="missing", value="test", provided_by="Tester"
                )
            ],
        )
    with pytest.raises(ValueError, match="authority"):
        Resolution(
            resolution_id="bad",
            assertion_id="a",
            value="x",
            provided_by="Tester",
            authoritative=True,
        )
    with pytest.raises(ValueError, match="before integrity"):
        controller.run(source, prior_assessment=first, baseline="blocked")
