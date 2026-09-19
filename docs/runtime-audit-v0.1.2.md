# v0.1.2 live integration and platform audit

Date: 2026-09-19

## Exact artifacts
The existing published v0.1.2 wheel and source distribution were downloaded from GitHub on each runner and checked against the release SHA256SUMS manifest. Installation was noneditable. The audit verified the imported package came from site-packages. Published binaries and the v0.1.2 tag were not changed.

## Windows and macOS
Eight native GitHub-hosted runner jobs covered Windows Server 2022 (x64, build 20348) and macOS 14.8.9 (Apple silicon/arm64), Python 3.11 and 3.14, and wheel and source installs. All eight passed 111 tests (95.52% coverage), with no skips, plus 23 CLI checks. Aggregate: 888 passing test executions and 184 passing CLI checks.

The CLI checks exercised nine workbook/CSV/TSV fixtures, inspect/profile, all five mock reasoning roles with the manufacturing context, source immutability, report artifact hashes, evidence validity, ten maturity dimensions, proposed contracts, human resolutions, named baseline establishment, unchanged-history reuse, changed-source regression comparison, and six invalid-input/policy rejection paths.

The 100,000-row performance test verifies 10,000-row disclosed sampling, peak process memory below 512 MiB, and execution below 60 seconds. Its original implementation imported the Unix-only resource module. The audit corrected this test to use native Windows peak-working-set counters and normalized macOS/Linux measurements to bytes; the application package did not require a change. These tests used the current repository harness against the installed release. The immutable v0.1.2 source archive still contains the original Unix-only performance test; running that bundled test directly on Windows remains unsupported unless the harness correction is applied.

POSIX output permission bits are checked on macOS/Linux. Windows end-to-end success does not establish a Windows ACL privacy guarantee; this audit does not certify every desktop configuration, Python version, processor architecture, or spreadsheet feature.

## Live model integration
The native Ollama adapter completed all five reasoning roles on the first attempt using Qwen 2.5 3B under Ollama 0.34.2 on a CPU-only Ubuntu 24.04 runner. The published wheel was installed rather than the source checkout. The application produced validated reports, all evidence references passed validation, all output hashes matched, and the synthetic source file remained unchanged.

The OpenAI-compatible adapter also completed all five roles. Its first semantic response failed schema validation (ValidationError); the configured second attempt succeeded. The other four roles completed on their first attempt. All ten final inference records report COMPLETE, and all component statuses are COMPLETE. Both assessments include a nonempty inferred identifier hypothesis for part_id. Both correctly retain WAITING_FOR_HUMAN as the control outcome: successful inference does not supply missing human authority.

Observed model digest: `357c53fb659c5076de1d65ccb0b397446227b71a42be9d1603d46168015c9e4b` (3.1B parameters, Q4_K_M). The combined live-adapter step took approximately 22 minutes on the CPU runner. Downloaded assessment bundles were independently revalidated locally after the successful job.

The configuration used local_only policy, no raw sample rows, temperature 0, JSON Schema responses, a 2,048-token output limit and a 600-second per-request timeout. CPU-only inference is slow; this check does not establish that the default 30-second timeout is sufficient on every machine. The model was downloaded to the temporary runner; no model server or weights were installed on the user's computer.

No commercial/cloud API credentials were configured in this environment or repository. Commercial provider authentication, rate limits, model-specific API restrictions and remote deployment have not been verified. Ollama's compatible API is a real local-model endpoint, not evidence of a successful paid cloud API call. vLLM and other compatible servers were not tested.

References: [Ollama chat API](https://docs.ollama.com/api/chat), [Ollama OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility).


## Artifact identities
- Release source/tag commit: `2e9b18c374cbae0c55b2b28e26b2da51e4ec240e`
- Wheel SHA-256: `6ae67b5fef5ab4bab53b48c2bf5dfedfa1dc9a2e4def9c2156087235e24194a9`
- Source package SHA-256: `7e9c14c821ece1404329223f557d6d0874cbb938ef0788287c457380c40b5b5e`

## Reproduction and evidence
- Runtime audit: https://github.com/drcrael/agentic-data-ops/actions/runs/35464225430
- Linux quality CI: https://github.com/drcrael/agentic-data-ops/actions/runs/35464225501
- Reusable workflow: .github/workflows/release-runtime-audit.yml (manual workflow_dispatch)
- Audit scripts: scripts/install_audit_artifact.py, scripts/audit_release_cli.py, scripts/audit_live_models.py
- Test harness commit: d387419

The first audit run exposed the Unix-only performance-test implementation and a checksum filename-filter mismatch in the new Ollama installation step. Both audit issues were corrected before the successful platform rerun. These were not product-runtime failures.

The final nine-job runtime audit completed successfully. Application logs, inference records, reports and platform test artifacts are available with the GitHub run. A diagnostic log filename was subsequently separated from the application log filename to prevent overwriting server diagnostics on future runs; no inference behavior changed. Repository verification notes supersede the narrower test-scope statements in the original v0.1.2 release manual/report.
