# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Phase 5 — quality gates and packaging foundations (in progress)

- Add `pyproject.toml` with project metadata, runtime dependency list
  (mirroring `environment.yml`), `[project.optional-dependencies] dev`
  (ruff, black, pytest, pre-commit, nbstripout), and tool sections
  (`[tool.ruff]`, `[tool.black]`, `[tool.pytest.ini_options]`).
- Add `requirements.txt` so non-conda users can `pip install -r`.
- Move `Code/environment.yml` → `environment.yml` at repo root
  (standard location).
- Add `.github/workflows/ci.yml` with three jobs:
  - `lint`: `ruff check` on a conservative ruleset (catches real bugs:
    syntax errors, undefined names; doesn't enforce style yet).
  - `format-check`: `black --check --diff`, informational only
    (continue-on-error); will become enforcing after a one-shot
    reformat.
  - `notebook-clean`: fails if any `*.ipynb` contains outputs or
    execution counts. Backstop for the nbstripout pre-commit hook.
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
