"""Manufacturing use-case acceptance, including authoritative feedback and regression."""

from pathlib import Path
from shutil import copyfile

import pytest
import yaml
from openpyxl import load_workbook

from data_maturity.config import load_config
from data_maturity.control.controller import AssessmentController
from data_maturity.evidence.validation import validate_assessment
from data_maturity.models.assessment import MissionContext
from data_maturity.models.control import Resolution

pytestmark = pytest.mark.integration


def context():
    path = Path(__file__).parents[2] / "examples/manufacturing_operations.yaml"
    return MissionContext.model_validate(yaml.safe_load(path.read_text()))


def statuses(run):
    return {r.requirement_id: r.status for r in run.assessment.mission_fitness}


def test_manufacturing_authority_updates_requirement_fitness(fixtures):
    source = fixtures / "ambiguous_manufacturing.xlsx"
    controller = AssessmentController(load_config())
    first = controller.run(source, context())
    assert statuses(first) == {
        "part-identity-completeness": "FIT",
        "coordinate-frame": "UNDETERMINED",
        "coordinate-units": "UNDETERMINED",
    }
    dataset = first.assessment.datasets[0]
    assert dataset.profile.row_count == 10
    assert dataset.structure.worksheet == "Inspections"
    answers = []
    for property_name, value in (
        ("coordinate_unit", "mm"),
        ("coordinate_reference_frame", "fixture-local; origin at datum A; axes per drawing TEST-001"),
    ):
        assertion = next(a for a in dataset.assertions if a.assertion_type == property_name)
        answers.append(
            Resolution(
                resolution_id=f"resolution:{property_name}",
                assertion_id=assertion.assertion_id,
                value=value,
                provided_by="Synthetic inspection owner",
                authoritative=True,
                authority="Fictional inspection specification",
                source_reference="TEST-001",
            )
        )
    second = controller.run(source, prior_assessment=first, resolutions=answers)
    assert all(value == "FIT" for value in statuses(second).values())
    assert statuses(first)["coordinate-units"] == "UNDETERMINED"
    assert "profiling" in second.iterations[-1].components_skipped
    # Passing the three use-case checks does not invent other governance answers.
    assert second.iterations[-1].outcome == "WAITING_FOR_HUMAN"
    fields = second.assessment.datasets[0].target_schema.fields
    assert [f.unit for f in fields][2:5] == ["mm"] * 3
    validate_assessment(second.assessment, {r.resolution_id for r in answers})


def test_manufacturing_missing_part_id_regresses_fitness(fixtures, tmp_path):
    source = tmp_path / "inspection.xlsx"
    copyfile(fixtures / "ambiguous_manufacturing.xlsx", source)
    controller = AssessmentController(load_config())
    first = controller.run(source, context())
    workbook = load_workbook(source)
    workbook["Inspections"]["A2"] = None
    workbook.save(source)
    workbook.close()
    second = controller.run(source, prior_assessment=first)
    assert statuses(second)["part-identity-completeness"] == "NOT_FIT"
    assert second.iterations[-1].trigger == "SOURCE_DATA_CHANGED"
    assert any(change.classification == "REGRESSED" for change in second.delta.mission_fitness)
    validate_assessment(second.assessment)
