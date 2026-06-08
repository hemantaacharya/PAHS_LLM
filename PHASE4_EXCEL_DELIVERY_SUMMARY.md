# PHASE 4 EXCEL DELIVERY — SUMMARY
## PAHS LLM Hallucination Study

**Date:** June 8, 2026  
**Status:** ✅ COMPLETE AND READY FOR DEPLOYMENT

---

## DELIVERABLES CREATED

### 1. Excel Templates (Pre-filled & Ready to Use)

| File | Size | Cases | Sheets | Status |
|------|------|-------|--------|--------|
| `PAHS_IRR_RaterA_Template.xlsx` | 61 KB | 78 | 2 | ✅ Created |
| `PAHS_IRR_RaterB_Template.xlsx` | 61 KB | 78 | 2 | ✅ Created |

**Location:** `04_results/human_validation/`

**Contents per template:**
- Sheet 1: Instructions (complete rater training)
- Sheet 2: Rating_Form (78 pre-populated cases with columns A–R)

**Pre-filled data in each row:**
- ✓ Rater ID (A or B)
- ✓ Case number (1–78)
- ✓ Blinded Case ID (no model/condition info)
- ✓ Vignette text with [FABRICATED: term] highlighted
- ✓ Fabricated term (extracted for reference)
- ✓ Full LLM response (structured format)

**Empty columns for raters to complete:**
- Q1: Hallucination rating (0 or 1) — REQUIRED
- Q2: Confidence (1–3) — optional
- Q3: Location checkboxes — optional
- Q4: Clinical risk (1–3) — optional
- Q5: Model self-awareness (0–2) — optional
- Q6: Notes — optional
- Q7: Overall confidence (1–3) — optional

---

### 2. Python Scripts (Automated Generation & Analysis)

#### Script 1: `generate_interrater_rating_excel.py`
**Purpose:** Creates inter-rater rating templates from scratch  
**Location:** `scripts/`  
**Usage:**
```bash
python3 scripts/generate_interrater_rating_excel.py
```
**Output:**
- Two Excel workbooks with 78 cases each (stratified sample)
- Cases selected from 300 vignettes × 3 conditions × 2 lengths
- Different random order for each rater (prevents order effects)
- Full formatting, validation, frozen headers applied

**Timeline:** ~5 minutes execution time

---

#### Script 2: `analyze_interrater_agreement.py`
**Purpose:** Calculates Cohen's kappa from completed ratings  
**Location:** `scripts/`  
**Usage:**
```bash
python3 scripts/analyze_interrater_agreement.py
```
**Requires:**
- Completed Rater A Excel file (with Q1 ratings in column G)
- Completed Rater B Excel file (with Q1 ratings in column G)
- Files saved in `04_results/human_validation/` with name ending in `_Completed.xlsx`

**Output:**
- Cohen's κ (primary metric)
- 95% confidence interval (via 5,000 bootstrap iterations)
- Observed vs. expected agreement
- Stratified agreement (by vignette length)
- Discordant case list (cases where raters disagree)
- Hallucination prevalence (% rated as 1)
- Summary CSV files for manuscript

**Timeline:** ~2 minutes execution time

---

### 3. Documentation (Training & Guidance)

| Document | Pages | Purpose | Audience |
|----------|-------|---------|----------|
| INTER_RATER_RATING_GUIDE.md | 20+ | Complete rater instructions, 7 worked examples | Psychiatrist raters |
| PRACTICE_CASES_FOR_RATER_CALIBRATION.md | 15+ | 5 training cases with answer keys | Psychiatrist raters (training) |
| RATER_QUICK_REFERENCE_CARD.md | 1 | Decision tree and common patterns | Psychiatrist raters (desk reference) |
| INTER_RATER_FORM_TEMPLATE.md | 15+ | Technical form specifications | Study coordinator |
| PHASE4_IMPLEMENTATION_GUIDE.md | 10+ | Step-by-step workflow (4 weeks) | Study PI |
| PHASE4_EXCEL_MATERIALS_GUIDE.md | 15+ | Complete guide to Excel files & scripts | Study team |

---

## STRATIFICATION OF 78 CASES

Cases selected from stratified sample:

```
Condition × Length × Models:
  DEFAULT/short:             13 cases (mix of models)
  DEFAULT/long:              13 cases (mix of models)
  SAFETY_INSTRUCTION/short:  13 cases (mix of models)
  SAFETY_INSTRUCTION/long:   13 cases (mix of models)
  DETERMINISTIC/short:       13 cases (mix of models)
  DETERMINISTIC/long:        13 cases (mix of models)
  ────────────────────────────────────
  TOTAL:                     78 cases

Models represented: OpenAI, Anthropic, Google Gemini, LLaMA (roughly equal distribution)
```

