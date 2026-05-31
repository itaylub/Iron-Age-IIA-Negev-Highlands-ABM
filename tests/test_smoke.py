"""Smoke tests: import the package and walk the obvious entry points.

These tests don't try to reproduce any scientific result. They
exercise the import chain, the CLI surface, and the synthetic data
fixture — enough to catch packaging regressions (broken imports,
missing files, dependency drift) on every push.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import h5py
import numpy as np
import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_package_imports():
    """``import nomad_abm`` works and exposes a version string."""
    import nomad_abm

    assert isinstance(nomad_abm.__version__, str)
    assert nomad_abm.__version__


def test_cli_help_runs():
    """``python -m nomad_abm run --help`` exits cleanly."""
    proc = subprocess.run(
        [sys.executable, "-m", "nomad_abm", "run", "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, f"stderr:\n{proc.stderr}"
    assert "--config" in proc.stdout
    assert "--seed" in proc.stdout


def test_legacy_shim_redirects(env_with_synthetic_data):
    """The Code/ shim re-exports the canonical model symbols."""
    # The shim adds src/ to sys.path and re-exports from nomad_abm.model.
    sys.path.insert(0, str(REPO_ROOT / "Code"))
    try:
        import model_opt  # noqa: F401  — exercising the shim
    finally:
        sys.path.remove(str(REPO_ROOT / "Code"))
    assert hasattr(model_opt, "run_model_opt")


def test_synthetic_fixture_schema_matches_real(synthetic_data_dir):
    """The fixture matches the schema documented in docs/DATA.md."""
    # yearly_data_10_25.h5: groups named group_0..N, datasets array_0..M.
    with h5py.File(synthetic_data_dir / "yearly_data_10_25.h5", "r") as f:
        top = sorted(f.keys())
        assert all(k.startswith("group_") for k in top)
        first = f[top[0]]
        assert sorted(first.keys()) == ["array_0", "array_1", "array_2"]
        assert first["array_0"].shape == (318, 280)

    # per_data_10_25.h5: singleton group_1 + sibling metadata group.
    with h5py.File(synthetic_data_dir / "per_data_10_25.h5", "r") as f:
        assert set(f.keys()) == {"group_1", "metadata"}
        assert "array_0" in f["group_1"]

    # Both .npy rasters are 318x280 uint8 binary masks.
    for name in ("place_raster.npy", "ext_raster.npy"):
        arr = np.load(synthetic_data_dir / name)
        assert arr.shape == (318, 280)
        assert arr.dtype == np.uint8
        assert set(np.unique(arr)).issubset({0, 1})


def test_synthetic_calib_shapefile_has_both_classes(synthetic_data_dir):
    """Calibration shapefile must contain both value=1 and value=2."""
    geopandas = pytest.importorskip("geopandas")
    gdf = geopandas.read_file(synthetic_data_dir / "P_for_calib.shp")
    assert "value" in gdf.columns
    assert set(gdf["value"].unique()) == {1, 2}
    assert str(gdf.crs).upper() == "EPSG:2039"


def test_default_yaml_loads_with_pyyaml():
    """The shipped default config parses cleanly."""
    import yaml

    with open(REPO_ROOT / "configs" / "default.yaml") as f:
        cfg = yaml.safe_load(f)
    assert "run" in cfg
    assert "seed" in cfg["run"]
