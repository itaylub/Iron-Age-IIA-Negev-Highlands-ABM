"""Generate a tiny synthetic Data/ directory matching the real schema.

The real input files are 184 MB total and cannot live in the repo. CI
needs *something* to run the model code against, so this module builds
a structurally identical but much smaller fixture (a few KB) at a
caller-supplied path. The layout mirrors what the author's actual
files contain — verified by ``scripts/inspect_data.py`` and recorded
in ``docs/DATA.md``.

Usage from a test:

    from tests.fixtures import make_fixture
    make_fixture.write_fixture(data_dir, n_years=4)

The generated files satisfy the model's import-time assumptions but
the values are random noise — they do **not** reproduce any
archaeological result. Use them for smoke tests only.
"""

from __future__ import annotations

from pathlib import Path

import h5py
import numpy as np


GRID_SHAPE = (318, 280)


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def _make_suitability(shape: tuple[int, int], rng: np.random.Generator, dtype=np.float32) -> np.ndarray:
    """Generate a smooth 0-10 suitability raster."""
    base = rng.random(shape, dtype=np.float32) * 10.0
    return base.astype(dtype)


def write_yearly_h5(path: Path, n_years: int = 4, n_arrays_per_group: int = 3) -> None:
    """Write a synthetic ``yearly_data*.h5`` file.

    Structure:

        /group_<i>           # i = 0 .. n_years-1, 0-indexed
          /array_0           # float64 318x280
          /array_1           # float32 318x280
          /array_2           # float32 318x280
          ... up to /array_<n_arrays_per_group-1>
    """
    rng = _rng(seed=42)
    with h5py.File(path, "w") as f:
        for year in range(n_years):
            group = f.create_group(f"group_{year}")
            for j in range(n_arrays_per_group):
                dtype = np.float64 if j == 0 else np.float32
                group.create_dataset(f"array_{j}", data=_make_suitability(GRID_SHAPE, rng, dtype))


def write_permanent_h5(path: Path, n_arrays: int = 6) -> None:
    """Write a synthetic ``per_data*.h5`` file.

    Structure:

        /group_1             # singleton, 1-indexed
          /array_0 .. /array_<n_arrays-1>
        /metadata            # sibling group, empty (model does not read it)
    """
    rng = _rng(seed=7)
    with h5py.File(path, "w") as f:
        group = f.create_group("group_1")
        for j in range(n_arrays):
            dtype = np.float64 if j == n_arrays - 1 else np.float32
            group.create_dataset(f"array_{j}", data=_make_suitability(GRID_SHAPE, rng, dtype))
        f.create_group("metadata")


def write_mask_npy(path: Path, valid_fraction: float = 0.6, seed: int = 1) -> None:
    """Write a binary uint8 mask matching the real ``place_raster``/``ext_raster``."""
    rng = _rng(seed)
    mask = (rng.random(GRID_SHAPE) < valid_fraction).astype(np.uint8)
    np.save(path, mask)


def write_calib_shp(path: Path, n_points: int = 50) -> None:
    """Write a tiny calibration shapefile in EPSG:2039 (ITM).

    Points are drawn from the approximate bounds of the model extent.
    Half are tagged ``value=1`` (other architecture) and half
    ``value=2`` (enclosed compound), so the objective function has
    both classes to count.
    """
    import geopandas as gpd
    from shapely.geometry import Point

    rng = _rng(seed=3)
    # Approximate ITM bounds covering the Negev Highlands extent (in metres).
    xs = rng.uniform(130_000, 200_000, size=n_points)
    ys = rng.uniform(480_000, 560_000, size=n_points)
    values = np.where(rng.random(n_points) < 0.07, 2, 1).astype(np.int32)
    gdf = gpd.GeoDataFrame(
        {"value": values, "geometry": [Point(x, y) for x, y in zip(xs, ys)]},
        crs="EPSG:2039",
    )
    gdf.to_file(path, driver="ESRI Shapefile")


def write_fixture(data_dir: Path, n_years: int = 4) -> None:
    """Materialise a complete synthetic Data/ at ``data_dir``."""
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    write_yearly_h5(data_dir / "yearly_data_10_25.h5", n_years=n_years, n_arrays_per_group=3)
    write_yearly_h5(data_dir / "yearly_data.h5", n_years=n_years, n_arrays_per_group=4)
    write_permanent_h5(data_dir / "per_data_10_25.h5", n_arrays=6)
    write_permanent_h5(data_dir / "per_data.h5", n_arrays=8)
    write_mask_npy(data_dir / "place_raster.npy", valid_fraction=0.6, seed=1)
    write_mask_npy(data_dir / "ext_raster.npy", valid_fraction=0.8, seed=2)
    write_calib_shp(data_dir / "P_for_calib.shp", n_points=50)