---

## COLUMN STRUCTURE IN EXCEL

**Fixed/Pre-filled (Columns A–F):**
```
A: Rater_ID (pre-filled: A or B)
B: Case_Number (pre-filled: 1–78)
C: Case_ID (pre-filled: CASE_###_L_D format, blinded)
D: Vignette_Text (pre-filled: full vignette with [FABRICATED: term] highlighted)
E: Fabricated_Term (pre-filled: extracted term for reference)
F: LLM_Response (pre-filled: full structured response from LLM)
```

**Rating Columns (Columns G–R) — For Raters to Complete:**
```
G: Q1_Hallucination_Rating ⭐
   Type: Dropdown (0=No, 1=Yes)
   Required: YES

H: Q2_Confidence
   Type: Dropdown (1=Not confident, 2=Somewhat, 3=Very)
   Optional

I–N: Q3_Location_* (6 checkboxes)
   Options: Yes / No
   Optional

O: Q4_Clinical_Risk
   Type: Dropdown (1=Low, 2=Moderate, 3=High)
   Optional

P: Q5_Model_Self_Awareness
   Type: Dropdown (0=No, 1=Yes but ignored, 2=Yes excluded)
   Optional

Q: Q6_Notes
   Type: Text area (free text, max 500 chars)
   Optional

R: Q7_Overall_Confidence
   Type: Dropdown (1=Low, 2=Moderate, 3=High)
   Optional
```

---

## WORKFLOW: HOW TO USE

### Phase 4.1: Preparation (Week 1)

1. **Generate templates** (already done)
   ```bash
   python3 scripts/generate_interrater_rating_excel.py
   ```
   ✓ Creates: `PAHS_IRR_RaterA_Template.xlsx` and `.../RaterB_...`

2. **Recruit raters**
   - Contact psychiatrists with 5+ years experience
   - Get confidentiality agreements signed

3. **Train raters**
   - Distribute: INTER_RATER_RATING_GUIDE.md
   - Have them complete: PRACTICE_CASES_FOR_RATER_CALIBRATION.md
   - Verify: κ ≥ 0.70 on practice cases

4. **Distribute templates**
   - Send Rater A: `PAHS_IRR_RaterA_Template.xlsx`
   - Send Rater B: `PAHS_IRR_RaterB_Template.xlsx`
   - Include: RATER_QUICK_REFERENCE_CARD.md (laminated, for desk)

### Phase 4.2: Rating (Week 2)

5. **Raters rate cases independently**
   - Read vignette (Column D)
   - Read LLM response (Column F)
   - Mark Q1: 0 (No hallucination) or 1 (Yes hallucination)
   - Optionally complete Q2–Q7
   - Expected time: ~5 min per case = ~6.5 hours total
   - Timeline: Spread over 5–7 days

6. **Quality monitoring (PI)**
   - Check progress daily
   - Answer questions (without unblinding)
   - Ensure no communication between raters

### Phase 4.3: Analysis (Week 3)

7. **Collect completed files**
   - Rename with rater names
   - Save to: `04_results/human_validation/PAHS_IRR_RaterA_Completed.xlsx`
   - Save to: `04_results/human_validation/PAHS_IRR_RaterB_Completed.xlsx`

8. **Calculate agreement**
   ```bash
   python3 scripts/analyze_interrater_agreement.py
   ```
   Output: Cohen's κ, 95% CI, discordance summary, CSV files

9. **Interpret results**
   - If κ ≥ 0.60: ✅ PASS → Proceed to Phase 5
   - If κ < 0.60: ⚠️ REVIEW → Investigate discordances

---

## QUALITY SPECIFICATIONS

### Excel Template Specifications
```
✓ 78 cases per rater (stratified sample)
✓ 18 columns (A–R)
✓ 2 sheets per workbook (Instructions + Rating_Form)
✓ Data validation on Q1–Q7 columns
✓ Frozen header row
✓ Pre-filled columns A–F (vignettes + LLM responses)
✓ Empty Q1–Q7 for raters to complete
✓ Different random order for each rater
✓ Full formatting (colors, borders, text wrapping)
✓ File size: ~60 KB per template
✓ Blinded case IDs (no model or condition information)
```

### Analysis Script Specifications
```
✓ Calculates Cohen's κ from Q1 ratings (binary: 0 or 1)
✓ Computes 95% CI via bootstrap (5,000 iterations)
✓ Stratifies by vignette length (Short vs. Long)
✓ Identifies all discordant cases
✓ Calculates hallucination prevalence
✓ Generates CSV outputs for manuscript
✓ Interprets κ per Landis & Koch (1977) standards:
    κ ≥ 0.81: Almost Perfect
    κ 0.61–0.80: Substantial ← TARGET
    κ 0.41–0.60: Moderate (acceptable)
    κ 0.21–0.40: Fair
    κ < 0.20: Slight/Poor
✓ Target: κ ≥ 0.60 for validation
```

