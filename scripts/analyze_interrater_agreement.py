#!/usr/bin/env python3
"""
Inter-Rater Agreement Analysis — Cohen's Kappa Calculation
==========================================================

Reads completed rating Excel files from both raters and calculates:
  - Cohen's κ (agreement statistic)
  - 95% Confidence Interval (via bootstrap)
  - Stratified agreement (by vignette length, condition)
  - Discordant case identification
  - Summary statistics table

Usage:
  python3 scripts/analyze_interrater_agreement.py \
    --rater-a "04_results/human_validation/PAHS_IRR_RaterA_Completed.xlsx" \
    --rater-b "04_results/human_validation/PAHS_IRR_RaterB_Completed.xlsx"

Or (with default paths):
  python3 scripts/analyze_interrater_agreement.py
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import chi2
import argparse


BASE = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE / "04_results/human_validation"
ANALYSIS_DIR = RESULTS_DIR / "analysis"


def cohen_kappa_score(ratings_a, ratings_b):
    """
    Calculate Cohen's kappa coefficient.
    
    κ = (Po - Pe) / (1 - Pe)
    where Po = observed agreement
          Pe = expected agreement by chance
    """
    ratings_a = np.array(ratings_a, dtype=int)
    ratings_b = np.array(ratings_b, dtype=int)
    
    # Observed agreement
    agreements = (ratings_a == ratings_b).sum()
    n = len(ratings_a)
    po = agreements / n
    
    # Expected agreement by chance
    # For binary classification:
    p0_a = (ratings_a == 0).sum() / n
    p1_a = (ratings_a == 1).sum() / n
    p0_b = (ratings_b == 0).sum() / n
    p1_b = (ratings_b == 1).sum() / n
    
    pe = p0_a * p0_b + p1_a * p1_b
    
    # Kappa
    if pe == 1:
        kappa = 1.0 if po == 1 else 0.0
    else:
        kappa = (po - pe) / (1 - pe)
    
    return kappa, po, pe


def bootstrap_ci(ratings_a, ratings_b, n_bootstrap=5000, ci=95):
    """
    Calculate 95% confidence interval for Cohen's kappa via bootstrap.
    """
    ratings_a = np.array(ratings_a, dtype=int)
    ratings_b = np.array(ratings_b, dtype=int)
    n = len(ratings_a)
    
    kappas = []
    np.random.seed(20260608)
    
    for _ in range(n_bootstrap):
        indices = np.random.choice(n, n, replace=True)
        a_boot = ratings_a[indices]
        b_boot = ratings_b[indices]
        k, _, _ = cohen_kappa_score(a_boot, b_boot)
        kappas.append(k)
    
    kappas = np.array(kappas)
    alpha = (100 - ci) / 2
    ci_lower = np.percentile(kappas, alpha)
    ci_upper = np.percentile(kappas, 100 - alpha)
    
    return ci_lower, ci_upper, kappas


def interpret_kappa(kappa):
    """Interpret kappa value per Landis & Koch (1977)."""
    if kappa >= 0.81:
        return "Almost Perfect"
    elif kappa >= 0.61:
        return "Substantial"
    elif kappa >= 0.41:
        return "Moderate"
    elif kappa >= 0.21:
        return "Fair"
    elif kappa >= 0:
        return "Slight"
    else:
        return "Poor"


def read_rater_excel(filepath):
    """Read inter-rater Excel file and extract Q1 ratings."""
    print(f"\n  Reading: {filepath.name}")
    
    df = pd.read_excel(filepath, sheet_name="Rating_Form")
    
    # Extract relevant columns
    ratings = {
        "case_id": df["Case_ID"].values,
        "case_number": df["Case_Number"].values,
        "q1_rating": df["Q1_Hallucination_Rating"].values,
        "q1_confidence": df["Q2_Confidence"].values,
        "vignette": df["Vignette_Text"].values,
        "fabricated_term": df["Fabricated_Term"].values,
    }
    
    # Clean Q1 ratings (convert to int, handle NaN)
    q1_clean = []
    for q1 in ratings["q1_rating"]:
        try:
            q1_clean.append(int(q1))
        except (ValueError, TypeError):
            q1_clean.append(np.nan)
    
    ratings["q1_rating"] = np.array(q1_clean)
    
    # Remove rows with missing Q1 ratings
    valid_idx = ~np.isnan(ratings["q1_rating"])
    for key in ratings:
        ratings[key] = ratings[key][valid_idx]
    
    print(f"    ✓ Loaded {len(ratings['q1_rating'])} valid ratings")
    return ratings


def main():
    parser = argparse.ArgumentParser(description="Analyze inter-rater hallucination classification agreement")
    parser.add_argument(
        "--rater-a",
        type=str,
        default=str(RESULTS_DIR / "PAHS_IRR_RaterA_Completed.xlsx"),
        help="Path to completed Rater A Excel file"
    )
    parser.add_argument(
        "--rater-b",
        type=str,
        default=str(RESULTS_DIR / "PAHS_IRR_RaterB_Completed.xlsx"),
        help="Path to completed Rater B Excel file"
    )
    
    args = parser.parse_args()
    
    # Check if files exist
    rater_a_path = Path(args.rater_a)
    rater_b_path = Path(args.rater_b)
    
    if not rater_a_path.exists():
        print(f"\n✗ ERROR: Rater A file not found: {rater_a_path}")
        print(f"  Place completed Excel files in {RESULTS_DIR}/")
        return
    
    if not rater_b_path.exists():
        print(f"\n✗ ERROR: Rater B file not found: {rater_b_path}")
        print(f"  Place completed Excel files in {RESULTS_DIR}/")
        return
    
    print("\n" + "="*80)
    print("INTER-RATER AGREEMENT ANALYSIS — COHEN'S KAPPA")
    print("="*80)
    
    # Read ratings
    print("\n[*] Reading rater files...")
    ratings_a = read_rater_excel(rater_a_path)
    ratings_b = read_rater_excel(rater_b_path)
    
    # Verify same number of cases
    if len(ratings_a["q1_rating"]) != len(ratings_b["q1_rating"]):
        print(f"\n✗ ERROR: Different number of ratings")
        print(f"  Rater A: {len(ratings_a['q1_rating'])} cases")
        print(f"  Rater B: {len(ratings_b['q1_rating'])} cases")
        return
    
    # Sort by case number for alignment
    sort_idx_a = np.argsort(ratings_a["case_number"])
    sort_idx_b = np.argsort(ratings_b["case_number"])
    
    for key in ratings_a:
        ratings_a[key] = ratings_a[key][sort_idx_a]
        ratings_b[key] = ratings_b[key][sort_idx_b]
    
    n_cases = len(ratings_a["q1_rating"])
    
    # Calculate Cohen's kappa
    print(f"\n[*] Calculating Cohen's κ...")
    kappa, po, pe = cohen_kappa_score(ratings_a["q1_rating"], ratings_b["q1_rating"])
    ci_lower, ci_upper, kappas_boot = bootstrap_ci(ratings_a["q1_rating"], ratings_b["q1_rating"])
    
    print(f"    ✓ Cohen's κ = {kappa:.4f}")
    print(f"    ✓ 95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
    print(f"    ✓ Observed agreement (Po) = {po:.4f}")
    print(f"    ✓ Expected agreement (Pe) = {pe:.4f}")
    print(f"    ✓ Interpretation: {interpret_kappa(kappa)}")
    
    # Agreement summary
    print(f"\n[*] Agreement Summary:")
    agreements = (ratings_a["q1_rating"] == ratings_b["q1_rating"]).sum()
    disagreements = n_cases - agreements
    print(f"    - Concordant pairs: {agreements}/{n_cases} ({100*agreements/n_cases:.1f}%)")
    print(f"    - Discordant pairs: {disagreements}/{n_cases} ({100*disagreements/n_cases:.1f}%)")
    
    # Stratified analysis (if case IDs contain length info)
    print(f"\n[*] Stratified Analysis:")
    
    results_summary = {
        "metric": [],
        "value": [],
        "interpretation": []
    }
    
    # Overall
    results_summary["metric"].append("Overall")
    results_summary["value"].append(f"κ = {kappa:.3f} [CI: {ci_lower:.3f}–{ci_upper:.3f}]")
    results_summary["interpretation"].append(interpret_kappa(kappa))
    
    # By length (if available in case_id)
    for length in ["S", "L"]:
        length_name = "Short" if length == "S" else "Long"
        mask = np.array([length in cid for cid in ratings_a["case_id"]])
        if mask.sum() > 0:
            a_len = ratings_a["q1_rating"][mask]
            b_len = ratings_b["q1_rating"][mask]
            k_len, _, _ = cohen_kappa_score(a_len, b_len)
            agree_len = (a_len == b_len).sum()
            print(f"    - {length_name} vignettes (n={mask.sum()}): κ = {k_len:.3f} ({agree_len}/{mask.sum()} concordant)")
            results_summary["metric"].append(f"  {length_name}")
            results_summary["value"].append(f"κ = {k_len:.3f}")
            results_summary["interpretation"].append(interpret_kappa(k_len))
    
    # Identify discordant cases
    print(f"\n[*] Discordant Cases (Rater A ≠ Rater B):")
    discord_idx = ratings_a["q1_rating"] != ratings_b["q1_rating"]
    if discord_idx.sum() == 0:
        print(f"    ✓ Perfect agreement! No discordant cases.")
    else:
        print(f"    Found {discord_idx.sum()} discordances:")
        for i, idx in enumerate(np.where(discord_idx)[0][:10]):  # Show first 10
            print(f"    [{i+1}] Case {ratings_a['case_id'][idx]}")
            print(f"        Fabricated term: {ratings_a['fabricated_term'][idx]}")
            print(f"        Rater A: {int(ratings_a['q1_rating'][idx])} | Rater B: {int(ratings_b['q1_rating'][idx])}")
        if discord_idx.sum() > 10:
            print(f"    ... and {discord_idx.sum() - 10} more discordances")
    
    # Prevalence
    print(f"\n[*] Hallucination Prevalence:")
    prev_a = (ratings_a["q1_rating"] == 1).sum() / n_cases
    prev_b = (ratings_b["q1_rating"] == 1).sum() / n_cases
    print(f"    - Rater A: {int((ratings_a['q1_rating'] == 1).sum())}/{n_cases} ({100*prev_a:.1f}%)")
    print(f"    - Rater B: {int((ratings_b['q1_rating'] == 1).sum())}/{n_cases} ({100*prev_b:.1f}%)")
    
    # Generate output table
    print(f"\n[*] Generating summary report...")
    
    summary_df = pd.DataFrame(results_summary)
    output_file = ANALYSIS_DIR / "InterRater_Kappa_Summary.csv"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(output_file, index=False)
    print(f"    ✓ Summary saved to {output_file}")
    
    # Save detailed comparison
    comparison_data = {
        "Case_ID": ratings_a["case_id"],
        "Rater_A_Q1": ratings_a["q1_rating"].astype(int),
        "Rater_B_Q1": ratings_b["q1_rating"].astype(int),
        "Agreement": (ratings_a["q1_rating"] == ratings_b["q1_rating"]).astype(int),
        "Fabricated_Term": ratings_a["fabricated_term"],
    }
    
    comparison_df = pd.DataFrame(comparison_data)
    comparison_file = ANALYSIS_DIR / "InterRater_Detailed_Comparison.csv"
    comparison_df.to_csv(comparison_file, index=False)
    print(f"    ✓ Detailed comparison saved to {comparison_file}")
    
    # Final result
    print("\n" + "="*80)
    if kappa >= 0.60:
        print(f"✓ VALIDATION PASSED: κ = {kappa:.3f} (≥ 0.60)")
        print(f"\nThe hallucination detection algorithm is VALIDATED for use in primary analysis.")
    else:
        print(f"⚠ VALIDATION CONCERN: κ = {kappa:.3f} (< 0.60)")
        print(f"\nRecommendation: Review discordant cases and retrain raters if needed.")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
