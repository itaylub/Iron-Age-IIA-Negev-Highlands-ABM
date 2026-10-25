"""Figures for the result notes of a calibrated weight set (here trial 197).

Reads the outputs of ``calibrate.py``, ``analyse_calibration.py``,
``run_measures.py`` and ``sensitivity.py``; runs no model. Run from the
repository root, in the model's environment:

    python scripts/plot_results.py --results-dir D:/abm_runs/opt_fixed_strict_2026_10 --study-name opt_fixed_strict_2026_10 --trial 197

Writes one figure per result note to ``<results-dir>/figures/``, as
``negev_abm_<name>.png`` (300 dpi) and ``.pdf``. Choose some with ``--only``:
- ``calibration_procedure``: best score by completed trial; the ten leading
  sets' 10-run calibration score against their 30-run re-run mean;
- ``calibrated_drivers``: normalised weights of the 20 leading trials, with
  the calibrated trial and the thesis trial 173;
- ``fit_to_the_record``: each run's ellipse against the record's; one run of
  median score, site by site;
- ``palimpsest_trajectory``: cumulative compound locations; building and
  reuse events a year;
- ``null_baseline``: composite error paired by seed; each run's ellipse for
  both arms;
- ``run_length``: sites, compound locations, compound share and the errors
  over 150 years;
- ``site_threshold``: sites by year at each distinct threshold; compound
  share and composite error at 75 years;
- ``households``: composite error, IoU, sites and compound share against the
  number of households;
- ``territory``: each run's ellipse, fixed and flexible; spatial against
  site-type error.

Colours: blue, orange and aqua, the first three slots of a colour-blind-safe
categorical palette, and a four-step blue ramp for the ordered thresholds.
Maps are in km on the Israel TM Grid (EPSG:2039). Ellipses are drawn as the
calibration scores them (semi-axes 2 SD; ``run_measures.ellipse_params``).
"""

import argparse
import glob
import json
import os
import sys
import traceback

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

# Ink and chrome
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
# Categorical slots 1-3 (validated all-pairs for colour-blind readers)
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
# Ordered blue ramp, light to dark, for the four thresholds
RAMP = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]

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


def read_json(ctx, *parts):
    p = path_of(ctx, *parts)
    if not os.path.exists(p):
        return {}
    with open(p) as f:
        return json.load(f)


def save(fig, ctx, name):
    import matplotlib.pyplot as plt

    base = os.path.join(ctx["out_dir"], f"negev_abm_{name}")
    try:
        fig.tight_layout()
    except Exception:
        pass
    fig.savefig(base + ".png", dpi=300)
    fig.savefig(base + ".pdf")
    plt.close(fig)
    return [base + ".png", base + ".pdf"]


def panel(ax, letter, text):
    ax.set_title(f"{letter}   {text}", loc="left")


def ref_line(ax, y, text, where="bottom"):
    """A dashed horizontal line for a recorded value, labelled at the left."""
    ax.axhline(y, ls="--", lw=1.0, color=INK2, zorder=2)
    ax.text(0.01, y, " " + text, transform=ax.get_yaxis_transform(), ha="left",
            va=where, fontsize=7, color=INK2)


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
    ax.plot([cx], [cy], marker="+", color=INK, ms=9, mew=1.6, zorder=7)


def draw_runs(ax, sites_dir, color, label):
    """Each run's ellipse (thin) and centre (dot)."""
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
                label=f"{label} ({len(files)} runs)" if first else None)
        ax.plot([cx], [cy], "o", color=color, ms=2.5, alpha=0.85, zorder=4)
        first = False
    return len(files)


def map_axes(ax):
    ax.set_aspect("equal")
    ax.set_xlabel("Easting (km, Israel TM Grid)")
    ax.set_ylabel("Northing (km)")


def means_by(d, key, col):
    g = d.groupby(key)[col]
    return g.mean(), g.std(ddof=1)


