"""nomad_abm.cli

Command-line entry point. Usage::

    python -m nomad_abm run --config configs/default.yaml --seed 42

Runs a single replicate of the model (one ``run_model_opt`` call)
using the calibrated weights from Section 4.6.4 of the thesis, unless
overridden in the YAML config. Outputs land under
``$NOMAD_ABM_RESULTS_DIR/cli_run_<timestamp>/trial_0/iter_0/``.

The full Optuna calibration workflow (~200 trials, ~12 days
wall-clock on 4 workers) lives in
``Code/model_code_26_2.ipynb`` and is not driven from this CLI.
"""

from __future__ import annotations

import argparse
import datetime
import os
import sys
from pathlib import Path

import yaml


# Calibrated weights from Section 4.6.4 of the thesis: best-trial
# integer weights [7, 1, 3, 0, 7, 5, 0] (sum 23) normalise to the
# published [0.304, 0.043, 0.130, 0.000, 0.304, 0.217, 0.000]. Order
# matters: ``run_model_opt`` consumes ``ras_wts`` positionally in
# permanent-then-yearly order.
DEFAULT_PERMANENT_INT_WEIGHTS = {
    "dist_to_kb": 7,
    "p_water": 1,
    "Mean_rain": 3,
    "slope_suitability": 0,
}
DEFAULT_YEARLY_INT_WEIGHTS = {
    "return_to_site": 7,
    "humen_stress": 5,
    "Yearly_rain": 0,
}


def _apply_config(config_path):
    """Load YAML config and translate path settings into env vars.

    Must run before ``nomad_abm.model`` is imported, because the path
    constants are computed at module import time.
    """
    if config_path is None:
        return {}
    with open(config_path) as f:
        config = yaml.safe_load(f) or {}
    paths = config.get("paths") or {}
    env_map = {
        "data_dir": "NOMAD_ABM_DATA_DIR",
        "results_dir": "NOMAD_ABM_RESULTS_DIR",
        "calib_shp": "NOMAD_ABM_CALIB_SHP",
    }
    for key, env in env_map.items():
        if paths.get(key):
            os.environ[env] = str(Path(paths[key]).expanduser())
    return config


def _resolve_weights(run_cfg: dict) -> tuple[dict, dict, list]:
    """Apply any weight overrides from the YAML and normalise."""
    weights_cfg = run_cfg.get("weights") or {}
    permanent = {**DEFAULT_PERMANENT_INT_WEIGHTS, **(weights_cfg.get("permanent") or {})}
    yearly = {**DEFAULT_YEARLY_INT_WEIGHTS, **(weights_cfg.get("yearly") or {})}
    total = sum(permanent.values()) + sum(yearly.values())
    if total == 0:
        raise SystemExit("ERROR: weights sum to zero; cannot normalise.")
    perm_n = {k: v / total for k, v in permanent.items()}
    yearly_n = {k: v / total for k, v in yearly.items()}
    ras_wts = list(perm_n.values()) + list(yearly_n.values())
    return perm_n, yearly_n, ras_wts


def _cmd_run(args):
    config = _apply_config(args.config)
    run_cfg = config.get("run") or {}

    seed = args.seed if args.seed is not None else run_cfg.get("seed", 42)
    years = args.years if args.years is not None else run_cfg.get("years", 75)

    perm_n, yearly_n, ras_wts = _resolve_weights(run_cfg)

    # Import AFTER env vars are set so the model's path constants
    # (DATA_DIR, RESULTS_DIR, CALIB_SHP_PATH) resolve to the right
    # locations on disk.
    from nomad_abm.model import ensure_data_loaded, run_model_opt, RESULTS_DIR

    ensure_data_loaded()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    main_run_directory = os.path.join(RESULTS_DIR, f"cli_run_{timestamp}")
    os.makedirs(main_run_directory, exist_ok=True)

    print(f"Running nomad_abm: {years} year(s), seed={seed}")
    print(f"  permanent weights: {perm_n}")
    print(f"  yearly weights:    {yearly_n}")
    print(f"  results root:      {main_run_directory}")
    print()

    _, run_dir = run_model_opt(
        model_years=years,
        ras_wts=ras_wts,
        main_run_directory=main_run_directory,
        permanent_weights_dict=perm_n,
        yearly_weights_dict=yearly_n,
        trial_number=0,
        iteration=0,
        seed=seed,
    )

    print(f"\nDone. Output: {run_dir}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="nomad-abm",
        description="Run a single replicate of the Nomad ABM (Iron Age IIA Negev Highlands).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run a single simulation.")
    run_p.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to YAML config (see configs/default.yaml).",
    )
    run_p.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed (overrides any value in the config).",
    )
    run_p.add_argument(
        "--years",
        type=int,
        default=None,
        help="Number of simulated years. Default 75 (matches the published calibration). "
             "Use --years 5 for a quick smoke run (~3 min).",
    )
    run_p.set_defaults(func=_cmd_run)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
