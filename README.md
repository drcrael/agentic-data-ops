# Data Maturity Agent

A local-first Python CLI for understanding Excel, CSV and TSV data, measuring its quality, identifying missing knowledge, and defining a proposed governed data product.

**[User manual (PDF)](docs/Agentic_Data_Ops_User_Manual.pdf)** - 30-page installation and operating guide with worked examples, command reference and troubleshooting. [Editable source and build instructions](docs/manual/README.md).

Examples are fictional and use synthetic data. They do not describe or imply endorsement by any employer, customer, or operational program.

**Agents reason. Tools measure. Evidence persists. Humans resolve ambiguity.**

This is a functioning MVP, not an enterprise certification system. Measurements, semantic hypotheses, human authority, mission requirements and recommendations remain separately represented. A clean spreadsheet is not automatically AI-ready.

## Install

Python **3.11 or newer** is required. Linux is the primary tested platform.

```bash
git clone https://github.com/drcrael/agentic-data-ops.git
cd agentic-data-ops
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
data-maturity --help
```

On Windows, activate with `.venv\Scripts\Activate.ps1`; the shell scripts and resource-based performance test target Linux/macOS. A captured dependency set is in `requirements-dev.lock`; `pyproject.toml` defines supported version ranges.

## Quick start

```bash
python scripts/generate_test_workbooks.py
data-maturity inspect tests/fixtures/semi_structured.xlsx
data-maturity profile tests/fixtures/dirty_customers.xlsx
data-maturity analyze tests/fixtures/dirty_customers.xlsx --no-llm -o output/dirty
sh scripts/demo.sh
```

The default configuration also disables inference. No cloud account, network connection, model server or GPU is needed for these commands. Inputs are never modified. Use a new output directory for every run; existing reports are never overwritten.

`WAITING_FOR_HUMAN` is a successful assessment outcome: evidence and reports have been produced, but authoritative definitions or decisions remain missing. CLI exit code `0` means a valid assessment was produced, **not** that the data meets all requirements. Exit code `2` indicates invalid input, configuration, policy or output integrity.

## What it measures

- XLSX/XLSM structure: explicit tables, inferred regions, headers, hidden content, merged cells, named ranges, formulas, validations, filters and freeze panes.
- Physical schema with original/canonical names and explicit collision handling.
- Nulls, distinctness, duplicate records, physical type mixtures, finite numerical statistics and quantiles, string lengths, date formats, ambiguous/invalid dates, whitespace, case variants and potential anomalies.
- Complete/unique candidate keys, bounded two-field composite candidates, same-name identifier relationship candidates, containment, cardinality and candidate orphans.
- Explicit user-defined quality rules (`not_null`, `unique`, `range`, `enum`, `pattern`, `type`, `freshness`). Inferred expectations never silently become authoritative.
- Independent maturity dimensions, AI-readiness criteria and optional requirement-level mission fitness.

Null percentages use all measured rows; uniqueness ratios and duplicate frequencies use non-null values. Duplicate counts count occurrences beyond the first. Values are type-sensitive (`1`, `"1"`, and `true` differ). CSV types are inferred lexically; leading-zero identifiers remain strings. Slash dates with ambiguous day/month ordering are unresolved, not guessed.

Formula expressions are **not executed**. Their results are unavailable and count as missing in profiling, with an explicit formula finding. This does not prove those source cells are blank. XLSM macro code is never executed or interpreted.

## Architecture

```text
Adapters → table discovery → canonical dataset → deterministic profiling/rules
                                               ↓
                                            evidence
                                               ↓
                         bounded agents → policy-enforcing model gateway
                                               ↓
                    semantics / governance / mission fitness / maturity
                                               ↓
                              proposed schema, contract and remediation
                                               ↓
                     assessment controller → human gate → reassessment
```

`src/data_maturity/` separates ingestion, profiling, evidence, agents, providers, security, mission, maturity, contracts, reporting and control. Pydantic validates boundaries. The graph exports explicit references without requiring a graph database. Reporting renders canonical models and does not recompute analysis.

All assertions use **OBSERVED**, **INFERRED**, or **UNRESOLVED**. Inferences require confidence, reasoning and existing evidence. The model output schema cannot set units, coordinate frames, authoritative keys, policy, scores, endpoints or tool actions. Human resolutions create new assertion versions with provenance and supersession links.

## Models: local or remote

Use a deterministic mock end to end:

```bash
data-maturity analyze tests/fixtures/ambiguous_manufacturing.xlsx \
  --config configs/test_mock_llm.yaml -o output/mock
```

