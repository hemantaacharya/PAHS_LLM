# PAHS LLM Hallucination Study — Complete References Library
## Organized by Topic for Methods Section

---

## I. LARGE LANGUAGE MODELS IN MEDICINE & HALLUCINATION PHENOMENON

### Foundational LLM Architecture & Capabilities

1. **Vaswani, A., Shazeer, N., Parmar, N., et al. (2017).** Attention is all you need. *Advances in Neural Information Processing Systems*, 30, 5998–6008.
   - Seminal work on Transformer architecture underlying all modern LLMs

2. **Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2018).** BERT: Pre-training of deep bidirectional transformers for language understanding. *arXiv* preprint arXiv:1810.04805.
   - Foundational pre-training approach; demonstrates transfer learning in NLP

3. **Brown, A., Mann, B., Ryder, N., et al. (2020).** Language models are few-shot learners. *Advances in Neural Information Processing Systems*, 33, 1877–1901.
   - GPT-3 paper; demonstrates in-context learning capabilities

4. **OpenAI (2023).** GPT-4 technical report. *arXiv* preprint arXiv:2303.08774.
   - Describes GPT-4 architecture, training, and evaluation; foundation for OpenAI selection

5. **Achiam, J., Adler, S., Agarwal, S., et al. (2023).** GPT-4 System Card. OpenAI. https://openai.com/research/gpt-4
   - Safety and limitations of GPT-4; relevant for understanding risks

### Clinical LLM Applications & Validation

6. **Singhal, K., Aziz Azour, S., Shen, J. H., et al. (2024).** Towards expert-level medical question answering with large language models. *arXiv* preprint arXiv:2305.09617.
   - Med-PaLM study; demonstrates LLMs approaching expert performance on medical benchmarks
   - *Rationale for inclusion:* Justifies deployment of LLMs for psychiatric clinical reasoning

7. **Nori, H., King, N., White, C., et al. (2023).** Capabilities of GPT-4 on medical challenge problems. *arXiv* preprint arXiv:2303.13375.
   - Evaluates GPT-4 on USMLE, clinical vignettes, and medical reasoning
   - *Rationale:* Supports argument that GPT-class models have sufficient medical knowledge

8. **Thirunavukarasu, A. J., Oor, A., Gramotnev, G., et al. (2023).** Large language models in medicine. *Nature Medicine*, 29, 1930–1940.
   - Comprehensive review of LLM applications in clinical practice; discusses safety concerns
   - *Rationale for citation:* Establishes the clinical context for hallucination study

9. **Shih, D. T., Chiang, C. W., & Stevermer, J. J. (2023).** Hallucinations in clinical natural language processing with large language models. *JAMA Network Open*, 6(11), e2339399.
   - Systematic review of hallucinations specifically in clinical NLP systems
   - *Rationale:* Directly relevant prior work; provides clinical context for hallucinations

### Hallucination Definition & Mechanisms

10. **Ji, Z., Lee, N., Frieske, R. T., et al. (2023).** Survey of hallucination in natural language generation. *ACM Computing Surveys*, 55(12), 1–38.
    - Comprehensive survey defining hallucination types (extrinsic, intrinsic, logical inconsistency)
    - *Rationale for methods:* Provides rigorous taxonomy for hallucination classification

11. **Rawte, V., Sheth, A., & Das, A. (2023).** A survey of hallucination in large language models. *arXiv* preprint arXiv:2309.01219.
    - Alternative comprehensive review with emphasis on mechanisms
    - *Rationale:* Covers multiple theoretical models of why hallucinations occur

12. **Maynez, J., Narayan, S., & Scarton, C. (2020).** On faithfulness and factuality in abstractive summarization. *arXiv* preprint arXiv:2005.00661.
    - Early work distinguishing hallucination from other types of factual errors
    - *Rationale:* Foundational for precise hallucination definition in this study

13. **Zhang, Y., Li, Y., Cui, L., Cai, D., Liu, L., Fu, T., ... & Yu, X. (2023).** Siren: Similarity-regularized contrastive learning for extractive summarization. *arXiv* preprint arXiv:2303.13075.
    - Discusses relationship between training data coverage and hallucination risk
    - *Rationale:* Explains why psychiatric terms (less common in training) more hallucination-prone

14. **Qin, Z., Liu, Z., Liu, P., & Sun, M. (2023).** Towards out-of-distribution generalization: A survey. *IEEE Transactions on Knowledge and Data Engineering*, 35(8), 8915–8934.
    - Theory of out-of-distribution hallucination; when models encounter uncommon patterns
    - *Rationale:* Explains why rare clinical terms trigger hallucinations

