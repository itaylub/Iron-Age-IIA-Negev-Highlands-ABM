"""Build the calibration sites file from the sites table (thesis Appendix 1).

The model is calibrated against a point file of observed sites with a
``value`` field: 1 = other site, 2 = enclosed compound
(``model.obj_func``). This script makes that file from the sites table,
so the calibration uses the author's own classification:

    python scripts/make_calib_sites.py --xlsx "G:/My Drive/MA Thesis/Thesis_submission/appendices/Appendix 1. Sites.xlsx"

Classification (column ``Type``):
- "Enclosed Compound"  -> 2
- "Other"              -> 1
- "Enclosed Compound?" -> set by ``--questionable``: ``other`` (1, the
  default: a site, but not a confirmed compound), ``compound`` (2) or
  ``exclude`` (left out).

Model area (``--area``): which table sites lie in the modelled region.
- ``file`` (default): the table sites that coincide (within
  ``--tolerance`` m) with a point of ``--area-from``, by default the
  current ``Data/P_for_calib.shp``. Keeps the area identical to the
  earlier calibration, so the two differ only in which sites count.
- ``ext`` / ``place``: the table sites on a cell of ``ext_raster`` /
  ``place_raster`` with value 1.
The counts under all three are printed whatever is chosen.

Writes ``--out`` (default ``Data/P_for_calib_strict.shp``, EPSG:2039) with
fields ``value``, ``site_id`` and ``type``, and a CSV of every table site
with its classification and area tests next to it.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abm_parallel as ap  # noqa: E402

# Grid of the model rasters: lower-left corner and cell size as in
# model.to_gdf; 318 rows x 280 columns, row 0 at the north.
X0, Y0, CELL, NROWS, NCOLS = 139554.9251999901, 478515.53229999694, 250.0, 318, 280
TYPES = {"Enclosed Compound": 2, "Other": 1, "Enclosed Compound?": None}


def find_col(df, *names):
    low = {str(c).strip().lower(): c for c in df.columns}
    for n in names:
        if n.lower() in low:
            return low[n.lower()]
    raise SystemExit(f"Column not found; expected one of {names}. Columns: {list(df.columns)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--xlsx", required=True, help="the sites table (Appendix 1)")
    parser.add_argument("--out", default=os.path.join(ap.REPO_ROOT, "Data", "P_for_calib_strict.shp"))
    parser.add_argument("--questionable", choices=["other", "compound", "exclude"], default="other")
    parser.add_argument("--area", choices=["file", "ext", "place"], default="file")
    parser.add_argument("--area-from", default=os.path.join(ap.REPO_ROOT, "Data", "P_for_calib.shp"))
    parser.add_argument("--tolerance", type=float, default=1.0, help="metres, for --area file")
    args = parser.parse_args()

    ap.set_environment(os.path.join(ap.REPO_ROOT, "Results"))
    model = ap.import_model()
    import geopandas as gpd
    import numpy as np
    import pandas as pd
    from scipy.spatial import cKDTree

    df = pd.read_excel(args.xlsx)
    c_id = find_col(df, "Site_ID", "site id", "id")
    c_type = find_col(df, "Type")
    c_x = find_col(df, "X (ITM)", "X")
    c_y = find_col(df, "Y (ITM)", "Y")
    df = df.dropna(subset=[c_x, c_y]).copy()
    df["type_clean"] = df[c_type].astype(str).str.strip()
    unknown = sorted(set(df["type_clean"]) - set(TYPES))
    if unknown:
        raise SystemExit(f"Unknown types in '{c_type}': {unknown}. Expected {list(TYPES)}.")
    x = df[c_x].astype(float).to_numpy()
    y = df[c_y].astype(float).to_numpy()

    # Area tests
    col = np.floor((x - X0) / CELL).astype(int)
    row = NROWS - 1 - np.floor((y - Y0) / CELL).astype(int)
    in_grid = (col >= 0) & (col < NCOLS) & (row >= 0) & (row < NROWS)
    ext = np.load(model.EXT_RASTER_PATH)[0:NROWS, 0:NCOLS]
    place = np.load(model.PLACE_RASTER_PATH)[0:NROWS, 0:NCOLS]
    rr, cc = np.clip(row, 0, NROWS - 1), np.clip(col, 0, NCOLS - 1)
    df["in_ext"] = in_grid & (ext[rr, cc] == 1)
    df["in_place"] = in_grid & (place[rr, cc] == 1)
    ref = gpd.read_file(args.area_from)
    ref_xy = np.column_stack([ref.geometry.x, ref.geometry.y])
    dist, _ = cKDTree(ref_xy).query(np.column_stack([x, y]))
    df["in_file"] = dist <= args.tolerance
    # Points of the reference file with no table site at them
    back, _ = cKDTree(np.column_stack([x, y])).query(ref_xy)
    ref_unmatched = int((back > args.tolerance).sum())

    # Classification
    q = {"other": 1, "compound": 2, "exclude": None}[args.questionable]
    df["value"] = df["type_clean"].map(lambda t: TYPES[t] if TYPES[t] is not None else q)

    print(f"Sites table: {len(df)} sites; types: "
          + ", ".join(f"{t} {n}" for t, n in df["type_clean"].value_counts().items()))
    print(f"\nModel area, by method (sites / enclosed compounds / questionable):")
    for name in ("in_file", "in_ext", "in_place"):
        s = df[df[name]]
        print(f"  {name[3:]:<6} {len(s):>4} / {int((s['type_clean'] == 'Enclosed Compound').sum()):>3}"
              f" / {int((s['type_clean'] == 'Enclosed Compound?').sum()):>2}"
              + ("   <- used" if name == f"in_{args.area}" else ""))
    print(f"  ({ref_unmatched} points of {os.path.basename(args.area_from)} have no table site within "
          f"{args.tolerance:g} m)")

    sel = df[df[f"in_{args.area}"] & df["value"].notna()].copy()
    sel["value"] = sel["value"].astype(int)
    gdf = gpd.GeoDataFrame(
        {"value": sel["value"].to_numpy(), "site_id": sel[c_id].astype(int).to_numpy(),
         "type": sel["type_clean"].to_numpy()},
        geometry=gpd.points_from_xy(sel[c_x].astype(float), sel[c_y].astype(float)),
        crs="EPSG:2039",
    )
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    gdf.to_file(args.out)
    csv_path = os.path.splitext(args.out)[0] + "_sites.csv"
    df.rename(columns={c_id: "site_id"})[
        ["site_id", "type_clean", "value", c_x, c_y, "in_file", "in_ext", "in_place"]
    ].to_csv(csv_path, index=False)

    n2, n1 = int((gdf["value"] == 2).sum()), int((gdf["value"] == 1).sum())
    print(f"\nWrote {args.out}")
    print(f"  {len(gdf)} sites: {n2} enclosed compounds, {n1} other "
          f"({100 * n2 / len(gdf):.2f}% enclosed; enclosed-to-other ratio {n2 / n1:.4f}). "
          f"Questionable compounds: {args.questionable}.")
    print(f"  Every table site with its area tests: {csv_path}")


if __name__ == "__main__":
    main()
