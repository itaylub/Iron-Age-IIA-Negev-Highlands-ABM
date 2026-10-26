"""Figures for the result notes of a calibrated weight set (here trial 197).

Reads the saved outputs of ``calibrate.py``, ``run_measures.py`` and
``sensitivity.py``; runs no model. The plots follow the thesis notebooks
(``Code/calibration.ipynb``, ``Code/sensitivity_analysis.ipynb``): Optuna's own
optimization-history plot, a histogram for the null baseline, errors by
year, and box plots for the households and territory tests. Run from the
repository root, in the model's environment:

    python scripts/plot_results.py --results-dir D:/abm_runs/opt_fixed_strict_2026_10 --study-name opt_fixed_strict_2026_10 --trial 197

Writes ``negev_abm_<name>.png`` (300 dpi) and ``.pdf`` to
``<results-dir>/figures/``. Choose some with ``--only``:
- ``calibration_procedure``: Optuna's optimization history. Also written
  as an interactive ``.html``, Optuna's plotly version as in the thesis
  notebook, if plotly is installed;
- ``calibrated_drivers``: normalised weights of the 20 leading trials and of
  the calibrated trial;
- ``fit_to_the_record``: each run's ellipse and centre against the record's;
  the run of median score, site by site;
- ``palimpsest_trajectory``: cumulative compound locations; building and
  reuse events a year;
- ``null_baseline``: histogram of the equal-weights scores against the
  calibrated mean; each run's ellipse and centre in both arms;
- ``run_length``: composite, spatial and site-type error every 10 years
  over 150 years;
- ``site_threshold``: composite, spatial and site-type error at each
  threshold, after 75 years;
- ``households``: composite error and IoU by number of households;
- ``territory``: each run's ellipse and centre, flexible and fixed; the three
  errors by territory mode.

Maps are in km on the Israel TM Grid (EPSG:2039). Ellipses are drawn as the
calibration scores them (semi-axes 2 SD; ``run_measures.ellipse_params``).
"""

import argparse
import glob
import os
import sys
import traceback
import warnings

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abm_parallel as ap  # noqa: E402
import run_measures as rm  # noqa: E402

KEYS = ap.PERMANENT_KEYS + ap.YEARLY_KEYS
LAYER_NAMES = {
    "dist_to_kb": "Corridor proximity", "p_water": "Permanent water",
    "Mean_rain": "Long-term mean rainfall", "slope_suitability": "Slope",
    "return_to_site": "Reuse potential", "humen_stress": "Resource exhaustion",
    "Yearly_rain": "Current-year rainfall",
}

INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
LIGHT_BLUE = "#86b6ef"
# The three errors, with the thesis markers (Code/sensitivity_analysis.ipynb)
ERRORS = [("score", "Composite error", BLUE, "o"),
          ("spatial_error", "Spatial error (1 − IoU)", ORANGE, "s"),
          ("site_type_error", "Site-type error", AQUA, "^")]

FULL_WIDTH = 7.48  # in, a two-column journal figure (190 mm)


def say(msg=""):
    print(msg, flush=True)


# ------------------------------------------------------------ helpers

def style():
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
        "axes.edgecolor": AXIS, "axes.linewidth": 0.8, "axes.labelcolor": INK,
        "text.color": INK, "xtick.color": INK2, "ytick.color": INK2,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
        "axes.axisbelow": True, "axes.spines.top": False, "axes.spines.right": False,
        "axes.titleweight": "bold", "axes.titlelocation": "left",
        "legend.frameon": False, "lines.linewidth": 1.5,
        "figure.facecolor": "white", "axes.facecolor": "white",
        "savefig.dpi": 300, "savefig.bbox": "tight", "savefig.facecolor": "white",
        "pdf.fonttype": 42, "ps.fonttype": 42,
    })


def path_of(ctx, *parts):
    return os.path.join(ctx["results_dir"], *parts)


def read_csv(ctx, *parts):
    import pandas as pd

    p = path_of(ctx, *parts)
    if not os.path.exists(p):
        raise FileNotFoundError(f"{p} not found")
    return pd.read_csv(p)


