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

- uniqueness/duplicate\_records: 1 (FAIL, full); evidence evidence:d34a50b6fdd4fb39a797ebc9.
- completeness/missing\_identifier: 1 (WARNING, full); evidence evidence:ece551154c8509ee2ece44ca.
- uniqueness/duplicate\_candidate\_identifier: 1 (WARNING, full); evidence evidence:ece551154c8509ee2ece44ca.
- conformity/whitespace\_inconsistency: 0 (PASS, full); evidence evidence:ece551154c8509ee2ece44ca.
- consistency/casing\_inconsistency: 0 (PASS, full); evidence evidence:ece551154c8509ee2ece44ca.
- validity/invalid\_or\_ambiguous\_dates: 0 (PASS, full); evidence evidence:ece551154c8509ee2ece44ca.
- consistency/mixed\_physical\_types: 1 (FAIL, full); evidence evidence:ece551154c8509ee2ece44ca.
- validity/nonfinite\_values: 0 (PASS, full); evidence evidence:ece551154c8509ee2ece44ca.
- accuracy_proxies/potential\_anomaly\_iqr: 0 (PASS, full); evidence evidence:ece551154c8509ee2ece44ca.
- accuracy_proxies/potential\_anomaly\_mad: 0 (PASS, full); evidence evidence:ece551154c8509ee2ece44ca.
- accuracy_proxies/potential\_anomaly\_length\_iqr: 0 (PASS, full); evidence evidence:ece551154c8509ee2ece44ca.
- accuracy_proxies/potential\_anomaly\_rare\_categories: 0 (PASS, full); evidence evidence:ece551154c8509ee2ece44ca.
- completeness/missing\_values: 0 (PASS, full); evidence evidence:938d45faa32a2bd80830792a.
- conformity/whitespace\_inconsistency: 1 (FAIL, full); evidence evidence:938d45faa32a2bd80830792a.
- consistency/casing\_inconsistency: 0 (PASS, full); evidence evidence:938d45faa32a2bd80830792a.
- validity/invalid\_or\_ambiguous\_dates: 0 (PASS, full); evidence evidence:938d45faa32a2bd80830792a.
- consistency/mixed\_physical\_types: 0 (PASS, full); evidence evidence:938d45faa32a2bd80830792a.
- validity/nonfinite\_values: 0 (PASS, full); evidence evidence:938d45faa32a2bd80830792a.
- accuracy_proxies/potential\_anomaly\_length\_iqr: 1 (WARNING, full); evidence evidence:938d45faa32a2bd80830792a.
- accuracy_proxies/potential\_anomaly\_rare\_categories: 0 (PASS, full); evidence evidence:938d45faa32a2bd80830792a.
- completeness/missing\_values: 0 (PASS, full); evidence evidence:a357a02d6609b91377107440.
- conformity/whitespace\_inconsistency: 0 (PASS, full); evidence evidence:a357a02d6609b91377107440.
- consistency/casing\_inconsistency: 4 (FAIL, full); evidence evidence:a357a02d6609b91377107440.
- validity/invalid\_or\_ambiguous\_dates: 0 (PASS, full); evidence evidence:a357a02d6609b91377107440.
- consistency/mixed\_physical\_types: 0 (PASS, full); evidence evidence:a357a02d6609b91377107440.
- validity/nonfinite\_values: 0 (PASS, full); evidence evidence:a357a02d6609b91377107440.
- accuracy_proxies/potential\_anomaly\_length\_iqr: 0 (PASS, full); evidence evidence:a357a02d6609b91377107440.
- accuracy_proxies/potential\_anomaly\_rare\_categories: 0 (PASS, full); evidence evidence:a357a02d6609b91377107440.
- completeness/missing\_values: 0 (PASS, full); evidence evidence:fe5074569d3d66692a37e142.
- conformity/whitespace\_inconsistency: 1 (FAIL, full); evidence evidence:fe5074569d3d66692a37e142.
- consistency/casing\_inconsistency: 4 (FAIL, full); evidence evidence:fe5074569d3d66692a37e142.
- validity/invalid\_or\_ambiguous\_dates: 0 (PASS, full); evidence evidence:fe5074569d3d66692a37e142.
- consistency/mixed\_physical\_types: 0 (PASS, full); evidence evidence:fe5074569d3d66692a37e142.
- validity/nonfinite\_values: 0 (PASS, full); evidence evidence:fe5074569d3d66692a37e142.
- accuracy_proxies/potential\_anomaly\_length\_iqr: 1 (WARNING, full); evidence evidence:fe5074569d3d66692a37e142.
- accuracy_proxies/potential\_anomaly\_rare\_categories: 0 (PASS, full); evidence evidence:fe5074569d3d66692a37e142.
- completeness/missing\_values: 0 (PASS, full); evidence evidence:33aa23d0ec82d62668e0a41d.
- conformity/whitespace\_inconsistency: 0 (PASS, full); evidence evidence:33aa23d0ec82d62668e0a41d.
- consistency/casing\_inconsistency: 0 (PASS, full); evidence evidence:33aa23d0ec82d62668e0a41d.
- validity/invalid\_or\_ambiguous\_dates: 3 (WARNING, full); evidence evidence:33aa23d0ec82d62668e0a41d.
- consistency/mixed\_physical\_types: 3 (FAIL, full); evidence evidence:33aa23d0ec82d62668e0a41d.
- validity/nonfinite\_values: 0 (PASS, full); evidence evidence:33aa23d0ec82d62668e0a41d.
- accuracy_proxies/potential\_anomaly\_length\_iqr: 0 (PASS, full); evidence evidence:33aa23d0ec82d62668e0a41d.
- accuracy_proxies/potential\_anomaly\_rare\_categories: 0 (PASS, full); evidence evidence:33aa23d0ec82d62668e0a41d.
- integrity/integrity\_unresolved: UNDETERMINED (UNDETERMINED, metadata); evidence evidence:3e8794fe4c1086e2c0393cdc.
- timeliness/timeliness\_unresolved: UNDETERMINED (UNDETERMINED, metadata); evidence evidence:3e8794fe4c1086e2c0393cdc.
- semantic_clarity/semantic\_clarity\_unresolved: UNDETERMINED (UNDETERMINED, metadata); evidence evidence:3e8794fe4c1086e2c0393cdc.
- provenance/provenance\_unresolved: UNDETERMINED (UNDETERMINED, metadata); evidence evidence:3e8794fe4c1086e2c0393cdc.
- governance/governance\_unresolved: UNDETERMINED (UNDETERMINED, metadata); evidence evidence:3e8794fe4c1086e2c0393cdc.