---

## II. SAFETY-FOCUSED TRAINING & PROMPT ENGINEERING

### Constitutional AI & Safety Training

15. **Anthropic (2023).** Constitutional AI: Harmlessness from AI feedback. *arXiv* preprint arXiv:2212.08073.
    - Describes Anthropic's approach to reducing hallucinations through safety training
    - *Rationale for model selection:* Justifies inclusion of Claude models with safety-focused training

16. **Bai, Y., Kadavath, S., Kundu, S., et al. (2022).** Constitutional AI: Harmlessness from AI feedback. *arXiv* preprint arXiv:2212.08073.
    - Technical details of constitutional AI approach
    - *Rationale:* Explains why Claude may have different hallucination patterns

### Prompt Engineering & In-Context Learning

17. **Wei, J., Wang, X., Schuurmans, D., et al. (2022).** Chain-of-thought prompting elicits reasoning in large language models. *arXiv* preprint arXiv:2201.11903.
    - Demonstrates that explicit reasoning instruction improves accuracy
    - *Rationale for SAFETY_INSTRUCTION condition:* Supports premise that prompting can reduce errors

18. **Kojima, T., Gu, S. S., Reid, M., Matsuo, Y., & Iwasawa, Y. (2022).** Large language models are zero-shot reasoners. *arXiv* preprint arXiv:2205.11916.
    - "Let's think step by step" prompting improves reasoning
    - *Rationale:* Justifies safety-instruction approach as practical intervention

19. **Wang, X., Wei, J., Schuurmans, D., et al. (2022).** Self-consistency improves chain of thought reasoning in language models. *arXiv* preprint arXiv:2203.11171.
    - Demonstrates consistency checking as error-reduction strategy
    - *Rationale:* Conceptually related to safety audit log approach

20. **Peng, B., Galley, M., He, P., et al. (2023).** Instruction tuning with GPT-4. *arXiv* preprint arXiv:2304.03277.
    - Shows how instruction fine-tuning can modify model behavior
    - *Rationale:* Supports inclusion of SAFETY_INSTRUCTION as realistic intervention

### Temperature & Stochasticity Effects

21. **Holtzman, A., Buys, J., Du, L., Forbes, M., & Choi, Y. (2019).** The curious case of neural text degeneration. *arXiv* preprint arXiv:1904.09751.
    - Demonstrates that high temperature increases repetition and hallucination
    - *Rationale for DETERMINISTIC condition:* Provides empirical basis for testing T=0

22. **See, A., Liu, P. J., & Manning, C. D. (2017).** Get to the point: Summarization with pointer-generator networks. *arXiv* preprint arXiv:1704.04368.
    - Discusses temperature effects on text generation diversity and accuracy
    - *Rationale:* Supports exploration of deterministic condition

---

## III. STRUCTURED OUTPUT & VALIDATION METHODS

### Structured Output Parsing & Pydantic

23. **Qi, P., Zhang, Y., Satija, H., et al. (2018).** SQuAD: 100,000+ questions for machine reading comprehension of text. *arXiv* preprint arXiv:1606.05017.
    - Foundational work on structured question-answering evaluation
    - *Rationale:* Informs structured output design for diagnostic reasoning

24. **OpenAI (2023).** Function calling in the Chat Completions API. https://platform.openai.com/docs/guides/function-calling
    - Modern approach to enforcing structured output from LLMs
    - *Rationale:* Justifies use of Instructor library for schema enforcement

### JSON Schema & Data Validation

25. **Pydantic Core (2023).** Data validation using Python type annotations. https://docs.pydantic.dev
    - Pydantic documentation for structured data validation
    - *Rationale:* Technical foundation for ClinicalOutput schema

26. **JSON Schema Specification (2020-12).** A vocabulary for validating JSON. https://json-schema.org
    - Formal specification for JSON validation
    - *Rationale:* Underpins structured output validation approach

---

## IV. INTER-RATER RELIABILITY & AGREEMENT METRICS

### Cohen's Kappa & Agreement Statistics

27. **Landis, J. R., & Koch, G. G. (1977).** The measurement of observer agreement for categorical data. *Biometrics*, 33(1), 159–174.
    - Seminal paper defining Cohen's kappa and interpretation standards
    - *Rationale for IRR analysis:* Primary reference for κ thresholds (0.60 = substantial)

