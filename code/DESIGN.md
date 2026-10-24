# Sample-output evidence design

This document traces every object in dataset/sample_output.csv to participant-visible evidence and policy. Evidence IDs resolve through dataset/evidence_files.csv. SQL line references mean the relevant INSERT or, for absence, the complete snapshot table scan. Empty evidence IDs are intentional future-work steps.

## Contract-derived findings

- COMPLETE rows contain only evidence-backed verification steps.
- Every INCOMPLETE finding cites an evidence ID; every INCOMPLETE remediation and verification uses an empty evidence_id, including checks of resources already clean at audit time.
- Evidence selection is subject- and system-specific: generally the latest relevant capture at or before audit_at, not the latest file globally.

## Hypothesis checks

### Latest capture rule — confirmed for the samples

Case_03 uses evidence_94 (2026-09-26 10:38:56Z) before its 11:00Z audit. Case_04 uses evidence_54 for the account and evidence_56 for analytics before the 2026-09-07 10:20Z audit. Cases 27-28 use evidence_92 before their 2026-09-15 12:00Z audits. Case_31 uses evidence_51 captured exactly at its audit. This is the latest relevant capture, not necessarily the repository's latest capture.

### INCOMPLETE evidence IDs — confirmed

Cases 05-20, 22-24, 29-30, and 32 have evidence IDs only on FINDING steps. Their REMEDIATION and VERIFICATION objects use an empty evidence_id.

### Already-clean verification in INCOMPLETE cases — confirmed

Many incomplete cases verify accounts, retained audits, blocked backups, disabled flows, or other already-compliant resources. Case_10 explicitly verifies account_010 as absent while support_002 remains.

### Retained security audit records — confirmed

VERIFY_RECORD_PRESENT on security_service appears exactly in cases 03, 09, and 11-32. These map to rule_12.

### Remediation order — partially refuted

Flows and restore controls precede record changes, but the samples then order by operation class DELETE, REDACT, ANONYMIZE rather than globally by system_id. Case_11 is decisive: data_flow_9522, search_052 DELETE, support_864 REDACT, analytics_2034 ANONYMIZE. Within an operation class, system/resource ordering is consistent.

## Identity-to-resource resolution

Resolve current and historical identifiers first, then match resource payloads by email, user_id, customer_reference, subject_reference, hashes, or source references. Do not assume every numeric suffix equals the user number.

| Subject | Evidence-backed mapping |
|---|---|
| user_05 | account_005 in evidence_54 SQL; failover row contains the direct identifiers. |
| user_06 | account_006 is the source_resource_id of search_001 in evidence_57 SQL. |
| user_07 | support_001 is the subject-only delivery attachment in evidence_58; account verification is account_007. |
| user_08 | export_001 is the export resource in evidence_59; account verification is account_008. |
| user_10 | support_002 is located by nadia.ionescu@yahoo.com in evidence_61; account verification is account_010. |
| user_17 | tombstone_17 is the stable-reference record in the identity-service evidence/activity. |

## FAILED/PARTIAL claims and replica drift

Reported workflow results are claims, not state proof. Evidence contradicts the reported state in case_05 (COMPLETE but account_005 present, evidence_54), case_06 (PARTIALLY_COMPLETE but search_001 present, evidence_57), case_08 (PARTIALLY_COMPLETE but export_001 present, evidence_59), case_10 (COMPLETE but support_002 remains, evidence_61), case_12 (COMPLETE but analytics_9914 found, evidence_01), and case_15 (COMPLETE but data_flow_9846 enabled, evidence_01).

Replica drift is explicit in evidence_54: account_005 exists in customer_profiles_failover_replica but not customer_profiles_primary. A primary deletion claim therefore cannot establish global absence. Compare primary/read/failover tables at capture time and report any still-present downstream copy.

## Rules not fully explainable from the samples

- rule_02 SECONDARY_IDENTIFIER, rule_04 CACHE_ENTRY, rule_08 PRODUCT_TELEMETRY, rule_10 MARKETING_PROFILE, rule_11 EMAIL_DELIVERY_LOG, and rule_13 LEGAL_HOLD_RECORD have no independently identifiable sample step.
- integration_service flows have no direct deletion_rules.csv row; disabling them is a recreation-prevention prerequisite from the project contract.
- support_002 is not typed MESSAGE vs ATTACHMENT in its supplied evidence, so its DELETE operation cannot be uniquely justified by rule_05 versus rule_06.
- case_12 analytics_9914 uses DELETE_RECORD although rules_07/08 require ANONYMIZE when attributable.

## Per-step trace

Each row below shows the exact expected step, evidence file/row, rule, and evidence-ID rationale.

### case_01 — COMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | VERIFICATION | account_service / account_001 | VERIFY_RECORD_ABSENT / ABSENT | evidence_54 evidence/databases/customer_accounts_failover_replica_20260902.sql captured 2026-09-02T23:00:00Z; SQL table scan has no literal account_001 row (absence is the evidence) | rule_01 USER_PROFILE -> DELETE; participant-visible finding/current verification |

### case_02 — COMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | VERIFICATION | account_service / account_002 | VERIFY_RECORD_ABSENT / ABSENT | evidence_54 evidence/databases/customer_accounts_failover_replica_20260902.sql captured 2026-09-02T23:00:00Z; SQL table scan has no literal account_002 row (absence is the evidence) | rule_01 USER_PROFILE -> DELETE; participant-visible finding/current verification |