# ------------------------------------------------------------ figures

def fig_calibration_procedure(ctx):
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.lines import Line2D

    trials = read_csv(ctx, "analysis", "trials.csv")
    done = trials[(trials["state"] == "COMPLETE") & trials["value"].notna()].sort_values("number")
    vals = done["value"].to_numpy(float)
    best = np.minimum.accumulate(vals)
    k = np.arange(1, len(vals) + 1)

    fig, (a, b) = plt.subplots(1, 2, figsize=(FULL_WIDTH, 3.2))
    a.scatter(k, vals, s=6, color=MUTED, alpha=0.6, lw=0, zorder=2, label="Completed trial (10 runs)")
    a.step(k, best, where="post", color=BLUE, lw=1.6, zorder=3, label="Best so far")
    if len(k) > 50:
        a.axvspan(k[-50], k[-1], color=GRID, alpha=0.6, lw=0, zorder=1)
        gain = read_json(ctx, "analysis", "settle_check.json").get("improvement_last_50")
        note = "last 50 completed trials" + (f": gain {gain:.3f}" if isinstance(gain, (int, float)) else "")
        a.text(k[-50], 0.98, " " + note, transform=a.get_xaxis_transform(), ha="left", va="top",
               fontsize=6.5, color=INK2)
    a.set_ylim(best.min() - 0.01, np.percentile(vals, 95))
    a.set_xlabel("Completed trials")
    a.set_ylabel("Composite error (mean of 10 runs)")
    a.legend(loc="upper right", bbox_to_anchor=(1.0, 0.88))
    panel(a, "a", "Calibration: best score by completed trial")

    top = read_csv(ctx, "analysis", "rerun_top10.csv")
    lo = min(top["calibration_score_10runs"].min(), top["mean_score"].min()) - 0.003
    hi = max(top["calibration_score_10runs"].max(), top["mean_score"].max()) + 0.006
    b.plot([lo, hi], [lo, hi], ls="--", lw=1.0, color=MUTED, zorder=1)
    b.text(hi - 0.0005, hi - 0.0015, "equal scores", ha="right", va="top", fontsize=6.5, color=MUTED)
    for _, r in top.iterrows():
        mine = int(r["trial"]) == ctx["trial"]
        col = ORANGE if mine else BLUE
        b.errorbar([r["calibration_score_10runs"]], [r["mean_score"]], yerr=[r["se"]], fmt="o",
                   color=col, ms=4.5 if mine else 3.5, capsize=2, lw=1.0, zorder=3)
        b.text(r["calibration_score_10runs"] + 0.0003, r["mean_score"], f" {int(r['trial'])}",
               fontsize=6, color=INK2, va="center")
    fresh = path_of(ctx, "sensitivity", "null", "runs.csv")
    handles = [Line2D([], [], marker="o", ls="", color=BLUE, ms=3.5, label="Leading set, 30 fresh runs (± SE)"),
               Line2D([], [], marker="o", ls="", color=ORANGE, ms=4.5, label=f"Trial {ctx['trial']}, chosen")]
    if os.path.exists(fresh):
        d = read_csv(ctx, "sensitivity", "null", "runs.csv")
        s = d.loc[d["arm"] == "calibrated", "score"]
        x0 = float(top.loc[top["trial"] == ctx["trial"], "calibration_score_10runs"].iloc[0])
        b.errorbar([x0], [s.mean()], yerr=[s.std(ddof=1) / len(s) ** 0.5], fmt="o", mfc="white",
                   color=ORANGE, ms=4.5, capsize=2, lw=1.0, zorder=4)
        handles.append(Line2D([], [], marker="o", ls="", color=ORANGE, mfc="white", ms=4.5,
                                  label=f"Trial {ctx['trial']}, 30 further runs on new seeds"))
    b.set_xlim(lo, hi)
    b.set_ylim(lo, hi)
    b.set_xlabel("Calibration score (10 runs)")
    b.set_ylabel("Re-run score (mean of 30 runs)")
    b.legend(handles=handles, loc="lower right")
    panel(b, "b", "The ten leading weight sets, re-run")
    return save(fig, ctx, "calibration_procedure")


