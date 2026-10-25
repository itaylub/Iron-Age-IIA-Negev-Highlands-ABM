"""The thesis plots, redrawn with the new data.

The plotting code of ``Code/calibration.ipynb`` and
``Code/sensitivity_analysis.ipynb``, unchanged in form (plot type, figure
size, titles, labels, matplotlib and seaborn defaults), reading the saved
outputs of ``calibrate.py``, ``run_measures.py`` and ``sensitivity.py``.
Run from the repository root, in the model's environment:

    python scripts/plot_thesis_figures.py --results-dir D:/abm_runs/opt_fixed_strict_2026_10 --study-name opt_fixed_strict_2026_10 --trial 197

Writes to ``<results-dir>/figures_thesis/`` (``--only`` to choose):

From ``calibration.ipynb``:
- ``optimization_history``, ``param_importances``, ``slice``: Optuna's plotly
  plots, as ``.html`` (interactive; its camera button saves a PNG) and as
  ``.png`` when plotly can export images (kaleido). The export runs in a
  separate process with a time limit, so a stuck exporter cannot stall the
  script;
- ``best_trial_dynamics``: households, livestock, surplus and prosperity
  across the calibrated trial's 30 runs (``household_data.csv`` of each run of
  ``run_measures.py``).

From ``sensitivity_analysis.ipynb``:
- ``time_horizon``: total, spatial and ratio error every 10 years over 150
  years, here the mean of the 30 runs (the thesis plotted one run);
- ``households``: score by number of households (box plot);
- ``territory``: score, flexible against fixed (box plot);
- ``null_baseline``: histogram of the equal-weights scores against the
  calibrated mean (thesis Fig. A5.1).

From the model itself:
- ``spatial_similarity``: ``model.obj_func``'s own plot of the run of median
  score, copied from that run's folder;
- ``maps`` (only with ``--maps``): ``model.viz_map``'s yearly maps (years 10,
  20, ..., 70 and the last) of the same run, re-run once with ``plot=True``
  (about 4 minutes; it reproduces the saved run exactly). Don't use
  ``--maps`` while another model script is running: it uses the same
  shared-memory names.
"""

import argparse
import glob
import os
import shutil
import subprocess
import sys
import traceback
import warnings

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abm_parallel as ap  # noqa: E402
import run_measures as rm  # noqa: E402

KEYS = ap.PERMANENT_KEYS + ap.YEARLY_KEYS


def say(msg=""):
    print(msg, flush=True)


def path_of(ctx, *parts):
    return os.path.join(ctx["results_dir"], *parts)


def read_csv(ctx, *parts):
    import pandas as pd

    p = path_of(ctx, *parts)
    if not os.path.exists(p):
        raise FileNotFoundError(f"{p} not found")
    return pd.read_csv(p)


def out(ctx, name, ext):
    return os.path.join(ctx["out_dir"], f"negev_abm_thesis_{name}.{ext}")


def save(ctx, name):
    """Save the current pyplot figure as PNG (300 dpi) and PDF."""
    import matplotlib.pyplot as plt

    files = [out(ctx, name, "png"), out(ctx, name, "pdf")]
    plt.savefig(files[0], dpi=300, bbox_inches="tight")
    plt.savefig(files[1], bbox_inches="tight")
    plt.close("all")
    return files


def median_run(ctx):
    """The calibrated trial's run whose score is the median of its 30 runs."""
    runs = read_csv(ctx, "analysis", f"measures_trial{ctx['trial']}", "runs.csv")
    med = runs["score_obj_func"].median()
    return runs.iloc[(runs["score_obj_func"] - med).abs().argsort().iloc[0]]


# ------------------------------------------------------------ calibration.ipynb

