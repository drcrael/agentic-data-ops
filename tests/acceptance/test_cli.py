import json
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from data_maturity.cli import app
from data_maturity.models.assessment import DataContract, WorkbookAssessment
from data_maturity.models.control import AssessmentRun
from data_maturity.reporting.writer import RunManifest

pytestmark = pytest.mark.acceptance
runner = CliRunner()
ROOT = Path(__file__).parents[2]


@pytest.mark.parametrize(
    "fixture",
    [
        "clean_customers",
        "dirty_customers",
        "semi_structured",
        "relational",
        "ambiguous_manufacturing",
        "anomalies",
        "prompt_injection",
    ],
)
def test_required_outputs(fixtures, tmp_path, fixture):
    output = tmp_path / fixture
    result = runner.invoke(
        app, ["analyze", str(fixtures / f"{fixture}.xlsx"), "--no-llm", "--output", str(output)]
    )
    assert result.exit_code == 0, result.output
    expected = {
        "assessment.json",
        "schema.json",
        "quality_report.json",
        "evidence.json",
        "evidence_graph.json",
        "data_contract.yaml",
        "sme_questions.md",
        "maturity_report.md",
        "run_manifest.json",
        "assessment_history.json",
    }
    assert expected <= {p.name for p in output.iterdir()}
    assessment = WorkbookAssessment.model_validate_json((output / "assessment.json").read_text())
    history = AssessmentRun.model_validate_json((output / "assessment_history.json").read_text())
    manifest = RunManifest.model_validate_json((output / "run_manifest.json").read_text())
    assert manifest.assessment_id == history.assessment.assessment_id == assessment.assessment_id
    assert manifest.llm_enabled is False
    for contract in yaml.safe_load((output / "data_contract.yaml").read_text())["contracts"]:
        assert DataContract.model_validate(contract).status == "proposed"
    if fixture == "dirty_customers":
        assert assessment.datasets[0].profile.duplicate_record_count == 1
        assert "OBSERVED" in (output / "maturity_report.md").read_text()
    repeat = runner.invoke(
        app, ["analyze", str(fixtures / f"{fixture}.xlsx"), "--no-llm", "-o", str(output)]
    )
    assert repeat.exit_code == 2
    assert "new or empty" in repeat.output


def test_inspect_profile_help(fixtures, tmp_path):
    assert runner.invoke(app, ["--help"]).exit_code == 0
    result = runner.invoke(app, ["inspect", str(fixtures / "semi_structured.xlsx")])
    assert result.exit_code == 0
    assert len(json.loads(result.stdout)["datasets"]) == 3
    result = runner.invoke(app, ["profile", str(fixtures / "dirty_customers.xlsx")])
    assert result.exit_code == 0
    assert next(iter(json.loads(result.stdout)["profiles"].values()))["duplicate_record_count"] == 1
    output = tmp_path / "profile"
    result = runner.invoke(app, ["profile", str(fixtures / "small.tsv"), "-o", str(output)])
    assert result.exit_code == 0 and (output / "profile.json").is_file()


def test_mock_and_mission(fixtures, tmp_path):
    output = tmp_path / "mission"
    result = runner.invoke(
        app,
        [
            "analyze",
            str(fixtures / "ambiguous_manufacturing.xlsx"),
            "--config",
            str(ROOT / "configs/test_mock_llm.yaml"),
            "--mission",
            str(ROOT / "examples/manufacturing_operations.yaml"),
            "-o",
            str(output),
        ],
    )
    assert result.exit_code == 0, result.output
    assessment = WorkbookAssessment.model_validate_json((output / "assessment.json").read_text())
    statuses = {m.requirement_id: m.status for m in assessment.mission_fitness}
    assert statuses == {
        "part-identity-completeness": "FIT",
        "coordinate-frame": "UNDETERMINED",
        "coordinate-units": "UNDETERMINED",
    }
    assert len(assessment.inference_records) == 5


def test_resolve_cli(fixtures, tmp_path):
    original, revised = tmp_path / "original", tmp_path / "revised"
    source = fixtures / "ambiguous_manufacturing.xlsx"
    assert runner.invoke(app, ["analyze", str(source), "-o", str(original)]).exit_code == 0
    assessment = WorkbookAssessment.model_validate_json((original / "assessment.json").read_text())
    question = next(q for q in assessment.datasets[0].unresolved_questions if "units" in q.question)
    answers = tmp_path / "answers.yaml"
    answers.write_text(
        yaml.safe_dump(
            {
                "answers": {
                    question.question_id: {
                        "answer": "mm",
                        "answered_by": "Fixture owner",
                        "authoritative": True,
                        "authority": "Synthetic source specification",
                    }
                }
            }
        )
    )
    result = runner.invoke(
        app,
        [
            "resolve",
            str(original / "assessment.json"),
            str(answers),
            "--source",
            str(source),
            "-o",
            str(revised),
        ],
    )
    assert result.exit_code == 0, result.output
    history = AssessmentRun.model_validate_json((revised / "assessment_history.json").read_text())
    assert len(history.iterations) == 2
    assert "profiling" in history.iterations[-1].components_skipped
    assert history.resolutions[0].value == "mm"


def test_config_invalid_and_fatal_policy(fixtures, tmp_path):
    config = tmp_path / "bad.yaml"
    config.write_text("unknown_setting: true\n")
    result = runner.invoke(
        app,
        [
            "analyze",
            str(fixtures / "small.csv"),
            "--config",
            str(config),
            "-o",
            str(tmp_path / "out"),
        ],
    )
    assert result.exit_code == 2
    config.write_text(
        "llm_enabled: true\nmodels:\n  semantic_inference:\n    provider: ollama\n    model: test\n    base_url: https://example.com\n"
    )
    result = runner.invoke(
        app,
        [
            "analyze",
            str(fixtures / "small.csv"),
            "--config",
            str(config),
            "-o",
            str(tmp_path / "out"),
        ],
    )
    assert result.exit_code == 2 and "local_only" in result.output
    assert not (tmp_path / "out").exists()
    result = runner.invoke(
        app,
        [
            "analyze",
            str(fixtures / "small.csv"),
            "--config",
            str(config),
            "--no-llm",
            "-o",
            str(tmp_path / "out"),
        ],
    )
    assert result.exit_code == 0
