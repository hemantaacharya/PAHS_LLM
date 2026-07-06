# PAHS LLM — Core Code Files Summary

This document covers the files directly cited in the manuscript Methods section.

## Study Runner

| File | What it does | Main inputs | Main outputs |
| --- | --- | --- | --- |
| `main.py` | Orchestrates the full 2026 PAHS study across all model providers with resumable execution and structured outputs. | Vignette JSON (`02_data/experimental/combined_vignettes_clean.json`), API keys, CLI flags (`--provider`, `--model`, `--independent-model-runs`). | Raw model outputs (JSON/CSV), hallucination-focused analysis JSON/CSV, and summary JSON under `04_results/`. |

## Core Data Schema

| File | What it does | Main inputs | Main outputs |
| --- | --- | --- | --- |
| `src/pahs_llm/core/schemas.py` | Defines the Pydantic response schema (`ClinicalOutput`, `SafetyAudit`) that enforces structured generation from every LLM call. | LLM response payload at call time. | Validated structured objects consumed by all downstream analysis. |

## Evaluation and Metrics

| File | What it does | Main inputs | Main outputs |
| --- | --- | --- | --- |
| `src/pahs_llm/evaluation/extract_hallucination_data.py` | Derives the four primary trial outcomes (Successful Defense, Silent Adoption, False Positive, Blind Spot) and computes Boolean-logic endpoint flags for each trial. | Raw trial JSON from `04_results/raw_json/`; real-term allowlist (CIWA-Ar). | Hallucination-focused JSON/CSV extracts and summary metrics by model, condition, and vignette length. |
| `src/pahs_llm/evaluation/pool_hallucination_analysis.py` | Pools all per-model study files into publication-ready trial-level and aggregate tables with Wilson 95% CIs, risk differences, and risk ratios. | `04_results/raw_json/PAHS_STUDY_RESULTS_2026_*.json`. | `pooled_trial_level.csv`, `table1_coverage.csv`, `table2_outcomes_by_model_condition.csv`, `table3_condition_effects.csv`, `table4_length_effects.csv`, `run_summary.json` in `04_results/analysis_ready/pooled/`. |
| `src/pahs_llm/evaluation/interrater_reliability.py` | Computes Cohen's kappa, 95% CI, and percent agreement between rater pairs, overall and stratified by model, condition, and vignette length. | JSON records with paired binary rater labels. | Reliability summary JSON/console report. |

## Human Validation

| File | What it does | Main inputs | Main outputs |
| --- | --- | --- | --- |
| `scripts/generate_stratified_sample_400.py` | Creates the 400-case stratified random sample (16–17 cases per model × condition × length cell) with model-name anonymization and blinding. | Analysis-ready model output CSVs. | `stratified_sample_400_blinded.csv`, `stratified_sample_400_key.csv`, and summary text. |
| `scripts/generate_rater_excel_sheets.py` | Distributes the 400 blinded cases into four psychiatrist-specific Excel rating sheets (100 cases each, non-overlapping). | 400-case blinded sample and unblinding key. | Four formatted Excel rating files, one per psychiatrist. |
| `scripts/calculate_kappa_4raters.py` | Calculates all-pairs pairwise Cohen's kappa and Fleiss' kappa for the 4-psychiatrist panel. | Four rater CSV files with aligned `Case_ID` and `Hallucination` columns. | Pairwise kappa matrix, Fleiss' kappa, and agreement summary table. |
