.PHONY: help install install-dev lint format test test-cov clean run-dashboard generate-sheets analyze-agreement

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

lint: ## Run linters (ruff)
	ruff check scripts/ src/ tests/

format: ## Format code (ruff)
	ruff format scripts/ src/ tests/

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ -v --cov=src/pahs_llm --cov-report=term-missing

clean: ## Clean build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
	find . -name "*.pyc" -delete 2>/dev/null
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf build/ dist/ *.egg-info

run-dashboard: ## Launch the Streamlit dashboard
	streamlit run src/pahs_llm/dashboard/app.py

generate-sheets: ## Generate rater Excel sheets
	python scripts/generate_rater_sample_400.py

analyze-agreement: ## Analyze inter-rater agreement
	python scripts/analyze_interrater_agreement.py
