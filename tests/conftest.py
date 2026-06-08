"""Shared test fixtures."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def data_dir(project_root):
    """Return the data directory."""
    return project_root / "02_data"


@pytest.fixture
def results_dir(project_root):
    """Return the results directory."""
    return project_root / "04_results"


@pytest.fixture
def sample_vignette_short(data_dir):
    """Load a sample short vignette."""
    path = data_dir / "experimental" / "vignettes_short_embedded_300_final.json"
    if path.exists():
        return json.loads(path.read_text())
    return None


@pytest.fixture
def sample_vignette_long(data_dir):
    """Load a sample long vignette."""
    path = data_dir / "experimental" / "vignettes_long_embedded_300_final.json"
    if path.exists():
        return json.loads(path.read_text())
    return None
