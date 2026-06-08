#!/usr/bin/env python3
"""
Cohen's Kappa (Pairwise) and Fleiss' Kappa (Multi-Rater)
for 4-Psychiatrist Hallucination Ratings
===========================================================

Usage:
  After all 4 psychiatrists complete their ratings, export each Excel
  Rating Sheet as CSV (with columns: Case_ID, Hallucination, Confidence, Notes)
  and run:

    python calculate_kappa_4raters.py \\
        Psychiatrist_1.csv Psychiatrist_2.csv \\
        Psychiatrist_3.csv Psychiatrist_4.csv

  Or with stratification:
    python calculate_kappa_4raters.py *.csv --stratify model condition vignette_length

Output:
  - Pairwise Cohen's Kappa for all 6 rater pairs
  - Fleiss' Kappa (overall multi-rater agreement)
  - Agreement summary table
  - Stratified Kappa (optional, by model/condition/length)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from math import sqrt
from itertools import combinations
import sys

BASE = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE / "04_results/human_validation"


# ── Cohen's Kappa (Pairwise) ─────────────────────────────────────────────────

def cohens_kappa(rater1, rater2, labels=None):
    """Compute Cohen's Kappa for two raters. Returns dict."""
    rater1 = np.array(rater1)
    rater2 = np.array(rater2)

    if len(rater1) != len(rater2):
        raise ValueError(f"Length mismatch: {len(rater1)} vs {len(rater2)}")

    n = len(rater1)
    if labels is None:
        labels = sorted(set(np.concatenate([rater1, rater2])))

    k = len(labels)
    conf_matrix = np.zeros((k, k), dtype=int)
    label_to_idx = {l: i for i, l in enumerate(labels)}
    for a, b in zip(rater1, rater2):
        conf_matrix[label_to_idx[a]][label_to_idx[b]] += 1

    observed = np.trace(conf_matrix) / n
    row_marginals = conf_matrix.sum(axis=1) / n
    col_marginals = conf_matrix.sum(axis=0) / n
    expected = np.sum(row_marginals * col_marginals)

    if expected == 1.0:
        kappa = 1.0
    else:
        kappa = (observed - expected) / (1 - expected)

    p_o = observed
    p_e = expected
    se_kappa = sqrt((p_o * (1 - p_o)) / (n * (1 - p_e) ** 2)) if (1 - p_e) > 0 else 0

    ci_lower = max(kappa - 1.96 * se_kappa, -1.0)
    ci_upper = min(kappa + 1.96 * se_kappa, 1.0)

    if kappa < 0:
        interp = "Poor"
    elif kappa <= 0.20:
        interp = "Slight"
    elif kappa <= 0.40:
        interp = "Fair"
    elif kappa <= 0.60:
        interp = "Moderate"
    elif kappa <= 0.80:
        interp = "Substantial"
    else:
        interp = "Almost perfect"

    return {
        "n": n,
        "kappa": kappa,
        "se": se_kappa,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "observed": observed,
        "expected": expected,
        "interpretation": interp,
        "confusion_matrix": conf_matrix,
        "labels": labels,
    }


# ── Fleiss' Kappa (Multi-Rater) ──────────────────────────────────────────────

