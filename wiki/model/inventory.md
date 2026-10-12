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
| [`Code/sensitivity_model.py`](../../Code/sensitivity_model.py) | 1,175 | A diverging copy of `model.py` with `num_agents` and `fixed_territory` switches. No `objective_function` or `objective`. Itay (2026-10-12): `model.py` is the original, this file a specific version for the sensitivity analysis. |

### How the two model files differ
Apart from comments and docstrings, `diff` shows these behavioural differences (line numbers for `model.py` first, `sensitivity_model.py` second):
1. **Territory overlap test** (`overlap_territory`). `model.py` counts *households* whose territory touches the candidate neighbourhood and divides by the number of *cells* (L319–330). `sensitivity_model.py` computes the share of cells shared with each territory in `model.territories` (L264–272). See [camp and territory placement](../mechanisms/camp-and-territory-placement.md).
2. **Rainfall-year index.** `sensitivity_model.py` wraps with `year % len(indices)` (L398–400, L945); `model.py` does not (L486, L1029).
3. **Year-0 territory.** Radius 25 fixed in `model.py` (L993, L1002), 20/25/30 by suitability in `sensitivity_model.py` (L895–918). `model.py`'s rule is the intended one; the sensitivity file's is a mistake (Itay, 2026-10-12).
4. **Failure handling.** `model.py` calls `self.remove()` (L592). `sensitivity_model.py` removes the agent from the grid, from `model.agents` and from `model.territories` (L498–501), or in fixed-territory mode resets it in place (L491–496).
5. **Fixed-territory mode** (`sensitivity_model.py` only): `year_initiation` keeps the camp cell and territory (L528–539), and `move_year` skips `reset_pos` (L936–937).
6. **Replacement agents.** `sensitivity_model.py` places a new agent at the grid centre and runs `year_initiation` immediately (L979–989); `model.py` leaves that to the next `shuffle_do` (L1049–1058).
7. **`create_agents`.** `sensitivity_model.py` defines its own static `create_agents` (see diff); `model.py` relies on Mesa's `Agent.create_agents`.

## Documentation
| File | Content | Status |
|---|---|---|
| [`README.md`](../../README.md) | Overview, layout, install, data, citation. | Current; outputs described as "timestamped folders", see Things to check. |
| [`thesis/Lubel_Itay_MA_Thesis_ABM.pdf`](../../thesis/Lubel_Itay_MA_Thesis_ABM.pdf) | The owner's final text of Ch. 5 (printed pp. 131–176, §5.1–5.7 with Fig. 5.1–5.11 and equations), a tables page (p. 229: Table 5.1), and App. 5 (pp. 235–254: Tables A5.1–A5.7, eq. A5.1–A5.3, Fig. A5.1–A5.6). 67 PDF pages, text layer present. | Canonical (AGENTS.md › Local conventions). Text compared word by word with the working copies on 2026-10-12: identical apart from layout, hyphenation and the equations, which only the PDF carries. Figure images not examined. |
| Working copies on the owner's Drive: `full_thesis.md` (Ch. 5) and `Appendix 5. ABM.docx` | Paths in AGENTS.md. | Same text as the PDF. They replaced three older .docx copies in `thesis/`, whose Ch. 5 differed in about 7% of words (see log.md, 2026-10-12). |
| [`docs/DATA.md`](../../docs/DATA.md) | Data dictionary, HDF5 layout, checksums. | Read. Itay (2026-10-12): outdated, treat with suspicion; follow the code where they differ. Checked against the calibration files on 2026-10-12: checksums and sizes match, the yearly group count does not (75, not 76). See Things to check. |
| [`docs/objective_function.md`](../../docs/objective_function.md) | Code-level walkthrough of the objective. | Read; describes a different formula from `obj_func`. Outdated (Itay, 2026-10-12): follow the code and Ch. 5 §5.5.2. See Things to check. |
| [`docs/INSTALL.md`](../../docs/INSTALL.md), [`docs/ZENODO_UPLOAD.md`](../../docs/ZENODO_UPLOAD.md) | Install guide; one-time Zenodo upload walkthrough. | Listed only. |
| [`CHANGELOG.md`](../../CHANGELOG.md), [`CITATION.cff`](../../CITATION.cff) | History (v1.0.0 2026-05-31, then the [Unreleased] reshaping); citation metadata. | Read. |
| Docstrings in `model.py` | Few. The module docstring still names `nomad_abm.model` and a `Code/model_opt.py` shim. | Stale, see Things to check. |

## Input data (not in git; Zenodo 10.5281/zenodo.20473345)
Per docs/DATA.md (treat with suspicion, Itay 2026-10-12):
- `yearly_data_10_25.h5`: `group_0`…`group_75` (76 years), each with `array_0` (float64) and `array_1`, `array_2` (float32), 318 × 280. Lazy-loaded by `LazyYearlyData` (L62–120). The file itself holds 75 years, `group_0`…`group_74`, plus a `metadata` group (checked 2026-10-12; see Things to check).
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
  - Itay, 2026-10-12: This file is old, follow the code and updated thesis file.
  - The code and Ch. 5 §5.5.2 still differ on the site-type term: `obj_func` compares enclosure-to-other ratios (L1224–1232), Ch. 5 §5.5.2 proportions of all sites. That choice is the owed rationale on [calibration objective](../mechanisms/calibration-objective.md).
  - Deferred to that page (agreed 2026-10-12).
- docs/DATA.md gives the grid as "318 columns × 280 rows". The code treats arrays as (318, 280) = rows × columns and builds a grid 280 wide and 318 high (L957–958).
  - Itay, 2026-10-12: Same as above.
  - Asked whether DATA.md is outdated as a whole or only where it conflicts with the code and the files. Itay, 2026-10-12: Treat it with suspicion, I don't remember exactly from when is it and how I created it.
