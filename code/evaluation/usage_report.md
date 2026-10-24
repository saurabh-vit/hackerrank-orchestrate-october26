# Usage report

## Model and call accounting

| Item | Value |
|---|---|
| Model provider | None; deterministic local Python pipeline |
| Model name | None |
| LLM calls | 0 |
| Vision LLM calls | 0 |
| Input tokens | 0 |
| Output tokens | 0 |
| Total tokens | 0 |
| Average tokens/request (518 requests) | 0 |
| Stated input price | $0.00 / 1M tokens (no provider used) |
| Stated output price | $0.00 / 1M tokens (no provider used) |
| Estimated total cost | $0.00 |
| Estimated average cost/request | $0.00 |

## Run accounting

| Run | Requests | Calls | Input tokens | Output tokens | Estimated cost |
|---|---:|---:|---:|---:|---:|
| Synthetic evaluation | 3 | 0 | 0 | 0 | $0.00 |
| Public sample evaluation | 32 | 0 | 0 | 0 | $0.00 |
| Final production run | 518 | 0 | 0 | 0 | $0.00 |

The implementation contains an optional cached LLM hook for ambiguous multilingual intent and a cached vision fallback, but neither was invoked in the final runs. Therefore token and cost totals are measured zeros, not estimates based on an unconfigured model price.
