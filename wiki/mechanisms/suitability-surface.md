---
type: mechanism
created: 2026-10-08
code: "model.py › get_suitability_raster, L469–508; NomadModel.move_year, L1020–1043"
odd: "Submodels; Input data; Design concepts › sensing"
---

# Suitability surface

## What it does
Each year the model rebuilds one shared suitability raster as a weighted sum of seven 0–10 layers. Four are permanent: distance to Tell el-Qudeirat (`kb`), distance to permanent water (`pw`), mean rainfall, and slope. Three are annual: reuse potential, resource exhaustion, and the year's rainfall. Cells whose slope suitability is below 1 are then zeroed, and the result is multiplied by the `ext_raster` mask, the outline of the Negev Highlands; the band between it and `place_raster`, where camps may go, is the buffer (Itay, 2026-10-12). Households read this surface, plus their own adjustments, to choose camps. The seven weights are the only calibrated parameters.

## Where it lives
- `model.py › get_suitability_raster`, L469–508 (weighted sum L501–503, slope cut L505, mask L506).
- Called at Year 0 by `run_model_opt` (L1257–1259) and between years by `NomadModel.move_year` (L1023–1025).
- Weights are sampled in `model.py › objective` (L1353–1380). Order in code: `dist_to_kb, p_water, Mean_rain, slope_suitability, return_to_site, humen_stress, Yearly_rain`, unpacked as `wp2, wp4, wp6, wp8, ws1, ws2, ws6` (L488).

## Inputs and parameters
| Term | Code array | Source in data | Weight |
|---|---|---|---|
| Distance to Tell el-Qudeirat (corridor; formerly a point, code name kept, Itay 2026-10-12) | `kb_suitability_raster` | `per_data` array 1 | `wp2` / `dist_to_kb` |
| Distance to permanent water | `pw_suitability_raster` | `per_data` array 2 | `wp4` / `p_water` |
| Mean annual rainfall | `rain_suitability_raster` | `per_data` array 4 | `wp6` / `Mean_rain` |
| Slope | `slp_suitability_raster` | `per_data` array 5 | `wp8` / `slope_suitability` |
| Reuse potential | `return_ras` = accumulator × 5 | model-generated | `ws1` / `return_to_site` |
| Resource exhaustion | `yi_hu_stressed_z` | model-generated | `ws2` / `humen_stress` |
| Annual rainfall | `YrainFuzzyMember_calc` | yearly array 0 | `ws6` / `Yearly_rain` |

- `per_data` arrays 0 (`agri_raster`) and 3 (`veg_fit`) are loaded but not used in the sum (L481–482), as App. 5 Table A5.1 specifies ("No (collinear with annual rainfall)", "No (used in pasture derivation only)").
- Fuzzy transformations were done in ArcGIS Pro before the data reached the model (App. 5 §A5.1). Table A5.1 lists: mean and annual rainfall Linear 0–100 mm; slope FuzzySmall, midpoint 15°, spread 3; permanent water FuzzySmall, midpoint 3 h walking, spread 1; Tell el-Qudeirat FuzzySmall, midpoint 4 h walking, spread 1.
- Table A5.1 notes (App. 5; "suitability 0.5" means membership 0.5, i.e. suitability 5, per Itay, 2026-10-12): "FuzzySmall assigns maximum suitability (10) to low input values and minimum suitability (0) to high input values, using a sigmoidal decline; midpoint is the input value at suitability 0.5 and spread controls the steepness of the transition. Linear transformation maps raw values linearly between the specified minimum (suitability 0) and maximum (suitability 10)."
- The weights are integers 0–7, normalised to sum to 1 (`objective`, L1363–1367; Ch. 5 §5.5.2). Calibrated values are in [parameters](../model/parameters.md#calibrated-weights).

## What it changes
`model.suitability_raster`, which is then lowered in place during the year by [within-year degradation](within-year-degradation.md) and rebuilt from scratch at the next `move_year`.

## Assumption it encodes
Ch. 5 §5.2.1.2: households read "a single weighted suitability score for each cell", combined as `Suitability = Σ (Wᵢ × Parameterᵢ)`. Available pasture and cultivable land "are deliberately kept out", because both derive from that year's rainfall and "weighting them next to rainfall would overrepresent it" (Ch. 5 §5.2.1.2).

## Justification
- Owner's documentation: Ch. 5 §5.2.1.2 (rescaling to 0–10 by fuzzy membership, citing Fusco & de Runz 2020; walking-time distances by Tobler's function, citing Tobler 1993 and Herzog 2020). App. 5 Table A5.1 gives sources per layer.
- Calibration of the weights: Ch. 5 §5.5; App. 5 §A5.3.
- The slope cut (`slp < 1 → 0`) appears in Ch. 5 §5.7 as a possible "structural" reason slope received zero weight. No separate justification for the threshold of 1 is recorded in Ch. 5 or App. 5.
  - Asked where the threshold of 1 comes from. Itay, 2026-10-12: From the fuzzy calculation, where values equal or less than 1 represent very steep slopes that are uninhabitable such as cliffs.
  - Under App. 5 Table A5.1's parameters (FuzzySmall, midpoint 15°, spread 3) and ArcGIS's FuzzySmall, μ = 1 / (1 + (x/15)³), suitability 1 (μ = 0.1) falls at a slope of about 31°. This is calculated here, not stated in the thesis. The code zeroes values below 1 and keeps exactly 1 (L505).

