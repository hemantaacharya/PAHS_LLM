# PAHS LLM — Quick Start Guide

## Prerequisites

- Python 3.10 or higher
- Virtual environment (recommended)
- API keys for LLM providers (OpenAI, Anthropic, Google)

## Quick Setup (5 minutes)

```bash
# 1. Create virtual environment
/opt/homebrew/bin/python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
pip install -r dashboard_requirements.txt

# 3. Set environment variables (optional, for specific models)
export PAHS_OPENAI_MODEL=openai/gpt-5.4-mini
export PAHS_ANTHROPIC_MODEL=anthropic/claude-haiku-4-5
export PAHS_GEMINI_MODEL=google/gemini-3.1-flash-lite
```

## Run the Study

### Pilot Testing (Quick test)

```bash
python pilot.py
```

Tests 2 vignettes × 4 models × 3 conditions = 24 trials

### Full Study (Main execution)

```bash
python main.py
```

Tests 300 vignettes × 4 models × 3 conditions × 2 lengths = 7,200 trials

**Expected time:** 2–4 hours (depending on API speeds)

## View Results

### Original Dashboard

```bash
streamlit run dashboard.py
```

Features:
- Model leaderboard
- Condition effects
- Vignette length effects
- Per-case explorer

### Enhanced Dashboard (Recommended)

```bash
streamlit run dashboard_enhanced.py
```

Additional features:
- Diagnostic confidence analysis
- Safety audit log viewer
- Publication-ready exports
- Advanced statistical tests

## Analyze Hallucination Data

### Extract Hallucination Records

```bash
python 03_src/evaluation/extract_hallucination_data.py 04_results/raw_json/PILOT_2026_RESULTS.json
```

### Pool Data Across Models

```bash
python 03_src/evaluation/pool_hallucination_analysis.py
```

Generates pooled CSV with:
- All 7,200 trials
- Statistical summaries
- Significance tests

## Inter-Rater Reliability (Phase 4)

### Generate Rating Templates

```bash
python scripts/generate_interrater_rating_excel.py
```

Creates Excel templates in `04_results/human_validation/`

### Calculate Kappa

```bash
python scripts/calculate_cohens_kappa.py
```

Calculates Cohen's kappa from completed rating forms

## Common Tasks

### Switch Models

```bash
# OpenAI
export PAHS_OPENAI_MODEL=openai/gpt-5.4
python main.py

# Anthropic
export PAHS_ANTHROPIC_MODEL=anthropic/claude-3-sonnet
python main.py

# Google
export PAHS_GEMINI_MODEL=google/gemini-2.0-flash
python main.py
```

### View Specific Model Results

```bash
# OpenAI
cat 04_results/raw_json/PAHS_STUDY_RESULTS_2026_openai_gpt-5.4-mini.json | jq

# Anthropic
cat 04_results/raw_json/PAHS_STUDY_RESULTS_2026_anthropic_claude-haiku-4-5.json | jq

# Google
cat 04_results/raw_json/PAHS_STUDY_RESULTS_2026_gemini_gemini-3.1-flash-lite.json | jq

# OpenRouter (LLaMA)
cat 04_results/raw_json/PAHS_STUDY_RESULTS_2026_openrouter_meta-llama_llama-3.3-70b-instruct.json | jq
```

### Export to CSV

```bash
# Extract hallucination data as CSV
python 03_src/evaluation/extract_hallucination_data.py 04_results/raw_json/PILOT_2026_RESULTS.json --format csv
```

## Project Structure

```
PAHS_LLM/
├── 02_data/experimental/          # Vignettes (300 cases)
├── 03_src/evaluation/             # Analysis scripts
├── 04_results/raw_json/           # Raw LLM outputs
├── 04_results/analysis_ready/     # Cleaned data
├── 03_src/dashboard/              # Dashboard modules
├── scripts/                       # Utility scripts
└── pilot.py, main.py              # Main execution scripts
```

## Key Files

- **pilot.py** — Pilot testing script
- **main.py** — Full study execution
- **dashboard_enhanced.py** — Enhanced dashboard
- **03_src/evaluation/pool_hallucination_analysis.py** — Data pooling
- **02_data/experimental/combined_vignettes_clean.json** — Vignette dataset

## Documentation

- **README.md** — Main project overview
- **PROJECT_STRUCTURE.md** — Project structure
- **DASHBOARD_README.md** — Dashboard documentation
- **PHASE4_README.md** — Inter-rater reliability guide
- **COMPLETE_METHODS_SECTION.md** — Full technical methods
- **REFERENCES_LIBRARY.md** — Literature references

## Troubleshooting

### Virtual environment not activated

```bash
source .venv/bin/activate
```

### Module not found

```bash
pip install -r requirements.txt
```

### Dashboard won't load

```bash
# Check pooled data exists
ls 04_results/analysis_ready/pooled/

# Regenerate pooled data
python 03_src/evaluation/pool_hallucination_analysis.py
```

### API errors

- Check API keys are set correctly
- Verify API quotas are not exceeded
- Check network connectivity

## Next Steps

1. **Read the full documentation** in README.md
2. **Explore the dashboard** to understand your data
3. **Review the methods** in COMPLETE_METHODS_SECTION.md
4. **Check Phase 4 guide** if conducting inter-rater validation

## Support

For detailed information, see:
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) — Project organization
- [DASHBOARD_README.md](DASHBOARD_README.md) — Dashboard features
- [PHASE4_README.md](PHASE4_README.md) — Inter-rater reliability
- [COMPLETE_METHODS_SECTION.md](COMPLETE_METHODS_SECTION.md) — Technical methods
