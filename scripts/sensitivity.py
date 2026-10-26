"""Sensitivity tests of a calibrated weight set, run in parallel.

Runs ``Code/sensitivity_model.py`` (``model.py`` plus the switches
``num_agents`` and ``fixed_territory``) with one trial's weights, and
scores every run against the study's own target. Run from the
repository root, in the model's environment:

    python scripts/sensitivity.py --results-dir D:/abm_runs/opt_fixed_strict_2026_10 --study-name opt_fixed_strict_2026_10 --trial 197 --test check --workers 16

Tests (``--test``: one or more, or ``all``):
- ``check``: the default switches with the trial's re-evaluation seeds.
  Scores, sites and compounds must equal the re-evaluation's
  (``analysis/rerun_top10_runs.csv``, ``analysis/measures_trial<N>/runs.csv``),
  which shows that this file runs the calibrated model.
- ``null``: equal weights (all 1, so 1/7 each) against the trial's weights.
- ``horizon``: runs of ``--horizon-years`` (150). Every year: the number of
  sites at each threshold from 0.1 to 1.0, compounds, compound building
  and reuse. Every ``--checkpoint-every`` years (10) and at year 75: the
  score and all measures.
- ``households``: ``--households`` households (5, 9, 15, 20).
- ``territory``: flexible (calibrated) against fixed territories.
- ``threshold``: the site threshold from 0.1 to 1.0 on saved runs, by
  default those of ``run_measures.py`` (``analysis/measures_trial<N>/``).
  No new runs.

All tests but ``check`` and ``threshold`` use the seeds ``--seed-base`` + i
(8,000,000 + i), the same in every arm, and re-run the calibrated arm
(the trial's weights, the default number of households, flexible
territory, 75 years), so each table stands on its own. An arm differs
from the calibrated arm when the 95% confidence interval of the paired
mean difference excludes zero.

Outputs in ``<results-dir>/sensitivity/<test>/``:
- ``settings_<time>.json``: weights, target, seeds, arms, commit, machine;
- ``runs.csv`` (one row per run), ``summary.csv`` (mean, SD, min, max of
  each measure per arm), ``comparison.csv`` (paired differences from the
  calibrated arm), ``trajectory.csv`` (compound building and reuse, run x
  year), ``calibrated_arm.csv`` (for the check across tests);
- ``<arm>/sites/``, ``<arm>/occupation/``, ``<arm>/enclosures/``: each
  run's simulated sites at 0.6, summed occupation raster (.npz) and
  compound events (cell, year, household);
- ``results/``: one JSON file per run. A run with a result file is not
  run again, so a stopped test continues where it stopped.
The horizon test adds ``yearly.csv``, ``checkpoints.csv``,
``checkpoints_summary.csv``, ``targets.csv`` (years to the record's
number of sites and compounds, at each threshold) and ``blocks.csv``
(building and reuse per 25 years); its occupation files hold the raster
at each checkpoint. The threshold test writes ``thresholds.csv`` and
``thresholds_summary.csv``.

Rebuild a test's tables from its saved results, without running:

    python scripts/sensitivity.py ... --test null --summarise-only

Don't run this while a calibration or another of these scripts is
running: they use the same shared-memory names.
"""

import argparse
import csv
import glob
import inspect
import json
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
import run_measures as rm  # noqa: E402

KEYS = ap.PERMANENT_KEYS + ap.YEARLY_KEYS
EQUAL_WEIGHTS = {k: 1 for k in KEYS}
THRESHOLDS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
SITE_THRESHOLD = 0.6  # model.to_gdf, as in the calibration
RUN_TESTS = ["check", "null", "horizon", "households", "territory"]
ALL_TESTS = RUN_TESTS + ["threshold"]
REFERENCE = "calibrated"
TITLES = {
    "check": "Check: the sensitivity model with the default switches against the re-evaluation",
    "null": "Null baseline: equal weights against the calibrated weights",
    "horizon": "Time horizon",
    "households": "Number of households",
    "territory": "Territory: flexible against fixed",
    "threshold": "Site threshold",
}

# Summarised per arm (runs.csv has every column)
MEASURES = [
    "score", "spatial_error", "site_type_error", "iou", "sites", "enclosed", "other",
    "enclosed_share_pct", "enclosed_to_other", "ratio_diff_signed", "ellipse_area_km2",
    "semi_major_km", "semi_minor_km", "axis_ratio", "orientation_deg", "centroid_dist_km",
    "median_centre_dist_km", "score_recomputed", "compound_locations", "compound_events",
    "locations_built_by_year_25", "households_end", "households_ever", "minutes",
]
# Printed per arm: (measure, heading, format)
SHOWN = [
    ("score", "score", ".4f"), ("spatial_error", "spatial error", ".3f"),
    ("site_type_error", "site-type error", ".3f"), ("iou", "IoU", ".3f"),
    ("sites", "sites", ".1f"), ("enclosed", "compounds", ".1f"),
    ("enclosed_share_pct", "compound share %", ".1f"), ("axis_ratio", "axis ratio", ".2f"),
    ("orientation_deg", "orientation", ".0f"), ("centroid_dist_km", "centroid km", ".1f"),
    ("compound_locations", "locations", ".1f"),
    ("locations_built_by_year_25", "built by year 25", ".1f"),
    ("households_ever", "households ever", ".1f"), ("minutes", "minutes", ".1f"),
]
# Paired differences from the calibrated arm
COMPARED = ["score", "spatial_error", "site_type_error", "sites", "enclosed",
            "enclosed_share_pct", "axis_ratio", "centroid_dist_km", "compound_locations"]

_GDF_REAL = None
_OBS = None


def say(msg=""):
    print(msg, flush=True)


# ------------------------------------------------------------ model and sites

def import_sm():
    if ap.CODE_DIR not in sys.path:
        sys.path.insert(0, ap.CODE_DIR)
    import sensitivity_model  # noqa: E402  (Code/sensitivity_model.py)
    return sensitivity_model


def init_worker():
    """Run once in each worker process: connect to the shared data."""
    import_sm().ensure_data_loaded()


def worker_setup():
    """The model module and the observed sites, read once per process."""
    global _GDF_REAL, _OBS
    import geopandas as gpd

    sm = import_sm()
    if _GDF_REAL is None:
        _GDF_REAL = gpd.read_file(sm.CALIB_SHP_PATH)
        _OBS = rm.site_measures(_GDF_REAL)
    return sm


