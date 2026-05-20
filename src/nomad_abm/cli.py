"""nomad_abm.cli

Command-line entry point. Usage::

    python -m nomad_abm run --config configs/default.yaml --seed 42

The YAML config sets path overrides (``NOMAD_ABM_DATA_DIR``,
``NOMAD_ABM_RESULTS_DIR``, ``NOMAD_ABM_CALIB_SHP``) via environment
variables before the model module is imported, so the path defaults
resolve correctly inside the model code without changes.
"""

import argparse
import os
import sys
from pathlib import Path

import yaml


def _apply_config(config_path):
    """Load a YAML config and translate path settings into env vars.

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


def _cmd_run(args):
    config = _apply_config(args.config)
    # Import AFTER env vars are set so the path constants resolve.
    from nomad_abm.model import run_model_opt  # noqa: E402

    run_cfg = config.get("run") or {}
    seed = args.seed if args.seed is not None else run_cfg.get("seed")
    run_model_opt(seed=seed)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="nomad-abm",
        description="Run the Nomad ABM (Iron Age IIA Negev Highlands).",
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
    run_p.set_defaults(func=_cmd_run)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
