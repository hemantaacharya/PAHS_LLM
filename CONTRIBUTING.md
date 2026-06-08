# Contributing to PAHS_LLM

Thank you for your interest in contributing to the PAHS LLM Hallucination Study project.

## Getting Started

1. Clone the repository
2. Create a virtual environment: `python3 -m venv .venv && source .venv/bin/activate`
3. Install dependencies: `make install-dev`
4. Copy `.env.example` to `.env` and add your API keys

## Development Workflow

### Code Style

- Python: Follow PEP 8 with ruff enforcement
- Line length: 100 characters
- Use type hints where practical

### Running Tests

```bash
make test          # Run all tests
make test-cov      # Run with coverage
```

### Linting and Formatting

```bash
make lint          # Check for issues
make format        # Auto-format code
```

### Pre-commit Hooks

Pre-commit hooks are configured automatically with `make install-dev`. They run ruff linting and formatting on every commit.

## Project Structure

```
src/pahs_llm/       # Main Python package
  core/             # Data models and schemas
  evaluation/       # Hallucination analysis and metrics
  dashboard/        # Streamlit dashboard
scripts/            # Entry-point scripts
tests/              # Test suite
docs/               # Documentation
data/               # Data directory (gitignored)
results/            # Results directory (gitignored)
```

## Submitting Changes

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes with tests
3. Run `make lint` and `make test`
4. Commit with a clear message
5. Push and open a pull request

## Questions?

Contact the project maintainer: Hemanta Acharya (hemanta@pahs.edu.np)