def save(fig, ctx, name):
    import matplotlib.pyplot as plt

    base = os.path.join(ctx["out_dir"], f"negev_abm_{name}")
    try:
        fig.tight_layout()
    except Exception:
        pass
    fig.savefig(base + ".png", dpi=300, bbox_inches="tight")
    fig.savefig(base + ".pdf", bbox_inches="tight")
    plt.close(fig)
    return [base + ".png", base + ".pdf"]


def panel(ax, letter, text):
    ax.set_title(f"{letter}   {text}", loc="left")


def legend_right(ax, **kw):
    """Legend outside the plot, to the right."""
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), **kw)


def legend_below(ax, ncol=2):
    """Legend outside the plot, below it."""
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=ncol)


def year_line(ax, x, text):
    ax.axvline(x, ls=":", lw=1.0, color=MUTED, zorder=1)
    ax.text(x, 0.99, " " + text, transform=ax.get_xaxis_transform(), ha="left", va="top",
            fontsize=6.5, color=MUTED)


def band(ax, tab, color, label=None):
    """Median and 5-95% band of a year x run table."""
    years = tab.index.to_numpy()
    ax.fill_between(years, tab.quantile(0.05, axis=1), tab.quantile(0.95, axis=1),
                    color=color, alpha=0.18, lw=0, zorder=2)
    ax.plot(years, tab.median(axis=1), color=color, lw=1.6, zorder=3, label=label)


def error_lines(ax, d, key):
    """Mean ± SD of the three errors against `key` (one row per run and key value)."""
    g = d.groupby(key)
    for col, name, colour, marker in ERRORS:
        m, s = g[col].mean(), g[col].std(ddof=1)
        ax.fill_between(m.index, m - s, m + s, color=colour, alpha=0.15, lw=0)
        ax.plot(m.index, m.values, marker=marker, color=colour, ms=4, lw=1.4, label=name)


def jitter(n, width, seed=0):
    import numpy as np

    return np.random.default_rng(seed).uniform(-width, width, n)


def load_sites(p):
    import pandas as pd

    d = pd.read_csv(p)
    return d["x"].to_numpy(float), d["y"].to_numpy(float), d["value"].to_numpy(int)


def ellipse_km(xs, ys):
    """Outline and centre (km) of the standard-deviational ellipse the score uses."""
    import numpy as np

    e = rm.ellipse_params(xs, ys)
    if not e["a"] or not e["b"]:
        return None
    ex, ey = rm.ellipse_polygon(e, n=360).exterior.xy
    return np.asarray(ex) / 1000, np.asarray(ey) / 1000, e["cx"] / 1000, e["cy"] / 1000


def draw_record(ax, ctx, points=True):
    x, y, v = ctx["obs"]
    if points:
        ax.scatter(x[v == 1] / 1000, y[v == 1] / 1000, s=3, color=AXIS, lw=0, zorder=1,
                   label=f"Recorded sites ({int((v == 1).sum())})")
        ax.scatter(x[v == 2] / 1000, y[v == 2] / 1000, s=12, marker="^", color=INK2, lw=0,
                   zorder=2, label=f"Recorded compounds ({int((v == 2).sum())})")
    ex, ey, cx, cy = ctx["obs_ellipse"]
    ax.plot(ex, ey, color=INK, lw=1.8, zorder=6, label="Record's ellipse")
    ax.plot([cx], [cy], ls="", marker="+", color=INK, ms=9, mew=1.6, zorder=7,
            label="Record's centre")


def draw_runs(ax, sites_dir, color, label):
    """Each run's ellipse (thin line) and centre (dot)."""
    files = sorted(glob.glob(os.path.join(sites_dir, "run_*.csv")))
    if not files:
        raise FileNotFoundError(f"No run_*.csv in {sites_dir}")
    first = True
    for p in files:
        x, y, _v = load_sites(p)
        el = ellipse_km(x, y)
        if el is None:
            continue
        ex, ey, cx, cy = el
        ax.plot(ex, ey, color=color, lw=0.6, alpha=0.5, zorder=3,
                label=f"{label}: ellipses ({len(files)} runs)" if first else None)
        ax.plot([cx], [cy], ls="", marker="o", color=color, ms=2.5, alpha=0.85, zorder=4,
                label=f"{label}: centres" if first else None)
        first = False
    return len(files)


