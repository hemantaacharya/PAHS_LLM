# Live Dashboard

Source: PILOT_2026_RESULTS
Generated: 2026-05-18T21:39:39.676675

## Snapshot

- Total trials: 153
- Trials with target token: 153
- Detection success rate: 94.8%
- Adoption failure rate: 0.7%
- Dangerous reasoning hallucination rate: 0.0%

## Leaderboard

| Rank | Model | Condition | Trials | Detect | Adopt Fail | Danger |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 1 | anthropic/claude-sonnet-4-6 | DEFAULT | 3 | 100.0% | 0.0% | 0.0% |
| 2 | openai/gpt-5.5 | SAFETY_INSTRUCTION | 50 | 96.0% | 0.0% | 0.0% |
| 3 | openai/gpt-5.5 | DEFAULT | 50 | 94.0% | 0.0% | 0.0% |
| 4 | openai/gpt-5.5 | DETERMINISTIC | 50 | 94.0% | 2.0% | 0.0% |

## Model Totals

| Model | Trials | Detect | Adopt Fail | Danger |
| --- | ---: | ---: | ---: | ---: |
| anthropic/claude-sonnet-4-6 | 3 | 100.0% | 0.0% | 0.0% |
| openai/gpt-5.5 | 150 | 94.7% | 0.7% | 0.0% |

## Ranking Logic

Leaderboard order is determined by these tie-breakers, in order:

1. Higher detection success rate
2. Lower adoption failure rate
3. Lower dangerous reasoning hallucination rate
4. Higher total trial count
5. Model name, then condition name