### case_03 — COMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | VERIFICATION | account_service / account_7566 | VERIFY_RECORD_ABSENT / ABSENT | evidence_94 evidence/logs/resource_lookup_trace_20260926_103856.log captured 2026-09-26T10:38:56Z, line(s) 18,19 | rule_01 USER_PROFILE -> DELETE; participant-visible finding/current verification |
| 2 | VERIFICATION | security_service / audit_record_2016 | VERIFY_RECORD_PRESENT / PRESENT | evidence_94 evidence/logs/resource_lookup_trace_20260926_103856.log captured 2026-09-26T10:38:56Z, line(s) 34,35 | rule_12 SECURITY_AUDIT_LOG -> RETAIN; participant-visible finding/current verification |
| 3 | VERIFICATION | analytics_platform / analytics_9406 | VERIFY_RECORD_ANONYMIZED / ANONYMIZED | evidence_94 evidence/logs/resource_lookup_trace_20260926_103856.log captured 2026-09-26T10:38:56Z, line(s) 42,43 | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; participant-visible finding/current verification |

### case_04 — COMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | VERIFICATION | account_service / account_004 | VERIFY_RECORD_ABSENT / ABSENT | evidence_54 evidence/databases/customer_accounts_failover_replica_20260902.sql captured 2026-09-02T23:00:00Z; SQL table scan has no literal account_004 row (absence is the evidence) | rule_01 USER_PROFILE -> DELETE; participant-visible finding/current verification |
| 2 | VERIFICATION | analytics_platform / analytics_901 | VERIFY_RECORD_ANONYMIZED / ANONYMIZED | evidence_56 evidence/records/customer_analytics_report_20260907.json captured 2026-09-07T09:45:00Z, line(s) 7 | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; participant-visible finding/current verification |

### case_05 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | account_service / account_005 | REPORT_REMAINING_RECORD / PRESENT | evidence_54 evidence/databases/customer_accounts_failover_replica_20260902.sql captured 2026-09-02T23:00:00Z, line(s) 13 | rule_01 USER_PROFILE -> DELETE; participant-visible finding/current verification |
| 2 | REMEDIATION | account_service / account_005 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 3 | VERIFICATION | account_service / account_005 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |

### case_06 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | search_service / search_001 | REPORT_REMAINING_RECORD / PRESENT | evidence_57 evidence/databases/customer_search_primary_20260910.sql captured 2026-09-10T08:45:00Z, line(s) 9 | rule_03 SEARCH_INDEX_ENTRY -> DELETE; participant-visible finding/current verification |
| 2 | REMEDIATION | search_service / search_001 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 3 | VERIFICATION | account_service / account_006 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 4 | VERIFICATION | search_service / search_001 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |

### case_07 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | support_platform / support_001 | REPORT_REMAINING_RECORD / PRESENT | evidence_58 evidence/documents/delivery_correction_attachment.pdf captured 2026-09-12T07:30:00Z, line(s) 2,7 | rule_06 SUPPORT_ATTACHMENT -> DELETE; participant-visible finding/current verification |
| 2 | REMEDIATION | support_platform / support_001 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | rule_06 SUPPORT_ATTACHMENT -> DELETE; future action/check; contract requires empty evidence_id |
| 3 | VERIFICATION | account_service / account_007 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 4 | VERIFICATION | support_platform / support_001 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_06 SUPPORT_ATTACHMENT -> DELETE; future action/check; contract requires empty evidence_id |

### case_08 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | export_service / export_001 | REPORT_REMAINING_RECORD / PRESENT | evidence_59 evidence/records/customer_export_jobs_20260914.json captured 2026-09-14T15:40:00Z, line(s) 7,9 | rule_09 USER_EXPORT -> DELETE; participant-visible finding/current verification |
| 2 | REMEDIATION | export_service / export_001 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | rule_09 USER_EXPORT -> DELETE; future action/check; contract requires empty evidence_id |
| 3 | VERIFICATION | account_service / account_008 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 4 | VERIFICATION | export_service / export_001 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_09 USER_EXPORT -> DELETE; future action/check; contract requires empty evidence_id |

### case_09 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | backup_service / backup_4978 | REPORT_RESTORE_RISK / ACTIVE | evidence_93 evidence/databases/customer_data_inventory_20260916.sql captured 2026-09-16T08:37:39Z, line(s) 24 | rule_14 BACKUP_ARCHIVE -> RETAIN; block restore access; participant-visible finding/current verification |
| 2 | REMEDIATION | backup_service / backup_4978 | BLOCK_RESTORE / BLOCKED | evidence_id="" by contract: future remediation/verification | rule_14 BACKUP_ARCHIVE -> RETAIN; block restore access; future action/check; contract requires empty evidence_id |
| 3 | VERIFICATION | account_service / account_3960 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 4 | VERIFICATION | security_service / audit_record_4902 | VERIFY_RECORD_PRESENT / PRESENT | evidence_id="" by contract: future remediation/verification | rule_12 SECURITY_AUDIT_LOG -> RETAIN; future action/check; contract requires empty evidence_id |
| 5 | VERIFICATION | backup_service / backup_4978 | VERIFY_RESTORE_BLOCKED / BLOCKED | evidence_id="" by contract: future remediation/verification | rule_14 BACKUP_ARCHIVE -> RETAIN; block restore access; future action/check; contract requires empty evidence_id |

### case_10 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | support_platform / support_002 | REPORT_REMAINING_RECORD / PRESENT | evidence_61 evidence/logs/support_replica.log captured 2026-09-17T22:00:19Z, line(s) 5,6 | UNRESOLVED: support row is not typed MESSAGE vs ATTACHMENT; participant-visible finding/current verification |
| 2 | REMEDIATION | support_platform / support_002 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | UNRESOLVED: support row is not typed MESSAGE vs ATTACHMENT; future action/check; contract requires empty evidence_id |
| 3 | VERIFICATION | account_service / account_010 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 4 | VERIFICATION | support_platform / support_002 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | UNRESOLVED: support row is not typed MESSAGE vs ATTACHMENT; future action/check; contract requires empty evidence_id |