def plotly_png(fig, png_path, timeout):
    """Export a plotly figure to PNG in a separate process; True if it worked."""
    tmp = png_path + ".json.tmp"
    with open(tmp, "w") as f:
        f.write(fig.to_json())
    code = ("import sys, plotly.io as pio; "
            "pio.read_json(sys.argv[1]).write_image(sys.argv[2], scale=3)")
    try:
        r = subprocess.run([sys.executable, "-c", code, tmp, png_path],
                           capture_output=True, text=True, timeout=timeout)
        if r.returncode == 0 and os.path.exists(png_path):
            return True, ""
        lines = (r.stderr or "").strip().splitlines()
        return False, lines[-1] if lines else f"exit code {r.returncode}"
    except subprocess.TimeoutExpired:
        return False, f"no PNG after {timeout} s"
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def optuna_plot(ctx, name, make):
    import optuna

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = ctx.get("study")
    if study is None:
        study = ap.load_study_in(ctx["results_dir"], ctx["study_name"])
        ctx["study"] = study
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fig = make(study)
    files = [out(ctx, name, "html")]
    fig.write_html(files[0])
    ok, why = plotly_png(fig, out(ctx, name, "png"), ctx["png_timeout"])
    if ok:
        files.append(out(ctx, name, "png"))
    else:
        say(f"    PNG not written ({why}); use the camera button in the .html")
    return files


def fig_optimization_history(ctx):
    import optuna.visualization as vis

    return optuna_plot(ctx, "optimization_history", vis.plot_optimization_history)


def fig_param_importances(ctx):
    import optuna.visualization as vis

    return optuna_plot(ctx, "param_importances", vis.plot_param_importances)


def fig_slice(ctx):
    import optuna.visualization as vis

    return optuna_plot(ctx, "slice", vis.plot_slice)


def fig_best_trial_dynamics(ctx):
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns

    # Each run's household_data.csv, from run_measures.py (or the re-run)
    base = path_of(ctx, "analysis", f"measures_trial{ctx['trial']}", "runs", f"trial_{ctx['trial']}")
    if not os.path.isdir(base):
        base = path_of(ctx, "rerun_top10", f"trial_{ctx['trial']}")
    data_frames = []
    for folder in sorted(glob.glob(os.path.join(base, "iter_*"))):
        csv_file = os.path.join(folder, "household_data.csv")
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            df["Iteration"] = os.path.basename(folder).split("_")[1]
            data_frames.append(df)
    if not data_frames:
        raise FileNotFoundError(f"No household_data.csv under {base}")

    # As calibration.ipynb, "Deep Dive: Best Trial Analysis"
    all_data = pd.concat(data_frames, ignore_index=True)
    system_stats = all_data.groupby(["Step", "Iteration"]).agg({
        "flocks": "sum", "surplus": "mean", "proseprity index": "mean",
        "Manpower": ["sum", "count"],
    })
    system_stats.columns = ["_".join(col).strip() for col in system_stats.columns.values]
    system_stats = system_stats.reset_index().rename(columns={
        "flocks_sum": "Total_Flocks", "surplus_mean": "Avg_Surplus",
        "proseprity index_mean": "Avg_Prosperity", "Manpower_sum": "Total_Manpower",
        "Manpower_count": "Population",
    })
    with sns.axes_style("whitegrid"):
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle(f"Dynamics of Best Trial (Trial {ctx['trial']}) across {len(data_frames)} Iterations",
                     fontsize=16)
        sns.lineplot(data=system_stats, x="Step", y="Population", ax=axes[0, 0], color="tab:blue")
        axes[0, 0].set_title("Total Population (Households)")
        axes[0, 0].set_ylabel("Count")
        sns.lineplot(data=system_stats, x="Step", y="Total_Flocks", ax=axes[0, 1], color="tab:green")
        axes[0, 1].set_title("Total Livestock (Flock Head)")
        axes[0, 1].set_ylabel("Head Count")
        sns.lineplot(data=system_stats, x="Step", y="Avg_Surplus", ax=axes[1, 0], color="tab:orange")
        axes[1, 0].set_title("Average Household Surplus")
        axes[1, 0].set_ylabel("Surplus Units")
        sns.lineplot(data=system_stats, x="Step", y="Avg_Prosperity", ax=axes[1, 1], color="tab:purple")
        axes[1, 1].set_title("Average Prosperity Index")
        axes[1, 1].set_ylabel("Index")
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        return save(ctx, "best_trial_dynamics")


