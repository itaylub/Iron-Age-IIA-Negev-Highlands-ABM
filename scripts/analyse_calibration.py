"""Check whether a calibration has settled, then re-run its leading weight sets.

Run from the repository root, in the model's environment, after
``scripts/calibrate.py`` has finished (it only reads the study):

    python scripts/analyse_calibration.py --results-dir D:/abm_runs/opt_fixed_2026_10

Step 1, settle check (always). Prints, and saves to ``analysis/``:
- best score so far after 50, 100, 150, ... completed trials, and how much
  it improved over the last 50 (compare with about 0.007, the accuracy
  of a 10-run mean);
- how many completed trials since the best score last improved;
- the leading distinct weight sets, and how much the leading 20 trials
  agree on each weight (mean and SD of the normalised weights);
- ``trials.csv``: every trial with its state, score and weights.

Step 2, re-run (with ``--rerun-top N``). Runs each of the N leading
distinct weight sets ``--replicates`` times (default 30) with fresh
seeds, in parallel, and ranks them by their mean. The best of these is
the calibrated model; its runs double as the 30 best-trial replicates.
Saves ``analysis/rerun_top<N>.csv`` (one row per weight set) and
``analysis/rerun_top<N>_runs.csv`` (one row per run, with the spatial
and site-type errors separately).

    python scripts/analyse_calibration.py --results-dir D:/abm_runs/opt_fixed_2026_10 --rerun-top 10 --workers 16

Don't run step 2 while a calibration or timing test is running: they
use the same shared-memory names.
"""

import argparse
import csv
import json
import multiprocessing as mp
import os
import statistics
import sys
import time
import traceback
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abm_parallel as ap  # noqa: E402

KEYS = ap.PERMANENT_KEYS + ap.YEARLY_KEYS


def say(msg=""):
    print(msg, flush=True)


def normalised(params):
    total = sum(params[k] for k in KEYS)
    return {k: (params[k] / total if total else 0.0) for k in KEYS}


# ---------------------------------------------------------------- step 1

