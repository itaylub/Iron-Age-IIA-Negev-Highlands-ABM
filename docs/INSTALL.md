# Installation

The model is tested on **Python 3.11**. Geospatial dependencies
(`geopandas`, `fiona`, `pyproj`, `shapely`) are easier to install via
**conda** than via plain `pip`, especially on Windows; the conda path is
therefore recommended.

There is no package to build or install: the model is plain `.py` files
in `Code/` that the notebooks import directly. "Installing" just means
creating a Python environment with the dependencies.

## Path A — Conda (recommended)

```bash
conda env create -f environment.yml
conda activate nomad_model
```

## Path B — Pure pip

This path works but is more brittle on Windows because of GDAL.

```bash
python3.11 -m venv .venv
source .venv/bin/activate         # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If you see errors compiling `fiona` or `pyproj` from source on Windows,
install the matching pre-built wheels from
[Gohlke's archive](https://github.com/cgohlke/geospatial-wheels) for
your Python version first, then re-run `pip install -r requirements.txt`.

## Per-platform notes

### macOS

```bash
# Apple Silicon: use the conda-forge channel (already set in environment.yml)
xcode-select --install            # Command Line Tools
conda env create -f environment.yml
```

### Linux

No platform-specific notes. The conda path or pip path both work
cleanly on glibc-based distros.

### Windows

Use Anaconda or Miniconda. The conda path bypasses GDAL build issues.
If conda is not an option, see the Gohlke-wheels footnote above.

## Verifying the install

```bash
# The scientific stack imports cleanly:
python -c "import numpy, scipy, pandas, geopandas, mesa, optuna, h5py; print('ok')"
```

Then launch Jupyter from the repository root and open a notebook:

```bash
jupyter lab            # or: jupyter notebook
```

To actually run a simulation, the data files described in
[`DATA.md`](DATA.md) must be present. Fetch them with:

```bash
python scripts/download_data.py
```

They land in `./Data/` by default (or wherever `NOMAD_ABM_DATA_DIR`
points). Without data the notebooks import fine but fail at the first
HDF5 read.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ImportError` for `fiona`/`pyproj`/GDAL on Linux | GDAL/PROJ version mismatch | Reinstall via conda-forge: `conda install -c conda-forge geopandas` |
| `ModuleNotFoundError: No module named 'model'` in a notebook | Jupyter was launched from the wrong folder | Launch Jupyter from `Code/` (or from the repo root and open the notebook there) so the notebook sits next to `model.py` |
| `FileNotFoundError: yearly_data_10_25.h5` | `Data/` empty or env var pointed elsewhere | Run `python scripts/download_data.py`, or check `echo $NOMAD_ABM_DATA_DIR` |
| `FileNotFoundError: P_for_calib.shp` | calibration shapefile not extracted | Re-run `download_data.py`, or set `NOMAD_ABM_CALIB_SHP` to its path |
