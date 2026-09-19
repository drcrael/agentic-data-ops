# Data Maturity Assessment

## Executive Summary

Analyzed **1 datasets** from dirty\_customers.xlsx.
Control outcome: **WAITING_FOR_HUMAN**.
Findings distinguish OBSERVED measurements, INFERRED interpretations, and UNRESOLVED knowledge. Proposed contracts require owner review.

## Dataset Inventory

- Customers: 6 source rows; 6 measured rows; scope **full**; 5 fields.

## Structural Assessment

### Customers

- Region A1:E7, confidence 0.9, method blank_boundaries_and_header.

## Schema Assessment

### Customers

- customer\_id → customer\_id (mixed); candidate key membership remains unconfirmed.
- customer\_name → customer\_name (string); candidate key membership remains unconfirmed.
- state → state (string); candidate key membership remains unconfirmed.
- status → status (string); candidate key membership remains unconfirmed.
- created\_at → created\_at (mixed); candidate key membership remains unconfirmed.

## Data Quality

### Customers

- uniqueness/duplicate\_records: 1 (FAIL, full); evidence evidence:490393998160a489a29185bf.
- completeness/missing\_identifier: 1 (WARNING, full); evidence evidence:4cef4b91ea4a05b2e1afb18a.
- uniqueness/duplicate\_candidate\_identifier: 1 (WARNING, full); evidence evidence:4cef4b91ea4a05b2e1afb18a.
- conformity/whitespace\_inconsistency: 0 (PASS, full); evidence evidence:4cef4b91ea4a05b2e1afb18a.
- consistency/casing\_inconsistency: 0 (PASS, full); evidence evidence:4cef4b91ea4a05b2e1afb18a.
- validity/invalid\_or\_ambiguous\_dates: 0 (PASS, full); evidence evidence:4cef4b91ea4a05b2e1afb18a.
- consistency/mixed\_physical\_types: 1 (FAIL, full); evidence evidence:4cef4b91ea4a05b2e1afb18a.
- validity/nonfinite\_values: 0 (PASS, full); evidence evidence:4cef4b91ea4a05b2e1afb18a.
- accuracy_proxies/potential\_anomaly\_iqr: 0 (PASS, full); evidence evidence:4cef4b91ea4a05b2e1afb18a.
- accuracy_proxies/potential\_anomaly\_mad: 0 (PASS, full); evidence evidence:4cef4b91ea4a05b2e1afb18a.
- accuracy_proxies/potential\_anomaly\_length\_iqr: 0 (PASS, full); evidence evidence:4cef4b91ea4a05b2e1afb18a.
- accuracy_proxies/potential\_anomaly\_rare\_categories: 0 (PASS, full); evidence evidence:4cef4b91ea4a05b2e1afb18a.
- completeness/missing\_values: 0 (PASS, full); evidence evidence:a6e218fc3935394674fe4c11.
- conformity/whitespace\_inconsistency: 1 (FAIL, full); evidence evidence:a6e218fc3935394674fe4c11.
- consistency/casing\_inconsistency: 0 (PASS, full); evidence evidence:a6e218fc3935394674fe4c11.
- validity/invalid\_or\_ambiguous\_dates: 0 (PASS, full); evidence evidence:a6e218fc3935394674fe4c11.
- consistency/mixed\_physical\_types: 0 (PASS, full); evidence evidence:a6e218fc3935394674fe4c11.
- validity/nonfinite\_values: 0 (PASS, full); evidence evidence:a6e218fc3935394674fe4c11.
- accuracy_proxies/potential\_anomaly\_length\_iqr: 1 (WARNING, full); evidence evidence:a6e218fc3935394674fe4c11.
- accuracy_proxies/potential\_anomaly\_rare\_categories: 0 (PASS, full); evidence evidence:a6e218fc3935394674fe4c11.
- completeness/missing\_values: 0 (PASS, full); evidence evidence:5251f836c1f901de2055c575.
- conformity/whitespace\_inconsistency: 0 (PASS, full); evidence evidence:5251f836c1f901de2055c575.
- consistency/casing\_inconsistency: 4 (FAIL, full); evidence evidence:5251f836c1f901de2055c575.
- validity/invalid\_or\_ambiguous\_dates: 0 (PASS, full); evidence evidence:5251f836c1f901de2055c575.
- consistency/mixed\_physical\_types: 0 (PASS, full); evidence evidence:5251f836c1f901de2055c575.
- validity/nonfinite\_values: 0 (PASS, full); evidence evidence:5251f836c1f901de2055c575.
- accuracy_proxies/potential\_anomaly\_length\_iqr: 0 (PASS, full); evidence evidence:5251f836c1f901de2055c575.
- accuracy_proxies/potential\_anomaly\_rare\_categories: 0 (PASS, full); evidence evidence:5251f836c1f901de2055c575.
- completeness/missing\_values: 0 (PASS, full); evidence evidence:efd675a6196ddd2a8d50c782.
- conformity/whitespace\_inconsistency: 1 (FAIL, full); evidence evidence:efd675a6196ddd2a8d50c782.
- consistency/casing\_inconsistency: 4 (FAIL, full); evidence evidence:efd675a6196ddd2a8d50c782.
- validity/invalid\_or\_ambiguous\_dates: 0 (PASS, full); evidence evidence:efd675a6196ddd2a8d50c782.
- consistency/mixed\_physical\_types: 0 (PASS, full); evidence evidence:efd675a6196ddd2a8d50c782.
- validity/nonfinite\_values: 0 (PASS, full); evidence evidence:efd675a6196ddd2a8d50c782.
- accuracy_proxies/potential\_anomaly\_length\_iqr: 1 (WARNING, full); evidence evidence:efd675a6196ddd2a8d50c782.
- accuracy_proxies/potential\_anomaly\_rare\_categories: 0 (PASS, full); evidence evidence:efd675a6196ddd2a8d50c782.
- completeness/missing\_values: 0 (PASS, full); evidence evidence:650afac3e7f09c78af73b89d.
- conformity/whitespace\_inconsistency: 0 (PASS, full); evidence evidence:650afac3e7f09c78af73b89d.
- consistency/casing\_inconsistency: 0 (PASS, full); evidence evidence:650afac3e7f09c78af73b89d.
- validity/invalid\_or\_ambiguous\_dates: 3 (WARNING, full); evidence evidence:650afac3e7f09c78af73b89d.
- consistency/mixed\_physical\_types: 3 (FAIL, full); evidence evidence:650afac3e7f09c78af73b89d.
- validity/nonfinite\_values: 0 (PASS, full); evidence evidence:650afac3e7f09c78af73b89d.
- accuracy_proxies/potential\_anomaly\_length\_iqr: 0 (PASS, full); evidence evidence:650afac3e7f09c78af73b89d.
- accuracy_proxies/potential\_anomaly\_rare\_categories: 0 (PASS, full); evidence evidence:650afac3e7f09c78af73b89d.
- integrity/integrity\_unresolved: UNDETERMINED (UNDETERMINED, metadata); evidence evidence:17654c2cf035209d9d012c9c.
- timeliness/timeliness\_unresolved: UNDETERMINED (UNDETERMINED, metadata); evidence evidence:17654c2cf035209d9d012c9c.
- semantic_clarity/semantic\_clarity\_unresolved: UNDETERMINED (UNDETERMINED, metadata); evidence evidence:17654c2cf035209d9d012c9c.
- provenance/provenance\_unresolved: UNDETERMINED (UNDETERMINED, metadata); evidence evidence:17654c2cf035209d9d012c9c.
- governance/governance\_unresolved: UNDETERMINED (UNDETERMINED, metadata); evidence evidence:17654c2cf035209d9d012c9c.

