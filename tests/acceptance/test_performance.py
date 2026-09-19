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
import json, sys
from pathlib import Path
from data_maturity.config import load_config
from data_maturity.control.controller import AssessmentController
run=AssessmentController(load_config()).run(Path(sys.argv[1]))
d=run.assessment.datasets[0]
if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in (
                "PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
                "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage",
                "PagefileUsage", "PeakPagefileUsage")]
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    peak_bytes = counters.PeakWorkingSetSize
else:
    import resource
    peak_bytes = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform != "darwin":
        peak_bytes *= 1024
print(json.dumps({"source_rows":d.structure.source_row_count,"sample_rows":d.profile.row_count,"sampled":d.profile.sampled,"scope":d.profile.scope,"peak_rss_bytes":peak_bytes}))
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
    assert 0 < measurement["peak_rss_bytes"] < 512 * 1024 * 1024
    assert time.monotonic() - start < 60
