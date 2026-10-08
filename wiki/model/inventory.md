---
type: model
created: 2026-10-08
code_commit: 2249331932b0a42ec47c33bca0ac94f4b8728813
---

# Inventory

What is in the repository at commit `2249331` (2026-10-05), read on 2026-10-08. The repository is under git: <https://github.com/itaylub/Iron-Age-IIA-Negev-Highlands-ABM>. Nothing was run.

## Languages and environment
- Python. `environment.yml` (conda env `nomad_model`, `python>=3.11`) and `requirements.txt` both state "Verified working on Python 3.14 with numpy 2.3, mesa 3.3, geopandas 1.1". Pins are open-ended `>=`, with `mesa>=3.0,<4.0`.
- Libraries the model imports: mesa, numpy, scipy (`convolve2d`, `distance_transform_edt`, `linalg`), h5py, pandas, geopandas, shapely, matplotlib, seaborn, optuna, `multiprocessing.shared_memory` (`model.py`, L19–40).
- `model.py` forces single-threaded BLAS through environment variables before importing numpy (L11–17).

## Entry points (notebooks)
| File | What it does | Imports |
|---|---|---|
| [`Code/calibration.ipynb`](../../Code/calibration.ipynb) | Optuna study `opt_2_26_v1` (TPE sampler, MedianPruner), analysis plots, 30-replicate best-trial run, summary CSVs. 9 cells, no stored outputs. | `model` |
| [`Code/sensitivity_analysis.ipynb`](../../Code/sensitivity_analysis.ipynb) | Time horizon (150 y), number of agents (5/15/20), fixed vs flexible territory, null-weight baseline, CSV export. 12 cells, no stored outputs. | `sensitivity_model` |
| [`Code/test.ipynb`](../../Code/test.ipynb) | 2-year smoke run with random Dirichlet weights; substitutes mock zero rasters if the yearly HDF5 is missing. 2 cells. Added in the latest commit ("add small and fast test notebook"). | `model` |

Details per experiment: [experiments](experiments.md).

## Model files
| File | Lines | Role |
|---|---|---|
| [`Code/model.py`](../../Code/model.py) | 1,391 | The calibrated model: data loaders, helpers, `Household_Agent`, `NomadModel`, plotting, `to_gdf`, `obj_func`, `run_model_opt`, `objective_function`, Optuna `objective`. |
| [`Code/sensitivity_model.py`](../../Code/sensitivity_model.py) | 1,175 | A diverging copy of `model.py` with `num_agents` and `fixed_territory` switches. No `objective_function` or `objective`. |

### How the two model files differ
Apart from comments and docstrings, `diff` shows these behavioural differences (line numbers for `model.py` first, `sensitivity_model.py` second):
1. **Territory overlap test** (`overlap_territory`). `model.py` counts *households* whose territory touches the candidate neighbourhood and divides by the number of *cells* (L319–330). `sensitivity_model.py` computes the share of cells shared with each territory in `model.territories` (L264–272). See [camp and territory placement](../mechanisms/camp-and-territory-placement.md).
2. **Rainfall-year index.** `sensitivity_model.py` wraps with `year % len(indices)` (L398–400, L945); `model.py` does not (L486, L1029).
3. **Year-0 territory.** Radius 25 fixed in `model.py` (L993, L1002), 20/25/30 by suitability in `sensitivity_model.py` (L895–918).
4. **Failure handling.** `model.py` calls `self.remove()` (L592). `sensitivity_model.py` removes the agent from the grid, from `model.agents` and from `model.territories` (L498–501), or in fixed-territory mode resets it in place (L491–496).
5. **Fixed-territory mode** (`sensitivity_model.py` only): `year_initiation` keeps the camp cell and territory (L528–539), and `move_year` skips `reset_pos` (L936–937).
6. **Replacement agents.** `sensitivity_model.py` places a new agent at the grid centre and runs `year_initiation` immediately (L979–989); `model.py` leaves that to the next `shuffle_do` (L1049–1058).
7. **`create_agents`.** `sensitivity_model.py` defines its own static `create_agents` (see diff); `model.py` relies on Mesa's `Agent.create_agents`.

## Documentation
| File | Content | Status |
|---|---|---|
| [`README.md`](../../README.md) | Overview, layout, install, data, citation. | Current; outputs described as "timestamped folders", see Things to check. |
| [`thesis/chapter-5-ABM.docx`](../../thesis/chapter-5-ABM.docx) | Ch. 5, the narrative model description (§5.1–5.7). The owner's documentation (AGENTS.md › Local conventions). | Read in full. |
| [`thesis/appendix-5-ABM.docx`](../../thesis/appendix-5-ABM.docx) | App. 5, the technical specification: Table A5.1 (environmental layers), §A5.2 degradation equations, §A5.3 calibration, Table A5.4 (all parameters), A5.5–A5.6 (state variables), A5.7 (sensitivity results). | Read in full; embedded figures not read. |
| [`thesis/chapter-5-tables-and-figures.docx`](../../thesis/chapter-5-tables-and-figures.docx) | Table 5.1 (layer classification) and 12 figure images without captions in the export. | Table read; figures not read. |
| [`docs/DATA.md`](../../docs/DATA.md) | Data dictionary, HDF5 layout, checksums. | Read. |
| [`docs/objective_function.md`](../../docs/objective_function.md) | Code-level walkthrough of the objective. | Read; describes a different formula from `obj_func`, see Things to check. |
| [`docs/INSTALL.md`](../../docs/INSTALL.md), [`docs/ZENODO_UPLOAD.md`](../../docs/ZENODO_UPLOAD.md) | Install guide; one-time Zenodo upload walkthrough. | Listed only. |
| [`CHANGELOG.md`](../../CHANGELOG.md), [`CITATION.cff`](../../CITATION.cff) | History (v1.0.0 2026-05-31, then the [Unreleased] reshaping); citation metadata. | Read. |
| Docstrings in `model.py` | Few. The module docstring still names `nomad_abm.model` and a `Code/model_opt.py` shim. | Stale, see Things to check. |