# ------------------------------------------------------------ sensitivity_analysis.ipynb

def fig_time_horizon(ctx):
    import matplotlib.pyplot as plt

    ck = read_csv(ctx, "sensitivity", "horizon", "checkpoints.csv")
    ck = ck[ck["year"] % 10 == 0]  # the thesis checkpoints: every 10 years
    df_time = ck.groupby("year")[["score", "spatial_error", "site_type_error"]].mean().reset_index()

    plt.figure(figsize=(10, 6))
    plt.plot(df_time["year"], df_time["score"], label="Total Score (Obj Func)", marker="o")
    plt.plot(df_time["year"], df_time["spatial_error"], label="Spatial Error", marker="s")
    plt.plot(df_time["year"], df_time["site_type_error"], label="Ratio Error", marker="^")
    plt.xlabel("Year")
    plt.ylabel("Error (Lower is better)")
    plt.title("Objective Function over 150 Years")
    plt.legend()
    plt.grid(True)
    return save(ctx, "time_horizon")


def fig_households(ctx):
    import matplotlib.pyplot as plt
    import seaborn as sns

    d = read_csv(ctx, "sensitivity", "households", "runs.csv")
    df_agents = d.rename(columns={"households_start": "Num_Agents", "score": "Score"})
    plt.figure(figsize=(8, 6))
    sns.boxplot(x="Num_Agents", y="Score", data=df_agents)
    plt.title("Sensitivity to Number of Agents")
    return save(ctx, "households")


def fig_territory(ctx):
    import matplotlib.pyplot as plt
    import seaborn as sns

    d = read_csv(ctx, "sensitivity", "territory", "runs.csv")
    df_territory = d.assign(
        Territory_Type=d["arm"].map({"calibrated": "Flexible", "fixed_territory": "Fixed"}),
        Score=d["score"])
    plt.figure(figsize=(8, 6))
    sns.boxplot(x="Territory_Type", y="Score", data=df_territory, order=["Flexible", "Fixed"])
    plt.title("Sensitivity to Territory Flexibility")
    return save(ctx, "territory")


def fig_null_baseline(ctx):
    import matplotlib.pyplot as plt
    import numpy as np
    import seaborn as sns

    d = read_csv(ctx, "sensitivity", "null", "runs.csv")
    null_scores = d.loc[d["arm"] == "equal_weights", "score"].to_numpy(float)
    null_mean = np.mean(null_scores)
    if ctx["null_reference"] == "reevaluation":
        top = read_csv(ctx, "analysis", "rerun_top10.csv")
        best_replicates_mean = float(top.loc[top["trial"] == ctx["trial"], "mean_score"].iloc[0])
    else:  # the calibrated weights on the same seeds as the null runs
        best_replicates_mean = float(d.loc[d["arm"] == "calibrated", "score"].mean())

    plt.figure(figsize=(8, 6))
    sns.histplot(null_scores, kde=True, color="gray", label="Null Baseline")
    plt.axvline(best_replicates_mean, color="red", linestyle="--",
                label=f"Best trial, 30 replicates ({best_replicates_mean:.4f})")
    plt.axvline(null_mean, color="black", linestyle="-", label=f"Null Mean ({null_mean:.4f})")
    plt.xlabel("Objective Score (Error)")
    plt.title("Null Weight Baseline vs. Optimized Model")
    plt.legend()
    return save(ctx, "null_baseline")


# ------------------------------------------------------------ the model's own plots

def fig_spatial_similarity(ctx):
    r = median_run(ctx)
    src = path_of(ctx, "analysis", f"measures_trial{ctx['trial']}", "runs", f"trial_{ctx['trial']}",
                  f"iter_{int(r['iteration'])}", "spatial_similarity.png")
    if not os.path.exists(src):
        raise FileNotFoundError(f"{src} not found")
    dst = out(ctx, "spatial_similarity", "png")
    shutil.copyfile(src, dst)
    say(f"    run of median score: seed {int(r['seed'])}, score {r['score_obj_func']:.4f}")
    return [dst]