def grid_origin(sm):
    """Lower-left corner and cell size (m) that model.to_gdf uses."""
    p = inspect.signature(sm.to_gdf).parameters
    return p["lower_left_x"].default, p["lower_left_y"].default, p["cell_size"].default


def classify(occ, enc_mask, threshold):
    """Site raster as model.to_gdf builds it: 0 none, 1 other site, 2 compound.

    Cells whose summed occupation reaches the threshold are sites; compound
    cells are compounds whatever their occupation.
    """
    yo = occ.copy()
    yo[yo < threshold] = 0
    yo[yo > 0] = 1
    yo[enc_mask] = 2
    return yo


def sites_gdf(yo, origin):
    """Points of a classified raster, in the order and coordinates of model.to_gdf."""
    import geopandas as gpd
    import numpy as np
    from shapely.geometry import Point

    llx, lly, cell = origin
    rc = np.argwhere(yo > 0)
    vals = yo[yo > 0]
    xs = llx + rc[:, 1] * cell
    ys = lly + (yo.shape[0] - 1 - rc[:, 0]) * cell
    return gpd.GeoDataFrame({"geometry": [Point(x, y) for x, y in zip(xs, ys)], "value": vals},
                            crs="EPSG:2039")


def score_row(sm, gdf_sim, run_dir):
    """The calibration score (model.obj_func) and the fit measures of run_measures.py."""
    total, ratio_error = sm.obj_func(_GDF_REAL.copy(), gdf_sim.copy(), run_dir)
    total, ratio_error = float(total), float(ratio_error)
    sim_m = rm.site_measures(gdf_sim)
    row = {k: v for k, v in sim_m.items() if not k.startswith("_")}
    cmp_m = rm.compare(sim_m, _OBS)
    for k in ("iou", "ratio_diff_signed", "centroid_dist_km", "median_centre_dist_km",
              "score_recomputed"):
        row[k] = cmp_m[k]
    row["score"] = total
    row["spatial_error"] = 2 * total - ratio_error  # total = (spatial + site-type) / 2
    row["site_type_error"] = ratio_error
    return row


def households_ever(sim):
    """Households that lived at some point in the run (from the data collector)."""
    try:
        df = sim.datacollector.get_agent_vars_dataframe()
        names = list(df.index.names)
        level = names.index("AgentID") if "AgentID" in names else len(names) - 1
        return int(df.index.get_level_values(level).nunique())
    except Exception:
        return None


def _json_default(o):
    if hasattr(o, "tolist"):
        return o.tolist()
    if hasattr(o, "item"):
        return o.item()
    return str(o)


def write_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, default=_json_default)
    os.replace(tmp, path)  # never leave a half-written result file


# ------------------------------------------------------------ worker: one run

def run_task(task):
    """One run of one arm: run, score, save. Runs in a worker; never raises."""
    t0 = time.perf_counter()
    arm, seed = task["arm"], task["seed"]
    label = f"{task['test']} / {arm['name']} / seed {seed}"
    try:
        import numpy as np

        sm = worker_setup()
        perm, yearly, w = ap.normalised_weights(arm["weights"])
        years = arm["years"]
        sim, run_dir = sm.run_model_opt(
            years, ras_wts=w, main_run_directory=task["runs_dir"], trial_number=arm["name"],
            iteration=task["iteration"], permanent_weights_dict=perm, yearly_weights_dict=yearly,
            seed=seed, num_agents=arm["num_agents"], fixed_territory=arm["fixed_territory"],
        )
        gdf_sim = sm.to_gdf(sim)

        row = {"test": task["test"], "arm": arm["name"], "seed": seed,
               "iteration": task["iteration"], "years": years,
               "households_start": int(sim.num_agents),
               "fixed_territory": arm["fixed_territory"]}
        row.update(score_row(sm, gdf_sim, run_dir))
        traj = rm.trajectory(sim, years)
        row["compound_locations"] = traj[-1][3] if traj else 0
        row["compound_events"] = sum(r[1] + r[2] for r in traj)
        row["locations_built_by_year_25"] = sum(r[1] for r in traj if r[0] <= 25)
        row["households_end"] = len(sim.agents)
        row["households_ever"] = households_ever(sim)

        # Each run's sites at 0.6 and compound events
        arm_dir = task["arm_dir"]
        with open(os.path.join(arm_dir, "sites", f"run_{seed}.csv"), "w", newline="") as f:
            wr = csv.writer(f)
            wr.writerow(["x", "y", "value"])
            for x, y, v in zip(gdf_sim.geometry.x, gdf_sim.geometry.y, gdf_sim["value"]):
                wr.writerow([round(x, 2), round(y, 2), int(v)])
        with open(os.path.join(arm_dir, "enclosures", f"run_{seed}.csv"), "w", newline="") as f:
            wr = csv.writer(f)
            wr.writerow(["mesa_x", "mesa_y", "year", "household"])
            for pos, year, agent in sim.enclosures:
                wr.writerow([pos[0], pos[1], year, getattr(agent, "unique_id", "")])

        result = {"row": row, "trajectory": traj, "git_commit": task["git_commit"]}
        occ_path = os.path.join(arm_dir, "occupation", f"run_{seed}.npz")
        if task["test"] == "horizon":
            yearly_rows, checkpoints, match = horizon_series(sm, sim, task, run_dir, gdf_sim, occ_path)
            row["to_gdf_match"] = match
            result["yearly"] = yearly_rows
            result["checkpoints"] = checkpoints
        else:
            np.savez_compressed(occ_path, occupation=sum(sim.yearly_outputs))
        row["minutes"] = (time.perf_counter() - t0) / 60
        write_json(task["result_path"], result)
        return label, None
    except Exception:
        return label, traceback.format_exc()


