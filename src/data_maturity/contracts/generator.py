"""Proposed product schema preserves unknowns and separates candidates from authority."""

from __future__ import annotations

from data_maturity.models.assessment import DataContract, DatasetAssessment, MissionContext
from data_maturity.models.core import DatasetSchema
from data_maturity.util import stable_id


def generate_contract(
    assessment: DatasetAssessment, mission: MissionContext | None
) -> DataContract:
    fields = [f.model_copy(deep=True) for f in assessment.physical_schema.fields]
    active = [a for a in assessment.assertions if not a.superseded_by]
    for field in fields:
        field.status = "proposed"
        relevant = [a for a in active if field.field_id in a.field_ids]
        field.unresolved_properties = sorted(
            {a.assertion_type for a in relevant if a.state == "UNRESOLVED"} | {"nullable"}
        )
        semantics = [
            a for a in relevant if a.assertion_type == "semantic_type" and a.state != "UNRESOLVED"
        ]
        if semantics:
            field.semantic_type = str(semantics[0].value)
            field.constraints["semantic_type_status"] = semantics[0].state
        for a in relevant:
            if a.state == "OBSERVED":
                if a.assertion_type == "definition":
                    field.description = str(a.value)
                elif a.assertion_type == "coordinate_unit":
                    field.unit = str(a.value)
                elif a.assertion_type in {
                    "coordinate_reference_frame",
                    "temporal_semantics",
                    "code_definitions",
                }:
                    field.constraints[a.assertion_type] = a.value
                field.provenance = list(dict.fromkeys([*field.provenance, *a.evidence_refs]))
        field.key_membership = [k.key_id for k in assessment.keys if field.field_id in k.field_ids]
        for rule in assessment.quality.rules:
            if (
                rule.field in {field.field_id, field.canonical_name, field.source_name}
                and rule.operator == "not_null"
            ):
                field.nullable = False
                field.constraints["nullable_origin"] = rule.origin
                if "nullable" in field.unresolved_properties:
                    field.unresolved_properties.remove("nullable")
    schema = DatasetSchema(fields=fields, status="proposed")
    assessment.target_schema = schema
    governance = {i.property: i.value for i in assessment.governance.items if i.status == "PRESENT"}
    return DataContract(
        contract_id=stable_id("contract", assessment.dataset_id),
        dataset_id=assessment.dataset_id,
        name=assessment.structure.worksheet or assessment.structure.table,
        schema_definition=schema,
        owner=governance.get("owner"),
        keys=assessment.keys,
        relationships=assessment.relationships,
        quality_rules=assessment.quality.rules,
        update_expectations=governance.get("update_cadence"),
        provenance={
            "source_file": assessment.source.name,
            "source_sha256": assessment.source.sha256,
            "lineage": governance.get("lineage"),
        },
        governance=assessment.governance,
        mission_requirement_refs=[
            r.id
            for r in mission.data_requirements
            if not r.dataset
            or r.dataset
            in {assessment.dataset_id, assessment.structure.table, assessment.structure.worksheet}
        ]
        if mission
        else [],
        unresolved_items=[a.assertion_id for a in active if a.state == "UNRESOLVED"],
    )
