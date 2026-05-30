# Dashboard Module

Modular Streamlit dashboard for the PAHS LLM Hallucination Study.

## Structure

```
03_src/dashboard/
├── __init__.py          # Package exports
├── config.py            # Centralized configuration (colors, paths, labels)
├── utils.py             # Statistical utilities and analysis functions
├── export.py            # Publication-ready export functions
└── README.md            # This file
```

## Usage

### Run Enhanced Dashboard
```bash
streamlit run dashboard_enhanced.py
```

### Import Modules
```python
from dashboard.config import MODEL_COLORS, CATEGORY_ORDER, model_label
from dashboard.utils import category_rates, confidence_correlation_analysis
from dashboard.export import generate_publication_report
```

## Configuration

All visual and data paths are centralized in `config.py`:
- **Data paths**: Update `TRIAL_CSV`, `TABLE2_CSV`, etc. for new data locations
- **Colors**: Modify `CATEGORY_COLORS`, `MODEL_COLORS` for theme changes
- **Labels**: Update `MODEL_LABELS`, `TOKEN_CATEGORY_LABELS` for display names

## Enhancements

### v2.0 Features
1. **Modular Architecture**: Separated config, utils, and export logic
2. **Diagnostic Confidence Analysis**: Tab 7 - correlation between confidence and hallucination
3. **Safety Audit Log Viewer**: Tab 8 - detailed term detection analysis
4. **Statistical Significance**: Added p-values and significance indicators
5. **Enhanced Export**: Publication-ready report generation

## Adding New Features

1. Add configuration to `config.py`
2. Add utility functions to `utils.py`
3. Add visualization to `dashboard_enhanced.py`
4. Update `__init__.py` exports

## Dependencies

- pandas
- plotly
- streamlit
- scipy
- numpy