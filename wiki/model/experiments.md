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
| Time horizon (cell 3) | one run, 150 y, scored every 10 y; rainfall years recycle in the same shuffled order after the 75 years (`sensitivity_model.py` L399, L945), reuse intended (Itay, 2026-10-12: "for longer runs … I reused some of the years"), but not the exact replay, which should be a new shuffle, "not critical at all" (Itay, 2026-10-13); App. 5 §A5.7.2 does not mention the reuse | 42 | composite falls to year 75 mainly through ratio error; spatial error 0.27–0.32, drifting up after year 100; near-complete coverage by years 100–150 |
| Number of agents (cell 5) | 5, 15, 20 agents; 5 × 75 y each | 1000 + 100n + i | 5 too few sites; 15–20 score better but cover "practically the entire valid landscape" (App. 5 §A5.7.3) |
| Territory (cell 7) | fixed vs flexible; 5 × 75 y each | 2000 + 100·fixed + i | mean ~0.25 fixed vs ~0.21 flexible; fixed far more variable, one run 0.41 |
| Site threshold | 0.1–1.0 on one run's output | — | 245 sites at 0.6; ~6,000 at 0.1–0.2; 73 at 0.8–1.0; enclosure share <1% → 16.7% (0.6) → 56% |

- **Outputs**: `D:\itay\ABM\Results\sensitivity\{time_horizon,agents,territory,null_baseline}\…` and CSVs (cell 11). **Present in repo**: no.

## 4. Smoke test
[`Code/test.ipynb`](../../Code/test.ipynb): 2 years, random Dirichlet weights, seed 42, `plot=True`, writing to `Results/test_run`. Uses mock zero rasters if the yearly data are missing. Not a reported experiment.

## Things to check
- Re-running after the separate PR, which changes calibrated behaviour (separate-PR list in `log.md`). Asked whether the calibration and the §5.6 tests will be re-run or the reported results will stand as produced by the current code. Itay, 2026-10-13: They may re-run.
- Seeds for the null baseline. App. 5 §A5.7.1 says each iteration used "the same deterministic seed generation procedure as calibration (seed = trial × 100 + iteration)". The notebook uses `3000 + i` (cell 9).
  - Asked whether App. 5 should say 3000 + i. Itay, 2026-10-13: Which notebook? Be specific.
  - `Code/sensitivity_analysis.ipynb`, cell 9 (`run_null_baseline`), line 29 of the cell: `seed = 3000 + i`. Open: asked again.
- The site-threshold test (Ch. 5 §5.6, the fourth test) has no section in App. 5 §A5.7, which covers the null baseline, time horizon, population and territory, though Ch. 5 §5.6 says "Full methods, tables, and figures appear in Appendix 5.7". It also has no code in the repository, and `to_gdf` hard-codes 0.6 (`model.py`, L1133).
  - Also raised on [site classification](../mechanisms/site-classification.md); deferred here (agreed, Itay, 2026-10-13).
  - Asked how the sweep was run. Itay, 2026-10-13: Manually.
  - For the write-up: Ch. 5 §5.6 refers to App. 5 §A5.7 for "Full methods, tables, and figures", which has no section on this test.
