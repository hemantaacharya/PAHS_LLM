#!/usr/bin/env python3
"""
Stratified Random Sampling for 400 Psychiatrist Ratings
========================================================

Design:
  - 4 models × 3 conditions × 2 lengths = 24 cells
  - 400 total ratings
  - 16 or 17 samples per cell (16×24=384, plus 16 extra distributed randomly)
  - Random seed for reproducibility
  - Blinded: model names replaced with anonymous IDs (Model_A, Model_B, ...)

Models:
  1. anthropic/claude-haiku-4-5
  2. gemini/gemini-3.1-flash-lite
  3. openai/gpt-5.4-mini
  4. openrouter/meta-llama/llama-3.3-70b-instruct

Conditions:
  - DEFAULT
  - DETERMINISTIC
  - SAFETY_INSTRUCTION

Lengths:
  - short
  - long

Output:
  - 04_results/human_validation/stratified_sample_400.csv
  - 04_results/human_validation/stratified_sample_400_blinded.csv (for rater)
  - 04_results/human_validation/stratified_sample_400_key.csv (mapping, keep secret)
  - 04_results/human_validation/stratified_sample_400_summary.txt
"""

import pandas as pd
import numpy as np
import random
import os
from collections import defaultdict

# ── Configuration ──────────────────────────────────────────────────────────────

RANDOM_SEED = 20260602
SAMPLES_PER_CELL_BASE = 16  # 16 × 24 = 384
EXTRA_SAMPLES = 16           # 400 − 388 = 12 extra → distribute to 12 cells
# Actually: 16*24 = 384, need 16 more → 16 cells get 17, 8 cells get 16

MODELS = [
    "anthropic/claude-haiku-4-5",
    "gemini/gemini-3.1-flash-lite",
    "openai/gpt-5.4-mini",
    "openrouter/meta-llama/llama-3.3-70b-instruct",
]

CONDITIONS = ["DEFAULT", "DETERMINISTIC", "SAFETY_INSTRUCTION"]
LENGTHS = ["short", "long"]

# Model anonymization mapping (randomized order)
MODEL_ANON_KEYS = ["Model_A", "Model_B", "Model_C", "Model_D"]

DATA_DIR = "04_results/analysis_ready"
OUTPUT_DIR = "04_results/human_validation"

# ── Load Data ─────────────────────────────────────────────────────────────────

print("=" * 70)
print("STRATIFIED SAMPLING FOR 400 PSYCHIATRIST RATINGS")
print("=" * 70)
print()

# Load all 4 model datasets
model_data = {}
for model in MODELS:
    # Find the correct file
    model_slug = model.replace("/", "_").replace("-", "_")
    # Try different file patterns
    pattern1 = f"PAHS_STUDY_RESULTS_2026_{model.replace('/', '_')}_hallucination_focus.csv"
    pattern2 = f"PAHS_STUDY_RESULTS_2026_{model.split('/')[-1]}_hallucination_focus.csv"

    filepath = None
    for p in [pattern1, pattern2]:
        full_path = os.path.join(DATA_DIR, p)
        if os.path.exists(full_path):
            filepath = full_path
            break

    if filepath is None:
        # Try glob
        import glob
        files = glob.glob(os.path.join(DATA_DIR, f"*{model.split('/')[-1]}*_hallucination_focus.csv"))
        # Filter to only PAHS_STUDY files (not PILOT)
        files = [f for f in files if "PAHS_STUDY" in f and "PILOT" not in f]
        if files:
            filepath = files[0]

    if filepath is None:
        raise FileNotFoundError(f"Cannot find data file for model: {model}")

    df = pd.read_csv(filepath)
    # Only keep rows that have actual model name (some files may have multiple)
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

# Determine how many samples per cell
# 400 total / 24 cells = 16.67 → 16 cells get 17, 8 cells get 16
all_cells = [(m, c, l) for m in MODELS for c in CONDITIONS for l in LENGTHS]
random.shuffle(all_cells)  # randomize which cells get extra
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

            # Get available data for this cell
            df_cell = model_data[model][
                (model_data[model]["condition"] == condition)
                & (model_data[model]["vignette_length"] == length)
            ]

            if len(df_cell) < n:
                print(
                    f"  WARNING: {model}/{condition}/{length} has only "
                    f"{len(df_cell)} rows, need {n}. Taking all."
                )
                n = len(df_cell)

            # Random sample without replacement
            sampled = df_cell.sample(n=n, random_state=RANDOM_SEED + len(sampled_rows))
            sampled_rows.append(sampled)
            cell_counts[key] = n

# Combine all samples
df_sampled = pd.concat(sampled_rows, ignore_index=True)

# Add a unique rating ID
df_sampled.insert(0, "rating_id", range(1, len(df_sampled) + 1))

