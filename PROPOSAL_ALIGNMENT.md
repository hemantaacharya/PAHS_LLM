# PAHS LLM Study — Proposal to Repository Alignment

## Study Overview
**Title:** Hallucination Patterns in Large Language Models Processing Psychiatric Vignettes from Patan Hospital

**General Objective:** Evaluate the occurrence and patterns of hallucinations by large language models (LLMs) when processing psychiatry vignettes derived from real inpatient cases at Patan Hospital.

---

## Specific Objectives — Implementation Status

### ✅ Objective 1: Develop Standardized Psychiatry Vignettes
**Proposal:** Create de-identified vignettes from inpatient records with one deliberate fabricated detail each. Two versions per vignette (short 50–60 words; long 90–100 words).

**Repository Implementation:**
- **File:** `02_data/experimental/combined_vignettes_clean.json`
- **Status:** COMPLETE
- **Details:**
- 300 vignettes extracted from de-identified EMR
  - Each has `vignette_pair.short` and `vignette_pair.long`
  - Each contains `token_text` (fabricated detail) and `category`
  - Format: JSON array with `case_id`, `token_id`, and blind IDs per length

**Example structure:**
```json
{
  "case_id": "batch1_50__1",
  "token_text": "care coordination continuity score",
  "vignette_pair": {
    "short": {"blind_id": "1_S", "content": "...~60 words..."},
    "long": {"blind_id": "1_L", "content": "...~90-100 words..."}
  }
}
```

---

### ✅ Objective 2: Test LLMs Under Different Conditions
**Proposal:** Test multiple LLMs under three conditions:
1. DEFAULT: Standard system prompt
2. SAFETY_INSTRUCTION: Enhanced safety checking
3. DETERMINISTIC: Temperature = 0 (deterministic)

**Models included in proposal:**
- 3 paid models (OpenAI, Anthropic, Google)
- 1 open-source model (as baseline)

**Repository Implementation:**
- **File:** `pilot.py` (main entry point) and `main.py`
- **Paid Models:** ✅ TESTED
  - `openai/gpt-5.4-mini` (env var: `PAHS_OPENAI_MODEL`)
  - `anthropic/claude-haiku-4-5` (env var: `PAHS_ANTHROPIC_MODEL`)
  - `gemini/gemini-3.1-flash-lite` (env var: `PAHS_GEMINI_MODEL`)
- **Open-Source Model:** ⏳ PENDING
  - Default support: None (requires env var: `PAHS_OPENSOURCE_MODEL`)
  - Recommended: `groq/llama2-70b-4096` or `ollama/llama2`
  - Setup: See `OPENSOURCE_MODEL_SETUP.md`
- **Conditions:** Defined in `pilot.py` lines 594–610
  - DEFAULT: baseline system role
  - SAFETY_INSTRUCTION: adds "verify all metrics... exclude from reasoning"
  - DETERMINISTIC: temperature=0 + baseline role
- **Status:** ✅ Paid models COMPLETE; ⏳ Open-source PENDING

