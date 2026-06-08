# Phase 4 Excel Materials — File Index
## PAHS LLM Study — Complete Checklist

**Created:** June 8, 2026  
**Status:** ✅ READY FOR PHASE 4 DEPLOYMENT  
**Total Files:** 11 new + 2 Excel templates

---

## 📊 EXCEL TEMPLATES (START HERE FOR RATERS)

| File | Size | Cases | Format | Purpose |
|------|------|-------|--------|---------|
| **PAHS_IRR_RaterA_Template.xlsx** | 61 KB | 78 | .xlsx | Template for Rater A |
| **PAHS_IRR_RaterB_Template.xlsx** | 61 KB | 78 | .xlsx | Template for Rater B |

**Location:** `04_results/human_validation/`

**What raters receive:**
- Rater A gets: `PAHS_IRR_RaterA_Template.xlsx` + training materials
- Rater B gets: `PAHS_IRR_RaterB_Template.xlsx` + training materials
- Both get: RATER_QUICK_REFERENCE_CARD.md (laminated)

**Expected time to complete:** ~6.5 hours per rater (spread over 5–7 days)

---

## 🐍 PYTHON SCRIPTS (AUTOMATION)

| Script | Location | Purpose | Usage |
|--------|----------|---------|-------|
| **generate_interrater_rating_excel.py** | `scripts/` | Create Excel templates | `python3 scripts/generate_interrater_rating_excel.py` |
| **analyze_interrater_agreement.py** | `scripts/` | Calculate Cohen's kappa | `python3 scripts/analyze_interrater_agreement.py` |

**When to run:**
- Generation script: Before Phase 4 (creates templates)
- Analysis script: After both raters complete all cases

---

## 📚 DOCUMENTATION FILES

### Core Training Materials (For Raters)

| Document | Pages | Purpose | Who | When |
|----------|-------|---------|-----|------|
| **INTER_RATER_RATING_GUIDE.md** | 20+ | Complete rater instructions with 7 worked examples | Raters | Before rating |
| **PRACTICE_CASES_FOR_RATER_CALIBRATION.md** | 15+ | 5 training cases with answer keys | Raters | During training |
| **RATER_QUICK_REFERENCE_CARD.md** | 1 | Decision tree + common patterns (LAMINATE) | Raters | During rating |

**How to use:**
1. Give INTER_RATER_RATING_GUIDE.md to raters (read before training)
2. Have raters complete PRACTICE_CASES_FOR_RATER_CALIBRATION.md (~30 min)
3. Verify calibration: κ ≥ 0.70 on practice cases
4. Print & laminate RATER_QUICK_REFERENCE_CARD.md (desk reference)
5. Raters keep guide open while rating

### Technical References (For Study Team)

| Document | Pages | Purpose | Who | When |
|----------|-------|---------|-----|------|
| **PHASE4_IMPLEMENTATION_GUIDE.md** | 10+ | Complete 4-week Phase 4 workflow | Study PI | Planning |
| **INTER_RATER_FORM_TEMPLATE.md** | 15+ | Technical form specifications | Study coordinator | Setup |
| **PHASE4_EXCEL_MATERIALS_GUIDE.md** | 15+ | Complete guide to Excel files & scripts | Study team | Reference |
| **PHASE4_EXCEL_DELIVERY_SUMMARY.md** | 10+ | Quick-start guide & specifications | Study team | Quick ref |
| **04_results/human_validation/README.md** | 10+ | User-friendly guide for raters & PI | Everyone | Navigation |

**How to use:**
1. PI reads: PHASE4_IMPLEMENTATION_GUIDE.md (understand full workflow)
2. Coordinator reads: INTER_RATER_FORM_TEMPLATE.md (setup form)
3. Everyone refers to: PHASE4_EXCEL_MATERIALS_GUIDE.md (technical details)
4. Raters refer to: 04_results/human_validation/README.md (quick navigation)

---

## 📁 COMPLETE FILE STRUCTURE

```
/Users/hemanta/Desktop/PAHS_LLM/
├── scripts/
│   ├── generate_interrater_rating_excel.py ........................... NEW
│   └── analyze_interrater_agreement.py .............................. NEW
│
├── INTER_RATER_RATING_GUIDE.md ......... (from Session 3, needed for Phase 4)
├── PRACTICE_CASES_FOR_RATER_CALIBRATION.md (from Session 3, needed for Phase 4)
├── RATER_QUICK_REFERENCE_CARD.md ....... (from Session 3, needed for Phase 4)
├── INTER_RATER_FORM_TEMPLATE.md ........ (from Session 3, needed for Phase 4)
├── PHASE4_IMPLEMENTATION_GUIDE.md ...... (from Session 3, needed for Phase 4)
│
├── PHASE4_EXCEL_MATERIALS_GUIDE.md ............................. NEW
├── PHASE4_EXCEL_DELIVERY_SUMMARY.md ............................ NEW
│
└── 04_results/
    └── human_validation/
        ├── PAHS_IRR_RaterA_Template.xlsx ......................... NEW
        ├── PAHS_IRR_RaterB_Template.xlsx ......................... NEW
        ├── README.md ............................................. NEW
        ├── PHASE4_EXCEL_MATERIALS_GUIDE.md (symlink or copy)
        └── analysis/ ............................................. (created by analyze script)
            ├── InterRater_Kappa_Summary.csv
            └── InterRater_Detailed_Comparison.csv
```

---

## ✅ QUICK VERIFICATION CHECKLIST

Run these commands to verify everything is in place:

