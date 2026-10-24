"""Shared helpers for running the model in several processes at once.

Used by ``scripts/timing_test.py`` and ``scripts/calibrate.py``. Nothing
here changes the model: it loads the input data into shared memory the
same way ``Code/calibration.ipynb`` does, and sets up the Optuna study.

Import ``model`` only through ``import_model()``, after the results
folder has been set, because ``model.RESULTS_DIR`` is read at import.
"""

import faulthandler
import os
import sys

# If a compiled library (GDAL, PROJ, HDF5) crashes Python, print where.
faulthandler.enable()

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE_DIR = os.path.join(REPO_ROOT, "Code")

# Best trial of the thesis calibration (study opt_2_26_v1, trial 173),
# integer weights 0-7, in the order the model expects them.
THESIS_BEST = {
    "dist_to_kb": 7,
    "p_water": 1,
    "Mean_rain": 3,
    "slope_suitability": 0,
    "return_to_site": 7,
    "humen_stress": 5,
    "Yearly_rain": 0,
}
PERMANENT_KEYS = ["dist_to_kb", "p_water", "Mean_rain", "slope_suitability"]
YEARLY_KEYS = ["return_to_site", "humen_stress", "Yearly_rain"]


def set_environment(results_dir):
    """Point the model at a results folder; let processes share the HDF5 files.

    Must run before ``import_model()``. Child processes inherit these
    variables.
    """
    os.makedirs(results_dir, exist_ok=True)
    os.environ["NOMAD_ABM_RESULTS_DIR"] = results_dir
    # The input files are only read. Without this, HDF5 file locking can
    # refuse a second process opening the same file.
    os.environ.setdefault("HDF5_USE_FILE_LOCKING", "FALSE")
    # The model runs numpy single-threaded anyway (model.py). With Intel
    # MKL, the sequential layer also avoids loading the OpenMP/TBB
    # threading DLLs, whose mismatch crashed np.cov on the PC
    # (Windows code 0xc06d007f). Must be set before numpy is imported.
    os.environ.setdefault("MKL_THREADING_LAYER", "SEQUENTIAL")
    # Draw figures to files only; no window system in worker processes.
    os.environ.setdefault("MPLBACKEND", "Agg")
    # GDAL and PROJ data folders. A pixi or conda shell sets these when it
    # activates; starting python.exe directly does not. Look for them in
    # the environment Python runs from.
    _set_data_dir("GDAL_DATA", ["Library/share/gdal", "share/gdal"], "header.dxf")
    _set_data_dir("PROJ_DATA", ["Library/share/proj", "share/proj"], "proj.db")
    if os.environ.get("PROJ_DATA"):
        os.environ.setdefault("PROJ_LIB", os.environ["PROJ_DATA"])


def _set_data_dir(var, candidates, marker):
    if os.environ.get(var):
        return
    for rel in candidates:
        path = os.path.join(sys.prefix, *rel.split("/"))
        if os.path.exists(os.path.join(path, marker)):
            os.environ[var] = path
            return


def set_calib_shp(path):
    """Use this file of observed sites as the calibration target.

    Must run before ``import_model()``: the model reads
    NOMAD_ABM_CALIB_SHP at import. Child processes inherit it.
    """
    if path:
        os.environ["NOMAD_ABM_CALIB_SHP"] = os.path.abspath(path)


def describe_calib(model):
    """Path, counts and CRS of the calibration sites the model will use.

    Stops with a message if the file is missing or its ``value`` field
    holds anything other than 1 (other site) and 2 (enclosed compound).
    """
    import geopandas as gpd

    path = model.CALIB_SHP_PATH
    if not os.path.exists(path):
        raise SystemExit(f"Calibration sites not found: {path}")
    gdf = gpd.read_file(path)
    if "value" not in gdf.columns:
        raise SystemExit(f"{path} has no 'value' field (1 = other site, 2 = enclosed compound).")
    bad = sorted(set(gdf["value"].dropna().astype(int)) - {1, 2})
    if bad or gdf["value"].isna().any():
        raise SystemExit(f"{path}: 'value' must be 1 or 2 for every site; found {bad or 'empty values'}.")
    enc = int((gdf["value"] == 2).sum())
    oth = int((gdf["value"] == 1).sum())
    epsg = gdf.crs.to_epsg() if gdf.crs is not None else None
    return {"path": os.path.abspath(path), "sites": len(gdf), "enclosed": enc, "other": oth,
            "enclosed_share_pct": round(100 * enc / len(gdf), 2) if len(gdf) else None,
            "crs_epsg": epsg}


