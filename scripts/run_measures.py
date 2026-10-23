"""Measure the fit of one weight set run by run, against the record.

Re-runs a calibrated weight set with the same seeds as its re-evaluation
(``scripts/analyse_calibration.py --rerun-top``), so the runs are the
same ones; their scores are checked against the earlier ones as a test
of reproducibility. Run from the repository root, in the model's
environment:

    python scripts/run_measures.py --results-dir D:/abm_runs/opt_fixed_2026_10 --trial 209 --workers 16

For each run, and for the observed sites (``P_for_calib.shp``):
- sites: number, enclosed compounds, other sites, compound share, and
  the enclosed-to-other ratio (signed difference from the record);
- the standard-deviational ellipse as ``model.obj_func`` builds it
  (semi-axes = 2 SD): centre, semi-axes, area, axis ratio, orientation;
- overlap with the observed ellipse (IoU), centroid distance (mean and
  median centres);
- the composite score recomputed here and as ``model.obj_func`` gives it;
- the compound trajectory: per year, compound locations first built,
  reuse events, and cumulative locations.

Outputs in ``<results-dir>/analysis/measures_trial<N>/``:
``runs.csv`` (one row per run), ``summary.csv`` (mean, SD, min, max of
each measure, and the observed value), ``trajectory.csv`` (run x year),
``sites/`` (each run's simulated sites, x y value) and ``occupation/``
(each run's summed occupation raster, .npz).
"""

import argparse
import csv
import math
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
_GDF_REAL = None


def say(msg=""):
    print(msg, flush=True)


# ------------------------------------------------------------ geometry

def ellipse_params(xs, ys):
    """Standard-deviational ellipse exactly as model.obj_func computes it."""
    import numpy as np
    from scipy import linalg

    pts = np.column_stack([xs, ys]).astype(float)
    if len(pts) < 3:
        c = pts.mean(axis=0) if len(pts) else np.array([np.nan, np.nan])
        med = np.median(pts, axis=0) if len(pts) else c
        return {"cx": c[0], "cy": c[1], "medx": med[0], "medy": med[1],
                "a": 0.0, "b": 0.0, "rotation": 0.0}
    mean_center = pts.mean(axis=0)
    med_center = np.median(pts, axis=0)
    cov = np.cov(pts, rowvar=False)
    eigenvalues, eigenvectors = linalg.eigh(cov)
    idx = eigenvalues.argsort()[::-1]
    eigenvalues, eigenvectors = eigenvalues[idx], eigenvectors[:, idx]
    std_dev = np.sqrt(np.maximum(eigenvalues, 0)) * 2
    rotation = math.atan2(eigenvectors[1, 0], eigenvectors[0, 0])
    return {"cx": mean_center[0], "cy": mean_center[1], "medx": med_center[0],
            "medy": med_center[1], "a": float(std_dev[0]), "b": float(std_dev[1]),
            "rotation": rotation}


def ellipse_polygon(e, n=720):
    """Same shape as matplotlib Ellipse(width=2a, height=2b, angle=rotation)."""
    from shapely.geometry import Polygon

    ct, st = math.cos(e["rotation"]), math.sin(e["rotation"])
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x, y = e["a"] * math.cos(t), e["b"] * math.sin(t)
        pts.append((e["cx"] + x * ct - y * st, e["cy"] + x * st + y * ct))
    return Polygon(pts)


def site_measures(gdf):
    """Counts and ellipse for a GeoDataFrame of sites (value 1 other, 2 enclosed)."""
    xs, ys = gdf.geometry.x.values, gdf.geometry.y.values
    n_enc = int((gdf["value"] == 2).sum())
    n_oth = int((gdf["value"] == 1).sum())
    n = n_enc + n_oth
    e = ellipse_params(xs, ys)
    return {
        "sites": n, "enclosed": n_enc, "other": n_oth,
        "enclosed_share_pct": 100 * n_enc / n if n else float("nan"),
        "enclosed_to_other": n_enc / n_oth if n_oth else 0.0,
        "ellipse_area_km2": math.pi * e["a"] * e["b"] / 1e6,
        "semi_major_km": e["a"] / 1000, "semi_minor_km": e["b"] / 1000,
        "axis_ratio": e["a"] / e["b"] if e["b"] else float("nan"),
        "orientation_deg": math.degrees(e["rotation"]) % 180,
        "_ellipse": e,
    }


def compare(sim, obs):
    poly_s, poly_o = ellipse_polygon(sim["_ellipse"]), ellipse_polygon(obs["_ellipse"])
    union = poly_s.union(poly_o).area
    iou = poly_s.intersection(poly_o).area / union if union else 0.0
    es, eo = sim["_ellipse"], obs["_ellipse"]
    ratio_diff = sim["enclosed_to_other"] - obs["enclosed_to_other"]
    spatial = 1 - iou
    return {
        "iou": iou, "spatial_error": spatial,
        "ratio_diff_signed": ratio_diff, "site_type_error": abs(ratio_diff),
        "score_recomputed": (spatial + abs(ratio_diff)) / 2,
        "centroid_dist_km": math.hypot(es["cx"] - eo["cx"], es["cy"] - eo["cy"]) / 1000,
        "median_centre_dist_km": math.hypot(es["medx"] - eo["medx"], es["medy"] - eo["medy"]) / 1000,
    }


