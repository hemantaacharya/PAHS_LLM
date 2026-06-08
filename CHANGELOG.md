# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-06-08

### Added
- Initial release of PAHS LLM Hallucination Study pipeline
- Multi-model LLM evaluation framework (OpenAI, Anthropic, Gemini, OpenRouter)
- Fabricated token injection system for hallucination detection
- Three prompt conditions: DEFAULT, SAFETY_INSTRUCTION, DETERMINISTIC
- Two vignette lengths: short (~50-60 words), long (~90-100 words)
- Automated hallucination extraction and analysis
- Inter-rater reliability validation framework
- Excel rater sheet generation (4 reviewers x 100 cases)
- Streamlit dashboard for results visualization
- Cohen's kappa calculation for agreement analysis
- Stratified sampling across all model/condition/length combinations

### Project Structure
- Modular `src/pahs_llm/` package with core, evaluation, and dashboard modules
- `scripts/` for entry-point scripts
- `tests/` with pytest infrastructure
- `pyproject.toml` for modern Python packaging
- `.editorconfig` for consistent formatting
- `Makefile` for common development tasks
- `.pre-commit-config.yaml` for code quality automation
