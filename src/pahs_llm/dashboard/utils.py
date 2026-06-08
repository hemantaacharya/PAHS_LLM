"""
Dashboard Utility Functions
Statistical analysis, data processing, and visualization helpers
"""
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple, Optional

from .config import (
    CATEGORY_ORDER,
    CATEGORY_NUMERIC,
    ALPHA,
    BOOTSTRAP_ITERATIONS,
)


def category_rates(frame: pd.DataFrame) -> Dict[str, float]:
    """Calculate outcome category rates for a dataframe."""
    counts = frame["category"].value_counts()
    total = len(frame) or 1
    return {cat: counts.get(cat, 0) / total for cat in CATEGORY_ORDER}


def add_statistical_significance(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    comparison: str = "chi-square"
) -> pd.DataFrame:
    """
    Add p-values and significance indicators to grouped data.
    
    Args:
        df: DataFrame with grouped data
        group_col: Column to group by
        value_col: Binary column to test (0/1)
        comparison: Statistical test to use
        
    Returns:
        DataFrame with p-value and significance columns
    """
    results = []
    
    for group_val in df[group_col].unique():
        group_data = df[df[group_col] == group_val][value_col]
        results.append({
            group_col: group_val,
            "mean": group_data.mean(),
            "std": group_data.std(),
            "n": len(group_data)
        })
    
    result_df = pd.DataFrame(results)
    
    # Calculate pairwise comparisons
    if len(result_df) > 1:
        groups = [df[df[group_col] == g][value_col].values for g in result_df[group_col]]
        
        if comparison == "chi-square" and all(len(g) > 0 for g in groups):
            # Chi-square test for categorical proportions
            contingency = pd.crosstab(df[group_col], df[value_col])
            if contingency.shape[0] > 1 and contingency.shape[1] > 1:
                chi2, p, dof, expected = stats.chi2_contingency(contingency)
                result_df["p_value"] = p
                result_df["significant"] = p < ALPHA
                result_df["significance"] = result_df["p_value"].apply(
                    lambda p: "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
                )
    
    return result_df


def bootstrap_ci(
    data: np.ndarray,
    statistic: callable = np.mean,
    n_iterations: int = BOOTSTRAP_ITERATIONS,
    alpha: float = ALPHA
) -> Tuple[float, float, float]:
    """
    Calculate bootstrap confidence interval.
    
    Returns:
        Tuple of (statistic, lower_ci, upper_ci)
    """
    if len(data) == 0:
        return (0, 0, 0)
    
    bootstrap_stats = []
    for _ in range(n_iterations):
        sample = np.random.choice(data, size=len(data), replace=True)
        bootstrap_stats.append(statistic(sample))
    
    lower = np.percentile(bootstrap_stats, 100 * alpha / 2)
    upper = np.percentile(bootstrap_stats, 100 * (1 - alpha / 2))
    
    return (statistic(data), lower, upper)


def calculate_cohens_kappa(
    rater1: List[int],
    rater2: List[int]
) -> Tuple[float, float]:
    """
    Calculate Cohen's kappa for inter-rater reliability.
    
    Returns:
        Tuple of (kappa, std_error)
    """
    # Create confusion matrix
    observed = np.zeros((2, 2))
    for a, b in zip(rater1, rater2):
        observed[int(a), int(b)] += 1
    
    # Calculate expected agreement
    row_margins = observed.sum(axis=1) / len(rater1)
    col_margins = observed.sum(axis=0) / len(rater2)
    expected = np.outer(row_margins, col_margins)
    
    # Observed agreement
    po = np.trace(observed) / len(rater1)
    
    # Expected agreement
    pe = np.sum(expected * expected) / len(rater1)
    
    # Kappa
    kappa = (po - pe) / (1 - pe) if (1 - pe) > 0 else 0
    
    # Standard error (simplified)
    se = np.sqrt((po * (1 - po)) / (len(rater1) * (1 - pe) ** 2))
    
    return kappa, se


def confidence_correlation_analysis(
    df: pd.DataFrame,
    confidence_col: str = "diagnostic_confidence",
    outcome_col: str = "hallucination_detected"
) -> Dict:
    """
    Analyze correlation between diagnostic confidence and hallucination outcomes.
    
    Returns:
        Dictionary with correlation statistics
    """
    if confidence_col not in df.columns or outcome_col not in df.columns:
        return {}
    
    # Point-biserial correlation (confidence vs binary outcome)
    corr, p_value = stats.pointbiserialr(df[outcome_col].astype(int), df[confidence_col])
    
    # Group statistics
    high_conf = df[df[confidence_col] >= 80]
    low_conf = df[df[confidence_col] < 80]
    
    return {
        "correlation": corr,
        "p_value": p_value,
        "high_conf_mean": high_conf[outcome_col].mean() if len(high_conf) > 0 else 0,
        "low_conf_mean": low_conf[outcome_col].mean() if len(low_conf) > 0 else 0,
        "high_conf_n": len(high_conf),
        "low_conf_n": len(low_conf),
        "overconfident_rate": high_conf[outcome_col].mean() if len(high_conf) > 0 else 0,
    }


def analyze_safety_audit_log(safety_log: List[Dict]) -> Dict:
    """
    Analyze safety audit log for detection patterns.
    
    Args:
        safety_log: List of safety audit entries
        
    Returns:
        Dictionary with analysis results
    """
    if not safety_log:
        return {"total_terms": 0, "verified": 0, "hallucination_trap": 0, "unrecognized": 0}
    
    statuses = [entry.get("status", "unknown") for entry in safety_log]
    
    return {
        "total_terms": len(statuses),
        "verified": statuses.count("verified"),
        "hallucination_trap": statuses.count("hallucination_trap"),
        "unrecognized": statuses.count("unrecognized"),
        "excluded_terms": [e["term"] for e in safety_log if e.get("status") == "hallucination_trap"],
    }