def trajectory(sim, years):
    """Per year: compound locations first built, reuse events, cumulative locations."""
    seen, rows = set(), []
    by_year = {y: [] for y in range(years + 1)}
    for pos, year, _agent in sim.enclosures:
        by_year.setdefault(year, []).append(tuple(pos))
    for y in sorted(by_year):
        new = reuse = 0
        for pos in by_year[y]:
            if pos in seen:
                reuse += 1
            else:
                seen.add(pos)
                new += 1
        rows.append((y, new, reuse, len(seen)))
    return rows


# ------------------------------------------------------------ worker

def run_task(task):
    seed, iteration, trial_no, int_weights, years, runs_dir, sites_dir, occ_dir = task
    global _GDF_REAL
    t0 = time.perf_counter()
    try:
        import geopandas as gpd
        import numpy as np

        model = ap.import_model()
        if _GDF_REAL is None:
            _GDF_REAL = gpd.read_file(model.CALIB_SHP_PATH)
        perm, yearly, w = ap.normalised_weights(int_weights)
        sim, run_dir = model.run_model_opt(
            years, ras_wts=w, main_run_directory=runs_dir, trial_number=trial_no,
            iteration=iteration, permanent_weights_dict=perm, yearly_weights_dict=yearly,
            seed=seed,
        )
        gdf_sim = model.to_gdf(sim)

        # Save the simulated sites and the summed occupation raster
        with open(os.path.join(sites_dir, f"run_{seed}.csv"), "w", newline="") as f:
            wr = csv.writer(f)
            wr.writerow(["x", "y", "value"])
            for x, y, v in zip(gdf_sim.geometry.x, gdf_sim.geometry.y, gdf_sim["value"]):
                wr.writerow([round(x, 2), round(y, 2), int(v)])
        np.savez_compressed(os.path.join(occ_dir, f"run_{seed}.npz"),
                            occupation=sum(sim.yearly_outputs))

        sim_m = site_measures(gdf_sim)
        obs_m = site_measures(_GDF_REAL)
        cmp_m = compare(sim_m, obs_m)
        total, _ = model.obj_func(_GDF_REAL.copy(), gdf_sim.copy(), run_dir)
        traj = trajectory(sim, years)

        row = {"seed": seed, "iteration": iteration}
        row.update({k: v for k, v in sim_m.items() if not k.startswith("_")})
        row.update(cmp_m)
        row["score_obj_func"] = float(total)
        locs = traj[-1][3] if traj else 0
        row["compound_locations"] = locs
        row["compound_events"] = sum(r[1] + r[2] for r in traj)
        row["locations_built_by_year_25"] = sum(r[1] for r in traj if r[0] <= 25)
        row["minutes"] = (time.perf_counter() - t0) / 60
        return row, traj, None
    except Exception:
        return {"seed": seed, "iteration": iteration}, [], traceback.format_exc()


# ------------------------------------------------------------ main

def load_trial_params(results_dir, study_name, trial_no):
    import optuna

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.load_study(study_name=study_name,
                              storage=ap.make_storage(os.path.join(results_dir, "study.log")))
    match = [t for t in study.trials if t.number == trial_no]
    if not match:
        raise SystemExit(f"Trial {trial_no} not found in study {study_name}.")
    return {k: match[0].params[k] for k in KEYS}


