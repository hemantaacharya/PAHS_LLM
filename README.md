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

## Extract Hallucination Data

To pull only hallucination-focused rows from a results file, run:

```bash
python 03_src/evaluation/extract_hallucination_data.py 04_results/raw_json/PILOT_2026_RESULTS.json
```

Use `--format csv` if you want a flat table instead of JSON.
