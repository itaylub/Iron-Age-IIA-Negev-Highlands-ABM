# Nomad ABM — Iron Age IIA Settlement in the Negev Highlands

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20473345.svg)](https://doi.org/10.5281/zenodo.20473345)

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
[`docs/ODD.md`](docs/ODD.md) (the canonical technical reference) and
the accompanying thesis material under [`thesis/`](thesis/). Detailed
parameter tables and equations live in Appendix 4 of the thesis
(see Drive — kept outside the repo for now).

## Repository layout

```
.
├── src/nomad_abm/       # the canonical Python package
│   ├── model.py                    # main model (Mesa 3.0)
│   ├── sensitivity.py              # variant for sensitivity analysis
│   ├── cli.py                      # `python -m nomad_abm run ...`
│   └── __init__.py / __main__.py
├── Code/                # analysis notebooks + thin backwards-compat shims
│   ├── model_code_26_2.ipynb       # canonical optimization run notebook
│   ├── sensitivity_analysis.ipynb  # sensitivity analysis notebook
│   ├── model_opt.py                # shim → nomad_abm.model
│   └── model_opt_sensitivity.py    # shim → nomad_abm.sensitivity
├── configs/             # YAML run configurations
│   └── default.yaml
├── Data/                # HDF5/raster inputs (large; will move to Zenodo)
├── Results/             # simulation outputs (ignored by git)
├── docs/                # supplementary documentation
│   ├── ODD.md                      # canonical model description (Grimm et al. 2020)
│   ├── DATA.md                     # data dictionary
│   ├── INSTALL.md                  # long-form install guide
│   └── objective_function.md       # code-level walkthrough of the objective
├── thesis/              # accompanying thesis chapter + appendices
├── legacy/              # frozen pre-Phase-6 snapshot of Code/ for revert
├── environment.yml      # conda environment
├── requirements.txt     # pip-equivalent for non-conda users
├── pyproject.toml       # packaging + ruff/black/pytest config
├── .pre-commit-config.yaml
├── CITATION.cff
├── CHANGELOG.md
└── LICENSE
```

## Installation

```bash
# Conda (recommended — pins geospatial libraries via conda-forge)
conda env create -f environment.yml
conda activate nomad_model
pip install -e .

# Or pure pip
pip install -e .            # installs runtime deps from pyproject.toml
# (or, for exact pins) pip install -r requirements.txt
```

For development tools (ruff, black, pre-commit, nbstripout):

```bash
pip install -e ".[dev]"
pre-commit install
```

## How to run

### From the command line

After `pip install -e .` (or with the conda environment active):

```bash
python -m nomad_abm run --config configs/default.yaml --seed 42
```

The YAML config sets path overrides; `--seed` is optional and overrides
the config value.

### From a notebook

The two canonical notebooks live in `Code/`:

- **`Code/model_code_26_2.ipynb`** — optimization runs (uses
  `nomad_abm.model`).
- **`Code/sensitivity_analysis.ipynb`** — sensitivity analysis (uses
  `nomad_abm.sensitivity`).

Either of these import patterns works:

```python
# new layout (preferred)
from nomad_abm.model import run_model_opt

# old layout — still works via a thin shim in Code/model_opt.py
from model_opt import run_model_opt

run_model_opt(seed=42)
```

### Data paths

By default, input data is loaded from `./Data/` and outputs land in
`./Results/`, both relative to the repo root. To point at a different
location, edit `configs/default.yaml` or export environment variables:

```bash
export NOMAD_ABM_DATA_DIR=/path/to/data
export NOMAD_ABM_RESULTS_DIR=/path/to/results
export NOMAD_ABM_CALIB_SHP=/path/to/P_for_calib.shp
```

The YAML config is applied first, then env vars override it (env vars
win because the model reads them at import time).

> The pre-Phase-6 source layout is preserved in two places: the
> `legacy/` directory (browsable, easy to copy back) and the
> `legacy-pre-publication` git tag (recoverable via
> `git checkout legacy-pre-publication -- <path>`).

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
