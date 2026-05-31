# Data dictionary

Inputs consumed by the Nomad ABM. Until the Zenodo archive lands
(Phase 9 of the publication-readiness pass), these files live under
`Data/` on the author's data machine (`D:\itay\ABM\Data`) and are
**not committed to git** (large binaries plus the `.gitignore`
already excludes `*.h5`, `*.npy`, `*.shp`, `*.tif`, etc.).

This document is the single source of truth for the file layout the
model expects. Schemas and checksums below were captured by
`scripts/inspect_data.py` against the author's local `Data/` snapshot
and updated on every regeneration. Re-run the inspector to refresh.

## Coordinate system

All spatial layers are projected in **ITM (Israel Transverse Mercator,
EPSG:2039)**. Cell side length is **250 m**.

## Spatial extent

Common grid for all rasters: **318 columns × 280 rows = 89 040 cells**,
covering approximately **3 251.54 km²** of the Negev Highlands. The
binary `place_raster.npy` further restricts valid agent activity to
the Israeli portion of the highlands.

## Files

Sizes and SHA-256 below are from the May 2026 snapshot used during
calibration (verified by `scripts/inspect_data.py`).

### Files the model loads at runtime

| File | Size | Loaded by | Notes |
|---|---|---|---|
| `yearly_data_10_25.h5` | 63.8 MB | `nomad_abm.model.LazyYearlyData` | Lazy-loaded year stack used by the standard calibration run. |
| `per_data_10_25.h5` | 1.5 MB | `nomad_abm.model.load_permanent_data` | Permanent layers used by the standard calibration run. |
| `ext_raster.npy` | 89 KB | `nomad_abm.model` (`GlobalData.ext_raster`) | Binary `uint8` mask, 318 × 280. |
| `place_raster.npy` | 89 KB | `nomad_abm.model` (`GlobalData.place_raster`) | Binary `uint8` mask, 318 × 280. |
| `P_for_calib.shp` (+ .shx/.dbf/.prj) | small | `nomad_abm.model.obj_func` | Point shapefile, archaeological calibration targets. **Currently lives at `Data/points_all/P_for_calib.shp` — one folder below where the model's default looks.** Either copy it up to `Data/`, point `NOMAD_ABM_CALIB_SHP` at it, or set `paths.calib_shp` in `configs/default.yaml`. |

### Files retained for reference / Zenodo bundle

| File | Size | Use |
|---|---|---|
| `yearly_data.h5` | 87.0 MB | Full-history yearly stack (76 groups); the `_10_25` variant is a subset, but the full stack is needed to reproduce alternative-window experiments. |
| `per_data.h5` | 2.4 MB | Full-history permanent stack; analogous to `yearly_data.h5`. |
| `distac_pw.tif` + `.tfw` | 0.6 MB + 93 B | Source raster (cost-distance to permanent water sources) from which `pw_distance` is derived; kept for traceability. |
| `cntrl_outputs.pkl` / `.pbz2` | 7.1 MB / 7.8 MB | Reference outputs from earlier runs used in analysis notebooks. |
| `yearly_outputs.pkl` | 35.6 MB | Cached processed year-by-year arrays from an earlier run. |

## HDF5 internal layout

**Confirmed against the actual files via `scripts/inspect_data.py`**;
the model's `nomad_abm.model.LazyYearlyData` and
`nomad_abm.model.load_permanent_data` index into the structure shown
below.

### `yearly_data.h5` and `yearly_data_10_25.h5`

```
/group_<i>                  # one group per year, i = 0 .. 75 (76 groups)
  /array_0   : float64 [318, 280]
  /array_1   : float32 [318, 280]
  /array_2   : float32 [318, 280]
  /array_3   : float32 [318, 280]    # full-history file only
```

Notes:

- Groups are **0-indexed** (`group_0` through `group_75`).
- Each group's datasets are named `array_<j>`. The model reads them
  positionally via `sorted(group.keys(), key=lambda x:
  int(x.split('_')[1]))` — so the order matters, not the names.
- The `_10_25` subset retains 3 arrays per group; the full version
  retains 4. The model code only uses the first three positions.
- All groups have identical structure (`sample_structurally_uniform =
  true`).

### `per_data.h5` and `per_data_10_25.h5`

```
/group_1                    # single group (note: 1-indexed!)
  /array_0 .. /array_7      # 8 arrays in per_data.h5
  /array_0 .. /array_5      #  or 6 arrays in per_data_10_25.h5
                            # all float32 [318, 280] except one float64
/metadata                   # sibling group; not consumed by the model
```

Notes:

- The single permanent group is `group_1` (1-indexed), accessed in
  code as `f['group_1']`.
- `metadata` is a sibling top-level group present in the file but not
  read by the model.

## .npy and .tif files

| File | Shape | dtype | Range | Notes |
|---|---|---|---|---|
| `ext_raster.npy` | 318 × 280 | `uint8` | 0 / 1 | Binary mask (2 unique values). |
| `place_raster.npy` | 318 × 280 | `uint8` | 0 / 1 | Binary valid-placement mask. |
| `distac_pw.tif` | per `rasterio` metadata | — | walking hours | Cost-distance source. CRS confirmation deferred: requires `rasterio` (not installed in the author's Mesa env). |

## SHA-256 checksums

Used by `scripts/download_data.py` (Phase 9) to verify the Zenodo
bundle. **Regenerate by running `scripts/inspect_data.py` and copy
the `sha256` fields from the report.**

```text
cntrl_outputs.pbz2      c19300479c7a2d89d8b21739fd027d719b79cf9d584c6a096e68a7f3bef52517
cntrl_outputs.pkl       4c5bca27626121e38f7e79ddc575f580b8a4bb3370f7e7950fdf037a52b89267
distac_pw.tfw           a6e39ba66f1c944656482324a0c06b85fb0ae7cf31a3aca9c1ba0c5810f202bb
distac_pw.tif           2e8a0d178c39f8e03eb3a80d2e53c4c14790b874b75f662efdefba70b19a4362
ext_raster.npy          bb38c703b754961d5009814b80b33c843a2b3f87075fe8154d2e1117fe953f0f
per_data.h5             0edca83f4a8cb45f17cc6b4c8199e1ffb2f78fc60d38b5a967d56cb6e1038bcd
per_data_10_25.h5       0c5c1a191268de0d6cd8dfeb815a73ee46ec39ad61c8156a3a9f452d7325ca26
place_raster.npy        77f77f246f180604db2c3e6077e38d3106b47c1f1836ff5cb57b1f2934d57c1f
yearly_data.h5          5bdf2319c919913122e9915006df594fdba37169b7cf2ca23e5ca2a404e8d510
yearly_data_10_25.h5    e45c0f272fac39c038cc481ded64cba3c72c895da5e63fd88400569535f5340e
yearly_outputs.pkl      cf25483bcae98509c9bedf07458e66168d01ebbf80e5a8edf385b08ea457d9ac
```

`P_for_calib.shp` and its sidecars (`.shx`, `.dbf`, `.prj`) are not
yet in this manifest because the file currently sits at
`Data/points_all/P_for_calib.shp`; checksums will be added once it is
moved (or symlinked) to `Data/P_for_calib.shp` or its location is
fixed in `configs/default.yaml`.

## Zenodo plan (Phase 9)

When Phase 9 lands, all files listed above (including the calibration
shapefile) will be bundled into a single versioned `.zip`, uploaded
to Zenodo, and fetched by `scripts/download_data.py` using the
SHA-256s above. The repository itself will then carry only a tiny
synthetic fixture under `tests/fixtures/` for CI.