For Ollama, install a model yourself, replace `YOUR_INSTALLED_MODEL` in `configs/local.yaml`, start the server, then run:

```bash
data-maturity analyze workbook.xlsx --config configs/local.yaml -o output/local
```

Local endpoints must use **literal loopback IPs**, such as `http://127.0.0.1:11434` or `http://[::1]:11434`. `localhost` and private LAN IPs are conservatively classified as remote to avoid DNS/proxy ambiguity. Local servers must themselves be configured for local execution; an application cannot establish whether a local server secretly forwards requests elsewhere.

For vLLM or another compatible server:

```yaml
llm_enabled: true
security:
  mode: local_only
models:
  semantic_inference:
    provider: openai_compatible
    model: YOUR_INSTALLED_MODEL
    base_url: http://127.0.0.1:8000/v1
    timeout: 30
    json_schema: true
```

For a remote HTTPS service, explicitly enable metadata transmission:

```yaml
llm_enabled: true
security:
  mode: hybrid
  allow_metadata_to_remote_models: true
  allow_raw_data_to_remote_models: false
llm_context:
  include_samples: false
models:
  semantic_inference:
    provider: openai_compatible
    model: YOUR_CONFIGURED_MODEL
    base_url: https://YOUR_SERVICE/v1
    api_key_env: DATA_MATURITY_API_KEY
    timeout: 30
    json_schema: true
```

Export the API key in your shell or use your deployment's secret manager. `.env` files are **not** loaded automatically. Secrets are never stored in configuration objects or manifests. Set `json_schema: false` for JSON-only providers; returned JSON still undergoes Pydantic and reference validation.

Roles are independently configurable: `semantic_inference`, `quality_reasoning`, `governance_reasoning`, `maturation_reasoning`, `report_generation`. Missing roles are skipped. Models do not determine scores or completion. Model explanations remain attributed in `analyst_notes`; deterministic reports are always available.

