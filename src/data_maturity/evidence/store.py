"""Content-addressed evidence with bounded values and source provenance."""

from __future__ import annotations

from typing import Any, Literal

from data_maturity.models.core import Dataset, Evidence, SourceLocation
from data_maturity.util import primitive, stable_id


class EvidenceStore:
    def __init__(self, initial: list[Evidence] | None = None) -> None:
        self.items: dict[str, Evidence] = {e.evidence_id: e for e in initial or []}

    def add(
        self,
        dataset: Dataset,
        kind: str,
        value: Any,
        field: str | None = None,
        description: str = "",
        scope: Literal["full", "sample", "metadata", "human"] | None = None,
    ) -> Evidence:
        scope = scope or ("sample" if dataset.structure.sampled else "full")
        safe_value = primitive(value)
        identifier = stable_id(
            "evidence", dataset.dataset_id, dataset.source.sha256, kind, field, safe_value, scope
        )
        evidence = Evidence(
            evidence_id=identifier,
            evidence_type=kind,
            dataset_id=dataset.dataset_id,
            field=field,
            description=description or kind.replace("_", " "),
            value=safe_value,
            source_location=SourceLocation(
                workbook=dataset.source.name,
                worksheet=dataset.structure.worksheet,
                table=dataset.structure.table,
                column=field,
                cell_range=dataset.structure.cell_range,
                calculation=kind,
            ),
            generated_by="deterministic/0.1.1",
            scope=scope,
        )
        self.items.setdefault(identifier, evidence)
        return self.items[identifier]

    def for_dataset(self, dataset_id: str) -> list[Evidence]:
        return [e for e in self.items.values() if e.dataset_id == dataset_id]
