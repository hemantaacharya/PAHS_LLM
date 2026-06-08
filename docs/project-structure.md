# PAHS LLM Project Structure

## Overview

This document provides a high-level overview of the PAHS LLM Hallucination Study project structure, including file organization, purpose of each directory, and key components.

## Directory Structure

```
PAHS_LLM/
├── 01_admin/                    # Administrative files
│   └── [study documents, approvals, etc.]
├── 02_data/                     # Data files
│   ├── experimental/            # Study data
│   │   ├── combined_vignettes_clean.json      # 300 vignettes (short + long)
│   │   ├── remaining_7_vignettes.json         # 7 vignettes for validation
│   │   └── vignettes_long_embedded_300_final.json
│   └── processed/               # Processed data
│   └── raw/                     # Raw data sources
├── 03_src/                      # Source code
│   ├── core/                    # Core functionality
│   ├── dashboard/               # Dashboard modules
│   │   ├── config.py
│   │   ├── utils.py
│   │   ├── export.py
│   │   └── README.md
│   └── evaluation/              # Analysis scripts
│       ├── extract_hallucination_data.py
│       ├── pool_hallucination_analysis.py
│       └── [other analysis scripts]
├── 04_results/                  # Results and outputs
│   ├── analysis_ready/          # Cleaned/analyzed data
│   │   └── pooled/              # Multi-model pooled data
│   ├── human_validation/        # Inter-rater reliability data
│   ├── model_specific/          # Model-specific results
│   ├── raw_csv/                 # Raw CSV outputs
│   └── raw_json/                # Raw JSON outputs
├── 05_docs/                     # Documentation
│   └── Phase4_InterRater_ExcelSheets/
│       ├── INDEX.md
│       ├── INTER_RATER_RATING_GUIDE.md
│       ├── PRACTICE_CASES_FOR_RATER_CALIBRATION.md
│       ├── RATER_QUICK_REFERENCE_CARD.md
│       └── PHASE4_EXCEL_MATERIALS_GUIDE.md
├── scripts/                     # Utility scripts
│   ├── generate_interrater_rating_excel.py
│   ├── calculate_cohens_kappa.py
│   ├── calculate_kappa_4raters.py
│   └── [other utility scripts]
├── analyze_gemini.py            # Gemini-specific analysis
├── dashboard_enhanced.py        # Enhanced Streamlit dashboard
├── dashboard.py                 # Original Streamlit dashboard
├── detailed_hallucination_analysis.py
├── main.py                      # Main study execution script
├── pilot.py                     # Pilot testing script
├── recover_7_cases.py           # Recovery script for 7 vignettes
├── requirements.txt             # Python dependencies
├── dashboard_requirements.txt   # Dashboard dependencies
├── README.md                    # Main project README
├── COMPLETE_METHODS_SECTION.md  # Full technical methods
├── REFERENCES_LIBRARY.md        # Literature references
├── DASHBOARD_README.md          # Dashboard documentation
├── PHASE4_README.md             # Phase 4 inter-rater reliability guide
├── PROJECT_STRUCTURE.md         # This file
└── QUICK_START.md               # Quick start guide
```

## Key Components

### 01_admin/
Administrative files including study approvals, ethics documentation, and administrative records.

### 02_data/experimental/
Study data files:
- **combined_vignettes_clean.json**: 300 psychiatric vignettes with short (50–60 words) and long (90–100 words) versions
- Each vignette contains a fabricated detail (token_text) for hallucination detection
- Format: JSON array with case_id, token_id, and blinded IDs

### 03_src/
Source code organized by functionality:

#### core/
Core functionality modules (if any)

#### dashboard/
Streamlit dashboard modules:
- **config.py**: Centralized configuration (colors, paths, labels)
- **utils.py**: Statistical utilities and analysis functions
- **export.py**: Publication-ready export functions
- **README.md**: Dashboard module documentation

#### evaluation/
Analysis and processing scripts:
- **extract_hallucination_data.py**: Extracts hallucination records from raw data
- **pool_hallucination_analysis.py**: Pools data across multiple models
- Other analysis scripts for statistical testing

### 04_results/
Results organized by type:

#### analysis_ready/pooled/
Multi-model pooled data with:
- diagnostic_confidence field (0-100 scale)
- safety_audit_log field (JSON array)
- Statistical summaries and significance tests

#### human_validation/
Inter-rater reliability data:
- Excel templates for raters
- Completed rating forms
- Analysis reports

