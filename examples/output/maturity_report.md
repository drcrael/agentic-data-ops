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

- uniqueness/duplicate\_records: 1 (FAIL, full); evidence evidence:f2cdcda37101ead4d3c0e69c.
- completeness/missing\_identifier: 1 (WARNING, full); evidence evidence:3dbfb6238b57b1c535fcf2e3.
- uniqueness/duplicate\_candidate\_identifier: 1 (WARNING, full); evidence evidence:3dbfb6238b57b1c535fcf2e3.
- conformity/whitespace\_inconsistency: 0 (PASS, full); evidence evidence:3dbfb6238b57b1c535fcf2e3.
- consistency/casing\_inconsistency: 0 (PASS, full); evidence evidence:3dbfb6238b57b1c535fcf2e3.
- validity/invalid\_or\_ambiguous\_dates: 0 (PASS, full); evidence evidence:3dbfb6238b57b1c535fcf2e3.
- consistency/mixed\_physical\_types: 1 (FAIL, full); evidence evidence:3dbfb6238b57b1c535fcf2e3.
- validity/nonfinite\_values: 0 (PASS, full); evidence evidence:3dbfb6238b57b1c535fcf2e3.
- accuracy_proxies/potential\_anomaly\_iqr: 0 (PASS, full); evidence evidence:3dbfb6238b57b1c535fcf2e3.
- accuracy_proxies/potential\_anomaly\_mad: 0 (PASS, full); evidence evidence:3dbfb6238b57b1c535fcf2e3.
- accuracy_proxies/potential\_anomaly\_length\_iqr: 0 (PASS, full); evidence evidence:3dbfb6238b57b1c535fcf2e3.
- accuracy_proxies/potential\_anomaly\_rare\_categories: 0 (PASS, full); evidence evidence:3dbfb6238b57b1c535fcf2e3.
- completeness/missing\_values: 0 (PASS, full); evidence evidence:9053252796c047b3a919ea72.
- conformity/whitespace\_inconsistency: 1 (FAIL, full); evidence evidence:9053252796c047b3a919ea72.
- consistency/casing\_inconsistency: 0 (PASS, full); evidence evidence:9053252796c047b3a919ea72.
- validity/invalid\_or\_ambiguous\_dates: 0 (PASS, full); evidence evidence:9053252796c047b3a919ea72.
- consistency/mixed\_physical\_types: 0 (PASS, full); evidence evidence:9053252796c047b3a919ea72.
- validity/nonfinite\_values: 0 (PASS, full); evidence evidence:9053252796c047b3a919ea72.
- accuracy_proxies/potential\_anomaly\_length\_iqr: 1 (WARNING, full); evidence evidence:9053252796c047b3a919ea72.
- accuracy_proxies/potential\_anomaly\_rare\_categories: 0 (PASS, full); evidence evidence:9053252796c047b3a919ea72.
- completeness/missing\_values: 0 (PASS, full); evidence evidence:c10382eed0087052de6d28a7.
- conformity/whitespace\_inconsistency: 0 (PASS, full); evidence evidence:c10382eed0087052de6d28a7.
- consistency/casing\_inconsistency: 4 (FAIL, full); evidence evidence:c10382eed0087052de6d28a7.
- validity/invalid\_or\_ambiguous\_dates: 0 (PASS, full); evidence evidence:c10382eed0087052de6d28a7.
- consistency/mixed\_physical\_types: 0 (PASS, full); evidence evidence:c10382eed0087052de6d28a7.
- validity/nonfinite\_values: 0 (PASS, full); evidence evidence:c10382eed0087052de6d28a7.
- accuracy_proxies/potential\_anomaly\_length\_iqr: 0 (PASS, full); evidence evidence:c10382eed0087052de6d28a7.
- accuracy_proxies/potential\_anomaly\_rare\_categories: 0 (PASS, full); evidence evidence:c10382eed0087052de6d28a7.
- completeness/missing\_values: 0 (PASS, full); evidence evidence:0762a99e348ef5663fdf9d2b.
- conformity/whitespace\_inconsistency: 1 (FAIL, full); evidence evidence:0762a99e348ef5663fdf9d2b.
- consistency/casing\_inconsistency: 4 (FAIL, full); evidence evidence:0762a99e348ef5663fdf9d2b.
- validity/invalid\_or\_ambiguous\_dates: 0 (PASS, full); evidence evidence:0762a99e348ef5663fdf9d2b.
- consistency/mixed\_physical\_types: 0 (PASS, full); evidence evidence:0762a99e348ef5663fdf9d2b.
- validity/nonfinite\_values: 0 (PASS, full); evidence evidence:0762a99e348ef5663fdf9d2b.
- accuracy_proxies/potential\_anomaly\_length\_iqr: 1 (WARNING, full); evidence evidence:0762a99e348ef5663fdf9d2b.
- accuracy_proxies/potential\_anomaly\_rare\_categories: 0 (PASS, full); evidence evidence:0762a99e348ef5663fdf9d2b.
- completeness/missing\_values: 0 (PASS, full); evidence evidence:beabe145cfc8fcb7b6939ddd.
- conformity/whitespace\_inconsistency: 0 (PASS, full); evidence evidence:beabe145cfc8fcb7b6939ddd.
- consistency/casing\_inconsistency: 0 (PASS, full); evidence evidence:beabe145cfc8fcb7b6939ddd.
- validity/invalid\_or\_ambiguous\_dates: 3 (WARNING, full); evidence evidence:beabe145cfc8fcb7b6939ddd.
- consistency/mixed\_physical\_types: 3 (FAIL, full); evidence evidence:beabe145cfc8fcb7b6939ddd.
- validity/nonfinite\_values: 0 (PASS, full); evidence evidence:beabe145cfc8fcb7b6939ddd.
- accuracy_proxies/potential\_anomaly\_length\_iqr: 0 (PASS, full); evidence evidence:beabe145cfc8fcb7b6939ddd.
- accuracy_proxies/potential\_anomaly\_rare\_categories: 0 (PASS, full); evidence evidence:beabe145cfc8fcb7b6939ddd.
- integrity/integrity\_unresolved: UNDETERMINED (UNDETERMINED, metadata); evidence evidence:70e850ba0121b7494be29522.
- timeliness/timeliness\_unresolved: UNDETERMINED (UNDETERMINED, metadata); evidence evidence:70e850ba0121b7494be29522.
- semantic_clarity/semantic\_clarity\_unresolved: UNDETERMINED (UNDETERMINED, metadata); evidence evidence:70e850ba0121b7494be29522.
- provenance/provenance\_unresolved: UNDETERMINED (UNDETERMINED, metadata); evidence evidence:70e850ba0121b7494be29522.
- governance/governance\_unresolved: UNDETERMINED (UNDETERMINED, metadata); evidence evidence:70e850ba0121b7494be29522.