### case_11 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | search_service / search_052 | REPORT_REMAINING_RECORD / PRESENT | evidence_03 evidence/records/customer_account_handover_20261001.txt captured 2026-10-01T12:00:00Z, line(s) 26 | rule_03 SEARCH_INDEX_ENTRY -> DELETE; participant-visible finding/current verification |
| 2 | FINDING | analytics_platform / analytics_2034 | REPORT_EXPOSED_PII / PRESENT | evidence_03 evidence/records/customer_account_handover_20261001.txt captured 2026-10-01T12:00:00Z, line(s) 16 | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; participant-visible finding/current verification |
| 3 | FINDING | support_platform / support_864 | REPORT_EXPOSED_PII / PRESENT | evidence_03 evidence/records/customer_account_handover_20261001.txt captured 2026-10-01T12:00:00Z, line(s) 46 | rule_05 SUPPORT_MESSAGE -> REDACT; participant-visible finding/current verification |
| 4 | FINDING | integration_service / data_flow_9522 | REPORT_ACTIVE_DATA_FLOW / ACTIVE | evidence_03 evidence/records/customer_account_handover_20261001.txt captured 2026-10-01T12:00:00Z, line(s) 25 | No direct deletion_rules.csv row; disable flow to prevent recreation; participant-visible finding/current verification |
| 5 | REMEDIATION | integration_service / data_flow_9522 | DISABLE_DATA_FLOW / DISABLED | evidence_id="" by contract: future remediation/verification | No direct deletion_rules.csv row; disable flow to prevent recreation; future action/check; contract requires empty evidence_id |
| 6 | REMEDIATION | search_service / search_052 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 7 | REMEDIATION | support_platform / support_864 | REDACT_RECORD / REDACTED | evidence_id="" by contract: future remediation/verification | rule_05 SUPPORT_MESSAGE -> REDACT; future action/check; contract requires empty evidence_id |
| 8 | REMEDIATION | analytics_platform / analytics_2034 | ANONYMIZE_RECORD / ANONYMIZED | evidence_id="" by contract: future remediation/verification | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; future action/check; contract requires empty evidence_id |
| 9 | VERIFICATION | account_service / account_4248 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 10 | VERIFICATION | search_service / search_052 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 11 | VERIFICATION | security_service / audit_record_9394 | VERIFY_RECORD_PRESENT / PRESENT | evidence_id="" by contract: future remediation/verification | rule_12 SECURITY_AUDIT_LOG -> RETAIN; future action/check; contract requires empty evidence_id |
| 12 | VERIFICATION | support_platform / support_864 | VERIFY_RECORD_REDACTED / REDACTED | evidence_id="" by contract: future remediation/verification | rule_05 SUPPORT_MESSAGE -> REDACT; future action/check; contract requires empty evidence_id |
| 13 | VERIFICATION | analytics_platform / analytics_2034 | VERIFY_RECORD_ANONYMIZED / ANONYMIZED | evidence_id="" by contract: future remediation/verification | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; future action/check; contract requires empty evidence_id |
| 14 | VERIFICATION | integration_service / data_flow_9522 | VERIFY_DATA_FLOW_DISABLED / DISABLED | evidence_id="" by contract: future remediation/verification | No direct deletion_rules.csv row; disable flow to prevent recreation; future action/check; contract requires empty evidence_id |

### case_12 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | analytics_platform / analytics_9914 | REPORT_REMAINING_RECORD / PRESENT | evidence_01 evidence/logs/service_events_ap_south_20260915.log captured 2026-09-15T11:59:39Z, line(s) 92 | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; participant-visible finding/current verification |
| 2 | REMEDIATION | analytics_platform / analytics_9914 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | UNRESOLVED: sample says DELETE, but rules_07/08 require ANONYMIZE; future action/check; contract requires empty evidence_id |
| 3 | VERIFICATION | account_service / account_9797 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 4 | VERIFICATION | analytics_platform / analytics_9914 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; future action/check; contract requires empty evidence_id |
| 5 | VERIFICATION | security_service / audit_record_2945 | VERIFY_RECORD_PRESENT / PRESENT | evidence_id="" by contract: future remediation/verification | rule_12 SECURITY_AUDIT_LOG -> RETAIN; future action/check; contract requires empty evidence_id |

### case_13 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | search_service / search_1308 | REPORT_REMAINING_RECORD / PRESENT | evidence_03 evidence/records/customer_account_handover_20261001.txt captured 2026-10-01T12:00:00Z, line(s) 27 | rule_03 SEARCH_INDEX_ENTRY -> DELETE; participant-visible finding/current verification |
| 2 | FINDING | support_platform / support_4218 | REPORT_REMAINING_RECORD / PRESENT | evidence_03 evidence/records/customer_account_handover_20261001.txt captured 2026-10-01T12:00:00Z, line(s) 43 | rule_06 SUPPORT_ATTACHMENT -> DELETE; participant-visible finding/current verification |
| 3 | REMEDIATION | search_service / search_1308 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 4 | REMEDIATION | support_platform / support_4218 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | rule_06 SUPPORT_ATTACHMENT -> DELETE; future action/check; contract requires empty evidence_id |
| 5 | VERIFICATION | account_service / account_9335 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 6 | VERIFICATION | search_service / search_1308 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 7 | VERIFICATION | support_platform / support_4218 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_06 SUPPORT_ATTACHMENT -> DELETE; future action/check; contract requires empty evidence_id |
| 8 | VERIFICATION | security_service / audit_record_4816 | VERIFY_RECORD_PRESENT / PRESENT | evidence_id="" by contract: future remediation/verification | rule_12 SECURITY_AUDIT_LOG -> RETAIN; future action/check; contract requires empty evidence_id |