def horizon_series(sm, sim, task, run_dir, gdf_final, occ_path):
    """Year by year: sites at each threshold, compounds, building and reuse;
    at the checkpoints, the score and all measures.

    The occupation is summed in the order model.to_gdf sums it, so the sites
    after n years are exactly those a run of n years would give (the first
    75 years of a run don't depend on its length).
    """
    import numpy as np

    years = task["arm"]["years"]
    seed = task["seed"]
    checkpoints = set(task["checkpoints"])
    origin = grid_origin(sm)
    traj = {y: (new, reuse, cum) for y, new, reuse, cum in rm.trajectory(sim, years)}
    enc_in_year = {}
    for pos, year, _agent in sim.enclosures:
        enc_in_year.setdefault(year, []).append(pos)
    enc_mask = np.zeros(sim.yearly_outputs[0].shape, dtype=bool)
    occ = 0
    yearly, ckpts, stack, ck_years = [], [], [], []
    events = 0
    for n, out in enumerate(sim.yearly_outputs, start=1):  # n = years run so far
        occ = occ + out
        for mx, my in enc_in_year.get(n - 1, []):
            enc_mask[sm.to_numpy_y(sim, my), mx] = True
        n_enc = int(enc_mask.sum())
        new, reuse, cum = traj.get(n - 1, (0, 0, 0))
        events += new + reuse
        rec = {"seed": seed, "year": n, "enclosed": n_enc, "cumulative_locations": cum,
               "locations_built": new, "reuse_events": reuse}
        for t in THRESHOLDS:
            rec[f"sites_t{t:.1f}"] = int(np.count_nonzero((occ >= t) & ~enc_mask)) + n_enc
        yearly.append(rec)
        if n in checkpoints:
            ck_dir = os.path.join(run_dir, f"year_{n}")
            os.makedirs(ck_dir, exist_ok=True)
            ck = {"seed": seed, "year": n}
            ck.update(score_row(sm, sites_gdf(classify(occ, enc_mask, SITE_THRESHOLD), origin), ck_dir))
            ck["compound_locations"] = cum
            ck["compound_events"] = events
            ckpts.append(ck)
            stack.append(occ.copy())
            ck_years.append(n)
    np.savez_compressed(occ_path, years=np.array(ck_years), occupation=np.stack(stack))

    # The last year rebuilt this way must be model.to_gdf's own result
    final = sites_gdf(classify(occ, enc_mask, SITE_THRESHOLD), origin)
    match = bool(len(final) == len(gdf_final)
                 and np.array_equal(final.geometry.x.values, gdf_final.geometry.x.values)
                 and np.array_equal(final.geometry.y.values, gdf_final.geometry.y.values)
                 and np.array_equal(final["value"].values, gdf_final["value"].values))
    return yearly, ckpts, match


# ------------------------------------------------------------ worker: threshold

def threshold_task(task):
    """Re-classify one saved run at each threshold and score it. Never raises."""
    seed = task["seed"]
    try:
        import numpy as np

        sm = worker_setup()
        origin = grid_origin(sm)
        llx, lly, cell = origin
        with np.load(task["occupation"]) as d:
            occ = d["occupation"]
        if occ.ndim == 3:  # a horizon run: its last checkpoint
            occ = occ[-1]
        occ = occ.astype(np.float64)
        enc_mask = np.zeros(occ.shape, dtype=bool)
        saved = set()
        with open(task["sites"], newline="") as f:
            for r in csv.DictReader(f):
                col = int(round((float(r["x"]) - llx) / cell))
                row = occ.shape[0] - 1 - int(round((float(r["y"]) - lly) / cell))
                v = int(float(r["value"]))
                saved.add((row, col, v))
                if v == 2:
                    enc_mask[row, col] = True
        rows = []
        for t in THRESHOLDS:
            yo = classify(occ, enc_mask, t)
            run_dir = os.path.join(task["runs_dir"], f"run_{seed}", f"t_{t:.1f}")
            os.makedirs(run_dir, exist_ok=True)
            r = {"seed": seed, "threshold": t}
            r.update(score_row(sm, sites_gdf(yo, origin), run_dir))
            if abs(t - SITE_THRESHOLD) < 1e-9:
                mine = {(int(a), int(b), int(yo[a, b])) for a, b in np.argwhere(yo > 0)}
                r["matches_saved_sites"] = mine == saved
            rows.append(r)
        write_json(task["result_path"], {"rows": rows, "git_commit": task["git_commit"]})
        return f"threshold / seed {seed}", None
    except Exception:
        return f"threshold / seed {seed}", traceback.format_exc()


# ------------------------------------------------------------ statistics, tables

def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and not math.isnan(v)


def stats(values):
    vals = [v for v in values if _num(v)]
    if not vals:
        return None
    return {"n": len(vals), "mean": statistics.mean(vals),
            "sd": statistics.stdev(vals) if len(vals) > 1 else 0.0,
            "min": min(vals), "max": max(vals)}


def t975(df):
    try:
        from scipy import stats as sps

        return float(sps.t.ppf(0.975, df))
    except Exception:
        return 1.96


def paired(ref_rows, arm_rows, measure):
    """Mean difference arm - reference over runs with the same seed, with its 95% CI."""
    ref = {r["seed"]: r.get(measure) for r in ref_rows if _num(r.get(measure))}
    diffs = [r[measure] - ref[r["seed"]] for r in arm_rows
             if r["seed"] in ref and _num(r.get(measure))]
    if len(diffs) < 2:
        return None
    m, sd, n = statistics.mean(diffs), statistics.stdev(diffs), len(diffs)
    half = t975(n - 1) * sd / math.sqrt(n)
    ref_mean = statistics.mean(ref[r["seed"]] for r in arm_rows if r["seed"] in ref and _num(r.get(measure)))
    return {"n_pairs": n, "reference_mean": ref_mean, "arm_mean": ref_mean + m,
            "mean_diff": m, "sd_diff": sd, "ci_low": m - half, "ci_high": m + half,
            "differs": (m - half > 0) or (m + half < 0)}


def write_csv(path, rows, fields=None, digits=6):
    if not rows:
        return
    if fields is None:
        fields = []
        for r in rows:
            for k in r:
                if k not in fields:
                    fields.append(k)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, restval="", extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, digits) if digits is not None and isinstance(v, float) else v)
                        for k, v in r.items()})


def fmt_st(st, spec):
    """mean ± SD"""
    if not st:
        return "-"
    return format(st["mean"], spec) + " ± " + format(st["sd"], spec)


def fmt_ms(st, spec):
    """mean (SD)"""
    if not st:
        return "-"
    return format(st["mean"], spec) + " (" + format(st["sd"], spec) + ")"


def fmt_m(st, spec):
    """mean"""
    return format(st["mean"], spec) if st else "-"


