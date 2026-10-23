"""Time 75-year replicates on this machine, alone and several at once.

Run from the repository root, in the model's environment:

    python scripts/timing_test.py

By default it runs four rounds: 1, 8, 12 and 16 replicates at the same
time, all with the thesis best weights. The first round (1 replicate)
runs in this process, so any error shows directly; the others run each
replicate in its own process. One round takes about as long as one
replicate, a little longer as more run together. It prints, and saves to
``summary.csv``:

- the time per replicate in each round;
- replicates per hour for the whole machine;
- what that means for a calibration of N trials x 10 replicates.

Pick the number of processes with the highest replicates per hour, and
pass it to ``scripts/calibrate.py --workers``.

Options:
    --workers 1 8 12 16   the rounds to run
    --years 75            run length (use e.g. 5 for a one-minute check)
    --trials 200          calibration size used for the estimate
    --timeout 60          minutes before a round is given up as stalled

Outputs go to ``Results/timing_test_<date-time>/``. Don't run this while
a calibration is running: both use the same shared-memory names.
"""

import argparse
import csv
import json
import multiprocessing as mp
import os
import sys
import time
import traceback
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abm_parallel as ap  # noqa: E402


def say(msg):
    print(msg, flush=True)


def run_one(task):
    """One replicate with scoring, as in a calibration trial.

    Returns (seed, model minutes, total minutes, score, error text or None).
    Never raises, so one failure can't stall the round.
    """
    seed, years, out_dir = task
    t0 = time.perf_counter()
    t_model = None
    try:
        import geopandas as gpd

        model = ap.import_model()
        perm, yearly, w = ap.normalised_weights(ap.THESIS_BEST)
        sim, run_dir = model.run_model_opt(
            years,
            ras_wts=w,
            main_run_directory=out_dir,
            trial_number=0,
            iteration=seed,
            permanent_weights_dict=perm,
            yearly_weights_dict=yearly,
            seed=seed,
        )
        t_model = time.perf_counter() - t0
        say(f"    replicate {seed}: model done in {t_model / 60:.1f} min; scoring ...")
        gdf_real = gpd.read_file(model.CALIB_SHP_PATH)
        say(f"    replicate {seed}: read the sites shapefile ({len(gdf_real)} sites)")
        gdf_model = model.to_gdf(sim)
        say(f"    replicate {seed}: built the simulated sites ({len(gdf_model)} cells)")
        score, _ = model.obj_func(gdf_real, gdf_model, run_dir)
        total = time.perf_counter() - t0
        say(f"    replicate {seed}: scored {float(score):.3f}, {total / 60:.1f} min in all")
        return seed, t_model, total, float(score), None
    except Exception:
        return seed, t_model, time.perf_counter() - t0, None, traceback.format_exc()


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--workers", type=int, nargs="+", default=[1, 8, 12, 16])
    parser.add_argument("--years", type=int, default=75)
    parser.add_argument("--trials", type=int, default=200)
    parser.add_argument("--replicates", type=int, default=10)
    parser.add_argument("--timeout", type=float, default=60,
                        help="minutes before a round is given up as stalled")
    args = parser.parse_args()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_root = os.path.join(ap.REPO_ROOT, "Results", f"timing_test_{stamp}")
    ap.set_environment(out_root)
    model = ap.import_model()

    info = {**ap.machine_info(), "git_commit": ap.git_commit(), "args": vars(args),
            "GDAL_DATA": os.environ.get("GDAL_DATA"), "PROJ_DATA": os.environ.get("PROJ_DATA")}
    with open(os.path.join(out_root, "machine.json"), "w") as f:
        json.dump(info, f, indent=2)

    say(f"Logical CPUs: {os.cpu_count()}. Results: {out_root}")
    say(f"GDAL_DATA: {info['GDAL_DATA']}  PROJ_DATA: {info['PROJ_DATA']}")
    handles = ap.create_shared_data(model)
    ctx = mp.get_context("spawn")
    rows = []
    seed_base = 900000  # far from the calibration seeds (trial x 100 + i)
    try:
        for n in args.workers:
            out_dir = os.path.join(out_root, f"workers_{n}")
            tasks = [(seed_base + 1000 * n + k, args.years, out_dir) for k in range(n)]
            say(f"\nRound: {n} replicate(s) at once, started {datetime.now():%H:%M:%S}")
            t0 = time.perf_counter()
            if n == 1:
                ap.init_worker()
                results = [run_one(tasks[0])]
            else:
                pool = ctx.Pool(processes=n, initializer=ap.init_worker)
                try:
                    results = pool.map_async(run_one, tasks, chunksize=1).get(
                        timeout=args.timeout * 60)
                except mp.TimeoutError:
                    say(f"  Round of {n} still not finished after {args.timeout:.0f} min; "
                        "stopping. Check Task Manager: are the python.exe processes "
                        "using CPU (slow) or idle (stuck)?")
                    pool.terminate()
                    pool.join()
                    break
                pool.close()
                pool.join()
            wall = time.perf_counter() - t0

            errors = [r for r in results if r[4]]
            if errors:
                say(f"  {len(errors)} replicate(s) failed. First error:\n{errors[0][4]}")
                break

            per_run = [r[2] for r in results]
            mean_run = sum(per_run) / len(per_run)
            per_hour = n / wall * 3600
            rows.append({
                "processes": n,
                "wall_min": round(wall / 60, 2),
                "mean_replicate_min": round(mean_run / 60, 2),
                "slowest_replicate_min": round(max(per_run) / 60, 2),
                "mean_model_only_min": round(sum(r[1] for r in results) / n / 60, 2),
                "replicates_per_hour": round(per_hour, 1),
                "mean_score": round(sum(r[3] for r in results) / n, 4),
            })
            say(f"  {n:>2} at once: {mean_run / 60:.1f} min per replicate "
                f"(slowest {max(per_run) / 60:.1f}), {per_hour:.1f} replicates/hour")
    finally:
        ap.release_shared_data(handles)

    if not rows:
        say("\nNo round finished; nothing to summarise.")
        return

    with open(os.path.join(out_root, "summary.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    best = max(rows, key=lambda r: r["replicates_per_hour"])
    total_reps = args.trials * args.replicates
    hours = total_reps / best["replicates_per_hour"]
    say("\nSummary")
    say(f"{'processes':>9} {'min/replicate':>14} {'replicates/hour':>16}")
    for r in rows:
        say(f"{r['processes']:>9} {r['mean_replicate_min']:>14} {r['replicates_per_hour']:>16}")
    if args.years != 75:
        say(f"\n(Runs were {args.years} years, not 75: the estimate below is not meaningful.)")
    say(
        f"\nFastest: {best['processes']} processes. A calibration of {args.trials} trials x "
        f"{args.replicates} replicates would take about {hours:.0f} h ({hours / 24:.1f} days) "
        f"without pruning; pruned trials stop early, so expect less."
    )
    say(f"Saved: {os.path.join(out_root, 'summary.csv')}")


if __name__ == "__main__":
    main()