### case_14 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | backup_service / backup_3870 | REPORT_RESTORE_RISK / ACTIVE | evidence_03 evidence/records/customer_account_handover_20261001.txt captured 2026-10-01T12:00:00Z, line(s) 19 | rule_14 BACKUP_ARCHIVE -> RETAIN; block restore access; participant-visible finding/current verification |
| 2 | REMEDIATION | backup_service / backup_3870 | BLOCK_RESTORE / BLOCKED | evidence_id="" by contract: future remediation/verification | rule_14 BACKUP_ARCHIVE -> RETAIN; block restore access; future action/check; contract requires empty evidence_id |
| 3 | VERIFICATION | account_service / account_3677 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 4 | VERIFICATION | security_service / audit_record_987 | VERIFY_RECORD_PRESENT / PRESENT | evidence_id="" by contract: future remediation/verification | rule_12 SECURITY_AUDIT_LOG -> RETAIN; future action/check; contract requires empty evidence_id |
| 5 | VERIFICATION | backup_service / backup_3870 | VERIFY_RESTORE_BLOCKED / BLOCKED | evidence_id="" by contract: future remediation/verification | rule_14 BACKUP_ARCHIVE -> RETAIN; block restore access; future action/check; contract requires empty evidence_id |

### case_15 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | integration_service / data_flow_9846 | REPORT_ACTIVE_DATA_FLOW / ACTIVE | evidence_01 evidence/logs/service_events_ap_south_20260915.log captured 2026-09-15T11:59:39Z, line(s) 88 | No direct deletion_rules.csv row; disable flow to prevent recreation; participant-visible finding/current verification |
| 2 | REMEDIATION | integration_service / data_flow_9846 | DISABLE_DATA_FLOW / DISABLED | evidence_id="" by contract: future remediation/verification | No direct deletion_rules.csv row; disable flow to prevent recreation; future action/check; contract requires empty evidence_id |
| 3 | VERIFICATION | account_service / account_4745 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 4 | VERIFICATION | security_service / audit_record_1596 | VERIFY_RECORD_PRESENT / PRESENT | evidence_id="" by contract: future remediation/verification | rule_12 SECURITY_AUDIT_LOG -> RETAIN; future action/check; contract requires empty evidence_id |
| 5 | VERIFICATION | integration_service / data_flow_9846 | VERIFY_DATA_FLOW_DISABLED / DISABLED | evidence_id="" by contract: future remediation/verification | No direct deletion_rules.csv row; disable flow to prevent recreation; future action/check; contract requires empty evidence_id |

### case_16 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | account_service / account_994 | REPORT_REMAINING_RECORD / PRESENT | evidence_05 evidence/databases/customer_data_read_replica_20260921.sql captured 2026-09-21T10:00:00Z, line(s) 52 | rule_01 USER_PROFILE -> DELETE; participant-visible finding/current verification |
| 2 | FINDING | search_service / search_1007 | REPORT_REMAINING_RECORD / PRESENT | evidence_05 evidence/databases/customer_data_read_replica_20260921.sql captured 2026-09-21T10:00:00Z, line(s) 37,75 | rule_03 SEARCH_INDEX_ENTRY -> DELETE; participant-visible finding/current verification |
| 3 | REMEDIATION | account_service / account_994 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 4 | REMEDIATION | search_service / search_1007 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 5 | VERIFICATION | account_service / account_994 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 6 | VERIFICATION | search_service / search_1007 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 7 | VERIFICATION | security_service / audit_record_9528 | VERIFY_RECORD_PRESENT / PRESENT | evidence_id="" by contract: future remediation/verification | rule_12 SECURITY_AUDIT_LOG -> RETAIN; future action/check; contract requires empty evidence_id |

### case_17 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | backup_service / backup_3245 | REPORT_RESTORE_RISK / ACTIVE | evidence_01 evidence/logs/service_events_ap_south_20260915.log captured 2026-09-15T11:59:39Z, line(s) 53 | rule_14 BACKUP_ARCHIVE -> RETAIN; block restore access; participant-visible finding/current verification |
| 2 | REMEDIATION | backup_service / backup_3245 | BLOCK_RESTORE / BLOCKED | evidence_id="" by contract: future remediation/verification | rule_14 BACKUP_ARCHIVE -> RETAIN; block restore access; future action/check; contract requires empty evidence_id |
| 3 | VERIFICATION | account_service / account_4092 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 4 | VERIFICATION | security_service / audit_record_1797 | VERIFY_RECORD_PRESENT / PRESENT | evidence_id="" by contract: future remediation/verification | rule_12 SECURITY_AUDIT_LOG -> RETAIN; future action/check; contract requires empty evidence_id |
| 5 | VERIFICATION | backup_service / backup_3245 | VERIFY_RESTORE_BLOCKED / BLOCKED | evidence_id="" by contract: future remediation/verification | rule_14 BACKUP_ARCHIVE -> RETAIN; block restore access; future action/check; contract requires empty evidence_id |