## Semantic Assessment

### Customers

- **INFERRED** customer\_id likely represents identifier; evidence evidence:ece551154c8509ee2ece44ca.
- **UNRESOLVED** definition cannot be established from supplied evidence; evidence evidence:ece551154c8509ee2ece44ca.
- **INFERRED** customer\_name likely represents name; evidence evidence:938d45faa32a2bd80830792a.
- **UNRESOLVED** definition cannot be established from supplied evidence; evidence evidence:938d45faa32a2bd80830792a.
- **INFERRED** state likely represents category; evidence evidence:a357a02d6609b91377107440.
- **UNRESOLVED** definition cannot be established from supplied evidence; evidence evidence:a357a02d6609b91377107440.
- **INFERRED** status likely represents status; evidence evidence:fe5074569d3d66692a37e142.
- **UNRESOLVED** definition cannot be established from supplied evidence; evidence evidence:fe5074569d3d66692a37e142.
- **UNRESOLVED** code definitions cannot be established from supplied evidence; evidence evidence:fe5074569d3d66692a37e142.
- **INFERRED** created\_at likely represents timestamp; evidence evidence:33aa23d0ec82d62668e0a41d.
- **UNRESOLVED** definition cannot be established from supplied evidence; evidence evidence:33aa23d0ec82d62668e0a41d.
- **UNRESOLVED** temporal semantics cannot be established from supplied evidence; evidence evidence:33aa23d0ec82d62668e0a41d.

## Relationships

### Customers


## Governance Assessment

### Customers

- owner: UNRESOLVED; evidence evidence:0a290b42b3aa723c14fa392a.
- steward: UNRESOLVED; evidence evidence:cebc94d70dc2979c996ca095.
- authoritative_source: UNRESOLVED; evidence evidence:b4cbb96592517d3cb8bdacfc.
- source_system: UNRESOLVED; evidence evidence:f4f0778fda9235969fc1a717.
- provenance: UNRESOLVED; evidence evidence:b81f969569339544f2ed782a.
- lineage: UNRESOLVED; evidence evidence:e4e20ed96f3520d598b39642.
- sensitivity: UNRESOLVED; evidence evidence:294321b16a7f210045857e18.
- security_classification: UNRESOLVED; evidence evidence:7b46ce97079f643659fbfd8e.
- access_constraints: UNRESOLVED; evidence evidence:651009fa78ab468c36a1e410.
- retention: UNRESOLVED; evidence evidence:1fc2a6dcc07ab9a5f617ede5.
- update_cadence: UNRESOLVED; evidence evidence:7c35e52117932581ead9d839.
- version: UNRESOLVED; evidence evidence:82426fd7279da7c58567b45f.
- licensing: UNRESOLVED; evidence evidence:f57c438cf5e28751f7285208.
- quality_accountability: UNRESOLVED; evidence evidence:32764e398f5d083a029bf3b7.

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