## Input data (not in git; Zenodo 10.5281/zenodo.20473345)
Per docs/DATA.md:
- `yearly_data_10_25.h5`: `group_0`…`group_75` (76 years), each with `array_0` (float64) and `array_1`, `array_2` (float32), 318 × 280. Lazy-loaded by `LazyYearlyData` (L62–120).
- `per_data_10_25.h5`: single `group_1` with six arrays. `model.py` unpacks them as agri, kb, pw, veg_fit, rain, slope (L481–482).
- `ext_raster.npy`, `place_raster.npy`: `uint8` 0/1 masks.
- `P_for_calib.shp`: EPSG:2039 points, `value` 1 (other site) or 2 (enclosed compound).
- Paths default to `<repo>/Data`, overridable with `NOMAD_ABM_DATA_DIR`, `NOMAD_ABM_RESULTS_DIR`, `NOMAD_ABM_CALIB_SHP` (L49–59).

## Outputs (not in git)
- Per run: `household_data.csv` (Mesa DataCollector agent reporters: Manpower, flocks, surplus, "proseprity index", position, enclosures; L1005–1011, L1276–1277), weight JSONs, optional `year_<n>_map.png` (`viz_map`) and `spatial_similarity.png` (`obj_func`).
- The notebooks write to hard-coded `D:\itay\ABM\Results\…` paths, including the Optuna SQLite store `opt_run.db`. None of the results are in the repository. See [experiments](experiments.md).

## Scripts (data handling, not the model)
- [`scripts/download_data.py`](../../scripts/download_data.py): fetch and checksum the Zenodo bundle into `Data/`.
- [`scripts/build_data_bundle.py`](../../scripts/build_data_bundle.py): build the bundle zip on the data machine.
- [`scripts/inspect_data.py`](../../scripts/inspect_data.py): read-only JSON inventory of `Data/`.

## Utility code (one line each)
- `LazyYearlyData`, `load_permanent_data`, `SharedDataManager`, `GlobalData`, `ensure_data_loaded` (L62–228): data loading and shared memory for parallel workers; falls back to `np.ones`/zeros if files are missing.
- `viz_map` (L1065–1128): yearly maps. `to_numpy_y` (L250–252): Mesa-to-array row flip.

## Things to check
- `docs/objective_function.md` describes `ratio_enc = t1_ratio / t_ratio`, an `overlap_func` built from the symmetric difference, and `total = ((1 - overlap_func) + ratio_enc) / 2` with "higher is better". `obj_func` computes `1 - IoU`, `|t_ratio - t1_ratio|` and their mean, which is minimised (L1217–1233). The doc's pointers ("§5.6.3 of the thesis", "§A5.3 of the appendix") do not match the current numbering (§5.5.2; §A5.3 has no objective). Should the doc be rewritten from Ch. 5 §5.5.2?
- docs/DATA.md gives the grid as "318 columns × 280 rows". The code treats arrays as (318, 280) = rows × columns and builds a grid 280 wide and 318 high (L957–958).
- docs/DATA.md says the `metadata` group is "not consumed by the model". `LazyYearlyData` reads `f['metadata'].attrs['num_groups']` from the yearly file (L76), and `load_permanent_data` reads `num_groups` and `arrays_per_group` from the permanent file (L129–131). The DATA.md layout for the yearly file shows no `metadata` group.
- Stale names. The `model.py` docstring (L1–7) refers to `nomad_abm.model` and a `Code/model_opt.py` shim, and `sensitivity_model.py` to `Code/model_opt_sensitivity.py`. calibration.ipynb cell 0 says it uses "the standalone `model_opt.py` module". These files no longer exist (CHANGELOG [Unreleased]).
- README › Reproducibility says outputs "land in timestamped folders under `Results/`". `run_model_opt` writes `Results/run/trial_<n>/iter_<i>` (L1247, L1297), and the notebooks write to `D:\itay\ABM\Results`.
- The two model files are diverging copies (see "How the two model files differ"). Calibration used `model.py` and the sensitivity tests used `sensitivity_model.py`.
- App. 5 numbers its equations "eq 4.1", "eq 4.2" and "eq 4.3 + 2", while its text refers to eq A5.1–A5.3 (App. 5 §A5.2).
- The Chapter 5 .docx ends with a stray "C" after §5.7.
- Figures in `thesis/chapter-5-tables-and-figures.docx` and App. 5 were not read (images, no captions in the text export). Ch. 5 cites Figures 5.2–5.7 for the behaviours, the year cycle and the run (§5.2.2–5.4), so they may hold schedule detail worth checking against the code.
