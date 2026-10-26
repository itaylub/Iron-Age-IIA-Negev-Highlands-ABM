---
type: model
created: 2026-10-08
code_commit: 032c2a1fbd26ec47017c65939ca372e02a575938
previous_code_commit: 2249331932b0a42ec47c33bca0ac94f4b8728813
---

# Inventory

What is in the repository on branch `claude/separate-pr-code-fixes` at commit `032c2a1` (2026-10-26), re-pinned on 2026-10-26 from the first reading at `2249331` (2026-10-05, read on 2026-10-08). The branch holds the 18 fixes of PR 8 (separate-PR list in `log.md`) and the October 2026 calibration scripts; `master` is still the thesis version. The repository is under git: <https://github.com/itaylub/Iron-Age-IIA-Negev-Highlands-ABM>. Nothing was run.

## Languages and environment
- Python. `environment.yml` (conda env `nomad_model`, `python>=3.11`) and `requirements.txt` both state "Verified working on Python 3.14 with numpy 2.3, mesa 3.3, geopandas 1.1". Pins are open-ended `>=`, except Mesa. The code needs at least Mesa 3.3: `model.py`'s replacements call `Agent.create_agents`, which Mesa 3.0.0 lacks (log.md, 2026-10-14). Since 2026-10-26 both files pin `mesa==3.5.1`, the version in the owner's PC environment that ran the October 2026 calibration (`itay_base_env`, pixi: mesa 3.5.1, numpy 2.5.3, Python 3.12.14; reported by Itay, 2026-10-26), because seeded runs reproduce only with the same Mesa generator. Mesa 3.5 warns that `seed` will become `rng`; `NomadModel` still passes `seed`.
- Libraries the model imports: mesa, numpy, scipy (`convolve2d`, `distance_transform_edt`, `linalg`), h5py, pandas, geopandas, shapely, matplotlib, seaborn, optuna, `multiprocessing.shared_memory` (`model.py`, L19–39).
- `model.py` forces single-threaded BLAS through environment variables before importing numpy (L11–17).

## Entry points (notebooks)
| File | What it does | Imports |
|---|---|---|
| [`Code/calibration.ipynb`](../../Code/calibration.ipynb) | Optuna study `opt_2_26_v1` (the thesis study; TPE sampler, MedianPruner), analysis plots, 30-replicate best-trial run, summary CSVs. 10 cells (cells 5 and 6 swapped in PR 8 item 18), with stored outputs since commit `a83420c` (2026-10-23). Output paths use `RESULTS_DIR` (item 11). | `model` |
| [`Code/sensitivity_analysis.ipynb`](../../Code/sensitivity_analysis.ipynb) | Time horizon (150 y), number of agents (5/15/20), fixed vs flexible territory, null-weight baseline, CSV export. 12 cells, no stored outputs. Cell 9 compares the null baseline with the 30-replicate mean (item 18). | `sensitivity_model` |
| [`Code/test.ipynb`](../../Code/test.ipynb) | 2-year smoke run with random Dirichlet weights; substitutes mock zero rasters if the yearly HDF5 is missing. 2 cells, with stored outputs from the test runs (commits `180883d`, `a83420c`). | `model` |

Details per experiment: [experiments](experiments.md).

