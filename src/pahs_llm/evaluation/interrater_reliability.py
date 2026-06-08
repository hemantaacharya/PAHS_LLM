"""
Inter-rater Reliability Module for PAHS LLM Hallucination Study

Implements Cohen's kappa and related agreement metrics for hallucination labeling
by independent raters on a subset of model outputs.
"""

import json
import argparse
from collections import defaultdict
from typing import List, Dict, Tuple
import math


def cohens_kappa(rater1: List[int], rater2: List[int]) -> Tuple[float, float]:
    """
    Calculate Cohen's kappa coefficient and 95% CI for binary agreement.
    
    Args:
        rater1: List of binary labels (0/1) from rater 1
        rater2: List of binary labels (0/1) from rater 2
    
    Returns:
        Tuple of (kappa, se) where se is standard error for 95% CI calculation
    """
    if len(rater1) != len(rater2):
        raise ValueError("Rater sequences must be same length")
    
    n = len(rater1)
    
    # Observed agreement
    po = sum(1 for r1, r2 in zip(rater1, rater2) if r1 == r2) / n
    
    # Marginal frequencies
    p1_yes = sum(rater1) / n
    p1_no = 1 - p1_yes
    p2_yes = sum(rater2) / n
    p2_no = 1 - p2_yes
    
    # Expected agreement under independence
    pe = (p1_yes * p2_yes) + (p1_no * p2_no)
    
    # Cohen's kappa
    if pe == 1:
        kappa = 0
    else:
        kappa = (po - pe) / (1 - pe)
    
    # Standard error (Fleiss & Cohen, 1973)
    po_yes = sum(1 for r1, r2 in zip(rater1, rater2) if r1 == 1 and r2 == 1) / n
    po_no = sum(1 for r1, r2 in zip(rater1, rater2) if r1 == 0 and r2 == 0) / n
    
    numerator = (
        po_yes * (1 - p1_yes - p2_yes) ** 2 +
        po_no * (1 - p1_no - p2_no) ** 2
    )
    denominator = (1 - pe) ** 2
    
    var_kappa = (numerator - (po - pe) ** 2) / (n * denominator)
    se = math.sqrt(max(0, var_kappa))
    
    return kappa, se


def percent_agreement(rater1: List[int], rater2: List[int]) -> float:
    """Calculate simple percent agreement between two raters."""
    n = len(rater1)
    return 100 * sum(1 for r1, r2 in zip(rater1, rater2) if r1 == r2) / n


def generate_interrater_summary(records: List[Dict]) -> Dict:
    """
    Generate inter-rater reliability summary from labeled records.
    
    Each record should have:
    - case_id, model, condition, length
    - rater_1_hallucination: bool (detected hallucination)
    - rater_2_hallucination: bool (detected hallucination)
    
    Returns summary dict with kappa, CI, and stratified analyses.
    """
    if not records:
        return {"error": "No records provided"}
    
    summary = {
        "total_cases_rated": len(records),
        "overall": {},
        "by_vignette_length": {},
        "by_condition": {},
        "by_model": {},
        "stratified": {}
    }
    
    # Overall agreement
    rater1_overall = [r.get("rater_1_hallucination", 0) for r in records]
    rater2_overall = [r.get("rater_2_hallucination", 0) for r in records]
    
    kappa_overall, se_overall = cohens_kappa(rater1_overall, rater2_overall)
    pct_overall = percent_agreement(rater1_overall, rater2_overall)
    
    summary["overall"] = {
        "percent_agreement": round(pct_overall, 1),
        "cohens_kappa": round(kappa_overall, 3),
        "standard_error": round(se_overall, 3),
        "ci_95_lower": round(kappa_overall - 1.96 * se_overall, 3),
        "ci_95_upper": round(kappa_overall + 1.96 * se_overall, 3),
        "interpretation": _kappa_interpretation(kappa_overall)
    }
    
    # Stratified by vignette length
    by_length = defaultdict(list)
    for r in records:
        length = r.get("length", "unknown")
        by_length[length].append(r)
    
    for length, length_records in by_length.items():
        r1 = [r.get("rater_1_hallucination", 0) for r in length_records]
        r2 = [r.get("rater_2_hallucination", 0) for r in length_records]
        k, se = cohens_kappa(r1, r2)
        summary["by_vignette_length"][length] = {
            "n": len(length_records),
            "percent_agreement": round(percent_agreement(r1, r2), 1),
            "cohens_kappa": round(k, 3),
            "ci_95_lower": round(k - 1.96 * se, 3),
            "ci_95_upper": round(k + 1.96 * se, 3)
        }
    
    # Stratified by condition
    by_cond = defaultdict(list)
    for r in records:
        cond = r.get("condition", "unknown")
        by_cond[cond].append(r)
    
    for cond, cond_records in by_cond.items():
        r1 = [r.get("rater_1_hallucination", 0) for r in cond_records]
        r2 = [r.get("rater_2_hallucination", 0) for r in cond_records]
        k, se = cohens_kappa(r1, r2)
        summary["by_condition"][cond] = {
            "n": len(cond_records),
            "percent_agreement": round(percent_agreement(r1, r2), 1),
            "cohens_kappa": round(k, 3),
            "ci_95_lower": round(k - 1.96 * se, 3),
            "ci_95_upper": round(k + 1.96 * se, 3)
        }
    
    # Stratified by model
    by_model = defaultdict(list)
    for r in records:
        model = r.get("model", "unknown")
        by_model[model].append(r)
    
    for model, model_records in by_model.items():
        r1 = [r.get("rater_1_hallucination", 0) for r in model_records]
        r2 = [r.get("rater_2_hallucination", 0) for r in model_records]
        k, se = cohens_kappa(r1, r2)
        summary["by_model"][model] = {
            "n": len(model_records),
            "percent_agreement": round(percent_agreement(r1, r2), 1),
            "cohens_kappa": round(k, 3),
            "ci_95_lower": round(k - 1.96 * se, 3),
            "ci_95_upper": round(k + 1.96 * se, 3)
        }
    
    return summary


def _kappa_interpretation(kappa: float) -> str:
    """Interpret kappa value per Landis & Koch (1977) scale."""
    if kappa < 0:
        return "Poor agreement (kappa < 0)"
    elif kappa < 0.20:
        return "Slight agreement (0 - 0.20)"
    elif kappa < 0.40:
        return "Fair agreement (0.21 - 0.40)"
    elif kappa < 0.60:
        return "Moderate agreement (0.41 - 0.60)"
    elif kappa < 0.80:
        return "Substantial agreement (0.61 - 0.80)"
    else:
        return "Almost perfect agreement (0.81 - 1.00)"


def main():
    parser = argparse.ArgumentParser(
        description="Calculate inter-rater reliability (Cohen's kappa) for hallucination labeling."
    )
    parser.add_argument(
        "labeled_json",
        help="Path to JSON file containing records with rater_1_hallucination and rater_2_hallucination fields."
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output file for summary. Defaults to stdout + JSON file."
    )
    
    args = parser.parse_args()
    
    with open(args.labeled_json, 'r') as f:
        records = json.load(f)
    
    summary = generate_interrater_summary(records)
    
    # Print to console
    print(json.dumps(summary, indent=2))
    
    # Write to file if specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\nSummary written to {args.output}")


if __name__ == "__main__":
    main()