def fig_calibrated_drivers(ctx):
    import matplotlib.pyplot as plt
    import numpy as np

    trials = read_csv(ctx, "analysis", "trials.csv")
    done = trials[(trials["state"] == "COMPLETE") & trials["value"].notna()]
    lead = done.sort_values("value").head(20)
    means = {k: lead[f"norm_{k}"].mean() for k in KEYS}
    order = sorted(KEYS, key=lambda k: means[k])  # largest at the top
    chosen = {k: ctx["params"][k] / sum(ctx["params"].values()) for k in KEYS}
    thesis = {k: ap.THESIS_BEST[k] / sum(ap.THESIS_BEST.values()) for k in KEYS}

    fig, ax = plt.subplots(figsize=(5.2, 3.0))
    for i, k in enumerate(order):
        v = lead[f"norm_{k}"].to_numpy(float)
        ax.scatter(v, i + jitter(len(v), 0.14, seed=i), s=10, color=BLUE, alpha=0.45, lw=0, zorder=2,
                   label="20 leading trials" if i == 0 else None)
        ax.plot([means[k], means[k]], [i - 0.28, i + 0.28], color=BLUE, lw=1.6, zorder=3,
                label="Their mean" if i == 0 else None)
        ax.scatter([thesis[k]], [i], s=26, facecolor="white", edgecolor=INK2, lw=1.0, zorder=4,
                   label="Thesis model, trial 173" if i == 0 else None)
        ax.scatter([chosen[k]], [i], s=30, marker="D", color=ORANGE, lw=0, zorder=5,
                   label=f"Calibrated, trial {ctx['trial']}" if i == 0 else None)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([LAYER_NAMES[k] for k in order])
    ax.grid(axis="y", visible=False)
    top_weight = max([lead[f"norm_{k}"].max() for k in KEYS] + list(chosen.values()) + list(thesis.values()))
    ax.set_xlim(-0.02, top_weight + 0.04)
    ax.set_xlabel("Normalised weight")
    ax.legend(loc="lower right")
    ax.set_title("Weights of the seven suitability layers", loc="left")
    return save(fig, ctx, "calibrated_drivers")