### case_18 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | search_service / search_4013 | REPORT_REMAINING_RECORD / PRESENT | evidence_94 evidence/logs/resource_lookup_trace_20260926_103856.log captured 2026-09-26T10:38:56Z, line(s) 52,53 | rule_03 SEARCH_INDEX_ENTRY -> DELETE; participant-visible finding/current verification |
| 2 | FINDING | analytics_platform / analytics_037 | REPORT_EXPOSED_PII / PRESENT | evidence_94 evidence/logs/resource_lookup_trace_20260926_103856.log captured 2026-09-26T10:38:56Z, line(s) 22,23 | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; participant-visible finding/current verification |
| 3 | FINDING | support_platform / support_5569 | REPORT_EXPOSED_PII / PRESENT | evidence_94 evidence/logs/resource_lookup_trace_20260926_103856.log captured 2026-09-26T10:38:56Z, line(s) 10,11 | rule_05 SUPPORT_MESSAGE -> REDACT; participant-visible finding/current verification |
| 4 | FINDING | integration_service / data_flow_4890 | REPORT_ACTIVE_DATA_FLOW / ACTIVE | evidence_94 evidence/logs/resource_lookup_trace_20260926_103856.log captured 2026-09-26T10:38:56Z, line(s) 24,25 | No direct deletion_rules.csv row; disable flow to prevent recreation; participant-visible finding/current verification |
| 5 | REMEDIATION | integration_service / data_flow_4890 | DISABLE_DATA_FLOW / DISABLED | evidence_id="" by contract: future remediation/verification | No direct deletion_rules.csv row; disable flow to prevent recreation; future action/check; contract requires empty evidence_id |
| 6 | REMEDIATION | search_service / search_4013 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 7 | REMEDIATION | support_platform / support_5569 | REDACT_RECORD / REDACTED | evidence_id="" by contract: future remediation/verification | rule_05 SUPPORT_MESSAGE -> REDACT; future action/check; contract requires empty evidence_id |
| 8 | REMEDIATION | analytics_platform / analytics_037 | ANONYMIZE_RECORD / ANONYMIZED | evidence_id="" by contract: future remediation/verification | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; future action/check; contract requires empty evidence_id |
| 9 | VERIFICATION | account_service / account_5521 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 10 | VERIFICATION | search_service / search_4013 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 11 | VERIFICATION | security_service / audit_record_6645 | VERIFY_RECORD_PRESENT / PRESENT | evidence_id="" by contract: future remediation/verification | rule_12 SECURITY_AUDIT_LOG -> RETAIN; future action/check; contract requires empty evidence_id |
| 12 | VERIFICATION | support_platform / support_5569 | VERIFY_RECORD_REDACTED / REDACTED | evidence_id="" by contract: future remediation/verification | rule_05 SUPPORT_MESSAGE -> REDACT; future action/check; contract requires empty evidence_id |
| 13 | VERIFICATION | analytics_platform / analytics_037 | VERIFY_RECORD_ANONYMIZED / ANONYMIZED | evidence_id="" by contract: future remediation/verification | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; future action/check; contract requires empty evidence_id |
| 14 | VERIFICATION | integration_service / data_flow_4890 | VERIFY_DATA_FLOW_DISABLED / DISABLED | evidence_id="" by contract: future remediation/verification | No direct deletion_rules.csv row; disable flow to prevent recreation; future action/check; contract requires empty evidence_id |

### case_19 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | search_service / search_6083 | REPORT_REMAINING_RECORD / PRESENT | evidence_01 evidence/logs/service_events_ap_south_20260915.log captured 2026-09-15T11:59:39Z, line(s) 36 | rule_03 SEARCH_INDEX_ENTRY -> DELETE; participant-visible finding/current verification |
| 2 | FINDING | support_platform / support_9553 | REPORT_EXPOSED_PII / PRESENT | evidence_01 evidence/logs/service_events_ap_south_20260915.log captured 2026-09-15T11:59:39Z, line(s) 15 | rule_05 SUPPORT_MESSAGE -> REDACT; participant-visible finding/current verification |
| 3 | REMEDIATION | search_service / search_6083 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 4 | REMEDIATION | support_platform / support_9553 | REDACT_RECORD / REDACTED | evidence_id="" by contract: future remediation/verification | rule_05 SUPPORT_MESSAGE -> REDACT; future action/check; contract requires empty evidence_id |
| 5 | VERIFICATION | account_service / account_9102 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 6 | VERIFICATION | search_service / search_6083 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 7 | VERIFICATION | security_service / audit_record_6793 | VERIFY_RECORD_PRESENT / PRESENT | evidence_id="" by contract: future remediation/verification | rule_12 SECURITY_AUDIT_LOG -> RETAIN; future action/check; contract requires empty evidence_id |
| 8 | VERIFICATION | support_platform / support_9553 | VERIFY_RECORD_REDACTED / REDACTED | evidence_id="" by contract: future remediation/verification | rule_05 SUPPORT_MESSAGE -> REDACT; future action/check; contract requires empty evidence_id |

### case_20 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | search_service / search_4262 | REPORT_REMAINING_RECORD / PRESENT | evidence_94 evidence/logs/resource_lookup_trace_20260926_103856.log captured 2026-09-26T10:38:56Z, line(s) 8,9 | rule_03 SEARCH_INDEX_ENTRY -> DELETE; participant-visible finding/current verification |
| 2 | FINDING | integration_service / data_flow_1770 | REPORT_ACTIVE_DATA_FLOW / ACTIVE | evidence_94 evidence/logs/resource_lookup_trace_20260926_103856.log captured 2026-09-26T10:38:56Z, line(s) 40,41 | No direct deletion_rules.csv row; disable flow to prevent recreation; participant-visible finding/current verification |
| 3 | REMEDIATION | integration_service / data_flow_1770 | DISABLE_DATA_FLOW / DISABLED | evidence_id="" by contract: future remediation/verification | No direct deletion_rules.csv row; disable flow to prevent recreation; future action/check; contract requires empty evidence_id |
| 4 | REMEDIATION | search_service / search_4262 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 5 | VERIFICATION | account_service / account_5037 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 6 | VERIFICATION | search_service / search_4262 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 7 | VERIFICATION | security_service / audit_record_5569 | VERIFY_RECORD_PRESENT / PRESENT | evidence_id="" by contract: future remediation/verification | rule_12 SECURITY_AUDIT_LOG -> RETAIN; future action/check; contract requires empty evidence_id |
| 8 | VERIFICATION | integration_service / data_flow_1770 | VERIFY_DATA_FLOW_DISABLED / DISABLED | evidence_id="" by contract: future remediation/verification | No direct deletion_rules.csv row; disable flow to prevent recreation; future action/check; contract requires empty evidence_id |