## Semantic Assessment

### Customers

- **INFERRED** customer\_id likely represents identifier; evidence evidence:4cef4b91ea4a05b2e1afb18a.
- **UNRESOLVED** definition cannot be established from supplied evidence; evidence evidence:4cef4b91ea4a05b2e1afb18a.
- **INFERRED** customer\_name likely represents name; evidence evidence:a6e218fc3935394674fe4c11.
- **UNRESOLVED** definition cannot be established from supplied evidence; evidence evidence:a6e218fc3935394674fe4c11.
- **INFERRED** state likely represents category; evidence evidence:5251f836c1f901de2055c575.
- **UNRESOLVED** definition cannot be established from supplied evidence; evidence evidence:5251f836c1f901de2055c575.
- **INFERRED** status likely represents status; evidence evidence:efd675a6196ddd2a8d50c782.
- **UNRESOLVED** definition cannot be established from supplied evidence; evidence evidence:efd675a6196ddd2a8d50c782.
- **UNRESOLVED** code definitions cannot be established from supplied evidence; evidence evidence:efd675a6196ddd2a8d50c782.
- **INFERRED** created\_at likely represents timestamp; evidence evidence:650afac3e7f09c78af73b89d.
- **UNRESOLVED** definition cannot be established from supplied evidence; evidence evidence:650afac3e7f09c78af73b89d.
- **UNRESOLVED** temporal semantics cannot be established from supplied evidence; evidence evidence:650afac3e7f09c78af73b89d.