def map_axes(ax):
    ax.set_aspect("equal")
    ax.set_xlabel("Easting (km, Israel TM Grid)")
    ax.set_ylabel("Northing (km)")


# ------------------------------------------------------------ figures

def fig_calibration_procedure(ctx):
    import matplotlib.pyplot as plt
    import optuna

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = ap.load_study_in(ctx["results_dir"], ctx["study_name"])
    written = []
    try:  # Optuna's plotly version, as in the thesis notebook (no extra packages for html)
        import optuna.visualization as vis

        html = os.path.join(ctx["out_dir"], "negev_abm_calibration_procedure.html")
        vis.plot_optimization_history(study).write_html(html)
        written.append(html)
    except Exception as exc:
        say(f"    interactive version skipped ({exc.__class__.__name__}: {exc})")

    from optuna.visualization.matplotlib import plot_optimization_history

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # Optuna marks its matplotlib plots experimental
        with plt.rc_context():  # Optuna switches to its own style; keep it to this figure
            ax = plot_optimization_history(study)
            fig = ax.figure
            fig.set_size_inches(6.2, 3.4)
            legend_right(ax)
            written += save(fig, ctx, "calibration_procedure")
    return written


def fig_calibrated_drivers(ctx):
    import matplotlib.pyplot as plt

    trials = read_csv(ctx, "analysis", "trials.csv")
    done = trials[(trials["state"] == "COMPLETE") & trials["value"].notna()]
    lead = done.sort_values("value").head(20)
    means = {k: lead[f"norm_{k}"].mean() for k in KEYS}
    order = sorted(KEYS, key=lambda k: means[k])  # largest at the top
    chosen = {k: ctx["params"][k] / sum(ctx["params"].values()) for k in KEYS}

    fig, ax = plt.subplots(figsize=(6.2, 3.0))
    for i, k in enumerate(order):
        v = lead[f"norm_{k}"].to_numpy(float)
        ax.scatter(v, i + jitter(len(v), 0.14, seed=i), s=10, color=BLUE, alpha=0.45, lw=0, zorder=2,
                   label="20 leading trials" if i == 0 else None)
        ax.plot([means[k], means[k]], [i - 0.28, i + 0.28], color=BLUE, lw=1.6, zorder=3,
                label="Their mean" if i == 0 else None)
        ax.scatter([chosen[k]], [i], s=30, marker="D", color=ORANGE, lw=0, zorder=5,
                   label=f"Calibrated weights (trial {ctx['trial']})" if i == 0 else None)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([LAYER_NAMES[k] for k in order])
    ax.grid(axis="y", visible=False)
    top_weight = max([lead[f"norm_{k}"].max() for k in KEYS] + list(chosen.values()))
    ax.set_xlim(-0.02, top_weight + 0.04)
    ax.set_xlabel("Normalised weight")
    legend_right(ax)
    ax.set_title("Weights of the seven suitability layers", loc="left")
    return save(fig, ctx, "calibrated_drivers")


