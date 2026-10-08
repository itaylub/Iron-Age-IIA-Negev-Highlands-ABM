---
type: model
created: 2026-10-08
code_commit: 2249331932b0a42ec47c33bca0ac94f4b8728813
---

# Parameters

Values are copied from `Code/model.py` (line numbers at commit `2249331`). "Documented" gives the value and source label from App. 5 Table A5.4 (or Ch. 5 where the table is silent). A **≠** marks a documented value that differs from the code; details are under Things to check on the linked mechanism page. "—" means not documented. Except for the weights, all values are hard-coded literals and cannot be changed through arguments.

## Calibrated weights
Normalised integer weights, sampled 0–7 (`objective`, L1353–1367).

| Weight (code key) | Layer | Best trial, integer (normalised) | Leading 19 trials, mean ± SD | Used by |
|---|---|---|---|---|
| `dist_to_kb` | distance to Tell el-Qudeirat (–Faynan corridor) | 7 (0.304) | 0.304 ± 0.005 | [suitability](../mechanisms/suitability-surface.md) |
| `p_water` | distance to permanent water | 1 (0.043) | 0.041 ± 0.010 | suitability |
| `Mean_rain` | long-term mean rainfall | 3 (0.130) | 0.132 ± 0.009 | suitability |
| `slope_suitability` | slope | 0 | 0 in all 19 | suitability |
| `return_to_site` | reuse potential | 7 (0.304) | 0.304 ± 0.005 | suitability |
| `humen_stress` | multi-annual resource exhaustion | 5 (0.217) | 0.217 ± 0.010 | suitability |
| `Yearly_rain` | current-year rainfall | 0 | 0 in all 19 | suitability |

Sources: best-trial integers from CHANGELOG [1.0.0] "Phase 6 follow-up", which cites "§4.6.4 of the thesis" (older numbering). Cluster means from Ch. 5 §5.5.4 ("the 19 trials scoring below 0.21"). Ch. 5 §5.5.4 gives the best trial's structure only in Figure 5.9 (not read). Best calibration score 0.2013; 30-replicate re-run 0.213 ± 0.021 (Ch. 5 §5.5.4).

## Spatial and temporal
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Grid | 318 × 280 (rows × cols), from raster shape | `NomadModel.__init__` L957–958; `ensure_data_loaded` L193 | 318 × 280 cells, 250 m (A5.4) |
| Model area (for agent count) | 3,251.54 km² | `Num_agents` L284 | 3,251.54 km² (A5.4) |
| Run length | 75 years | `objective_function` L1294; notebooks | 75 years (A5.4; Ch. 5 §5.2.3) |
| Edge buffer for camps | 20 cells | `place_household` L351–354 | — |
| CRS origin, cell size | (139,554.93, 478,515.53), 250 m | `to_gdf` L1131 | ITM (Ch. 5 §5.2.1.1) |

