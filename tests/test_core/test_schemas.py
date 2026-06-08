"""Tests for core schemas."""

import pytest


def test_package_import():
    """Test that the package can be imported."""
    import src.pahs_llm
    assert src.pahs_llm.__version__ == "1.0.0"


def test_schemas_import():
    """Test that schemas can be imported from the new package."""
    from src.pahs_llm.core.schemas import ClinicalOutput
    assert ClinicalOutput is not None


def test_evaluation_import():
    """Test that evaluation modules can be imported."""
    from src.pahs_llm.evaluation.extract_hallucination_data import (
        extract_hallucination_records,
    )
    assert extract_hallucination_records is not None