## Semantic Assessment

### Customers

- **INFERRED** customer\_id likely represents identifier; evidence evidence:3dbfb6238b57b1c535fcf2e3.
- **UNRESOLVED** definition cannot be established from supplied evidence; evidence evidence:3dbfb6238b57b1c535fcf2e3.
- **INFERRED** customer\_name likely represents name; evidence evidence:9053252796c047b3a919ea72.
- **UNRESOLVED** definition cannot be established from supplied evidence; evidence evidence:9053252796c047b3a919ea72.
- **INFERRED** state likely represents category; evidence evidence:c10382eed0087052de6d28a7.
- **UNRESOLVED** definition cannot be established from supplied evidence; evidence evidence:c10382eed0087052de6d28a7.
- **INFERRED** status likely represents status; evidence evidence:0762a99e348ef5663fdf9d2b.
- **UNRESOLVED** definition cannot be established from supplied evidence; evidence evidence:0762a99e348ef5663fdf9d2b.
- **UNRESOLVED** code definitions cannot be established from supplied evidence; evidence evidence:0762a99e348ef5663fdf9d2b.
- **INFERRED** created\_at likely represents timestamp; evidence evidence:beabe145cfc8fcb7b6939ddd.
- **UNRESOLVED** definition cannot be established from supplied evidence; evidence evidence:beabe145cfc8fcb7b6939ddd.
- **UNRESOLVED** temporal semantics cannot be established from supplied evidence; evidence evidence:beabe145cfc8fcb7b6939ddd.

## Relationships

### Customers


## Governance Assessment

### Customers

- owner: UNRESOLVED; evidence evidence:f79dcb311b2369bf3e158905.
- steward: UNRESOLVED; evidence evidence:0c50fda449a7ca0912ce4910.
- authoritative_source: UNRESOLVED; evidence evidence:87d967c7d25a64ac28cc804b.
- source_system: UNRESOLVED; evidence evidence:6da56839e1b9e566ac970f88.
- provenance: UNRESOLVED; evidence evidence:756d0fefb1cced68e118b8a1.
- lineage: UNRESOLVED; evidence evidence:e75f22880dca5bff3eff0b0f.
- sensitivity: UNRESOLVED; evidence evidence:80dbc52b4ea54283fc53bf7a.
- security_classification: UNRESOLVED; evidence evidence:e5fd2dcd1bd4654f636515fd.
- access_constraints: UNRESOLVED; evidence evidence:34b33d80813283a52a6803a2.
- retention: UNRESOLVED; evidence evidence:f8af6e9792d27b7198f8cd0a.
- update_cadence: UNRESOLVED; evidence evidence:0619fc186b616aa5aae0cdaa.
- version: UNRESOLVED; evidence evidence:2da75764975ff8623f11b74d.
- licensing: UNRESOLVED; evidence evidence:da8878588e842bfd00d87547.
- quality_accountability: UNRESOLVED; evidence evidence:0c51d44daff02618bd5aab3f.

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

