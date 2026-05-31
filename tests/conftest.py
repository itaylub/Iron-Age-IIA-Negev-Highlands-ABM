"""Pytest configuration and shared fixtures."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture(scope="session")
def synthetic_data_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build a synthetic Data/ directory matching the real schema.

    Layout is the one confirmed by ``scripts/inspect_data.py`` against
    the author's local data (May 2026 snapshot) and documented in
    ``docs/DATA.md``.
    """
    from tests.fixtures import make_fixture

    data_dir = tmp_path_factory.mktemp("data")
    make_fixture.write_fixture(data_dir, n_years=4)
    return data_dir


@pytest.fixture()
def env_with_synthetic_data(synthetic_data_dir: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the ``NOMAD_ABM_*`` env vars at the synthetic fixture."""
    monkeypatch.setenv("NOMAD_ABM_DATA_DIR", str(synthetic_data_dir))
    monkeypatch.setenv("NOMAD_ABM_RESULTS_DIR", str(synthetic_data_dir.parent / "results"))
    monkeypatch.setenv(
        "NOMAD_ABM_CALIB_SHP",
        str(synthetic_data_dir / "P_for_calib.shp"),
    )
    os.makedirs(synthetic_data_dir.parent / "results", exist_ok=True)
    return synthetic_data_dir
