# Nomad ABM — Iron Age IIA Settlement in the Negev Highlands

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20473345.svg)](https://doi.org/10.5281/zenodo.20473345)

> Agent-based model of household mobility, environmental degradation, and
> palimpsest formation in the Negev Highlands during the Iron Age IIA
> (c. 980–830 BCE). Companion code to Chapter 4 of the thesis.

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
geospatial / scientific libraries (geopandas, shapely, numpy, scipy,
h5py).

For the full conceptual description of the model, see the accompanying
thesis chapter ([`thesis/ch.4-ABM.md`](thesis/ch.4-ABM.md)); the exact
parameters, units, and sources are tabulated in the technical appendix
under [`thesis/`](thesis/). A formal ODD-protocol description
(Grimm et al. 2020) is planned as part of preparing the model for
journal publication (see [Future development](#future-development)).

## Repository layout

The project is deliberately simple: two Jupyter notebooks, each paired
with the plain Python module it imports, plus the data and documentation.

```
.
├── Code/
│   ├── calibration.ipynb          # main calibration / optimization runs
│   ├── model.py                   #   ↳ the agent-based model it imports
│   ├── sensitivity_analysis.ipynb # sensitivity analysis
│   └── sensitivity_model.py       #   ↳ the model variant it imports
├── Data/                # input rasters etc. — fetched from Zenodo (not stored in git)
├── Results/             # simulation outputs (created on each run; not stored in git)
├── docs/                # supplementary documentation
│   ├── DATA.md                    # data dictionary
│   ├── INSTALL.md                 # long-form install guide
│   └── objective_function.md      # code-level walkthrough of the objective
├── scripts/
│   └── download_data.py           # fetch the input-data bundle from Zenodo
├── thesis/              # model description: ABM chapter + parameter appendix
├── environment.yml      # conda environment
├── requirements.txt     # pip-equivalent dependency list
├── CITATION.cff
├── CHANGELOG.md
└── LICENSE
```

## Installation

The model is developed and tested on **Python 3.11**. The geospatial
libraries (geopandas, shapely, fiona, pyproj) install most reliably via
**conda**, so that path is recommended.

```bash
# Conda (recommended)
conda env create -f environment.yml
conda activate nomad_model

# Or pure pip
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

There is nothing to "install" beyond the dependencies — the model is
plain `.py` files that the notebooks import directly. See
[`docs/INSTALL.md`](docs/INSTALL.md) for per-platform notes and
troubleshooting.

## How to run

The two notebooks in `Code/` are the entry points:

- **`Code/calibration.ipynb`** — the calibration / optimization runs
  (imports `model.py`).
- **`Code/sensitivity_analysis.ipynb`** — the sensitivity analysis
  (imports `sensitivity_model.py`).

Launch Jupyter from the repository root and open either notebook:

```bash
conda activate nomad_model
jupyter lab            # or: jupyter notebook
```

Because each notebook lives next to the module it imports, the imports
just work:

```python
import model                       # in calibration.ipynb
model.run_model_opt(seed=42)

import sensitivity_model           # in sensitivity_analysis.ipynb
```

### Getting the data

The input data is archived on Zenodo (DOI above), not stored in git.
Fetch it into `Data/` on a fresh clone with:

```bash
python scripts/download_data.py
```

This downloads the bundle, verifies its checksum, and extracts the
rasters, masks, and calibration shapefile into `Data/`. See
[`docs/DATA.md`](docs/DATA.md) for the full data dictionary.

### Data paths

By default the model reads inputs from `./Data/` and writes outputs to
`./Results/`, relative to the repository root. To point elsewhere, set
environment variables before launching Jupyter:

```bash
export NOMAD_ABM_DATA_DIR=/path/to/data
export NOMAD_ABM_RESULTS_DIR=/path/to/results
export NOMAD_ABM_CALIB_SHP=/path/to/P_for_calib.shp
```

## Reproducibility

- `environment.yml` and `requirements.txt` list every dependency.
- The model accepts a `seed` argument and seeds both `random` and
  `numpy.random`, so a given seed reproduces a given run.
- Simulation outputs land in timestamped folders under `Results/`.

## Data

Input data (HDF5 yearly/permanent rasters, GeoTIFF, `.npy` masks, and
the `P_for_calib.shp` calibration shapefile) are archived on
[Zenodo (10.5281/zenodo.20473345)](https://doi.org/10.5281/zenodo.20473345)
and fetched with `scripts/download_data.py`. The full schema is
documented in [`docs/DATA.md`](docs/DATA.md).

## Future development

Planned before submitting the model for journal publication:

- A formal **ODD-protocol** description (Grimm et al. 2020) of the model
  as implemented, superseding the narrative thesis chapter as the
  canonical technical reference.
- A citable **software DOI** for the code itself (via the GitHub↔Zenodo
  integration), alongside the existing input-data DOI.

## Citation

Citation metadata lives in [`CITATION.cff`](CITATION.cff) — GitHub
renders a "Cite this repository" button from it. To cite by hand:

> Lubel, I. (2026). *Nomad ABM: Agent-Based Model of Iron Age IIA
> Settlement in the Negev Highlands* (version 1.0.0). Hebrew University
> of Jerusalem. https://github.com/itaylub/ABM

The input-data archive has its own DOI
([10.5281/zenodo.20473345](https://doi.org/10.5281/zenodo.20473345)).

## License

This project is released under the [MIT License](LICENSE).

## Contact

Issues and questions: please use the
[GitHub issue tracker](https://github.com/itaylub/ABM/issues).