## My rationale
**My rationale** · Itay, 2026-10-12
> Q: Suitability is a weighted sum of seven 0–10 layers, then zeroed where slope suitability is below 1 (get_suitability_raster, L501–506). What reasoning led you to combine the layers additively?

The idea behind this approach is to try and reflect the balance between different considerations that households have when deciding on their camp location. As we do not know or have a defined assumption on the balance between those specific variables, I opted to calibrate the weight each one is given.

- Follow-up (asked whether there is also a reason to add the layers rather than combine them another way). Itay, 2026-10-12: It was the simplest way I could think of, following KISS principle. To do that, I chose to bring all the variables to the same scale (0-10 suitability).

## Things to check
- Which yearly array is rainfall and which is pasture? `get_suitability_raster` unpacks the yearly arrays as `YrainFuzzyMember_calc, agr_raster, calc_pastoral_Yi` (L489) and weights array 0 as annual rainfall. `NomadModel` reads array 0 as `veg_ras`/`veg_map`, the pasture used for herds (L980–982, L1030), and array 1 as `ag_ras` (L983, L1031). Array 2 (`calc_pastoral_Yi`) is not used anywhere. App. 5 Table A5.6 describes `veg_ras` as "multiplicative interaction of vegetation type and selected rainfall year". The test notebook's mock data repeats the suitability naming.
  - Itay, 2026-10-12: `get_suitability_raster` unpacks the yearly arrays correctly. If 'NomadModel' reads array 0 instead of array 2 it is probably a mistake or mismatch of some kind. But the way array 2 is calculated is the pasture map (the permanent pasture variable) multiplicated by the current year rainfall suitability map.
  - The reply means the code gives herds the year's rainfall membership (array 0) where pasture (array 2) was intended. Both model files do this (`model.py` L980–982, L1030; `sensitivity_model.py` L883–884, L947). `veg_map` sets herd capacity through `pasture_val` in `calc_surplus` (L667) and `update_flock_size` (L736), and `veg_ras` enters enclosure scoring (L800, L846, L868, L893). The calibration and all reported runs used array 0. App. 5 Table A5.6 describes the intended array.
  - Checked 2026-10-12 in the calibration data (files from the repository history, commit `14cb755^`). Array 2 ≈ `veg_fit` (permanent array 3) × array 0 / 10: the ratio has median 0.100 (IQR 0.093–0.108) and the correlation is 0.97 in groups 0, 1 and 37, as the reply describes. Group 74's array 2 holds no-data values (1,851 cells of −inf and 35,536 at −1.8 × 10³⁰⁸), 359 of them inside `ext_raster`; the other 74 groups are clean. Array 2 is unused now, but every 75-year run draws year 74.
  - Asked whether the separate PR should switch pasture to array 2 in both model files. Itay, 2026-10-12: Yes, separate PR. This is a big red flag!
- Corridor or point? Ch. 5 §5.2.1.2 describes this layer as cost-distance to the Tell el-Qudeirat–Faynan *corridor* ("only the red parts" of Figure 3.11). App. 5 Table A5.1 says "Distance to Tell el-Qudeirat … Site location", and Table A5.6 says "Cost-distance to Tell el-Qudeirat". The code name is `dist_to_kb`.
  - Itay, 2026-10-12: It was a point in the past but have changed to corridor, the name was just left so nothing breaks.
  - Checked 2026-10-12 in the calibration data. In `per_data` array 1 the cells at suitability ≥ 9.5 form a strip about 59 km long (237 columns) and 14 km wide (57 rows), elongated east–west (SD ratio 4.5), which fits a corridor rather than a point.
  - App. 5 still describes the point: Table A5.1 ("Site location; cost-distance (Tobler)", p. 235) and Table A5.6 (`kb_distance`, "Cost-distance to Tell el-Qudeirat via Tobler's hiking function", p. 246).
