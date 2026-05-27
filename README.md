# PAHS_LLM

Patan Academy of Health Sciences - LLM Hallucination Study

## Setup

Use the workspace-local `.venv` as the single Python environment for this repo.

```bash
/opt/homebrew/bin/python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

Run a single provider or model with the new CLI filters:

```bash
python pilot.py --provider openai
python main.py --provider anthropic
python pilot.py --model openai/gpt-5-mini
```

## Model Selection & Customization

The default models are low-cost variants suitable for efficient testing. To use different model versions or customize the defaults:

```bash
# Use higher-performance models
export PAHS_OPENAI_MODEL=openai/gpt-5.4
export PAHS_ANTHROPIC_MODEL=anthropic/claude-3-sonnet
export PAHS_GEMINI_MODEL=google/gemini-2.0-flash

# Then run
python pilot.py --vignettes-count 293
```

**For detailed model comparison and upgrade guidance, see [MODEL_REFINEMENT_GUIDE.md](MODEL_REFINEMENT_GUIDE.md).**

## Extract Hallucination Data

To pull only hallucination-focused rows from a results file, run:

```bash
python 03_src/evaluation/extract_hallucination_data.py 04_results/raw_json/PILOT_2026_RESULTS.json
```

Use `--format csv` if you want a flat table instead of JSON.

## Pooled Multi-Model Analysis

To generate standardized pooled tables across all raw JSON result files:

```bash
python 03_src/evaluation/pool_hallucination_analysis.py
```

This writes trial-level and aggregate CSV tables to `04_results/analysis_ready/pooled/`.
