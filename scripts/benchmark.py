"""Run a repeatable synthetic CSV benchmark on Unix, with no model services."""

from __future__ import annotations

import json
import platform
import resource
import tempfile
import time
from pathlib import Path

from data_maturity.config import load_config
from data_maturity.control.controller import AssessmentController


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="data-maturity-benchmark-") as directory:
        source = Path(directory) / "large.csv"
        with source.open("w", encoding="utf-8") as stream:
            stream.write("record_id,value,status\n")
            for i in range(100_000):
                stream.write(f"{i},{i % 997},ACTIVE\n")
        started = time.monotonic()
        run = AssessmentController(load_config()).run(source)
        elapsed = time.monotonic() - started
        dataset = run.assessment.datasets[0]
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if platform.system() == "Darwin":
            rss /= 1024
        print(
            json.dumps(
                {
                    "python": platform.python_version(),
                    "platform": platform.system(),
                    "source_rows": dataset.structure.source_row_count,
                    "measured_rows": dataset.profile.row_count,
                    "scope": dataset.profile.scope,
                    "elapsed_seconds": round(elapsed, 3),
                    "peak_rss_mib": round(rss / 1024, 2),
                    "outcome": run.iterations[-1].outcome,
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