def print_arm_table(arms, rows_by_arm):
    cols = [a for a in arms if rows_by_arm.get(a["name"])]
    if not cols:
        return
    width = max(20, max(len(a["name"]) for a in cols) + 2)
    say(f"  {'':<18}" + "".join(f"{a['name']:>{width}}" for a in cols))
    for m, head, spec in SHOWN:
        cells = [fmt_st(stats([r.get(m) for r in rows_by_arm[a["name"]]]), spec) for a in cols]
        if all(c == "-" for c in cells):
            continue
        say(f"  {head:<18}" + "".join(f"{c:>{width}}" for c in cells))
    say("  (mean ± SD over " + ", ".join(f"{len(rows_by_arm[a['name']])} {a['name']}" for a in cols)
        + " runs)")
    for a in cols:
        say(f"    {a['name']}: {a['label']}")


def print_comparison(arms, comp):
    others = [a["name"] for a in arms if a["name"] != REFERENCE and any(c["arm"] == a["name"] for c in comp)]
    if not others:
        return
    say(f"\n  Paired difference from the {REFERENCE} arm, mean (95% CI); * = the CI excludes zero:")
    width = 34
    say(f"  {'':<18}" + "".join(f"{o:>{width}}" for o in others))
    for m in COMPARED:
        cells = []
        for o in others:
            c = next((c for c in comp if c["arm"] == o and c["measure"] == m), None)
            if c is None:
                cells.append("-")
                continue
            spec = "+.4f" if m in ("score", "spatial_error", "site_type_error") else "+.2f"
            cells.append(format(c["mean_diff"], spec) + " (" + format(c["ci_low"], spec) + " to "
                         + format(c["ci_high"], spec) + ")" + (" *" if c["differs"] else "  "))
        say(f"  {m:<18}" + "".join(f"{c:>{width}}" for c in cells))


# ------------------------------------------------------------ arms, seeds, tasks

def make_arms(test, params, n_default, households, horizon_years):
    cal = {"name": REFERENCE, "label": f"trial weights, {n_default} households, flexible territory, 75 years",
           "weights": dict(params), "num_agents": None, "fixed_territory": False, "years": 75}

    def variant(name, label, **changes):
        a = dict(cal, name=name, label=label)
        a.update(changes)
        return a

    if test == "check":
        return [dict(cal, label=cal["label"] + ", re-evaluation seeds")]
    if test == "null":
        return [cal, variant("equal_weights", "equal weights (all 1, so 1/7 each)", weights=dict(EQUAL_WEIGHTS))]
    if test == "horizon":
        return [variant(f"years_{horizon_years}", f"trial weights, {n_default} households, "
                        f"flexible territory, {horizon_years} years", years=horizon_years)]
    if test == "households":
        arms = [dict(cal, label=f"{n} households (calibrated)") if n == n_default
                else variant(f"households_{n}", f"{n} households", num_agents=n)
                for n in sorted(set(households) | {n_default})]
        return arms
    if test == "territory":
        return [dict(cal, label="flexible territory (calibrated)"),
                variant("fixed_territory", "fixed territory: camp and territory as in year 0; "
                        "a failed household restarts in place", fixed_territory=True)]
    raise ValueError(test)


def result_path(test_dir, arm_name, seed):
    return os.path.join(test_dir, "results", f"{arm_name}__{seed}.json")


def checkpoint_years(years, every):
    marks = set(range(every, years + 1, every)) if every > 0 else set()
    if years >= 75:
        marks.add(75)  # the calibrated run length
    marks.add(years)
    return sorted(marks)


def write_settings(test_dir, test, args, results_dir, params, calib, arms, seeds, extra=None):
    _perm, _yearly, w = ap.normalised_weights(params)
    settings = {
        "started": datetime.now().isoformat(timespec="seconds"),
        "test": test,
        "study_name": args.study_name,
        "results_dir": results_dir,
        "trial": args.trial,
        "weights_int": {k: params[k] for k in KEYS},
        "weights_normalised": {k: round(float(v), 4) for k, v in zip(KEYS, w)},
        "model_file": "Code/sensitivity_model.py",
        "calibration_sites": calib,
        "site_threshold": SITE_THRESHOLD,
        "arms": arms,
        "seeds": seeds,
        "seed_rule": ("the trial's re-evaluation seeds" if test == "check"
                      else "seed_base + i, the same in every arm"),
        "workers": args.workers,
        "git_commit": ap.git_commit(),
        **ap.machine_info(),
        **(extra or {}),
    }
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(os.path.join(test_dir, f"settings_{stamp}.json"), "w") as f:
        json.dump(settings, f, indent=2, default=_json_default)


def make_tasks(test, arms, seeds, test_dir, checkpoints, n_default, commit, overwrite):
    tasks, done = [], 0
    os.makedirs(os.path.join(test_dir, "results"), exist_ok=True)
    for arm in arms:
        arm_dir = os.path.join(test_dir, arm["name"])
        for sub in ("sites", "occupation", "enclosures"):
            os.makedirs(os.path.join(arm_dir, sub), exist_ok=True)
        for i, seed in enumerate(seeds):
            path = result_path(test_dir, arm["name"], seed)
            if os.path.exists(path) and not overwrite:
                done += 1
                continue
            cost = arm["years"] / 75 * (arm["num_agents"] or n_default) / n_default
            tasks.append({"test": test, "arm": arm, "seed": seed, "iteration": i,
                          "runs_dir": os.path.join(test_dir, "runs"), "arm_dir": arm_dir,
                          "result_path": path, "checkpoints": checkpoints,
                          "git_commit": commit, "cost": cost})
    return tasks, done


def run_pool(tasks, workers, func, shared_model=None):
    """Run tasks in worker processes; with shared_model, load the data into shared memory first."""
    if not tasks:
        return []
    tasks = sorted(tasks, key=lambda t: -t.get("cost", 1))  # longest first
    n_proc = min(workers, len(tasks))
    say(f"{len(tasks)} runs on {n_proc} processes, started {datetime.now():%H:%M:%S}")
    handles = ap.create_shared_data(shared_model) if shared_model is not None else []
    failed = []
    try:
        ctx = mp.get_context("spawn")
        init = init_worker if shared_model is not None else None
        with ctx.Pool(processes=n_proc, initializer=init) as pool:
            for j, (label, err) in enumerate(pool.imap_unordered(func, tasks, chunksize=1), start=1):
                if err:
                    failed.append((label, err))
                if j % workers == 0 or j == len(tasks):
                    say(f"  {j}/{len(tasks)} runs done ({datetime.now():%H:%M:%S})")
    finally:
        ap.release_shared_data(handles)
    if failed:
        say(f"\n{len(failed)} run(s) failed; run the same command again to retry them. "
            f"First error ({failed[0][0]}):\n{failed[0][1]}")
    return failed