**Execution:** 
```bash
# Paid models
python pilot.py  (3 paid + 1 open-source)
- Prompt condition (DEFAULT, SAFETY_INSTRUCTION, DETERMINISTIC)
- Vignette length (short vs. long)

**Repository Implementation:**
- **Raw Results:** `04_results/raw_json/*.json`
  - ✅ PAHS_STUDY_RESULTS_2026_openai_gpt-5.4-mini.json (1,758 rows)
  - ✅ PAHS_STUDY_RESULTS_2026_anthropic_claude-haiku-4-5.json (1,758 rows)
  - ✅ PAHS_STUDY_RESULTS_2026_gemini_gemini-3.1-flash-lite.json (1,758 rows)
  - ⏳ PAHS_STUDY_RESULTS_2026_groq_llama2-70b-4096.json (1,758 rows) — PENDING
  - Total: 5,274 main study rows (awaiting open-source)lucination Rates by Model, Condition, Length
**Proposal:** Calculate hallucination rates stratified by:
- LLM model type
- Prompt condition (DEFAULT, SAFETY_INSTRUCTION, DETERMINISTIC)
- Vignette length (short vs. long)

**Repository Implementation:**
- **Raw Results:** `04_results/raw_json/*.json`
  - PAHS_STUDY_RESULTS_2026_openai_gpt-5.4-mini.json (1758 rows)
  - PAHS_STUDY_RESULTS_2026_anthropic_claude-haiku-4-5.json (1758 rows)
  - PAHS_STUDY_RESULTS_2026_gemini_gemini-3.1-flash-lite.json (1758 rows)
  - Total: 5,274 main study rows

- **Analysis:** `03_src/evaluation/extract_hallucination_data.py`
  - Extracts hallucination-focused records
  - Defines categories: Successful Defense, Silent Adoption, False Positive, Blind Spot
  - Maps to boolean logic: `hallucination_detected`, `adoption_rate_failure`, `detection_rate_success`, `dangerous_reasoning_hallucination`

- **Pooled Analysis:** `03_src/evaluation/pool_hallucination_analysis.py`
  - Aggregates across all models
  - Stratifies by: model, condition, vignette length
  - Output: `04_results/analysis_ready/pooled/*.csv`

- **Status:** COMPLETE
- **Output paths:**
  - Hallucination-focused JSON: `04_results/analysis_ready/*_hallucination_focus.json`
  - Summary JSON: `04_results/analysis_ready/*_summary.json`
  - Dashboard: `04_results/analysis_ready/*_DASHBOARD.md`

---

### ✅ Objective 4: Compare Hallucination Risk by Vignette Length
**Proposal:** Assess whether shorter vignettes (50–60 words) increase hallucination risk compared to longer (90–100 words).

**Repository Implementation:**
- **Data field:** `length` in all result rows (values: "short", "long")
- **Analysis:** Pooled analysis includes `by_vignette_length` summaries
- **Visualization:** `scripts/generate_reports.py` and `scripts/generate_top3_visuals.py`
  - Plots hallucination rate by vignette length and condition
- **Status:** COMPLETE

---

### ⚠️ Objective 5: Assess Inter-Rater Reliability
**Proposal:** Two psychiatrists independently code a subset (20% or pilot subset) of outputs for hallucination labeling. Report Cohen's kappa with 95% CI.

**Repository Implementation:**
- **Status:** NOT YET IMPLEMENTED
- **Gap:** No inter-rater labeling workflow in place

**Proposed Solution:**
1. Create inter-rater module: `03_src/evaluation/interrater_reliability.py` ✅ (created in this session)
2. Define subset for manual review (pilot set + 20% of main study)
3. Implement rater interface template for independent labeling
4. Calculate Cohen's kappa with 95% CI per Landis & Koch (1977)
5. Stratify agreement by condition, length, and model

**Module location:** `03_src/evaluation/interrater_reliability.py`
- Implements `cohens_kappa()` function
- Generates stratified agreement summaries
- Usage:
  ```bash
  python 03_src/evaluation/interrater_reliability.py labeled_output.json --output summary.json
  ```

---

## Data Schema and Output Mapping

### Raw Result Format
Each row in `raw_json/*.json`:
```json
{
  "model": "openai/gpt-5.4-mini",
  "requested_model": "openai/gpt-5.4-mini",
  "condition": "DEFAULT",
  "length": "short",
  "case_id": "batch1_50__1",
  "target_token": "care coordination continuity score",
  "output": {
    "primary_presentation": "...",
    "top_diagnosis": "...",
    "safety_audit_log": [...],
    "hallucination_detected": true/false,
    "diagnostic_confidence": 0-100,
    "recommended_management": [...]
  },
  "timestamp": "2026-05-25T13:29:43.123456"
}
```

### Analysis (Hallucination-Focused) Format
Example from `*_hallucination_focus.json`:
```json
{
  "trial_metadata": {
    "model": "openai/gpt-5.4-mini",
    "condition": "DEFAULT",
    "case_id": "batch1_50__1",
    "vignette_length": "short"
  },
  "output": {
    "hallucination_detected": true,
    "diagnostic_confidence": 75,
    "top_diagnosis": "..."
  },
  "boolean_logic": {
    "target_token": "care coordination continuity score",
    "token_in_diagnostic_reasoning": true,
    "token_in_final_diagnosis": true,
    "token_identified_in_safety_audit": true,
    "adoption_rate_failure": true,
    "detection_rate_success": false,
    "dangerous_reasoning_hallucination": true
  },
  "analysis": {
    "category": "Silent Adoption",
    "meaning_and_clinical_risk": "..."
  }
}
```

---

## Current Study Completion Status

| Objective | Status | % Complete | Notes |
|-----------|--------|-----------|-------|
| 1. Vignette development | ✅(paid) | ✅ Complete | 75% | 3 paid models × 3 conditions × 300 vignettes |
| 2. Multi-condition testing (OSS) | ⏳ Pending | 25% | Open-source baseline awaits completion |
| 3. Hallucination rate calc (paid) | ✅ Complete | 75% | 5,400 paid model rows analyzed |
| 3. Hallucination rate calc (OSS) | ⏳ Pending | 25% | Awaiting open-source data |
| 4. Length comparison | ✅ Complete | 100% | Stratified by short/long (paid models) |
| 5. Inter-rater reliability | ⚠️ Pending | 0% | Module created; awaits manual rater labels |
| Descriptive statistics | ✅ Complete | 75% | Dashboard, CSV, pooled analysis (paid models) |
| Comparative analysis | ✅ Complete | 75% | Model vs. condition vs. length (paid models)sis |
| Comparative analysis | ✅ Complete | 100% | Model vs. condition vs. length |

---

## Remaining Tasks for Full Study Completion

### Must Complete (High Priority)
1. **Inter-Rater Labeling Workflow**
   - Select 20% of main study (352 rows) + all pilot (153 rows) = ~505 cases for dual review
   - Create rater instruction/template
   - Have two psychiatrists independently label `hallucination_detected` boolean
   - Merge labels into single JSON with `rater_1_hallucination` and `rater_2_hallucination` fields
   - Run `interrater_reliability.py` to calculate Cohen's kappa

2. **Formal Methods Documentation**
   - Complete Methods section with all details per proposal (sampling, sample size, variables, data processing)
   - Include participant safety, ethical clearance narrative

3. **Results Writing**
   - Generate tables per proposal dummy tables (Table B)
   - Report hallucination rates with CI
   - Present inter-rater kappa with 95% CI

### Should Complete (Medium Priority)
1. Final dashboard combining all outputs
2. Publication-ready figures (hallucination rate by model/condition/length)
3. Conflict of interest documentation

### Optional (Low Priority)
1. Adverse event documentation (if any)
2. Data retention plan confirmation

---

## Key Files Reference

| File/Path | Purpose |
|-----------|---------|
| `pilot.py` | Main study runner (CLI interface) |
| `main.py` | Alternative study entry point |
| `02_data/experimental/combined_vignettes_clean.json` | Input vignette dataset (300) |
| `04_results/raw_json/*.json` | Raw model outputs |
| `04_results/analysis_ready/*_summary.json` | Hallucination summary metrics |
| `04_results/analysis_ready/*_DASHBOARD.md` | Human-readable results dashboard |
| `03_src/evaluation/extract_hallucination_data.py` | Hallucination labeling logic |
| `03_src/evaluation/interrater_reliability.py` | Cohen's kappa module (NEW) |
| `03_src/evaluation/pool_hallucination_analysis.py` | Pooled multi-model analysis |
| `03_src/core/schemas.py` | Output data model (Pydantic) |

---

## Ethical & Regulatory Status

✅ **Patient Confidentiality:** All vignettes de-identified; no identifiable data in results  
✅ **Data Storage:** Password-protected local computer  
⚠️ **IRC Approval:** Assumed waived for minimal-risk retrospective study (per proposal)  
✅ **Data Retention Plan:** 5 years minimum storage  

---

*Document generated: May 25, 2026*  
*Study Status: Phase 2 (inter-rater reliability in progress)*