def fig_fit_to_the_record(ctx):
    import matplotlib.pyplot as plt

    mdir = ctx["measures_dir"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(FULL_WIDTH, 4.0))
    draw_record(a, ctx)
    draw_runs(a, os.path.join(mdir, "sites"), BLUE, "Simulated ellipses")
    map_axes(a)
    a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2)
    panel(a, "a", "Each run's ellipse against the record's")

    runs = read_csv(ctx, "analysis", f"measures_trial{ctx['trial']}", "runs.csv")
    med = runs["score_obj_func"].median()
    r = runs.iloc[(runs["score_obj_func"] - med).abs().argsort().iloc[0]]
    seed = int(r["seed"])
    x, y, v = load_sites(os.path.join(mdir, "sites", f"run_{seed}.csv"))
    b.scatter(x[v == 1] / 1000, y[v == 1] / 1000, s=5, color=BLUE, lw=0, zorder=2,
              label=f"Simulated sites ({int((v == 1).sum())})")
    b.scatter(x[v == 2] / 1000, y[v == 2] / 1000, s=16, marker="^", color=ORANGE, lw=0, zorder=3,
              label=f"Simulated compounds ({int((v == 2).sum())})")
    el = ellipse_km(x, y)
    if el:
        b.plot(el[0], el[1], color=BLUE, lw=1.4, zorder=4, label="Run's ellipse")
        b.plot([el[2]], [el[3]], marker="+", color=BLUE, ms=9, mew=1.6, zorder=5)
    draw_record(b, ctx, points=False)
    b.set_xlim(a.get_xlim())
    b.set_ylim(a.get_ylim())
    map_axes(b)
    b.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2)
    panel(b, "b", f"One run of median score (seed {seed}, {r['score_obj_func']:.3f})")
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
    import numpy as np

    d = read_csv(ctx, "sensitivity", "null", "runs.csv")
    piv = d.pivot_table(index="seed", columns="arm", values="score").dropna()
    cal, eq = piv["calibrated"].to_numpy(float), piv["equal_weights"].to_numpy(float)

    fig, (a, b) = plt.subplots(1, 2, figsize=(FULL_WIDTH, 3.9), gridspec_kw={"width_ratios": [1, 1.6]})
    for c, e in zip(cal, eq):
        a.plot([0, 1], [c, e], color=AXIS, lw=0.6, zorder=1)
    a.scatter(np.zeros(len(cal)), cal, s=14, color=BLUE, lw=0, zorder=3)
    a.scatter(np.ones(len(eq)), eq, s=14, color=ORANGE, lw=0, zorder=3)
    for x, vals, col, side in ((-0.25, cal, BLUE, "right"), (1.25, eq, ORANGE, "left")):
        m, sd = vals.mean(), vals.std(ddof=1)
        a.errorbar([x], [m], yerr=[sd], fmt="o", color=col, ms=5, capsize=3, lw=1.2, zorder=4)
        a.text(x - 0.09 if side == "right" else x + 0.09, m, f"{m:.3f}", ha=side, va="center",
               fontsize=7, color=INK)
    a.set_xticks([0, 1])
    a.set_xticklabels(["Calibrated\nweights", "Equal\nweights"])
    a.set_xlim(-0.75, 1.75)
    a.grid(axis="x", visible=False)
    a.set_ylabel("Composite error")
    red = read_json(ctx, "sensitivity", "null", "headline.json").get("reduction_pct_vs_calibrated_arm")
    if isinstance(red, (int, float)):
        a.text(0.5, 0.99, f"{red:.0f}% less error with calibrated weights", transform=a.transAxes,
               ha="center", va="top", fontsize=7, color=INK2)
    panel(a, "a", f"Composite error, {len(cal)} runs paired by seed")

    draw_record(b, ctx)
    draw_runs(b, path_of(ctx, "sensitivity", "null", "calibrated", "sites"), BLUE, "Calibrated weights")
    draw_runs(b, path_of(ctx, "sensitivity", "null", "equal_weights", "sites"), ORANGE, "Equal weights")
    map_axes(b)
    b.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2)
    panel(b, "b", "Each run's ellipse and centre against the record's")
    return save(fig, ctx, "null_baseline")