def earlier_seeds(compare_csv, trial_no):
    """Seeds and scores of this trial's runs in the re-evaluation, if available."""
    if not compare_csv or not os.path.exists(compare_csv):
        return {}
    out = {}
    with open(compare_csv, newline="") as f:
        for r in csv.DictReader(f):
            if int(r["trial"]) == trial_no:
                out[int(r["seed"])] = float(r["score"])
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--results-dir", required=True, help="the calibration's folder")
    parser.add_argument("--study-name", default="opt_fixed_2026_10")
    parser.add_argument("--trial", type=int, required=True)
    parser.add_argument("--compare-csv", default=None,
                        help="default: <results-dir>/analysis/rerun_top10_runs.csv")
    parser.add_argument("--replicates", type=int, default=30,
                        help="used only when the compare CSV has no seeds for this trial")
    parser.add_argument("--seed-base", type=int, default=7_000_000)
    parser.add_argument("--years", type=int, default=75)
    parser.add_argument("--workers", type=int, default=16)
    args = parser.parse_args()

    results_dir = os.path.abspath(args.results_dir)
    ap.set_environment(results_dir)
    out_dir = os.path.join(results_dir, "analysis", f"measures_trial{args.trial}")
    runs_dir, sites_dir, occ_dir = (os.path.join(out_dir, d) for d in ("runs", "sites", "occupation"))
    for d in (out_dir, runs_dir, sites_dir, occ_dir):
        os.makedirs(d, exist_ok=True)

    params = load_trial_params(results_dir, args.study_name, args.trial)
    compare_csv = args.compare_csv or os.path.join(results_dir, "analysis", "rerun_top10_runs.csv")
    earlier = earlier_seeds(compare_csv, args.trial)
    seeds = sorted(earlier) if earlier else [args.seed_base + i for i in range(args.replicates)]
    say(f"Trial {args.trial}, weights {params}")
    say(f"{len(seeds)} runs, seeds {seeds[0]}-{seeds[-1]}"
        + (" (same as the re-evaluation)" if earlier else " (new)"))

    tasks = [(s, i, args.trial, params, args.years, runs_dir, sites_dir, occ_dir)
             for i, s in enumerate(seeds)]
    model = ap.import_model()
    handles = ap.create_shared_data(model)
    rows, trajs, failed = [], {}, []
    say(f"Started {datetime.now():%H:%M:%S} on {args.workers} processes")
    try:
        ctx = mp.get_context("spawn")
        with ctx.Pool(processes=args.workers, initializer=ap.init_worker) as pool:
            for j, (row, traj, err) in enumerate(
                    pool.imap_unordered(run_task, tasks, chunksize=1), start=1):
                if err:
                    failed.append((row["seed"], err))
                else:
                    rows.append(row)
                    trajs[row["seed"]] = traj
                if j % args.workers == 0 or j == len(tasks):
                    say(f"  {j}/{len(tasks)} runs done ({datetime.now():%H:%M:%S})")
    finally:
        ap.release_shared_data(handles)

    if failed:
        say(f"\n{len(failed)} run(s) failed. First error:\n{failed[0][1]}")
    if not rows:
        return
    rows.sort(key=lambda r: r["iteration"])

    # Reproducibility check against the re-evaluation
    if earlier:
        diffs = [abs(r["score_obj_func"] - earlier[r["seed"]]) for r in rows if r["seed"] in earlier]
        for r in rows:
            r["score_earlier"] = earlier.get(r["seed"], "")
        same = sum(d < 1e-4 for d in diffs)
        say(f"\nReproducibility: {same} of {len(diffs)} runs gave the same score as in the "
            f"re-evaluation (largest difference {max(diffs):.5f}).")

    fields = list(rows[0].keys())
    with open(os.path.join(out_dir, "runs.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 5) if isinstance(v, float) else v) for k, v in r.items()})

    with open(os.path.join(out_dir, "trajectory.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["seed", "year", "locations_built", "reuse_events", "cumulative_locations"])
        for s in sorted(trajs):
            for y, new, reuse, cum in trajs[s]:
                w.writerow([s, y, new, reuse, cum])

    # Observed values and summary
    import geopandas as gpd

    obs = site_measures(gpd.read_file(model.CALIB_SHP_PATH))
    measures = ["sites", "enclosed", "other", "enclosed_share_pct", "enclosed_to_other",
                "ratio_diff_signed", "site_type_error", "ellipse_area_km2", "semi_major_km",
                "semi_minor_km", "axis_ratio", "orientation_deg", "iou", "spatial_error",
                "centroid_dist_km", "median_centre_dist_km", "score_recomputed",
                "score_obj_func", "compound_locations", "compound_events",
                "locations_built_by_year_25"]
    summary = []
    for m in measures:
        vals = [r[m] for r in rows if isinstance(r[m], (int, float)) and not math.isnan(r[m])]
        if not vals:
            continue
        summary.append({
            "measure": m, "mean": round(statistics.mean(vals), 4),
            "sd": round(statistics.stdev(vals), 4) if len(vals) > 1 else 0,
            "min": round(min(vals), 4), "max": round(max(vals), 4),
            "observed": round(obs[m], 4) if m in obs and not m.startswith("_") else "",
        })
    with open(os.path.join(out_dir, "summary.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["measure", "mean", "sd", "min", "max", "observed"])
        w.writeheader()
        w.writerows(summary)

    say(f"\n{'measure':<28}{'simulated mean ± SD':>24}{'range':>22}{'observed':>12}")
    for s in summary:
        say(f"{s['measure']:<28}{s['mean']:>14} ± {s['sd']:<8}"
            f"{str(s['min']) + '-' + str(s['max']):>21}{str(s['observed']):>12}")
    n_years = args.years
    mean_cum = {}
    for traj in trajs.values():
        for y, _new, _re, cum in traj:
            mean_cum.setdefault(y, []).append(cum)
    marks = [y for y in (5, 10, 25, 50, n_years) if y in mean_cum]
    say("\nCompound locations, mean cumulative across runs: "
        + ", ".join(f"year {y}: {statistics.mean(mean_cum[y]):.1f}" for y in marks))
    say(f"\nOutputs in {out_dir}")


if __name__ == "__main__":
    main()