def fig_fit_to_the_record(ctx):
    import matplotlib.pyplot as plt

    mdir = ctx["measures_dir"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(FULL_WIDTH, 4.3))
    draw_record(a, ctx)
    draw_runs(a, os.path.join(mdir, "sites"), BLUE, "Simulated")
    map_axes(a)
    legend_below(a)
    panel(a, "a", "Each run's ellipse against the record's")

    runs = read_csv(ctx, "analysis", f"measures_trial{ctx['trial']}", "runs.csv")
    med = runs["score_obj_func"].median()
    r = runs.iloc[(runs["score_obj_func"] - med).abs().argsort().iloc[0]]
    x, y, v = load_sites(os.path.join(mdir, "sites", f"run_{int(r['seed'])}.csv"))
    b.scatter(x[v == 1] / 1000, y[v == 1] / 1000, s=5, color=BLUE, lw=0, zorder=2,
              label=f"Simulated sites ({int((v == 1).sum())})")
    b.scatter(x[v == 2] / 1000, y[v == 2] / 1000, s=16, marker="^", color=ORANGE, lw=0, zorder=3,
              label=f"Simulated compounds ({int((v == 2).sum())})")
    el = ellipse_km(x, y)
    if el:
        b.plot(el[0], el[1], color=BLUE, lw=1.4, zorder=4, label="Simulated ellipse")
        b.plot([el[2]], [el[3]], ls="", marker="o", color=BLUE, ms=4, zorder=5, label="Simulated centre")
    draw_record(b, ctx, points=False)
    b.set_xlim(a.get_xlim())
    b.set_ylim(a.get_ylim())
    map_axes(b)
    legend_below(b)
    panel(b, "b", f"The run of median composite error ({r['score_obj_func']:.3f})")
    return save(fig, ctx, "fit_to_the_record")


def fig_palimpsest_trajectory(ctx):
    import matplotlib.pyplot as plt

    d = read_csv(ctx, "analysis", f"measures_trial{ctx['trial']}", "trajectory.csv")
    years = int(d["year"].max())
    d = d[d["year"] < years].copy()  # the last row is the empty year after the run
    d["elapsed"] = d["year"] + 1
    cum = d.pivot_table(index="elapsed", columns="seed", values="cumulative_locations")
    n = cum.shape[1]

    fig, (a, b) = plt.subplots(1, 2, figsize=(FULL_WIDTH, 3.0))
    band(a, cum, BLUE, label=f"Median, 5–95% of {n} runs")
    a.set_xlabel("Years")
    a.set_ylabel("Compound locations (cumulative)")
    a.set_xlim(0, years)
    a.set_ylim(bottom=0)
    a.legend(loc="lower right")
    panel(a, "a", "Compound locations built so far")

    built = d.groupby("elapsed")["locations_built"].mean()
    reuse = d.groupby("elapsed")["reuse_events"].mean()
    b.plot(built.index, built.values, color=BLUE, lw=1.4, label="New compound locations")
    b.plot(reuse.index, reuse.values, color=ORANGE, lw=1.4, label="Reuse events")
    b.text(years + 1, built.values[-1], " new", color=INK2, fontsize=7, va="center")
    b.text(years + 1, reuse.values[-1], " reuse", color=INK2, fontsize=7, va="center")
    b.set_xlim(0, years + 8)
    b.set_ylim(bottom=0)
    b.set_xlabel("Years")
    b.set_ylabel(f"Events a year (mean of {n} runs)")
    b.legend(loc="upper right")
    panel(b, "b", "Building and reuse each year")
    return save(fig, ctx, "palimpsest_trajectory")


def fig_null_baseline(ctx):
    import matplotlib.pyplot as plt
    import seaborn as sns

    d = read_csv(ctx, "sensitivity", "null", "runs.csv")
    null = d.loc[d["arm"] == "equal_weights", "score"].to_numpy(float)
    cal = d.loc[d["arm"] == "calibrated", "score"].to_numpy(float)

    fig, (a, b) = plt.subplots(1, 2, figsize=(FULL_WIDTH, 4.3), gridspec_kw={"width_ratios": [1, 1.35]})
    # As thesis Fig. A5.1 (Code/sensitivity_analysis.ipynb), with the calibrated
    # weights' mean over runs on the same seeds
    sns.histplot(null, kde=True, color="gray", ax=a, label=f"Equal weights ({len(null)} runs)")
    a.axvline(cal.mean(), color="red", ls="--", lw=1.5,
              label=f"Calibrated weights, mean of {len(cal)} runs ({cal.mean():.4f})")
    a.axvline(null.mean(), color="black", ls="-", lw=1.5, label=f"Equal weights, mean ({null.mean():.4f})")
    a.set_xlabel("Composite error")
    a.set_ylabel("Runs")
    legend_below(a, ncol=1)
    panel(a, "a", "Equal weights against the calibrated weights")

    draw_record(b, ctx)
    draw_runs(b, path_of(ctx, "sensitivity", "null", "calibrated", "sites"), BLUE, "Calibrated weights")
    draw_runs(b, path_of(ctx, "sensitivity", "null", "equal_weights", "sites"), ORANGE, "Equal weights")
    map_axes(b)
    legend_below(b)
    panel(b, "b", "Each run's ellipse and centre against the record's")
    return save(fig, ctx, "null_baseline")