## Population and initialisation
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Households | ⌊(3,251.54/18)/20⌋ = 9 | `Num_agents` L283–287 | 9 (A5.4; Ch. 5 §5.2.4, from Rosen & Finkelstein 1992) |
| Initial herd | Σ₁₀ ⌊N(105, 15)⌋ | `Household_Agent.__init__` L519–522 | ~105 per family, ~1,050 (A5.4, modified from Rosen & Finkelstein 1992) |
| Initial manpower | max(35, ⌊herd/20⌋) | L526–527 | Ch. 5 §5.2.2 |
| Initial surplus | 0 | L531–532 | Ch. 5 §5.2.4 ("no accumulated experience or surplus") |
| Year-0 territory radius | 25 | L993, L1002 | — (≠ year_initiation's 20/25/30) |

## Suitability and occupation history ([suitability](../mechanisms/suitability-surface.md), [history layers](../mechanisms/occupation-history-layers.md))
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Slope cut-off | slope suitability < 1 → 0 | L505 | Ch. 5 §5.7 (mentioned) |
| Accumulator decay | 0.5 | `Yi_params` L437 | 0.5, Assumed (A5.4) |
| Weight for cells ≥ 2 | × 1.5 | L433–434 | — |
| Smoothing window | ±20 cells, 1/(d+1)² | L442–446 | 5 km, Assumed (A5.4) |
| Exhaustion fuzzy range | 0 → 10, 2 → 0 | L458–463 | — (value 2) |
| Reuse multiplier | × 5 | L465 | — |
| Pasture reduction by exhaustion | `1 − 0.1 × min(10/stress − 1, 9)` | `move_year` L1034–1037 | — |

## Memory and territorial attachment
([page](../mechanisms/memory-and-territorial-attachment.md))
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Centre update | 0.9 previous / 0.1 current | L624–627 | 90% / 10%, Assumed |
| Home-range bonus | 5.0 × exp(−D²/(2·50²)) | L926–929 | +5.0, σ 50, Assumed |
| Territory bonus | 2.5/(d+1), d ≤ 20 | L935–937 | Assumed |
| Memory quality threshold | 5 | L946 | 5, Assumed |
| Current-year penalty | −0.5 | L943 | −0.5, Assumed |
| Memory factor, time weight | 0.5, 1/√Δy | L945–949 | Ch. 5 §5.3.1 |
| Memory retention | keep if age × U < 15 | L620 | < 15 always; ~15/age, Assumed |

## Placement and territory ([page](../mechanisms/camp-and-territory-placement.md))
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Selection exponent | 3 | L336, L379 | Ch. 5 §5.3.1 |
| Territory radius | 20 / 25 / 30 at suitability ≥ 5.0 / 3.5–5.0 / < 3.5 | L632–638 | same, Assumed |
| Overlap threshold | 0.25 | L328 | 25%, Assumed (≠ in effect, see page) |
| Capacity test | `n` starts at 35; re-draw if < 1 | L362, L297–316 | — |
| Family camps per household | 9 (plus the main camp) | L645 | Ch. 5 §5.2.2: a household is "a tentative group of about ten nuclear families" |
| Camp signal / family signal | +0.5 / +0.25 | L280, L649 | Ch. 5 §5.5.3 |
| Camp surplus cost | −1 | L279 | — |

## Within-year degradation ([page](../mechanisms/within-year-degradation.md))
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Household D, P, radius | 0.5, 0.9, territory radius | L651 | D 0.5, P 0.9, Assumed |
| Family D, P, radius | 0.3, 0.5, 11 | L647 | 0.3, 0.5, 11, Assumed |
| Distance | (\|dx\|+\|dy\|)/2 + 0.001 | L240–241 | — |
| Floor | 0.0001 | L418–420 | 0.0001, Assumed |

## Herd dynamics ([page](../mechanisms/herd-dynamics.md))
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Goats per cell at PV 5 | 1.125 | L743 | 1.125, Rosen & Finkelstein 1992 |
| Evaluation radius | 30 | L736–738 | 25, Assumed **≠** |
| Growth / decline thresholds | ratio > 1.1 / < 0.9 | L761, L769 | Ch. 5 §5.3.2 |
| Max growth rate | 0.2 × multipliers | L762–764 | up to 20%, Literature-based **≠** |
| Diminishing returns | 1 − herd/1500 | L763 | 1,000 cap, Assumed **≠** |
| Small-herd factor | 2 − herd/500 below 500 | L758–759 | Ch. 5 §5.3.2 |
| Decline rate | (0.05 + 0.5·gap)(1 + stress/20)·U(0.8,1.2), ≤ 0.3 | L770–776 | 10–30%, Literature-based **≠** |
| Growth cap | 1.2 × capacity | L765 | — |

## Household economy ([page](../mechanisms/household-economy.md))
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Goats per person | 18 | L664, L711 | 18, modified from Rosen & Finkelstein 1992 |
| Agricultural offset | min(0.4, 0.04 × mean ag) | L663 | up to 40%, Rosen & Finkelstein 1992; Günther et al. 2021 |
| Surplus capacity radius | 25 | L667–669 | 25 (A5.4) |
| Working-herd buffer | 1.5 | L677 | Ch. 5 §5.3.2 |
| Stress multiplier | 1 + 0.3 s | L678 | 15% × s (A5.4) **≠**; 0.3 (Ch. 5) |
| Products yield | 0.15 | L686 | Ch. 5 §5.3.2 ("adopted for simplicity") |
| Culling share, value | 0.8, 0.35 | L690–691 | Ch. 5 §5.3.2 |
| Carry-over | 0.7 (30% loss) | L696–697 | 30%, Assumed |
| Consumption | 1.2 × M + 5% luxury | L699–702 | 1.2, Assumed (luxury —) |
| Surplus cap | 200 + 2.5 × M | L705 | Ch. 5 §5.3.2 |
| Large-surplus decay | min(0.25, 0.05 + 0.001(S − 100)) above 100; 1% below | L607–616 | 5–25%, Assumed (1% —) |
| Livestock purchase | S > 80 and herd < 600; min(0.2 S, 40); 0.3 per head | L594–596, L724 | same, Assumed |
| Manpower deductions | −10, −herd//75 | L547–549 | — |
| Manpower drift | +⌈5U⌉ p 0.3; −⌈5U⌉ p 0.2 if > 55; +1 p 0.3 if S > 100 | L600–605 | — |

## Enclosures ([page](../mechanisms/enclosure-construction.md))
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Prosperity thresholds | 0.6 (eligible), 0.8 (new) | L563, L576 | 0.6, 0.8, Assumed |
| Start | `year > 5` | L564 | "from the fifth year onward" (Ch. 5 §5.3.3) **≠** |
| Reuse minima, cost | M ≥ 15, S ≥ 10; 10 M, 6 S | L565, L568–569 | same, Assumed |
| New-build minima, cost | M ≥ 30, S ≥ 30; 20 M, 25 S | L576, L579–580 | same, Assumed |
| Manpower recovery | 90% | L575, L587 | 90%, Assumed |
| Reuse windows | own < 35, any < 25 y | L788, L793 | 35 / 25, Assumed |
| Others' weighting, noise | 0.8; U(0.8, 1.2) | L794, L803 | 80%, ±20%, Assumed |
| Search radius | 20 (Chebyshev) | L779–788 | — |
| Enclosure signal | reuse +1; new 1 + 2 × prosperity | L572, L581 | — |
| build_enclosure scoring | ownership bias 1.5; others > 15 y; avg > 8; p 0.3 / 0.4; env > mean + 1 | L840–915 | — |

## Crisis ([page](../mechanisms/crisis-and-replacement.md))
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Crisis threshold | surplus < 10 | L589 | 10, Assumed |
| Distress sale rate | 0.3 per head | L709 | 0.3, Assumed |
| Reserve | min(18 × M, 100) | L712 | 18/person capped at 100, Assumed |
| Failure | S < 0, herd < 15, M ≤ 0 | L828 | S < 0, herd < 15 (A5.4); M > 0 (Ch. 5 §5.3.4) |
| Replacement herd | + Σ₁₀ ⌊N(90, 15)⌋ | L1050 | ~900 (Ch. 5 §5.3.4) |

## Observation and calibration ([classification](../mechanisms/site-classification.md), [objective](../mechanisms/calibration-objective.md))
| Parameter | Code | Where | Documented |
|---|---|---|---|
| Site threshold | 0.6 | `to_gdf` L1133 | Ch. 5 §5.5.3 (face validation) |
| Ellipse scale | 2 SD | L1170 | Ch. 5 §5.5.2 |
| Error weighting | (spatial + ratio)/2 | L1233 | Ch. 5 §5.5.2 |
| Replicates per trial | 10 | L1294, L1342 | 10 (Ch. 5 §5.5.2) |
| Seeds | trial × 100 + i | L1310 | App. 5 §A5.3 |
| Pruner | MedianPruner(10, 5) | calibration.ipynb cell 1 | Ch. 5 §5.5.2 (no settings given) |
