"""
Dashboard Configuration Module
Centralized configuration for maintainability and easy customization
"""
from pathlib import Path

# ── Data Paths ───────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent.parent
RESULTS_DIR = BASE_DIR / "04_results"

# Pooled analysis paths
POOLED_DIR = RESULTS_DIR / "analysis_ready" / "pooled"
TRIAL_CSV = POOLED_DIR / "pooled_trial_level.csv"
TABLE2_CSV = POOLED_DIR / "table2_outcomes_by_model_condition.csv"
TABLE3_CSV = POOLED_DIR / "table3_condition_effects.csv"
TABLE4_CSV = POOLED_DIR / "table4_length_effects.csv"
TABLE1_CSV = POOLED_DIR / "table1_coverage.csv"
RUN_SUMMARY = POOLED_DIR / "run_summary.json"

# Dashboard data paths
DASHBOARD_JSON = RESULTS_DIR / "analysis_ready" / "PAHS_STUDY_2026_DASHBOARD.json"
VIGNETTES_JSON = BASE_DIR / "02_data" / "experimental" / "combined_vignettes_clean.json"

# ── Visual Configuration ───────────────────────────────────────────────────────
CATEGORY_COLORS = {
    "Successful Defense": "#2ecc71",
    "Silent Adoption": "#f39c12",
    "Blind Spot": "#e74c3c",
    "False Positive": "#9b59b6",
}

CATEGORY_ORDER = [
    "Successful Defense",
    "Silent Adoption",
    "Blind Spot",
    "False Positive",
]

CATEGORY_NUMERIC = {
    "Silent Adoption": 0,
    "False Positive": 1,
    "Blind Spot": 2,
    "Successful Defense": 3,
}

MODEL_COLORS = {
    "anthropic/claude-haiku-4.5": "#9b59b6",
    "gemini/gemini-3.1-flash-lite": "#3498db",
    "openai/gpt-5.4-mini": "#e67e22",
    "openrouter/meta-llama/llama-3.3-70b-instruct": "#1abc9c",
}

MODEL_LABELS = {
    "anthropic/claude-haiku-4.5": "Claude Haiku 4.5",
    "gemini/gemini-3.1-flash-lite": "Gemini 3.1 Flash Lite",
    "openai/gpt-5.4-mini": "GPT-5.4-mini",
    "openrouter/meta-llama/llama-3.3-70b-instruct": "Llama 3.3 70B",
}

CONDITION_COLORS = {
    "DEFAULT": "#2ecc71",
    "DETERMINISTIC": "#3498db",
    "SAFETY_INSTRUCTION": "#e74c3c",
}

TOKEN_CATEGORY_LABELS = {
    "pathway_of_care": "Pathway of care",
    "laboratory_markers": "Laboratory markers",
    "pharmacological_agents": "Pharmacological agents",
    "assessment_diagnostic_criteria": "Assessment / diagnostic",
}

# ── Statistical Configuration ─────────────────────────────────────────────────
ALPHA = 0.05  # Significance level
BOOTSTRAP_ITERATIONS = 1000

# ── Models to Exclude (for testing/experimental) ───────────────────────────────
EXCLUDE_MODELS = {"openai/gpt-5.5", "anthropic/claude-sonnet-4-6"}

# ── Helper Functions ────────────────────────────────────────────────────────
def model_label(model_full: str) -> str:
    """Convert full model identifier to display label."""
    return MODEL_LABELS.get(model_full, model_full.split("/")[-1])

def pct(value, digits: int = 1) -> str:
    """Format decimal as percentage string."""
    if value is None or pd.isna(value):
        return "—"
    return f"{100 * value:.{digits}f}%"

# Import pandas here to avoid circular imports
import pandas as pd