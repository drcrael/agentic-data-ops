# Executed validation

Release: v0.1.3. Validation date: 2026-09-19. Environment: Linux, CPython 3.14.7. These are observed execution results, not expected targets.

## Installation and static gates

- Created a new virtual environment and successfully installed `pip install -e ".[dev]"`.
- `data-maturity --help` succeeded with inspect, profile, analyze and resolve commands.
- `ruff check .`: all checks passed.
- `mypy src`: no issues in 55 source files.
- Built the source distribution and wheel with `python -m build`.
- Dependency versions captured in `requirements-dev.lock`.

## Automated tests

- **111 passed, 0 failed**.
- **95.52% total line coverage** (2,500 executable statements; 112 not executed).
- Security-only invocation: **19 passed, 92 deselected**.
- Test markers: unit, integration, acceptance, security, regression, performance.
- External network connections are blocked in the test process. Models use deterministic mocks/controlled HTTP transports.

Sixteen fingerprint/history regression cases cover nested models, timezone round trips, mapping order, scalar type distinctions, non-finite rejection, persistent CLI processes, legacy baselines, real input changes and risk expiry.

Two manufacturing-specific integration tests verify that authoritative units/frame answers improve the mapped requirements while other human gates remain open, and that a missing part ID causes mission-fitness regression.

The suite verifies exact fixture measurements, table boundaries, key candidates, three known relationships with one orphan each, uncertainty preservation, references, source hashing, sampling, provider routing, remote-policy denial before invocation, actual payload minimization, prompt injection, bounded malformed/fabricated response retries, regex timeouts, human resolutions, unchanged-source profile reuse, finding history, risk expiry and immutable named baselines.

## Executed end-to-end commands

All **14 demonstration commands** exited successfully:

1. Generate the documented fixtures.
2. Display CLI help.
3. Inspect the semi-structured workbook.
4. Profile the dirty workbook.
5. Analyze the clean workbook without an LLM.
6. Analyze the dirty workbook without an LLM.
7. Analyze the semi-structured workbook without an LLM.
8. Analyze the relational workbook without an LLM.
9. Analyze the anomaly workbook without an LLM.
10. Analyze the prompt-injection workbook without an LLM.
11. Analyze ambiguous manufacturing data with Mock LLM configuration and explicit mission context.
12. Analyze anomalies using an explicit user-defined absolute-zero quality rule.
13. Run the security test marker separately.
14. Run the single-command demo script.

Outputs correctly report WAITING_FOR_HUMAN for unresolved authoritative knowledge. This is a successful, useful assessment result, not an execution failure.

Generated, sanitized report artifacts from the dirty fixture are retained in `examples/output/`. They include actual calculated measurements and the complete output contract. Source files contain synthetic data only; the spreadsheet generator is the ground truth.

## Performance sanity check

`scripts/benchmark.py` measured:

- Source: 100,000 CSV rows.
- Retained/assessed: 10,000 rows.
- Scope: explicitly `sample`.
- Elapsed assessment time: **0.336 seconds**.
- Peak process RSS: **103.0 MiB**.

The raw measurement is in `docs/benchmark.json`. Hardware and dependency versions affect performance; these measurements are not a production SLA.

## Verification limits

The follow-up [runtime audit](docs/runtime-audit-v0.1.2.md) verified the published
v0.1.2 wheel and source package on Windows Server 2022 x64 and macOS 14 Apple
silicon, with Python 3.11 and 3.14: all eight combinations passed 111 tests and
23 CLI checks. The performance test now uses native memory measurements on each
platform; the released application package did not require changes.

Live Qwen 2.5 3B inference through Ollama 0.34.2 passed all five reasoning roles
through both the native Ollama and OpenAI-compatible adapters, using the released
wheel on Ubuntu 24.04. One invalid compatible-API response was rejected, and the
bounded retry succeeded. The CPU-only run used a 600-second request timeout;
default-timeout performance is not established. Commercial/cloud credentials,
vLLM, other models/servers, and live inference on Windows/macOS were not tested.
No claim is made about general semantic accuracy.

The release verification report records the original exact-artifact installation
checks; the runtime audit adds the later platform and live-model evidence without
replacing the published release assets. CI uses pinned Action commits and Python
3.11-3.14 on Linux, with a manually runnable release runtime audit for the additional
platforms. Enterprise identity, remote catalogs, persistent shared caches and
external schema-registry enforcement remain outside this MVP; see LIMITATIONS.md
and DELIVERY_CHECKLIST.md.

## v0.1.3 packaging update

v0.1.3 packages the portable performance test, repeatable release-runtime audit
workflow, and updated installation/manual guidance. Application behavior is unchanged
from v0.1.2; only version/provenance identifiers change. The v0.1.2 live-model
audit above is retained as prior integration evidence, not represented as a new
v0.1.3 model run. Version-specific artifact and platform results are recorded in
the v0.1.3 release verification asset.