## Relationships

### Customers


## Governance Assessment

### Customers

- owner: UNRESOLVED; evidence evidence:bc0d37eb228904982415210a.
- steward: UNRESOLVED; evidence evidence:f21b27ce23c3c68dd7990a81.
- authoritative_source: UNRESOLVED; evidence evidence:7026d2189af6b19c5e3cf7cf.
- source_system: UNRESOLVED; evidence evidence:bad804492f05241a15f0bf72.
- provenance: UNRESOLVED; evidence evidence:bd40c5b1523aaafe42ccc7db.
- lineage: UNRESOLVED; evidence evidence:1e916eeebc0ff8f212f9fd03.
- sensitivity: UNRESOLVED; evidence evidence:aad7f6035568b437b42496c6.
- security_classification: UNRESOLVED; evidence evidence:9dfd604551b9fc51cd3981a6.
- access_constraints: UNRESOLVED; evidence evidence:a16201e58695fb75267c29ee.
- retention: UNRESOLVED; evidence evidence:4e2350091176e0d7b15851f2.
- update_cadence: UNRESOLVED; evidence evidence:2198f3250d85342dba0d016e.
- version: UNRESOLVED; evidence evidence:f2ad6bae188e205284ce853c.
- licensing: UNRESOLVED; evidence evidence:b036483e08687215ad245e52.
- quality_accountability: UNRESOLVED; evidence evidence:063c18b17a44e4169d2d01ac.

## AI Readiness

### Customers

- accessibility: SATISFIED — Explicit criterion &\#x27;machine\_accessible&\#x27; satisfied
- structure: SATISFIED — Explicit criterion &\#x27;stable\_tabular\_structure&\#x27; satisfied
- semantics: BLOCKED — Explicit criterion &\#x27;semantics\_resolved&\#x27; not established
- quality: BLOCKED — Explicit criterion &\#x27;quality\_controlled&\#x27; not established
- provenance: BLOCKED — Explicit criterion &\#x27;provenance\_documented&\#x27; not established
- lineage: BLOCKED — Explicit criterion &\#x27;lineage\_documented&\#x27; not established
- governance: BLOCKED — Explicit criterion &\#x27;governance\_defined&\#x27; not established
- documentation: BLOCKED — Explicit criterion &\#x27;field\_definitions\_present&\#x27; not established
- contracts: BLOCKED — Explicit criterion &\#x27;contract\_authoritative&\#x27; not established
- stability: BLOCKED — Explicit criterion &\#x27;schema\_versioned&\#x27; not established
- observability: BLOCKED — Explicit criterion &\#x27;monitoring\_operational&\#x27; not established
- suitability: UNDETERMINED — Requires explicit intended-use requirements and their evidence-backed evaluation

## Maturity Assessment

### Customers