def fig_maps(ctx):
    model = ap.import_model()
    r = median_run(ctx)
    seed, iteration = int(r["seed"]), int(r["iteration"])
    perm, yearly, w = ap.normalised_weights(ctx["params"])
    maps_dir = os.path.join(ctx["out_dir"], "maps_run")
    say(f"    re-running seed {seed} with plot=True (about 4 minutes)")
    handles = ap.create_shared_data(model)  # the same data path as the parallel runs
    try:
        model.ensure_data_loaded()
        sim, run_dir = model.run_model_opt(
            75, ras_wts=w, main_run_directory=maps_dir, trial_number=ctx["trial"], iteration=iteration,
            permanent_weights_dict=perm, yearly_weights_dict=yearly, seed=seed, plot=True)
        import geopandas as gpd

        score, _ratio = model.obj_func(gpd.read_file(model.CALIB_SHP_PATH), model.to_gdf(sim), run_dir)
    finally:
        ap.release_shared_data(handles)
    same = abs(float(score) - float(r["score_obj_func"])) < 1e-4
    say(f"    score {float(score):.4f} ({'the same as' if same else 'DIFFERENT from'} the saved run)")
    files = []
    for p in sorted(glob.glob(os.path.join(run_dir, "year_*_map.png"))):
        dst = out(ctx, "map_" + os.path.basename(p)[:-len("_map.png")], "png")
        shutil.copyfile(p, dst)
        files.append(dst)
    return files


FIGURES = {
    "optimization_history": fig_optimization_history,
    "param_importances": fig_param_importances,
    "slice": fig_slice,
    "best_trial_dynamics": fig_best_trial_dynamics,
    "time_horizon": fig_time_horizon,
    "households": fig_households,
    "territory": fig_territory,
    "null_baseline": fig_null_baseline,
    "spatial_similarity": fig_spatial_similarity,
    "maps": fig_maps,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--results-dir", required=True, help="the calibration's folder (holds study.log)")
    parser.add_argument("--study-name", required=True)
    parser.add_argument("--trial", type=int, required=True, help="the calibrated weight set")
    parser.add_argument("--only", nargs="+", choices=list(FIGURES), default=None)
    parser.add_argument("--maps", action="store_true",
                        help="also re-run the run of median score with plot=True for the yearly maps")
    parser.add_argument("--null-reference", choices=["same-seeds", "reevaluation"], default="same-seeds",
                        help="red line of the null plot: the calibrated weights on the null runs' seeds "
                             "(default) or the trial's re-evaluation mean")
    parser.add_argument("--png-timeout", type=int, default=180,
                        help="seconds allowed for each plotly PNG export")
    parser.add_argument("--out-dir", default=None, help="default: <results-dir>/figures_thesis")
    args = parser.parse_args()

    results_dir = os.path.abspath(args.results_dir)
    ap.set_environment(results_dir)  # also draws to files only (Agg)
    params, stored = rm.load_trial_params(results_dir, args.study_name, args.trial)
    ap.set_calib_shp(stored)
    ctx = {
        "results_dir": results_dir, "study_name": args.study_name, "trial": args.trial,
        "params": params, "null_reference": args.null_reference, "png_timeout": args.png_timeout,
        "out_dir": os.path.abspath(args.out_dir or os.path.join(results_dir, "figures_thesis")),
    }
    os.makedirs(ctx["out_dir"], exist_ok=True)

    names = args.only or [n for n in FIGURES if n != "maps"]
    if args.maps and "maps" not in names:
        names.append("maps")
    written, failed = [], []
    for name in names:
        try:
            files = FIGURES[name](ctx)
            written += files
            say(f"  {name}: done")
        except Exception:
            failed.append(name)
            say(f"  {name}: FAILED\n{traceback.format_exc()}")
    say(f"\nFiles in {ctx['out_dir']}:")
    for p in written:
        if not p.endswith(".pdf"):
            say(f"  {os.path.basename(p)}")
    if failed:
        say(f"Failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