## Entry points (scripts, since 2026-10-22)
The October 2026 recalibration and sensitivity tests ran from these scripts rather than from the notebooks (on the owner's PC, 16 processes).

| File | What it does (its docstring) |
|---|---|
| [`scripts/abm_parallel.py`](../../scripts/abm_parallel.py) | Shared helpers for several processes: input data in shared memory, the Optuna study; sets `MKL_THREADING_LAYER=SEQUENTIAL` and the GDAL/PROJ paths (`4b1230b`). |
| [`scripts/timing_test.py`](../../scripts/timing_test.py) | Times 75-year replicates alone and several at once. |
| [`scripts/calibrate.py`](../../scripts/calibrate.py) | The Optuna calibration on one shared study from several processes: "Same objective, search space, pruner and replicates as `Code/calibration.ipynb`". `TPESampler(constant_liar=True)`, `MedianPruner(n_startup_trials=10, n_warmup_steps=5)` (L55, L61); target file chosen with `--calib-shp` (`fa64c9e`). |
| [`scripts/analyse_calibration.py`](../../scripts/analyse_calibration.py) | Settle check of a finished study, then re-runs of its leading weight sets. |
| [`scripts/run_measures.py`](../../scripts/run_measures.py) | Per-run fit measures of one weight set with the seeds of its re-evaluation, which also tests reproducibility. |
| [`scripts/make_calib_sites.py`](../../scripts/make_calib_sites.py) | Builds the calibration sites file from the sites table (thesis Appendix 1). |
| [`scripts/sensitivity.py`](../../scripts/sensitivity.py) | Sensitivity tests of one calibrated weight set with `sensitivity_model.py`, run in parallel. |
| [`scripts/plot_results.py`](../../scripts/plot_results.py), [`scripts/plot_thesis_figures.py`](../../scripts/plot_thesis_figures.py) | Figures from saved outputs; run no model. |

## Model files
| File | Lines | Role |
|---|---|---|
| [`Code/model.py`](../../Code/model.py) | 1,460 | The calibrated model: data loaders, helpers, `Household_Agent`, `NomadModel`, plotting, `to_gdf`, `obj_func`, `run_model_opt`, `objective_function`, Optuna `objective`. |
| [`Code/sensitivity_model.py`](../../Code/sensitivity_model.py) | 1,251 | `model.py` with `num_agents` and `fixed_territory` switches (PR 8 applied every fix to both files, so it stays `model.py` plus its switches; log.md, 2026-10-14). No `objective_function` or `objective`. Itay (2026-10-12): `model.py` is the original, this file a specific version for the sensitivity analysis. |

### How the two model files differ
At commit `032c2a1`, apart from comments and docstrings, `diff` shows these behavioural differences (line numbers for `model.py` first, `sensitivity_model.py` second). PR 8 removed the earlier differences in the overlap test, the Year-0 territory and the placement of replacements (items 2, 3, 6), and `5f415eb` the Year-0 camp-memory radius.
1. **Switches.** `NomadModel` takes `num_agents` and `fixed_territory` (L927–937); `model.py` always uses `Num_agents()` (L1029).
2. **Rainfall years.** `sensitivity_model.py` reads `indices[year % len(indices)]` (L418, L1032) and, once a run passes the end of the list, appends a new shuffle of the years for each further cycle, with Mesa's generator (`move_year`, L1018–1024; item 18). `model.py` reads `inds[year]` with no wrap-around (L501, L1106), which is enough for 75 years.
3. **Failure handling.** Both files take a failed household off the grid and call `self.remove()` (L628–629; L540–541). `sensitivity_model.py` also removes its territory from `model.territories` (L535–536). In fixed-territory mode it instead resets the household in place, with a new herd, manpower and a surplus of 10 (L528–533), and queues no replacement (L794–797; item 5).
4. **Fixed-territory mode** (`sensitivity_model.py` only): `year_initiation` keeps the camp cell and territory and only places the family camps (L571–582), and `move_year` skips `reset_pos` (L1013–1014).
5. **Territory radius attribute.** `sensitivity_model.py` stores the radius on the household (`territory_radius`, L481), which fixed-territory mode reuses (L580–581).
6. **`create_agents`.** `sensitivity_model.py` defines its own static `create_agents` (L871–877); `model.py` relies on Mesa's `Agent.create_agents` (Mesa 3.3).

## Documentation
| File | Content | Status |
|---|---|---|
| [`README.md`](../../README.md) | Overview, layout, install, data, citation. | Edited in PR 8 (item 11, `7bb336e`); not re-read since. At `2249331` it described outputs as "timestamped folders", see Things to check. |
| [`thesis/Lubel_Itay_MA_Thesis_ABM.pdf`](../../thesis/Lubel_Itay_MA_Thesis_ABM.pdf) | The owner's final text of Ch. 5 (printed pp. 131–176, §5.1–5.7 with Fig. 5.1–5.11 and equations), a tables page (p. 229: Table 5.1), and App. 5 (pp. 235–254: Tables A5.1–A5.7, eq. A5.1–A5.3, Fig. A5.1–A5.6). 67 PDF pages, text layer present. | Canonical (AGENTS.md › Local conventions). Text compared word by word with the working copies on 2026-10-12: identical apart from layout, hyphenation and the equations, which only the PDF carries. Figure images not examined. |
| Working copies on the owner's Drive: `full_thesis.md` (Ch. 5) and `Appendix 5. ABM.docx` | Paths in AGENTS.md. | Same text as the PDF. They replaced three older .docx copies in `thesis/`, whose Ch. 5 differed in about 7% of words (see log.md, 2026-10-12). |
| [`docs/DATA.md`](../../docs/DATA.md) | Data dictionary, HDF5 layout, checksums. | Read. Itay (2026-10-12): outdated, treat with suspicion; follow the code where they differ. Checked against the calibration files on 2026-10-12: checksums and sizes match, the yearly group count does not (75, not 76). See Things to check. Revised in PR 8 (item 11, `7bb336e`: 75 yearly groups plus `metadata`, grid orientation, metadata use); the revision not yet re-read against the files. |
| [`docs/objective_function.md`](../../docs/objective_function.md) | Code-level walkthrough of the objective. | At `2249331` it described a different formula from `obj_func`; outdated (Itay, 2026-10-12): follow the code and Ch. 5 §5.5.2. Rewritten from the code and Ch. 5 in PR 8 (item 11, `7bb336e`); not yet re-read. See Things to check. |
| [`docs/INSTALL.md`](../../docs/INSTALL.md), [`docs/ZENODO_UPLOAD.md`](../../docs/ZENODO_UPLOAD.md) | Install guide; one-time Zenodo upload walkthrough. | Listed only. |
| [`CHANGELOG.md`](../../CHANGELOG.md), [`CITATION.cff`](../../CITATION.cff) | History (v1.0.0 2026-05-31, then the [Unreleased] reshaping); citation metadata. | Read. |
| Docstrings in `model.py` | Few, plus comments on each PR 8 change. The module docstring now names `Code/calibration.ipynb` and `Code/sensitivity_model.py` (L1–7; item 11). | Current. |

## Input data (not in git; Zenodo 10.5281/zenodo.20473345)
Per docs/DATA.md (treat with suspicion, Itay 2026-10-12):
- `yearly_data_10_25.h5`: `group_0`…`group_75` (76 years), each with `array_0` (float64) and `array_1`, `array_2` (float32), 318 × 280. Lazy-loaded by `LazyYearlyData` (L61–119). The file itself holds 75 years, `group_0`…`group_74`, plus a `metadata` group (checked 2026-10-12; see Things to check). Array 0 enters the suitability sum as current-year rainfall; array 2 is the herds' pasture (`pasture_layer`, L273–280, which sets no-data cells to 0; PR 8 item 1).
- `per_data_10_25.h5`: single `group_1` with six arrays. `model.py` unpacks them as agri, kb, pw, veg_fit, rain, slope (L496–497).
- `ext_raster.npy`, `place_raster.npy`: `uint8` 0/1 masks.
- `P_for_calib.shp`: EPSG:2039 points, `value` 1 (other site) or 2 (enclosed compound). The model's default target.
- `P_for_calib_strict.shp` (since 2026-10-24): the same format, built from the sites table by `scripts/make_calib_sites.py`; the scripts take it with `--calib-shp`.
- Paths default to `<repo>/Data`, overridable with `NOMAD_ABM_DATA_DIR`, `NOMAD_ABM_RESULTS_DIR`, `NOMAD_ABM_CALIB_SHP` (L48–58).

## Outputs (not in git)
- Per run: `household_data.csv` (Mesa DataCollector agent reporters: Manpower, flocks, surplus, "proseprity index", position, enclosures, env_quality; L1078–1085, L1352–1353), weight JSONs, optional `year_<n>_map.png` (`viz_map`) and `spatial_similarity.png` (`obj_func`).
- At `2249331` the notebooks wrote to hard-coded `D:\itay\ABM\Results\…` paths, including the Optuna SQLite store `opt_run.db`; since PR 8 they use `RESULTS_DIR` (item 11). The October 2026 studies write their own results folders, given with `--results-dir` (on the PC, under `D:\abm_runs\`). None of the results are in the repository. See [experiments](experiments.md).

## Scripts (data handling, not the model)
- [`scripts/download_data.py`](../../scripts/download_data.py): fetch and checksum the Zenodo bundle into `Data/`.
- [`scripts/build_data_bundle.py`](../../scripts/build_data_bundle.py): build the bundle zip on the data machine.
- [`scripts/inspect_data.py`](../../scripts/inspect_data.py): read-only JSON inventory of `Data/`.

## Utility code (one line each)
- `LazyYearlyData`, `load_permanent_data`, `SharedDataManager`, `GlobalData`, `ensure_data_loaded` (L61–227): data loading and shared memory for parallel workers; falls back to `np.ones`/zeros if files are missing.
- `viz_map` (L1142–1205): yearly maps. `to_numpy_y` (L250–252): Mesa-to-array row flip.

## Things to check
Dated entries below keep the line numbers of commit `2249331` (2026-10-05), as checked then. Lines starting "Done in PR 8" were added on 2026-10-26.
- `docs/objective_function.md` describes `ratio_enc = t1_ratio / t_ratio`, an `overlap_func` built from the symmetric difference, and `total = ((1 - overlap_func) + ratio_enc) / 2` with "higher is better". `obj_func` computes `1 - IoU`, `|t_ratio - t1_ratio|` and their mean, which is minimised (L1217–1233). The doc's pointers ("§5.6.3 of the thesis", "§A5.3 of the appendix") do not match the current numbering (§5.5.2; §A5.3 has no objective). Should the doc be rewritten from Ch. 5 §5.5.2?
  - Itay, 2026-10-12: This file is old, follow the code and updated thesis file.
  - The code and Ch. 5 §5.5.2 still differ on the site-type term: `obj_func` compares enclosure-to-other ratios (L1224–1232), Ch. 5 §5.5.2 proportions of all sites. That choice is the owed rationale on [calibration objective](../mechanisms/calibration-objective.md).
  - Deferred to that page (agreed 2026-10-12).
  - Done in PR 8 (item 11, `7bb336e`): the doc was rewritten from the code and Ch. 5. Not yet re-read.
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
  - Done in PR 8 (item 11, `7bb336e`): stale module names in the `Code/` docstrings and calibration.ipynb, and docs/DATA.md (75 yearly groups plus `metadata`, grid orientation, metadata use).
- README › Reproducibility says outputs "land in timestamped folders under `Results/`". `run_model_opt` writes `Results/run/trial_<n>/iter_<i>` (L1247, L1297), and the notebooks write to `D:\itay\ABM\Results`.
  - Itay, 2026-10-12: The code will need to be updated so it will be able to land in the relevant folder if someone wants to reproduce it.
  - Done in PR 8 (item 11, `7bb336e`): output paths for reproduction. Whether README's wording now matches is not yet re-read.
- The two model files are diverging copies (see "How the two model files differ"). Calibration used `model.py` and the sensitivity tests used `sensitivity_model.py`.
  - Itay, 2026-10-12: This is okay as the sensitivity analysis necessitated some adaptations. It just have to be clear. Treat the model.py as the original and the sensitivity as a specific version.
  - Differences 2 and 5, and the fixed-territory reset in 4, serve the sensitivity tests directly (longer runs, fixed territory). Differences 1, 3 and 6 are not tied to a sensitivity switch. For difference 3, Itay's Year-0 reply ([overview](overview.md), Things to check, 2026-10-12) makes `model.py`'s rule the intended one, so the sensitivity runs used a different Year-0 rule from the calibrated model.
  - Asked whether the sensitivity file's Year-0 rule was a deliberate adaptation. Itay, 2026-10-12: No, it is a mistake, it should follow the same as model.py (I don't think it did any harm as usually year 0 no one is in stress nor flourish).
  - Checked 2026-10-12 with the calibration data files and the best-trial weights. On the Year-0 surface (no history: reuse 0, exhaustion 10 everywhere), the mean suitability within 20 cells (`env_mean_val`, L255–263) at valid camp cells, weighted as camp draws are (suitability³, L336), averages 5.02, against the thresholds 3.5 and 5.0 (`sensitivity_model.py` L896–903). The first household to place gets radius 20 with probability about 52%, 25 with about 43% and 30 with about 6%. Later households draw on a surface already lowered by earlier camps, which shifts them toward 25 and 30. So in the sensitivity runs, roughly half of the Year-0 territories were probably 20 cells rather than 25. Script: a numpy rebuild of `get_suitability_raster` at year 0; nothing was run in the model itself. Its effect on the §5.6 results is deferred to [experiments](experiments.md) (agreed 2026-10-12).
  - Asked whether to take up differences 1, 4 and 6 on their mechanism pages. Itay, 2026-10-12: On the overlap rule never firing - yes this is a bug I didn't notice at the time...; but agree overall to defer to the files.
  - Deferred (agreed 2026-10-12): difference 1 to [camp and territory placement](../mechanisms/camp-and-territory-placement.md), differences 4 and 6 to [crisis and replacement](../mechanisms/crisis-and-replacement.md).
  - Done in PR 8: differences 1, 3 and 6 are gone (items 3, 2 and 6), and the Year-0 camp memory now matches too (`5f415eb`). What remains is listed under "How the two model files differ" above.
- Equation labels in App. 5. The captions say "Equations A5.1 and A5.2" and "Equation A5.3", but the equation objects themselves read "eq 4.1", "eq 4.2" and "eq 4.3 + 2" (App. 5 §A5.2).
  - Itay, 2026-10-12: Recheck in the updated pdf file. But generally should be 5.x.
  - Rechecked 2026-10-12 on the rendered page of `thesis/Lubel_Itay_MA_Thesis_ABM.pdf`, printed p. 237 (PDF p. 50). The body text says "Equations eq A5.1 and eq A5.2" and "Equation eq A5.3", the caption boxes say "Equations A5.1 and A5.2" and "Equation A5.3", and the equation objects still read "eq 4.1", "eq 4.2" and "eq 4.3 + 2". The Ch. 5 equations (e.g. Need and Working herd, p. 154) carry no numbers.
  - Asked which numbering the App. 5 equations should carry, A5.1–A5.3 or 5.x. Itay, 2026-10-12: A5.x.
- Figure images (Ch. 5 Fig. 5.1–5.11, App. 5 Fig. A5.1–A5.6) are in the PDF but have not been examined; only their captions were read. Fig. 5.2–5.7 (pp. 143–161) show the behaviours, the year cycle and the run, so the images may hold schedule detail worth checking against the code.
  - Asked whether to compare the images with the code now. Itay, 2026-10-12: No need.
