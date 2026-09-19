import json
import os
import subprocess
import sys
import time

import pytest

pytestmark = [pytest.mark.acceptance, pytest.mark.performance]


def test_100k_rows_bounded_memory_and_disclosed_sampling(tmp_path):
    source = tmp_path / "large.csv"
    with source.open("w") as stream:
        stream.write("record_id,value,status\n")
        for i in range(100_000):
            stream.write(f"{i},{i % 997},ACTIVE\n")
    script = """
import json, resource, sys
from pathlib import Path
from data_maturity.config import load_config
from data_maturity.control.controller import AssessmentController
run=AssessmentController(load_config()).run(Path(sys.argv[1]))
d=run.assessment.datasets[0]
print(json.dumps({"source_rows":d.structure.source_row_count,"sample_rows":d.profile.row_count,"sampled":d.profile.sampled,"scope":d.profile.scope,"rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))
"""
    start = time.monotonic()
    result = subprocess.run(
        [sys.executable, "-c", script, str(source)],
        capture_output=True,
        text=True,
        timeout=60,
        env=os.environ.copy(),
        check=True,
    )
    measurement = json.loads(result.stdout)
    assert measurement["source_rows"] == 100_000
    assert measurement["sample_rows"] == 10_000
    assert measurement["sampled"] and measurement["scope"] == "sample"
    # Linux reports KiB, macOS bytes. Windows lacks resource; CI targets Linux.
    if sys.platform == "linux":
        assert measurement["rss_kib"] < 512 * 1024
    assert time.monotonic() - start < 60
