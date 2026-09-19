"""Cross-dataset overlap, cardinality and candidate orphan measurements."""

from __future__ import annotations

from typing import Literal

from data_maturity.config import Config
from data_maturity.evidence.store import EvidenceStore
from data_maturity.models.core import Dataset, DatasetProfile, Relationship
from data_maturity.profiling.statistics import missing, value_key
from data_maturity.util import stable_id


def discover_relationships(
    datasets: list[Dataset],
    profiles: dict[str, DatasetProfile],
    config: Config,
    store: EvidenceStore,
) -> list[Relationship]:
    relationships: list[Relationship] = []
    tested = 0
    for source in datasets:
        for target in datasets:
            if source.dataset_id == target.dataset_id:
                continue
            for si, sf in enumerate(source.fields):
                for ti, tf in enumerate(target.fields):
                    if sf.canonical_name != tf.canonical_name or not (
                        sf.canonical_name.endswith("_id") or sf.canonical_name == "id"
                    ):
                        continue
                    tested += 1
                    if tested > config.profiling.max_relationship_pairs:
                        return relationships
                    sp, tp = (
                        profiles[source.dataset_id].columns[si],
                        profiles[target.dataset_id].columns[ti],
                    )
                    if (
                        sp.physical_type != tp.physical_type
                        or not sp.unique_count
                        or not tp.unique_count
                    ):
                        continue
                    left = [value_key(row[si]) for row in source.rows if not missing(row[si])]
                    right = [value_key(row[ti]) for row in target.rows if not missing(row[ti])]
                    ls, rs = set(left), set(right)
                    containment = len(ls & rs) / len(ls)
                    if containment < 0.5:
                        continue
                    # Orient toward the stronger unique parent; canonical order for equal candidates.
                    source_unique, target_unique = len(ls) == len(left), len(rs) == len(right)
                    if source_unique and not target_unique:
                        continue
                    if source_unique == target_unique and source.dataset_id > target.dataset_id:
                        continue
                    orphan = sum(v not in rs for v in left)
                    sampled = source.structure.sampled or target.structure.sampled
                    value = {
                        "source_field": sf.field_id,
                        "target_field": tf.field_id,
                        "containment": containment,
                        "orphan_count": orphan,
                        "source_unique": source_unique,
                        "target_unique": target_unique,
                        "source_null_count": sp.null_count,
                        "target_null_count": tp.null_count,
                    }
                    ev = store.add(
                        source,
                        "relationship_overlap",
                        value,
                        sf.field_id,
                        scope="sample" if sampled else "full",
                    )
                    cardinality: Literal[
                        "ONE_TO_ONE", "ONE_TO_MANY", "MANY_TO_ONE", "MANY_TO_MANY"
                    ] = (
                        "ONE_TO_ONE"
                        if source_unique and target_unique
                        else "MANY_TO_ONE"
                        if target_unique
                        else "ONE_TO_MANY"
                        if source_unique
                        else "MANY_TO_MANY"
                    )
                    relationships.append(
                        Relationship(
                            relationship_id=stable_id("relationship", sf.field_id, tf.field_id),
                            source_dataset_id=source.dataset_id,
                            source_field_id=sf.field_id,
                            target_dataset_id=target.dataset_id,
                            target_field_id=tf.field_id,
                            cardinality=cardinality,
                            containment=containment,
                            orphan_count=orphan,
                            null_count=sp.null_count,
                            confidence=min(0.7 if sampled else 0.95, 0.5 + containment * 0.45),
                            reasoning="Matching identifier names, compatible types and measured value overlap; authority unconfirmed",
                            evidence_refs=[ev.evidence_id, *tp.evidence_refs],
                            scope="sample" if sampled else "full",
                        )
                    )
    return relationships
