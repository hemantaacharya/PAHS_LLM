#!/usr/bin/env python3
"""
Cohen's Kappa Calculator for Hallucination Ratings
===================================================

Usage:
  1. Export the psychiatrist's ratings from the Excel sheet as CSV
     (columns needed: rating_id, hallucination_rating)
  2. If you have a second rater, export their ratings similarly
  3. Run this script to compute Cohen's Kappa and related statistics

Cohen's Kappa interpretation (Landis & Koch, 1977):
  < 0.00     : Poor
  0.00–0.20  : Slight
  0.21–0.40  : Fair
  0.41–0.60  : Moderate
  0.61–0.80  : Substantial
  0.81–1.00  : Almost perfect

Also computes:
  - Observed agreement (simple % agreement)
  - Expected agreement (by chance)
  - 95% confidence interval for Kappa
  - Agreement stratified by model, condition, and length
"""

import pandas as pd
import numpy as np
from pathlib import Path
from math import sqrt

BASE = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE / "04_results/human_validation"


def cohens_kappa(rater1, rater2, labels=None):
    """
    Compute Cohen's Kappa for two sets of categorical ratings.

    Parameters
    ----------
    rater1 : array-like — ratings from rater 1 (e.g., [0, 1, 1, 0, ...])
    rater2 : array-like — ratings from rater 2 (same length)
    labels : list — category labels (default: inferred from data)

    Returns
    -------
    dict with kappa, observed_agreement, expected_agreement, ci_lower, ci_upper,
             confusion_matrix, n, category_prevalence
    """
    rater1 = np.array(rater1)
    rater2 = np.array(rater2)

    if len(rater1) != len(rater2):
        raise ValueError("Rater arrays must be the same length")

    n = len(rater1)
    if labels is None:
        labels = sorted(set(np.concatenate([rater1, rater2])))

    # Confusion matrix (contingency table)
    k = len(labels)
    conf_matrix = np.zeros((k, k), dtype=int)
    label_to_idx = {l: i for i, l in enumerate(labels)}
    for a, b in zip(rater1, rater2):
        conf_matrix[label_to_idx[a]][label_to_idx[b]] += 1

    # Observed agreement (proportion of agreeing ratings)
    observed = np.trace(conf_matrix) / n

    # Expected agreement (by chance, from marginal probabilities)
    row_marginals = conf_matrix.sum(axis=1) / n
    col_marginals = conf_matrix.sum(axis=0) / n
    expected = np.sum(row_marginals * col_marginals)

    # Cohen's Kappa
    if expected == 1.0:
        kappa = 1.0  # Perfect agreement by chance definition
    else:
        kappa = (observed - expected) / (1 - expected)

    # Standard error and 95% CI (large-sample approximation)
    # Using the formula from Fleiss, Cohen, & Everitt (1969)
    p_o = observed
    p_e = expected

    # Variance of kappa (simplified large-sample formula)
    theta1 = (1 / (1 - p_e) ** 2) * (
        p_o * (1 - p_o) / n
    )
    theta2 = (1 / (1 - p_e) ** 2) * (
        2 * (1 - p_o) * (2 * p_o * p_e - p_o - p_e) / (n * (1 - p_e))
    )
    theta3 = (1 / (1 - p_e) ** 2) * (
        (1 - p_o) ** 2 * (p_e - 4 * p_e ** 2) / (n * (1 - p_e) ** 2)
    )

    # Simpler SE formula (Cohen 1960, large sample)
    se_kappa = sqrt(
        (p_o * (1 - p_o)) / (n * (1 - p_e) ** 2)
    )

    ci_lower = kappa - 1.96 * se_kappa
    ci_upper = kappa + 1.96 * se_kappa

    # Category prevalence
    prev_rater1 = {l: int((rater1 == l).sum()) for l in labels}
    prev_rater2 = {l: int((rater2 == l).sum()) for l in labels}

    # Kappa interpretation
    if kappa < 0:
        interpretation = "Poor"
    elif kappa <= 0.20:
        interpretation = "Slight"
    elif kappa <= 0.40:
        interpretation = "Fair"
    elif kappa <= 0.60:
        interpretation = "Moderate"
    elif kappa <= 0.80:
        interpretation = "Substantial"
    else:
        interpretation = "Almost perfect"

    return {
        "n": n,
        "kappa": round(kappa, 4),
        "se_kappa": round(se_kappa, 4),
        "ci_95_lower": round(max(ci_lower, -1.0), 4),
        "ci_95_upper": round(min(ci_upper, 1.0), 4),
        "observed_agreement": round(observed, 4),
        "expected_agreement": round(expected, 4),
        "interpretation": interpretation,
        "confusion_matrix": conf_matrix,
        "labels": labels,
        "prevalence_rater1": prev_rater1,
        "prevalence_rater2": prev_rater2,
    }