- finding:fd499fd5fc242e90f09d1379: [high/OBSERVED/OPEN] duplicate records in measured scope; review source evidence. Evidence: evidence:d34a50b6fdd4fb39a797ebc9.
- finding:850bce205d0d29a326d3c637: [high/INFERRED/OPEN] missing identifier in measured scope; review source evidence. Evidence: evidence:ece551154c8509ee2ece44ca.
- finding:519536cac6d39dbbd493afb3: [high/INFERRED/OPEN] duplicate candidate identifier in measured scope; review source evidence. Evidence: evidence:ece551154c8509ee2ece44ca.
- finding:b87bc9df10bf12ab65b106a8: [high/OBSERVED/OPEN] mixed physical types in measured scope; review source evidence. Evidence: evidence:ece551154c8509ee2ece44ca.
- finding:59bf15dddabcf27efb2af5eb: [high/OBSERVED/OPEN] whitespace inconsistency in measured scope; review source evidence. Evidence: evidence:938d45faa32a2bd80830792a.
- finding:439905cc3e3b800959366b89: [high/OBSERVED/OPEN] casing inconsistency in measured scope; review source evidence. Evidence: evidence:a357a02d6609b91377107440.
- finding:7940d984f4ccec0120df2c72: [high/OBSERVED/OPEN] whitespace inconsistency in measured scope; review source evidence. Evidence: evidence:fe5074569d3d66692a37e142.
- finding:90f4c807b44497e68e9b7359: [high/OBSERVED/OPEN] casing inconsistency in measured scope; review source evidence. Evidence: evidence:fe5074569d3d66692a37e142.
- finding:a1cd355b99256fa77f0074cc: [high/INFERRED/OPEN] invalid or ambiguous dates in measured scope; review source evidence. Evidence: evidence:33aa23d0ec82d62668e0a41d.
- finding:78209f737241b4f63d907144: [high/OBSERVED/OPEN] mixed physical types in measured scope; review source evidence. Evidence: evidence:33aa23d0ec82d62668e0a41d.
- finding:8eb0556b69812d0729b34ca0: [high/UNRESOLVED/OPEN] code definitions cannot be established from supplied evidence Evidence: evidence:fe5074569d3d66692a37e142.
- finding:78b6a75cc0ef561e07c1ccc7: [high/UNRESOLVED/OPEN] temporal semantics cannot be established from supplied evidence Evidence: evidence:33aa23d0ec82d62668e0a41d.
- finding:5725d06e94f7d0d3ef6b3d56: [high/UNRESOLVED/OPEN] governance owner cannot be established from supplied evidence Evidence: evidence:0a290b42b3aa723c14fa392a.
- finding:b799423fd9b083b7e3809a51: [high/UNRESOLVED/OPEN] governance authoritative source cannot be established from supplied evidence Evidence: evidence:b4cbb96592517d3cb8bdacfc.
- finding:33f4f57b73a91ff220d3f950: [high/UNRESOLVED/OPEN] governance security classification cannot be established from supplied evidence Evidence: evidence:7b46ce97079f643659fbfd8e.

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

