# PAHS LLM Dashboard Documentation

## Overview

The Streamlit dashboard provides comprehensive visualization and analysis of hallucination detection data across multiple LLM models, conditions, and vignette lengths.

## Dashboard Versions

### 1. Original Dashboard (`dashboard.py`)

**Status:** Legacy version, still functional

**Features:**
- Model leaderboard (hallucination rates by model)
- Condition effects (DEFAULT vs. SAFETY_INSTRUCTION vs. DETERMINISTIC)
- Vignette length effects (short vs. long)
- Token-category breakdowns
- Per-case explorer

**Usage:**
```bash
streamlit run dashboard.py
```

### 2. Enhanced Dashboard (`dashboard_enhanced.py`)

**Status:** Current version with advanced features

**New Features:**

#### Modular Architecture (`03_src/dashboard/`)

- **`config.py`**: Centralized configuration (colors, paths, labels)
- **`utils.py`**: Statistical utilities and analysis functions
- **`export.py`**: Publication-ready export functions

#### Tab 7: Diagnostic Confidence Analysis

- Confidence distribution by outcome category (box plots)
- Overconfidence analysis (high ≥80 vs. low <80 confidence)
- Point-biserial correlation statistics
- Scatter plot with LOWESS trendline
- Statistical significance metrics

#### Tab 8: Safety Audit Log Viewer

- Term detection and exclusion patterns
- Safety audit outcomes by model (verified, hallucination_trap, unrecognized)
- Most frequently flagged fabricated terms table
- Detailed breakdown of audit log entries

#### Enhanced Statistical Significance

- Chi-square tests for categorical comparisons
- Bootstrap confidence intervals (1000 iterations)
- Significance stars (* p<0.05, ** p<0.01, *** p<0.001)
- Wilson confidence intervals for rates

#### Publication-Ready Export

- Markdown report generator with statistical summaries
- Figure export to PNG, SVG, PDF (via kaleido)
- Download buttons for filtered data
- Automated report generation

## Running the Enhanced Dashboard

```bash
# Run enhanced dashboard

streamlit run dashboard_enhanced.py

# Regenerate pooled data (if needed)

python 03_src/evaluation/pool_hallucination_analysis.py
```

## Data Requirements

The enhanced dashboard requires updated pooled data with:

- `diagnostic_confidence` field (0-100 scale)
- `safety_audit_log` field (JSON array of audit entries)

## Configuration

All visual settings are centralized in `03_src/dashboard/config.py`:

```python
# Category colors

CATEGORY_COLORS = {
    "Successful Defense": "#2ecc71",
    "Silent Adoption": "#f39c12",
    "Blind Spot": "#e74c3c",
    "False Positive": "#9b59b6",
}

# Model labels

MODEL_LABELS = {
    "openai/gpt-5.4-mini": "GPT-5.4-mini",
    "anthropic/claude-haiku-4-5": "Claude Haiku 4.5",
    "google/gemini-3.1-flash-lite": "Gemini 3.1 Flash Lite",
    "openrouter/meta-llama-llama-3.3-70b-instruct": "LLaMA 3.3 70B",
}

# Path configurations

DATA_PATH = "04_results/analysis_ready/pooled/"
OUTPUT_PATH = "04_results/analysis_ready/pooled/"
```

## Adding New Features

1. **Add configuration** to `03_src/dashboard/config.py`
2. **Add utility functions** to `03_src/dashboard/utils.py`
3. **Add visualization** to `dashboard_enhanced.py`
4. **Update exports** in `03_src/dashboard/export.py`

## Key Benefits

1. **Maintainability**: All configuration in one place, easy to update colors/labels
2. **Extensibility**: Add new features by extending modules
3. **Statistical Rigor**: Proper significance testing on all comparisons
4. **Clinical Insight**: Confidence analysis reveals overconfident hallucinations
5. **Transparency**: Safety audit log shows exactly what terms were flagged
6. **Publication Ready**: Export functions for manuscripts and reports

## Technical Details

### Statistical Methods

- **Chi-square tests**: For categorical comparisons between groups
- **Bootstrap CI**: 1000 iterations for confidence intervals
- **Point-biserial correlation**: Between confidence and detection
- **Wilson CI**: For rate calculations with small sample sizes
- **LOWESS**: Locally weighted scatterplot smoothing for trendlines

### Data Flow

```
Raw JSON Files → Pooling Script → Pooled CSV → Dashboard → Analysis/Export
```

### Dependencies

- Streamlit
- pandas
- numpy
- matplotlib
- seaborn
- kaleido (for figure export)
- scipy (for statistical tests)

## Troubleshooting

### Dashboard won't load

1. Check that pooled data exists: `04_results/analysis_ready/pooled/`
2. Verify all required fields are present in pooled CSV
3. Check Python environment: `source .venv/bin/activate`

### Charts not displaying

1. Ensure matplotlib backend is configured
2. Check data types in config.py
3. Verify all required columns exist in pooled data

### Export not working

1. Install kaleido: `pip install kaleido`
2. Check output directory permissions
3. Verify file paths in config.py

## Future Enhancements

1. **Inter-rater reliability integration** (human validation data)
2. **Cost-effectiveness dashboard** (API costs vs. performance)
3. **Comparative model analyzer** (head-to-head comparisons)
4. **CONSORT flow diagram generator**
5. **Automated manuscript section generation**