def interpret_kappa(kappa):
    """Return interpretation string for a kappa value."""
    if kappa < 0:
        return "Poor"
    elif kappa <= 0.20:
        return "Slight"
    elif kappa <= 0.40:
        return "Fair"
    elif kappa <= 0.60:
        return "Moderate"
    elif kappa <= 0.80:
        return "Substantial"
    else:
        return "Almost perfect"


def print_report(result, title="Cohen's Kappa Report"):
    """Print a formatted report."""
    print("=" * 60)
    print(title)
    print("=" * 60)
    print(f"  N (paired ratings):     {result['n']}")
    print(f"  Cohen's Kappa (κ):      {result['kappa']:.4f}")
    print(f"  95% CI:                 [{result['ci_95_lower']:.4f}, {result['ci_95_upper']:.4f}]")
    print(f"  Interpretation:         {result['interpretation']}")
    print()
    print(f"  Observed agreement:     {result['observed_agreement']:.1%}")
    print(f"  Expected (chance):      {result['expected_agreement']:.1%}")
    print()
    print("  Confusion Matrix:")
    labels = result["labels"]
    cm = result["confusion_matrix"]
    header = "           " + "  ".join(f"R2_{l:>3}" for l in labels)
    print(f"  {header}")
    for i, label in enumerate(labels):
        row_str = "  ".join(f"{cm[i][j]:>5}" for j in range(len(labels)))
        print(f"  R1_{label:>3}  {row_str}")
    print()
    print("  Category prevalence:")
    for l in labels:
        n1 = result["prevalence_rater1"][l]
        n2 = result["prevalence_rater2"][l]
        pct1 = n1 / result["n"] * 100
        pct2 = n2 / result["n"] * 100
        print(f"    {l}: Rater 1 = {n1} ({pct1:.1f}%)  |  Rater 2 = {n2} ({pct2:.1f}%)")
    print("=" * 60)


def demo_with_synthetic_data():
    """
    Demonstrate Cohen's Kappa calculation with synthetic data.
    Replace this with your actual rating data.
    """
    print("\n*** DEMO: Cohen's Kappa with synthetic data ***\n")
    print("Replace this with your actual psychiatrist ratings.\n")

    # Simulated data: 100 cases, two raters
    np.random.seed(42)
    n = 100

    # Simulate rater 1 (e.g., psychiatrist)
    rater1 = np.random.choice([0, 1], size=n, p=[0.6, 0.4])

    # Simulate rater 2 (e.g., second psychiatrist or automated detection)
    # With 85% agreement rate
    rater2 = rater1.copy()
    flip_mask = np.random.random(n) > 0.85
    rater2[flip_mask] = 1 - rater2[flip_mask]

    result = cohens_kappa(rater1, rater2, labels=[0, 1])
    print_report(result, "DEMO: Cohen's Kappa (Synthetic Data)")

    print("\nTo use with your actual data:")
    print("  1. Export ratings from Excel as CSV")
    print("  2. Load with: df = pd.read_csv('your_ratings.csv')")
    print("  3. Call: result = cohens_kappa(df['rater1_hallucination'], df['rater2_hallucination'])")


