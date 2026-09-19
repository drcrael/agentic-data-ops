"""Cross-process JSON histories must not invent changes or lose real changes."""

import hashlib
import json
import subprocess
import sys
from datetime import timedelta

import pytest
import yaml

from data_maturity import __version__
from data_maturity.config import Config, ProviderConfig, load_config
from data_maturity.control.controller import FINGERPRINT_FORMAT, AssessmentController
from data_maturity.models.assessment import QualityRule
from data_maturity.models.control import AssessmentRun, Resolution
from data_maturity.util import digest, now

pytestmark = [pytest.mark.integration, pytest.mark.regression]


def reload(run):
    return AssessmentRun.model_validate_json(run.model_dump_json())


def legacy_digest(value):
    """The released v0.1.1 container encoding, retained only as test input."""
    value = json.loads(json.dumps(value, default=str, allow_nan=False))
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def legacy_history(run, config):
    prior = run.model_copy(deep=True)
    prior.assessment.application_version = "0.1.1"
    prior.assessment.fingerprints.pop("fingerprint_format", None)
    prior.assessment.fingerprints.update(
        quality_rules=legacy_digest(config.quality_rules),
        resolutions=legacy_digest(prior.resolutions),
        models=legacy_digest(
            {
                "models": config.models,
                "enabled": config.llm_enabled,
                "context": config.llm_context,
                "security": config.security,
            }
        ),
    )
    for baseline in prior.baselines:
        if baseline.assessment_id == prior.assessment.assessment_id:
            baseline.assessment_hash = digest(prior.assessment)
    return reload(prior)


@pytest.fixture
def baseline(tmp_path):
    source = tmp_path / "parts.csv"
    source.write_text("part_id,value\nP-001,10\nP-002,20\n")
    config = load_config()
    config.quality_rules = [
        QualityRule(rule_id="id", field="part_id", operator="not_null", dimension="completeness")
    ]
    config.models = {"semantic_inference": ProviderConfig()}
    controller = AssessmentController(config)
    initial = controller.run(source)
    risks = [
        Resolution(
            resolution_id=f"risk:{q.question_id}",
            question_id=q.question_id,
            resolution_type="ACCEPTED_RISK",
            value="Synthetic check only",
            provided_by="Owner",
            authoritative=True,
            authority="Fixture owner",
            rationale="Test lifecycle",
            scope="Synthetic fixture",
            review_at=now() + timedelta(days=1),
        )
        for d in initial.assessment.datasets
        for q in d.unresolved_questions
        if q.blocking
    ]
    saved = controller.run(source, prior_assessment=initial, resolutions=risks, baseline="approved")
    return source, config, saved


@pytest.mark.parametrize("legacy", [False, True])
def test_saved_baseline_no_change_and_comparison(baseline, legacy, monkeypatch):
    source, config, saved = baseline
    prior = legacy_history(saved, config) if legacy else reload(saved)
    before = prior.model_dump_json()
    controller = AssessmentController(Config.model_validate(config.model_dump(mode="json")))

    def forbidden(*args, **kwargs):
        raise AssertionError("Unchanged inputs must not execute assessment or derivation")

    monkeypatch.setattr(controller.orchestrator, "assess", forbidden)
    monkeypatch.setattr(controller.orchestrator, "derive", forbidden)
    result = controller.run(source, prior_assessment=prior)
    assert result.iterations[-1].components_executed == []
    assert result.iterations[-1].trigger == "MANUAL_REASSESSMENT"
    assert result.assessment.fingerprints["fingerprint_format"] == FINGERPRINT_FORMAT
    assert result.assessment.application_version == __version__
    assert prior.model_dump_json() == before
    assert result.baselines == prior.baselines
    again = controller.run(source, prior_assessment=reload(result))
    assert again.iterations[-1].components_executed == []
    # Explicit comparison may derive results, but must find the original hashed snapshot.
    compared = AssessmentController(config).run(
        source, prior_assessment=reload(again), compare_baseline="approved"
    )
    assert compared.delta.from_iteration == prior.baselines[0].iteration_number


@pytest.mark.parametrize("change", ["source", "quality_rules", "models", "resolution", "expiry"])
def test_legacy_migration_does_not_hide_changes(baseline, change):
    source, config, saved = baseline
    prior = legacy_history(saved, config)
    resolutions = []
    if change == "source":
        source.write_text("part_id,value\nP-001,10\n,20\n")
    elif change == "quality_rules":
        config.quality_rules.append(
            QualityRule(
                rule_id="unique", field="part_id", operator="unique", dimension="uniqueness"
            )
        )
    elif change == "models":
        config.models["semantic_inference"].model = "changed-model"
    elif change == "resolution":
        q = next(q for q in prior.assessment.datasets[0].unresolved_questions if not q.blocking)
        resolutions = [
            Resolution(
                resolution_id="new",
                question_id=q.question_id,
                value="Definition",
                provided_by="Owner",
                authoritative=True,
                authority="Fixture owner",
            )
        ]
    else:
        prior.resolutions[0].review_at = now() - timedelta(days=1)
    result = AssessmentController(config).run(
        source, prior_assessment=prior, resolutions=resolutions
    )
    assert result.iterations[-1].components_executed
    expected = {
        "source": "SOURCE_DATA_CHANGED",
        "quality_rules": "QUALITY_RULE_CHANGED",
        "models": "MODEL_CONFIGURATION_CHANGED",
        "resolution": "SME_RESPONSE_RECEIVED",
    }
    if change in expected:
        assert result.iterations[-1].trigger == expected[change]
    if change == "expiry":
        assert result.iterations[-1].outcome == "WAITING_FOR_HUMAN"


@pytest.mark.parametrize("legacy", [False, True])
def test_cli_saved_history_across_processes(baseline, legacy, tmp_path):
    source, config, saved = baseline
    prior = legacy_history(saved, config) if legacy else reload(saved)
    history_path = tmp_path / "history.json"
    history_path.write_text(prior.model_dump_json())
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config.model_dump(mode="json")))
    for number in range(2):
        output = tmp_path / f"run-{number}"
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "data_maturity.cli",
                "analyze",
                str(source),
                "--config",
                str(config_path),
                "--prior",
                str(history_path),
                "-o",
                str(output),
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert completed.returncode == 0, completed.stderr
        history_path = output / "assessment_history.json"
        result = AssessmentRun.model_validate_json(history_path.read_text())
        assert result.iterations[-1].trigger == "MANUAL_REASSESSMENT"
        assert result.iterations[-1].components_executed == []
        assert result.baselines == prior.baselines
        assert result.resolutions == prior.resolutions
