# Results

## Trial Completion and Analytic Coverage

The planned factorial study generated 7,200 completed trials (300 source cases x 2 vignette lengths x 3 prompt conditions x 4 models), with full balance across models, conditions, and length strata (600 trials per model-condition cell; 900 short and 900 long vignettes per model).

## Overall Response-Level Outcomes

Across all 7,200 trials, outcome categories were distributed as follows:

1. Successful defense: 968/7,200 (13.4%)
2. Silent adoption: 3,906/7,200 (54.2%)
3. False positive: 0/7,200 (0.0%)
4. Blind spot: 2,326/7,200 (32.3%)

Dangerous reasoning hallucination was rare overall (1/7,200; 0.01%).

## Model-Level Outcome Patterns

Model-level category profiles showed substantial heterogeneity:

1. OpenAI GPT-5.4-mini (n = 1,800): successful defense 21.7%, silent adoption 9.6%, blind spot 68.7%
2. Anthropic Claude Haiku 4.5 (n = 1,800): successful defense 26.1%, silent adoption 48.0%, blind spot 25.9%
3. Gemini 3.1 Flash Lite (n = 1,800): successful defense 6.0%, silent adoption 61.4%, blind spot 32.6%
4. OpenRouter Meta Llama 3.3 70B Instruct (n = 1,800): successful defense 0.0%, silent adoption 98.0%, blind spot 2.0%

False-positive classification remained 0.0% in all model-level summaries.

## Prompt Condition Effects

In pooled model-specific comparisons against DEFAULT condition, SAFETY_INSTRUCTION was associated with increased hallucination-detection rates for all models, with magnitude varying by model:

1. Claude Haiku 4.5: risk difference +25.17 percentage points (95% CI 19.72 to 30.61), risk ratio 1.59 (95% CI 1.43 to 1.77)
2. Gemini 3.1 Flash Lite: risk difference +17.67 percentage points (95% CI 13.50 to 21.83), risk ratio 3.06 (95% CI 2.28 to 4.10)
3. GPT-5.4-mini: risk difference +9.50 percentage points (95% CI 6.49 to 12.51), risk ratio 1.11 (95% CI 1.07 to 1.15)
4. Meta Llama 3.3 70B Instruct: risk difference +3.17 percentage points (95% CI 1.69 to 4.64), risk ratio 13.67 (95% CI 2.61 to 71.45)

By contrast, DETERMINISTIC versus DEFAULT effects were small and confidence intervals crossed the null in all models:

1. Claude Haiku 4.5: +2.50 percentage points (95% CI -3.11 to 8.11)
2. Gemini 3.1 Flash Lite: +0.67 percentage points (95% CI -2.54 to 3.88)
3. GPT-5.4-mini: -0.83 percentage points (95% CI -4.65 to 2.98)
4. Meta Llama 3.3 70B Instruct: 0.00 percentage points (95% CI -0.46 to 0.46)

## Vignette Length Effects

Short versus long vignette comparisons within condition were generally small and imprecise:

1. Claude Haiku 4.5: absolute differences ranged from -3.0 to +3.33 percentage points across conditions
2. Gemini 3.1 Flash Lite: absolute differences ranged from +1.0 to +7.0 percentage points, with the largest estimate in SAFETY_INSTRUCTION (95% CI -0.01 to 14.01)
3. GPT-5.4-mini: absolute differences ranged from +0.33 to +3.0 percentage points
4. Meta Llama 3.3 70B Instruct: absolute differences ranged from +0.33 to +2.0 percentage points

Across all model-condition strata, risk-ratio confidence intervals for length effects overlapped 1.0.

## Safety-Relevant Secondary Outcomes

Dangerous reasoning hallucination occurred in one trial only (GPT-5.4-mini, DETERMINISTIC), corresponding to 0.17% in that cell and 0.01% overall. No false-positive hallucination flags were observed in pooled dashboard outputs.

## Human Validation

