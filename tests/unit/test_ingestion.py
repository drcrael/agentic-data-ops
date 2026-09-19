import pytest

from data_maturity.config import Config, ProfilingConfig
from data_maturity.ingestion.base import IngestionError, ingest

pytestmark = pytest.mark.unit


def test_semi_structured(fixtures):
    source, datasets = ingest(fixtures / "semi_structured.xlsx", Config())
    assert len(datasets) == 3
    assert [d.structure.source_row_count for d in datasets] == [2, 2, 1]
    assert sum(d.structure.formula_count for d in datasets) == 1
    assert source.inspection["worksheets"][0]["hidden_columns"] == ["E"]
    assert source.inspection["named_ranges"][0]["name"] == "CustomerRange"


@pytest.mark.parametrize("extension", ["csv", "tsv"])
def test_delimited(fixtures, extension):
    _, datasets = ingest(fixtures / f"small.{extension}", Config())
    assert len(datasets[0].rows) == 2
    assert datasets[0].fields[0].canonical_name == "customer_id"


def test_sampling_repeatable(fixtures):
    config = Config(profiling=ProfilingConfig(sample_rows=3))
    _, first = ingest(fixtures / "clean_customers.xlsx", config)
    _, second = ingest(fixtures / "clean_customers.xlsx", config)
    assert first[0].rows == second[0].rows
    assert first[0].structure.sampled
    assert first[0].structure.source_row_count == 10


def test_limits_and_ragged(fixtures, tmp_path):
    with pytest.raises(IngestionError):
        ingest(
            fixtures / "clean_customers.xlsx", Config(profiling=ProfilingConfig(max_file_bytes=1))
        )
    bad = tmp_path / "ragged.csv"
    bad.write_text("a,b\n1,2,3\n")
    with pytest.raises(IngestionError, match="Ragged"):
        ingest(bad, Config())


def test_xlsm_container_without_executing_vba(fixtures, tmp_path):
    import shutil

    target = tmp_path / "sample.xlsm"
    shutil.copyfile(fixtures / "clean_customers.xlsx", target)
    source, datasets = ingest(target, Config())
    assert source.format == "xlsm" and source.inspection["macros_executed"] is False
    assert len(datasets[0].rows) == 10


def test_csv_prefix_limit_disclosed(tmp_path):
    path = tmp_path / "small.csv"
    path.write_text("id,value\n1,a\n2,b\n3,c\n4,d\n")
    _, datasets = ingest(path, Config(profiling=ProfilingConfig(max_rows=2, sample_rows=1)))
    structure = datasets[0].structure
    assert structure.source_row_count == 4 and structure.rows_scanned == 2
    assert structure.truncated and structure.sampled


def test_collision_and_repeated_headers(tmp_path):
    from openpyxl import Workbook

    book = Workbook()
    sheet = book.active
    for row in [["Customer ID", "Customer-ID"], [1, 2], ["Customer ID", "Customer-ID"], [3, 4]]:
        sheet.append(row)
    path = tmp_path / "collisions.xlsx"
    book.save(path)
    book.close()
    _, datasets = ingest(path, Config())
    assert len(datasets) == 2
    assert datasets[0].structure.collisions == ["customer_id"]
    assert [f.canonical_name for f in datasets[0].fields] == ["customer_id", "customer_id_2"]
