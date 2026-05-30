"""
PAHS LLM Hallucination Study Dashboard Package
"""
from .config import (
    CATEGORY_COLORS,
    CATEGORY_ORDER,
    MODEL_COLORS,
    MODEL_LABELS,
    CONDITION_COLORS,
    model_label,
    pct,
)
from .utils import (
    category_rates,
    add_statistical_significance,
    bootstrap_ci,
    calculate_cohens_kappa,
    confidence_correlation_analysis,
    analyze_safety_audit_log,
)
from .export import (
    generate_publication_report,
    create_download_button,
    export_figure,
    create_figure_download_package,
)

__all__ = [
    "CATEGORY_COLORS",
    "CATEGORY_ORDER",
    "MODEL_COLORS",
    "MODEL_LABELS",
    "CONDITION_COLORS",
    "model_label",
    "pct",
    "category_rates",
    "add_statistical_significance",
    "bootstrap_ci",
    "calculate_cohens_kappa",
    "confidence_correlation_analysis",
    "analyze_safety_audit_log",
    "generate_publication_report",
    "create_download_button",
    "export_figure",
    "create_figure_download_package",
]