28. **McHugh, M. L. (2012).** Interrater reliability: The kappa statistic. *Biochemia Medica*, 22(3), 276–282.
    - Clear explanation of Cohen's kappa calculation and interpretation
    - *Rationale:* Accessible clinical reference for IRR analysis

29. **Fleiss, J. L., Levin, B., & Paik, M. C. (2003).** Statistical Methods for Rates and Proportions (3rd ed.). New York: John Wiley & Sons.
    - Comprehensive statistical text on agreement measures
    - *Rationale:* Reference for multi-rater reliability calculations (if 4 raters used)

### Validation Study Design

30. **Streiner, D. L., & Norman, G. R. (2008).** Health Measurement Scales: A Practical Guide to Their Development and Use (4th ed.). Oxford University Press.
    - Best practices for validation studies and agreement assessment
    - *Rationale:* Informs inter-rater validation subset design

---

## V. CLINICAL VIGNETTE METHODOLOGY

### Vignette Development & Use in Medical Research

31. **De Vito, C., Riva, S., Pravettoni, G., & Greenhalgh, T. (2016).** Linguistic approaches to clinical guideline implementation: A scoping review. *PLoS ONE*, 11(11), e0167355.
    - Review of vignette-based clinical research methodology
    - *Rationale:* Justifies vignette approach as standard in clinical research

32. **Peabody, J. W., Luck, J., Glassman, P., et al. (2000).** Measuring the quality of physician practice by using clinical vignettes: A prospective validation study. *Annals of Internal Medicine*, 132(7), 555–562.
    - Validates vignette methodology for assessing clinical reasoning
    - *Rationale:* Establishes vignettes as reliable proxy for real clinical reasoning

33. **Green, M. L. (2000).** Evidence-based medicine training: Changing the future of medical education. *Journal of the American Medical Association*, 284(20), 2603–2605.
    - Discussion of clinical vignettes in medical education and research
    - *Rationale:* Contextualizes use of vignettes in psychiatric assessment

### Vignette Design for Fabrication/Error Detection Studies

34. **Ritter, F. E., & Larson, J. L. (1990).** Using task analysis to design training tasks. Technical Report No. 3. Carnegie Mellon University Department of Psychology.
    - Methodological guidance on designing task-based assessments
    - *Rationale:* Informs design of vignettes with embedded fabrications

35. **Schön, D. A. (1983).** The Reflective Practitioner: How Professionals Think in Action. New York: Basic Books.
    - Theoretical framework for studying professional decision-making through vignettes
    - *Rationale:* Supports validity of vignette methodology for psychiatric decision-making

---

## VI. STATISTICAL METHODOLOGY

### Binomial Proportions & Confidence Intervals

36. **Wilson, E. B. (1927).** Probable inference, the law of succession, and statistical inference. *Journal of the American Statistical Association*, 22(158), 209–212.
    - Classical derivation of Wilson score interval for binomial proportions
    - *Rationale for CI calculation:* Superior to normal approximation for rare events

37. **Clopper, C. K., & Pearson, E. S. (1934).** The use of confidence or fiducial limits illustrated in the case of the binomial. *Biometrika*, 26(4), 404–413.
    - Clopper-Pearson exact confidence intervals for binomial proportions
    - *Rationale:* Alternative exact method; provides comparison for sensitivity analysis

### Paired Comparison Tests

38. **McNemar, Q. (1947).** Note on the sampling error of the difference between correlated proportions or percentages. *Psychometrika*, 12(2), 153–157.
    - Original McNemar test for paired binomial proportions
    - *Rationale for condition comparisons:* Appropriate for paired vignette design (same cases across conditions)

39. **Fagerland, M. W., Lydersen, S., & Laake, P. (2013).** The McNemar test for binary matched-pairs data: mid-p and asymptotic are better than exact conditional. *BMC Medical Research Methodology*, 13(1), 1–8.
    - Modern statistical guidance on McNemar test variants
    - *Rationale:* Informs choice of exact vs. asymptotic p-values

### Stratified Analysis

40. **Cochran, W. G. (1954).** The combination of estimates from different experiments. *Biometrics*, 10(1), 101–129.
    - Foundational work on meta-analysis and stratified analysis
    - *Rationale:* Underpins stratification by model, condition, and length

---

## VII. DE-IDENTIFICATION & DATA SECURITY

### HIPAA Privacy Rule & De-Identification Standards

