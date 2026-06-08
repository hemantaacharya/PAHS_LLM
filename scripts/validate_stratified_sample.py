#!/usr/bin/env python3
"""Validate the 400-sample stratified output for correctness and blinding."""

import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
BLINDED_PATH = BASE / "04_results/human_validation/stratified_sample_400_blinded.csv"
FULL_PATH = BASE / "04_results/human_validation/stratified_sample_400.csv"
KEY_PATH = BASE / "04_results/human_validation/stratified_sample_400_key.csv"

print("=" * 60)
print("VALIDATION: Stratified Sample 400")
print("=" * 60)

# Load files
df_blinded = pd.read_csv(BLINDED_PATH)
df_full = pd.read_csv(FULL_PATH)
df_key = pd.read_csv(KEY_PATH)

errors = []
warnings = []

# 1. Row count
if len(df_blinded) != 400:
    errors.append(f"Blinded CSV has {len(df_blinded)} rows, expected 400")
if len(df_full) != 400:
    errors.append(f"Full CSV has {len(df_full)} rows, expected 400")
print(f"[1] Row count: {len(df_blinded)} (blinded), {len(df_full)} (full) — {'OK' if len(df_blinded)==400 and len(df_full)==400 else 'FAIL'}")

# 2. Column check — blinded should NOT have sensitive columns
sensitive_cols = ["hallucination_detected", "dangerous_reasoning_hallucination",
                  "flagged_term_count", "flagged_terms", "target_token",
                  "target_token_source", "token_identified_in_safety_audit",
                  "token_in_diagnostic_reasoning", "token_in_final_diagnosis",
                  "token_in_primary_presentation", "detection_rate_success",
                  "adoption_rate_failure", "meaning_and_clinical_risk",
                  "diagnostic_confidence"]
leaked = [c for c in sensitive_cols if c in df_blinded.columns]
if leaked:
    errors.append(f"Sensitive columns in blinded CSV: {leaked}")
    print(f"[2] Sensitive columns: FAIL — {leaked}")
else:
    print(f"[2] Sensitive columns: OK (none present)")

# 3. Model names should be anonymized
anon_models = set(df_blinded["model"].unique())
expected_anon = {"Model_A", "Model_B", "Model_C", "Model_D"}
if anon_models != expected_anon:
    errors.append(f"Unexpected model IDs: {anon_models}")
    print(f"[3] Model anonymization: FAIL — found {anon_models}")
else:
    print(f"[3] Model anonymization: OK ({sorted(anon_models)})")

# 4. No real model name leaks in any text column
real_model_keywords = ["anthropic", "gemini", "openai", "openrouter", "claude", "llama", "gpt"]
leak_found = False
for col in df_blinded.columns:
    if df_blinded[col].dtype == "object":
        for kw in real_model_keywords:
            matches = df_blinded[col].str.contains(kw, case=False, na=False).sum()
            if matches > 0:
                warnings.append(f"Possible leak in '{col}': {matches} matches for '{kw}'")
                print(f"  WARNING: '{col}' has {matches} matches for '{kw}'")
                leak_found = True
if not leak_found:
    print(f"[4] Text leak check: OK (no model name keywords found)")
else:
    print(f"[4] Text leak check: WARNINGS (see above)")

# 5. Stratification balance
print(f"\n[5] Stratification balance:")
print(f"  By model: {dict(df_blinded['model'].value_counts().sort_index())}")
print(f"  By length: {dict(df_blinded['vignette_length'].value_counts())}")
print(f"  By condition: {dict(df_blinded['condition'].value_counts())}")

# Check each cell has 16 or 17
ct = df_full.groupby(["model", "condition", "vignette_length"]).size()
cell_sizes = ct.values
if all(16 <= s <= 17 for s in cell_sizes):
    print(f"  Cell sizes: all 16 or 17 (min={min(cell_sizes)}, max={max(cell_sizes)}) — OK")
else:
    errors.append(f"Cell sizes out of range: min={min(cell_sizes)}, max={max(cell_sizes)}")
    print(f"  Cell sizes: FAIL (min={min(cell_sizes)}, max={max(cell_sizes)})")

# 6. Marginal totals
print(f"\n[6] Marginal totals:")
for model in sorted(df_full["model"].unique()):
    n = len(df_full[df_full["model"] == model])
    print(f"  {model}: {n}")
for cond in sorted(df_full["condition"].unique()):
    n = len(df_full[df_full["condition"] == cond])
    print(f"  {cond}: {n}")
for length in sorted(df_full["vignette_length"].unique()):
    n = len(df_full[df_full["vignette_length"] == length])
    print(f"  {length}: {n}")

# 7. No duplicate case_ids
dupes = df_full["case_id"].duplicated().sum()
if dupes > 0:
    warnings.append(f"{dupes} duplicate case_ids found")
    print(f"\n[7] Duplicates: {dupes} duplicate case_ids (WARNING)")
else:
    print(f"\n[7] Duplicates: OK (no duplicate case_ids)")

# 8. Rating IDs
if df_blinded["rating_id"].nunique() == 400 and df_blinded["rating_id"].min() == 1 and df_blinded["rating_id"].max() == 400:
    print(f"[8] Rating IDs: OK (1-400, all unique)")
else:
    errors.append("Rating IDs not 1-400 unique")
    print(f"[8] Rating IDs: FAIL")

# 9. Key file
print(f"\n[9] Key file:")
for _, row in df_key.iterrows():
    print(f"  {row['anonymous_id']} <- {row['real_model']}")

# Summary
print(f"\n{'=' * 60}")
if errors:
    print(f"ERRORS ({len(errors)}):")
    for e in errors:
        print(f"  FAIL: {e}")
else:
    print("ALL VALIDATIONS PASSED")
if warnings:
    print(f"\nWARNINGS ({len(warnings)}):")
    for w in warnings:
        print(f"  WARN: {w}")
print("=" * 60)
