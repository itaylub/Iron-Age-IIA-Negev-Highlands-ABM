"""Inventory and sanity-check the local Data/ directory.

Read-only. Writes a JSON report describing every file under ``Data/``:
size, SHA-256, and, for the geospatial files, the internal schema
(HDF5 layout, raster CRS, shapefile feature counts). The report is
both printed to stdout and saved to ``scripts/inspect_data.report.json``
(git-ignored).

Run from the repository root in the ``nomad_model`` conda env::

    conda activate nomad_model
    python scripts/inspect_data.py

The stdout is what drives the Phase 7 test-fixture generator and the
Phase 9 Zenodo manifest, so paste it into the publication-readiness
conversation when done.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parent.parent
DATA = REPO / "Data"
REPORT_PATH = HERE.parent / "inspect_data.report.json"


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
            sample_structures = [tuple(sorted(f[k].keys())) for k in top[: min(5, len(top))]]
            info["sample_structurally_uniform"] = len(set(sample_structures)) == 1
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
    """Locate ``P_for_calib.shp`` anywhere the user might keep it.

    The model references ``Data/P_for_calib.shp`` but it is not in the
    repo's ``Data/`` snapshot. This widens the search so the user does
    not have to hunt manually.
    """
    seen: set[Path] = set()
    candidates: list[Path] = []
    roots = [REPO, DATA, REPO.parent]
    # On Windows the user mentioned D:\itay\ABM — also probe its likely siblings.
    for extra in ("D:/itay", "D:/itay/ABM", "D:/itay/ABM/points_all"):
        p = Path(extra)
        if p.exists():
            roots.append(p)
    patterns = ("P_for_calib.shp", "*calib*.shp")
    for root in roots:
        if not root.exists():
            continue
        for pat in patterns:
            for hit in root.rglob(pat):
                if hit not in seen:
                    seen.add(hit)
                    candidates.append(hit)
    return [str(p) for p in candidates]


def main() -> int:
    if not DATA.exists():
        print(
            f"ERROR: {DATA} does not exist. Run from the repo root with Data/ present.",
            file=sys.stderr,
        )
        return 1

    report: dict = {
        "library_versions": library_versions(),
        "data_dir": str(DATA),
        "files": {},
    }

    for path in sorted(DATA.iterdir()):
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

    REPORT_PATH.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    print(f"\n# report written to: {REPORT_PATH}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
