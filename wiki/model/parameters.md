---
type: model
created: 2026-10-08
code_commit: 032c2a1fbd26ec47017c65939ca372e02a575938
previous_code_commit: 2249331932b0a42ec47c33bca0ac94f4b8728813
---

# Parameters

Values are copied from `Code/model.py` (line numbers at commit `032c2a1`, the code after the 18 fixes of PR 8; re-pinned 2026-10-26 from `2249331`). "Documented" gives the value and source label from App. 5 Table A5.4 (or Ch. 5 where the table is silent). A **≠** marks a documented value that differs from the code; details are under Things to check on the linked mechanism page. "PR 8 item N" marks a value or rule the fixes changed (separate-PR list in `log.md`); the Documented column still describes the thesis text, which the write-up list in `log.md` corrects. "—" means not documented. Except for the weights, all values are hard-coded literals and cannot be changed through arguments.

## Calibrated weights
Normalised integer weights, sampled 0–7 (`objective`, L1422–1436).

### Thesis calibration (code before PR 8)

| Weight (code key) | Layer | Best trial, integer (normalised) | Leading 19 trials, mean ± SD | Used by |
|---|---|---|---|---|
| `dist_to_kb` | distance to Tell el-Qudeirat (–Faynan corridor) | 7 (0.304) | 0.304 ± 0.005 | [suitability](../mechanisms/suitability-surface.md) |
| `p_water` | distance to permanent water | 1 (0.043) | 0.041 ± 0.010 | suitability |
| `Mean_rain` | long-term mean rainfall | 3 (0.130) | 0.132 ± 0.009 | suitability |
| `slope_suitability` | slope | 0 | 0 in all 19 | suitability |
| `return_to_site` | reuse potential | 7 (0.304) | 0.304 ± 0.005 | suitability |
| `humen_stress` | multi-annual resource exhaustion | 5 (0.217) | 0.217 ± 0.010 | suitability |
| `Yearly_rain` | current-year rainfall | 0 | 0 in all 19 | suitability |

Sources: best-trial integers from CHANGELOG [1.0.0] "Phase 6 follow-up", which cites "§4.6.4 of the thesis" (older numbering). Cluster means from Ch. 5 §5.5.4 ("the 19 trials scoring below 0.21"). Ch. 5 Fig. 5.9 (p. 169) shows the 19-trial means. The best trial's own integers appear only in the CHANGELOG. Best calibration score 0.2013; 30-replicate re-run 0.213 ± 0.021 (Ch. 5 §5.5.4).

### Calibration of the fixed code (October 2026)
The fixed code was recalibrated on the owner's PC with `scripts/calibrate.py` against `P_for_calib_strict.shp` (study `opt_fixed_strict_2026_10`; calibrated set: trial 197). The weights are to be copied here from the study's `analysis\rerun_top10.csv`, which is on the PC and has not been read in this session.

## Spatial and temporal
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Grid | 318 × 280 (rows × cols), from raster shape | `NomadModel.__init__` L1030–1031; `ensure_data_loaded` L192 | 318 × 280 cells, 250 m (A5.4) |
| Model area (for agent count) | 3,251.54 km² | `Num_agents` L290 | 3,251.54 km² (A5.4). The `ext_raster` area, buffer included; kept (Itay, 2026-10-12; [overview](overview.md), Things to check) |
| Run length | 75 years | `objective_function` L1370; notebooks; scripts | 75 years (A5.4; Ch. 5 §5.2.3) |
| Edge buffer for camps | 20 cells | `place_household` L349–352 | — |
| CRS origin, cell size | (139,554.93, 478,515.53), 250 m | `to_gdf` L1208 | ITM (Ch. 5 §5.2.1.1) |

