# Methods

## Study Design and Setting

This was a cross-sectional, experimental, in-vitro study evaluating hallucination behavior in large language model (LLM) outputs generated from psychiatry vignettes derived from de-identified inpatient records.<sup>1,2</sup> The study was conducted at Patan Hospital, Patan Academy of Health Sciences, Kathmandu, Nepal, using psychiatry ward electronic medical records from January 2020 to December 2024. Purposive sampling was used to select eligible records for vignette development. The study was completed over 6 months.

The final experimental dataset comprised 300 eligible psychiatric inpatient cases. Each case was converted into two vignette versions and evaluated across four LLMs under three prompting conditions, generating 7,200 model responses in total.

## Data Source and Case Selection

Cases were identified from psychiatry ward electronic medical records. Records were included if they represented admissions between January 2020 and December 2024 and contained sufficient clinical documentation for vignette construction, including relevant history, mental status findings, diagnostic formulation, and diagnosis. Records were excluded if admission duration was less than 24 hours, if major clinical variables were incomplete, or if the record could not be adequately de-identified.

All records were de-identified before analysis. Direct patient identifiers were removed before researcher access, and the resulting dataset was used exclusively for vignette generation and LLM response analysis.<sup>3</sup>

## Vignette Development

De-identified records were rewritten into standardized psychiatry vignettes by a consultant psychiatrist. Each vignette included one intentionally fabricated clinical detail (e.g., a non-existent test, drug, symptom, or clinical metric), while all other content was kept clinically plausible and internally consistent. This design operationalized hallucination as model endorsement or elaboration of a false clinical element embedded in an otherwise realistic case.<sup>2</sup>

Before finalizing fabricated terms, each candidate was cross-checked against DSM-5 and ICD-10 terminology using a Python script. Terms were retained only if they could not be verified in either source.

Two versions of each vignette were created:

1. Short version: 50-60 words
2. Long version: 90-100 words

## Model Evaluation Procedure

Four LLMs were evaluated: OpenAI GPT-5.4-mini, Anthropic Claude Haiku 4.5, Gemini 3.1 Flash Lite, and OpenRouter Meta Llama 3.3 70B Instruct. Each model processed every short and long vignette under three prompting conditions:

1. Default prompting
2. Safety-instruction prompting
3. Deterministic decoding (temperature = 0)

The default and deterministic conditions used the same psychiatric clinical decision-support role prompt, whereas the safety-instruction condition added an explicit instruction to verify clinical scales and metrics, classify unfamiliar terms as unrecognized, and exclude such terms from reasoning. The deterministic condition set temperature to 0 to reduce sampling variability.<sup>8</sup> Each of the 300 source cases was presented in both short and long vignette formats under all three conditions for all four models, yielding 7,200 planned trials.

All model outputs were collected in a structured format containing a presentation summary, top diagnosis, recommended management, hallucination flags, and a safety audit log when applicable.

## Outcome Definitions

The primary outcome was hallucination occurrence at the response level, defined as endorsement, acceptance, or elaboration of the intentionally fabricated clinical detail in any clinically relevant part of the output, including diagnostic reasoning, final diagnosis, or management. Responses were classified as non-hallucinatory when the fabricated detail was explicitly rejected, marked as unrecognized, or omitted from reasoning.

Secondary outcomes included model self-detection of the fabricated detail, silent adoption of the fabricated detail without explicit warning, false-positive flagging of genuine clinical content, and dangerous reasoning hallucination, defined as a hallucination that influenced the final diagnosis or management recommendation.

Automated scoring was performed by parsing the structured response fields and applying predefined boolean logic to derive binary hallucination labels and response categories. For descriptive analyses, responses were additionally grouped into four mutually exclusive categories: successful defense, silent adoption, false positive, and blind spot.

## Study Size

The study size was determined by the number of eligible psychiatry inpatient records available during the prespecified sampling window and the fixed factorial experimental design. A total of 300 eligible cases were transformed into paired short and long vignettes. Because each vignette version was evaluated under three prompting conditions across four models, the final dataset contained 7,200 response trials.