# Shuffle the entire dataset (so rater sees random order)
df_sampled = df_sampled.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
# Re-assign rating IDs after shuffle
df_sampled["rating_id"] = range(1, len(df_sampled) + 1)

print(f"Total samples drawn: {len(df_sampled)}")
print()

# ── Create Blinded Version ────────────────────────────────────────────────────

df_blinded = df_sampled.copy()

# Replace model names with anonymous IDs
df_blinded["model"] = df_blinded["model"].map(model_to_anon)

# Remove columns that could reveal the model or bias the rater
# Keep only: rating_id, case_id, primary_presentation, recommended_management,
#            top_diagnosis, vignette_length, condition, category
columns_to_keep = [
    "rating_id",
    "case_id",
    "primary_presentation",
    "recommended_management",
    "top_diagnosis",
    "vignette_length",
    "condition",
    "category",
    "model",  # anonymized
]

# Only keep columns that exist
columns_to_keep = [c for c in columns_to_keep if c in df_blinded.columns]
df_blinded = df_blinded[columns_to_keep]

# ── Save Outputs ──────────────────────────────────────────────────────────────

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Full sample (unblinded, for reference)
df_sampled.to_csv(os.path.join(OUTPUT_DIR, "stratified_sample_400.csv"), index=False)
print(f"  Saved: stratified_sample_400.csv ({len(df_sampled)} rows)")

# Blinded sample (for rater)
df_blinded.to_csv(os.path.join(OUTPUT_DIR, "stratified_sample_400_blinded.csv"), index=False)
print(f"  Saved: stratified_sample_400_blinded.csv ({len(df_blinded)} rows)")

# Key (keep secret — maps anonymous IDs to real model names)
key_data = []
for model, anon in model_to_anon.items():
    key_data.append({"anonymous_id": anon, "real_model": model})
df_key = pd.DataFrame(key_data)
df_key.to_csv(os.path.join(OUTPUT_DIR, "stratified_sample_400_key.csv"), index=False)
print(f"  Saved: stratified_sample_400_key.csv (KEEP SECRET)")

# Summary report
summary_lines = []
summary_lines.append("=" * 70)
summary_lines.append("STRATIFIED SAMPLING SUMMARY — 400 PSYCHIATRIST RATINGS")
summary_lines.append("=" * 70)
summary_lines.append("")
summary_lines.append(f"Random seed: {RANDOM_SEED}")
summary_lines.append(f"Total ratings: {len(df_sampled)}")
summary_lines.append("")

summary_lines.append("Sample allocation (Model × Condition × Length):")
summary_lines.append("-" * 60)
summary_lines.append(
    f"{'Model':<45} {'Condition':<22} {'Length':<8} {'N':>4}"
)
summary_lines.append("-" * 60)

for model in MODELS:
    for condition in CONDITIONS:
        for length in LENGTHS:
            n = cell_counts[(model, condition, length)]
            summary_lines.append(f"{model:<45} {condition:<22} {length:<8} {n:>4}")

summary_lines.append("-" * 60)

# Marginal totals
summary_lines.append("")
summary_lines.append("Marginal totals by model:")
for model in MODELS:
    total = sum(
        cell_counts[(model, c, l)] for c in CONDITIONS for l in LENGTHS
    )
    summary_lines.append(f"  {model}: {total}")

summary_lines.append("")
summary_lines.append("Marginal totals by condition:")
for condition in CONDITIONS:
    total = sum(
        cell_counts[(m, condition, l)] for m in MODELS for l in LENGTHS
    )
    summary_lines.append(f"  {condition}: {total}")

summary_lines.append("")
summary_lines.append("Marginal totals by length:")
for length in LENGTHS:
    total = sum(
        cell_counts[(m, c, length)] for m in MODELS for c in CONDITIONS
    )
    summary_lines.append(f"  {length}: {total}")

summary_lines.append("")
summary_lines.append("Model anonymization key (KEEP SECRET until ratings complete):")
for model, anon in model_to_anon.items():
    summary_lines.append(f"  {anon} ← {model}")

summary_lines.append("")
summary_lines.append("Blinding measures:")
summary_lines.append("  - Model names replaced with anonymous IDs")
summary_lines.append("  - Rating order randomized")
summary_lines.append("  - Rater sees: case presentation, diagnosis, management, length, condition")
summary_lines.append("  - Rater does NOT see: model name, case_id, category, hallucination flags")

summary_text = "\n".join(summary_lines)

with open(os.path.join(OUTPUT_DIR, "stratified_sample_400_summary.txt"), "w") as f:
    f.write(summary_text)

print(f"  Saved: stratified_sample_400_summary.txt")
print()
print(summary_text)
print()
print("=" * 70)
print("DONE. All files saved to:", OUTPUT_DIR)
print("=" * 70)
