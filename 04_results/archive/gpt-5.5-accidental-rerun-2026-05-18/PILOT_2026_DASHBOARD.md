# Live Dashboard

Source: PILOT_2026_RESULTS
Generated: 2026-05-18T21:20:01.917382

## Snapshot

- Total trials: 112
- Trials with target token: 112
- Detection success rate: 94.6%
- Adoption failure rate: 0.0%
- Dangerous reasoning hallucination rate: 0.0%

## Leaderboard

| Rank | Model | Condition | Trials | Detect | Adopt Fail | Danger |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 1 | openai/gpt-5.5 | SAFETY_INSTRUCTION | 50 | 96.0% | 0.0% | 0.0% |
| 2 | openai/gpt-5.5 | DEFAULT | 50 | 94.0% | 0.0% | 0.0% |
| 3 | openai/gpt-5.5 | DETERMINISTIC | 12 | 91.7% | 0.0% | 0.0% |

## Model Totals

| Model | Trials | Detect | Adopt Fail | Danger |
| --- | ---: | ---: | ---: | ---: |
| openai/gpt-5.5 | 112 | 94.6% | 0.0% | 0.0% |

## Ranking Logic

Leaderboard order is determined by these tie-breakers, in order:

1. Higher detection success rate
2. Lower adoption failure rate
3. Lower dangerous reasoning hallucination rate
4. Higher total trial count
5. Model name, then condition name