### case_21 — COMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | VERIFICATION | account_service / account_6440 | VERIFY_RECORD_ABSENT / ABSENT | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 46 | rule_01 USER_PROFILE -> DELETE; participant-visible finding/current verification |
| 2 | VERIFICATION | security_service / audit_record_3737 | VERIFY_RECORD_PRESENT / PRESENT | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 288 | rule_12 SECURITY_AUDIT_LOG -> RETAIN; participant-visible finding/current verification |
| 3 | VERIFICATION | analytics_platform / analytics_5335 | VERIFY_RECORD_ANONYMIZED / ANONYMIZED | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 105 | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; participant-visible finding/current verification |

### case_22 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | search_service / search_8911 | REPORT_REMAINING_RECORD / PRESENT | evidence_05 evidence/databases/customer_data_read_replica_20260921.sql captured 2026-09-21T10:00:00Z, line(s) 41,79 | rule_03 SEARCH_INDEX_ENTRY -> DELETE; participant-visible finding/current verification |
| 2 | FINDING | analytics_platform / analytics_4440 | REPORT_EXPOSED_PII / PRESENT | evidence_05 evidence/databases/customer_data_read_replica_20260921.sql captured 2026-09-21T10:00:00Z, line(s) 17,55 | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; participant-visible finding/current verification |
| 3 | REMEDIATION | search_service / search_8911 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 4 | REMEDIATION | analytics_platform / analytics_4440 | ANONYMIZE_RECORD / ANONYMIZED | evidence_id="" by contract: future remediation/verification | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; future action/check; contract requires empty evidence_id |
| 5 | VERIFICATION | account_service / account_4990 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 6 | VERIFICATION | search_service / search_8911 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 7 | VERIFICATION | security_service / audit_record_3482 | VERIFY_RECORD_PRESENT / PRESENT | evidence_id="" by contract: future remediation/verification | rule_12 SECURITY_AUDIT_LOG -> RETAIN; future action/check; contract requires empty evidence_id |
| 8 | VERIFICATION | analytics_platform / analytics_4440 | VERIFY_RECORD_ANONYMIZED / ANONYMIZED | evidence_id="" by contract: future remediation/verification | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; future action/check; contract requires empty evidence_id |

### case_23 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | export_service / export_7364 | REPORT_REMAINING_RECORD / PRESENT | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 150,154 | rule_09 USER_EXPORT -> DELETE; participant-visible finding/current verification |
| 2 | FINDING | search_service / search_898 | REPORT_REMAINING_RECORD / PRESENT | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 254,261 | rule_03 SEARCH_INDEX_ENTRY -> DELETE; participant-visible finding/current verification |
| 3 | REMEDIATION | export_service / export_7364 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | rule_09 USER_EXPORT -> DELETE; future action/check; contract requires empty evidence_id |
| 4 | REMEDIATION | search_service / search_898 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 5 | VERIFICATION | account_service / account_410 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 6 | VERIFICATION | export_service / export_7364 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_09 USER_EXPORT -> DELETE; future action/check; contract requires empty evidence_id |
| 7 | VERIFICATION | search_service / search_898 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 8 | VERIFICATION | security_service / audit_record_4128 | VERIFY_RECORD_PRESENT / PRESENT | evidence_id="" by contract: future remediation/verification | rule_12 SECURITY_AUDIT_LOG -> RETAIN; future action/check; contract requires empty evidence_id |

### case_24 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | account_service / account_5334 | REPORT_REMAINING_RECORD / PRESENT | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 28 | rule_01 USER_PROFILE -> DELETE; participant-visible finding/current verification |
| 2 | FINDING | search_service / search_5577 | REPORT_REMAINING_RECORD / PRESENT | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 236,243 | rule_03 SEARCH_INDEX_ENTRY -> DELETE; participant-visible finding/current verification |
| 3 | REMEDIATION | account_service / account_5334 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 4 | REMEDIATION | search_service / search_5577 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 5 | VERIFICATION | account_service / account_5334 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 6 | VERIFICATION | search_service / search_5577 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 7 | VERIFICATION | security_service / audit_record_7095 | VERIFY_RECORD_PRESENT / PRESENT | evidence_id="" by contract: future remediation/verification | rule_12 SECURITY_AUDIT_LOG -> RETAIN; future action/check; contract requires empty evidence_id |

### case_25 — COMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | VERIFICATION | account_service / account_3136 | VERIFY_RECORD_ABSENT / ABSENT | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 10 | rule_01 USER_PROFILE -> DELETE; participant-visible finding/current verification |
| 2 | VERIFICATION | security_service / audit_record_451 | VERIFY_RECORD_PRESENT / PRESENT | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 302 | rule_12 SECURITY_AUDIT_LOG -> RETAIN; participant-visible finding/current verification |
| 3 | VERIFICATION | analytics_platform / analytics_1895 | VERIFY_RECORD_ANONYMIZED / ANONYMIZED | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 60 | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; participant-visible finding/current verification |

### case_26 — COMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | VERIFICATION | account_service / account_5684 | VERIFY_RECORD_ABSENT / ABSENT | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 40 | rule_01 USER_PROFILE -> DELETE; participant-visible finding/current verification |
| 2 | VERIFICATION | security_service / audit_record_5416 | VERIFY_RECORD_PRESENT / PRESENT | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 309 | rule_12 SECURITY_AUDIT_LOG -> RETAIN; participant-visible finding/current verification |
| 3 | VERIFICATION | support_platform / support_4715 | VERIFY_RECORD_REDACTED / REDACTED | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 349 | rule_05 SUPPORT_MESSAGE -> REDACT; participant-visible finding/current verification |
| 4 | VERIFICATION | analytics_platform / analytics_4566 | VERIFY_RECORD_ANONYMIZED / ANONYMIZED | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 78 | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; participant-visible finding/current verification |
| 5 | VERIFICATION | integration_service / data_flow_6244 | VERIFY_DATA_FLOW_DISABLED / DISABLED | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 194 | No direct deletion_rules.csv row; disable flow to prevent recreation; participant-visible finding/current verification |
| 6 | VERIFICATION | backup_service / backup_3120 | VERIFY_RESTORE_BLOCKED / BLOCKED | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 121,125 | rule_14 BACKUP_ARCHIVE -> RETAIN; block restore access; participant-visible finding/current verification |