def settle_check(study, out_dir, top_distinct):
    from optuna.trial import TrialState

    trials = sorted(study.trials, key=lambda t: t.number)
    states = {}
    for t in trials:
        states[t.state.name] = states.get(t.state.name, 0) + 1
    complete = [t for t in trials if t.state == TrialState.COMPLETE and t.value is not None]
    say(f"Trials: {states}")
    if not complete:
        say("No completed trials.")
        return []

    # All trials to CSV
    with open(os.path.join(out_dir, "trials.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["number", "state", "value", "started", "completed", "minutes"]
                   + [f"int_{k}" for k in KEYS] + [f"norm_{k}" for k in KEYS])
        for t in trials:
            p = t.params
            norm = normalised(p) if all(k in p for k in KEYS) else {}
            mins = ((t.datetime_complete - t.datetime_start).total_seconds() / 60
                    if t.datetime_complete and t.datetime_start else "")
            w.writerow([t.number, t.state.name, t.value, t.datetime_start, t.datetime_complete,
                        round(mins, 1) if mins != "" else ""]
                       + [p.get(k, "") for k in KEYS] + [round(norm[k], 4) if norm else "" for k in KEYS])

    # Best score so far, in trial order
    best, curve, last_improved = float("inf"), [], 0
    for i, t in enumerate(complete, start=1):
        if t.value < best - 1e-12:
            best, last_improved = t.value, i
        curve.append(best)
    n = len(complete)
    say(f"\nBest score so far, by completed trials (of {n}):")
    for k in list(range(50, n + 1, 50)) + ([n] if n % 50 else []):
        say(f"  after {k:>4}: {curve[k - 1]:.4f}")
    gain50 = curve[n - 51] - curve[-1] if n > 50 else float("nan")
    say(f"Improvement over the last 50 completed trials: {gain50:.4f} "
        f"(a 10-run mean is accurate to about 0.007)")
    say(f"Completed trials since the best score last improved: {n - last_improved}")

    # Leading distinct weight sets
    ranked = sorted(complete, key=lambda t: t.value)
    distinct, seen = [], set()
    for t in ranked:
        key = tuple(t.params[k] for k in KEYS)
        if key not in seen:
            seen.add(key)
            distinct.append(t)
    say(f"\nLeading {min(top_distinct, len(distinct))} distinct weight sets "
        f"(integers 0-7, in the order {', '.join(KEYS)}):")
    for r, t in enumerate(distinct[:top_distinct], start=1):
        same = sum(1 for x in complete if tuple(x.params[k] for k in KEYS) == tuple(t.params[k] for k in KEYS))
        say(f"  {r:>2}. trial {t.number:>4}  score {t.value:.4f}  "
            f"{[t.params[k] for k in KEYS]}  (tried {same}x)")

    # Agreement among the leading 20 trials
    lead = ranked[:20]
    say(f"\nNormalised weights in the leading {len(lead)} trials (mean ± SD):")
    agreement = {}
    for k in KEYS:
        vals = [normalised(t.params)[k] for t in lead]
        m = statistics.mean(vals)
        sd = statistics.stdev(vals) if len(vals) > 1 else 0.0
        agreement[k] = (m, sd)
        say(f"  {k:<18} {m:.3f} ± {sd:.3f}")

    summary = {
        "states": states, "completed": n, "best": curve[-1],
        "best_trial": ranked[0].number, "best_params": ranked[0].params,
        "improvement_last_50": gain50, "since_last_improvement": n - last_improved,
        "curve_every_50": {k: curve[k - 1] for k in range(50, n + 1, 50)},
        "leading20_mean_sd": agreement,
    }
    with open(os.path.join(out_dir, "settle_check.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)
    return distinct


# ---------------------------------------------------------------- step 2

def run_task(task):
    """One run of one weight set, with scoring. Runs in a worker; never raises."""
    rank, trial_no, int_weights, seed, years, out_dir, iteration = task
    t0 = time.perf_counter()
    try:
        import geopandas as gpd

        model = ap.import_model()
        perm, yearly, w = ap.normalised_weights(int_weights)
        sim, run_dir = model.run_model_opt(
            years, ras_wts=w, main_run_directory=out_dir,
            trial_number=trial_no, iteration=iteration,
            permanent_weights_dict=perm, yearly_weights_dict=yearly, seed=seed,
        )
        gdf_real = gpd.read_file(model.CALIB_SHP_PATH)
        total, ratio_error = model.obj_func(gdf_real, model.to_gdf(sim), run_dir)
        total, ratio_error = float(total), float(ratio_error)
        spatial_error = 2 * total - ratio_error  # total = (spatial + ratio) / 2
        return (rank, trial_no, seed, total, spatial_error, ratio_error,
                time.perf_counter() - t0, None)
    except Exception:
        return (rank, trial_no, seed, None, None, None,
                time.perf_counter() - t0, traceback.format_exc())


def rerun_top(distinct, n_top, replicates, years, workers, results_dir, out_dir, tag=""):
    chosen = distinct[:n_top]
    runs_dir = os.path.join(results_dir, f"rerun_top{n_top}{tag}")
    tasks = []
    for rank, t in enumerate(chosen, start=1):
        params = {k: t.params[k] for k in KEYS}
        for i in range(replicates):
            # Fresh seeds, far from the calibration's (trial x 100 + i)
            seed = 5_000_000 + rank * 1000 + i
            tasks.append((rank, t.number, params, seed, years, runs_dir, i))

    say(f"\nRe-running {len(chosen)} weight sets x {replicates} runs = {len(tasks)} runs "
        f"on {workers} processes, started {datetime.now():%H:%M:%S}")
    model = ap.import_model()
    say(ap.calib_line(ap.describe_calib(model)))
    handles = ap.create_shared_data(model)
    results, failed = [], []
    try:
        ctx = mp.get_context("spawn")
        with ctx.Pool(processes=workers, initializer=ap.init_worker) as pool:
            for j, r in enumerate(pool.imap_unordered(run_task, tasks, chunksize=1), start=1):
                (failed if r[7] else results).append(r)
                if j % workers == 0 or j == len(tasks):
                    say(f"  {j}/{len(tasks)} runs done ({datetime.now():%H:%M:%S})")
    finally:
        ap.release_shared_data(handles)

    if failed:
        say(f"\n{len(failed)} run(s) failed. First error:\n{failed[0][7]}")

    with open(os.path.join(out_dir, f"rerun_top{n_top}{tag}_runs.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank_in_calibration", "trial", "seed", "score", "spatial_error",
                    "site_type_error", "minutes"])
        for r in sorted(results):
            w.writerow([r[0], r[1], r[2], round(r[3], 5), round(r[4], 5), round(r[5], 5),
                        round(r[6] / 60, 2)])

    rows = []
    for rank, t in enumerate(chosen, start=1):
        mine = [r for r in results if r[0] == rank]
        if not mine:
            continue
        scores = [r[3] for r in mine]
        m = statistics.mean(scores)
        sd = statistics.stdev(scores) if len(scores) > 1 else 0.0
        norm = normalised(t.params)
        rows.append({
            "rank_in_calibration": rank, "trial": t.number,
            "calibration_score_10runs": round(t.value, 4),
            "runs": len(scores), "mean_score": round(m, 4), "sd": round(sd, 4),
            "se": round(sd / len(scores) ** 0.5, 4),
            "mean_spatial_error": round(statistics.mean(r[4] for r in mine), 4),
            "mean_site_type_error": round(statistics.mean(r[5] for r in mine), 4),
            **{f"int_{k}": t.params[k] for k in KEYS},
            **{f"norm_{k}": round(norm[k], 3) for k in KEYS},
        })
    rows.sort(key=lambda r: r["mean_score"])
    if not rows:
        say("No runs finished.")
        return
    with open(os.path.join(out_dir, f"rerun_top{n_top}{tag}.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    say(f"\nRanked by the mean of {replicates} fresh runs:")
    say(f"{'':>3} {'trial':>6} {'calib':>7} {'mean':>7} {'± se':>7} {'spatial':>8} {'site-type':>10}")
    for i, r in enumerate(rows, start=1):
        say(f"{i:>3} {r['trial']:>6} {r['calibration_score_10runs']:>7} {r['mean_score']:>7} "
            f"{r['se']:>7} {r['mean_spatial_error']:>8} {r['mean_site_type_error']:>10}")
    win = rows[0]
    say(f"\nCalibrated weights: trial {win['trial']}, mean {win['mean_score']} ± {win['sd']} (SD, "
        f"{win['runs']} runs)")
    say("  " + ", ".join(f"{k} {win[f'norm_{k}']}" for k in KEYS))
    if len(rows) > 1 and rows[1]["mean_score"] - win["mean_score"] < 2 * win["se"]:
        say("  Note: the runner-up is within two standard errors; the two are not clearly different.")
    say(f"Saved: {os.path.join(out_dir, f'rerun_top{n_top}{tag}.csv')}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--results-dir", required=True,
                        help="the calibration's folder (holds study.log)")
    parser.add_argument("--study-name", default=None,
                        help="default: the only study in <results-dir>/study.log")
    parser.add_argument("--top", type=int, default=10, help="distinct weight sets to list")
    parser.add_argument("--rerun-top", type=int, default=0,
                        help="re-run this many leading weight sets (0 = settle check only)")
    parser.add_argument("--replicates", type=int, default=30)
    parser.add_argument("--years", type=int, default=75)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--calib-shp", default=None,
                        help="score the re-runs against this file instead of the study's own target")
    args = parser.parse_args()

    results_dir = os.path.abspath(args.results_dir)
    out_dir = os.path.join(results_dir, "analysis")
    ap.set_environment(results_dir)
    os.makedirs(out_dir, exist_ok=True)

    import optuna

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = ap.load_study_in(results_dir, args.study_name)
    say(f"Study: {study.study_name}")
    stored = study.user_attrs.get("calib_shp")  # None for studies made before 24 Oct 2026
    ap.set_calib_shp(args.calib_shp or stored)
    tag = ""
    if args.calib_shp and (stored is None or
                           os.path.normcase(os.path.abspath(args.calib_shp)) != os.path.normcase(stored)):
        # Scoring against another target: keep these outputs apart from the study's own.
        tag = "_vs_" + os.path.splitext(os.path.basename(args.calib_shp))[0]
        say(f"Note: re-runs are scored against {args.calib_shp}, not the study's own target "
            f"({stored or 'the default Data/P_for_calib.shp'}). Outputs end in '{tag}'.")
    distinct = settle_check(study, out_dir, max(args.top, args.rerun_top))
    if args.rerun_top and distinct:
        rerun_top(distinct, args.rerun_top, args.replicates, args.years, args.workers,
                  results_dir, out_dir, tag)
    say(f"\nOutputs in {out_dir}")


if __name__ == "__main__":
    main()
