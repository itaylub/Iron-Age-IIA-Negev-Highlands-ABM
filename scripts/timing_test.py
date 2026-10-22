"""Time 75-year replicates on this machine, alone and several at once.

Run from the repository root, in the model's environment:

    python scripts/timing_test.py

By default it runs four rounds: 1, 8, 12 and 16 replicates at the same
time, each replicate in its own process, all with the thesis best
weights. One round takes about as long as one replicate, a little longer
as more run together. It prints, and saves to ``summary.csv``:

- the time per replicate in each round;
- replicates per hour for the whole machine;
- what that means for a calibration of N trials x 10 replicates.

Pick the number of processes with the highest replicates per hour, and
pass it to ``scripts/calibrate.py --workers``.

Options:
    --workers 1 8 12 16   the rounds to run
    --years 75            run length
    --trials 200          calibration size used for the estimate

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
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abm_parallel as ap  # noqa: E402


def run_one(task):
    """One replicate with scoring, as in a calibration trial. Runs in a worker."""
    seed, years, out_dir = task
    import geopandas as gpd
    import matplotlib.pyplot as plt

    model = ap.import_model()
    perm, yearly, w = ap.normalised_weights(ap.THESIS_BEST)

    t0 = time.perf_counter()
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
    gdf_real = gpd.read_file(model.CALIB_SHP_PATH)
    gdf_model = model.to_gdf(sim)
    score, _ = model.obj_func(gdf_real, gdf_model, run_dir)
    plt.close("all")
    return seed, time.perf_counter() - t0, float(score)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--workers", type=int, nargs="+", default=[1, 8, 12, 16])
    parser.add_argument("--years", type=int, default=75)
    parser.add_argument("--trials", type=int, default=200)
    parser.add_argument("--replicates", type=int, default=10)
    args = parser.parse_args()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_root = os.path.join(ap.REPO_ROOT, "Results", f"timing_test_{stamp}")
    ap.set_environment(out_root)
    model = ap.import_model()

    with open(os.path.join(out_root, "machine.json"), "w") as f:
        json.dump({**ap.machine_info(), "git_commit": ap.git_commit(), "args": vars(args)}, f, indent=2)

    print(f"Logical CPUs: {os.cpu_count()}. Results: {out_root}")
    handles = ap.create_shared_data(model)
    ctx = mp.get_context("spawn")
    rows = []
    seed_base = 900000  # far from the calibration seeds (trial x 100 + i)
    try:
        for n in args.workers:
            out_dir = os.path.join(out_root, f"workers_{n}")
            tasks = [(seed_base + 1000 * n + k, args.years, out_dir) for k in range(n)]
            print(f"\nRound: {n} replicate(s) at once ...", flush=True)
            with ctx.Pool(processes=n, initializer=ap.init_worker) as pool:
                t0 = time.perf_counter()
                results = pool.map(run_one, tasks, chunksize=1)
                wall = time.perf_counter() - t0
            per_run = [r[1] for r in results]
            mean_run = sum(per_run) / len(per_run)
            per_hour = n / wall * 3600
            rows.append({
                "processes": n,
                "wall_min": round(wall / 60, 2),
                "mean_replicate_min": round(mean_run / 60, 2),
                "slowest_replicate_min": round(max(per_run) / 60, 2),
                "replicates_per_hour": round(per_hour, 1),
                "mean_score": round(sum(r[2] for r in results) / n, 4),
            })
            print(
                f"  {n:>2} at once: {mean_run / 60:.1f} min per replicate "
                f"(slowest {max(per_run) / 60:.1f}), {per_hour:.1f} replicates/hour",
                flush=True,
            )
    finally:
        ap.release_shared_data(handles)

    with open(os.path.join(out_root, "summary.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    best = max(rows, key=lambda r: r["replicates_per_hour"])
    total_reps = args.trials * args.replicates
    hours = total_reps / best["replicates_per_hour"]
    print("\nSummary")
    print(f"{'processes':>9} {'min/replicate':>14} {'replicates/hour':>16}")
    for r in rows:
        print(f"{r['processes']:>9} {r['mean_replicate_min']:>14} {r['replicates_per_hour']:>16}")
    print(
        f"\nFastest: {best['processes']} processes. A calibration of {args.trials} trials x "
        f"{args.replicates} replicates would take about {hours:.0f} h ({hours / 24:.1f} days) "
        f"without pruning; pruned trials stop early, so expect less."
    )
    print(f"Saved: {os.path.join(out_root, 'summary.csv')}")


if __name__ == "__main__":
    main()