### case_27 — COMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | VERIFICATION | account_service / account_3866 | VERIFY_RECORD_ABSENT / ABSENT | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 16 | rule_01 USER_PROFILE -> DELETE; participant-visible finding/current verification |
| 2 | VERIFICATION | security_service / audit_record_3830 | VERIFY_RECORD_PRESENT / PRESENT | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 295 | rule_12 SECURITY_AUDIT_LOG -> RETAIN; participant-visible finding/current verification |
| 3 | VERIFICATION | support_platform / support_4707 | VERIFY_RECORD_REDACTED / REDACTED | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 340 | rule_05 SUPPORT_MESSAGE -> REDACT; participant-visible finding/current verification |
| 4 | VERIFICATION | analytics_platform / analytics_4574 | VERIFY_RECORD_ANONYMIZED / ANONYMIZED | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 87 | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; participant-visible finding/current verification |
| 5 | VERIFICATION | integration_service / data_flow_2295 | VERIFY_DATA_FLOW_DISABLED / DISABLED | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 167 | No direct deletion_rules.csv row; disable flow to prevent recreation; participant-visible finding/current verification |
| 6 | VERIFICATION | backup_service / backup_5970 | VERIFY_RESTORE_BLOCKED / BLOCKED | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 129,133 | rule_14 BACKUP_ARCHIVE -> RETAIN; block restore access; participant-visible finding/current verification |

### case_28 — COMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | VERIFICATION | account_service / account_5482 | VERIFY_RECORD_ABSENT / ABSENT | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 34 | rule_01 USER_PROFILE -> DELETE; participant-visible finding/current verification |
| 2 | VERIFICATION | security_service / audit_record_9265 | VERIFY_RECORD_PRESENT / PRESENT | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 316 | rule_12 SECURITY_AUDIT_LOG -> RETAIN; participant-visible finding/current verification |
| 3 | VERIFICATION | support_platform / support_2351 | VERIFY_RECORD_REDACTED / REDACTED | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 331 | rule_05 SUPPORT_MESSAGE -> REDACT; participant-visible finding/current verification |
| 4 | VERIFICATION | analytics_platform / analytics_6077 | VERIFY_RECORD_ANONYMIZED / ANONYMIZED | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 114 | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; participant-visible finding/current verification |
| 5 | VERIFICATION | integration_service / data_flow_2337 | VERIFY_DATA_FLOW_DISABLED / DISABLED | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 176 | No direct deletion_rules.csv row; disable flow to prevent recreation; participant-visible finding/current verification |
| 6 | VERIFICATION | backup_service / backup_838 | VERIFY_RESTORE_BLOCKED / BLOCKED | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 137,141 | rule_14 BACKUP_ARCHIVE -> RETAIN; block restore access; participant-visible finding/current verification |

### case_29 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | search_service / search_1993 | REPORT_REMAINING_RECORD / PRESENT | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 218,225 | rule_03 SEARCH_INDEX_ENTRY -> DELETE; participant-visible finding/current verification |
| 2 | FINDING | analytics_platform / analytics_5208 | REPORT_EXPOSED_PII / PRESENT | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 96 | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; participant-visible finding/current verification |
| 3 | FINDING | support_platform / support_5281 | REPORT_EXPOSED_PII / PRESENT | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 358 | rule_05 SUPPORT_MESSAGE -> REDACT; participant-visible finding/current verification |
| 4 | FINDING | integration_service / data_flow_3827 | REPORT_ACTIVE_DATA_FLOW / ACTIVE | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 185 | No direct deletion_rules.csv row; disable flow to prevent recreation; participant-visible finding/current verification |
| 5 | REMEDIATION | integration_service / data_flow_3827 | DISABLE_DATA_FLOW / DISABLED | evidence_id="" by contract: future remediation/verification | No direct deletion_rules.csv row; disable flow to prevent recreation; future action/check; contract requires empty evidence_id |
| 6 | REMEDIATION | search_service / search_1993 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 7 | REMEDIATION | support_platform / support_5281 | REDACT_RECORD / REDACTED | evidence_id="" by contract: future remediation/verification | rule_05 SUPPORT_MESSAGE -> REDACT; future action/check; contract requires empty evidence_id |
| 8 | REMEDIATION | analytics_platform / analytics_5208 | ANONYMIZE_RECORD / ANONYMIZED | evidence_id="" by contract: future remediation/verification | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; future action/check; contract requires empty evidence_id |
| 9 | VERIFICATION | account_service / account_7012 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 10 | VERIFICATION | search_service / search_1993 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 11 | VERIFICATION | security_service / audit_record_3954 | VERIFY_RECORD_PRESENT / PRESENT | evidence_id="" by contract: future remediation/verification | rule_12 SECURITY_AUDIT_LOG -> RETAIN; future action/check; contract requires empty evidence_id |
| 12 | VERIFICATION | support_platform / support_5281 | VERIFY_RECORD_REDACTED / REDACTED | evidence_id="" by contract: future remediation/verification | rule_05 SUPPORT_MESSAGE -> REDACT; future action/check; contract requires empty evidence_id |
| 13 | VERIFICATION | analytics_platform / analytics_5208 | VERIFY_RECORD_ANONYMIZED / ANONYMIZED | evidence_id="" by contract: future remediation/verification | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; future action/check; contract requires empty evidence_id |
| 14 | VERIFICATION | integration_service / data_flow_3827 | VERIFY_DATA_FLOW_DISABLED / DISABLED | evidence_id="" by contract: future remediation/verification | No direct deletion_rules.csv row; disable flow to prevent recreation; future action/check; contract requires empty evidence_id |