- finding:fd499fd5fc242e90f09d1379: [high/OBSERVED/OPEN] duplicate records in measured scope; review source evidence. Evidence: evidence:f2cdcda37101ead4d3c0e69c.
- finding:850bce205d0d29a326d3c637: [high/INFERRED/OPEN] missing identifier in measured scope; review source evidence. Evidence: evidence:3dbfb6238b57b1c535fcf2e3.
- finding:519536cac6d39dbbd493afb3: [high/INFERRED/OPEN] duplicate candidate identifier in measured scope; review source evidence. Evidence: evidence:3dbfb6238b57b1c535fcf2e3.
- finding:b87bc9df10bf12ab65b106a8: [high/OBSERVED/OPEN] mixed physical types in measured scope; review source evidence. Evidence: evidence:3dbfb6238b57b1c535fcf2e3.
- finding:59bf15dddabcf27efb2af5eb: [high/OBSERVED/OPEN] whitespace inconsistency in measured scope; review source evidence. Evidence: evidence:9053252796c047b3a919ea72.
- finding:439905cc3e3b800959366b89: [high/OBSERVED/OPEN] casing inconsistency in measured scope; review source evidence. Evidence: evidence:c10382eed0087052de6d28a7.
- finding:7940d984f4ccec0120df2c72: [high/OBSERVED/OPEN] whitespace inconsistency in measured scope; review source evidence. Evidence: evidence:0762a99e348ef5663fdf9d2b.
- finding:90f4c807b44497e68e9b7359: [high/OBSERVED/OPEN] casing inconsistency in measured scope; review source evidence. Evidence: evidence:0762a99e348ef5663fdf9d2b.
- finding:a1cd355b99256fa77f0074cc: [high/INFERRED/OPEN] invalid or ambiguous dates in measured scope; review source evidence. Evidence: evidence:beabe145cfc8fcb7b6939ddd.
- finding:78209f737241b4f63d907144: [high/OBSERVED/OPEN] mixed physical types in measured scope; review source evidence. Evidence: evidence:beabe145cfc8fcb7b6939ddd.
- finding:8eb0556b69812d0729b34ca0: [high/UNRESOLVED/OPEN] code definitions cannot be established from supplied evidence Evidence: evidence:0762a99e348ef5663fdf9d2b.
- finding:78b6a75cc0ef561e07c1ccc7: [high/UNRESOLVED/OPEN] temporal semantics cannot be established from supplied evidence Evidence: evidence:beabe145cfc8fcb7b6939ddd.
- finding:5725d06e94f7d0d3ef6b3d56: [high/UNRESOLVED/OPEN] governance owner cannot be established from supplied evidence Evidence: evidence:f79dcb311b2369bf3e158905.
- finding:b799423fd9b083b7e3809a51: [high/UNRESOLVED/OPEN] governance authoritative source cannot be established from supplied evidence Evidence: evidence:87d967c7d25a64ac28cc804b.
- finding:33f4f57b73a91ff220d3f950: [high/UNRESOLVED/OPEN] governance security classification cannot be established from supplied evidence Evidence: evidence:e5fd2dcd1bd4654f636515fd.

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