def fig_run_length(ctx):
    import matplotlib.pyplot as plt

    y = read_csv(ctx, "sensitivity", "horizon", "yearly.csv")
    ck = read_csv(ctx, "sensitivity", "horizon", "checkpoints.csv")
    targets = read_csv(ctx, "sensitivity", "horizon", "targets.csv")
    last = int(y["year"].max())
    obs_sites, obs_enc = ctx["calib"]["sites"], ctx["calib"]["enclosed"]
    obs_share = 100 * obs_enc / obs_sites
    y = y.copy()
    y["share"] = 100 * y["enclosed"] / y["sites_t0.6"].where(y["sites_t0.6"] > 0)
    n = y["seed"].nunique()

    fig, axes = plt.subplots(2, 2, figsize=(FULL_WIDTH, 5.4))
    (a, b), (c, e) = axes

    band(a, y.pivot_table(index="year", columns="seed", values="sites_t0.6"), BLUE,
         label=f"Median, 5–95% of {n} runs")
    ref_line(a, obs_sites, f"Record: {obs_sites} sites")
    row = targets[targets["measure"] == "sites_t0.6"]
    if len(row) and row["first_year_mean"].notna().iloc[0]:
        fy, sd = float(row["first_year_mean"].iloc[0]), float(row["first_year_sd"].iloc[0])
        a.plot([fy], [obs_sites], "o", color=INK, ms=5, zorder=5)
        a.text(fy, obs_sites, f"year {fy:.0f} ± {sd:.0f}  ", ha="right", va="bottom", fontsize=7,
               color=INK)
    year_line(a, 75, "75 years")
    a.set_ylabel("Sites (threshold 0.6)")
    a.legend(loc="upper left", bbox_to_anchor=(0.0, 0.88))
    panel(a, "a", "Sites")

    band(b, y.pivot_table(index="year", columns="seed", values="cumulative_locations"), BLUE)
    ref_line(b, obs_enc, f"Record: {obs_enc} compounds", where="top")
    year_line(b, 75, "75 years")
    b.set_ylim(0, obs_enc + 6)
    b.set_ylabel("Compound locations")
    panel(b, "b", "Compound locations")

    start = 30
    band(c, y[y["year"] >= start].pivot_table(index="year", columns="seed", values="share"), BLUE)
    ref_line(c, obs_share, f"Record: {obs_share:.1f}%")
    year_line(c, 75, "75 years")
    c.set_xlim(start, last)
    c.set_ylim(0, 40)
    c.set_ylabel("Compound share of sites (%)")
    panel(c, "c", f"Compound share (from year {start})")

    g = ck[ck["year"] >= start].groupby("year")
    for col, colour, name in (("score", BLUE, "composite"), ("spatial_error", ORANGE, "spatial"),
                              ("site_type_error", AQUA, "site-type")):
        m, s = g[col].mean(), g[col].std(ddof=1)
        e.fill_between(m.index, m - s, m + s, color=colour, alpha=0.15, lw=0)
        e.plot(m.index, m.values, "o-", color=colour, ms=3, lw=1.4, label=name)
        e.text(m.index[-1] + 2, m.values[-1], " " + name, color=INK2, fontsize=7, va="center")
    year_line(e, 75, "75 years")
    e.set_xlim(start, last + 22)
    e.set_ylim(0, 0.55)
    e.set_ylabel("Error (mean ± SD)")
    e.legend(loc="upper right", bbox_to_anchor=(0.86, 1.0))
    panel(e, "d", f"Errors, every 10 years (from year {start})")

    for ax in (a, b, c, e):
        ax.set_xlabel("Years")
    for ax in (a, b):
        ax.set_xlim(0, last)
    return save(fig, ctx, "run_length")