Providers use [Ollama's chat structured-output API](https://ollama.com/blog/structured-outputs) or the configurable chat-completions wire format. HTTP transport disables redirects and environment proxies, following [HTTPX's documented controls](https://www.python-httpx.org/api/). Optional content-keyed caching is bounded to a gateway instance and disabled by default.

## Security and minimization

- `local_only` hard-fails configured remote inference **before transmission**. `--no-llm` never invokes a provider.
- Remote metadata requires permission independently of raw samples. Metadata payloads are constructed from an allowlist; they exclude rows, common values, extrema, human answers and arbitrary evidence values. Field names and aggregate counts are metadata and may themselves be sensitive.
- Raw sampling is disabled by default. Both `llm_context.include_samples` and remote raw permission must permit it. Requests and responses have size limits.
- Workbook values, names and metadata remain explicitly delimited untrusted JSON. No tool execution interface is exposed to models. Reference IDs and allowed output types are validated with bounded retries.
- Input bytes, expanded workbook size, cell count, columns and retained samples have configurable bounds. Outputs are staged atomically, with owner-only filesystem permissions on Unix.
- The test suite blocks external network connections. It inspects actual outbound contexts and verifies that a rejected provider is never called.
- Human authority is attributed, not authenticated by enterprise identity. Treat resolution/configuration files as trusted administrative inputs. See [SECURITY.md](SECURITY.md).

## Sampling and reproducibility

Defaults retain up to 10,000 rows using deterministic reservoir sampling over up to 1,000,000 scanned rows. CSV input is streamed. Excel uses one bounded openpyxl workbook, without a second DataFrame copy. If the scan limit is exceeded, reports explicitly label a sample of the **scanned prefix**, not an unbiased full-source sample.

Every profile and evidence object records its scope; sample-only relationships do not prove full-data orphans. Reports record file SHA-256, configuration hash, seed, provider/model, prompt and rule/model versions, sampling scope, timestamps and component statuses. The source hash identifies the exact artifact; profile evidence IDs are deterministic for unchanged inputs.

Set `profiling.include_value_summaries: true` to include bounded common values/enums in **local report files**. It does not override outbound model policy.

## Mission context and explicit rules

```bash
data-maturity analyze tests/fixtures/ambiguous_manufacturing.xlsx --no-llm \
  --mission examples/manufacturing_operations.yaml -o output/mission

data-maturity analyze tests/fixtures/anomalies.xlsx --no-llm \
  --config configs/quality_rules.yaml -o output/rules
```

The manufacturing fixture contains ten synthetic part-inspection records. Part identifiers are complete; measurement units, reference frame, and status-code meanings are intentionally undefined. The example initially reports identity `FIT`, frame `UNDETERMINED`, and units `UNDETERMINED`. These checks assess data readiness, not whether parts meet engineering tolerances.

Mission requirements have explicit dataset/field mappings and checks. Results are `FIT`, `PARTIALLY_FIT`, `NOT_FIT`, or `UNDETERMINED` per requirement. Narrative requirements without executable criteria remain unresolved. Freshness checks require an explicit quality rule, timezone-aware timestamps and a user-defined age threshold; timezone and temporal meaning are never inferred as authoritative.

Maturity criteria are shipped in `configs/maturity_model.yaml` and packaged as resources. Customize the `maturity_model` mapping in configuration. Levels are cumulative: an unsatisfied lower-level requirement blocks higher levels. Unknown criterion names never pass. New criterion implementations belong in `maturity/evaluator.py`.

## Resolve, reassess and establish baselines

Create an answer file using IDs from `sme_questions.md`:

```yaml
answers:
  question:REPLACE_WITH_ACTUAL_ID:
    answer: mm
    answered_by: Inspection data steward
    authority: Accountable source owner
    authoritative: true
    source_reference: Approved source specification, section 4
```

```bash
data-maturity resolve output/mission/assessment.json answers.yaml \
  --source tests/fixtures/ambiguous_manufacturing.xlsx -o output/resolved

data-maturity analyze changed-workbook.xlsx --no-llm \
  --prior output/resolved/assessment_history.json -o output/reassessed
```

Preserve the source filename to compare the same asset. Dataset/field IDs are stable across content changes, while evidence captures the content hash. Changed source data is remeasured; unchanged measurements are reused for SME and rule-only changes. Source changes conservatively require re-confirmation of old authoritative answers. Historical answers and snapshots remain available.

`assessment_history.json` contains iterations, triggers, decisions, resolutions, snapshots, finding changes and baselines. `assessment_delta.json` exposes dimensional changes. The controller is event-driven: one automatic assessment pass per supplied event, followed by a deterministic stop, human gate or baseline decision. It does not repeatedly call models hoping to manufacture authority. This conservative one-pass automatic budget is always below the configured `max_iterations` ceiling; additional iterations require new explicit invocations.

When blocking questions have been answered or formally accepted as risk:

```bash
data-maturity analyze workbook.xlsx --prior output/resolved/assessment_history.json \
  --baseline approved -o output/baseline

data-maturity analyze workbook.xlsx --prior output/baseline/assessment_history.json \
  --compare-baseline approved -o output/compared
```

Named baselines are immutable and content-validated. Baseline establishment describes a trustworthy assessment, not perfect data. `REMEDIATION_REQUIRED` indicates a valid baseline with material findings. Risk acceptance requires an authoritative resolution with rationale, scope and a future timezone-aware review date; expired risk reopens the question. Full resolution objects also support acknowledgement and remediation-planned finding states. See [docs/control-loop.md](docs/control-loop.md).

## Output artifacts

| Artifact | Purpose |
|---|---|
| `assessment.json` | Canonical Pydantic-validated workbook assessment |
| `schema.json` | Observed and proposed schemas by dataset |
| `quality_report.json` | Metrics and explicit rules, with scopes and evidence |
| `evidence.json` | Measurement and provenance objects, not full raw rows |
| `evidence_graph.json` | Explicit graph edges with validated references |
| `data_contract.yaml` | Proposed contracts, candidate keys and unresolved items |
| `sme_questions.md` | Targeted, prioritized questions with stable IDs |
| `maturity_report.md` | Human-readable assessment and remediation roadmap |
| `mission_fitness.json` | Optional requirement-level fitness results |
| `run_manifest.json` | Reproducibility metadata and artifact hashes |
| `assessment_history.json` | Longitudinal control and knowledge history |
| `assessment_delta.json` | Changes when a prior run or baseline is supplied |

Generated synthetic example outputs are in [examples/output](examples/output).

## Tests and demonstration

```bash
sh scripts/test.sh
pytest -m unit
pytest -m integration
pytest -m acceptance
pytest -m security
pytest --cov=data_maturity --cov-report=term-missing
sh scripts/demo.sh
```

The suite checks exact fixture counts, uncertain semantics, provider payloads, policy enforcement, malicious cell contents, evidence integrity, human resolutions, named baselines and a 100,000-row input. Provider tests exercise the HTTP wire format with a controlled transport; running a real model is optional and is not required by CI.

See [DELIVERY_CHECKLIST.md](DELIVERY_CHECKLIST.md), [VALIDATION.md](VALIDATION.md), and [LIMITATIONS.md](LIMITATIONS.md) for the implemented scope, measured verification and remaining limitations.
