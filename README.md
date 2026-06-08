# PAHS_LLM

Patan Academy of Health Sciences - LLM Hallucination Study

Multi-model evaluation of hallucinations in psychiatric clinical vignettes using fabricated token injection.

## Quick Start

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
make install-dev

# Configure API keys
cp .env.example .env
# Edit .env with your API keys

# Run the study
python main.py --provider anthropic
python pilot.py --provider openai
```

## Project Structure

```
PAHS_LLM/
+-- src/pahs_llm/          # Main Python package
|   +-- core/              # Data models and schemas
|   +-- evaluation/        # Hallucination analysis and metrics
|   +-- dashboard/         # Streamlit dashboard
+-- scripts/               # Entry-point scripts
+-- tests/                 # Test suite
+-- docs/                  # Documentation
+-- data/                  # Data directory (gitignored)
+-- results/               # Results directory (gitignored)
+-- Phase4_InterRater_ExcelSheets/  # Human validation materials
```

## Commands

```bash
make install          # Install dependencies
make install-dev      # Install dev dependencies + pre-commit hooks
make lint             # Run linters
make format           # Format code
make test             # Run tests
make test-cov         # Run tests with coverage
make clean            # Clean build artifacts
make generate-sheets  # Generate rater Excel sheets
make analyze-agreement # Analyze inter-rater agreement
make run-dashboard    # Launch Streamlit dashboard
```

## Extract Hallucination Data

```bash
python -m pahs_llm.evaluation.extract_hallucination_data \
    04_results/raw_json/PAHS_STUDY_RESULTS_2026_openai_gpt-5.4-mini.json
```

## Pooled Multi-Model Analysis

```bash
python -m pahs_llm.evaluation.pool_hallucination_analysis
```

Writes trial-level and aggregate CSV tables to `04_results/analysis_ready/pooled/`.

## Interactive Dashboard

```bash
streamlit run src/pahs_llm/dashboard/app.py
```

Includes model leaderboard, condition/length effects, token-category breakdowns, and per-case explorer across all 4 study models (7,200 trials).

## Documentation

### Quick Start & Setup

- [docs/quick-start.md](docs/quick-start.md) - Get started in 5 minutes
- [docs/project-structure.md](docs/project-structure.md) - Project organization
- [docs/architecture.md](docs/architecture.md) - Technical architecture

### Study Documentation

- [COMPLETE_METHODS_SECTION.md](COMPLETE_METHODS_SECTION.md) - Full technical methods for publication
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

### Dashboard

- [docs/dashboard.md](docs/dashboard.md) - Dashboard features and usage

### Phase 4: Human Validation

- [Phase4_InterRater_ExcelSheets/README_Phase4.md](Phase4_InterRater_ExcelSheets/README_Phase4.md) - Overview
- [Phase4_InterRater_ExcelSheets/phase4-guide.md](Phase4_InterRater_ExcelSheets/phase4-guide.md) - Complete workflow
- [Phase4_InterRater_ExcelSheets/INTER_RATER_RATING_GUIDE.md](Phase4_InterRater_ExcelSheets/INTER_RATER_RATING_GUIDE.md) - Rater training
- [Phase4_InterRater_ExcelSheets/PRACTICE_CASES_FOR_RATER_CALIBRATION.md](Phase4_InterRater_ExcelSheets/PRACTICE_CASES_FOR_RATER_CALIBRATION.md) - Training cases
- [Phase4_InterRater_ExcelSheets/RATER_QUICK_REFERENCE_CARD.md](Phase4_InterRater_ExcelSheets/RATER_QUICK_REFERENCE_CARD.md) - Decision guide

## License

[MIT](LICENSE)