- The sensitivity tests run `sensitivity_model.py`, which differs from the calibrated `model.py` beyond the two switches: overlap rule, Year-0 territory, failure handling and replacement (see [inventory](inventory.md#how-the-two-model-files-differ)). How do these differences bear on comparing §5.6 results with the calibration score?
  - Year-0 rule: a mistake in `sensitivity_model.py` (Itay, 2026-10-12). By the inventory check (2026-10-12), roughly half of the Year-0 territories in the sensitivity runs were probably 20 cells rather than 25. Its effect on §5.6: deferred to this page (agreed 2026-10-12).
  - Asked whether §5.6 should say that the tests ran on `sensitivity_model.py` and how it differs (overlap rule, Year-0 radius, failure handling, replacement). Itay, 2026-10-13: No. This closes the Year-0 item too.
- The null-baseline comparison sets the null mean (30 runs) against `study.best_value` (cell 9), which is the lowest mean among 143 completed trials. The 30-replicate re-run of the best trial gave 0.213 (Ch. 5 §5.5.4). Which figure should the comparison use?
  - Checked 2026-10-13 in `null_baseline_scores.csv` (Itay's results folder on Drive): 30 scores, mean 0.318, SD 0.027, 95% CI 0.309–0.328, as reported. The "36.7% reduction" uses 0.2013; against the 30-replicate 0.213 it would be 33.1%.
  - Itay, 2026-10-13: The 30-replicate re-run (0.213).
  - For the write-up: Ch. 5 §5.6 ("The best calibrated trial, at 0.201, … a 36.7% reduction in error") and App. 5 Table A5.7 ("Best calibrated 0.2013", "Improvement 36.7%") should use 0.213 and 33.1%. For the separate PR: cell 9 of `sensitivity_analysis.ipynb` compares with `study.best_value` (line 62 of the cell); compare with the 30-replicate mean instead.
- Fixed-territory runs may gain households when a household fails ([crisis and replacement](../mechanisms/crisis-and-replacement.md), Things to check). That would affect the territory comparison.
  - Confirmed by reading (2026-10-12): each failure adds a household in fixed mode. Itay (2026-10-12): the population should be constant. To fix in the separate PR.
- Pasture input in every reported run. Calibration, replication and all sensitivity tests fed yearly array 0 (the year's rainfall membership) to herds as pasture instead of array 2 ([suitability surface](../mechanisms/suitability-surface.md), Things to check). Itay (2026-10-12): "a big red flag"; fix in a separate PR.
- Parallel trials and seeds (deferred here from the calibration-objective round, agreed 2026-10-12). Calibration trials ran in parallel threads sharing the global `random` and `np.random` generators. Itay does not think they interfered with each other. Trial 173's ten calibration replicates used seeds 17300–17309. calibration.ipynb cell 6, as it stands, runs the 30 validation replicates one after another with seeds `best_trial × 100 + i` = 17300–17329, which would repeat those ten seeds; Ch. 5 §5.5.4 calls them "30 additional replicates". Which seeds did the validation runs use? If the first ten repeat the calibration's seeds, comparing their scores with trial 173's replicates (recoverable from the running means in `opt_run.db`) would test the no-interference reply, provided the code and data did not change in between.
  - Checked 2026-10-13 through the Drive connector (Itay's results folders, read-only). Trial 173's ten calibration replicates (`trial_173/iter_0…9`, 2026-03-01, about 50 min each) and the validation runs (`trial_best_params/iter_0…29`, 2026-03-05, one after another, about 14 min each) both have `household_data.csv`. With the same seeds (17300–17309, if cell 6 ran as it stands) the files would be identical, but all ten pairs differ in size (for example iter_0: 423,059 against 435,378 bytes). The validation folders hold no per-run scores (only maps, the CSV and the weights), so scores cannot be compared directly.
  - Why the runs differ, whatever the threads did: `NomadModel` calls `super().__init__()` without a seed (L955). In Mesa 3.0.0 and 3.3.0 (`mesa/model.py › Model.__init__`) the model's own generator `self.random` is then seeded from operating-system entropy, and `agents_by_type[...]` uses that generator (`random=self.random`), so `shuffle_do("step")` (L1015) and `shuffle_do("year_initiation")` (L1043) put households in a different order on every run. Seeding `random` and `np.random` (L1250–1252) does not reach it. No run in calibration, validation or sensitivity can be reproduced exactly from its seed, and seed-matched runs cannot test the no-interference reply.
  - Itay, 2026-10-13 (on the chat summary of this check): the validation runs were not meant to repeat the calibration replicates, as discussed in the previous session. That is so: they are "30 additional replicates" (Ch. 5 §5.5.4; calibration-objective round, 2026-10-12), and the size comparison was only the deferred no-interference check. With Mesa's generator unseeded, the validation runs are distinct from the calibration replicates even if cell 6 reused seeds 17300–17309.
  - Proposed: the separate PR passes each run's seed to Mesa (`super().__init__(seed=seed)` through `NomadModel`) so runs reproduce; App. 5 §A5.3's reproducibility statement is revised; the no-interference check is closed as untestable with these runs. Itay, 2026-10-13: OK; don't revise the statement yet.
  - For the separate PR: seed Mesa's generator. The no-interference check is closed. App. 5 §A5.3 is left as it is for now (Itay).
- Time horizon is a single run (seed 42), as App. 5 §A5.7.2 states ("given its exploratory diagnostic purpose").
- Rainfall replay in the time-horizon run. With 75 years and `year % len(inds)` (`sensitivity_model.py` L399, L945), years 75–149 repeat years 0–74 in the same shuffled order, so the second half of the run replays the first half's rainfall exactly. Itay (2026-10-12, overview round) described the longer runs as reusing "some of the years". Raised in the overview round and deferred to this page (agreed 2026-10-12).
  - Asked whether the exact replay is intended. Itay, 2026-10-13: Not intended, should be shuffled, but it is not critical at all.
  - For the separate PR (low priority): a new shuffle of the year order for each further 75-year cycle (`sensitivity_model.py` L399, L945).
- Which run is "seed-173" (Ch. 5 Fig. 5.11)? Best-trial replicates use seeds `best_trial × 100 + i` with i = 0–29 (calibration.ipynb cell 6), and calibration replicates use i = 0–9. Seed 173 fits neither pattern unless the best trial number is 1 and i = 73.
  - Checked 2026-10-12 in the Optuna exports: trial 173 is the best trial (0.2013), so "seed-173" may name the trial rather than a seed. Raised in the calibration-objective round; to confirm in the experiments round.
  - Asked whether "seed-173" means trial 173. Itay, 2026-10-13: Yes, I don't remember which replicate.
  - For the write-up: the Fig. 5.11 caption should say trial 173 rather than "seed-173".
- calibration.ipynb cell 5 reads `trial_best_params`, which cell 6 creates, so the cells run out of order on a fresh run.
  - Asked whether to swap them in the separate PR. Itay, 2026-10-13: Yes.