def load_results(test_dir, arms, seeds):
    out, missing = {}, 0
    for a in arms:
        out[a["name"]] = []
        for s in seeds:
            p = result_path(test_dir, a["name"], s)
            if os.path.exists(p):
                with open(p) as f:
                    out[a["name"]].append(json.load(f))
            else:
                missing += 1
    return out, missing


# ------------------------------------------------------------ summaries

def summarise_runs(test, test_dir, arms, results):
    """runs.csv, summary.csv, comparison.csv, trajectory.csv; printed tables."""
    rows_by_arm = {a["name"]: [r["row"] for r in results[a["name"]]] for a in arms}
    rows = [r for a in arms for r in rows_by_arm[a["name"]]]
    if not rows:
        say("  No results yet.")
        return rows_by_arm, []
    write_csv(os.path.join(test_dir, "runs.csv"), rows)

    traj_rows = []
    for a in arms:
        for res in results[a["name"]]:
            for y, new, reuse, cum in res["trajectory"]:
                traj_rows.append({"arm": a["name"], "seed": res["row"]["seed"], "year": y,
                                  "locations_built": new, "reuse_events": reuse,
                                  "cumulative_locations": cum})
    write_csv(os.path.join(test_dir, "trajectory.csv"), traj_rows)

    summary = []
    for a in arms:
        for m in MEASURES:
            st = stats([r.get(m) for r in rows_by_arm[a["name"]]])
            if st:
                summary.append({"arm": a["name"], "label": a["label"], "measure": m, **st})
    write_csv(os.path.join(test_dir, "summary.csv"), summary)

    comp = []
    ref_rows = rows_by_arm.get(REFERENCE, [])
    for a in arms:
        if a["name"] == REFERENCE or not ref_rows:
            continue
        for m in COMPARED:
            p = paired(ref_rows, rows_by_arm[a["name"]], m)
            if p:
                comp.append({"arm": a["name"], "measure": m, **p})
    write_csv(os.path.join(test_dir, "comparison.csv"), comp)

    print_arm_table(arms, rows_by_arm)
    print_comparison(arms, comp)

    commits = {res.get("git_commit") for a in arms for res in results[a["name"]]}
    if len(commits) > 1:
        say(f"  Note: these runs come from {len(commits)} commits: {', '.join(sorted(map(str, commits)))}")
    return rows_by_arm, comp


def write_calibrated_arm(test_dir, rows):
    """Seed, score (full precision), sites, compounds: compared across tests."""
    write_csv(os.path.join(test_dir, "calibrated_arm.csv"),
              [{"seed": r["seed"], "score": repr(float(r["score"])), "sites": r["sites"],
                "enclosed": r["enclosed"]} for r in rows],
              fields=["seed", "score", "sites", "enclosed"], digits=None)


def read_calibrated_arm(path):
    if not os.path.exists(path):
        return {}
    with open(path, newline="") as f:
        return {int(r["seed"]): r for r in csv.DictReader(f)}


def cross_check(base_out, test):
    mine = read_calibrated_arm(os.path.join(base_out, test, "calibrated_arm.csv"))
    if not mine:
        return
    for other in ("null", "horizon", "households", "territory"):
        if other == test:
            continue
        theirs = read_calibrated_arm(os.path.join(base_out, other, "calibrated_arm.csv"))
        common = sorted(set(mine) & set(theirs))
        if not common:
            continue
        same = sum(float(mine[s]["score"]) == float(theirs[s]["score"])
                   and int(mine[s]["sites"]) == int(theirs[s]["sites"])
                   and int(mine[s]["enclosed"]) == int(theirs[s]["enclosed"]) for s in common)
        say(f"  Check across tests: the calibrated runs equal the '{other}' test's in {same} of "
            f"{len(common)} runs (score, sites, compounds).")


def reevaluation_mean(results_dir, trial):
    path = os.path.join(results_dir, "analysis", "rerun_top10.csv")
    if not os.path.exists(path):
        return None
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            if int(r["trial"]) == trial:
                return float(r["mean_score"]), float(r["sd"]), int(r["runs"])
    return None


def summarise_check(test_dir, rows, results_dir, trial):
    compare_csv = os.path.join(results_dir, "analysis", "rerun_top10_runs.csv")
    earlier = rm.earlier_seeds(compare_csv, trial)
    measures_csv = os.path.join(results_dir, "analysis", f"measures_trial{trial}", "runs.csv")
    saved = {}
    if os.path.exists(measures_csv):
        with open(measures_csv, newline="") as f:
            saved = {int(r["seed"]): r for r in csv.DictReader(f)}
    out, same_score, same_counts, n_counts, diffs = [], 0, 0, 0, []
    for r in sorted(rows, key=lambda r: r["seed"]):
        e, m = earlier.get(r["seed"]), saved.get(r["seed"])
        rec = {"seed": r["seed"], "score": r["score"], "score_reevaluation": e,
               "sites": r["sites"], "enclosed": r["enclosed"]}
        if e is not None:
            d = abs(r["score"] - e)
            diffs.append(d)
            same_score += d < 1e-5  # rerun_top10_runs.csv keeps 5 decimals
        if m is not None:
            rec["sites_saved"] = int(float(m["sites"]))
            rec["enclosed_saved"] = int(float(m["enclosed"]))
            n_counts += 1
            same_counts += rec["sites_saved"] == r["sites"] and rec["enclosed_saved"] == r["enclosed"]
        out.append(rec)
    write_csv(os.path.join(test_dir, "check.csv"), out)
    say(f"\n  Scores equal the re-evaluation's ({os.path.basename(compare_csv)}) in {same_score} of "
        f"{len(diffs)} runs" + (f"; largest difference {max(diffs):.6f}." if diffs else "."))
    if n_counts:
        say(f"  Sites and compounds equal measures_trial{trial}\\runs.csv in {same_counts} of {n_counts} runs.")
    ok = diffs and same_score == len(diffs) == len(rows) and (not n_counts or same_counts == n_counts)
    say("  PASSED: with the default switches, sensitivity_model.py runs the calibrated model."
        if ok else "  NOT PASSED: the sensitivity model does not reproduce these runs; stop and check.")


