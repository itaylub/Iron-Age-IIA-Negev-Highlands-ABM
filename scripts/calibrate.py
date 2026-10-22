"""Run the Optuna calibration with several processes on one shared study.

Same objective, search space, pruner and replicates as
``Code/calibration.ipynb`` (``model.objective``), but each trial runs in
its own process, so trials don't wait for each other. Run from the
repository root, in the model's environment:

    python scripts/calibrate.py --workers 12 --trials 200

What it does:
- creates (or continues) the study ``--study-name`` in
  ``Results/<study-name>/study.log`` (an Optuna journal file);
- on a new study, queues the thesis best trial (173) as the first trial,
  and optionally the leading trials of the thesis study (``--warm-start-db``);
- starts ``--workers`` processes; each takes the next trial from the study
  until ``--trials`` trials are complete or pruned;
- writes replicate outputs to ``Results/<study-name>/run/trial_<n>/iter_<i>/``
  and the settings to ``Results/<study-name>/run_settings.json``.

Stopping and restarting: Ctrl+C stops all processes. Run the same
command again to continue the same study. Finished trials are kept;
trials cut off mid-run are not counted toward ``--trials``.

For the notebook's analysis cells, copy the study to SQLite:

    python scripts/calibrate.py --export-sqlite

which writes ``Results/<study-name>/opt_run.db``.

Settings changed from the thesis run (record them in the ODD):
- separate processes instead of threads;
- TPE with ``constant_liar=True``, so processes running at the same
  time don't all try the same weights;
- journal storage instead of SQLite (SQLite can lock under many writers).
"""

import argparse
import json
import multiprocessing as mp
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abm_parallel as ap  # noqa: E402


def make_sampler():
    import optuna

    return optuna.samplers.TPESampler(constant_liar=True)


def make_pruner():
    import optuna

    return optuna.pruners.MedianPruner(n_startup_trials=10, n_warmup_steps=5)


def worker(worker_id, storage_path, study_name, n_trials, n_iter, years):
    """One process: take trials from the shared study until enough are done."""
    import optuna
    from optuna.study import MaxTrialsCallback
    from optuna.trial import TrialState

    model = ap.import_model()
    model.ensure_data_loaded()
    storage = ap.make_storage(storage_path)
    study = optuna.load_study(
        study_name=study_name, storage=storage,
        sampler=make_sampler(), pruner=make_pruner(),
    )
    print(f"[worker {worker_id}] started (pid {os.getpid()})", flush=True)
    study.optimize(
        lambda trial: model.objective(trial, sim_y=years, n_iter=n_iter),
        n_trials=None,
        callbacks=[MaxTrialsCallback(n_trials, states=(TrialState.COMPLETE, TrialState.PRUNED))],
        catch=(Exception,),  # a failed trial is recorded; the worker goes on
    )
    print(f"[worker {worker_id}] finished", flush=True)


def enqueue_warm_start(study, args):
    queued = [dict(ap.THESIS_BEST)]
    if args.warm_start_db:
        import optuna
        from optuna.trial import TrialState

        old = optuna.load_study(
            study_name=args.warm_start_study,
            storage="sqlite:///" + os.path.abspath(args.warm_start_db),
        )
        done = [t for t in old.trials if t.state == TrialState.COMPLETE and t.value is not None]
        done.sort(key=lambda t: t.value)
        for t in done[: args.warm_start_top]:
            if t.params not in queued:
                queued.append(dict(t.params))
    for params in queued:
        study.enqueue_trial(params, skip_if_exists=True)
    print(f"Queued {len(queued)} warm-start trial(s) from the thesis calibration.")
    return queued


def export_sqlite(storage_path, study_name, results_dir):
    import optuna

    target = os.path.join(results_dir, "opt_run.db")
    optuna.copy_study(
        from_study_name=study_name,
        from_storage=ap.make_storage(storage_path),
        to_storage="sqlite:///" + target,
    )
    print(f"Copied study '{study_name}' to {target}")


def main():
    parser = argparse.ArgumentParser(description="Parallel Optuna calibration of the Nomad ABM.")
    parser.add_argument("--study-name", default="opt_fixed_2026_10")
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--trials", type=int, default=200,
                        help="stop when this many trials are complete or pruned")
    parser.add_argument("--replicates", type=int, default=10)
    parser.add_argument("--years", type=int, default=75)
    parser.add_argument("--results-dir", default=None,
                        help="default: Results/<study-name> in the repository")
    parser.add_argument("--no-warm-start", action="store_true")
    parser.add_argument("--warm-start-db", default=None,
                        help="path to the thesis opt_run.db, to also queue its leading trials")
    parser.add_argument("--warm-start-study", default="opt_2_26_v1")
    parser.add_argument("--warm-start-top", type=int, default=19)
    parser.add_argument("--export-sqlite", action="store_true",
                        help="copy the study to opt_run.db and exit")
    args = parser.parse_args()

    results_dir = os.path.abspath(
        args.results_dir or os.path.join(ap.REPO_ROOT, "Results", args.study_name)
    )
    ap.set_environment(results_dir)
    storage_path = os.path.join(results_dir, "study.log")

    import optuna

    if args.export_sqlite:
        export_sqlite(storage_path, args.study_name, results_dir)
        return

    storage = ap.make_storage(storage_path)
    study = optuna.create_study(
        study_name=args.study_name, storage=storage, direction="minimize",
        load_if_exists=True, sampler=make_sampler(), pruner=make_pruner(),
    )
    is_new = len(study.trials) == 0
    queued = enqueue_warm_start(study, args) if (is_new and not args.no_warm_start) else []
    if not is_new:
        print(f"Continuing study '{args.study_name}' ({len(study.trials)} trials so far).")

    settings = {
        "started": datetime.now().isoformat(timespec="seconds"),
        "study_name": args.study_name,
        "storage": storage_path,
        "results_dir": results_dir,
        "workers": args.workers,
        "trials_target": args.trials,
        "replicates_per_trial": args.replicates,
        "years": args.years,
        "seeds": "trial.number * 100 + replicate (model.objective_function)",
        "sampler": "TPESampler(constant_liar=True)",
        "pruner": "MedianPruner(n_startup_trials=10, n_warmup_steps=5)",
        "search_space": "integer weights 0-7 for the seven layers (model.objective)",
        "warm_start": queued,
        "git_commit": ap.git_commit(),
        **ap.machine_info(),
    }
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(os.path.join(results_dir, f"run_settings_{stamp}.json"), "w") as f:
        json.dump(settings, f, indent=2)

    model = ap.import_model()
    handles = ap.create_shared_data(model)
    ctx = mp.get_context("spawn")
    procs = []
    try:
        for i in range(args.workers):
            p = ctx.Process(
                target=worker,
                args=(i, storage_path, args.study_name, args.trials, args.replicates, args.years),
            )
            p.start()
            procs.append(p)
        print(f"Started {args.workers} worker processes. Results: {results_dir}")
        for p in procs:
            p.join()
    except KeyboardInterrupt:
        print("Stopping workers ...")
        for p in procs:
            p.terminate()
        for p in procs:
            p.join()
    finally:
        ap.release_shared_data(handles)

    study = optuna.load_study(study_name=args.study_name, storage=ap.make_storage(storage_path))
    complete = [t for t in study.trials if t.value is not None]
    if complete:
        print(f"Best value: {study.best_value:.4f}  (trial {study.best_trial.number})")
        print(f"Best params: {study.best_params}")


if __name__ == "__main__":
    main()
