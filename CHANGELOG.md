# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Phase 7 — smoke tests + synthetic fixture + CI pytest job

- `tests/fixtures/make_fixture.py` builds a tiny synthetic `Data/`
  directory at a caller-supplied path. Layout matches the real schema
  confirmed by `scripts/inspect_data.py` and documented in
  `docs/DATA.md`:
  - `yearly_data*.h5`: `group_0..N` with `array_0..M`.
  - `per_data*.h5`: singleton `group_1` (1-indexed) + sibling
    `metadata` group.
  - `place_raster.npy` / `ext_raster.npy`: `uint8` binary masks
    of shape (318, 280).
  - `P_for_calib.shp`: EPSG:2039 points with `value` 1 or 2.
  Values are random noise — for smoke tests only.
- `tests/conftest.py` provides session-scoped `synthetic_data_dir`
  and per-test `env_with_synthetic_data` fixtures (the latter
  monkeypatches the three `NOMAD_ABM_*` env vars).
- `tests/test_smoke.py` exercises the package import, the
  `python -m nomad_abm run --help` CLI surface, the `Code/`
  backwards-compat shim, the synthetic fixture schema, the
  calibration shapefile classes, and the shipped `configs/default.yaml`.
- New `tests` job in `.github/workflows/ci.yml` uses
  `conda-incubator/setup-miniconda` to create the `nomad_model`
  environment from `environment.yml`, installs the package with
  `pip install -e .`, and runs `pytest -q`. Runs alongside the
  existing `lint` and `notebook-clean` jobs.

### Phase 5b — dependency cleanup (informed by data-machine inventory)

- Ran `scripts/inspect_data.py` on the data machine (Windows, conda
  env `Mesa_env`, Python 3.14.0). Output drove the following changes.
- Dropped explicit dependencies that the package code never imports:
  `rasterio`, `folium`, `pysal`, `scikit-learn`, `sympy`, `tqdm`,
  `fiona`, `pyproj`. (`fiona` and `pyproj` still arrive transitively
  through `geopandas`.) Reduces the dep surface from ~20 to 11 and
  matches the author's actually-installed Mesa env (which lacks
  `rasterio` yet runs the model successfully).
- Relaxed version pins to `>=` with an upper bound only on `mesa`
  (where 4.0 will be a breaking change). The previously exact pins
  (`numpy 1.26`, `mesa 3.0`, etc.) blocked the data machine's
  working configuration (`numpy 2.3.3`, `mesa 3.3.0`,
  `geopandas 1.1.1`, `pandas 2.3.3`, `h5py 3.15.0`, `optuna 4.5.0`).
- `pyproject.toml` `[tool.black] extend-exclude` updated to the new
  `thesis/` path (was `Thesis Chapter/`) and now also skips
  `legacy/`.

### Phase 8 — ODD protocol and documentation (in progress)

- `docs/ODD.md` — canonical model description following Grimm et al.
  (2020). Seven standard sections (Purpose & patterns, Entities &
  state variables, Process overview, Design concepts, Initialisation,
  Input data, Submodels) seeded from the current thesis Chapter 4 and
  Appendix 4 (read from the author's Drive; .docx files untouched).
  Cross-references Appendix 4 sections for full parameter tables
  rather than duplicating them.
- `docs/DATA.md` — data dictionary of every input file under `Data/`:
  format, shape, units, CRS (EPSG:2039 / ITM), source. Includes a
  list of open items needing data-machine confirmation (HDF5 internal
  layout, `ext_raster.npy` provenance, file checksums for the planned
  Zenodo bundle).
- `docs/INSTALL.md` — long-form install guide for Linux / macOS /
  Windows, with conda (recommended) and pip paths and a
  troubleshooting table.
- `docs/objective_function.md` — header rewritten to clarify it is a
  *code-level* walkthrough; mathematical statement is in §4.6.3 +
  §A4.3 of the thesis and summarised in `docs/ODD.md` §7.6.
- Rename `Thesis Chapter/` → `thesis/` (no space — friendlier to
  shell scripts and CI). Seven tracked files renamed cleanly via
  `git mv`.
- README layout block updated to reflect the new `docs/` contents and
  the renamed `thesis/` directory; `pyproject.toml` ruff
  `extend-exclude` follows the rename.
- The author's `.docx` thesis materials on Drive (`full_thesis.docx`,
  `Appendix 4. ABM.docx`, `Appendix 6. Glossary.docx`, the per-chapter
  tables/figures docs) are treated as **read-only**: they were
  consulted to author the ODD and DATA documents but **never
  modified**.

### Phase 6 — package layout, CLI, YAML config (in progress)

- New package at `src/nomad_abm/`:
  - `model.py` (canonical home of the simulation; was `Code/model_opt.py`).
  - `sensitivity.py` (sensitivity variant; was
    `Code/model_opt_sensitivity.py`).
  - `cli.py` exposing `python -m nomad_abm run --config <path>
    --seed <int>` as the canonical entry point.
  - `__init__.py`, `__main__.py`.
- `configs/default.yaml` — YAML config consumed by the CLI. Settings
  in `paths.*` are translated into `NOMAD_ABM_*` env vars before the
  model module is imported, so existing env-var contracts still hold.
