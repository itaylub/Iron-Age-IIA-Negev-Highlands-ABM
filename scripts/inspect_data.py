"""Inventory and sanity-check the local Data/ directory.

Read-only. Walks Data/ and emits a JSON report (sizes, SHA-256, HDF5
layouts, raster CRS, shapefile counts) to stdout AND to a file next
to Data/.

Locating Data/ — tries, in order:
  1. NOMAD_ABM_DATA_DIR  environment variable
  2. ./Data               (cwd)
  3. <repo-root>/Data     where repo root is two levels up from this file
  4. D:/itay/ABM/Data     the documented user data location
  5. /home/user/ABM/Data  the documented cloud-container path

Usage (Windows, after `conda activate nomad_model`):

    cd /d D:\\itay\\ABM
    python scripts\\inspect_data.py

The script can live anywhere — drop it in the repo root or in
``scripts/`` and run it from any working directory.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path


def _script_path() -> Path | None:
    """Resolve this file's path, or None when running in a REPL/notebook
    cell where ``__file__`` is undefined."""
    try:
        return Path(__file__).resolve()
    except NameError:
        return None


def find_data_dir() -> Path:
    env = os.environ.get("NOMAD_ABM_DATA_DIR")
    candidates: list[Path] = []
    if env:
        candidates.append(Path(env))
    candidates.append(Path.cwd() / "Data")
    here = _script_path()
    if here is not None:
        for ancestor in (here.parent, here.parent.parent, here.parent.parent.parent):
            candidates.append(ancestor / "Data")
    candidates.append(Path("D:/itay/ABM/Data"))
    candidates.append(Path("/home/user/ABM/Data"))
    seen: set[Path] = set()
    for c in candidates:
        try:
            c = c.resolve()
        except OSError:
            continue
        if c in seen:
            continue
        seen.add(c)
        if c.is_dir():
            return c
    raise SystemExit(
        "ERROR: could not find Data/. Tried:\n  " + "\n  ".join(str(c) for c in seen)
    )


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def inspect_h5(path: Path) -> dict:
    import h5py
    import numpy as np

    info: dict = {"size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
    with h5py.File(path, "r") as f:
        info["root_attrs"] = {k: str(v) for k, v in f.attrs.items()}
        top = sorted(f.keys())
        info["n_top_keys"] = len(top)
        info["top_keys_sample"] = top[: min(5, len(top))]
        first = f[top[0]]
        if isinstance(first, h5py.Group):
            info["layout"] = "groups"
            info["group_attrs_sample"] = {k: str(v) for k, v in first.attrs.items()}
            datasets: dict = {}
            for sk in sorted(first.keys()):
                d = first[sk]
                arr = np.asarray(d[:])
                datasets[sk] = {
                    "shape": list(d.shape),
                    "dtype": str(d.dtype),
                    "min": float(arr.min()),
                    "max": float(arr.max()),
                    "mean": float(arr.mean()),
                }
            info["first_group_datasets"] = datasets
            sample = [tuple(sorted(f[k].keys())) for k in top[: min(5, len(top))]]
            info["sample_structurally_uniform"] = len(set(sample)) == 1
        else:
            info["layout"] = "flat"
            datasets = {}
            for k in top:
                d = f[k]
                arr = np.asarray(d[:])
                datasets[k] = {
                    "shape": list(d.shape),
                    "dtype": str(d.dtype),
                    "min": float(arr.min()),
                    "max": float(arr.max()),
                    "mean": float(arr.mean()),
                }
            info["datasets"] = datasets
    return info


def inspect_npy(path: Path) -> dict:
    import numpy as np

    a = np.load(path)
    return {
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "shape": list(a.shape),
        "dtype": str(a.dtype),
        "min": float(a.min()),
        "max": float(a.max()),
        "n_unique": int(np.unique(a).size),
    }


def inspect_tif(path: Path) -> dict:
    info: dict = {"size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
    try:
        import rasterio

        with rasterio.open(path) as r:
            info["shape"] = list(r.shape)
            info["dtype"] = str(r.dtypes[0])
            info["crs"] = str(r.crs) if r.crs else None
            info["crs_wkt"] = r.crs.to_wkt() if r.crs else None
            info["res"] = list(r.res)
            info["bounds"] = list(r.bounds)
            info["nodata"] = r.nodata
    except Exception as e:
        info["error"] = f"{type(e).__name__}: {e}"
    return info


def inspect_shp(path: Path) -> dict:
    info: dict = {"size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
    try:
        import geopandas as gpd

        gdf = gpd.read_file(path)
        info["n_features"] = int(len(gdf))
        info["columns"] = list(gdf.columns)
        info["geom_types"] = sorted(map(str, gdf.geom_type.unique()))
        info["crs"] = str(gdf.crs) if gdf.crs is not None else None
        info["crs_wkt"] = gdf.crs.to_wkt() if gdf.crs is not None else None
        info["bounds"] = [float(b) for b in gdf.total_bounds]
        if "value" in gdf.columns:
            info["value_counts"] = {
                str(k): int(v) for k, v in gdf["value"].value_counts().items()
            }
    except Exception as e:
        info["error"] = f"{type(e).__name__}: {e}"
    return info


def library_versions() -> dict:
    versions: dict = {"python": sys.version.split()[0]}
    for mod in ("numpy", "h5py", "geopandas", "rasterio", "mesa", "optuna", "pandas", "scipy"):
        try:
            versions[mod] = __import__(mod).__version__
        except Exception as e:
            versions[mod] = f"MISSING: {type(e).__name__}"
    return versions


def find_calib_shp() -> list[str]:
    """Locate ``P_for_calib.shp`` anywhere the user might keep it."""
    seen: set[Path] = set()
    candidates: list[Path] = []
    roots: list[Path] = [Path.cwd()]
    here = _script_path()
    if here is not None:
        roots.extend([here.parent, here.parent.parent])
    for extra in ("D:/itay", "D:/itay/ABM", "D:/itay/ABM/points_all", "/home/user/ABM"):
        p = Path(extra)
        if p.exists():
            roots.append(p)
    for root in roots:
        if not root.exists():
            continue
        for pat in ("P_for_calib.shp", "*calib*.shp"):
            for hit in root.rglob(pat):
                if hit not in seen:
                    seen.add(hit)
                    candidates.append(hit)
    return [str(p) for p in candidates]


def main() -> int:
    data = find_data_dir()
    report_path = data.parent / "inspect_data.report.json"

    report: dict = {
        "library_versions": library_versions(),
        "data_dir": str(data),
        "files": {},
    }

    for path in sorted(data.iterdir()):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        try:
            if suffix == ".h5":
                report["files"][path.name] = inspect_h5(path)
            elif suffix == ".npy":
                report["files"][path.name] = inspect_npy(path)
            elif suffix == ".tif":
                report["files"][path.name] = inspect_tif(path)
            elif suffix == ".shp":
                report["files"][path.name] = inspect_shp(path)
            else:
                report["files"][path.name] = {
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
        except Exception as e:
            report["files"][path.name] = {"error": f"{type(e).__name__}: {e}"}

    report["calib_shp_search"] = find_calib_shp()

    report_path.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    print(f"\n# report also written to: {report_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
