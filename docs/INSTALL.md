# Installation

The model is tested on **Python 3.11**. Geospatial dependencies
(`rasterio`, `geopandas`, `fiona`, `pyproj`, `shapely`) are easier to
install via **conda** than via plain `pip`, especially on Windows; the
conda path is therefore recommended.

## Path A — Conda (recommended)

```bash
conda env create -f environment.yml
conda activate nomad_model
pip install -e .
```

`pip install -e .` makes the `nomad_abm` package importable from
anywhere and registers the `nomad-abm` console script. Without it the
package is still usable through the backwards-compatibility shims in
`Code/`.

For development tools (ruff, black, pre-commit, nbstripout, pytest):

```bash
pip install -e ".[dev]"
pre-commit install
```

## Path B — Pure pip

This path works but is more brittle on Windows because of GDAL.

```bash
python3.11 -m venv .venv
source .venv/bin/activate         # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt   # exact pins
pip install -e .
```

If you see errors compiling `rasterio` or `fiona` from source on
Windows, install the matching pre-built wheels from
[Gohlke's archive](https://github.com/cgohlke/geospatial-wheels) for
your Python version first, then re-run `pip install -r requirements.txt`.

## Per-platform notes

### macOS

```bash
# Apple Silicon: use the conda-forge channel (already pinned in environment.yml)
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
# CLI is registered:
python -m nomad_abm run --help
nomad-abm run --help              # only after `pip install -e .`

# Package is importable:
python -c "import nomad_abm; print(nomad_abm.__version__)"

# Lint passes:
ruff check .
```

To actually run a simulation, the data files described in
[`DATA.md`](DATA.md) must be present (default location `./Data/`, or
point `NOMAD_ABM_DATA_DIR` elsewhere). Without data the CLI will
import successfully but fail at the first HDF5 read.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ImportError: cannot find _rasterio` on Linux | GDAL/PROJ version mismatch | Reinstall via conda: `conda install -c conda-forge rasterio=1.3.9` |
| `Could not find a version that satisfies the requirement ruff==0.6.9` | Air-gapped/no PyPI access | Skip; install `pip install -e ".[dev]"` from a machine with network and copy the env |
| `nomad_abm` not found from a notebook | Notebook is in `Code/` but the shim's `sys.path` insert hit a stale `__pycache__` | `rm -rf Code/__pycache__ src/nomad_abm/__pycache__` and re-import |
| `FileNotFoundError: yearly_data_10_25.h5` | `Data/` empty or env var pointed elsewhere | Confirm `echo $NOMAD_ABM_DATA_DIR` or copy the file into `./Data/` |
| Hardcoded `D:\itay\ABM\...` path still appears in stack trace | Old shell session, env vars stale | Restart the shell / re-source `conda activate`; see `docs/objective_function.md` |
