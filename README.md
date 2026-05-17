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
├── Code/                # model source (model_opt.py) and analysis notebooks
│   ├── model_opt.py
│   ├── model_opt_sensitivity.py
│   ├── environment.yml
│   └── *.ipynb
├── Data/                # HDF5/raster inputs (large; will move to Zenodo)
├── Results/             # simulation outputs (ignored by git)
├── Thesis Chapter/      # accompanying thesis chapter
└── LICENSE
```

## Installation (current state)

```bash
conda env create -f Code/environment.yml
conda activate nomad_model
```

## How to run

The model is currently driven from notebooks. Open
`Code/run_numpy.ipynb` for a working example, or import the module:

```python
from Code.model_opt import run_model_opt
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