- structure: Level 1 (STRUCTURED); satisfied: stable_tabular_structure; next: typed_fields; missing: typed_fields, authoritative_schema, schema_validation_automated, monitoring_operational.
- schema_definition: Level 1 (STRUCTURED); satisfied: stable_tabular_structure, machine_readable_contract; next: typed_fields, candidate_keys_identified, field_definitions_present; missing: typed_fields, candidate_keys_identified, field_definitions_present, authoritative_schema, constraints_defined, schema_validation_automated, schema_versioned, semantic_definitions_machine_readable.
- data_quality: Level 1 (STRUCTURED); satisfied: quality_measured; next: no_high_quality_findings; missing: no_high_quality_findings, quality_controlled, monitoring_operational, ai_readiness_verified.
- semantic_clarity: Level 1 (STRUCTURED); satisfied: metadata_recorded; next: field_definitions_present; missing: field_definitions_present, semantics_resolved, schema_versioned, semantic_definitions_machine_readable.
- metadata: Level 1 (STRUCTURED); satisfied: metadata_recorded; next: field_definitions_present; missing: field_definitions_present, governance_defined, schema_versioned, semantic_definitions_machine_readable.
- provenance_lineage: Level 1 (STRUCTURED); satisfied: metadata_recorded; next: provenance_documented; missing: provenance_documented, lineage_documented, monitoring_operational, ai_readiness_verified.
- governance: Level 1 (STRUCTURED); satisfied: metadata_recorded; next: owner_known; missing: owner_known, governance_defined, authority_known, monitoring_operational, ai_readiness_verified.
- machine_accessibility: Level 1 (STRUCTURED); satisfied: machine_accessible; next: typed_fields; missing: typed_fields, governance_defined, schema_validation_automated, ai_readiness_verified.
- data_contracts: Level 1 (STRUCTURED); satisfied: machine_readable_contract; next: constraints_defined; missing: constraints_defined, contract_authoritative, schema_versioned, semantic_definitions_machine_readable.
- ai_readiness: Level 1 (STRUCTURED); satisfied: machine_accessible; next: semantics_resolved; missing: semantics_resolved, governance_defined, quality_controlled, monitoring_operational, ai_readiness_verified.

## Critical Findings

### Customers

- finding:fd499fd5fc242e90f09d1379: [high/OBSERVED/OPEN] duplicate records in measured scope; review source evidence. Evidence: evidence:490393998160a489a29185bf.
- finding:850bce205d0d29a326d3c637: [high/INFERRED/OPEN] missing identifier in measured scope; review source evidence. Evidence: evidence:4cef4b91ea4a05b2e1afb18a.
- finding:519536cac6d39dbbd493afb3: [high/INFERRED/OPEN] duplicate candidate identifier in measured scope; review source evidence. Evidence: evidence:4cef4b91ea4a05b2e1afb18a.
- finding:b87bc9df10bf12ab65b106a8: [high/OBSERVED/OPEN] mixed physical types in measured scope; review source evidence. Evidence: evidence:4cef4b91ea4a05b2e1afb18a.
- finding:59bf15dddabcf27efb2af5eb: [high/OBSERVED/OPEN] whitespace inconsistency in measured scope; review source evidence. Evidence: evidence:a6e218fc3935394674fe4c11.
- finding:439905cc3e3b800959366b89: [high/OBSERVED/OPEN] casing inconsistency in measured scope; review source evidence. Evidence: evidence:5251f836c1f901de2055c575.
- finding:7940d984f4ccec0120df2c72: [high/OBSERVED/OPEN] whitespace inconsistency in measured scope; review source evidence. Evidence: evidence:efd675a6196ddd2a8d50c782.
- finding:90f4c807b44497e68e9b7359: [high/OBSERVED/OPEN] casing inconsistency in measured scope; review source evidence. Evidence: evidence:efd675a6196ddd2a8d50c782.
- finding:a1cd355b99256fa77f0074cc: [high/INFERRED/OPEN] invalid or ambiguous dates in measured scope; review source evidence. Evidence: evidence:650afac3e7f09c78af73b89d.
- finding:78209f737241b4f63d907144: [high/OBSERVED/OPEN] mixed physical types in measured scope; review source evidence. Evidence: evidence:650afac3e7f09c78af73b89d.
- finding:8eb0556b69812d0729b34ca0: [high/UNRESOLVED/OPEN] code definitions cannot be established from supplied evidence Evidence: evidence:efd675a6196ddd2a8d50c782.
- finding:78b6a75cc0ef561e07c1ccc7: [high/UNRESOLVED/OPEN] temporal semantics cannot be established from supplied evidence Evidence: evidence:650afac3e7f09c78af73b89d.
- finding:5725d06e94f7d0d3ef6b3d56: [high/UNRESOLVED/OPEN] governance owner cannot be established from supplied evidence Evidence: evidence:bc0d37eb228904982415210a.
- finding:b799423fd9b083b7e3809a51: [high/UNRESOLVED/OPEN] governance authoritative source cannot be established from supplied evidence Evidence: evidence:7026d2189af6b19c5e3cf7cf.
- finding:33f4f57b73a91ff220d3f950: [high/UNRESOLVED/OPEN] governance security classification cannot be established from supplied evidence Evidence: evidence:9dfd604551b9fc51cd3981a6.

## Unresolved Questions

### Customers