```bash
# Check Excel templates exist
ls -lh 04_results/human_validation/PAHS_IRR_*.xlsx

# Check Python scripts exist
ls -lh scripts/generate_interrater_rating_excel.py
ls -lh scripts/analyze_interrater_agreement.py

# Check documentation files exist
ls -lh INTER_RATER_RATING_GUIDE.md
ls -lh PRACTICE_CASES_FOR_RATER_CALIBRATION.md
ls -lh RATER_QUICK_REFERENCE_CARD.md
ls -lh PHASE4_*.md
ls -lh 04_results/human_validation/README.md
```

**Expected output:** All files should exist with dates ~June 8, 2026

---

## 🚀 DEPLOYMENT SEQUENCE

### Step 1: Verify Everything
```bash
python3 scripts/generate_interrater_rating_excel.py  # Should complete without errors
```

### Step 2: Prepare Rater Package
For each rater, package:
1. `PAHS_IRR_RaterA_Template.xlsx` (or RaterB)
2. `INTER_RATER_RATING_GUIDE.md` (print or PDF)
3. `PRACTICE_CASES_FOR_RATER_CALIBRATION.md` (print or PDF)
4. `RATER_QUICK_REFERENCE_CARD.md` (printed & laminated)
5. `04_results/human_validation/README.md` (digital or print)

### Step 3: Conduct Training
- Have raters review INTER_RATER_RATING_GUIDE.md (1 hour)
- Have raters complete PRACTICE_CASES_FOR_RATER_CALIBRATION.md (~30 min)
- Verify calibration: κ ≥ 0.70 on practice cases
- Distribute templates and quick reference cards

### Step 4: Monitor Rating Period
- Check progress daily
- Respond to rater questions (within 24 hours)
- Maintain blinding (don't reveal model/condition info)

### Step 5: Analyze Results
```bash
python3 scripts/analyze_interrater_agreement.py
cat 04_results/human_validation/analysis/InterRater_Kappa_Summary.csv
```

---

## 📋 COLUMN REFERENCE (QUICK LOOKUP)

### In Excel Templates

**Pre-filled (Read-only):**
- A: Rater_ID
- B: Case_Number
- C: Case_ID (blinded)
- D: Vignette_Text (with [FABRICATED: term])
- E: Fabricated_Term
- F: LLM_Response

**For Raters to Complete:**
- G: Q1_Hallucination_Rating (0 or 1) ← **REQUIRED**
- H: Q2_Confidence (1–3 = Not confident to Very confident)
- I–N: Q3_Location_* (checkboxes: Primary, Reasoning, Differential, TopDiagnosis, Management, Other)
- O: Q4_Clinical_Risk (1–3 = Low to High)
- P: Q5_Model_Self_Awareness (0–2)
- Q: Q6_Notes (free text)
- R: Q7_Overall_Confidence (1–3)

---

## 🎯 METRICS & TARGETS

**Cohen's κ Interpretation:**
- κ ≥ 0.81: Almost Perfect
- κ 0.61–0.80: **Substantial** ← Target
- κ 0.41–0.60: Moderate (acceptable)
- κ 0.21–0.40: Fair
- κ < 0.20: Slight/Poor

**Validation Threshold:** κ ≥ 0.60 (minimum acceptable)

**Expected Outcomes:**
- Hallucination prevalence: ~40–50% of cases
- Concordance: ~90% (72/78 matching)
- Discordances: ~10% (6–8 cases)

---

## 📞 SUPPORT MATRIX

| Question | Answer | Resource |
|----------|--------|----------|
| How do I rate? | Follow decision tree | RATER_QUICK_REFERENCE_CARD.md |
| What's a hallucination? | Read definition & examples | INTER_RATER_RATING_GUIDE.md |
| I'm unsure about a case | Try practice cases first | PRACTICE_CASES_FOR_RATER_CALIBRATION.md |
| How do I set up the form? | See technical specs | INTER_RATER_FORM_TEMPLATE.md |
| What's the full workflow? | 4-week timeline | PHASE4_IMPLEMENTATION_GUIDE.md |
| Where are my files? | Check file structure | This index + README.md |
| How do I analyze results? | Run Python script | analyze_interrater_agreement.py |
| General questions? | User-friendly guide | 04_results/human_validation/README.md |

---

## 🔄 REGENERATION (If Needed)

**To create new templates with different cases:**

```python
# Edit this in generate_interrater_rating_excel.py:
RANDOM_SEED = 20260609  # Change seed for different cases
n_cases = 100           # Change to 100 cases instead of 78

# Then run:
python3 scripts/generate_interrater_rating_excel.py
```

**To re-analyze completed ratings:**

```bash
# Copy completed files to human_validation/ with correct names:
# PAHS_IRR_RaterA_Completed.xlsx
# PAHS_IRR_RaterB_Completed.xlsx

# Then run:
python3 scripts/analyze_interrater_agreement.py

# Check results:
cat 04_results/human_validation/analysis/InterRater_Kappa_Summary.csv
```

---

## ✨ COMPLETION STATUS

### What's Ready NOW ✅
- ✓ Excel templates (78 cases each, fully formatted)
- ✓ Python scripts (generation & analysis)
- ✓ Rater training materials (20+ pages)
- ✓ Technical documentation (40+ pages)
- ✓ Quick reference cards (desk-ready)
- ✓ Complete workflow guidance (4 weeks)

### What's Next 📋
- [ ] Recruit psychiatrist raters
- [ ] Conduct rater training (Week 1)
- [ ] Distribute templates (Week 1)
- [ ] Raters complete ratings (Week 2)
- [ ] Analyze inter-rater agreement (Week 3)
- [ ] Validate and proceed to Phase 5 (Week 4)

---

**Document Version:** 1.0  
**Created:** June 8, 2026  
**Status:** ✅ ALL PHASE 4 MATERIALS COMPLETE

For questions: Contact Hemanta Acharya (Study PI)