def summarise_null(test_dir, rows_by_arm, results_dir, trial):
    cal = stats([r["score"] for r in rows_by_arm.get(REFERENCE, [])])
    null = stats([r["score"] for r in rows_by_arm.get("equal_weights", [])])
    if not cal or not null:
        return
    head = {"null_mean": null["mean"], "null_sd": null["sd"], "null_runs": null["n"],
            "calibrated_mean": cal["mean"], "calibrated_sd": cal["sd"], "calibrated_runs": cal["n"],
            "reduction_pct_vs_calibrated_arm": 100 * (null["mean"] - cal["mean"]) / null["mean"]}
    say(f"\n  Reduction in error, (null - calibrated) / null: "
        f"{head['reduction_pct_vs_calibrated_arm']:.1f}% against the calibrated arm (same seeds).")
    ree = reevaluation_mean(results_dir, trial)
    if ree:
        head.update({"reevaluation_mean": ree[0], "reevaluation_sd": ree[1], "reevaluation_runs": ree[2],
                     "reduction_pct_vs_reevaluation": 100 * (null["mean"] - ree[0]) / null["mean"]})
        say(f"  {head['reduction_pct_vs_reevaluation']:.1f}% against trial {trial}'s re-evaluation mean "
            f"({ree[0]:.4f} ± {ree[1]:.4f}, {ree[2]} runs; analysis\\rerun_top10.csv).")
        say(f"  The calibrated arm on these fresh seeds: {cal['mean']:.4f} ± {cal['sd']:.4f}.")
    with open(os.path.join(test_dir, "headline.json"), "w") as f:
        json.dump(head, f, indent=2)


def summarise_horizon(test_dir, arm, results, calib):
    yearly = [rec for res in results for rec in res.get("yearly", [])]
    ckpts = [rec for res in results for rec in res.get("checkpoints", [])]
    if not yearly:
        return
    write_csv(os.path.join(test_dir, "yearly.csv"), yearly)
    write_csv(os.path.join(test_dir, "checkpoints.csv"), ckpts)
    n_runs = len(results)
    last = max(rec["year"] for rec in yearly)

    # Score and measures at each checkpoint
    ck_years = sorted({c["year"] for c in ckpts})
    ck_summary = []
    for y in ck_years:
        at = [c for c in ckpts if c["year"] == y]
        for m in MEASURES:
            st = stats([c.get(m) for c in at])
            if st:
                ck_summary.append({"year": y, "measure": m, **st})
    write_csv(os.path.join(test_dir, "checkpoints_summary.csv"), ck_summary)

    def ck(y, m):
        return next((s for s in ck_summary if s["year"] == y and s["measure"] == m), None)

    say(f"\n  At each checkpoint (mean over {n_runs} runs; SD in brackets), threshold {SITE_THRESHOLD}:")
    say(f"  {'year':>5}{'score':>16}{'spatial':>9}{'site-type':>10}{'sites':>13}{'compounds':>11}"
        f"{'share %':>9}{'IoU':>7}{'axis':>7}{'centre km':>10}")
    for y in ck_years:
        cells = [fmt_ms(ck(y, "score"), ".4f").rjust(16),
                 fmt_m(ck(y, "spatial_error"), ".3f").rjust(9),
                 fmt_m(ck(y, "site_type_error"), ".3f").rjust(10),
                 fmt_ms(ck(y, "sites"), ".0f").rjust(13),
                 fmt_m(ck(y, "enclosed"), ".1f").rjust(11),
                 fmt_m(ck(y, "enclosed_share_pct"), ".1f").rjust(9),
                 fmt_m(ck(y, "iou"), ".3f").rjust(7),
                 fmt_m(ck(y, "axis_ratio"), ".2f").rjust(7),
                 fmt_m(ck(y, "centroid_dist_km"), ".1f").rjust(10)]
        say("  " + str(y).rjust(5) + "".join(cells))

    # Years to the record's site and compound counts
    by_seed = {}
    for rec in yearly:
        by_seed.setdefault(rec["seed"], []).append(rec)
    for recs in by_seed.values():
        recs.sort(key=lambda r: r["year"])
    by_year = {}
    for rec in yearly:
        by_year.setdefault(rec["year"], []).append(rec)
    all_years = sorted(by_year)

    def target_row(key, observed, threshold):
        firsts = []
        for recs in by_seed.values():
            firsts.append(next((r["year"] for r in recs if r[key] >= observed), None))
        reached = [f for f in firsts if f is not None]
        mean_by_year = {y: statistics.mean(r[key] for r in by_year[y]) for y in all_years}
        curve = next((y for y in all_years if mean_by_year[y] >= observed), None)
        st = stats(reached)
        return {"measure": key, "observed": observed, "threshold": threshold,
                "runs": len(firsts), "runs_reaching": len(reached),
                "first_year_mean": st["mean"] if st else "", "first_year_sd": st["sd"] if st else "",
                "first_year_min": st["min"] if st else "", "first_year_max": st["max"] if st else "",
                "year_mean_count_reaches": curve if curve is not None else "",
                "mean_at_year_75": mean_by_year.get(75, ""), "mean_at_last_year": mean_by_year[last]}

    targets = [target_row(f"sites_t{t:.1f}", calib["sites"], t) for t in THRESHOLDS]
    targets.append(target_row("enclosed", calib["enclosed"], ""))
    write_csv(os.path.join(test_dir, "targets.csv"), targets)
    say(f"\n  Years to the record ({calib['sites']} sites, {calib['enclosed']} compounds), "
        f"first year a run reaches it:")
    say("  " + "".ljust(16) + "runs reaching".rjust(15) + "first year: mean ± SD (range)".rjust(34)
        + "mean count, year 75".rjust(21) + ("year " + str(last)).rjust(10))
    for t in targets:
        if t["measure"] == "enclosed":
            name = "compounds"
        else:
            name = "sites at " + format(t["threshold"], ".1f")
        if t["runs_reaching"]:
            fy = (format(t["first_year_mean"], ".1f") + " ± " + format(t["first_year_sd"], ".1f")
                  + " (" + str(t["first_year_min"]) + "-" + str(t["first_year_max"]) + ")")
        else:
            fy = "-"
        y75 = t["mean_at_year_75"]
        y75 = format(y75, ".0f") if y75 != "" else "-"
        reach = str(t["runs_reaching"]) + "/" + str(t["runs"])
        say("  " + name.ljust(16) + reach.rjust(15) + fy.rjust(34) + y75.rjust(21)
            + format(t["mean_at_last_year"], ".0f").rjust(10))

    # Building and reuse per 25 years
    blocks = []
    for start in range(0, last, 25):
        end = min(start + 25, last)
        new, reuse = [], []
        for res in results:
            tr = [r for r in res["trajectory"] if start <= r[0] < end]
            new.append(sum(r[1] for r in tr))
            reuse.append(sum(r[2] for r in tr))
        sn, sr = stats(new), stats(reuse)
        blocks.append({"years": f"{start + 1}-{end}", "new_locations_mean": sn["mean"],
                       "new_locations_sd": sn["sd"], "reuse_events_mean": sr["mean"],
                       "reuse_events_sd": sr["sd"]})
    write_csv(os.path.join(test_dir, "blocks.csv"), blocks)
    say("\n  Compound building and reuse per 25 years (mean ± SD per run):")
    say(f"  {'years':<10}{'new locations':>18}{'reuse events':>18}")
    for b in blocks:
        say(f"  {b['years']:<10}{b['new_locations_mean']:>11.1f} ± {b['new_locations_sd']:<4.1f}"
            f"{b['reuse_events_mean']:>11.1f} ± {b['reuse_events_sd']:<4.1f}")

    match = [res["row"].get("to_gdf_match") for res in results]
    say(f"\n  Check: the last year rebuilt from the yearly rasters equals model.to_gdf in "
        f"{sum(bool(m) for m in match)} of {len(match)} runs.")
    # Year 75 is the calibrated run: keep it for the check across tests
    at75 = [c for c in ckpts if c["year"] == 75]
    if at75:
        write_calibrated_arm(test_dir, at75)