- question:92945c4250cc104c658878f7: What is the authoritative business definition of &\#x27;customer\_id&\#x27; in Customers? (OPEN)
- question:c6caf782af2d3a4939e6b2ba: What is the authoritative business definition of &\#x27;customer\_name&\#x27; in Customers? (OPEN)
- question:f8dd87ca25f991b59dc17149: What is the authoritative business definition of &\#x27;state&\#x27; in Customers? (OPEN)
- question:28d53945d66fcd233fbcb42a: What is the authoritative business definition of &\#x27;status&\#x27; in Customers? (OPEN)
- question:760df82ff4f02c074b635f7c: &\#x27;status&\#x27; has 5 distinct non-null values in measured scope. What is the authoritative code dictionary and permitted vocabulary? (OPEN)
- question:8105db661afd3cad4d3d763d: What is the authoritative business definition of &\#x27;created\_at&\#x27; in Customers? (OPEN)
- question:3baa98d6f2a7ef02e0bab2b9: Does &\#x27;created\_at&\#x27; record event, processing or publication time, and what timezone/time scale and freshness limit apply? (OPEN)
- question:205c6eb4d23f4fba53fdd94a: Who can authoritatively document owner for &\#x27;Customers&\#x27;, and provide a source reference? (OPEN)
- question:ae243e7c119accc07c7069bc: Who can authoritatively document steward for &\#x27;Customers&\#x27;, and provide a source reference? (OPEN)
- question:94a1230b58001c88897ca73b: Who can authoritatively document authoritative source for &\#x27;Customers&\#x27;, and provide a source reference? (OPEN)
- question:96a67b7cb958e998b8052c01: Who can authoritatively document source system for &\#x27;Customers&\#x27;, and provide a source reference? (OPEN)
- question:a1c1b9f93e0a198dddd73923: Who can authoritatively document provenance for &\#x27;Customers&\#x27;, and provide a source reference? (OPEN)
- question:39d2fdfd284211be632a3359: Who can authoritatively document lineage for &\#x27;Customers&\#x27;, and provide a source reference? (OPEN)
- question:b4154a4318e9313cd0b819d2: Who can authoritatively document sensitivity for &\#x27;Customers&\#x27;, and provide a source reference? (OPEN)
- question:b15f34380d23038027f8ad9e: Who can authoritatively document security classification for &\#x27;Customers&\#x27;, and provide a source reference? (OPEN)
- question:604cdac724dce0e0ca61a67b: Who can authoritatively document access constraints for &\#x27;Customers&\#x27;, and provide a source reference? (OPEN)
- question:c07094ca316ca841488e2a23: Who can authoritatively document retention for &\#x27;Customers&\#x27;, and provide a source reference? (OPEN)
- question:ed2579d4c6af9d3488d62b03: Who can authoritatively document update cadence for &\#x27;Customers&\#x27;, and provide a source reference? (OPEN)
- question:77e85ce87fa2eb8b5e4c71a5: Who can authoritatively document version for &\#x27;Customers&\#x27;, and provide a source reference? (OPEN)
- question:36e1c8bd1e11be78d52cf48d: Who can authoritatively document licensing for &\#x27;Customers&\#x27;, and provide a source reference? (OPEN)
- question:f0b78bd40c4361c650654b79: Who can authoritatively document quality accountability for &\#x27;Customers&\#x27;, and provide a source reference? (OPEN)

## Recommended Target State

### Customers

- Proposed schema and contract are in schema.json and data_contract.yaml. Unknown units, authority and constraints remain explicit.

## Prioritized Remediation Roadmap

### Customers