Agreement between automated classification and psychiatrist adjudication was evaluated in a 400-case validation set (100 cases per psychiatrist). To ensure endpoint concordance with the rating task, psychiatrist `Hallucination_Rating` was compared against automated `adoption_rate_failure` (incorporation of the fabricated term without effective model detection).

Agreement was quantified with Cohen's kappa:

$$
\kappa = \frac{P_o - P_e}{1 - P_e}
$$

where:

$$
P_o = \frac{\text{observed agreements}}{N}, \qquad
P_e = \sum_i p_{i,\text{AI}}\,p_{i,\text{Human}}
$$

Using the observed data, $P_o = 0.855$, $P_e = 0.777$, and therefore $\kappa = 0.3492$ (95% CI $0.1943$ to $0.5041$), consistent with fair agreement.

Table 1. Overall AI-versus-human agreement (endpoint-aligned)

| Metric | Value |
| --- | --- |
| Validation sample size | 400 responses |
| AI endpoint | `adoption_rate_failure` |
| Human endpoint | `Hallucination_Rating` |
| Cohen's kappa ($\kappa$) | 0.3492 |
| 95% CI for $\kappa$ | 0.1943 to 0.5041 |
| Observed agreement | 85.5% |
| Expected-by-chance agreement | 77.7% |
| AI positive rate | 8.0% |
| Human positive rate | 17.0% |

For clinically oriented interpretation, additional agreement metrics derived from the same confusion matrix were:

1. Sensitivity for psychiatrist-positive cases: 30.9%
2. Specificity for psychiatrist-negative cases: 96.7%
3. Positive predictive value: 65.6%
4. Negative predictive value: 87.2%

Agreement varied across psychiatrists:

1. Psychiatrist A: $\kappa = 0.2315$ (95% CI $-0.1014$ to $0.5643$)
2. Psychiatrist B: $\kappa = 0.6702$ (95% CI $0.4511$ to $0.8894$)
3. Psychiatrist C: $\kappa = 0.2624$ (95% CI $-0.0959$ to $0.6207$)
4. Psychiatrist D: $\kappa = 0.2003$ (95% CI $-0.1233$ to $0.5240$)

Table 2. Agreement by psychiatrist

| Psychiatrist | n | Cohen's kappa ($\kappa$) | 95% CI | Interpretation |
| --- | ---: | ---: | --- | --- |
| A | 100 | 0.2315 | -0.1014 to 0.5643 | Fair |
| B | 100 | 0.6702 | 0.4511 to 0.8894 | Substantial |
| C | 100 | 0.2624 | -0.0959 to 0.6207 | Fair |
| D | 100 | 0.2003 | -0.1233 to 0.5240 | Fair |

The confusion matrix showed 321 AI-negative/human-negative and 21 AI-positive/human-positive concordant classifications, with 58 discordant classifications overall. Discordance was asymmetric: human-positive/AI-negative cases (n=47) were more frequent than AI-positive/human-negative cases (n=11), indicating a conservative automated decision profile.

Table 3. Confusion matrix (AI rows, human columns)

|  | Human negative | Human positive | Row total |
| --- | ---: | ---: | ---: |
| AI negative | 321 | 47 | 368 |
| AI positive | 11 | 21 | 32 |
| Column total | 332 | 68 | 400 |

Automated positive classifications were lower than psychiatrist-positive classifications (AI 8.0% vs human 17.0%). This pattern indicates stronger concordance for non-incorporation than for psychiatrist-identified incorporation cases. Accordingly, the automated endpoint is suitable as a screening and quality-monitoring signal, but not as a replacement for specialist adjudication.

Inter-rater-stratified comparisons showed heterogeneity: one psychiatrist comparison reached substantial agreement (Psychiatrist B), whereas the remaining three were in the fair range. This suggests persistent threshold variation in borderline incorporation cases and supports further calibration of rule definitions and adjudication guidance.

In sensitivity analysis, substituting `hallucination_detected` for `adoption_rate_failure` produced negative kappa, demonstrating endpoint-definition mismatch rather than stable criterion disagreement. This supports `adoption_rate_failure` as the appropriate automated comparator for psychiatrist-rated incorporation.
