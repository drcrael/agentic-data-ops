"""Bounded candidate discovery: measured uniqueness is not business authority."""

from __future__ import annotations

from itertools import combinations

from data_maturity.config import Config
from data_maturity.evidence.store import EvidenceStore
from data_maturity.models.core import Dataset, DatasetProfile, KeyCandidate
from data_maturity.profiling.statistics import missing, value_key
from data_maturity.util import stable_id


def discover_keys(
    dataset: Dataset, profile: DatasetProfile, config: Config, store: EvidenceStore
) -> list[KeyCandidate]:
    keys = []
    for field, col in zip(dataset.fields, profile.columns, strict=True):
        if col.row_count >= 2 and col.null_count == 0 and col.unique_count == col.row_count:
            identifier = field.canonical_name == "id" or field.canonical_name.endswith("_id")
            keys.append(
                KeyCandidate(
                    key_id=stable_id("key", field.field_id),
                    field_ids=[field.field_id],
                    kind="surrogate"
                    if identifier and col.physical_type == "integer"
                    else "primary"
                    if identifier
                    else "natural",
                    confidence=0.7 if profile.sampled else 0.95 if identifier else 0.75,
                    reasoning="Complete and unique in measured scope; naming suggests identifier"
                    if identifier
                    else "Complete and unique in measured scope; business role unconfirmed",
                    evidence_refs=col.evidence_refs,
                    scope=profile.scope,
                )
            )
    singles = {key.field_ids[0] for key in keys}
    for count, (a, b) in enumerate(combinations(range(len(dataset.fields)), 2)):
        if count >= config.profiling.max_composite_candidates:
            break
        if dataset.fields[a].field_id in singles or dataset.fields[b].field_id in singles:
            continue
        pairs = [(row[a], row[b]) for row in dataset.rows]
        if (
            len(pairs) >= 2
            and not any(missing(x) or missing(y) for x, y in pairs)
            and len({(value_key(x), value_key(y)) for x, y in pairs}) == len(pairs)
        ):
            fields = [dataset.fields[a].field_id, dataset.fields[b].field_id]
            ev = store.add(
                dataset,
                "composite_uniqueness",
                {"field_ids": fields, "rows": len(pairs), "unique": len(pairs)},
            )
            keys.append(
                KeyCandidate(
                    key_id=stable_id("key", fields),
                    field_ids=fields,
                    kind="composite",
                    confidence=0.65 if profile.sampled else 0.9,
                    reasoning="Pair is complete and unique; temporal stability untested",
                    evidence_refs=[ev.evidence_id],
                    scope=profile.scope,
                )
            )
    return keys