- `Code/model_opt.py` and `Code/model_opt_sensitivity.py` are now
  thin **shims** that re-export from the new package. Existing
  notebooks that say `from model_opt import ...` keep working without
  any edits. The shims inject `src/` onto `sys.path` so they work
  even without `pip install -e .`.
- `legacy/` directory holds a frozen pre-Phase-6 copy of the four
  `Code/` files (two `.py`, two `.ipynb`) and a `legacy/README.md`
  explaining the revert procedure.
- `pyproject.toml`: added `[project.scripts] nomad-abm` entry point,
  `[tool.setuptools.packages.find] where = ["src"]`, `pyyaml` runtime
  dep, ruff per-file-ignores moved to the new file paths, ruff
  `extend-exclude` skips `legacy/`.
- `environment.yml` and `requirements.txt` gain `pyyaml`.
- README rewritten: install adds `pip install -e .`, "How to run"
  documents both the CLI and the notebook paths, layout updated.

### Phase 5 — quality gates and packaging foundations (in progress)

- Add `pyproject.toml` with project metadata, runtime dependency list
  (mirroring `environment.yml`), `[project.optional-dependencies] dev`
  (ruff, black, pytest, pre-commit, nbstripout), and tool sections
  (`[tool.ruff]`, `[tool.black]`, `[tool.pytest.ini_options]`).
- Add `requirements.txt` so non-conda users can `pip install -r`.
- Move `Code/environment.yml` → `environment.yml` at repo root
  (standard location).
- Add `.github/workflows/ci.yml` with two jobs:
  - `lint`: `ruff check` on a conservative ruleset (catches real bugs:
    syntax errors, undefined names; doesn't enforce style yet).
  - `notebook-clean`: fails if any `*.ipynb` contains outputs or
    execution counts. Backstop for the nbstripout pre-commit hook.
  - A `black --check` job will be added once the codebase has been
    reformatted in a dedicated pass.
- Extend `.pre-commit-config.yaml` with the ruff hook to match CI.
- README install section rewritten with conda + pip + dev paths.

### Phase 4 — notebook hygiene (in progress)

- Remove legacy notebooks: `Code/old/` (29 MB, six notebooks),
  `Code/run_numpy.ipynb`, `Code/run_numpy.md`,
  `Code/model_code_26.ipynb`, `Code/convert_to_numpy.ipynb`.
- Tag `legacy-pre-publication` (local) preserves the pre-deletion
  state; `master` also still contains all removed files for recovery.
- Strip outputs from the two surviving notebooks:
  `Code/model_code_26_2.ipynb` (384 KB → 20 KB) and
  `Code/sensitivity_analysis.ipynb` (80 KB → 20 KB).
- Move `Code/varia/obj_explain.md` → `docs/objective_function.md`;
  remove duplicate `obj_func_explanation` (byte-identical to .md) and
  `env111.txt` (byte-identical to `environment.yml`). Empty `varia/`
  directory removed.
- Add `.pre-commit-config.yaml` with nbstripout + standard hygiene
  hooks (`trailing-whitespace`, `end-of-file-fixer`,
  `check-added-large-files` capped at 1 MB) to keep notebook outputs
  and large binaries from sneaking back in.
- Remove overly broad `*.yml` / `*.yaml` rules from `.gitignore`
  (they were blocking legitimate config files like
  `.pre-commit-config.yaml`, future CI workflows, and the planned
  `configs/default.yaml`).
- README updated: clarifies which notebooks are canonical, points at
  `docs/`, notes the legacy removal.

### Phase 3 — externalize hardcoded paths (in progress)

- Remove hardcoded `D:\itay\ABM\...` Windows paths from
  `Code/model_opt.py` (lines 42–47, 1285) and
  `Code/model_opt_sensitivity.py` (lines 42–47).
- Paths now default to `<repo_root>/Data` and `<repo_root>/Results`,
  resolved at module import time relative to the source file.
- Three environment variables override the defaults:
  `NOMAD_ABM_DATA_DIR`, `NOMAD_ABM_RESULTS_DIR`, `NOMAD_ABM_CALIB_SHP`.
- `README.md` documents the env-var contract.

### Phase 2 — citation metadata (in progress)

- Add `CITATION.cff` so GitHub renders a "Cite this repository" button.
- Add this `CHANGELOG.md`.
- Update `LICENSE` copyright holder from the GitHub handle to the
  author's full name.

### Phase 1 — quick wins (merged via PR #2)

- Rewrite `README.md` with project abstract, install, run instructions,
  reproducibility notes, and a publication-status notice. Replaces the
  3-line placeholder.
- Stop tracking `.idea/` and `.ipynb_checkpoints/` (rules already
  existed in `.gitignore`).
- Remove orphaned files: `output.jpg`, `Code/varia/*.html` (stale
  notebook exports), empty `Thesis Chapter/overview.md`.
- Trim 191 lines of enumerated per-run PNG entries from `.gitignore`;
  blanket `Results/` rule covers them.

## [0.1.0] — 2025-01-01

Initial snapshot of the model accompanying Chapter 4 of the thesis.
Functional Mesa 3.0 agent-based model with Optuna calibration, but with
the publication-readiness gaps tracked above (hardcoded paths, no
tests, no ODD protocol, large data in git, etc.).

[Unreleased]: https://github.com/itaylub/ABM/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/itaylub/ABM/releases/tag/v0.1.0
