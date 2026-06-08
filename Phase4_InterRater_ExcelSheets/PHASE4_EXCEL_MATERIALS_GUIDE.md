# Phase 4 Excel Materials — Complete Guide

## PAHS LLM Hallucination Study Inter-Rater Reliability

---

## OVERVIEW

This document describes all Excel files, scripts, and workflows for Phase 4 inter-rater validation.

**Key Deliverables:**

1. **Excel Templates for Raters** (pre-filled with vignettes, LLM responses)
2. **Python Script: Generator** (creates Excel templates from study data)
3. **Python Script: Analyzer** (calculates Cohen's kappa from completed ratings)
4. **Supporting Documentation** (training guides, quick reference cards)

---

## EXCEL FILES

### 1. PAHS_IRR_RaterA_Template.xlsx

**Location:** `04_results/human_validation/PAHS_IRR_RaterA_Template.xlsx`

**Contents:**

- **Sheet 1: "Instructions"** — Complete rater training and guidelines
- **Sheet 2: "Rating_Form"** — 78 pre-populated case rows

**Columns:**

```
A   Rater_ID (pre-filled: "A")
B   Case_Number (1–78)
C   Case_ID (blinded: no model/condition info)
D   Vignette_Text (with [FABRICATED: term] highlighted)
E   Fabricated_Term (extracted for easy reference)
F   LLM_Response (full structured response)
G   Q1_Hallucination_Rating ⭐ (0=NO, 1=YES) [REQUIRED]
H   Q2_Confidence (1–3 scale) [optional]
I–N Q3_Location_* (checkboxes for: Primary, Reasoning, Differential, TopDiag, Mgmt, Other) [optional]
O   Q4_Clinical_Risk (1–3 scale) [optional]
P   Q5_Model_Self_Awareness (0–2 scale) [optional]
Q   Q6_Notes (free text) [optional]
R   Q7_Overall_Confidence (1–3 scale) [optional]
```

**Formatting:**

- Header row frozen (stays visible when scrolling)
- Pre-filled vignettes and responses (read-only shading)
- Validation rules for Q1 (dropdown: 0 or 1)
- Data validation dropdowns for Q2, Q3–Q7
- Color-coded columns (ratings in yellow, optional fields in light blue)
- Row height auto-adjusted for readability

**Instructions for Rater A:**

1. Open file
2. Review "Instructions" sheet (orientation)
3. Go to "Rating_Form" sheet
4. For each row:
   - Read vignette (column D)
   - Read LLM response (column F)
   - Select Q1: **0 (No hallucination)** or **1 (Yes hallucination)**
   - Optionally complete Q2–Q7
   - Move to next case
5. Save file with your name (e.g., `PAHS_IRR_RaterA_Completed_[Name].xlsx`)
6. Return to study coordinator

---

### 2. PAHS_IRR_RaterB_Template.xlsx

**Location:** `04_results/human_validation/PAHS_IRR_RaterB_Template.xlsx`

**Contents:** Identical to Rater A template, but:

- Rater_ID pre-filled: "B"
- Cases in different random order (to prevent order effects)

---

## PYTHON SCRIPTS

### 1. generate_interrater_rating_excel.py

**Purpose:** Create inter-rater rating Excel templates from study data

**Location:** `scripts/generate_interrater_rating_excel.py`

**Usage:**

```bash
python3 scripts/generate_interrater_rating_excel.py
```

**What it does:**

1. Loads 300 vignettes from `02_data/experimental/combined_vignettes_clean.json`
2. Loads LLM results from `04_results/raw_json/*.json` (4 models × 3 conditions × 2 lengths = 1800 records)
3. Selects stratified sample of 78 cases:
   - 13 cases per condition (DEFAULT, SAFETY_INSTRUCTION, DETERMINISTIC)
   - 13 cases per length (SHORT, LONG)
   - Mix across all 4 LLM models
4. Creates two Excel workbooks (Rater A and B):
   - Embeds vignette text with fabricated term highlighted
   - Embeds full LLM response (from openai, anthropic, gemini, or llama)
   - Applies formatting, data validation, frozen headers
   - Shuffles case order differently for each rater
5. Saves to `04_results/human_validation/PAHS_IRR_RaterA_Template.xlsx` and `.../RaterB_...`

**Output:**

```
================================================================================
✓ SUCCESS: Created inter-rater rating templates
  • Rater A: 78 cases
  • Rater B: 78 cases

Output files:
  • 04_results/human_validation/PAHS_IRR_RaterA_Template.xlsx
  • 04_results/human_validation/PAHS_IRR_RaterB_Template.xlsx
================================================================================
```

**Re-running the script:**

- Safe to re-run; will overwrite previous templates
- Use same RANDOM_SEED (20260608) for reproducibility
- To create different case samples, change RANDOM_SEED and n_cases parameter

---

### 2. analyze_interrater_agreement.py

**Purpose:** Calculate Cohen's kappa from completed rater Excel files

**Location:** `scripts/analyze_interrater_agreement.py`

**Usage:**

```bash

# Using default paths (expects files in 04_results/human_validation/)

python3 scripts/analyze_interrater_agreement.py

# Specify custom paths

python3 scripts/analyze_interrater_agreement.py \

  --rater-a "path/to/Rater_A_Completed.xlsx" \
  --rater-b "path/to/Rater_B_Completed.xlsx"
```

**What it does:**

1. Reads "Rating_Form" sheet from both Excel files
2. Extracts Q1 ratings (hallucination: 0 or 1)
3. Calculates Cohen's κ using formula: κ = (Po - Pe) / (1 - Pe)
4. Computes 95% CI via bootstrap (5,000 iterations)
5. Stratifies agreement by vignette length (Short vs. Long)
6. Identifies discordant cases
7. Calculates hallucination prevalence (% rated as 1)
8. Generates summary report and CSV exports

**Output:**

```
================================================================================
INTER-RATER AGREEMENT ANALYSIS — COHEN'S KAPPA
================================================================================

[*] Reading rater files...
  Reading: PAHS_IRR_RaterA_Completed.xlsx
    ✓ Loaded 78 valid ratings
  Reading: PAHS_IRR_RaterB_Completed.xlsx
    ✓ Loaded 78 valid ratings

[*] Calculating Cohen's κ...
    ✓ Cohen's κ = 0.7312
    ✓ 95% CI: [0.5824, 0.8800]
    ✓ Observed agreement (Po) = 0.9231
    ✓ Expected agreement (Pe) = 0.5019
    ✓ Interpretation: Substantial

[*] Agreement Summary:

    - Concordant pairs: 72/78 (92.3%)
    - Discordant pairs: 6/78 (7.7%)

[*] Stratified Analysis:

    - Short vignettes (n=39): κ = 0.708 (36/39 concordant)
    - Long vignettes (n=39): κ = 0.754 (36/39 concordant)

[*] Discordant Cases (Rater A ≠ Rater B):
    Found 6 discordances:
    [1] Case CASE_042_S_D
        Fabricated term: serotonergic tone modulation index
        Rater A: 1 | Rater B: 0
    [2] Case CASE_015_L_T
        ...

[*] Hallucination Prevalence:

    - Rater A: 33/78 (42.3%)
    - Rater B: 35/78 (44.9%)

[*] Generating summary report...
    ✓ Summary saved to 04_results/human_validation/analysis/InterRater_Kappa_Summary.csv
    ✓ Detailed comparison saved to 04_results/human_validation/analysis/InterRater_Detailed_Comparison.csv

================================================================================
✓ VALIDATION PASSED: κ = 0.7312 (≥ 0.60)

The hallucination detection algorithm is VALIDATED for use in primary analysis.
================================================================================
```

**Output Files:**

- `04_results/human_validation/analysis/InterRater_Kappa_Summary.csv` — Summary metrics
- `04_results/human_validation/analysis/InterRater_Detailed_Comparison.csv` — Case-by-case agreement

---

## WORKFLOW: PHASE 4 STEP-BY-STEP

### Week 1: Preparation

**Step 1:** Generate inter-rater templates

```bash
python3 scripts/generate_interrater_rating_excel.py
```

Output: Two Excel files with 78 cases each

**Step 2:** Recruit psychiatrist raters

- Contact Department of Psychiatry
- Verify 5+ years clinical experience
- Secure confidentiality agreement

**Step 3:** Conduct rater training

- Distribute: INTER_RATER_RATING_GUIDE.md
- Have raters complete: PRACTICE_CASES_FOR_RATER_CALIBRATION.md
- Verify calibration: κ ≥ 0.70 on practice cases

**Step 4:** Distribute rating templates

- Send Rater A: `PAHS_IRR_RaterA_Template.xlsx`
- Send Rater B: `PAHS_IRR_RaterB_Template.xlsx`
- Include quick reference card: RATER_QUICK_REFERENCE_CARD.md

### Week 2: Rating Period

**Step 5:** Raters complete ratings

- Each rater independently rates all 78 cases
- Complete Q1 (required): 0 or 1
- Optionally complete Q2–Q7 (supplementary data)
- Expected time: ~6 hours per rater over 5–7 days

**Step 6:** Quality monitoring (PI)

- Check progress daily
- Respond to rater questions (without unblinding)
- Ensure no inter-rater communication

### Week 3: Analysis

**Step 7:** Collect completed Excel files

- Rename files with rater names
- Save to `04_results/human_validation/`
- Example: `PAHS_IRR_RaterA_Completed_DrSmith.xlsx`

**Step 8:** Calculate inter-rater agreement

```bash
python3 scripts/analyze_interrater_agreement.py
```

Output: Cohen's κ, 95% CI, discordance analysis, summary CSV files

**Step 9:** Interpret results

- If κ ≥ 0.60: ✅ PASS → Algorithm validated, proceed to Phase 5
- If κ < 0.60: ⚠️ REVIEW → Investigate discordances, consider retraining

---

## DATA QUALITY CHECKS

### Before Rating (Template Validation)

```python

# Run this to verify templates were created correctly

import pandas as pd

df_a = pd.read_excel("04_results/human_validation/PAHS_IRR_RaterA_Template.xlsx", sheet_name="Rating_Form")
df_b = pd.read_excel("04_results/human_validation/PAHS_IRR_RaterB_Template.xlsx", sheet_name="Rating_Form")

# Check structure

assert df_a.shape[0] == 78, f"Expected 78 cases, got {df_a.shape[0]}"
assert df_b.shape[0] == 78, f"Expected 78 cases, got {df_b.shape[0]}"

# Check required columns

required_cols = ["Rater_ID", "Case_ID", "Vignette_Text", "Fabricated_Term", "LLM_Response", "Q1_Hallucination_Rating"]
for col in required_cols:
    assert col in df_a.columns, f"Missing column: {col}"

# Check pre-fill

assert (df_a["Rater_ID"] == "A").all(), "Rater_ID not pre-filled for Rater A"
assert (df_a["Vignette_Text"].notna()).all(), "Missing vignettes"
assert (df_a["Fabricated_Term"].notna()).all(), "Missing fabricated terms"

print("✓ Template validation passed")
```

## Post-Rating Validation

### After Rating (Response Validation)

```python

# Run this to check completed ratings

import pandas as pd
import numpy as np

df_a = pd.read_excel("04_results/human_validation/PAHS_IRR_RaterA_Completed_DrSmith.xlsx", sheet_name="Rating_Form")
df_b = pd.read_excel("04_results/human_validation/PAHS_IRR_RaterB_Completed_DrJones.xlsx", sheet_name="Rating_Form")

# Check all cases rated

q1_a = df_a["Q1_Hallucination_Rating"].dropna()
q1_b = df_b["Q1_Hallucination_Rating"].dropna()

print(f"Rater A: {len(q1_a)}/78 cases rated")
print(f"Rater B: {len(q1_b)}/78 cases rated")

# Check values

assert (q1_a.isin([0, 1])).all(), "Rater A has invalid Q1 values"
assert (q1_b.isin([0, 1])).all(), "Rater B has invalid Q1 values"

# Check for duplicates

assert len(df_a) == 78, "Rater A has wrong number of rows"
assert len(df_b) == 78, "Rater B has wrong number of rows"

print("✓ Response validation passed")
```

---

## COMMON ISSUES & SOLUTIONS

### Issue: Excel formulas broken after editing

**Solution:** Do not edit columns A–F (pre-filled data). Only edit Q1–Q7 columns (G–R).

### Issue: Data validation dropdown not appearing

**Solution:** Ensure you're using Excel 2016+ or LibreOffice Calc. Some older spreadsheet tools may not support data validation.

### Issue: File too large or slow to open

**Solution:** Normal for large vignette texts. Expected file size: ~2–3 MB per template. If >5 MB, check that LLM responses are truncated to first 50,000 characters.

### Issue: Cohen's kappa script says "File not found"

**Solution:** Place completed Excel files in `04_results/human_validation/` with names ending in `_Completed.xlsx`. Example:

```
04_results/human_validation/PAHS_IRR_RaterA_Completed.xlsx
04_results/human_validation/PAHS_IRR_RaterB_Completed.xlsx
```

### Issue: Discordant cases hard to interpret

**Solution:** Open INTER_RATER_DETAILED_COMPARISON.csv in Excel, filter for Agreement=0, and review the cases. Discussion with raters often reveals misunderstanding of hallucination definition.

---

## NEXT STEPS AFTER PHASE 4

### If κ ≥ 0.60 (Validation Passed)

1. ✅ Use automatic hallucination classifications in primary analysis
2. ✅ Proceed to Phase 5: Final Analysis
3. ✅ Generate results tables (hallucination rates by model/condition)
4. ✅ Include inter-rater validation results in Methods section of manuscript

**Sample Methods text:**
> "Two independent senior psychiatrists (5+ years clinical experience) rated a stratified sample of 78 cases (20% of study pool) using the hallucination definition and structured rating form.
> Inter-rater agreement was calculated using Cohen's kappa. Demonstrated κ = 0.73 (95% CI: 0.58–0.88) indicated substantial agreement, validating the automatic hallucination detection algorithm for
> use in the primary analysis."

### If κ < 0.60 (Validation Concerns)

1. ⚠️ Review all discordant cases with both raters
2. ⚠️ Identify systematic disagreements (specific conditions? specific fabrication types?)
3. ⚠️ Retrain raters on problem areas
4. ⚠️ Consider re-rating discordant cases or recruiting third rater
5. ⚠️ Document recalibration in methods amendment

---

## FILES CREATED/UPDATED FOR PHASE 4

| File | Type | Purpose |
|------|------|---------|
| `scripts/generate_interrater_rating_excel.py` | Python script | Create inter-rater Excel templates (NEW) |
| `scripts/analyze_interrater_agreement.py` | Python script | Calculate Cohen's kappa (NEW) |
| `INTER_RATER_RATING_GUIDE.md` | Documentation | Complete rater instructions (NEW) |
| `PRACTICE_CASES_FOR_RATER_CALIBRATION.md` | Documentation | Training cases (NEW) |
| `RATER_QUICK_REFERENCE_CARD.md` | Documentation | One-page desk reference (NEW) |
| `INTER_RATER_FORM_TEMPLATE.md` | Documentation | Form specifications (NEW) |
| `PHASE4_IMPLEMENTATION_GUIDE.md` | Documentation | Step-by-step workflow (NEW) |
| `04_results/human_validation/PAHS_IRR_RaterA_Template.xlsx` | Excel | Template for Rater A (GENERATED) |
| `04_results/human_validation/PAHS_IRR_RaterB_Template.xlsx` | Excel | Template for Rater B (GENERATED) |

---

**Document Version:** 1.0  
**Created:** June 8, 2026  
**Status:** Ready for Phase 4 Deployment