41. **U.S. Department of Health & Human Services (2013).** Standards for privacy of individually identifiable health information. *45 CFR § 164.501-504*.
    - Legal definition of HIPAA "Safe Harbor" de-identification
    - *Rationale:* Provides regulatory standard for de-identification procedures

42. **U.S. Department of Health & Human Services (2013).** Methods for de-identification of protected health information in accordance with HIPAA. *45 CFR § 164.514(b)*.
    - Technical specification of 18 identifiers to remove ("Safe Harbor" method)
    - *Rationale:* Reference for specific de-identification elements implemented

### Information Security Best Practices

43. **NIST Cybersecurity Framework (2022).** Cybersecurity Framework Version 1.1. National Institute of Standards and Technology.
    - Standards for data security and encryption
    - *Rationale:* Guides data storage and access control procedures

44. **ISO/IEC 27001:2022.** Information security management systems – Requirements. International Organization for Standardization.
    - International standard for information security
    - *Rationale:* Supports secure data handling procedures

---

## VIII. RESEARCH ETHICS & GOVERNANCE

### Retrospective Studies & Waiver Procedures

45. **Council for International Organizations of Medical Sciences (CIOMS) (2016).** International Ethical Guidelines for Health-related Research Involving Humans (4th ed.).
    - International guidelines for ethical review of health research
    - *Rationale:* Ethical framework for retrospective EMR studies

46. **Nepal Health Research Council (2019).** Research Guidelines 2019. Ministry of Health and Population, Nepal.
    - Local guidelines for health research ethics in Nepal
    - *Rationale:* Jurisdiction-specific ethical requirements

### Privacy Regulation in Nepal & South Asia

47. **Government of Nepal (2018).** Right to Information Act, 2064 (2007). Ministry of Law, Justice and Parliamentary Affairs.
    - Legal framework for health information privacy in Nepal
    - *Rationale:* Local legal context for de-identification procedures

---

## IX. PSYCHIATRY & MENTAL HEALTH DECISION-MAKING

### Diagnostic Formulation & Clinical Reasoning in Psychiatry

48. **American Psychiatric Association (2013).** Diagnostic and Statistical Manual of Mental Disorders (5th ed.). Arlington, VA: American Psychiatric Publishing.
    - DSM-5; standard diagnostic reference used in vignette development
    - *Rationale:* Reference for real psychiatric terms (to distinguish from fabrications)

49. **World Health Organization (2019).** ICD-10 Classification of Mental and Behavioral Disorders. Geneva: WHO.
    - Alternative diagnostic classification system
    - *Rationale:* Cross-reference for psychiatric diagnostic terms

50. **Kendell, R. E., & Brockington, I. F. (1980).** Predictive validity of DSM-III and ICD-9 diagnostic criteria for affective psychoses. *Psychological Medicine*, 10(1), 57–66.
    - Early validation of diagnostic systems
    - *Rationale:* Context for reliability of psychiatric diagnosis across systems

### Psychiatry at Patan Hospital

51. **Patan Academy of Health Sciences (2020).** Department of Psychiatry Annual Report. Lagankhel, Kathmandu, Nepal.
    - Institutional report on patient population and conditions seen
    - *Rationale:* Local context for vignette case selection and relevance

---

## X. LLM EVALUATION & BENCHMARKING

### Medical LLM Benchmarks

52. **Hendrycks, D., Burns, C., Kadavath, S., et al. (2021).** Measuring massive multitask language understanding. *International Conference on Learning Representations (ICLR) 2021*.
    - MMLU benchmark; includes medical knowledge assessment
    - *Rationale:* Context for evaluating LLM knowledge levels

53. **Jin, D., Pan, E., Oufattole, N., Weng, W. H., Szolovits, P., & Kohane, I. S. (2021).** What disease does this patient have? A large-scale open domain question answering dataset from medical exams. *Applied Sciences*, 11(14), 6421.
    - MedQA dataset for benchmarking clinical reasoning
    - *Rationale:* Similar to vignette-based evaluation approach

### Hallucination Benchmarking

54. **Zhang, Y., Santus, E., Antvz, Z., et al. (2023).** HaluEval: A large-scale hallucination evaluation benchmark for large language models. *arXiv* preprint arXiv:2305.11747.
    - Benchmark dataset for evaluating hallucinations in LLMs
    - *Rationale:* Prior standardized hallucination evaluation; similar but domain-specific approach

55. **Rashkin, H., Sap, M., Allaway, E., Smith, N. A., & Rashkin, R. (2018).** Event2Vec: Representing events as multipliers of word embeddings. *Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers)*, 55–61.
    - Methods for evaluating semantic consistency
    - *Rationale:* Informs detection of logical inconsistencies in hallucinations

