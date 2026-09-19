from datetime import timedelta

import pytest

from data_maturity.config import load_config
from data_maturity.control.controller import AssessmentController
from data_maturity.control.resolutions import expire_risks
from data_maturity.evidence.validation import validate_assessment
from data_maturity.models.assessment import DataRequirement, MissionContext, QualityRule
from data_maturity.models.control import Resolution
from data_maturity.profiling.columns import DatasetProfiler
from data_maturity.util import now

pytestmark = pytest.mark.integration


def test_configured_rules_and_contract_nullability(fixtures):
    cfg = load_config()
    cfg.quality_rules = [
        QualityRule(
            rule_id="required_id",
            field="customer_id",
            dimension="completeness",
            operator="not_null",
        ),
        QualityRule(
            rule_id="approved_states",
            field="state",
            dimension="validity",
            operator="enum",
            parameters={"values": ["CA", "NY"]},
        ),
        QualityRule(
            rule_id="missing",
            field="absent",
            dimension="validity",
            operator="type",
            parameters={"type": "integer"},
        ),
    ]
    run = AssessmentController(cfg).run(fixtures / "dirty_customers.xlsx")
    d = run.assessment.datasets[0]
    results = {m.rule_id: m for m in d.quality.metrics if m.rule_id}
    assert results["required_id"].value == 1
    assert results["approved_states"].value == 2
    assert results["missing"].status == "UNDETERMINED"
    assert d.target_schema.fields[0].nullable is False
    assert any(f.finding_type == "rule_violation_approved_states" for f in d.findings)
    validate_assessment(run.assessment)


def test_rule_only_change_reuses_profiles(fixtures, monkeypatch):
    cfg = load_config()
    source = fixtures / "anomalies.xlsx"
    first = AssessmentController(cfg).run(source)
    cfg.quality_rules = [
        QualityRule(
            rule_id="valid_temperature",
            field="temperature",
            dimension="validity",
            operator="range",
            parameters={"min": -273.15},
        )
    ]

    def fail(*args, **kwargs):
        raise AssertionError("Rule-only change should reuse existing profiles")

    monkeypatch.setattr(DatasetProfiler, "profile", fail)
    second = AssessmentController(cfg).run(source, prior_assessment=first)
    assert "profiling" in second.iterations[-1].components_skipped
    assert second.iterations[-1].trigger == "QUALITY_RULE_CHANGED"
    assert next(m for m in second.assessment.datasets[0].quality.metrics if m.rule_id).value == 1


def test_mission_checks_and_missing_fields(fixtures):
    cfg = load_config()
    cfg.governance_metadata = {
        "*": {"owner": "Fixture owner", "authoritative_source": "Synthetic generator"}
    }
    cfg.quality_rules = [
        QualityRule(
            rule_id="unique_id", field="customer_id", dimension="uniqueness", operator="unique"
        )
    ]
    mission = MissionContext(
        data_requirements=[
            DataRequirement(
                id="unique", description="Unique ID", fields=["customer_id"], check="uniqueness"
            ),
            DataRequirement(
                id="owner", description="Owner identified", check="governance", property="owner"
            ),
            DataRequirement(id="rule", description="Rule holds", check="rule", rule_id="unique_id"),
            DataRequirement(
                id="absent_field",
                description="Required field",
                fields=["missing"],
                check="completeness",
            ),
            DataRequirement(id="unknown", description="Narrative alone is insufficient"),
        ]
    )
    result = AssessmentController(cfg).run(fixtures / "dirty_customers.xlsx", mission)
    statuses = {m.requirement_id: m.status for m in result.assessment.mission_fitness}
    assert statuses == {
        "unique": "NOT_FIT",
        "owner": "FIT",
        "rule": "NOT_FIT",
        "absent_field": "NOT_FIT",
        "unknown": "UNDETERMINED",
    }
    assert result.assessment.datasets[0].proposed_contract.owner == "Fixture owner"
    validate_assessment(result.assessment)


def test_schema_change_preserves_history_and_detects_regression(tmp_path):
    source = tmp_path / "source.csv"
    source.write_text("id,value\n1,10\n2,20\n")
    controller = AssessmentController(load_config())
    first = controller.run(source)
    source.write_text("id,new_field\n1,A\n2,B\n")
    second = controller.run(source, prior_assessment=first)
    assert second.delta.schema_changes[0].classification == "REGRESSED"
    assert any(
        f.finding_type == "schema_regression" for f in second.assessment.datasets[0].findings
    )
    validate_assessment(second.assessment)


