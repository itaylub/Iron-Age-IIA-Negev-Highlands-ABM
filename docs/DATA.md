# Data dictionary

Inputs consumed by the Nomad ABM. The canonical archive of these files
lives at **Zenodo: [10.5281/zenodo.20473345](https://doi.org/10.5281/zenodo.20473345)**
(bundled as `nomad-abm-data-v1.0.zip`). Fetch them on a fresh clone
with:

```bash
python scripts/download_data.py
```

This downloads the bundle, verifies its SHA-256, and extracts the
files into `Data/`. The legacy `.h5` / `.pkl` / `.tif` files documented
below are **not** in the Zenodo bundle; they live only on the author's
data machine.

This document is the single source of truth for the file layout the
model expects. Schemas and checksums below were captured by
`scripts/inspect_data.py` against the author's local `Data/` snapshot
and updated on every regeneration. Re-run the inspector to refresh.

## Coordinate system

All spatial layers are projected in **ITM (Israel Transverse Mercator,
EPSG:2039)**. Cell side length is **250 m**.

## Spatial extent

Common grid for all rasters: **318 rows × 280 columns = 89 040 cells**.
Arrays are indexed `[row, column]`, with row 0 at the northern edge.
The model builds its Mesa grid 280 cells wide and 318 high, with
Mesa's `y` running northward, and converts between the two with
`to_numpy_y` (`numpy_row = 317 − y`).

The binary `ext_raster.npy` mask marks the model extent, 52 012 cells
(about 3 251 km²): the Negev Highlands and the buffer around them. The
household count uses this area (3 251.54 km², `Num_agents`). The binary
`place_raster.npy` (37 555 cells, about 2 347 km²) restricts camps to
the Israeli part of the Negev Highlands; the band between the two masks
is the buffer.

## Files

Sizes and SHA-256 below are from the May 2026 snapshot used during
calibration (verified by `scripts/inspect_data.py`).

### Files the model loads at runtime

These are the **current** (October 2025 regeneration) inputs. The
`_10_25` suffix is a date stamp, not a window subset.

| File | Size | Loaded by | Notes |
|---|---|---|---|
| `yearly_data_10_25.h5` | 63.8 MB | `model.LazyYearlyData` | Lazy-loaded yearly stack. |
| `per_data_10_25.h5` | 1.5 MB | `model.load_permanent_data` | Permanent layers. |
| `ext_raster.npy` | 89 KB | `model` (`GlobalData.ext_raster`) | Binary `uint8` mask, 318 × 280. |
| `place_raster.npy` | 89 KB | `model` (`GlobalData.place_raster`) | Binary `uint8` mask, 318 × 280. |
| `P_for_calib.shp` (+ .shx/.dbf/.prj) | small | `model.obj_func` | Point shapefile, archaeological calibration targets. Shipped in the Zenodo bundle and extracted to `Data/P_for_calib.shp` by `scripts/download_data.py`, which is where the model looks by default. If it is stored elsewhere, point `NOMAD_ABM_CALIB_SHP` at it. |

### Legacy files (kept for reference; not loaded by current code)

| File | Size | Notes |
|---|---|---|
| `yearly_data.h5` | 87.0 MB | Earlier (pre-October-2025) regeneration of the yearly stack. 4 arrays per group instead of the current 3. |
| `per_data.h5` | 2.4 MB | Earlier permanent stack. 8 arrays per `group_1` instead of the current 6. |
| `distac_pw.tif` + `.tfw` | 0.6 MB + 93 B | Source raster (cost-distance to permanent water sources) from which `pw_distance` is derived; kept for traceability. |
| `cntrl_outputs.pkl` / `.pbz2` | 7.1 MB / 7.8 MB | Reference outputs from earlier runs used in analysis notebooks. |
| `yearly_outputs.pkl` | 35.6 MB | Cached processed year-by-year arrays from an earlier run. |

> **Zenodo plan:** the published archive should include only the
> current files (the four `*_10_25.h5` / `.npy` and the calibration
> shapefile). The legacy `.h5` / `.pkl` / `.tif` artifacts above can
> stay on the data machine; they aren't needed to reproduce
> published results.

## HDF5 internal layout

**Confirmed against the actual files via `scripts/inspect_data.py`**;
the model's `model.LazyYearlyData` and
`model.load_permanent_data` index into the structure shown
below.

### `yearly_data.h5` and `yearly_data_10_25.h5`

```
/group_<i>                  # one group per year, i = 0 .. 74 (75 years)
  /array_0   : float64 [318, 280]
  /array_1   : float32 [318, 280]
  /array_2   : float32 [318, 280]
  /array_3   : float32 [318, 280]    # legacy file only
/metadata                   # current file: num_groups = 75, arrays_per_group = 3
```

Notes:

- `yearly_data_10_25.h5` holds **75 years**, `group_0` through
  `group_74`, plus a top-level `metadata` group. An earlier version
  of this document listed 76 groups (`group_0` … `group_75`), counting
  `metadata` as a year. The group count of the legacy `yearly_data.h5`
  has not been re-checked.
- The model takes the number of years from
  `metadata.attrs['num_groups']` (`LazyYearlyData`), so a 75-year run
  uses every year once.
- Each group's datasets are named `array_<j>`. The model reads them
  positionally via `sorted(group.keys(), key=lambda x:
  int(x.split('_')[1]))` — so the order matters, not the names.
- The current (`_10_25`) file has 3 arrays per group; the legacy file
  has 4. The model code only uses the first three positions.
- Roles of the three arrays in each year:
  - `array_0`: the year's rainfall membership, the annual-rainfall
    layer of the suitability surface (`Yearly_rain` weight).
  - `array_1`: agricultural potential (`ag_ras`).
  - `array_2`: pasture, the permanent vegetation layer times the
    year's rainfall (about `veg_fit × array_0 / 10`). The model reads
    it as `veg_ras` for herd capacity and enclosure scoring
    (`pasture_layer`).
- `group_74`'s `array_2` has no-data cells (`-inf` and the
  `-1.8 × 10³⁰⁸` fill value), 359 of them inside `ext_raster`; the
  other groups are clean. `pasture_layer` sets them to 0 (no pasture).
