# Nomad ABM — Iron Age IIA Settlement in the Negev Highlands

> Agent-based model of household mobility, environmental degradation, and
> palimpsest formation in the Negev Highlands during the Iron Age IIA
> (c. 980–830 BCE). Companion code to Chapter 4 of the thesis.

> ⚠️ **Status: work in progress.** This repository is being prepared for
> academic publication. APIs, file layout, and data hosting are
> evolving. See [`/root/.claude/plans/i-will-need-to-mutable-pascal.md`](#)
> (local) for the publication-readiness plan and roadmap.

## Overview

This model simulates 75 years of annual household repositioning across a
318 × 280 cell grid (250 m cells, ~3 250 km²) of the Negev Highlands. It
tests whether autochthonous nomadic processes — temporal cycling driven
by environmental volatility and degradation feedback — can plausibly
generate the spatial palimpsest documented in the Iron Age IIA
archaeological record. Households make annual decisions about camp
location, territory, livestock management, and enclosure construction
under stochastic rainfall regimes.

The model is implemented in Python on top of [Mesa 3.0](https://mesa.readthedocs.io/),
with [Optuna](https://optuna.org/) for parameter calibration and standard
geospatial / scientific libraries (rasterio, geopandas, numpy, scipy,
h5py).

For the full conceptual and mathematical description, see
[`Thesis Chapter/ch.4-ABM.md`](Thesis%20Chapter/ch.4-ABM.md). An ODD
protocol document is planned (see roadmap).

## Repository layout

```
.
├── Code/                # model source and analysis notebooks
│   ├── model_opt.py                # main model (Mesa 3.0)
│   ├── model_opt_sensitivity.py    # variant for sensitivity analysis
│   ├── model_code_26_2.ipynb       # canonical optimization run notebook
│   └── sensitivity_analysis.ipynb  # sensitivity analysis notebook
├── Data/                # HDF5/raster inputs (large; will move to Zenodo)
├── Results/             # simulation outputs (ignored by git)
├── docs/                # supplementary documentation
│   └── objective_function.md       # explanation of the calibration objective
├── Thesis Chapter/      # accompanying thesis chapter
├── environment.yml      # conda environment
├── requirements.txt     # pip-equivalent for non-conda users
├── pyproject.toml       # packaging + ruff/black/pytest config
├── .pre-commit-config.yaml
├── CITATION.cff
├── CHANGELOG.md
└── LICENSE
```

## Installation

Choose one of:

```bash
# Conda (recommended — pins geospatial libraries via conda-forge)
conda env create -f environment.yml
conda activate nomad_model

# Or pip
pip install -r requirements.txt
```

For development tools (ruff, black, pre-commit, nbstripout):

```bash
pip install -e ".[dev]"
pre-commit install
```

## How to run

The model is driven from two notebooks:

- **`Code/model_code_26_2.ipynb`** — optimization runs against
  `model_opt.py`. This is the canonical run notebook.
- **`Code/sensitivity_analysis.ipynb`** — sensitivity analysis against
  `model_opt_sensitivity.py`.

Both notebooks import the corresponding `.py` module from the same
directory:

```python
from model_opt import run_model_opt
run_model_opt(seed=42)
```

By default, input data is loaded from `./Data/` and outputs land in
`./Results/`, both relative to the repo root. To point at a different
location, set environment variables before running:

```bash
# optional — only needed if your data lives outside the repo
export NOMAD_ABM_DATA_DIR=/path/to/data
export NOMAD_ABM_RESULTS_DIR=/path/to/results
export NOMAD_ABM_CALIB_SHP=/path/to/P_for_calib.shp
```

A CLI entry point (`python -m nomad_abm run`) is planned.

> Legacy notebooks (`run_numpy.ipynb`, `model_code_26.ipynb`,
> `convert_to_numpy.ipynb`, and everything that lived under `Code/old/`)
> were removed in the Phase 4 cleanup. They are recoverable from the
> `legacy-pre-publication` tag or from any commit on `master`.

## Reproducibility

- `Code/environment.yml` pins Python 3.11 plus every dependency to a
  specific minor version.
- The model accepts a `seed` argument and seeds both `random` and
  `numpy.random` (see `Code/model_opt.py:238–240`).
- Simulation outputs land in timestamped folders under `Results/`.

## Data

Input data (HDF5 yearly/permanent rasters, GeoTIFF, .npy) live under
`Data/`. They are currently committed to the repository (~184 MB), but
will be archived on Zenodo with a DOI as part of publication
preparation. The calibration shapefile `P_for_calib.shp` referenced by
the objective function is not yet included — see the publication plan.

## Citation

Citation metadata lives in [`CITATION.cff`](CITATION.cff) — GitHub
renders a "Cite this repository" button from it. To cite by hand:

> Lubel, I. (2025). *Nomad ABM: Agent-Based Model of Iron Age IIA
> Settlement in the Negev Highlands* (version 0.1.0). Hebrew University
> of Jerusalem. https://github.com/itaylub/ABM

A Zenodo DOI will be minted with the v1.0.0 release (see roadmap).

## License

This project is released under the [MIT License](LICENSE).

## Contact

Issues and questions: please use the
[GitHub issue tracker](https://github.com/itaylub/ABM/issues).