def fleiss_kappa(ratings_matrix, labels=None):
    """
    Compute Fleiss' Kappa for multiple raters.

    Parameters
    ----------
    ratings_matrix : 2D array (n_cases × n_ratings_per_case)
        Each row is one case, each column is one rater's rating.
        For 4 raters rating all cases: shape = (100, 4)
    labels : list — category labels (e.g., [0, 1])

    Returns
    -------
    dict with kappa, interpretation, and details
    """
    ratings = np.array(ratings_matrix)
    n_cases, n_raters = ratings.shape

    if labels is None:
        labels = sorted(set(ratings.flatten()))
    n_categories = len(labels)

    # Build agreement matrix: for each case, count how many raters chose each category
    agreement = np.zeros((n_cases, n_categories))
    for i in range(n_cases):
        for j in range(n_raters):
            cat_idx = labels.index(ratings[i, j])
            agreement[i, cat_idx] += 1

    # Proportion of assignments to each category (overall)
    p_categories = agreement.sum(axis=0) / (n_cases * n_raters)

    # Observed agreement: for each case, proportion of agreeing rater pairs
    P_i = np.zeros(n_cases)
    for i in range(n_cases):
        # Number of agreeing pairs for this case
        agreeing_pairs = sum(agreement[i, k] * (agreement[i, k] - 1) for k in range(n_categories))
        total_pairs = n_raters * (n_raters - 1)
        P_i[i] = agreeing_pairs / total_pairs if total_pairs > 0 else 0

    P_bar = P_i.mean()

    # Expected agreement (by chance)
    P_e = sum(p_categories ** 2)

    # Fleiss' Kappa
    if P_e >= 1.0:
        kappa = 1.0
    else:
        kappa = (P_bar - P_e) / (1 - P_e)

    # Standard error (large sample)
    se = sqrt(2 / (n_cases * n_raters * (n_raters - 1))) if n_cases > 0 else 0
    ci_lower = max(kappa - 1.96 * se, -1.0)
    ci_upper = min(kappa + 1.96 * se, 1.0)

    if kappa < 0:
        interp = "Poor"
    elif kappa <= 0.20:
        interp = "Slight"
    elif kappa <= 0.40:
        interp = "Fair"
    elif kappa <= 0.60:
        interp = "Moderate"
    elif kappa <= 0.80:
        interp = "Substantial"
    else:
        interp = "Almost perfect"

    return {
        "n_cases": n_cases,
        "n_raters": n_raters,
        "kappa": kappa,
        "se": se,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "P_bar": P_bar,
        "P_e": P_e,
        "interpretation": interp,
        "category_proportions": dict(zip(labels, p_categories)),
    }


# ── Reporting ────────────────────────────────────────────────────────────────

def print_pairwise_table(pairwise_results):
    """Print a formatted table of all pairwise Kappa results."""
    print()
    print("=" * 70)
    print("PAIRWISE COHEN'S KAPPA — All 6 Rater Pairs")
    print("=" * 70)
    print(f"{'Pair':<30} {'N':>4} {'κ':>8} {'95% CI':>18} {'Agreement':>10} {'Interpret.':<16}")
    print("-" * 70)

    for (r1, r2, res) in pairwise_results:
        pair_label = f"{r1} vs {r2}"
        ci_str = f"[{res['ci_lower']:.3f}, {res['ci_upper']:.3f}]"
        print(f"{pair_label:<30} {res['n']:>4} {res['kappa']:>8.4f} {ci_str:>18} "
              f"{res['observed']:>9.1%} {res['interpretation']:<16}")

    # Summary statistics
    kappas = [res['kappa'] for _, _, res in pairwise_results]
    print("-" * 70)
    print(f"  Mean κ:   {np.mean(kappas):.4f}")
    print(f"  Median κ: {np.median(kappas):.4f}")
    print(f"  Min κ:    {np.min(kappas):.4f}")
    print(f"  Max κ:    {np.max(kappas):.4f}")
    print(f"  SD κ:     {np.std(kappas):.4f}")
    print("=" * 70)


def print_fleiss_report(fleiss_result):
    """Print Fleiss' Kappa report."""
    print()
    print("=" * 70)
    print("FLEISS' KAPPA — Multi-Rater Agreement (4 Psychiatrists)")
    print("=" * 70)
    print(f"  Cases rated:      {fleiss_result['n_cases']}")
    print(f"  Raters per case:  {fleiss_result['n_raters']}")
    print(f"  Fleiss' κ:        {fleiss_result['kappa']:.4f}")
    print(f"  95% CI:           [{fleiss_result['ci_lower']:.4f}, {fleiss_result['ci_upper']:.4f}]")
    print(f"  Interpretation:   {fleiss_result['interpretation']}")
    print(f"  Observed agree:   {fleiss_result['P_bar']:.1%}")
    print(f"  Expected (chance):{fleiss_result['P_e']:.1%}")
    print()
    print("  Category proportions:")
    for cat, prop in fleiss_result['category_proportions'].items():
        print(f"    {cat}: {prop:.1%}")
    print("=" * 70)


def print_confusion_matrix(r1_name, r2_name, result):
    """Print a single confusion matrix."""
    labels = result['labels']
    cm = result['confusion_matrix']
    print(f"\n  {r1_name} vs {r2_name} — Confusion Matrix:")
    header = "           " + "  ".join(f"{r2_name[:3]}_{l:>3}" for l in labels)
    print(f"  {header}")
    for i, label in enumerate(labels):
        row_str = "  ".join(f"{cm[i][j]:>7}" for j in range(len(labels)))
        print(f"  {r1_name[:3]}_{label:>3}  {row_str}")