- 36.7 [high] Review variants against original values; approve a canonical mapping and enforce it during ingestion. Finding: finding:439905cc3e3b800959366b89; evidence: evidence:a357a02d6609b91377107440.
- 36.7 [high] Review variants against original values; approve a canonical mapping and enforce it during ingestion. Finding: finding:90f4c807b44497e68e9b7359; evidence: evidence:fe5074569d3d66692a37e142.
- 35.0 [high] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:5725d06e94f7d0d3ef6b3d56; evidence: evidence:0a290b42b3aa723c14fa392a.
- 35.0 [high] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:b799423fd9b083b7e3809a51; evidence: evidence:b4cbb96592517d3cb8bdacfc.
- 35.0 [high] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:8eb0556b69812d0729b34ca0; evidence: evidence:fe5074569d3d66692a37e142.
- 35.0 [high] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:33f4f57b73a91ff220d3f950; evidence: evidence:7b46ce97079f643659fbfd8e.
- 35.0 [high] Review variants against original values; approve a canonical mapping and enforce it during ingestion. Finding: finding:78209f737241b4f63d907144; evidence: evidence:33aa23d0ec82d62668e0a41d.
- 35.0 [high] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:78b6a75cc0ef561e07c1ccc7; evidence: evidence:33aa23d0ec82d62668e0a41d.
- 35.0 [high] Review failing records against the explicit rule or field definition; correct from an authoritative source and rerun validation. Finding: finding:a1cd355b99256fa77f0074cc; evidence: evidence:33aa23d0ec82d62668e0a41d.
- 31.7 [high] Review variants against original values; approve a canonical mapping and enforce it during ingestion. Finding: finding:b87bc9df10bf12ab65b106a8; evidence: evidence:ece551154c8509ee2ece44ca.
- 31.7 [high] Define a canonical representation with the owner and validate formatting at ingestion; preserve original values in lineage. Finding: finding:7940d984f4ccec0120df2c72; evidence: evidence:fe5074569d3d66692a37e142.
- 31.7 [high] Confirm entity granularity and key authority; quarantine duplicates for owner review before deduplicating. Finding: finding:fd499fd5fc242e90f09d1379; evidence: evidence:d34a50b6fdd4fb39a797ebc9.
- 31.7 [high] Confirm requiredness and obtain missing values from the authoritative source; add a not-null rule only after approval. Finding: finding:850bce205d0d29a326d3c637; evidence: evidence:ece551154c8509ee2ece44ca.
- 31.7 [high] Confirm entity granularity and key authority; quarantine duplicates for owner review before deduplicating. Finding: finding:519536cac6d39dbbd493afb3; evidence: evidence:ece551154c8509ee2ece44ca.
- 31.7 [high] Define a canonical representation with the owner and validate formatting at ingestion; preserve original values in lineage. Finding: finding:59bf15dddabcf27efb2af5eb; evidence: evidence:938d45faa32a2bd80830792a.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:5914f4c8a75711a7e07c63d6; evidence: evidence:32764e398f5d083a029bf3b7.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:bb7552d82ecae73dc26593e6; evidence: evidence:7c35e52117932581ead9d839.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:311d35157b5827799fa5969e; evidence: evidence:294321b16a7f210045857e18.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:f664d4872f6912c580b6fb93; evidence: evidence:b81f969569339544f2ed782a.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:6409bba33b5a78b8e1e62bb2; evidence: evidence:82426fd7279da7c58567b45f.
- 25.0 [medium] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:3c257ad6732cd27bd31b9c4a; evidence: evidence:33aa23d0ec82d62668e0a41d.
- 25.0 [medium] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:abff3db953aa7b1e57bc7ec7; evidence: evidence:a357a02d6609b91377107440.
- 25.0 [medium] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:180da86ca1343f544cf291af; evidence: evidence:ece551154c8509ee2ece44ca.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:26b3823513a0631cdb40249d; evidence: evidence:f57c438cf5e28751f7285208.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:cf3d51356b5de19270acc538; evidence: evidence:cebc94d70dc2979c996ca095.
- 25.0 [medium] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:07594156edb8d62cbe5584a8; evidence: evidence:938d45faa32a2bd80830792a.
- 25.0 [medium] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:f2ec804cb8ed539a938fae73; evidence: evidence:fe5074569d3d66692a37e142.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:21c595d58a73b395579264e3; evidence: evidence:1fc2a6dcc07ab9a5f617ede5.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:0a0616e6d1065e4e664a575c; evidence: evidence:f4f0778fda9235969fc1a717.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:3a4036c116ca12e2ef739ab1; evidence: evidence:651009fa78ab468c36a1e410.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:efd040cb6ee61c0492bd8b0a; evidence: evidence:e4e20ed96f3520d598b39642.
- 11.7 [low] Review potential anomalies with a domain expert; do not delete statistical extremes solely because they are outliers. Finding: finding:2fca1102e35fc4169c5c0953; evidence: evidence:938d45faa32a2bd80830792a.
- 11.7 [low] Review potential anomalies with a domain expert; do not delete statistical extremes solely because they are outliers. Finding: finding:da77c09405ce0b6a1529e4e5; evidence: evidence:fe5074569d3d66692a37e142.