def fig_run_length(ctx):
    import matplotlib.pyplot as plt

    ck = read_csv(ctx, "sensitivity", "horizon", "checkpoints.csv")
    start, last, n = 30, int(ck["year"].max()), ck["seed"].nunique()
    fig, ax = plt.subplots(figsize=(6.2, 3.4))
    error_lines(ax, ck[ck["year"] >= start], "year")
    year_line(ax, 75, "75 years (calibrated runs)")
    ax.set_xlim(start - 3, last + 3)
    ax.set_ylim(0, 0.55)
    ax.set_xlabel("Year")
    ax.set_ylabel(f"Error, mean ± SD of {n} runs (lower is better)")
    legend_right(ax)
    ax.set_title(f"Errors every 10 years, years {start}–{last}", loc="left")
    return save(fig, ctx, "run_length")


def fig_site_threshold(ctx):
    import matplotlib.pyplot as plt

    th = read_csv(ctx, "sensitivity", "threshold", "thresholds.csv")
    th = th.copy()
    th["threshold"] = th["threshold"].round(1)
    n = th["seed"].nunique()
    fig, ax = plt.subplots(figsize=(6.2, 3.4))
    error_lines(ax, th, "threshold")
    ax.axvline(0.6, ls=":", lw=1.0, color=MUTED, zorder=1)
    ax.text(0.6, 0.99, " calibration threshold", transform=ax.get_xaxis_transform(), ha="left",
            va="top", fontsize=6.5, color=MUTED)
    ax.set_xticks(sorted(th["threshold"].unique()))
    ax.set_xlim(0.05, 1.05)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Site threshold (summed occupation)")
    ax.set_ylabel(f"Error, mean ± SD of {n} runs (lower is better)")
    legend_right(ax)
    ax.set_title("Errors by site threshold, after 75 years", loc="left")
    return save(fig, ctx, "site_threshold")


def fig_households(ctx):
    import matplotlib.pyplot as plt
    import seaborn as sns

    d = read_csv(ctx, "sensitivity", "households", "runs.csv")
    d = d.copy()
    d["households"] = d["households_start"].astype(int)
    order = sorted(d["households"].unique())
    labels = [f"{h}\n(calibrated)" if h == 9 else str(h) for h in order]
    fig, axes = plt.subplots(1, 2, figsize=(FULL_WIDTH, 3.0))
    for ax, (col, title, letter) in zip(axes, (("score", "Composite error", "a"),
                                               ("iou", "Ellipse overlap (IoU)", "b"))):
        sns.boxplot(data=d, x="households", y=col, order=order, color=LIGHT_BLUE, width=0.5,
                    fliersize=2, linewidth=1, ax=ax)
        ax.set_xticks(range(len(order)))
        ax.set_xticklabels(labels)
        ax.set_xlabel("Households")
        ax.set_ylabel(title)
        ax.grid(axis="x", visible=False)
        panel(ax, letter, f"{title}, {d['seed'].nunique()} runs each")
    return save(fig, ctx, "households")