def fig_site_threshold(ctx):
    import matplotlib.pyplot as plt
    import numpy as np

    classes = [(0.1, "0.25", "≥ 0.25 units (thresholds 0.1–0.2)"),
               (0.3, "0.5", "≥ 0.5 (0.3–0.5)"),
               (0.6, "0.75", "≥ 0.75 (0.6–0.7, calibration)"),
               (0.8, "1.0", "≥ 1.0 (0.8–1.0)")]
    y = read_csv(ctx, "sensitivity", "horizon", "yearly.csv")
    targets = read_csv(ctx, "sensitivity", "horizon", "targets.csv")
    th = read_csv(ctx, "sensitivity", "threshold", "thresholds.csv")
    last = int(y["year"].max())
    obs_sites, obs_enc = ctx["calib"]["sites"], ctx["calib"]["enclosed"]
    obs_share = 100 * obs_enc / obs_sites

    fig, (a, b, c) = plt.subplots(1, 3, figsize=(FULL_WIDTH, 3.2), gridspec_kw={"width_ratios": [1.7, 1, 1]})
    for (t, _short, label), colour in zip(classes, RAMP):
        col = f"sites_t{t:.1f}"
        m = y.groupby("year")[col].mean()
        a.plot(m.index, np.where(m.values > 0, m.values, np.nan), color=colour, lw=1.6, label=label)
        row = targets[targets["measure"] == col]
        if len(row) and row["first_year_mean"].notna().iloc[0]:
            a.plot([float(row["first_year_mean"].iloc[0])], [obs_sites], "o", color=colour, ms=5,
                   mec="white", mew=0.8, zorder=5)
    a.set_yscale("log")
    ref_line(a, obs_sites, f"Record: {obs_sites} sites")
    year_line(a, 75, "75 years")
    a.set_xlim(0, last)
    a.set_xlabel("Years")
    a.set_ylabel(f"Sites (mean of {y['seed'].nunique()} runs, log scale)")
    a.legend(loc="lower right", title="A site needs", title_fontsize=7)
    panel(a, "a", "Sites by year at each threshold")

    xs = np.arange(len(classes))
    for ax, colname, ylabel, ref, log in ((b, "enclosed_share_pct", "Compound share (%, log scale)", obs_share, True),
                                          (c, "score", "Composite error", None, False)):
        for i, ((t, _short, _label), colour) in enumerate(zip(classes, RAMP)):
            v = th.loc[(th["threshold"] - t).abs() < 1e-9, colname].to_numpy(float)
            ax.scatter(i + jitter(len(v), 0.12, seed=i), v, s=6, color=colour, alpha=0.5, lw=0, zorder=2)
            ax.errorbar([i + 0.28], [v.mean()], yerr=[v.std(ddof=1)], fmt="o", color=colour, ms=4.5,
                        capsize=2, lw=1.1, zorder=3)
        if ref is not None:
            ref_line(ax, ref, f"Record: {ref:.1f}%")
        if log:
            ax.set_yscale("log")
        ax.set_xticks(xs)
        ax.set_xticklabels([s for _t, s, _l in classes])
        ax.set_xlim(-0.5, len(classes) - 0.3)
        ax.grid(axis="x", visible=False)
        ax.set_xlabel("Units of use a site needs")
        ax.set_ylabel(ylabel)
    panel(b, "b", "Compound share, 75 years")
    panel(c, "c", "Composite error, 75 years")
    return save(fig, ctx, "site_threshold")


def fig_households(ctx):
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    d = read_csv(ctx, "sensitivity", "households", "runs.csv")
    obs_sites, obs_enc = ctx["calib"]["sites"], ctx["calib"]["enclosed"]
    obs_share = 100 * obs_enc / obs_sites
    ns = sorted(d["households_start"].unique())
    panels = [("score", "a", "Composite error", None, ""),
              ("iou", "b", "Ellipse overlap (IoU)", None, ""),
              ("sites", "c", "Sites after 75 years", obs_sites, f"Record: {obs_sites} sites"),
              ("enclosed_share_pct", "d", "Compound share (%)", obs_share, f"Record: {obs_share:.1f}%")]
    fig, axes = plt.subplots(2, 2, figsize=(FULL_WIDTH, 4.8))
    for ax, (col, letter, title, ref, ref_text) in zip(axes.flat, panels):
        for i, n in enumerate(ns):
            v = d.loc[d["households_start"] == n, col].to_numpy(float)
            ax.scatter(n + jitter(len(v), 0.45, seed=i), v, s=7, color=BLUE, alpha=0.35, lw=0, zorder=2)
        m, s = means_by(d, "households_start", col)
        ax.errorbar(m.index, m.values, yerr=s.values, fmt="o-", color=INK, ms=4, lw=1.0, capsize=2, zorder=3)
        if ref is not None:
            ref_line(ax, ref, ref_text)
        ax.set_xticks(ns)
        ax.set_xlabel("Households")
        ax.set_ylabel(title)
        panel(ax, letter, title)
    a = axes.flat[0]
    if 9 in ns:
        m, _s = means_by(d, "households_start", "score")
        a.annotate("calibrated", xy=(9, m.loc[9]), xytext=(0, -20), textcoords="offset points", ha="center",
                   fontsize=7, color=INK2, arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.8})
    handles = [Line2D([], [], marker="o", ls="", color=BLUE, alpha=0.5, ms=3, label="One run"),
               Line2D([], [], marker="o", ls="-", color=INK, ms=4, label=f"Mean ± SD ({d['seed'].nunique()} runs)")]
    axes.flat[1].legend(handles=handles, loc="upper right")
    return save(fig, ctx, "households")