def summarise_threshold(out_dir, results, src):
    rows = [r for res in results for r in res["rows"]]
    if not rows:
        say("  No results yet.")
        return
    write_csv(os.path.join(out_dir, "thresholds.csv"), rows)
    summary = []
    for t in THRESHOLDS:
        at = [r for r in rows if abs(r["threshold"] - t) < 1e-9]
        for m in MEASURES:
            st = stats([r.get(m) for r in at])
            if st:
                summary.append({"threshold": t, "measure": m, **st})
    write_csv(os.path.join(out_dir, "thresholds_summary.csv"), summary)

    def s(t, m):
        return next((x for x in summary if abs(x["threshold"] - t) < 1e-9 and x["measure"] == m), None)

    n_runs = len(results)
    say(f"\n  By threshold (mean over {n_runs} runs; SD in brackets):")
    say(f"  {'thr.':>5}{'sites':>14}{'other':>8}{'compounds':>11}{'share %':>9}{'score':>16}"
        f"{'spatial':>9}{'site-type':>10}{'IoU':>7}{'axis':>7}")
    for t in THRESHOLDS:
        if not s(t, "sites"):
            continue
        cells = [fmt_ms(s(t, "sites"), ".0f").rjust(14),
                 fmt_m(s(t, "other"), ".0f").rjust(8),
                 fmt_m(s(t, "enclosed"), ".1f").rjust(11),
                 fmt_m(s(t, "enclosed_share_pct"), ".1f").rjust(9),
                 fmt_ms(s(t, "score"), ".4f").rjust(16),
                 fmt_m(s(t, "spatial_error"), ".3f").rjust(9),
                 fmt_m(s(t, "site_type_error"), ".3f").rjust(10),
                 fmt_m(s(t, "iou"), ".3f").rjust(7),
                 fmt_m(s(t, "axis_ratio"), ".2f").rjust(7)]
        say("  " + format(t, ".1f").rjust(5) + "".join(cells))

    # Check at 0.6: the saved runs must come back unchanged
    at06 = [r for r in rows if abs(r["threshold"] - SITE_THRESHOLD) < 1e-9]
    same_sites = sum(bool(r.get("matches_saved_sites")) for r in at06)
    say(f"\n  Check at {SITE_THRESHOLD}: sites equal the saved site files in {same_sites} of {len(at06)} runs.")
    saved_runs = os.path.join(src, "runs.csv")
    if os.path.exists(saved_runs):
        with open(saved_runs, newline="") as f:
            saved = {int(r["seed"]): float(r["score_obj_func"]) for r in csv.DictReader(f)
                     if r.get("score_obj_func")}
        common = [r for r in at06 if r["seed"] in saved]
        same = sum(abs(r["score"] - saved[r["seed"]]) < 1e-5 for r in common)  # runs.csv keeps 5 decimals
        say(f"  Scores equal {saved_runs} in {same} of {len(common)} runs.")


# ------------------------------------------------------------ main