#### raw_json/
Raw JSON outputs from LLM testing:
- PAHS_STUDY_RESULTS_2026_openai_gpt-5.4-mini.json
- PAHS_STUDY_RESULTS_2026_anthropic_claude-haiku-4-5.json
- PAHS_STUDY_RESULTS_2026_gemini_gemini-3.1-flash-lite.json
- PAHS_STUDY_RESULTS_2026_openrouter_meta-llama_llama-3.3-70b-instruct.json
- PILOT_2026_RESULTS.json

### 05_docs/
Documentation organized by phase:
- Phase 4 inter-rater reliability materials
- Training guides and reference cards

### scripts/
Utility scripts for data generation and analysis:
- Excel template generation
- Kappa calculation
- Agreement analysis
- Other data processing scripts

## Data Flow

```
┌─────────────────┐
│ 02_data/experimental/ │
│  (vignettes)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 03_src/evaluation/ │
│  (pilot.py, main.py) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 04_results/raw_json/ │
│  (raw outputs)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 03_src/evaluation/ │
│  (pool_hallucination_analysis.py) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 04_results/analysis_ready/pooled/ │
│  (cleaned data) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 03_src/dashboard/ │
│  (dashboard_enhanced.py) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Visualization & Export │
└─────────────────┘
```

## File Naming Conventions

### Data Files
- `combined_vignettes_clean.json` — Cleaned vignette dataset
- `PAHS_STUDY_RESULTS_YYYY_MODEL.json` — Raw study results
- `PILOT_YYYY_RESULTS.json` — Pilot results

### Scripts
- `generate_*.py` — Data generation scripts
- `calculate_*.py` — Statistical calculation scripts
- `analyze_*.py` — Analysis scripts

### Documentation
- `*_README.md` — Comprehensive documentation
- `*_GUIDE.md` — Step-by-step guides
- `*_TEMPLATE.md` — Template specifications

## Key Scripts

### Execution Scripts
- **pilot.py**: Pilot testing with 2 vignettes
- **main.py**: Full study execution with 300 vignettes
- **analyze_gemini.py**: Gemini-specific analysis

### Analysis Scripts
- **extract_hallucination_data.py**: Extract hallucination records
- **pool_hallucination_analysis.py**: Pool data across models
- **calculate_cohens_kappa.py**: Cohen's kappa calculation
- **calculate_kappa_4raters.py**: Fleiss' kappa calculation

### Dashboard Scripts
- **dashboard.py**: Original Streamlit dashboard
- **dashboard_enhanced.py**: Enhanced dashboard with advanced features

### Utility Scripts
- **generate_interrater_rating_excel.py**: Create Excel templates
- **recover_7_cases.py**: Recover 7 vignettes
- **validate_rater_sample.py**: Validate rater sample
- **validate_stratified_sample.py**: Validate stratified sample

## Dependencies

### Core Dependencies (requirements.txt)
- Python 3.10+
- Streamlit
- pandas
- numpy
- matplotlib
- seaborn
- scipy
- pydantic
- litellm

### Dashboard Dependencies (dashboard_requirements.txt)
- Streamlit
- pandas
- numpy
- matplotlib
- seaborn
- kaleido
- scipy

## Environment Setup

```bash
# Create virtual environment
/opt/homebrew/bin/python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r dashboard_requirements.txt
```

## Running the Project

### Run Study
```bash
# Pilot testing
python pilot.py

# Full study
python main.py
```

### Run Dashboard
```bash
# Original dashboard
streamlit run dashboard.py

# Enhanced dashboard
streamlit run dashboard_enhanced.py
```

### Run Analysis
```bash
# Extract hallucination data
python 03_src/evaluation/extract_hallucination_data.py

# Pool data across models
python 03_src/evaluation/pool_hallucination_analysis.py

# Calculate inter-rater reliability
python scripts/calculate_cohens_kappa.py
```

## Documentation Index

- **README.md** — Main project overview
- **QUICK_START.md** — Quick start guide
- **PROJECT_STRUCTURE.md** — This file
- **ARCHITECTURE.md** — Technical architecture
- **COMPLETE_METHODS_SECTION.md** — Full technical methods
- **REFERENCES_LIBRARY.md** — Literature references
- **DASHBOARD_README.md** — Dashboard documentation
- **PHASE4_README.md** — Phase 4 inter-rater reliability guide
- **OPENSOURCE_MODEL_SETUP.md** — Open-source model setup
- **MODEL_REFINEMENT_GUIDE.md** — Model upgrade guide
- **STUDY_COMPLETION_CHECKLIST.md** — Study completion checklist
