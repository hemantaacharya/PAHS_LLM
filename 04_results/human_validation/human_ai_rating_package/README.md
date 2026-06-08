# Human-AI Rating Package

This folder contains all materials for the PAHS LLM Hallucination Study 2026 human-AI rating phase.

## Package Contents

### For Psychiatrists (4 files)
- **Psychiatrist_1_rating_sheet.xlsx** — Rating sheet with 100 cases
- **Psychiatrist_2_rating_sheet.xlsx** — Rating sheet with 100 cases
- **Psychiatrist_3_rating_sheet.xlsx** — Rating sheet with 100 cases
- **Psychiatrist_4_rating_sheet.xlsx** — Rating sheet with 100 cases

Each rating sheet includes:
- **Instructions sheet** with detailed rating guidelines
- **Rating Sheet** with 100 blinded cases (different cases per psychiatrist)
- Data validation (0 or 1 only for Hallucination column)
- Freeze panes and auto-filter

### For Analysis (2 files)
- **rater_sample_400_blinded.csv** — All 400 cases with anonymized model information
- **rater_sample_400_key.csv** — Model key (A, B, C, D → actual model names)

### Master Sheets (4 files)
- **Psychiatrist_1_master_sheet.xlsx** — Progress tracker and consolidation template
- **Psychiatrist_2_master_sheet.xlsx** — Progress tracker and consolidation template
- **Psychiatrist_3_master_sheet.xlsx** — Progress tracker and consolidation template
- **Psychiatrist_4_master_sheet.xlsx** — Progress tracker and consolidation template

Each master sheet includes:
- Progress tracker (completed cases, ratings, notes)
- Metadata reference (case details, model info)
- Consolidation template (for combining all ratings)
- Analysis sheet (for Kappa calculations)

## Study Design

- **Total ratings**: 400 (100 per psychiatrist)
- **Unique cases**: 400 (each psychiatrist rates different cases)
- **Models**: 4 anonymized (A, B, C, D)
- **Conditions**: 3 (DEFAULT, DETERMINISTIC, SAFETY_INSTRUCTION)
- **Lengths**: 2 (short, long)
- **Stratification**: 24 cells (4 models × 3 conditions × 2 lengths)

## Rating Instructions

Each rating sheet contains detailed instructions including:
- Study background and purpose
- Task description (rate if LLM incorporated fabricated term)
- Hallucination rating scale (0 = NO, 1 = YES)
- Important guidelines for consistent ratings
- Column descriptions

## Analysis

After all ratings are complete, run the Kappa analysis:

```bash
python scripts/calculate_kappa_4raters.py
```

This will compute:
- Pairwise Cohen's Kappa (6 pairs: P1-P2, P1-P3, P1-P4, P2-P3, P2-P4, P3-P4)
- Fleiss' Kappa for multi-rater agreement

## Random Seed

All randomization uses seed: **20260602**

## Study Information

- **Study**: PAHS LLM Hallucination Study 2026
- **Site**: Patan Academy of Health Sciences, Patan Hospital
- **Date**: June 2026

## Notes

- Do not share rating sheets between psychiatrists
- Rate independently — do not discuss ratings until all are complete
- Focus on the fabricated term only, not overall diagnosis accuracy
- Model IDs (A, B, C, D) are anonymized — do not try to guess which model is which