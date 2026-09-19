# Executed validation

Validation date: 2026-09-19. Environment: Linux, CPython 3.14.7. These are observed execution results, not expected targets.

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
- Elapsed assessment time: **0.314 seconds**.
- Peak process RSS: **103.25 MiB**.

The raw measurement is in `docs/benchmark.json`. Hardware and dependency versions affect performance; these measurements are not a production SLA.

## Verification limits

Actual Ollama/vLLM model execution and commercial inference were not performed: no model server, downloaded weights or cloud credentials were supplied. HTTP protocol implementations, configuration independence, structured-output fallback, failure handling and security boundaries are exercised with controlled transports. No claim is made about provider-specific models' semantic accuracy.

The release verification report records exact-artifact installation checks and published CI results for this version. CI uses pinned Action commits and Python 3.11-3.14 on Linux. Enterprise identity, remote catalogs, persistent shared caches and external schema-registry enforcement remain outside this MVP; see LIMITATIONS.md and DELIVERY_CHECKLIST.md.
