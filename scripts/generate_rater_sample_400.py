#!/usr/bin/env python3
"""
Generate Stratified 400-Case Sample for 4-Psychiatrist Rating
==============================================================

Design:
  - 400 unique cases, each rated by 1 psychiatrist
  - 400 total ratings (4 psychiatrists × 100 cases)
  - Stratified across 4 models × 3 conditions × 2 lengths = 24 cells
  - ~16 cases per cell (some get 16, some get 17 to reach 400)
  - Blinded: model names replaced with anonymous IDs

Output:
  - 04_results/human_validation/rater_sample_400.csv
  - 04_results/human_validation/rater_sample_400_blinded.csv
  - 04_results/human_validation/rater_sample_400_key.csv
  - 04_results/human_validation/rater_sample_400_summary.txt
"""

import pandas as pd
import numpy as np
import random
import os
from pathlib import Path
from collections import defaultdict

# ── Configuration ──────────────────────────────────────────────────────────────

RANDOM_SEED = 20260602
TOTAL_CASES = 400
SAMPLES_PER_CELL_BASE = 16  # 16 × 24 = 384
EXTRA_SAMPLES = 16           # 400 − 384 = 16 extra → 16 cells get 17

MODELS = [
    "anthropic/claude-haiku-4-5",
    "gemini/gemini-3.1-flash-lite",
    "openai/gpt-5.4-mini",
    "openrouter/meta-llama/llama-3.3-70b-instruct",
]

CONDITIONS = ["DEFAULT", "DETERMINISTIC", "SAFETY_INSTRUCTION"]
LENGTHS = ["short", "long"]

MODEL_ANON_KEYS = ["Model_A", "Model_B", "Model_C", "Model_D"]

DATA_DIR = Path("04_results/analysis_ready")
OUTPUT_DIR = Path("04_results/human_validation")

# ── Load Data ─────────────────────────────────────────────────────────────────

print("=" * 70)
print("GENERATING 400-CASE STRATIFIED SAMPLE FOR 4-PSYCHIATRIST RATING")
print("=" * 70)
print()

model_data = {}
for model in MODELS:
    import glob
    files = glob.glob(str(DATA_DIR / f"*{model.split('/')[-1]}*_hallucination_focus.csv"))
    files = [f for f in files if "PAHS_STUDY" in f and "PILOT" not in f]
    if not files:
        raise FileNotFoundError(f"Cannot find data file for model: {model}")

    df = pd.read_csv(files[0])
    df = df[df["model"] == model].copy()
    model_data[model] = df
    print(f"  Loaded {model}: {len(df)} rows")

print()

# ── Stratified Sampling ───────────────────────────────────────────────────────

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# Shuffle model anonymization
shuffled_indices = list(range(len(MODELS)))
random.shuffle(shuffled_indices)
model_to_anon = {}
for i, idx in enumerate(shuffled_indices):
    model_to_anon[MODELS[idx]] = MODEL_ANON_KEYS[i]

print("Model anonymization (keep secret):")
for model, anon in model_to_anon.items():
    print(f"  {anon} ← {model}")
print()

# Determine samples per cell: 400 / 24 = 16 remainder 16
all_cells = [(m, c, l) for m in MODELS for c in CONDITIONS for l in LENGTHS]
random.shuffle(all_cells)
cell_n = {}
for i, cell in enumerate(all_cells):
    cell_n[cell] = SAMPLES_PER_CELL_BASE + (1 if i < EXTRA_SAMPLES else 0)

# Sample from each cell
sampled_rows = []
cell_counts = defaultdict(int)

for model in MODELS:
    for condition in CONDITIONS:
        for length in LENGTHS:
            key = (model, condition, length)
            n = cell_n[key]

            df_cell = model_data[model][
                (model_data[model]["condition"] == condition)
                & (model_data[model]["vignette_length"] == length)
            ]

            if len(df_cell) < n:
                print(f"  WARNING: {model}/{condition}/{length} has only {len(df_cell)} rows, need {n}")
                n = len(df_cell)

            sampled = df_cell.sample(n=n, random_state=RANDOM_SEED + len(sampled_rows))
            sampled_rows.append(sampled)
            cell_counts[key] = n

df_sampled = pd.concat(sampled_rows, ignore_index=True)
df_sampled.insert(0, "case_seq_id", range(1, len(df_sampled) + 1))

# Shuffle order
df_sampled = df_sampled.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
df_sampled["case_seq_id"] = range(1, len(df_sampled) + 1)

print(f"Total unique cases: {len(df_sampled)}")
print()

# ── Create Blinded Version ────────────────────────────────────────────────────

df_blinded = df_sampled.copy()
df_blinded["model"] = df_blinded["model"].map(model_to_anon)

columns_to_keep = [
    "case_seq_id", "case_id", "primary_presentation",
    "recommended_management", "top_diagnosis",
    "vignette_length", "condition", "category", "model",
    "target_token",
]
columns_to_keep = [c for c in columns_to_keep if c in df_blinded.columns]
df_blinded = df_blinded[columns_to_keep]

# ── Save Outputs ──────────────────────────────────────────────────────────────

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df_sampled.to_csv(OUTPUT_DIR / "rater_sample_400.csv", index=False)
print(f"  Saved: rater_sample_400.csv ({len(df_sampled)} rows)")

df_blinded.to_csv(OUTPUT_DIR / "rater_sample_400_blinded.csv", index=False)
print(f"  Saved: rater_sample_400_blinded.csv ({len(df_blinded)} rows)")

# ── Create Key File (model mapping) ───────────────────────────────────────────

df_key = pd.DataFrame({
    "anonymized_model": MODEL_ANON_KEYS,
    "actual_model": MODELS,
})
df_key.to_csv(OUTPUT_DIR / "rater_sample_400_key.csv", index=False)
print(f"  Saved: rater_sample_400_key.csv ({len(df_key)} rows)")

# ── Summary Statistics ───────────────────────────────────────────────────────

print()
print("=" * 70)
print("400-CASE SAMPLE SUMMARY — 4-PSYCHIATRIST RATING")
print("=" * 70)
print(f"Random seed: {RANDOM_SEED}")
print(f"Total unique cases: {len(df_sampled)}")
print(f"Total ratings: {len(df_sampled)} × 4 psychiatrists = {len(df_sampled) * 4}")
print()

print("Allocation (Model × Condition × Length):")
print("-" * 70)
print(f"{'Model':<45} {'Condition':<20} {'Length':<10} {'N':<5}")
print("-" * 70)
for model in MODELS:
    for condition in CONDITIONS:
        for length in LENGTHS:
            key = (model, condition, length)
            n = cell_counts.get(key, 0)
            print(f"{model:<45} {condition:<20} {length:<10} {n:<5}")
print("-" * 70)

print()
print("Marginal totals:")
for model in MODELS:
    total = sum(cell_counts.get((model, c, l), 0) for c in CONDITIONS for l in LENGTHS)
    print(f"  {model}: {total}")
for condition in CONDITIONS:
    total = sum(cell_counts.get((m, condition, l), 0) for m in MODELS for l in LENGTHS)
    print(f"  {condition}: {total}")
for length in LENGTHS:
    total = sum(cell_counts.get((m, c, length), 0) for m in MODELS for c in CONDITIONS)
    print(f"  {length}: {total}")

print()
print("Model anonymization (KEEP SECRET):")
for model, anon in model_to_anon.items():
    print(f"  {anon} ← {model}")

print()
print("Blinding: model names → anonymous IDs, cases randomized")
print()
print("DONE. Output directory: 04_results/human_validation")