# Evaluation report

## Public 32-case sample score

| Metric | Result |
|---|---:|
| Case-level status accuracy | 81.25% |
| Exact output-row match | 6.25% (2/32) |
| Mean step F1 on phase/operation/system/resource/state | 0.482 |
| Sequence accuracy | 6.25% |
| Phase accuracy | 0.627 |
| Operation accuracy | 0.434 |
| System ID accuracy | 0.450 |
| Resource ID accuracy | 0.458 |
| State accuracy | 0.538 |
| Evidence ID accuracy | 0.605 |

Metrics are produced by `code/evaluation/main.py`; every failing sample emits a complete expected/actual diff in the evaluator output. The before/after history is in `CHANGELOG.md`.

## Synthetic cases

| Case | Scenario | Expected | Result |
|---|---|---|---|
| synthetic_old_email_chain | Old email resolves through an email audit chain | Resolved user; INCOMPLETE | PASS |
| synthetic_failover_drift | Primary is absent while failover still contains the record | INCOMPLETE | PASS |
| synthetic_non_deletion | Data-copy request explicitly says not to delete | NOT_APPLICABLE | PASS |
| **Total** |  |  | **3/3 PASS** |

## Full dataset run

| Status | Count |
|---|---:|
| COMPLETE | 130 |
| INCOMPLETE | 378 |
| NOT_APPLICABLE | 10 |
| Total | 518 |

## Improvements made

| Problem | General fix |
|---|---|
| Cached parser generators were exhausted on later cases | Cache materialized observation tuples |
| Empty authoritative snapshots omitted absent resources | Reconstruct absence from linked deletion resources and snapshot evidence |
| 404/zero-row traces were treated as present | Normalize completed zero-row lookups to ABSENT |
| Analytics records with no identifiers lacked state | Infer ANONYMIZED only for completed analytics reads with no identifiers |
| Retained backups produced redundant presence checks | Verify restore blocking without a duplicate backup-presence step |

Remaining sample failures are reported rather than hidden; no case IDs are hardcoded into prediction logic.
