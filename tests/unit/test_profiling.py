import pytest

from data_maturity.config import Config
from data_maturity.evidence.store import EvidenceStore
from data_maturity.ingestion.base import ingest
from data_maturity.models.assessment import QualityRule
from data_maturity.profiling.columns import DatasetProfiler
from data_maturity.profiling.keys import discover_keys
from data_maturity.profiling.quality import assess_quality, evaluate_rule
from data_maturity.profiling.relationships import discover_relationships

pytestmark = [pytest.mark.unit, pytest.mark.regression]


def measured(path):
    config = Config()
    _, datasets = ingest(path, config)
    store = EvidenceStore()
    profiles = {d.dataset_id: DatasetProfiler().profile(d, config, store) for d in datasets}
    return config, datasets, store, profiles


def test_dirty_ground_truth(fixtures):
    config, datasets, store, profiles = measured(fixtures / "dirty_customers.xlsx")
    d = datasets[0]
    p = profiles[d.dataset_id]
    assert p.row_count == 6
    assert p.duplicate_record_count == 1
    assert p.columns[0].null_count == 1
    assert p.columns[0].duplicate_count == 1
    assert p.columns[0].physical_type == "mixed"
    assert p.columns[3].whitespace_count == 1
    assert p.columns[3].casing_variation_count == 4
    assert p.columns[4].invalid_date_count == 3
    _, findings = assess_quality(d, p, config, store)
    assert {"missing_identifier", "duplicate_candidate_identifier", "mixed_physical_types"} <= {
        f.finding_type for f in findings
    }


def test_clean_key(fixtures):
    config, datasets, store, profiles = measured(fixtures / "clean_customers.xlsx")
    d = datasets[0]
    keys = discover_keys(d, profiles[d.dataset_id], config, store)
    assert any(k.field_ids == [d.fields[0].field_id] for k in keys)


def test_relationship_orphans(fixtures):
    config, datasets, store, profiles = measured(fixtures / "relational.xlsx")
    relationships = discover_relationships(datasets, profiles, config, store)
    assert len(relationships) == 3
    assert sorted(r.orphan_count for r in relationships) == [1, 1, 1]
    assert all(r.cardinality == "MANY_TO_ONE" for r in relationships)


def test_anomalies_not_errors(fixtures):
    config, datasets, store, profiles = measured(fixtures / "anomalies.xlsx")
    d = datasets[0]
    quality, findings = assess_quality(d, profiles[d.dataset_id], config, store)
    outliers = [f for f in findings if "anomaly" in f.finding_type]
    assert outliers and all(f.state == "INFERRED" for f in outliers)
    rule = QualityRule(
        rule_id="absolute_zero",
        field="temperature",
        dimension="validity",
        operator="range",
        parameters={"min": -273.15},
    )
    count, _ = evaluate_rule(rule, [r[1] for r in d.rows])
    assert count == 1