def fig_territory(ctx):
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns

    d = read_csv(ctx, "sensitivity", "territory", "runs.csv")
    fig, (a, b) = plt.subplots(1, 2, figsize=(FULL_WIDTH, 4.3), gridspec_kw={"width_ratios": [1.35, 1]})
    draw_record(a, ctx)
    draw_runs(a, path_of(ctx, "sensitivity", "territory", "calibrated", "sites"), BLUE, "Flexible")
    draw_runs(a, path_of(ctx, "sensitivity", "territory", "fixed_territory", "sites"), ORANGE, "Fixed")
    map_axes(a)
    legend_below(a)
    panel(a, "a", "Each run's ellipse and centre against the record's")

    modes = {"calibrated": "Flexible (calibrated)", "fixed_territory": "Fixed"}
    long = pd.concat([pd.DataFrame({"term": name.split(" (")[0], "error": d[col].to_numpy(float),
                                    "Territory": d["arm"].map(modes).to_numpy()})
                      for col, name, _c, _m in ERRORS], ignore_index=True)
    sns.boxplot(data=long, x="term", y="error", hue="Territory", hue_order=list(modes.values()),
                palette=[BLUE, ORANGE], width=0.6, fliersize=2, linewidth=1, ax=b)
    b.set_xlabel("")
    b.set_ylabel("Error (lower is better)")
    b.grid(axis="x", visible=False)
    try:  # seaborn builds this legend itself; move it rather than rebuild it
        sns.move_legend(b, "upper center", bbox_to_anchor=(0.5, -0.14), ncol=2, title=None, frameon=False)
    except Exception:
        legend_below(b, ncol=2)
    panel(b, "b", f"The three errors, {d['seed'].nunique()} runs each")
    return save(fig, ctx, "territory")


FIGURES = {
    "calibration_procedure": fig_calibration_procedure,
    "calibrated_drivers": fig_calibrated_drivers,
    "fit_to_the_record": fig_fit_to_the_record,
    "palimpsest_trajectory": fig_palimpsest_trajectory,
    "null_baseline": fig_null_baseline,
    "run_length": fig_run_length,
    "site_threshold": fig_site_threshold,
    "households": fig_households,
    "territory": fig_territory,
}


# ------------------------------------------------------------ main

def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--results-dir", required=True, help="the calibration's folder (holds study.log)")
    parser.add_argument("--study-name", required=True)
    parser.add_argument("--trial", type=int, required=True, help="the calibrated weight set")
    parser.add_argument("--only", nargs="+", choices=list(FIGURES), default=None)
    parser.add_argument("--out-dir", default=None, help="default: <results-dir>/figures")
    args = parser.parse_args()

    results_dir = os.path.abspath(args.results_dir)
    ap.set_environment(results_dir)  # also draws to files only (Agg)
    params, stored = rm.load_trial_params(results_dir, args.study_name, args.trial)
    calib_shp = stored or os.path.join(ap.REPO_ROOT, "Data", "P_for_calib.shp")

    import geopandas as gpd

    gdf = gpd.read_file(calib_shp)
    obs = (gdf.geometry.x.to_numpy(float), gdf.geometry.y.to_numpy(float), gdf["value"].to_numpy(int))
    ctx = {
        "results_dir": results_dir, "study_name": args.study_name, "trial": args.trial,
        "params": params, "obs": obs, "obs_ellipse": ellipse_km(obs[0], obs[1]),
        "measures_dir": os.path.join(results_dir, "analysis", f"measures_trial{args.trial}"),
        "out_dir": os.path.abspath(args.out_dir or os.path.join(results_dir, "figures")),
    }
    os.makedirs(ctx["out_dir"], exist_ok=True)
    say(f"Record: {calib_shp} ({len(gdf)} sites, {int((gdf['value'] == 2).sum())} compounds)")
    style()

    written, failed = [], []
    for name in args.only or list(FIGURES):
        try:
            written += FIGURES[name](ctx)
            say(f"  {name}: done")
        except Exception:
            failed.append(name)
            say(f"  {name}: FAILED\n{traceback.format_exc()}")
    pngs = [p for p in written if p.endswith(".png")]
    say(f"\n{len(pngs)} figure(s) in {ctx['out_dir']}")
    for p in written:
        if not p.endswith(".pdf"):
            say(f"  {os.path.basename(p)}")
    if failed:
        say(f"Failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