- 36.7 [high] Review variants against original values; approve a canonical mapping and enforce it during ingestion. Finding: finding:439905cc3e3b800959366b89; evidence: evidence:5251f836c1f901de2055c575.
- 36.7 [high] Review variants against original values; approve a canonical mapping and enforce it during ingestion. Finding: finding:90f4c807b44497e68e9b7359; evidence: evidence:efd675a6196ddd2a8d50c782.
- 35.0 [high] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:5725d06e94f7d0d3ef6b3d56; evidence: evidence:bc0d37eb228904982415210a.
- 35.0 [high] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:b799423fd9b083b7e3809a51; evidence: evidence:7026d2189af6b19c5e3cf7cf.
- 35.0 [high] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:8eb0556b69812d0729b34ca0; evidence: evidence:efd675a6196ddd2a8d50c782.
- 35.0 [high] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:33f4f57b73a91ff220d3f950; evidence: evidence:9dfd604551b9fc51cd3981a6.
- 35.0 [high] Review variants against original values; approve a canonical mapping and enforce it during ingestion. Finding: finding:78209f737241b4f63d907144; evidence: evidence:650afac3e7f09c78af73b89d.
- 35.0 [high] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:78b6a75cc0ef561e07c1ccc7; evidence: evidence:650afac3e7f09c78af73b89d.
- 35.0 [high] Review failing records against the explicit rule or field definition; correct from an authoritative source and rerun validation. Finding: finding:a1cd355b99256fa77f0074cc; evidence: evidence:650afac3e7f09c78af73b89d.
- 31.7 [high] Review variants against original values; approve a canonical mapping and enforce it during ingestion. Finding: finding:b87bc9df10bf12ab65b106a8; evidence: evidence:4cef4b91ea4a05b2e1afb18a.
- 31.7 [high] Define a canonical representation with the owner and validate formatting at ingestion; preserve original values in lineage. Finding: finding:7940d984f4ccec0120df2c72; evidence: evidence:efd675a6196ddd2a8d50c782.
- 31.7 [high] Confirm entity granularity and key authority; quarantine duplicates for owner review before deduplicating. Finding: finding:fd499fd5fc242e90f09d1379; evidence: evidence:490393998160a489a29185bf.
- 31.7 [high] Confirm requiredness and obtain missing values from the authoritative source; add a not-null rule only after approval. Finding: finding:850bce205d0d29a326d3c637; evidence: evidence:4cef4b91ea4a05b2e1afb18a.
- 31.7 [high] Confirm entity granularity and key authority; quarantine duplicates for owner review before deduplicating. Finding: finding:519536cac6d39dbbd493afb3; evidence: evidence:4cef4b91ea4a05b2e1afb18a.
- 31.7 [high] Define a canonical representation with the owner and validate formatting at ingestion; preserve original values in lineage. Finding: finding:59bf15dddabcf27efb2af5eb; evidence: evidence:a6e218fc3935394674fe4c11.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:5914f4c8a75711a7e07c63d6; evidence: evidence:063c18b17a44e4169d2d01ac.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:bb7552d82ecae73dc26593e6; evidence: evidence:2198f3250d85342dba0d016e.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:311d35157b5827799fa5969e; evidence: evidence:aad7f6035568b437b42496c6.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:f664d4872f6912c580b6fb93; evidence: evidence:bd40c5b1523aaafe42ccc7db.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:6409bba33b5a78b8e1e62bb2; evidence: evidence:f2ad6bae188e205284ce853c.
- 25.0 [medium] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:3c257ad6732cd27bd31b9c4a; evidence: evidence:650afac3e7f09c78af73b89d.
- 25.0 [medium] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:abff3db953aa7b1e57bc7ec7; evidence: evidence:5251f836c1f901de2055c575.
- 25.0 [medium] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:180da86ca1343f544cf291af; evidence: evidence:4cef4b91ea4a05b2e1afb18a.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:26b3823513a0631cdb40249d; evidence: evidence:b036483e08687215ad245e52.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:cf3d51356b5de19270acc538; evidence: evidence:f21b27ce23c3c68dd7990a81.
- 25.0 [medium] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:07594156edb8d62cbe5584a8; evidence: evidence:a6e218fc3935394674fe4c11.
- 25.0 [medium] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:f2ec804cb8ed539a938fae73; evidence: evidence:efd675a6196ddd2a8d50c782.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:21c595d58a73b395579264e3; evidence: evidence:4e2350091176e0d7b15851f2.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:0a0616e6d1065e4e664a575c; evidence: evidence:bad804492f05241a15f0bf72.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:3a4036c116ca12e2ef739ab1; evidence: evidence:a16201e58695fb75267c29ee.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:efd040cb6ee61c0492bd8b0a; evidence: evidence:1e916eeebc0ff8f212f9fd03.
- 11.7 [low] Review potential anomalies with a domain expert; do not delete statistical extremes solely because they are outliers. Finding: finding:2fca1102e35fc4169c5c0953; evidence: evidence:a6e218fc3935394674fe4c11.
- 11.7 [low] Review potential anomalies with a domain expert; do not delete statistical extremes solely because they are outliers. Finding: finding:da77c09405ce0b6a1529e4e5; evidence: evidence:efd675a6196ddd2a8d50c782.