- All groups have identical structure (`sample_structurally_uniform =
  true`).

### `per_data.h5` and `per_data_10_25.h5`

```
/group_1                    # single group (note: 1-indexed!)
  /array_0 .. /array_5      # 6 arrays in the current per_data_10_25.h5
                            #  (8 arrays in the legacy per_data.h5)
                            # all float32 [318, 280] except one float64
/metadata                   # current file: num_groups = 1, arrays_per_group = 6
```

Notes:

- The single permanent group is `group_1` (1-indexed). The model
  reaches it through `metadata`: `load_permanent_data` reads
  `group_<i + 1>` for `i` in `range(num_groups)`, and
  `Code/calibration.ipynb` (cell 1) reads `group_<num_groups>`.
- `metadata` is **read by the model**: `num_groups` and
  `arrays_per_group` here, and `num_groups` in the yearly file. The
  reads are unguarded, so a data file without a `metadata` group stops
  the model at loading.

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

`P_for_calib.shp` and its sidecars (`.shx`, `.dbf`, `.prj`) ship inside
the Zenodo bundle and are extracted to `Data/P_for_calib.shp` by
`scripts/download_data.py` — the location the model reads by default.

## Zenodo archive

The canonical archive is at
[10.5281/zenodo.20473345](https://doi.org/10.5281/zenodo.20473345).
The bundle (`nomad-abm-data-v1.0.zip`) contains exactly the five
current input files (`yearly_data_10_25.h5`, `per_data_10_25.h5`,
`ext_raster.npy`, `place_raster.npy`, and `P_for_calib.shp` +
sidecars). Fetch with:

```bash
python scripts/download_data.py
```

`scripts/download_data.py` verifies the bundle's SHA-256 before
extracting, so any tampering or corruption in transit is caught
automatically.

Future regenerations of the data should use Zenodo's *New version*
flow on the same record (the concept DOI stays stable, a new version
DOI is issued, and `scripts/download_data.py` gets a one-line bump).
See `docs/ZENODO_UPLOAD.md`.