def analyze_from_dataframe(df, rater1_col, rater2_col,
                           stratify_by=None, labels=None):
    """
    Compute overall and stratified Cohen's Kappa from a DataFrame.

    Parameters
    ----------
    df : DataFrame with rating columns
    rater1_col : str — column name for rater 1
    rater2_col : str — column name for rater 2
    stratify_by : list of str — columns to stratify by (e.g., ['model', 'condition'])
    labels : list — category labels
    """
    # Overall kappa
    r1 = df[rater1_col].values
    r2 = df[rater2_col].values
    result = cohens_kappa(r1, r2, labels=labels)
    print_report(result, "OVERALL Cohen's Kappa")

    # Stratified kappa
    if stratify_by:
        for col in stratify_by:
            if col not in df.columns:
                print(f"\n  WARNING: Column '{col}' not found, skipping stratification")
                continue
            print(f"\n{'─' * 60}")
            print(f"STRATIFIED BY: {col}")
            print(f"{'─' * 60}")
            for val in sorted(df[col].unique()):
                subset = df[df[col] == val]
                if len(subset) < 5:
                    print(f"\n  {val}: n={len(subset)} (too few for reliable kappa)")
                    continue
                r1_s = subset[rater1_col].values
                r2_s = subset[rater2_col].values
                res = cohens_kappa(r1_s, r2_s, labels=labels)
                print(f"\n  {val} (n={res['n']}):")
                print(f"    κ = {res['kappa']:.4f} [{res['ci_95_lower']:.4f}, {res['ci_95_upper']:.4f}] "
                      f"({res['interpretation']})")
                print(f"    Agreement: {res['observed_agreement']:.1%}")


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 3:
        # Usage: python calculate_cohens_kappa.py rater1.csv rater2.csv [--stratify model condition]
        rater1_path = sys.argv[1]
        rater2_path = sys.argv[2]

        df1 = pd.read_csv(rater1_path)
        df2 = pd.read_csv(rater2_path)

        # Merge on rating_id
        df_merged = pd.merge(df1, df2, on="rating_id", suffixes=("_r1", "_r2"))

        # Find stratify columns
        stratify = []
        if "--stratify" in sys.argv:
            idx = sys.argv.index("--stratify")
            stratify = sys.argv[idx + 1:]

        r1_col = "hallucination" if "hallucination" in df_merged.columns else [
            c for c in df_merged.columns if "hallucination" in c and "_r1" in c
        ][0]
        r2_col = "hallucination" if "hallucination" in df_merged.columns else [
            c for c in df_merged.columns if "hallucination" in c and "_r2" in c
        ][0]

        analyze_from_dataframe(df_merged, r1_col, r2_col,
                               stratify_by=stratify if stratify else None,
                               labels=[0, 1])
    else:
        # Demo mode
        demo_with_synthetic_data()

        print("\n" + "=" * 60)
        print("USAGE WITH REAL DATA")
        print("=" * 60)
        print("""
Once you have two sets of ratings, you can:

1. QUICK METHOD — pass CSV files:
   python calculate_cohens_kappa.py rater1_ratings.csv rater2_ratings.csv

2. WITH STRATIFICATION:
   python calculate_cohens_kappa.py rater1.csv rater2.csv --stratify model condition vignette_length

3. IN YOUR OWN SCRIPT:
   from calculate_cohens_kappa import cohens_kappa, analyze_from_dataframe
   
   # Load merged ratings (both raters on same cases)
   df = pd.read_csv('merged_ratings.csv')
   
   # Overall kappa
   result = cohens_kappa(df['rater1_hallucination'], df['rater2_hallucination'])
   print(f"κ = {result['kappa']:.3f}")
   
   # Stratified by model, condition, length
   analyze_from_dataframe(df, 'rater1_hallucination', 'rater2_hallucination',
                          stratify_by=['model', 'condition', 'vignette_length'])
        """)