- App. 5 §A5.3 reports that exploratory runs "revealed, for example, that annual rainfall weights required substantial influence to generate appropriate temporal cycling", while the calibrated annual-rainfall weight is 0 across the leading 19 trials (Ch. 5 §5.5.4). Does the A5.3 sentence describe an earlier version of the model?
  - Itay, 2026-10-12: There may be confusion here between the mean annual rainfall and a specific year annual rainfall.
  - If A5.3 means mean rainfall: that layer is "Permanent" and so does not change between years (App. 5 Table A5.1 caption: "'Permanent' parameters remain constant across all 75 simulation years"). Its calibrated weight is 0.130 ([parameters](../model/parameters.md#calibrated-weights)). Which layer does A5.3 mean, and does its wording need to change?
  - Itay, 2026-10-12: It is just some preliminary observation, from trial runs before the calibration process, it is not critical and can go if needed.
- `ext_raster` multiplies the surface (L504–506), but its meaning is not documented beyond "Binary mask" (docs/DATA.md). Ch. 5 §5.2.1.1 describes a buffer zone where environmental processes run and a place raster confining camps. Is `ext_raster` the outer limit of that buffer?
  - Itay, 2026-10-12: No, it is making sure no household is placing itself outside of the study area. The buffer is between this raster and the edge of the grid. (Superseded by Itay's later reply below.)
  - Ch. 5 §5.2.1.1 gives that role to the place raster: "a binary 'place raster' confines actual camps to the Israeli part of the Negev Highlands". In the code both masks keep camps in: `ext_raster` zeroes suitability (L504–506), so camp draws there have probability 0, and `place_raster` is required for main camps (L355) and family camps (L372). How do the two masks differ?
  - Checked 2026-10-12 in the calibration data. `ext_raster` has 52,012 cells (3,250.8 km², the model extent of App. 5 Table A5.4 that `Num_agents` uses, L283–287). `place_raster` has 37,555 cells (2,347.2 km²), all but 24 of them inside `ext_raster`. The 14,481 cells (905 km²) inside `ext_raster` but outside `place_raster` lie mostly east (8,991) and west (5,060) of the placement area. Camps need `place_raster` (L355, L372); outside `ext_raster` suitability is 0.
  - Asked which band is the buffer of Ch. 5 §5.2.1.1: the band between the masks or the area outside `ext_raster`. Itay, 2026-10-12: place_raster is the valid placement, ext_raster is the buffer: the Negev Highlands are not a rectangle, hence their complex shape is recorded in ext_raster. place_raster is solely differentiating between where there is not sufficient data (the Egyptian side) and where there is. I am aware I wrote something different before, disregard it. The buffer lies between ext_raster and place_raster.
  - Open. Of the 14,481 band cells, 5,060 lie west of the placement area (the strip along the straight Israel–Egypt border) and 8,991 east of it in the same rows: a large south-eastern block and an inlet in the east-centre (map drawn from the calibration masks, 2026-10-12). What separates the eastern band from the placement area?
- The Table A5.1 notes put the FuzzySmall midpoint at "suitability 0.5" on a scale whose maximum is 10. Does this mean membership 0.5, which is suitability 5?
  - Itay, 2026-10-12: Yes.
  - The note in App. 5 (Table A5.1, p. 236) still reads "midpoint is the input value at suitability 0.5".
- The suitability can exceed 10, because reuse potential (accumulator × 5) is unbounded. Ch. 5 §5.3.3 treats Q, the mean suitability around the camp, as running "from 0 … to 1" after division by 10 (code: `env_quality = current_env_value / 10.0`, L553).
  - Itay, 2026-10-12: This is relating to the base suitability.
  - In the code, Q comes from `env_mean_val` (L552–553), the mean of `model.suitability_raster` within 20 cells (L255–263). That is the full weighted surface, with reuse potential and exhaustion, lowered by this year's degradation. The same mean sets the territory radius (L631–638). Which layers does "base suitability" mean here?
  - Asked which layers "base suitability" means. Itay, 2026-10-12: I meant that it does not include each agent's own perception.
  - So Q uses the shared surface, not the personalised one, as the code does. That surface can exceed 10 where reuse potential is high, so Q can exceed 1 in principle, against Ch. 5 §5.3.3's "from 0 … to 1"; whether it does in runs has not been checked. Deferral to [enclosure construction](enclosure-construction.md), where the prosperity index is, proposed 2026-10-12.