### case_30 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | search_service / search_9359 | REPORT_REMAINING_RECORD / PRESENT | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 272,279 | rule_03 SEARCH_INDEX_ENTRY -> DELETE; participant-visible finding/current verification |
| 2 | FINDING | analytics_platform / analytics_3697 | REPORT_EXPOSED_PII / PRESENT | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 69 | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; participant-visible finding/current verification |
| 3 | FINDING | support_platform / support_6477 | REPORT_EXPOSED_PII / PRESENT | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 367 | rule_05 SUPPORT_MESSAGE -> REDACT; participant-visible finding/current verification |
| 4 | FINDING | integration_service / data_flow_8524 | REPORT_ACTIVE_DATA_FLOW / ACTIVE | evidence_92 evidence/records/service_resource_export_20260915_114455.json captured 2026-09-15T11:44:55Z, line(s) 203 | No direct deletion_rules.csv row; disable flow to prevent recreation; participant-visible finding/current verification |
| 5 | REMEDIATION | integration_service / data_flow_8524 | DISABLE_DATA_FLOW / DISABLED | evidence_id="" by contract: future remediation/verification | No direct deletion_rules.csv row; disable flow to prevent recreation; future action/check; contract requires empty evidence_id |
| 6 | REMEDIATION | search_service / search_9359 | DELETE_RECORD / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 7 | REMEDIATION | support_platform / support_6477 | REDACT_RECORD / REDACTED | evidence_id="" by contract: future remediation/verification | rule_05 SUPPORT_MESSAGE -> REDACT; future action/check; contract requires empty evidence_id |
| 8 | REMEDIATION | analytics_platform / analytics_3697 | ANONYMIZE_RECORD / ANONYMIZED | evidence_id="" by contract: future remediation/verification | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; future action/check; contract requires empty evidence_id |
| 9 | VERIFICATION | account_service / account_4163 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 10 | VERIFICATION | search_service / search_9359 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_03 SEARCH_INDEX_ENTRY -> DELETE; future action/check; contract requires empty evidence_id |
| 11 | VERIFICATION | security_service / audit_record_1707 | VERIFY_RECORD_PRESENT / PRESENT | evidence_id="" by contract: future remediation/verification | rule_12 SECURITY_AUDIT_LOG -> RETAIN; future action/check; contract requires empty evidence_id |
| 12 | VERIFICATION | support_platform / support_6477 | VERIFY_RECORD_REDACTED / REDACTED | evidence_id="" by contract: future remediation/verification | rule_05 SUPPORT_MESSAGE -> REDACT; future action/check; contract requires empty evidence_id |
| 13 | VERIFICATION | analytics_platform / analytics_3697 | VERIFY_RECORD_ANONYMIZED / ANONYMIZED | evidence_id="" by contract: future remediation/verification | rule_07 ANALYTICS_PROFILE -> ANONYMIZE; rule_08 is the other possible analytics rule; future action/check; contract requires empty evidence_id |
| 14 | VERIFICATION | integration_service / data_flow_8524 | VERIFY_DATA_FLOW_DISABLED / DISABLED | evidence_id="" by contract: future remediation/verification | No direct deletion_rules.csv row; disable flow to prevent recreation; future action/check; contract requires empty evidence_id |

### case_31 — COMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | VERIFICATION | account_service / account_4857 | VERIFY_RECORD_ABSENT / ABSENT | evidence_51 evidence/records/customer_data_snapshot_bundle_20260915.json captured 2026-09-15T12:00:00Z; snapshot/readback scope | rule_01 USER_PROFILE -> DELETE; participant-visible finding/current verification |
| 2 | VERIFICATION | security_service / audit_record_6909 | VERIFY_RECORD_PRESENT / PRESENT | evidence_51 evidence/records/customer_data_snapshot_bundle_20260915.json captured 2026-09-15T12:00:00Z, line(s) 42 | rule_12 SECURITY_AUDIT_LOG -> RETAIN; participant-visible finding/current verification |
| 3 | VERIFICATION | identity_service / tombstone_440 | VERIFY_RECORD_REDACTED / REDACTED | evidence_51 evidence/records/customer_data_snapshot_bundle_20260915.json captured 2026-09-15T12:00:00Z, line(s) 17 | rule_15 ACCOUNT_TOMBSTONE -> REDACT; participant-visible finding/current verification |

### case_32 — INCOMPLETE

| # | Phase | System/resource | Operation/state | Evidence file/row | Rule and why |
|---:|---|---|---|---|---|
| 1 | FINDING | identity_service / tombstone_9178 | REPORT_EXPOSED_PII / PRESENT | evidence_51 evidence/records/customer_data_snapshot_bundle_20260915.json captured 2026-09-15T12:00:00Z, line(s) 26 | rule_15 ACCOUNT_TOMBSTONE -> REDACT; participant-visible finding/current verification |
| 2 | REMEDIATION | identity_service / tombstone_9178 | REDACT_RECORD / REDACTED | evidence_id="" by contract: future remediation/verification | rule_15 ACCOUNT_TOMBSTONE -> REDACT; future action/check; contract requires empty evidence_id |
| 3 | VERIFICATION | account_service / account_8858 | VERIFY_RECORD_ABSENT / ABSENT | evidence_id="" by contract: future remediation/verification | rule_01 USER_PROFILE -> DELETE; future action/check; contract requires empty evidence_id |
| 4 | VERIFICATION | security_service / audit_record_7068 | VERIFY_RECORD_PRESENT / PRESENT | evidence_id="" by contract: future remediation/verification | rule_12 SECURITY_AUDIT_LOG -> RETAIN; future action/check; contract requires empty evidence_id |
| 5 | VERIFICATION | identity_service / tombstone_9178 | VERIFY_RECORD_REDACTED / REDACTED | evidence_id="" by contract: future remediation/verification | rule_15 ACCOUNT_TOMBSTONE -> REDACT; future action/check; contract requires empty evidence_id |

