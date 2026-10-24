# Final audit scorecard

This scorecard consolidates the existing Stage A–D artifacts. Estimates are
explicitly labeled; no hidden-set labels are available.

## 1. Stage A hard-fail gates

**All PASS? No.** The submission-format checks pass, but the audit gates do not:

| Gate | Result | Evidence |
|---|---|---|
| `output.csv` schema, 518 rows, IDs, sorting | PASS | Prior validator/audit: no schema or ordering violations |
| Status/JSON/step numbering | PASS | Prior validator: no violations |
| Deterministic clean generation | PASS | Repeated runs matched; full run about 52 seconds |
| Evidence citations grounded to the cited user/resource | **FAIL** | 125 offending cases in `audit_full_report.md` |
| Policy operation matches | **FAIL** | 11 contradictions |
| Findings/remediation/verification structure | **FAIL** | 36 findings without remediation; 10 orphan remediation/verification cases |
| Restore-risk handling | **FAIL** | `case_519` emitted `COMPLETE,[]` despite in-scope restore evidence |
| Image-only evidence | **FAIL** | `case_34` misses image `evidence_04` showing `account_5762` |

## 2. Reproduced metrics

| Metric | Result | Source/check |
|---|---:|---|
| Sample status accuracy | 81.25% | Reproduced by `python code/evaluation/main.py` |
| Sample row exact match | 6.25% (2/32) | Reproduced |
| Sample step F1 | 0.482346 | Reproduced |
| Sample phase accuracy | 0.626648 | Reproduced |
| Sample operation accuracy | 0.434475 | Reproduced |
| Sample system accuracy | 0.449752 | Reproduced |
| Sample resource accuracy | 0.458148 | Reproduced |
| Sample state accuracy | 0.537832 | Reproduced |
| Sample evidence-ID accuracy | 0.604889 | Reproduced |
| Sample sequence accuracy | 6.25% | Reproduced |
| Blind status agreement | 92.5% (37/40) | `blind_comparison_report.md` |
| Blind step precision | 0.435 | Blind derivation |
| Blind step recall | 0.203 | Blind derivation |
| Blind mean step F1 | 0.477 | Blind derivation |
| NOT_APPLICABLE precision | 100% (10/10) | Full audit: 10 text non-deletion cases, 10 predicted NA |
| NOT_APPLICABLE recall | 100% (10/10) | Full audit and CLASSIFY_REQUEST agreement |

Sample status confusion matrix (expected rows, actual columns):

| Expected \ Actual | COMPLETE | INCOMPLETE | NOT_APPLICABLE |
|---|---:|---:|---:|
| COMPLETE | 5 | 5 | 0 |
| INCOMPLETE | 0 | 21 | 1 |
| NOT_APPLICABLE | 0 | 0 | 0 |

## 3. Risk register

Ranking is approximate probability × affected-case count. Counts are observed
upper bounds from the 518-case audit unless marked as an estimate.

| Rank | Risk | Probability | Affected cases | Concrete fix | Effort |
|---:|---|---|---:|---|---|
| 1 | Reported COMPLETE masks computed INCOMPLETE | High | 179 | Add regression checks comparing computed state against every reported COMPLETE; fail closed on unresolved findings. | 1–2 h |
| 2 | File evidence is not actually grounded to the subject/resource | High | 125 | Require identifier/resource intersection before citation; retain resource-scoped provenance through planning. | 2–3 h |
| 3 | Findings lack matching remediation or verification | High | 36 + 10 orphan cases | Build a plan invariant: every finding has one remediation and verification unless policy explicitly retains it. | 1–2 h |
| 4 | Restore-risk evidence is not planned | High | Up to 28 restore checks + 1 restore event | Model flow/restore state as latest event, emit `REPORT_RESTORE_RISK`, and plan `BLOCK_RESTORE` before deletes. | 2–3 h |
| 5 | Policy heuristic contradicts `deletion_rules.csv` | Medium–high | 11 | Make category/condition matching data-driven and pass legal-hold/retention context explicitly. | 2–3 h |
| 6 | Non-zero-step COMPLETE/incorrect empty plans | Medium–high | 8 | Reject `COMPLETE` with no proof steps; treat missing evidence as unresolved, not clean. | 1 h |
| 7 | Primary `CLASSIFY_REQUEST` signal is unused by `main.py` | Medium | 10 linked events | Integrate the primary activity signal, then use text as secondary evidence. | 1–2 h |
| 8 | Later activity reversals are not modeled | Medium | 1 explicit restore reversal; broader flow population unknown | Replace boolean-OR activity claims with ordered per-resource state transitions. | 2–3 h |
| 9 | Image-only evidence can be missed | Medium | At least 1 (`case_34`) | Validate OCR identifiers, use deterministic OCR fallback diagnostics, and fail closed when an image is unreadable. | 1–2 h |
| 10 | Corrupt/missing files and unmatched identities are unsafe | Low observed, high severity | 0 observed unresolved; potentially any of 518 | Return structured per-file errors and an explicit `UNRESOLVED` internal state; never infer clean deletion. | 2 h |

## 4. Overfitting verdict

| Check | Verdict |
|---|---|
| Hardcoding found | **Yes, outside the decision path.** `code/evidence/demo.py`, `DESIGN.md`, and scratch/custom artifacts contain sample IDs; no sample IDs were found in the production prediction logic. |
| Single-case branches | No suspicious production case-ID branch. The non-deletion ablation changed only one public sample because only one labeled sample exercises that intent; the branch itself is general. |
| Mutation testing | 48/50 recorded mutations passed. Two failed expectations: `case_07` audit-time shift and `case_09` evidence deletion. Both were explained in the audit as boundary/resource-selection behavior, but they remain coverage warnings. |

## 5. Hidden-set confidence band (estimates)

| Scenario | Estimated status accuracy | Estimated step F1 | Reasoning |
|---|---:|---:|---|
| Conservative | 55–70% | 0.20–0.35 | 32 labels are small; 125 grounding failures, 36 incomplete plans, and restore/image misses are directly observed. |
| Expected | 65–80% | 0.30–0.50 | Sample status is 81.25% and blind status agreement is 92.5%, but structural/evidence metrics are materially weaker. |
| Optimistic | 80–90% | 0.50–0.65 | Assumes hidden cases resemble the exercised evidence families and the observed sample misses do not generalize. |

These are estimates, not measured hidden-set results.

## 6. Verdict and ordered work

**Verdict: NOT READY.** Known evidence, policy, planning, restore, and image failures are too substantial for shipment.

### Next 2 hours

1. Make unresolved/missing evidence fail closed and enforce resource-scoped citation grounding.
2. Implement latest-event state transitions for data flows and restores; emit and order restore-risk remediation.
3. Repair image observation linkage and add a regression for `account_5762`-style image evidence.
4. Enforce finding/remediation/verification invariants and data-driven policy conditions.
5. Rerun Stages A–C, regenerate `output.csv`, and inspect all new violations.

### Next 8 hours

1. Add corrupt-file, missing-file, malformed-time, unmatched-email, ambiguous-email, and reversal fixtures.
2. Add unit/property tests for evidence selection, identity chains, policy mapping, and ordering.
3. Expand non-PII synthetic evaluations beyond three cases and report confidence intervals.
4. Add a real Markdown usage ledger and regenerate both reports from the final run.
5. Run a clean-copy reproducibility test, validate the archive, and rerun deterministic hash checks.
