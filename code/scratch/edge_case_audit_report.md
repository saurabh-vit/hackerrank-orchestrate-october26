# Edge-case pipeline audit

Scope: raw participant-facing `dataset/`, current root `output.csv`, and the
existing parser output. No production file was changed. Evidence IDs below are
participant-visible manifest/activity IDs.

| # | Behavior | Concrete case | Expected from raw data | Actual pipeline output | Result |
|---:|---|---|---|---|---|
| 1 | Replica drift | `case_453` | `evidence_43` (`customer_data_reporting_replica_20260305.sql`) contains `account_3183` and `search_1317` for the subject while the primary table is clean. Report remaining records and delete them. | `INCOMPLETE`; findings cite `account_3183` and `search_1317`; remediation emits `DELETE_RECORD` for both before verification. | **PASS** |
| 2 | Tombstone retains direct PII | `case_548` | `evidence_52` (`customer_data_failover_replica_20260920.sql`) has `tombstone_3745` with name, email, phone, and email hash. Stable subject reference may remain; direct identifiers require redaction. | `INCOMPLETE`; `REPORT_EXPOSED_PII` -> `REDACT_RECORD` -> `VERIFY_RECORD_REDACTED` for `tombstone_3745`. | **PASS** |
| 3 | Active recreation flow | `case_461` | `evidence_43` contains enabled `data_flow_4612`; activity `activity_438` is a `CHECK_DATA_FLOW` success. | Finding `REPORT_ACTIVE_DATA_FLOW`, then remediation `DISABLE_DATA_FLOW` at step 5 before downstream delete/redact/anonymize steps. | **PASS** |
| 4 | Restorable backup and restore repopulation | `case_519`; restore event is `activity_3387` | `activity_49` says `backup_8264` can still be restored, and the Feb-03 log records `eligible=true`, `deletion_block=false` before `audit_at`. Separately, `activity_3387` says `backup_9287` repopulated `search_4882`; `activity_3388` then reports deletion failure. | `case_519` is `COMPLETE` with `[]`; it has no `REPORT_RESTORE_RISK` or `BLOCK_RESTORE`. The `activity_3387` event is after `case_55`’s April audit cutoff, so it is correctly out of scope for that case, but the in-scope backup risk is missed. | **FAIL** |
| 5 | Activity claims contradicted by evidence | `case_453` and `case_35` | `activity_567` says `account_3183` deletion succeeded, but reporting-replica evidence still contains it. For `case_35`, delete activities `activity_3436`/`3437` report failure while authoritative evidence `evidence_10` has `search_428`/`search_4801` absent. | `case_453` reports the remaining replica records despite the success claim. `case_35` verifies the failed-activity resources as absent. | **PASS** |
| 6 | Image/PDF-only evidence | `case_34` (image `evidence_04`); `case_45` (PDF `evidence_55`) | The image shows live `user_11` / `account_5762`; the PDF contains retained `audit_record_003`. | PDF is read and cited: `case_45` verifies `audit_record_003` with `evidence_55`. The image is not carried into the case evidence: `case_34` emits `VERIFY_RECORD_ABSENT` for `account_5762` with empty evidence despite the image and `activity_4000` link. | **FAIL** |
| 7 | Shared support message vs sole-owner attachment | `case_461` vs `case_455` | `support_3901` is a shared support conversation and must be redacted; `support_2055` is a ticket attachment owned by the subject and must be deleted. | `case_461`: `REDACT_RECORD` for `support_3901`. `case_455`: `DELETE_RECORD` for `support_2055`. | **PASS** |
| 8 | Security retention and legal hold | `case_45` and `case_261` | `audit_record_003` is inside the retention period; `legal_hold_8017` is retained through its ledger/register date. The audit found no record whose retention expired at its case `audit_at`. | `case_45` verifies `audit_record_003` present. `case_261` verifies `legal_hold_8017` present. No out-of-retention example exists in the supplied data; observed expired-at-audit count is 0. | **PASS (inside/hold); NO OUTSIDE CASE** |
| 9 | Historical-only identifier | `case_37` | Resolver uses `audit:audit_179`; the request identifier is not the current identity value. Evidence still finds the user’s `search_1934` and `data_flow_2528`. | `INCOMPLETE`; reports the search record and active flow, and disables the flow before deleting the search record. | **PASS** |
| 10 | Later event reverses earlier state | `case_55` / `case_519` | Raw activity contains one restore reversal: `activity_3387` restores `search_4882`, followed by failed delete `activity_3388`. No `DISABLE_DATA_FLOW` followed by a same-resource re-enable event exists. The restore is after `case_55`’s audit cutoff; the backup-risk sequence for `case_519` is in scope. | The post-cutoff restore is ignored for `case_55`, as required. However, the in-scope backup risk in `case_519` is missed. | **FAIL for in-scope restore handling; no disable/re-enable case** |

## Failure ranking

| Rank | Root cause | Directly demonstrated | Estimated affected scope |
|---:|---|---|---:|
| 1 | Restore-risk claims/evidence are not connected into planning | `case_519` | Up to 28 `CHECK_RESTORE_ACCESS` activity events, plus the single `RESTORE_BACKUP` event; exact case count requires a corrected resource-to-user join. |
| 2 | Image observations are not retained/linked to the case | `case_34` | 1 manifest image (`evidence_04`) in this dataset, therefore at least 1 case. |
| 3 | Restore reversal is only handled by the audit cutoff, not by an in-scope restore-risk finding | `case_55` versus `case_519` | 1 explicit restore event; its downstream impact is one linked subject, while the broader restore-risk family is the 28-event population above. |

## Reproduction records

The scratch verifier is [edge_case_audit.py](edge_case_audit.py); its compact raw
inspection output is [edge_case_audit_raw.txt](edge_case_audit_raw.txt). The
image was independently visually inspected at `dataset/evidence/images/account_admin_console_20260926.png`.
