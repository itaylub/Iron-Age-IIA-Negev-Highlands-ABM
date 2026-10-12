---
type: model
created: 2026-10-08
---

# Experiments

None of the result files are in the repository. `Results/` is untracked, and the notebooks write to `D:\itay\ABM\Results`. Reported results below are quoted or summarised from Ch. 5 and App. 5, attributed and located. The notebooks have no stored outputs.

## 1. Calibration (Optuna study `opt_2_26_v1`)
- **Question**: which of the seven suitability weights best reproduce the two target patterns (Ch. 5 §5.5).
- **Code**: [`Code/calibration.ipynb`](../../Code/calibration.ipynb) cell 1 → `model.objective` ([calibration objective](../mechanisms/calibration-objective.md)).
- **Settings**: integer weights 0–7; TPE sampler; MedianPruner(n_startup_trials = 10, n_warmup_steps = 5); 10 replicates × 75 years per trial; seeds `trial × 100 + i`; `n_jobs = 4`. The notebook's main block calls 13 trials, the function default is 200, and Ch. 5 §5.5.2 reports 200.
- **Outputs**: SQLite study `D:\itay\ABM\Results\run\opt_run.db`; per replicate `Results/run/trial_<n>/iter_<i>/household_data.csv` and `spatial_similarity.png`; `optimization_summary.csv` (cell 8).
- **Present in repo**: no. Itay's copies (2026-10-12): `G:\Other computers\My Computer\Drive\01_PROJECTS\MA_thesis\ABM\Results\opt_2_26_v1.csv`, `G:\Other computers\My Computer\Drive\01_PROJECTS\MA_thesis\ABM\Results\run\opt_run.db`, `G:\Other computers\My Computer\Drive\01_PROJECTS\MA_thesis\ABM\Results\run\optimization_summary.csv`, readable through the Drive connector. Trials ran in small batches over 2026-02-17 to 2026-03-05: 218 trials, of which 143 complete, 57 pruned and 18 failed; best trial 173 (checked 2026-10-12).
- **Reported** (Ch. 5 §5.5.4; App. 5 §A5.3): 200 trials, 143 completed, 57 pruned; best composite 0.2013; four workers, mean ~8.4 h per completed trial (range 3.0–19.8 h), ~12–13 days in total. Leading 19 trials < 0.21 share one weight structure (see [parameters](parameters.md#calibrated-weights)).

## 2. Best-trial replication (30 runs)
- **Code**: calibration.ipynb cell 6. Best parameters, 30 iterations, `plot=True`, seeds `best_trial × 100 + i`; summary in cell 8 (`best_params_30iter_stats.csv`).
- **Outputs**: `D:\itay\ABM\Results\trial_best_params\iter_<i>\…`; maps `year_<n>_map.png` at years 10–70 and the last year.
- **Present in repo**: no.
- **Reported** (Ch. 5 §5.5.4, §5.7, Fig. 5.10–5.11): mean composite 0.213 ± 0.021; spatial error 0.314 ± 0.039; site-type error 0.111 ± 0.021; IoU 0.68; simulated ellipse 1,602.43 km², axis ratio 1.25:1 against the observed 2.2:1; enclosed compounds ~17.6% of simulated sites against 6.93% observed. A sample run had 41 enclosure locations and 519 construction and reuse events, 26 of the locations built in years 0–25 (Fig. 5.10). Fig. 5.11 shows the occupation intensity of the "best-trial seed-173 output".

## 3. Sensitivity analysis
[`Code/sensitivity_analysis.ipynb`](../../Code/sensitivity_analysis.ipynb), on `sensitivity_model.py`, with the best weights loaded from the Optuna study (cell 1).

| Test | Settings in code | Seeds | Reported (Ch. 5 §5.6; App. 5 §A5.7) |
|---|---|---|---|
| Null baseline (cell 9) | all weights 1/7; 30 × 75 y | 3000 + i | mean 0.318, 95% CI 0.309–0.328; best calibrated 0.201; "36.7% reduction in error" |
| Time horizon (cell 3) | one run, 150 y, scored every 10 y; rainfall years recycle in the same shuffled order after the 75 years (`sensitivity_model.py` L399, L945), as Itay intended (2026-10-12: "for longer runs … I reused some of the years"); App. 5 §A5.7.2 does not mention the reuse | 42 | composite falls to year 75 mainly through ratio error; spatial error 0.27–0.32, drifting up after year 100; near-complete coverage by years 100–150 |
| Number of agents (cell 5) | 5, 15, 20 agents; 5 × 75 y each | 1000 + 100n + i | 5 too few sites; 15–20 score better but cover "practically the entire valid landscape" (App. 5 §A5.7.3) |
| Territory (cell 7) | fixed vs flexible; 5 × 75 y each | 2000 + 100·fixed + i | mean ~0.25 fixed vs ~0.21 flexible; fixed far more variable, one run 0.41 |
| Site threshold | 0.1–1.0 on one run's output | — | 245 sites at 0.6; ~6,000 at 0.1–0.2; 73 at 0.8–1.0; enclosure share <1% → 16.7% (0.6) → 56% |

- **Outputs**: `D:\itay\ABM\Results\sensitivity\{time_horizon,agents,territory,null_baseline}\…` and CSVs (cell 11). **Present in repo**: no.

## 4. Smoke test
[`Code/test.ipynb`](../../Code/test.ipynb): 2 years, random Dirichlet weights, seed 42, `plot=True`, writing to `Results/test_run`. Uses mock zero rasters if the yearly data are missing. Not a reported experiment.

## Things to check
- Seeds for the null baseline. App. 5 §A5.7.1 says each iteration used "the same deterministic seed generation procedure as calibration (seed = trial × 100 + iteration)". The notebook uses `3000 + i` (cell 9).
- The site-threshold test (Ch. 5 §5.6, the fourth test) has no section in App. 5 §A5.7, which covers the null baseline, time horizon, population and territory, though Ch. 5 §5.6 says "Full methods, tables, and figures appear in Appendix 5.7". It also has no code in the repository, and `to_gdf` hard-codes 0.6 (`model.py`, L1133).
- The sensitivity tests run `sensitivity_model.py`, which differs from the calibrated `model.py` beyond the two switches: overlap rule, Year-0 territory, failure handling and replacement (see [inventory](inventory.md#how-the-two-model-files-differ)). How do these differences bear on comparing §5.6 results with the calibration score?
  - Year-0 rule: a mistake in `sensitivity_model.py` (Itay, 2026-10-12). By the inventory check (2026-10-12), roughly half of the Year-0 territories in the sensitivity runs were probably 20 cells rather than 25. Its effect on §5.6: deferred to this page (agreed 2026-10-12).
- The null-baseline comparison sets the null mean (30 runs) against `study.best_value` (cell 9), which is the lowest mean among 143 completed trials. The 30-replicate re-run of the best trial gave 0.213 (Ch. 5 §5.5.4). Which figure should the comparison use?
- Fixed-territory runs may gain households when a household fails ([crisis and replacement](../mechanisms/crisis-and-replacement.md), Things to check). That would affect the territory comparison.
- Pasture input in every reported run. Calibration, replication and all sensitivity tests fed yearly array 0 (the year's rainfall membership) to herds as pasture instead of array 2 ([suitability surface](../mechanisms/suitability-surface.md), Things to check). Itay (2026-10-12): "a big red flag"; fix in a separate PR.
- Time horizon is a single run (seed 42), as App. 5 §A5.7.2 states ("given its exploratory diagnostic purpose").
- Rainfall replay in the time-horizon run. With 75 years and `year % len(inds)` (`sensitivity_model.py` L399, L945), years 75–149 repeat years 0–74 in the same shuffled order, so the second half of the run replays the first half's rainfall exactly. Itay (2026-10-12, overview round) described the longer runs as reusing "some of the years". Raised in the overview round and deferred to this page (agreed 2026-10-12).
- Which run is "seed-173" (Ch. 5 Fig. 5.11)? Best-trial replicates use seeds `best_trial × 100 + i` with i = 0–29 (calibration.ipynb cell 6), and calibration replicates use i = 0–9. Seed 173 fits neither pattern unless the best trial number is 1 and i = 73.
  - Checked 2026-10-12 in the Optuna exports: trial 173 is the best trial (0.2013), so "seed-173" may name the trial rather than a seed. Raised in the calibration-objective round; to confirm in the experiments round.
- calibration.ipynb cell 5 reads `trial_best_params`, which cell 6 creates, so the cells run out of order on a fresh run.
