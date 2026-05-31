# Legacy snapshot

Frozen copies of the model source as it existed at the **start of
Phase 6** of the publication-readiness pass, kept here as an explicit
"worst case I can revert" safety net.

The same files are also reachable through git history (every commit
before `Phase 6: ...` contains them at their original paths under
`Code/`) and through the local `legacy-pre-publication` tag — this
directory just makes them visible without git commands.

## Contents

| File | Original path | Notes |
|---|---|---|
| `model_opt.py` | `Code/model_opt.py` | Main model, before being moved to `src/nomad_abm/model.py`. Already had hardcoded paths externalized in Phase 3. |
| `model_opt_sensitivity.py` | `Code/model_opt_sensitivity.py` | Sensitivity variant, before being moved to `src/nomad_abm/sensitivity.py`. |
| `model_code_26_2.ipynb` | `Code/model_code_26_2.ipynb` | Optimization run notebook, outputs already stripped (Phase 4). |
| `sensitivity_analysis.ipynb` | `Code/sensitivity_analysis.ipynb` | Sensitivity notebook, outputs already stripped (Phase 4). |

## How to restore

Replace the contents of `Code/` with the files here and delete
`src/nomad_abm/`:

```bash
cp legacy/*.py legacy/*.ipynb Code/
git rm -r src/ configs/
```

You will lose the CLI (`python -m nomad_abm run`) and the YAML config
plumbing, but the notebook-driven workflow returns exactly as it was
before Phase 6.

This directory may be removed once Phase 6 is verified end-to-end on
the data machine.
