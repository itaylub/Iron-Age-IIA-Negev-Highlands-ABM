# AGENTS.md — Development Guidelines for Nomad ABM

This file defines the coding, modeling, and architectural guidelines for AI agents and contributors working on the **Nomad ABM (Iron Age IIA Negev Highlands Human-Environment Dynamics Model)**.

---

## 1. Modeling Framework & Conventions

- **Mesa 3.0 Syntax**: Follow modern Mesa 3.x patterns:
  - Agent initialization: `super().__init__(model)` (or `model.next_id()` when appropriate).
  - Use `mesa.Model` and standard scheduler / agent containers.
  - Data collection via `mesa.datacollection.DataCollector`.
- **Optimization & Parallelism**:
  - Parameter calibration uses [Optuna](https://optuna.org/) with multiprocessing / shared memory.
  - Always enforce single-threading flags (`OMP_NUM_THREADS="1"`, `MKL_NUM_THREADS="1"`, `OPENBLAS_NUM_THREADS="1"`, `NUMEXPR_NUM_THREADS="1"`) before importing NumPy or SciPy in compute workers to prevent core oversubscription.
- **Vectorization over Loops**:
  - Vectorize agent step calculations, terrain queries, and spatial operations with NumPy arrays and SciPy filters (`convolve2d`, `distance_transform_edt`) rather than pure-Python loops over cells.

---

## 2. File Organization & Paths

- **Root-relative paths**:
  - Never hardcode absolute file paths (e.g., `C:\...` or `d:\...`).
  - Derive paths from `_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` or respect environment variables (`NOMAD_ABM_DATA_DIR`, `NOMAD_ABM_RESULTS_DIR`).
- **Data & Results Separation**:
  - `Data/`: Input rasters, shapefiles, and `.h5` bundles (managed via Zenodo and `scripts/download_data.py`). Never commit raw input data to Git.
  - `Results/`: Generated simulation dumps, Optuna study logs, and plots. Always kept out of Git.
  - `Code/`: Pure Python modules (`model.py`, `sensitivity_model.py`) and high-level execution notebooks (`calibration.ipynb`, `sensitivity_analysis.ipynb`).

---

## 3. Code Style & Documentation

- **Docstrings & Units**:
  - Always state physical units in docstrings and parameter comments (e.g., `cell_size: 250 m`, `rainfall: mm/yr`, `flock_size: head of sheep/goats`, `simulation_years: 75`).
  - Keep docstrings clean and concise for academic review and thesis defense.
- **Interactive Script Pattern (`# %%`)**:
  - When prototyping or refactoring agent logic in `.py` files, use `# %%` interactive cell dividers. This allows running code blocks directly in the Jupyter interactive window with variable inspection while maintaining clean, importable modules.
- **Linting & Formatting**:
  - Handled automatically via [Ruff](https://docs.astral.sh/ruff/). Avoid manually tweaking imports or whitespace.

---

## 4. Git & GitHub Hygiene

- **Notebook Cleanliness**:
  - Diffs must ignore cell outputs and execution metadata (`notebook.diff.ignoreOutputs: true`).
- **Data Safeguards**:
  - Large binary data (`.h5`, `.npy`, `.parquet`, `.gdb`) must never be staged or committed.
  - Large simulation artifacts should be aggregated into lightweight summary CSVs or uploaded to Zenodo / OSF with citable DOIs.