## Human Validation and Reliability

A stratified human-validation sample of 400 unique model responses was drawn across model type, prompting condition, and vignette length. These responses were distributed across four psychiatrists, with each psychiatrist reviewing 100 responses. This phase was used to provide expert clinical review of the automated response classifications.

Because the 400 responses were uniquely allocated across psychiatrists rather than co-rated in an overlapping design, the primary validation statistic was agreement between automated and expert labels, rather than psychiatrist-to-psychiatrist inter-rater reliability. For endpoint alignment with the rater task (incorporation of fabricated terms), the automated comparator was `adoption_rate_failure` and the expert comparator was psychiatrist `Hallucination_Rating`. Cohen's kappa was used to quantify agreement for this binary comparison.<sup>4</sup>

## Statistical Analysis

Descriptive statistics were used to summarize hallucination rates overall and by model, prompting condition, and vignette length. Proportions were reported with 95% confidence intervals calculated using the Wilson method.<sup>5</sup>

Comparative analyses focused on effect-size estimation rather than hypothesis-testing alone. Condition effects and vignette-length effects were summarized using absolute risk differences and risk ratios with 95% confidence intervals at the pooled trial level. Stratified summaries were generated for each model and condition combination.

Within the human-validation sample, endpoint-aligned automated labels (`adoption_rate_failure`) were compared with psychiatrist expert judgments (`Hallucination_Rating`) to assess concordance between scripted classification and clinician review. Agreement was summarized using Cohen's kappa.<sup>4</sup> As a sensitivity analysis, `hallucination_detected` (model self-detection/flagging signal) was also compared with psychiatrist ratings to evaluate label-definition effects.

All data processing, pooled analyses, and human-validation workflows were performed using project-specific Python scripts.

## Ethics and Reporting

This retrospective EMR-based study used de-identified data only and involved no direct patient contact. Patient confidentiality was protected through anonymization and restricted-access data handling. The study did not influence clinical care and was conducted as minimal-risk research using retrospective de-identified records.<sup>3</sup>

Methodological reporting was aligned, where applicable, with contemporary reporting guidance for studies involving artificial intelligence in health research.<sup>6,7</sup>

## Data Management and Quality Assurance

All extracted data and model outputs were stored in access-controlled research storage. A study codebook and labeling guide were maintained before final scoring. Random checks were used to verify consistency between source vignette text, assigned prompt condition, stored model output, and downstream pooled analysis tables.

Any missing or invalid model outputs were documented and excluded from pooled analysis only when the response could not be parsed or linked to the required trial metadata.

## References

1. Thirunavukarasu AJ, Oor A, Gramotnev G, et al. Large language models in medicine. Nat Med. 2023;29:1930-40.
2. Ji Z, Lee N, Frieske R, et al. Survey of hallucination in natural language generation. ACM Comput Surv. 2023;55(12):1-38.
3. U.S. Department of Health & Human Services. HIPAA Privacy Rule Safe Harbor for De-identification. 45 CFR 164.514(b) [Internet]. [cited 2026 Jun 29]. Available from: https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html
4. Landis JR, Koch GG. The measurement of observer agreement for categorical data. Biometrics. 1977;33(1):159-74.
5. Wilson EB. Probable inference, the law of succession, and statistical inference. J Am Stat Assoc. 1927;22(158):209-12.
6. Liu X, Rivera SC, Moher D, Calvert MJ, Denniston AK, SPIRIT-AI and CONSORT-AI Working Group. Reporting guidelines for clinical trial reports for interventions involving artificial intelligence: the CONSORT-AI extension. Nat Med. 2020;26:1364-74.
7. Rivera SC, Liu X, Chan AW, et al. Guidelines for clinical trial protocols for interventions involving artificial intelligence: the SPIRIT-AI extension. Nat Med. 2020;26:1351-63.
8. Holtzman A, Buys J, Du L, Forbes M, Choi Y. The curious case of neural text degeneration [preprint]. arXiv. 2019 [cited 2026 Jun 29]. Available from: https://arxiv.org/abs/1904.09751