# ── Stratified Analysis ──────────────────────────────────────────────────────

def stratified_kappa(merged_df, rater_cols, stratify_cols, labels=None):
    """Compute pairwise Kappa stratified by specified columns."""
    if labels is None:
        labels = [0, 1]

    for col in stratify_cols:
        if col not in merged_df.columns:
            print(f"\n  WARNING: Column '{col}' not found, skipping.")
            continue

        print(f"\n{'─' * 70}")
        print(f"STRATIFIED BY: {col}")
        print(f"{'─' * 70}")

        for val in sorted(merged_df[col].unique()):
            subset = merged_df[merged_df[col] == val]
            if len(subset) < 5:
                print(f"\n  {val}: n={len(subset)} (too few)")
                continue

            print(f"\n  ■ {val} (n={len(subset)}):")
            for c1, c2 in combinations(rater_cols, 2):
                r1 = subset[c1].values
                r2 = subset[c2].values
                res = cohens_kappa(r1, r2, labels=labels)
                ci = f"[{res['ci_lower']:.3f}, {res['ci_upper']:.3f}]"
                print(f"    {c1} vs {c2}: κ={res['kappa']:.3f} {ci} "
                      f"({res['observed']:.0%} agree) — {res['interpretation']}")


# ── Main Analysis ────────────────────────────────────────────────────────────

def run_analysis(csv_files, stratify_cols=None):
    """
    Run full pairwise + Fleiss' Kappa analysis.

    Parameters
    ----------
    csv_files : list of paths — one CSV per rater
    stratify_cols : list of str — columns to stratify by
    """
    labels = [0, 1]

    # Load and merge all rater files
    rater_names = []
    rater_dfs = []
    for fpath in csv_files:
        name = Path(fpath).stem.replace("_rating_sheet", "").replace("_ratings", "")
        df = pd.read_csv(fpath)
        rater_names.append(name)
        rater_dfs.append(df)

    # Merge on case_seq_id (or Case_ID)
    id_col = "case_seq_id" if "case_seq_id" in rater_dfs[0].columns else "Case_ID"
    merged = rater_dfs[0][[id_col]].copy()

    rater_cols = []
    for name, df in zip(rater_names, rater_dfs):
        hall_col = "Hallucination" if "Hallucination" in df.columns else \
                   [c for c in df.columns if "hallucination" in c.lower()][0]
        conf_col = "Confidence" if "Confidence" in df.columns else \
                   [c for c in df.columns if "confidence" in c.lower()][0] if any("confidence" in c.lower() for c in df.columns) else None

        merged[name + "_hall"] = df[hall_col].values
        if conf_col:
            merged[name + "_conf"] = df[conf_col].values
        rater_cols.append(name + "_hall")

    # Add stratification columns from first file
    if stratify_cols:
        for col in stratify_cols:
            if col in rater_dfs[0].columns:
                merged[col] = rater_dfs[0][col].values

    # Drop rows with any missing ratings
    merged_complete = merged.dropna(subset=rater_cols)
    print(f"\nCases with complete ratings from all {len(rater_names)} psychiatrists: "
          f"{len(merged_complete)}")

    # ── Pairwise Cohen's Kappa ────────────────────────────────────────────
    pairwise_results = []
    for c1, c2 in combinations(rater_cols, 2):
        r1 = merged_complete[c1].values
        r2 = merged_complete[c2].values
        res = cohens_kappa(r1, r2, labels=labels)
        pairwise_results.append((c1.replace("_hall", ""), c2.replace("_hall", ""), res))

    print_pairwise_table(pairwise_results)

    # Print confusion matrices
    print("\n" + "=" * 70)
    print("CONFUSION MATRICES")
    print("=" * 70)
    for r1, r2, res in pairwise_results:
        print_confusion_matrix(r1, r2, res)

    # ── Fleiss' Kappa ──────────────────────────────────────────────────────
    ratings_matrix = merged_complete[rater_cols].values
    fleiss_result = fleiss_kappa(ratings_matrix, labels=labels)
    print_fleiss_report(fleiss_result)

    # ── Stratified Analysis ────────────────────────────────────────────────
    if stratify_cols:
        stratified_kappa(merged_complete, rater_cols, stratify_cols, labels=labels)

    # ── Per-case agreement summary ─────────────────────────────────────────
    print("\n" + "=" * 70)
    print("PER-CASE AGREEMENT SUMMARY")
    print("=" * 70)
    n_raters = len(rater_cols)
    agreement_counts = {}
    for _, row in merged_complete.iterrows():
        ratings = tuple(row[rater_cols].values)
        n_agree = max(np.bincount([labels.index(r) for r in ratings]))
        agreement_counts[n_agree] = agreement_counts.get(n_agree, 0) + 1

    for n_agree in sorted(agreement_counts.keys(), reverse=True):
        count = agreement_counts[n_agree]
        pct = count / len(merged_complete) * 100
        desc = {4: "Unanimous (4/4)", 3: "Majority (3/4)", 2: "Split (2/4)", 1: "All disagree"} \
            .get(n_agree, f"{n_agree}/4 agree")
        print(f"  {desc}: {count} cases ({pct:.1f}%)")

    print("=" * 70)

    return pairwise_results, fleiss_result