def fig_territory(ctx):
    import matplotlib.pyplot as plt
    import numpy as np

    d = read_csv(ctx, "sensitivity", "territory", "runs.csv")
    fig, (a, b) = plt.subplots(1, 2, figsize=(FULL_WIDTH, 3.9), gridspec_kw={"width_ratios": [1.5, 1]})
    draw_record(a, ctx)
    draw_runs(a, path_of(ctx, "sensitivity", "territory", "calibrated", "sites"), BLUE, "Flexible territory")
    draw_runs(a, path_of(ctx, "sensitivity", "territory", "fixed_territory", "sites"), ORANGE, "Fixed territory")
    map_axes(a)
    a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2)
    panel(a, "a", "Each run's ellipse and centre against the record's")

    xmax = d["spatial_error"].max() * 1.05
    ymax = d["site_type_error"].max() * 1.1
    xmin = max(0.0, d["spatial_error"].min() * 0.9)
    for comp in (0.15, 0.20, 0.25, 0.30):
        xs = np.linspace(xmin, xmax, 50)
        ys = 2 * comp - xs  # composite = (spatial + site-type) / 2
        keep = (ys >= 0) & (ys <= ymax)
        if keep.any():
            b.plot(xs[keep], ys[keep], ls="--", lw=0.8, color=AXIS, zorder=1)
            b.text(xs[keep][-1], ys[keep][-1], f" {comp:.2f}", fontsize=6.5, color=MUTED, va="center")
    for arm, colour, label in (("calibrated", BLUE, "Flexible"), ("fixed_territory", ORANGE, "Fixed")):
        r = d[d["arm"] == arm]
        b.scatter(r["spatial_error"], r["site_type_error"], s=12, color=colour, alpha=0.7, lw=0, zorder=3,
                  label=f"{label}, one run")
        b.plot([r["spatial_error"].mean()], [r["site_type_error"].mean()], "o", color=colour, ms=7,
               mec="white", mew=1.0, zorder=4)
    b.set_xlim(xmin, xmax + 0.03)
    b.set_ylim(0, ymax)
    b.set_xlabel("Spatial error (1 − IoU)")
    b.set_ylabel("Site-type error")
    b.legend(loc="upper right")
    b.text(0.02, 0.02, "dashed: equal composite error; large dots: means", transform=b.transAxes,
           fontsize=6.5, color=MUTED)
    panel(b, "b", "Two routes to the same score")
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
        "results_dir": results_dir, "trial": args.trial, "params": params, "obs": obs,
        "obs_ellipse": ellipse_km(obs[0], obs[1]),
        "calib": {"sites": len(gdf), "enclosed": int((gdf["value"] == 2).sum())},
        "measures_dir": os.path.join(results_dir, "analysis", f"measures_trial{args.trial}"),
        "out_dir": os.path.abspath(args.out_dir or os.path.join(results_dir, "figures")),
    }
    os.makedirs(ctx["out_dir"], exist_ok=True)
    say(f"Record: {calib_shp} ({ctx['calib']['sites']} sites, {ctx['calib']['enclosed']} compounds)")
    style()

    written, failed = [], []
    for name in args.only or list(FIGURES):
        try:
            written += FIGURES[name](ctx)
            say(f"  {name}: done")
        except Exception:
            failed.append(name)
            say(f"  {name}: FAILED\n{traceback.format_exc()}")
    say(f"\n{len(written) // 2} figure(s) in {ctx['out_dir']}")
    for p in written:
        if p.endswith(".png"):
            say(f"  {os.path.basename(p)}")
    if failed:
        say(f"Failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