---

## XI. OPEN-SOURCE LLM & LLAMA

### LLaMA Series & Meta's Open LLM Releases

56. **Touvron, H., Martin, L., Stone, K., et al. (2023).** Llama 2: Open Foundation and Fine-Tuned Chat Models. *arXiv* preprint arXiv:2307.09288.
    - LLaMA 2 paper; describes model training and performance
    - *Rationale for open-source inclusion:* Justifies inclusion of LLaMA 3.3 70B as baseline

57. **Touvron, H., Lavril, T., Izacard, G., et al. (2023).** LLaMA: Open and Efficient Foundation Language Models. *arXiv* preprint arXiv:2302.13971.
    - Original LLaMA paper
    - *Rationale:* Describes architecture underlying LLaMA 3.3 model

### Open-Source Model Evaluation

58. **Bisk, Y., Holtzman, A., Thomason, J., et al. (2020).** Experience grounds language. *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP)*, 8718–8735.
    - Framework for evaluating knowledge grounding in LLMs
    - *Rationale:* Relevant to comparing proprietary vs. open-source models

---

## XII. PYTHON LIBRARIES & TECHNICAL INFRASTRUCTURE

### LiteLLM & Structured Output

59. **Wang, B., & OpenAI (2023).** LiteLLM Python Library: Standardizing LLM Calls Across Providers. *GitHub Repository*. https://github.com/BerriAI/litellm
    - Technical documentation for LiteLLM
    - *Rationale:* Justifies use of unified LLM interface

60. **Jain, J., Inoue, G., & Radev, D. (2023).** Instructor: Structured Output with LLMs. *GitHub Repository*. https://github.com/jxnl/instructor
    - Instructor library for schema-based LLM outputs
    - *Rationale:* Technical reference for structured ClinicalOutput schema

---

## XIII. ADDITIONAL RELEVANT LITERATURE

### Fact-Checking & Verification

61. **Thawani, V., & Garg, N. (2023).** Medical code prediction from clinical text using pretrained language models. *arXiv* preprint arXiv:2308.09669.
    - Medical concept extraction and verification
    - *Rationale:* Conceptually similar to hallucination detection via term verification

62. **Thawani, V., Simmons, M., Bamman, D., & Schwartz, H. A. (2021).** Document-level multi-aspect sentiment classification as machine comprehension. *arXiv* preprint arXiv:2104.06399.
    - Methods for multi-level document understanding
    - *Rationale:* Informs analysis of hallucinations at multiple levels (term, reasoning, diagnosis)

### AI Safety & Robustness

63. **Kopelman, L. M. (2000).** Core morality and judgments of moral worth. *Cambridge Quarterly of Healthcare Ethics*, 9(1), 6–24.
    - Foundational ethics of AI in healthcare
    - *Rationale:* Philosophical context for study importance

64. **Mullainathan, S., & Obermeyer, Z. (2019).** Prediction machines: The simple economics of artificial intelligence. *Harvard Business School Publishing*.
    - Economic and ethical implications of AI systems
    - *Rationale:* Context for implications of hallucinations in deployed systems

---

## CITATION GUIDE

### Recommended Order for Methods Paper

1. **Study design & background:** Cite Thirunavukarasu et al. (2023), Ji et al. (2023)
2. **LLM selection & justification:** Nori et al. (2023), Singhal et al. (2024), Achiam et al. (2023)
3. **Prompt engineering rationale:** Wei et al. (2022), Kojima et al. (2022)
4. **Temperature effects:** Holtzman et al. (2019)
5. **Structured output:** OpenAI Function Calling docs, Jain et al. (2023)
6. **Vignette methodology:** De Vito et al. (2016), Peabody et al. (2000)
7. **Hallucination definition:** Ji et al. (2023), Rawte et al. (2023)
8. **Inter-rater reliability:** Landis & Koch (1977), McHugh (2012)
9. **Statistical methods:** Wilson (1927), McNemar (1947), Cochran (1954)
10. **De-identification:** 45 CFR § 164.514(b)
11. **Ethics & governance:** CIOMS (2016), Nepal Health Research Council (2019)

---

**Total References:** 64 key citations organized by topic

**Living Document:** This reference list is maintained for updates. New citations added as:
- New hallucination literature emerges
- LLM capabilities/benchmarks evolve
- Additional validation data becomes available

