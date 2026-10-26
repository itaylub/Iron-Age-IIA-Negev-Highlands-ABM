# Calibration objective — code-level walkthrough

> This document explains the calibration objective as implemented in
> `Code/model.py` (`to_gdf`, `obj_func`, `objective_function`,
> `objective`). For the conceptual statement see the thesis,
> Chapter 5 §5.5.2 (calibration procedure) and §5.5.3 (target and
> simulated patterns), and Appendix 5 §A5.3 (implementation details),
> in [`thesis/Lubel_Itay_MA_Thesis_ABM.pdf`](../thesis/Lubel_Itay_MA_Thesis_ABM.pdf).
>
> Where the two differ, follow the code. One known difference: Ch. 5
> §5.5.2 writes the site-type term with *proportions* of enclosed
> compounds among all sites, while the code compares *ratios* of
> enclosed-compound sites to other sites. The ratio is the intended
> definition (Ch. 5 §5.5.3 also speaks of "the number of
> enclosed-compound sites relative to the number of other sites").

The calibration minimises a composite error, so **lower is better**
(0 = perfect match).

## 1. From a run to sites (`to_gdf`)

```python
yo_sum = sum(model_output.yearly_outputs)   # occupation signal summed over all years
yo_sum[yo_sum < 0.6] = 0                    # below the site threshold: no site
yo_sum[yo_sum > 0] = 1                      # value 1: site
for enclosure in model_output.enclosures:   # value 2: enclosed compound
    ...
    yo_sum[numpy_y, mesa_x] = 2
```

- Each year a main camp adds 0.5 to its cell, a nuclear-family camp
  0.25, and enclosure reuse or construction adds more (Ch. 5 §5.5.3).
  `model.yearly_outputs` holds one such raster per year.
- A cell is a site (value 1) once its summed signal reaches 0.6.
- Every cell that appears in `model.enclosures` (built or reused) is
  set to value 2, whatever its signal.
- Cells are converted to points in ITM (EPSG:2039) from the grid
  origin and the 250 m cell size.

The archaeological points (`Data/P_for_calib.shp`) carry the same
`value` field: 1 for other sites, 2 for sites with enclosed compounds.

## 2. Score of one run (`obj_func(gdf, gdf1, run_dir)`)

`gdf` holds the archaeological points and `gdf1` the simulated ones.
The function returns `(total_error, ratio_error)` and saves a plot of
both point sets and their ellipses as `spatial_similarity.png` in
`run_dir`.

### Spatial error

```python
def calculate_ellipse(points):
    if len(points) < 3: return np.mean(points, axis=0), np.median(points, axis=0), 0, 0, 0
    mean_center = np.mean(points, axis=0)
    cov = np.cov(points, rowvar=False)
    eigenvalues, eigenvectors = linalg.eigh(cov)      # sorted to decreasing order
    std_dev = np.sqrt(np.maximum(eigenvalues, 0)) * 2  # two standard deviations
    rotation = np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0])
    ...
iou = overlapping_area / union_area if union_area != 0 else 0
spatial_error = 1 - iou
```

- Each point set is summarised by its standard deviational ellipse:
  centred on the mean, semi-axes of two standard deviations along the
  covariance eigenvectors, oriented along the first eigenvector
  (Ch. 5 §5.5.2, after Yuill 1971).
- The ellipses are converted to shapely polygons, and their overlap is
  the Intersection over Union, `IoU = intersection / union`
  (equivalently `A_overlap / (A_overlap + A_symmetric difference)`,
  as Ch. 5 §5.5.2 writes it).
- `spatial_error = 1 − IoU`: 0 for identical ellipses, 1 for
  ellipses that do not overlap.
- Guardrails: with fewer than three points the ellipse has zero axes,
  so the IoU is 0 and the spatial error 1; with no simulated points at
  all the function returns `(1.0, 1.0)`. Neither happens in full
  75-year runs.

### Site-type (ratio) error

```python
t_ratio  = t2 / t1   if t1  != 0 else 0   # archaeological: value-2 count / value-1 count
t1_ratio = t21 / t11 if t11 != 0 else 0   # simulated:      value-2 count / value-1 count
ratio_error = abs(t_ratio - t1_ratio)
```

- Each record's site-type ratio is the number of enclosed-compound
  sites (value 2) divided by the number of other sites (value 1). The
  archaeological target is 32 : 430, about 1 : 13.4 (Ch. 5 §5.5.3).
- `ratio_error` is the absolute difference between the two ratios. It
  lies between 0 and 1 while other sites outnumber enclosed ones, as
  at the 0.6 threshold; it is not bounded by 1 in general.

### Composite

```python
total_error = (spatial_error + ratio_error) / 2
```

The two errors are weighted equally (Ch. 5 §5.5.2).

## 3. Score of one weight set (`objective_function`)

- Runs `n_iterations` replicates (10 in the calibration) of `n_years`
  years (75) with the same normalised weights, with seeds
  `trial × 100 + i` for replicate `i`.
- Each replicate is classified (`to_gdf`) and scored (`obj_func`).
  After each replicate the running mean of `total_error` is reported
  to Optuna (`trial.report`), so the MedianPruner can stop an
  unpromising trial early.
- The trial's score is the mean of the replicate scores (Ch. 5
  §5.5.2: "The ten scores are then averaged").
- Replicate outputs go to
  `Results/run/trial_<trial>/iter_<i>/` (`household_data.csv`, the
  weight JSON files, `spatial_similarity.png`).
- If the calibration shapefile is missing the function returns 1.0.

## 4. The Optuna objective (`objective`)

- Samples the seven weights as integers 0–7: `dist_to_kb`, `p_water`,
  `Mean_rain`, `slope_suitability` (permanent layers) and
  `return_to_site`, `humen_stress`, `Yearly_rain` (yearly layers).
- Returns 9999 if all seven are 0; otherwise divides each by their
  sum, so the weights sum to 1 (Ch. 5 §5.5.2; App. 5 §A5.3).
- Calls `objective_function` with `random_seed = trial.number`.

The study itself (TPE sampler, MedianPruner with
`n_startup_trials=10`, `n_warmup_steps=5`, SQLite storage) is set up
in `Code/calibration.ipynb`, cell 1.