- 36.7 [high] Review variants against original values; approve a canonical mapping and enforce it during ingestion. Finding: finding:439905cc3e3b800959366b89; evidence: evidence:c10382eed0087052de6d28a7.
- 36.7 [high] Review variants against original values; approve a canonical mapping and enforce it during ingestion. Finding: finding:90f4c807b44497e68e9b7359; evidence: evidence:0762a99e348ef5663fdf9d2b.
- 35.0 [high] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:5725d06e94f7d0d3ef6b3d56; evidence: evidence:f79dcb311b2369bf3e158905.
- 35.0 [high] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:b799423fd9b083b7e3809a51; evidence: evidence:87d967c7d25a64ac28cc804b.
- 35.0 [high] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:8eb0556b69812d0729b34ca0; evidence: evidence:0762a99e348ef5663fdf9d2b.
- 35.0 [high] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:33f4f57b73a91ff220d3f950; evidence: evidence:e5fd2dcd1bd4654f636515fd.
- 35.0 [high] Review variants against original values; approve a canonical mapping and enforce it during ingestion. Finding: finding:78209f737241b4f63d907144; evidence: evidence:beabe145cfc8fcb7b6939ddd.
- 35.0 [high] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:78b6a75cc0ef561e07c1ccc7; evidence: evidence:beabe145cfc8fcb7b6939ddd.
- 35.0 [high] Review failing records against the explicit rule or field definition; correct from an authoritative source and rerun validation. Finding: finding:a1cd355b99256fa77f0074cc; evidence: evidence:beabe145cfc8fcb7b6939ddd.
- 31.7 [high] Review variants against original values; approve a canonical mapping and enforce it during ingestion. Finding: finding:b87bc9df10bf12ab65b106a8; evidence: evidence:3dbfb6238b57b1c535fcf2e3.
- 31.7 [high] Define a canonical representation with the owner and validate formatting at ingestion; preserve original values in lineage. Finding: finding:7940d984f4ccec0120df2c72; evidence: evidence:0762a99e348ef5663fdf9d2b.
- 31.7 [high] Confirm entity granularity and key authority; quarantine duplicates for owner review before deduplicating. Finding: finding:fd499fd5fc242e90f09d1379; evidence: evidence:f2cdcda37101ead4d3c0e69c.
- 31.7 [high] Confirm requiredness and obtain missing values from the authoritative source; add a not-null rule only after approval. Finding: finding:850bce205d0d29a326d3c637; evidence: evidence:3dbfb6238b57b1c535fcf2e3.
- 31.7 [high] Confirm entity granularity and key authority; quarantine duplicates for owner review before deduplicating. Finding: finding:519536cac6d39dbbd493afb3; evidence: evidence:3dbfb6238b57b1c535fcf2e3.
- 31.7 [high] Define a canonical representation with the owner and validate formatting at ingestion; preserve original values in lineage. Finding: finding:59bf15dddabcf27efb2af5eb; evidence: evidence:9053252796c047b3a919ea72.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:5914f4c8a75711a7e07c63d6; evidence: evidence:0c51d44daff02618bd5aab3f.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:bb7552d82ecae73dc26593e6; evidence: evidence:0619fc186b616aa5aae0cdaa.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:311d35157b5827799fa5969e; evidence: evidence:80dbc52b4ea54283fc53bf7a.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:f664d4872f6912c580b6fb93; evidence: evidence:756d0fefb1cced68e118b8a1.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:6409bba33b5a78b8e1e62bb2; evidence: evidence:2da75764975ff8623f11b74d.
- 25.0 [medium] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:3c257ad6732cd27bd31b9c4a; evidence: evidence:beabe145cfc8fcb7b6939ddd.
- 25.0 [medium] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:abff3db953aa7b1e57bc7ec7; evidence: evidence:c10382eed0087052de6d28a7.
- 25.0 [medium] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:180da86ca1343f544cf291af; evidence: evidence:3dbfb6238b57b1c535fcf2e3.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:26b3823513a0631cdb40249d; evidence: evidence:da8878588e842bfd00d87547.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:cf3d51356b5de19270acc538; evidence: evidence:0c50fda449a7ca0912ce4910.
- 25.0 [medium] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:07594156edb8d62cbe5584a8; evidence: evidence:9053252796c047b3a919ea72.
- 25.0 [medium] Answer the linked SME question with an authoritative definition and source reference; incorporate the resolution in the proposed contract. Finding: finding:f2ec804cb8ed539a938fae73; evidence: evidence:0762a99e348ef5663fdf9d2b.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:21c595d58a73b395579264e3; evidence: evidence:f8af6e9792d27b7198f8cd0a.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:0a0616e6d1065e4e664a575c; evidence: evidence:6da56839e1b9e566ac970f88.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:3a4036c116ca12e2ef739ab1; evidence: evidence:34b33d80813283a52a6803a2.
- 25.0 [medium] Obtain the missing governance decision from the accountable owner and record authority, source reference and review date. Finding: finding:efd040cb6ee61c0492bd8b0a; evidence: evidence:e75f22880dca5bff3eff0b0f.
- 11.7 [low] Review potential anomalies with a domain expert; do not delete statistical extremes solely because they are outliers. Finding: finding:2fca1102e35fc4169c5c0953; evidence: evidence:9053252796c047b3a919ea72.
- 11.7 [low] Review potential anomalies with a domain expert; do not delete statistical extremes solely because they are outliers. Finding: finding:da77c09405ce0b6a1529e4e5; evidence: evidence:0762a99e348ef5663fdf9d2b.
