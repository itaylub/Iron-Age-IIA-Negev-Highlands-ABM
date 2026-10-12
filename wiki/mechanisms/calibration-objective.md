---
type: mechanism
created: 2026-10-08
code: "model.py › obj_func, L1160–1235; objective_function, L1294–1339; objective, L1342–1392; Code/calibration.ipynb cell 1"
odd: "Purpose and patterns; Design concepts › observation; (calibration, outside ODD core)"
---

# Calibration objective and procedure

## What it does
**Score per run** (`obj_func`, L1160–1235), comparing the archaeological points (`gdf`, from `P_for_calib.shp`) with the simulated sites (`gdf1`, from [site classification](site-classification.md)):
- **Spatial error** = 1 − IoU of the two standard deviational ellipses. Each ellipse is centred on the mean, with semi-axes 2√λ from the covariance eigenvalues, oriented along the first eigenvector, and converted to a polygon (L1161–1172, L1201–1220).
- **Ratio error** = |(# value 2 / # value 1)_archaeological − (# value 2 / # value 1)_simulated| (L1224–1232).
- **Total** = (spatial + ratio) / 2, minimised. If there are no simulated sites, the function returns 1.0, 1.0 (L1182).

**Score per weight set** (`objective_function`, L1294–1339): 10 replicates of 75 years with seeds `trial × 100 + i`. The running mean is reported to Optuna after each replicate for pruning, and the final mean is returned.

**Search** (`objective`, L1342–1392; calibration.ipynb cell 1): seven integer weights 0–7 (TPE sampler), normalised to sum 1; an all-zero draw scores 9999. MedianPruner(`n_startup_trials=10`, `n_warmup_steps=5`). Study `opt_2_26_v1`, SQLite storage, `study.optimize(n_jobs=4)`.

## Where it lives
`model.py`, as in the frontmatter; [`Code/calibration.ipynb`](../../Code/calibration.ipynb) cells 1, 3, 5, 6, 8.

## Inputs and parameters
Equal weighting of the two errors; ellipse scale 2 SD; 10 replicates; 75 years; weight range 0–7; pruner settings; 200 trials (Ch. 5 §5.5.2). Targets (Ch. 5 §5.5.3): ellipse area 1,585.02 km², centroid 168,369.37 E, 515,592.33 N, axes 66.68 and 30.26 km, orientation 55.66°; 32 of 462 sites (6.93%) with enclosed compounds, "about 1:13.4".

## What it changes
Selects the weights of the [suitability surface](suitability-surface.md). Results are in [parameters](../model/parameters.md#calibrated-weights) and [experiments](../model/experiments.md).

## Assumption it encodes
Pattern-oriented modelling (Ch. 5 §5.5.1, citing Grimm et al. 2005 and Gallagher et al. 2021): matching two patterns at once is "aimed at reducing equifinality". The metrics avoid "the prediction of exact site locations"; the ellipse "allows the two distributions to be compared at the regional scale without penalising the model for the location of any individual site" (Ch. 5 §5.5.1). The two errors are "weighted equally to reflect their complementary diagnostic value" (Ch. 5 §5.5.2).

## Justification
Owner's documentation: Ch. 5 §5.5 and App. 5 §A5.3. Tools cited: Optuna (Akiba et al. 2019), TPE (Watanabe 2023), standard deviational ellipse (Yuill 1971). Ch. 5 §5.6 records a known limitation: "ellipse overlap does not account for the number of sites produced, so the more cells that register activity across the area of the observed ellipse, the greater the overlap and the better the score".

## My rationale
**My rationale** · Itay, 2026-10-12
> Q: The ratio error compares enclosure-to-other ratios (obj_func, L1224–1232), while Ch. 5 §5.5.2 defines it on proportions of all sites. Which definition do you intend for the journal version?

Ratio, it ranges always between 0 to 1 as there are always more other sites (value ==1).

## Things to check
- Ratio or proportion? Ch. 5 §5.5.2 defines `ratio_error = |p_archaeological − p_simulated|` with p "the site-type proportion", the share of enclosed compounds among all sites, and says it "ranges from 0 … to 1". Ch. 5 §5.5.3 defines the site-type ratio as "the number of enclosed-compound sites relative to the number of other sites", which is what the code computes (L1224–1230). A ratio difference is not bounded by 1.
  - Itay, 2026-10-12: Ratio (My rationale above). Ch. 5 §5.5.2's formula and App. 5 §A5.7.2's "enclosed compound proportions" are to be reworded.
  - The bound in the reply holds while simulated other sites outnumber enclosed ones. The code does not guarantee it: Ch. 5 §5.6's threshold test reports an enclosed share of 56% at thresholds 0.8–1.0, a ratio of about 1.3. At the calibration threshold of 0.6 the share is 16.7%.
  - Recorded with Itay's agreement (2026-10-12): the ratio error lies between 0 and 1 while other sites outnumber enclosed ones, as at the 0.6 threshold.
- Threads and seeds. `study.optimize(n_jobs=4)` (calibration.ipynb cell 1) runs Optuna trials as threads in one process. `run_model_opt` seeds the shared global `random` and `np.random` (L1250–1252), and every draw in the model uses those generators. Can trials running at the same time disturb each other's random streams? If so, does `seed = t × 100 + i` reproduce a calibration replicate when it is rerun alone? (App. 5 §A5.3: "ensuring full reproducibility".)
  - Asked whether the 200 reported trials ran with `n_jobs` above 1. Itay, 2026-10-12: No they did not. But I was sure it did not disturb one another.
  - Checked 2026-10-12 in `optimization_summary.csv` (Optuna trial export, on Drive). Trials 10–19 started together (2026-02-17 17:10:17) and ran side by side for about 19.5 hours. From trial 26 on, trials ran four at a time, a new one starting as one finished (e.g. trials 26–29 started 2026-02-18 17:07:16). App. 5 §A5.3 also says "With four workers running trials in parallel". So trials ran concurrently, 10 and then 4 at a time, as threads sharing the global `random` and `np.random` generators. Reading of the code, not tested by running: each replicate is still a valid stochastic run, but it cannot be reproduced from its seed alone.
  - Itay, 2026-10-12 (clarifying the reply above): I did not say they didn't. I said they did and I don't think they interrupted each other. I will consider (b) [each run with its own generator, in the separate PR]. (c) [re-running the best trial alone] already happened in the validation.
  - What (c) refers to (Ch. 5 §5.5.4): "To confirm that this result is not an artefact of a single fortunate set of random seeds, the best-scoring combination was re-run for 30 additional replicates", giving 0.213 ± 0.021 against the calibration's 0.2013. That tests robustness across new seeds, not whether a seed reproduces its score.
  - A further check of the no-interference reply is deferred to [experiments](../model/experiments.md) (agreed 2026-10-12): comparing trial 173's ten calibration replicates (seeds 17300–17309, `objective_function` L1309–1310) with runs that used the same seeds outside the parallel batch, if any exist.
- `objective` sets `CUDA_VISIBLE_DEVICES` per trial (L1348–1350). No GPU code is in the model.
  - Asked whether this can go in the separate PR. Itay, 2026-10-12: Yes.
- calibration.ipynb's main block calls `run_optimization(n_trials=13, n_jobs=4)`, while the function default is 200 trials with `n_jobs=10`. The study is loaded with `load_if_exists=True`, so the 200 trials reported (Ch. 5 §5.5.2) may have accumulated over several sessions. Is the notebook state the last of them?
  - Itay, 2026-10-12: As the 200 runs took very long, I did not run them all at once but, as written did small batches at each time (e.g. 13). The Optuna database contains 200 trials (see exported table "G:\Other computers\My Computer\Drive\01_PROJECTS\MA_thesis\ABM\Results\opt_2_26_v1.csv"; "G:\Other computers\My Computer\Drive\01_PROJECTS\MA_thesis\ABM\Results\run\opt_run.db"; "G:\Other computers\My Computer\Drive\01_PROJECTS\MA_thesis\ABM\Results\run\optimization_summary.csv").
  - Checked 2026-10-12 in both exports (read through the Drive connector). Trials 0–217: 143 complete, 57 pruned and 18 failed (0–9, 22–25, 56–59), so the 200 are the complete and pruned trials, as App. 5 §A5.3 says. They ran from 2026-02-17 to 2026-03-05. The best is trial 173 (0.2013), whose weights are the best-trial weights in [parameters](../model/parameters.md#calibrated-weights).
- Target ratio. Ch. 5 §5.5.3 gives "about 1:13.4"; App. 5 §A5.7.3 gives "1:13.3". 32/430 = 1:13.44.
  - Asked whether App. 5 should read 1:13.4. Itay, 2026-10-12: Yes.
- docs/objective_function.md describes a different objective (see [inventory](../model/inventory.md), Things to check). Itay (2026-10-12): the file is old; follow the code and the thesis. The code and Ch. 5 §5.5.2 still differ on ratio vs proportion, the owed rationale above; deferred here from the inventory round (agreed 2026-10-12).
- Ellipse fit. `calculate_ellipse` returns zero axes for fewer than three points (L1162), so the IoU would then be 0 and the spatial error 1.
  - Asked whether that is the intended scoring for runs with fewer than three simulated sites. Itay, 2026-10-12: It is a guardrail, but it does not happen in full runs of 75 years.
