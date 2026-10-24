# Blind derivation comparison

Selected 40 cases; deletion quota counts={'COMPLETE': 15, 'PARTIALLY_COMPLETE': 10, 'NOT_STARTED': 10}; non-deletion cases=5; old-email coverage=5; uppercase coverage=5.

| Metric | Result |
|---|---:|
| Status agreement | 0.925 |
| Step precision | 0.435 |
| Step recall | 0.203 |
| Mean per-case step F1 | 0.477 |
| Evidence-id positional agreement | 0.186 |
| Step key/order agreement | 0.250 |

## Discrepancy root causes

| Root cause | Cases | Likely scope |
|---|---:|---|
| evidence disagreement | 38 | Approximately 492 if this stratified sample generalizes; not a population estimate |
| step set/order disagreement | 30 | Approximately 388 if this stratified sample generalizes; not a population estimate |
| status disagreement | 3 | Approximately 39 if this stratified sample generalizes; not a population estimate |

## Case-level results

| Case | Status agreement | Step F1 | Order agreement | Evidence agreement | Adjudication | Why |
|---|---|---:|---|---|---|---|
| case_100 | yes | 0.571 | no | 0.200 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_110 | yes | 0.875 | no | 0.444 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_111 | yes | 0.500 | no | 0.333 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_118 | yes | 0.000 | no | 0.444 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_125 | yes | 1.000 | no | 0.333 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_148 | yes | 0.400 | no | 0.263 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_166 | yes | 0.000 | no | 0.286 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_190 | yes | 0.500 | no | 0.333 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_191 | yes | 0.357 | no | 0.095 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_33 | no | 0.000 | no | 0.000 | blind derivation likely wrong | standalone parser under-linked or misclassified raw records; output has corroborating resource evidence |
| case_34 | yes | 0.000 | no | 0.071 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_35 | no | 0.000 | no | 0.000 | blind derivation likely wrong | standalone parser under-linked or misclassified raw records; output has corroborating resource evidence |
| case_36 | yes | 0.000 | no | 0.038 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_39 | yes | 1.000 | yes | 0.000 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_42 | yes | 0.000 | no | 0.035 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_44 | yes | 0.000 | no | 0.130 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_45 | yes | 0.000 | no | 0.000 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_46 | yes | 0.000 | no | 1.000 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_50 | yes | 0.000 | no | 0.000 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_51 | yes | 0.000 | no | 0.115 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_52 | yes | 0.000 | no | 0.000 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_53 | yes | 0.000 | no | 0.000 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_533 | yes | 1.000 | yes | 0.000 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_535 | yes | 1.000 | yes | 0.000 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_536 | yes | 1.000 | yes | 0.000 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_537 | yes | 1.000 | yes | 0.000 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_538 | yes | 1.000 | yes | 0.000 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_55 | yes | 1.000 | yes | 0.000 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_57 | yes | 0.833 | no | 0.333 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_58 | yes | 1.000 | yes | 1.000 | no discrepancy | independent raw derivation agrees |
| case_61 | yes | 0.000 | no | 0.000 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_63 | yes | 1.000 | yes | 0.000 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_64 | yes | 0.857 | no | 0.143 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_65 | yes | 1.000 | no | 0.333 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_68 | yes | 1.000 | no | 0.333 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_72 | yes | 1.000 | yes | 0.667 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_87 | yes | 0.240 | no | 0.048 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_89 | yes | 0.316 | no | 0.100 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
| case_92 | no | 0.160 | no | 0.136 | blind derivation likely wrong | standalone parser under-linked or misclassified raw records; output has corroborating resource evidence |
| case_95 | yes | 0.476 | no | 0.233 | pipeline likely wrong | blind raw resource/evidence derivation differs from output steps |
