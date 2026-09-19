# Assessment control loop

`AssessmentController` owns state, change detection, comparison and convergence. `AssessmentOrchestrator` executes stages. All assertions, resolutions and iterations are validated domain objects.

An invocation handles one explicit event. It moves through INITIALIZED or REASSESSING, then measurement stages if needed. The final decision is deterministic:

1. Open blocking authoritative questions → WAITING_FOR_HUMAN.
2. No blocking questions, but failed optional reasoning → DEGRADED.
3. All authoritative gates pass and material findings remain → REMEDIATION_REQUIRED.
4. All gates pass without material findings → BASELINE_ESTABLISHED.

Optional failure is also recorded in component_status when the human gate takes precedence. Fatal input/policy/integrity errors raise and the CLI exits with code 2 rather than publishing an apparently valid report. There is no hidden retry loop for authoritative knowledge. A single pass is below the configured maximum automatic iteration limit; another event requires a new invocation.

Fingerprint inputs include source content, sampling configuration/seed, quality rules, maturity model, mission context, governance metadata, SME responses, prompt versions and model/policy settings. Derived fingerprints cover datasets, schema, contract and traversed affected dependencies.

SME resolutions never modify a historical assertion's value/state. The original receives a superseded_by link, and the new assertion records supersedes and resolved_by. Prior snapshots remain unchanged. Authoritative answers become OBSERVED **as attributed human knowledge**, not independently verified truth. Non-authoritative answers remain INFERRED and leave the gate open.

## Full resolution format

```yaml
resolutions:
  - resolution_id: resolution:example-risk
    question_id: question:REPLACE_WITH_REAL_ID
    resolution_type: ACCEPTED_RISK
    value: Defer this question for the sandbox use case
    provided_by: Accountable owner
    authority: Data-product owner
    authoritative: true
    source_reference: Decision record DR-001
    rationale: Limited synthetic-data demonstration
    scope: Synthetic dataset and sandbox use only
    review_at: '2027-01-01T00:00:00Z'
```

Supported resolution types include SME_ANSWER, DATA_OWNER_DECISION, GOVERNANCE_DECISION, AUTHORITATIVE_REFERENCE, USER_OVERRIDE, ACCEPTED_RISK, ACKNOWLEDGED and REMEDIATION_PLANNED. RULE_UPDATE is represented but intentionally requires a validated configuration update and `analyze --prior`; arbitrary answer values cannot change code or executable rules.

Risk acceptance requires authority/rationale/scope/review date. Expiry reopens applicable questions/findings. Authoritative answers cannot erase deterministic defects; correct the data, change an explicit rule, or accept risk through the dedicated lifecycle operation.

Snapshots preserve evidence and findings across source changes. Baseline names cannot be reused; their hashes must match stored snapshots before comparison. Comparison is dimensional, never one aggregate score. Authoritative resolutions on old source content remain in history but must be reconfirmed after source changes.