## Population and initialisation
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Households | ⌊(3,251.54/18)/20⌋ = 9 | `Num_agents` L289–293 | 9 (A5.4; Ch. 5 §5.2.4, from Rosen & Finkelstein 1992) |
| Initial herd | Σ₁₀ ⌊N(105, 15)⌋ | `Household_Agent.__init__` L548–551 | ~105 per family, ~1,050 (A5.4, modified from Rosen & Finkelstein 1992) |
| Initial manpower | max(35, ⌊herd/20⌋); also for successors (PR 8 item 7) | L555–556 | Ch. 5 §5.2.2 |
| Initial surplus | 0 | L560–561 | Ch. 5 §5.2.4 ("no accumulated experience or surplus") |
| Year-0 territory radius | 25 | L1066, L1075 | — (≠ year_initiation's 20/25/30). Intended (Itay, 2026-10-12; [overview](overview.md), Things to check). `sensitivity_model.py` the same since PR 8 item 2 |
| Year-0 camp memory radius | 20 | L1076 | — (later years: the territory radius, L694). `sensitivity_model.py` the same since `5f415eb` |
| Random generators | two numpy generators per run from its seed (rainfall-year order; camp draws), Mesa's generator seeded with the same seed for all Python-level draws and the household order | `run_generators` L530–541; `NomadModel.__init__` L1027–1028; `run_model_opt` L1328–1330 | App. 5 §A5.3 (PR 8 items 10 and 17) |

## Suitability and occupation history ([suitability](../mechanisms/suitability-surface.md), [history layers](../mechanisms/occupation-history-layers.md))
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Slope cut-off | slope suitability < 1 → 0 | L520 | Ch. 5 §5.7 (mentioned) |
| Accumulator decay | 0.5 | `Yi_params` L451 | 0.5, Assumed (A5.4) |
| Weight for cells ≥ 2 | × 1.5 | L447–448 | — (heavily invested cells; Itay, 2026-10-13) |
| Smoothing window | circle of radius 20 cells, 1/(d+1)² (PR 8 item 15) | L456–461 | 5 km, Assumed (A5.4); a circle intended (Itay, 2026-10-13) |
| Exhaustion fuzzy range | 0 → 10, 2 → 0 | L473–478 | — (value 2: face validation, Itay, 2026-10-13) |
| Reuse multiplier | × 5 | L480 | — (face validation, Itay, 2026-10-13) |
| Pasture | yearly array 2, no-data cells 0 (PR 8 item 1) | `pasture_layer` L273–280; L1054, L1107 | array 2 is pasture (Itay, 2026-10-12) |
| Pasture reduction by exhaustion | `1 − 0.1 × min(10/stress − 1, 9)` | `move_year` L1111–1114 | — (owner's abstract understanding, Itay, 2026-10-13) |

## Memory and territorial attachment
([page](../mechanisms/memory-and-territorial-attachment.md))
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Centre update | 0.9 previous / 0.1 last year's camp; starts at the Year-0 camp (PR 8 item 14) | L663–669 | 90% / 10%, Assumed |
| Home-range bonus | 5.0 × exp(−D²/(2·50²)) | L990–995 | +5.0, σ 50, Assumed |
| Territory bonus, main-camp draw | 2.5/(d+1), d ≤ 20, around last year's territory | L1011–1018 | Assumed |
| Territory bonus, family-camp draws | +2.5 on the territory's cells (PR 8 item 14) | `place_members` L388 | Assumed |
| Memory quality threshold | 5 | L1004 | 5, Assumed |
| Current-year penalty | −0.5, also at each new family camp (PR 8 item 14) | L1001, L403 | −0.5, Assumed |
| Memory factor, time weight | 0.5, 1/√Δy | L1003–1008 | Ch. 5 §5.3.1 |
| Penalty cap for poor camps | q counts as no lower than 0.1, so at most 5 × w (PR 8 item 14) | L1008 | — |
| Memory retention | keep if age × U < 15 | L660 | < 15 always; ~15/age, Assumed |

## Placement and territory ([page](../mechanisms/camp-and-territory-placement.md))
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Selection exponent | 3 (negative values clipped to 0 first) | L333–334, L390 | Ch. 5 §5.3.1; face validation in the initial runs (Itay, 2026-10-12) |
| Territory radius | 20 / 25 / 30 at suitability ≥ 5.0 / 3.5–5.0 / < 3.5 | L674–680 | same, Assumed |
| Overlap threshold | re-draw when ≥ 25% of the radius-20 candidate area lies in this year's other territories (PR 8 item 3) | L360, L365–367; `overlap_territory` L325–328 | 25%, Assumed |
| Re-draw rule and guard | re-draw while crowded *or* poor, at most 100 draws, then the least crowded candidate, preferring those that pass the capacity test (PR 8 item 3) | L362–371 | — |
| Capacity test | `n` starts at 35; poor if < 1 | L366, L303–322 | — |
| Family camps per household | 9 (plus the main camp) | L687 | Ch. 5 §5.2.2: a household is "a tentative group of about ten nuclear families" |
| Camp signal / family signal | +0.5 / +0.25 | L286, L691 | Ch. 5 §5.5.3 |
| Camp surplus cost | −1 | L285 | — |

## Within-year degradation ([page](../mechanisms/within-year-degradation.md))
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Household D, P, radius | 0.5, 0.9, territory radius | L693 | D 0.5, P 0.9, Assumed (preliminary runs, Itay, 2026-10-13). P acts on the camp cell now that the kernel centre is 0 (PR 8 item 16) |
| Family D, P, radius | 0.3, 0.5, 11 | L689 | 0.3, 0.5, 11, Assumed |
| Distance | (\|dx\|+\|dy\|)/2 + 0.001; kernel centre 0 (PR 8 item 16) | L239–241 | Manhattan (A5.1–A5.2 caption) **≠**; the code is intended (Itay, 2026-10-13) |
| Floor | 0.0001 | L432–434 | 0.0001, Assumed |

## Herd dynamics ([page](../mechanisms/herd-dynamics.md))
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Goats per cell at PV 5 | 1.125 | L779 | 1.125, Rosen & Finkelstein 1992 |
| Evaluation area | the territory's cells (PR 8 item 12) | L776; `territory_pasture` L266–270 | 25, Assumed **≠**; intended: the territory (Itay, 2026-10-13) |
| Growth / decline thresholds | ratio > 1.1 / < 0.9 | L800, L809 | Ch. 5 §5.3.2 |
| Max growth rate | 0.2 × multipliers; realised rate capped at 0.2 (PR 8 item 12) | L801–804 | up to 20%, Literature-based (Dahl & Hjort, Itay, 2026-10-13; to validate) |
| Diminishing returns | 1 − herd/1500 | L802 | 1,000 cap, Assumed **≠**; the taper to 1,500 is intended, the text to be fixed (Itay, 2026-10-13) |
| Small-herd factor | 2 − herd/500 below 500 | L797–798 | Ch. 5 §5.3.2 |
| Grazing pressure | 10 − mean `stress_ras` over the territory, so heavy use slows growth and speeds decline (PR 8 item 12) | L783–794 | Itay, 2026-10-13 |
| Decline rate | (0.05 + 0.5·gap)(1 + pressure/20)·U(0.8,1.2), ≤ 0.3 | L810–816 | 10–30%, Literature-based; a typical range, not a floor (Itay, 2026-10-13) |
| Growth cap | 1.2 × capacity | L805 | — |

## Household economy ([page](../mechanisms/household-economy.md))
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Goats per person | 18 | L706, L750 | 18, modified from Rosen & Finkelstein 1992 |
| Agricultural offset | min(0.4, 0.04 × mean ag) | L705 | up to 40%, Rosen & Finkelstein 1992; Günther et al. 2021 |
| Surplus capacity area | the territory's cells (PR 8 item 13) | L710 | 25 (A5.4); intended: the territory (Itay, 2026-10-13) |
| Working-herd buffer | 1.5 | L716 | Ch. 5 §5.3.2 |
| Stress multiplier | 1 + 0.3 s | L717 | 15% × s (A5.4) **≠**; 0.3 (Ch. 5); 0.3 intended (Itay, 2026-10-13) |
| Productive herd | herd left after culling (PR 8 item 13) | L727 | Ch. 5 §5.3.2 |
| Products yield | 0.15 | L728–729 | Ch. 5 §5.3.2 ("adopted for simplicity") |
| Culling share, value | 0.8, 0.35 | L721–722 | Ch. 5 §5.3.2 |
| Carry-over | 0.7 (30% loss) | L733–734 | 30%, Assumed |
| Consumption | 1.2 × M, plus 5% of the available surplus when it is above 100 (PR 8 item 13) | L736–741 | 1.2, Assumed (luxury —); 5% only when surplus > 100 (Itay, 2026-10-13) |
| Surplus cap | 200 + 2.5 × M | L744 | Ch. 5 §5.3.2 |
| Large-surplus decay | min(0.25, 0.05 + 0.001(S − 100)) above 100; 1% below | L646–655 | 5–25%, Assumed (1% —; intended, Itay, 2026-10-13) |
| Livestock purchase | S > 80 and herd < 600; min(0.2 S, 40); 0.3 per head | L631–633, L763 | same, Assumed |
| Manpower deductions | −10, −herd//75 | L579–581 | — (migration; 1:75 from literature, to check: Itay, 2026-10-13) |
| Manpower drift | +⌈5U⌉ p 0.3 and −⌈5U⌉ p 0.3 at any size, at least 1 person; +1 p 0.3 if S > 100 (PR 8 item 13) | L635–644 | — (intended: −⌈5U⌉ p 0.3 at any size, Itay, 2026-10-13) |

## Enclosures ([page](../mechanisms/enclosure-construction.md))
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Prosperity thresholds | 0.6 (eligible), 0.8 (new) | L596, L609 | 0.6, 0.8, Assumed |
| Start | `year >= 4` (PR 8 item 9) | L597 | "from the fifth year onward" (Ch. 5 §5.3.3); `year >= 4` intended (Itay, 2026-10-12) |
| Environmental quality Q | mean suitability within 20 cells / 10, uncapped; logged | L584–586 | "from 0 … to 1" (Ch. 5 §5.3.3); whether to cap at 1 is open (PR 8 item 9) |
| Reuse minima, cost | M ≥ 15, S ≥ 10; 10 M, 6 S | L598, L601–602 | same, Assumed |
| New-build minima, cost | M ≥ 30, S ≥ 30; 20 M, 25 S | L609, L612–613 | same, Assumed |
| Manpower recovery | 90% | L608, L620 | 90%, Assumed |
| Reuse windows | own < 35, any < 25 y | L841, L846 | 35 / 25, Assumed |
| Reuse only unoccupied | not another household's camp this year, nor reused or built by it this year (PR 8 item 9) | L850–852; `cells_occupied_by_others` L819–830 | Ch. 5 §5.3.3 |
| Others' weighting, noise | 0.8; U(0.8, 1.2) | L847, L860 | 80%, ±20%, Assumed |
| Search radius | 20 (Chebyshev) | L832–846 | — |
| Enclosure signal | reuse +1; new 1 + 2 × prosperity | L605, L614–617 | — |
| build_enclosure scoring | ownership bias 1.5; others > 15 y; avg > 8; p 0.3 / 0.4; env > mean + 1 | L898–973 | — |

## Crisis ([page](../mechanisms/crisis-and-replacement.md))
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Crisis threshold | surplus < 10 | L622 | 10, Assumed |
| Distress sale rate | 0.3 per head | L748 | 0.3, Assumed |
| Reserve | min(18 × M, 100) | L751 | 18/person capped at 100, Assumed |
| Failure | S ≤ 0, herd < 15, M ≤ 0 (PR 8 item 4) | L885 | S < 0, herd < 15 (A5.4); M > 0 (Ch. 5 §5.3.4) |
| Replacement herd | inherited herd + Σ₁₀ ⌊N(90, 15)⌋; manpower as a new household (PR 8 item 7) | L1128–1135 | ~900 (Ch. 5 §5.3.4) |

## Observation and calibration ([classification](../mechanisms/site-classification.md), [objective](../mechanisms/calibration-objective.md))
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Site threshold | 0.6 | `to_gdf` L1210 | Ch. 5 §5.5.3 (face validation) |
| Ellipse scale | 2 SD | L1247 | Ch. 5 §5.5.2 |
| Error weighting | (spatial + ratio)/2 | L1310 | Ch. 5 §5.5.2 |
| Replicates per trial | 10 | L1370, L1415 | 10 (Ch. 5 §5.5.2) |
| Seeds | trial × 100 + i | L1383 | App. 5 §A5.3 |
| Sampler, pruner | TPE; MedianPruner(10, 5). `scripts/calibrate.py`: `TPESampler(constant_liar=True)`, `MedianPruner(n_startup_trials=10, n_warmup_steps=5)` | calibration.ipynb cell 1; `scripts/calibrate.py` L55, L61 | Ch. 5 §5.5.2 (no settings given) |