def calib_line(c):
    if c["crs_epsg"] == 2039:
        warn = ""
    elif c["crs_epsg"] is None:
        warn = "\n  Note: could not confirm the CRS as EPSG:2039 (Israel TM Grid); check the .prj"
    else:
        warn = f"\n  WARNING: CRS is EPSG:{c['crs_epsg']}; the model uses EPSG:2039 (Israel TM Grid)"
    return (f"Calibration sites: {c['path']}\n"
            f"  {c['sites']} sites, {c['enclosed']} enclosed, {c['other']} other "
            f"({c['enclosed_share_pct']}% enclosed){warn}")


def import_model():
    if CODE_DIR not in sys.path:
        sys.path.insert(0, CODE_DIR)
    import model  # noqa: E402  (Code/model.py)
    return model


def create_shared_data(model):
    """Load the static rasters into shared memory, as calibration.ipynb does.

    Returns the handles; keep them alive while workers run, then pass
    them to ``release_shared_data``.
    """
    import h5py
    import numpy as np

    ext_raster = np.load(model.EXT_RASTER_PATH)[0:318, 0:280].astype(np.float64)
    place_raster = np.load(model.PLACE_RASTER_PATH)[0:318, 0:280].astype(np.float64)

    perm_results = []
    if os.path.exists(model.PERMANENT_DATA_PATH):
        with h5py.File(model.PERMANENT_DATA_PATH, "r") as f:
            metadata = f["metadata"]
            num_groups = metadata.attrs["num_groups"]
            arrays_per_group = metadata.attrs["arrays_per_group"]
            group = f[f"group_{num_groups}"]
            perm_results = [
                np.array(group[f"array_{j}"]).astype(np.float64)
                for j in range(arrays_per_group)
            ]

    handles = [
        model.SharedDataManager.create_shared_block("ext_raster", ext_raster),
        model.SharedDataManager.create_shared_block("place_raster", place_raster),
    ]
    for i, arr in enumerate(perm_results):
        handles.append(model.SharedDataManager.create_shared_block(f"perm_res_{i}", arr))
    return handles


def release_shared_data(handles):
    for shm in handles:
        try:
            shm.close()
            shm.unlink()
        except Exception:
            pass


def init_worker():
    """Run once in each worker process: connect to the shared data."""
    model = import_model()
    model.ensure_data_loaded()


def normalised_weights(int_weights):
    """Integer weights -> (permanent dict, yearly dict, array for the model)."""
    import numpy as np

    total = sum(int_weights.values())
    norm = {k: v / total for k, v in int_weights.items()}
    perm = {k: norm[k] for k in PERMANENT_KEYS}
    yearly = {k: norm[k] for k in YEARLY_KEYS}
    w = np.array([norm[k] for k in PERMANENT_KEYS + YEARLY_KEYS], dtype=float)
    return perm, yearly, w


def make_storage(path):
    """Optuna journal storage in one file, safe for many processes on Windows.

    Uses the open-file lock rather than the default symlink lock, which
    needs extra permissions on Windows.
    """
    import optuna

    try:  # Optuna 4.x
        from optuna.storages.journal import JournalFileBackend, JournalFileOpenLock

        backend = JournalFileBackend(path, lock_obj=JournalFileOpenLock(path))
    except ImportError:  # Optuna 3.x
        from optuna.storages import JournalFileOpenLock, JournalFileStorage

        backend = JournalFileStorage(path, lock_obj=JournalFileOpenLock(path))
    return optuna.storages.JournalStorage(backend)


def git_commit():
    import subprocess

    try:
        out = subprocess.run(
            ["git", "-C", REPO_ROOT, "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except Exception:
        return "unknown"


def machine_info():
    import platform

    info = {
        "machine": platform.node(),
        "processor": platform.processor(),
        "logical_cpus": os.cpu_count(),
        "python": platform.python_version(),
    }
    for pkg in ("numpy", "mesa", "optuna", "geopandas", "h5py"):
        try:
            mod = __import__(pkg)
            info[pkg] = getattr(mod, "__version__", "unknown")
        except Exception:
            info[pkg] = "not installed"
    return info