- docs/DATA.md says the `metadata` group is "not consumed by the model". `LazyYearlyData` reads `f['metadata'].attrs['num_groups']` from the yearly file (L76), and `load_permanent_data` reads `num_groups` and `arrays_per_group` from the permanent file (L129–131). The DATA.md layout for the yearly file shows no `metadata` group.
  - Itay, 2026-10-12: I am not familiar with metadata group, but, as said above, it seems outdated. It may refer to the code I used to generate the different files inside the permanent and yearly data in the h5py files.
  - Checked 2026-10-12 in the calibration files (from the repository history, commit `14cb755^`; SHA-256 equal to docs/DATA.md). Both have a top-level `metadata` group: `yearly_data_10_25.h5` has `num_groups` = 75 and `arrays_per_group` = 3, and `per_data_10_25.h5` has `num_groups` = 1 and `arrays_per_group` = 6. DATA.md's "76 groups, `group_0`…`group_75`" counts `metadata` as a year; the file has `group_0`…`group_74`.
  - The code depends on the group: both reads are unguarded, so a data file without a `metadata` group would stop the model at loading (L76, L129–131). The part of DATA.md that looks outdated is the "not consumed" note, not the group itself.
- Stale names. The `model.py` docstring (L1–7) refers to `nomad_abm.model` and a `Code/model_opt.py` shim, and `sensitivity_model.py` to `Code/model_opt_sensitivity.py`. calibration.ipynb cell 0 says it uses "the standalone `model_opt.py` module". These files no longer exist (CHANGELOG [Unreleased]).
  - Itay, 2026-10-12: So correct those. I did some reorganization in the main.
  - Not done yet: these are edits to `Code/`, outside the wiki.
- README › Reproducibility says outputs "land in timestamped folders under `Results/`". `run_model_opt` writes `Results/run/trial_<n>/iter_<i>` (L1247, L1297), and the notebooks write to `D:\itay\ABM\Results`.
  - Itay, 2026-10-12: The code will need to be updated so it will be able to land in the relevant folder if someone wants to reproduce it.
- The two model files are diverging copies (see "How the two model files differ"). Calibration used `model.py` and the sensitivity tests used `sensitivity_model.py`.
  - Itay, 2026-10-12: This is okay as the sensitivity analysis necessitated some adaptations. It just have to be clear. Treat the model.py as the original and the sensitivity as a specific version.
  - Differences 2 and 5, and the fixed-territory reset in 4, serve the sensitivity tests directly (longer runs, fixed territory). Differences 1, 3 and 6 are not tied to a sensitivity switch. For difference 3, Itay's Year-0 reply ([overview](overview.md), Things to check, 2026-10-12) makes `model.py`'s rule the intended one, so the sensitivity runs used a different Year-0 rule from the calibrated model.
  - Asked whether the sensitivity file's Year-0 rule was a deliberate adaptation. Itay, 2026-10-12: No, it is a mistake, it should follow the same as model.py (I don't think it did any harm as usually year 0 no one is in stress nor flourish).
  - Checked 2026-10-12 with the calibration data files and the best-trial weights. On the Year-0 surface (no history: reuse 0, exhaustion 10 everywhere), the mean suitability within 20 cells (`env_mean_val`, L255–263) at valid camp cells, weighted as camp draws are (suitability³, L336), averages 5.02, against the thresholds 3.5 and 5.0 (`sensitivity_model.py` L896–903). The first household to place gets radius 20 with probability about 52%, 25 with about 43% and 30 with about 6%. Later households draw on a surface already lowered by earlier camps, which shifts them toward 25 and 30. So in the sensitivity runs, roughly half of the Year-0 territories were probably 20 cells rather than 25. Script: a numpy rebuild of `get_suitability_raster` at year 0; nothing was run in the model itself.
  - Asked whether to take up differences 1, 4 and 6 on their mechanism pages. Itay, 2026-10-12: On the overlap rule never firing - yes this is a bug I didn't notice at the time...; but agree overall to defer to the files.
  - Deferred (agreed 2026-10-12): difference 1 to [camp and territory placement](../mechanisms/camp-and-territory-placement.md), differences 4 and 6 to [crisis and replacement](../mechanisms/crisis-and-replacement.md).
- Equation labels in App. 5. The captions say "Equations A5.1 and A5.2" and "Equation A5.3", but the equation objects themselves read "eq 4.1", "eq 4.2" and "eq 4.3 + 2" (App. 5 §A5.2).
  - Itay, 2026-10-12: Recheck in the updated pdf file. But generally should be 5.x.
  - Rechecked 2026-10-12 on the rendered page of `thesis/Lubel_Itay_MA_Thesis_ABM.pdf`, printed p. 237 (PDF p. 50). The body text says "Equations eq A5.1 and eq A5.2" and "Equation eq A5.3", the caption boxes say "Equations A5.1 and A5.2" and "Equation A5.3", and the equation objects still read "eq 4.1", "eq 4.2" and "eq 4.3 + 2". The Ch. 5 equations (e.g. Need and Working herd, p. 154) carry no numbers.
  - Asked which numbering the App. 5 equations should carry, A5.1–A5.3 or 5.x. Itay, 2026-10-12: A5.x.
- Figure images (Ch. 5 Fig. 5.1–5.11, App. 5 Fig. A5.1–A5.6) are in the PDF but have not been examined; only their captions were read. Fig. 5.2–5.7 (pp. 143–161) show the behaviours, the year cycle and the run, so the images may hold schedule detail worth checking against the code.
  - Asked whether to compare the images with the code now. Itay, 2026-10-12: No need.