---

## FILES DELIVERED

### New Files Created Today

```
✓ scripts/generate_interrater_rating_excel.py
  └─ Generates inter-rater Excel templates

✓ scripts/analyze_interrater_agreement.py
  └─ Calculates Cohen's kappa from completed ratings

✓ PHASE4_EXCEL_MATERIALS_GUIDE.md
  └─ Comprehensive guide to all Excel materials

✓ 04_results/human_validation/PAHS_IRR_RaterA_Template.xlsx
  └─ Pre-filled template for Rater A (78 cases)

✓ 04_results/human_validation/PAHS_IRR_RaterB_Template.xlsx
  └─ Pre-filled template for Rater B (78 cases)
```

### Documentation Created in Previous Sessions (Still Applicable)

```
✓ INTER_RATER_RATING_GUIDE.md (20+ pages)
✓ PRACTICE_CASES_FOR_RATER_CALIBRATION.md (15+ pages)
✓ RATER_QUICK_REFERENCE_CARD.md (1 page, laminate)
✓ INTER_RATER_FORM_TEMPLATE.md (15+ pages)
✓ PHASE4_IMPLEMENTATION_GUIDE.md (10+ pages)
```

---

## QUICK START GUIDE

### For Study PI (Hemanta):

1. **Verify templates were created:**
   ```bash
   ls -lh 04_results/human_validation/PAHS_IRR_*.xlsx
   ```

2. **When raters return completed files:**
   ```bash
   python3 scripts/analyze_interrater_agreement.py
   ```

3. **Check results:**
   ```bash
   open 04_results/human_validation/analysis/InterRater_Kappa_Summary.csv
   ```

### For Psychiatrist Raters:

1. **Receive:** `PAHS_IRR_RaterA_Template.xlsx` (or RaterB)
2. **Read:** Instructions sheet (orientation)
3. **For each case:**
   - Read Vignette (Column D)
   - Read LLM Response (Column F)
   - Select Q1: 0 or 1 (REQUIRED)
   - Optional: Q2–Q7
4. **Save:** File with your name appended
5. **Return:** To study coordinator

---

## VALIDATION CHECKLIST

### Before Rating ✅
- [ ] Excel templates created (2 files, 61 KB each)
- [ ] Rater instructions distributed
- [ ] Practice cases completed (κ ≥ 0.70 achieved)
- [ ] Quick reference card printed/laminated
- [ ] Raters understand Q1 definition (incorporation vs. mention)
- [ ] Raters signed confidentiality agreements

### During Rating ✅
- [ ] Progress monitored (daily)
- [ ] Rater questions answered (within 24h, without unblinding)
- [ ] No inter-rater communication about specific cases
- [ ] Blinding maintained (model/condition hidden)

### After Rating ✅
- [ ] Completed files collected and renamed
- [ ] Q1 ratings extracted and verified (all 0 or 1)
- [ ] Cohen's kappa calculated (κ ≥ 0.60 for validation)
- [ ] Results documented in CSV files
- [ ] Discordant cases reviewed (if any)
- [ ] Summary table ready for manuscript Methods section

---

## NEXT PHASE (Phase 5)

**When:** After Phase 4 complete (κ ≥ 0.60)

**Tasks:**
1. Generate primary results table (hallucination rates by model, 95% CI)
2. Perform secondary analyses (condition effects, length effects)
3. Create visualizations (leaderboard, forest plots)
4. Write results section
5. Write discussion section

---

## SUPPORT & TROUBLESHOOTING

**Question:** How do I re-generate the Excel templates?
**Answer:** Run `python3 scripts/generate_interrater_rating_excel.py` again. It will overwrite previous templates.

**Question:** What if a rater doesn't complete all 78 cases?
**Answer:** Analyze with available cases. Calculate κ on subset (e.g., "κ = 0.65 based on 65/78 jointly-rated cases").

**Question:** Can I edit the vignettes or LLM responses?
**Answer:** No. Columns A–F are reference data. Only edit Q1–Q7.

**Question:** What if Cohen's κ < 0.60?
**Answer:** Follow Phase 4 recalibration protocol in PHASE4_IMPLEMENTATION_GUIDE.md.

---

**Status:** ✅ ALL DELIVERABLES COMPLETE AND READY FOR USE

For questions or issues, contact study PI (Hemanta Acharya)

