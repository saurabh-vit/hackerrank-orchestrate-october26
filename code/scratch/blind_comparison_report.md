# Blind derivation comparison

Selected 40 cases; old-email coverage=36; uppercase coverage=5.

| Metric | Result |
|---|---:|
| Status agreement | 0.825 |
| Mean step precision/recall (set F1 proxy) | 0.335 |
| Evidence-id positional agreement | 0.206 |
| Step key/order agreement | 0.025 |

## Discrepancy root causes

| Root cause | Cases | Likely scope |
|---|---:|---|
| evidence disagreement | 40 | Ranked by this blind sample; see case-level records in blind_expected.json |
| step set/order disagreement | 39 | Ranked by this blind sample; see case-level records in blind_expected.json |
| status disagreement | 7 | Ranked by this blind sample; see case-level records in blind_expected.json |

## Case-level results

| Case | Status agreement | Step F1 | Order agreement | Evidence agreement |
|---|---|---:|---|---|
| case_100 | yes | 0.571 | no | 0.200 |
| case_103 | no | 0.000 | no | 0.000 |
| case_110 | yes | 0.875 | no | 0.444 |
| case_118 | yes | 0.000 | no | 0.444 |
| case_125 | yes | 1.000 | no | 0.333 |
| case_136 | yes | 0.000 | no | 0.105 |
| case_139 | yes | 0.000 | no | 0.133 |
| case_143 | yes | 0.414 | no | 0.222 |
| case_148 | yes | 0.400 | no | 0.263 |
| case_152 | yes | 0.250 | no | 0.000 |
| case_153 | yes | 0.933 | no | 0.500 |
| case_155 | yes | 0.769 | no | 0.286 |
| case_159 | yes | 0.333 | no | 0.000 |
| case_160 | yes | 0.889 | no | 0.400 |
| case_175 | yes | 0.857 | no | 0.143 |
| case_185 | yes | 0.500 | no | 0.167 |
| case_188 | yes | 0.375 | no | 0.083 |
| case_194 | yes | 0.000 | no | 0.300 |
| case_199 | yes | 0.000 | no | 0.300 |
| case_201 | yes | 0.000 | no | 0.286 |
| case_206 | yes | 0.667 | no | 0.500 |
| case_216 | yes | 1.000 | no | 0.500 |
| case_220 | yes | 1.000 | no | 0.333 |
| case_227 | yes | 0.480 | no | 0.211 |
| case_238 | no | 0.000 | no | 0.250 |
| case_240 | yes | 0.000 | no | 0.250 |
| case_241 | yes | 0.000 | no | 0.167 |
| case_264 | yes | 0.000 | no | 0.214 |
| case_285 | yes | 0.000 | no | 0.154 |
| case_288 | yes | 0.000 | no | 0.200 |
| case_326 | yes | 0.000 | no | 0.120 |
| case_337 | yes | 0.500 | no | 0.300 |
| case_376 | yes | 0.000 | no | 0.200 |
| case_40 | yes | 0.000 | no | 0.038 |
| case_427 | no | 0.286 | no | 0.167 |
| case_53 | no | 0.000 | no | 0.000 |
| case_63 | no | 1.000 | yes | 0.000 |
| case_73 | no | 0.000 | no | 0.000 |
| case_85 | yes | 0.286 | no | 0.034 |
| case_90 | no | 0.000 | no | 0.000 |