# ── Demo with Synthetic Data ─────────────────────────────────────────────────

def demo():
    """Run demo with synthetic 4-rater data."""
    print("\n*** DEMO: 4-Rater Kappa with synthetic data ***\n")
    np.random.seed(42)
    n = 100

    # Simulate 4 raters with varying agreement levels
    true_labels = np.random.choice([0, 1], size=n, p=[0.6, 0.4])

    rater_data = {}
    rater_names = ["Psychiatrist_1", "Psychiatrist_2", "Psychiatrist_3", "Psychiatrist_4"]
    accuracies = [0.90, 0.85, 0.88, 0.82]  # Each rater's accuracy

    for name, acc in zip(rater_names, accuracies):
        rater = true_labels.copy()
        flip = np.random.random(n) > acc
        rater[flip] = 1 - rater[flip]
        rater_data[name] = rater

    # Create synthetic CSVs
    import tempfile
    tmpdir = Path(tempfile.mkdtemp())
    csv_files = []
    for name in rater_names:
        df = pd.DataFrame({
            "case_seq_id": range(1, n + 1),
            "condition": np.random.choice(["DEFAULT", "DETERMINISTIC", "SAFETY_INSTRUCTION"], n),
            "vignette_length": np.random.choice(["short", "long"], n),
            "model": np.random.choice(["Model_A", "Model_B", "Model_C", "Model_D"], n),
            "Hallucination": rater_data[name],
            "Confidence": np.random.choice([3, 4, 5], n),
        })
        fpath = tmpdir / f"{name}.csv"
        df.to_csv(fpath, index=False)
        csv_files.append(str(fpath))

    run_analysis(csv_files, stratify_cols=None)

    # Cleanup
    import shutil
    shutil.rmtree(tmpdir)


# ── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) >= 5 and not sys.argv[1].startswith("--"):
        # Real data mode: expect 4 CSV files
        csv_files = []
        stratify = []
        i = 1
        while i < len(sys.argv) and not sys.argv[i].startswith("--"):
            csv_files.append(sys.argv[i])
            i += 1

        if "--stratify" in sys.argv:
            idx = sys.argv.index("--stratify")
            stratify = sys.argv[idx + 1:]

        run_analysis(csv_files, stratify_cols=stratify if stratify else None)
    else:
        print("=" * 70)
        print("4-RATER KAPPA ANALYSIS")
        print("=" * 70)
        demo()
        print("\n" + "=" * 70)
        print("USAGE WITH REAL DATA")
        print("=" * 70)
        print("""
After all 4 psychiatrists complete their ratings:

1. Export each Excel Rating Sheet as CSV
2. Run:

   python calculate_kappa_4raters.py \\
       Psychiatrist_1.csv Psychiatrist_2.csv \\
       Psychiatrist_3.csv Psychiatrist_4.csv

3. With stratification by model/condition/length:

   python calculate_kappa_4raters.py *.csv --stratify model condition vignette_length

Output includes:
  • 6 pairwise Cohen's Kappa values
  • Fleiss' Kappa (overall multi-rater agreement)
  • Confusion matrices for each pair
  • Per-case agreement summary (unanimous, majority, split)
  • Stratified Kappa (optional)
        """)