def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--results-dir", required=True, help="the calibration's folder (holds study.log)")
    parser.add_argument("--study-name", required=True)
    parser.add_argument("--trial", type=int, required=True, help="the calibrated weight set")
    parser.add_argument("--test", nargs="+", required=True, choices=ALL_TESTS + ["all"])
    parser.add_argument("--replicates", type=int, default=30)
    parser.add_argument("--seed-base", type=int, default=8_000_000)
    parser.add_argument("--households", type=int, nargs="+", default=[5, 9, 15, 20])
    parser.add_argument("--horizon-years", type=int, default=150)
    parser.add_argument("--checkpoint-every", type=int, default=10)
    parser.add_argument("--threshold-source", default=None,
                        help="folder with sites/ and occupation/ of saved runs "
                             "(default: <results-dir>/analysis/measures_trial<N>)")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--out-dir", default=None, help="default: <results-dir>/sensitivity")
    parser.add_argument("--summarise-only", action="store_true",
                        help="rebuild the tables from saved results; run nothing")
    parser.add_argument("--overwrite", action="store_true",
                        help="run again the runs that already have a result file")
    args = parser.parse_args()

    tests = ALL_TESTS if "all" in args.test else [t for t in ALL_TESTS if t in args.test]
    results_dir = os.path.abspath(args.results_dir)
    base_out = os.path.abspath(args.out_dir or os.path.join(results_dir, "sensitivity"))
    ap.set_environment(results_dir)
    params, stored = rm.load_trial_params(results_dir, args.study_name, args.trial)
    if stored is None:
        say("Note: the study records no target; the model's default Data/P_for_calib.shp is used.")
    ap.set_calib_shp(stored)
    sm = import_sm()
    calib = ap.describe_calib(sm)
    say(ap.calib_line(calib))
    say(f"Trial {args.trial}, integer weights {[params[k] for k in KEYS]} ({', '.join(KEYS)})")
    n_default = sm.Num_agents()
    commit = ap.git_commit()
    say(f"Model: Code/sensitivity_model.py; commit {commit[:7]}; outputs in {base_out}")

    new_seeds = [args.seed_base + i for i in range(args.replicates)]
    if any(t in tests for t in ("null", "horizon", "households", "territory")):
        if any(s < 100_000 or 5_000_000 <= s < 5_011_000 for s in new_seeds):
            raise SystemExit("These seeds overlap the calibration's (trial x 100 + i) or the "
                             "re-evaluation's (5,001,000+); choose another --seed-base.")
        say(f"Seeds {new_seeds[0]}-{new_seeds[-1]}, the same in every arm")

    # Model runs: all chosen tests in one pool, longest runs first
    plans, tasks = {}, []
    for test in [t for t in RUN_TESTS if t in tests]:
        if test == "check":
            seeds = sorted(rm.earlier_seeds(
                os.path.join(results_dir, "analysis", "rerun_top10_runs.csv"), args.trial))
            if not seeds:
                raise SystemExit(f"No re-evaluation runs of trial {args.trial} in "
                                 f"{os.path.join(results_dir, 'analysis', 'rerun_top10_runs.csv')}.")
        else:
            seeds = new_seeds
        arms = make_arms(test, params, n_default, args.households, args.horizon_years)
        test_dir = os.path.join(base_out, test)
        os.makedirs(test_dir, exist_ok=True)
        ck = checkpoint_years(args.horizon_years, args.checkpoint_every) if test == "horizon" else []
        plans[test] = (arms, seeds, test_dir)
        if args.summarise_only:
            continue
        mine, done = make_tasks(test, arms, seeds, test_dir, ck, n_default, commit, args.overwrite)
        extra = {"checkpoints": ck, "thresholds_counted_yearly": THRESHOLDS} if test == "horizon" else None
        write_settings(test_dir, test, args, results_dir, params, calib, arms, seeds, extra)
        say(f"{test}: {len(arms)} arm(s) x {len(seeds)} runs"
            + (f"; {done} already done" if done else ""))
        tasks += mine
    if tasks:
        run_pool(tasks, args.workers, run_task, shared_model=sm)

    for test, (arms, seeds, test_dir) in plans.items():
        say(f"\n==== {TITLES[test]} ({test_dir}) ====")
        results, missing = load_results(test_dir, arms, seeds)
        if missing:
            say(f"  {missing} of {len(arms) * len(seeds)} runs have no result yet; the tables use the rest.")
        if test == "horizon":
            arm = arms[0]
            summarise_runs(test, test_dir, arms, results)
            summarise_horizon(test_dir, arm, results[arm["name"]], calib)
        else:
            rows_by_arm, _comp = summarise_runs(test, test_dir, arms, results)
            if test == "check":
                summarise_check(test_dir, rows_by_arm.get(REFERENCE, []), results_dir, args.trial)
            else:
                write_calibrated_arm(test_dir, rows_by_arm.get(REFERENCE, []))
            if test == "null":
                summarise_null(test_dir, rows_by_arm, results_dir, args.trial)
        if test != "check":
            cross_check(base_out, test)

    # Site threshold: saved runs only
    if "threshold" in tests:
        src = os.path.abspath(args.threshold_source or os.path.join(
            results_dir, "analysis", f"measures_trial{args.trial}"))
        name = "threshold" if not args.threshold_source else "threshold_" + os.path.basename(os.path.normpath(src))
        out_dir = os.path.join(base_out, name)
        os.makedirs(os.path.join(out_dir, "results"), exist_ok=True)
        th_tasks, seeds = [], []
        for p in sorted(glob.glob(os.path.join(src, "sites", "run_*.csv"))):
            seed = int(os.path.basename(p)[len("run_"):-len(".csv")])
            occ_p = os.path.join(src, "occupation", f"run_{seed}.npz")
            if not os.path.exists(occ_p):
                say(f"  No occupation raster for seed {seed}; skipped.")
                continue
            seeds.append(seed)
            res_p = os.path.join(out_dir, "results", f"run_{seed}.json")
            if os.path.exists(res_p) and not args.overwrite:
                continue
            th_tasks.append({"seed": seed, "sites": p, "occupation": occ_p,
                             "runs_dir": os.path.join(out_dir, "runs"), "result_path": res_p,
                             "git_commit": commit})
        if not seeds:
            raise SystemExit(f"No saved runs (sites/run_*.csv with occupation/run_*.npz) in {src}")
        if not args.summarise_only:
            th_settings = {
                "started": datetime.now().isoformat(timespec="seconds"), "test": "threshold",
                "study_name": args.study_name, "trial": args.trial, "source": src, "seeds": seeds,
                "thresholds": THRESHOLDS, "calibration_sites": calib, "model_file": "Code/sensitivity_model.py",
                "git_commit": commit, **ap.machine_info(),
            }
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(os.path.join(out_dir, f"settings_{stamp}.json"), "w") as f:
                json.dump(th_settings, f, indent=2, default=_json_default)
            say(f"\nthreshold: {len(seeds)} saved runs from {src}")
            run_pool(th_tasks, args.workers, threshold_task)
        say(f"\n==== {TITLES['threshold']} ({out_dir}) ====")
        results = []
        for s in seeds:
            p = os.path.join(out_dir, "results", f"run_{s}.json")
            if os.path.exists(p):
                with open(p) as f:
                    results.append(json.load(f))
        summarise_threshold(out_dir, results, src)

    say(f"\nOutputs in {base_out}")


if __name__ == "__main__":
    main()
