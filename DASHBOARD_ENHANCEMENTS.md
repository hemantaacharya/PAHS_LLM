# Dashboard Enhancements v2.0

## Overview

The Streamlit dashboard has been enhanced with modular architecture and new analytical features while maintaining backward compatibility with the original `dashboard.py`.

## New Features

### 1. **Modular Architecture** (`03_src/dashboard/`)
- **`config.py`**: Centralized configuration (colors, paths, labels)
- **`utils.py`**: Statistical utilities and analysis functions
- **`export.py`**: Publication-ready export functions
- Easy to maintain and extend

### 2. **Diagnostic Confidence Analysis** (Tab 7)
- Confidence distribution by outcome category
- Overconfidence analysis (high vs. low confidence models)
- Point-biserial correlation between confidence and detection
- Scatter plot with trendline analysis

### 3. **Safety Audit Log Viewer** (Tab 8)
- Term detection and exclusion patterns
- Safety audit outcomes by model
- Most frequently flagged fabricated terms
- Detailed breakdown of verified vs. hallucination trap terms

### 4. **Statistical Significance Indicators**
- P-values on all comparative visualizations
- Chi-square tests for categorical comparisons
- Bootstrap confidence intervals
- Significance stars (*, **, ***) on charts

### 5. **Enhanced Export Functionality**
- Publication-ready markdown reports
- Figure export to PNG, SVG, PDF
- Download buttons for filtered data
- Report generation with statistical summaries

## Running the Enhanced Dashboard

```bash
# Run enhanced dashboard
streamlit run dashboard_enhanced.py

# Or run original dashboard (still works)
streamlit run dashboard.py
```

## Data Requirements

The enhanced dashboard requires updated pooled data with:
- `diagnostic_confidence` field (0-100 scale)
- `safety_audit_log` field (JSON array of audit entries)

Run the pooling script to update:
```bash
python 03_src/evaluation/pool_hallucination_analysis.py
```

## Configuration

All visual settings are in `03_src/dashboard/config.py`:

```python
# Colors
CATEGORY_COLORS = {
    "Successful Defense": "#2ecc71",
    "Silent Adoption": "#f39c12",
    "Blind Spot": "#e74c3c",
    "False Positive": "#9b59b6",
}

# Model labels
MODEL_LABELS = {
    "openai/gpt-5.4-mini": "GPT-5.4-mini",
    "anthropic/claude-haiku-4.5": "Claude Haiku 4.5",
    ...
}
```

## Adding New Features

1. Add configuration to `config.py`
2. Add utility functions to `utils.py`
3. Add visualization to `dashboard_enhanced.py`
4. Update `__init__.py` exports

## Future Enhancements (Planned)

- Inter-rater reliability integration
- Cost-effectiveness dashboard
- Comparative model analyzer
- CONSORT flow diagram generator
- LaTeX table export
- Machine learning insights

## File Structure

```
PAHS_LLM/
├── dashboard.py              # Original dashboard (unchanged)
├── dashboard_enhanced.py     # Enhanced dashboard with new features
├── dashboard_requirements.txt # Dashboard-specific dependencies
├── DASHBOARD_ENHANCEMENTS.md  # This file
└── 03_src/dashboard/
    ├── __init__.py
    ├── config.py
    ├── utils.py
    ├── export.py
    └── README.md
```

## Maintenance Notes

- All paths use `pathlib.Path` for cross-platform compatibility
- Statistical functions use scipy for robust calculations
- Bootstrap iterations: 1000 (configurable in config.py)
- Significance level: α = 0.05 (configurable in config.py)