def test_expired_risk_reopens_question(fixtures):
    controller = AssessmentController(load_config())
    first = controller.run(fixtures / "clean_customers.xlsx")
    q = next(q for q in first.assessment.datasets[0].unresolved_questions if q.blocking)
    risk = Resolution(
        resolution_id="risk",
        question_id=q.question_id,
        resolution_type="ACCEPTED_RISK",
        value="Accept",
        provided_by="Tester",
        authority="Fixture owner",
        authoritative=True,
        rationale="Test",
        scope="fixture",
        review_at=now() + timedelta(days=1),
    )
    second = controller.run(
        fixtures / "clean_customers.xlsx", prior_assessment=first, resolutions=[risk]
    )
    risk.review_at = now() - timedelta(days=1)
    expire_risks(second.assessment, [risk])
    assert (
        next(
            x
            for x in second.assessment.datasets[0].unresolved_questions
            if x.question_id == q.question_id
        ).status
        == "OPEN"
    )


def test_unknown_maturity_criterion_does_not_pass(fixtures):
    cfg = load_config()
    cfg.maturity_model = {
        "version": "custom",
        "dimensions": {"custom": {"level_1": {"requirements": ["made_up_criterion"]}}},
    }
    run = AssessmentController(cfg).run(fixtures / "clean_customers.xlsx")
    dim = run.assessment.datasets[0].maturity.dimensions[0]
    assert dim.current_level == 0 and dim.missing_criteria == ["made_up_criterion"]


def test_bad_maturity_structure_rejected():
    cfg = load_config()
    with pytest.raises(ValueError, match="contiguous"):
        cfg.maturity_model = {
            "version": "1",
            "dimensions": {"bad": {"level_2": {"requirements": ["typed_fields"]}}},
        }


def test_named_baseline_comparison_and_resolved_findings(tmp_path):
    source = tmp_path / "records.csv"
    source.write_text("id,value\n1,A\n1,A\n2,B\n")
    controller = AssessmentController(load_config())
    first = controller.run(source)
    risks = [
        Resolution(
            resolution_id=f"risk:{q.question_id}",
            question_id=q.question_id,
            resolution_type="ACCEPTED_RISK",
            value="Test",
            provided_by="Tester",
            authority="Fixture owner",
            authoritative=True,
            rationale="Testing baseline",
            scope="fixture",
            review_at=now() + timedelta(days=1),
        )
        for q in first.assessment.datasets[0].unresolved_questions
        if q.blocking
    ]
    baseline = controller.run(
        source, prior_assessment=first, resolutions=risks, baseline="approved"
    )
    unchanged = controller.run(source, prior_assessment=baseline)
    source.write_text("id,value\n1,A\n2,B\n3,C\n")
    improved = controller.run(source, prior_assessment=unchanged, compare_baseline="approved")
    assert improved.delta.from_iteration == 2
    assert improved.delta.to_iteration == 4
    duplicate = next(
        f for f in improved.assessment.datasets[0].findings if f.finding_type == "duplicate_records"
    )
    assert duplicate.status == "RESOLVED"
    validate_assessment(improved.assessment, {r.resolution_id for r in improved.resolutions})


def test_governance_regression_and_contract_rule_regression(tmp_path):
    source = tmp_path / "records.csv"
    source.write_text("id,value\n1,A\n2,B\n")
    cfg = load_config()
    cfg.governance_metadata = {"*": {"owner": "Fixture owner"}}
    cfg.quality_rules = [
        QualityRule(rule_id="required", field="id", dimension="completeness", operator="not_null")
    ]
    first = AssessmentController(cfg).run(source)
    source.write_text("id,value\n1,A\n,B\n")
    cfg.governance_metadata = {}
    second = AssessmentController(cfg).run(source, prior_assessment=first)
    kinds = {f.finding_type for f in second.assessment.datasets[0].findings}
    assert {"governance_regression", "semantic_regression", "contract_rule_regression"} <= kinds
    assert second.delta.governance_changes[0].classification == "REGRESSED"
    validate_assessment(second.assessment)
