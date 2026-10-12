---
type: mechanism
created: 2026-10-08
code: "model.py › get_suitability_raster, L469–508; NomadModel.move_year, L1020–1043"
odd: "Submodels; Input data; Design concepts › sensing"
---

# Suitability surface

## What it does
Each year the model rebuilds one shared suitability raster as a weighted sum of seven 0–10 layers. Four are permanent: distance to Tell el-Qudeirat (`kb`), distance to permanent water (`pw`), mean rainfall, and slope. Three are annual: reuse potential, resource exhaustion, and the year's rainfall. Cells whose slope suitability is below 1 are then zeroed, and the result is multiplied by the `ext_raster` mask. Households read this surface, plus their own adjustments, to choose camps. The seven weights are the only calibrated parameters.

## Where it lives
- `model.py › get_suitability_raster`, L469–508 (weighted sum L501–503, slope cut L505, mask L506).
- Called at Year 0 by `run_model_opt` (L1257–1259) and between years by `NomadModel.move_year` (L1023–1025).
- Weights are sampled in `model.py › objective` (L1353–1380). Order in code: `dist_to_kb, p_water, Mean_rain, slope_suitability, return_to_site, humen_stress, Yearly_rain`, unpacked as `wp2, wp4, wp6, wp8, ws1, ws2, ws6` (L488).

## Inputs and parameters
| Term | Code array | Source in data | Weight |
|---|---|---|---|
| Distance to Tell el-Qudeirat (corridor) | `kb_suitability_raster` | `per_data` array 1 | `wp2` / `dist_to_kb` |
| Distance to permanent water | `pw_suitability_raster` | `per_data` array 2 | `wp4` / `p_water` |
| Mean annual rainfall | `rain_suitability_raster` | `per_data` array 4 | `wp6` / `Mean_rain` |
| Slope | `slp_suitability_raster` | `per_data` array 5 | `wp8` / `slope_suitability` |
| Reuse potential | `return_ras` = accumulator × 5 | model-generated | `ws1` / `return_to_site` |
| Resource exhaustion | `yi_hu_stressed_z` | model-generated | `ws2` / `humen_stress` |
| Annual rainfall | `YrainFuzzyMember_calc` | yearly array 0 | `ws6` / `Yearly_rain` |

- `per_data` arrays 0 (`agri_raster`) and 3 (`veg_fit`) are loaded but not used in the sum (L481–482), as App. 5 Table A5.1 specifies ("No (collinear with annual rainfall)", "No (used in pasture derivation only)").
- Fuzzy transformations were done in ArcGIS Pro before the data reached the model (App. 5 §A5.1). Table A5.1 lists: mean and annual rainfall Linear 0–100 mm; slope FuzzySmall, midpoint 15°, spread 3; permanent water FuzzySmall, midpoint 3 h walking, spread 1; Tell el-Qudeirat FuzzySmall, midpoint 4 h walking, spread 1.
- Table A5.1 notes (App. 5): "FuzzySmall assigns maximum suitability (10) to low input values and minimum suitability (0) to high input values, using a sigmoidal decline; midpoint is the input value at suitability 0.5 and spread controls the steepness of the transition. Linear transformation maps raw values linearly between the specified minimum (suitability 0) and maximum (suitability 10)."
- The weights are integers 0–7, normalised to sum to 1 (`objective`, L1363–1367; Ch. 5 §5.5.2). Calibrated values are in [parameters](../model/parameters.md#calibrated-weights).

## What it changes
`model.suitability_raster`, which is then lowered in place during the year by [within-year degradation](within-year-degradation.md) and rebuilt from scratch at the next `move_year`.

## Assumption it encodes
Ch. 5 §5.2.1.2: households read "a single weighted suitability score for each cell", combined as `Suitability = Σ (Wᵢ × Parameterᵢ)`. Available pasture and cultivable land "are deliberately kept out", because both derive from that year's rainfall and "weighting them next to rainfall would overrepresent it" (Ch. 5 §5.2.1.2).

## Justification
- Owner's documentation: Ch. 5 §5.2.1.2 (rescaling to 0–10 by fuzzy membership, citing Fusco & de Runz 2020; walking-time distances by Tobler's function, citing Tobler 1993 and Herzog 2020). App. 5 Table A5.1 gives sources per layer.
- Calibration of the weights: Ch. 5 §5.5; App. 5 §A5.3.
- The slope cut (`slp < 1 → 0`) appears in Ch. 5 §5.7 as a possible "structural" reason slope received zero weight. No separate justification for the threshold of 1 is recorded.

## My rationale
**My rationale** · owed
> Q: Suitability is a weighted sum of seven 0–10 layers, then zeroed where slope suitability is below 1 (get_suitability_raster, L501–506). What reasoning led you to combine the layers additively?

> A: the idea behind this approach is to try and reflect the balance between different considerations that households have when deciding on their camp location. as we do not know or have a defined assumption on the balance between those specific variables, i opted to calibrate the weight each one is given.

## Things to check
- Which yearly array is rainfall and which is pasture? `get_suitability_raster` unpacks the yearly arrays as `YrainFuzzyMember_calc, agr_raster, calc_pastoral_Yi` (L489) and weights array 0 as annual rainfall. `NomadModel` reads array 0 as `veg_ras`/`veg_map`, the pasture used for herds (L980–982, L1030), and array 1 as `ag_ras` (L983, L1031). Array 2 (`calc_pastoral_Yi`) is not used anywhere. App. 5 Table A5.6 describes `veg_ras` as "multiplicative interaction of vegetation type and selected rainfall year". The test notebook's mock data repeats the suitability naming. itay:  `get_suitability_raster` unpacks the yearly arrays correctly. if 'nomadmodel' reads array 0 instead of array 2 it is probably a mistake or mismatch of some kind. but the way array 2 is calculated is the pasture map (the permanent pasture variable) multiplicated by the current year rainfall suitability map.
- Corridor or point? Ch. 5 §5.2.1.2 describes this layer as cost-distance to the Tell el-Qudeirat–Faynan *corridor* ("only the red parts" of Figure 3.11). App. 5 Table A5.1 says "Distance to Tell el-Qudeirat … Site location", and Table A5.6 says "Cost-distance to Tell el-Qudeirat". The code name is `dist_to_kb`. itay: it was a point in the past but have changed to corridor, the name was just left so nothing breaks. 
- App. 5 §A5.3 reports that exploratory runs "revealed, for example, that annual rainfall weights required substantial influence to generate appropriate temporal cycling", while the calibrated annual-rainfall weight is 0 across the leading 19 trials (Ch. 5 §5.5.4). Does the A5.3 sentence describe an earlier version of the model? itay: there may be confusion here between the mean annual rainfall and a specific year annual rainfall.
- `ext_raster` multiplies the surface (L504–506), but its meaning is not documented beyond "Binary mask" (docs/DATA.md). Ch. 5 §5.2.1.1 describes a buffer zone where environmental processes run and a place raster confining camps. Is `ext_raster` the outer limit of that buffer? itay: no, it is making sure no household is placing itself outside of the study area. the buffer is between this raster and the edge of the grid. 
- The Table A5.1 notes put the FuzzySmall midpoint at "suitability 0.5" on a scale whose maximum is 10. Does this mean membership 0.5, which is suitability 5? itay: yes
- The suitability can exceed 10, because reuse potential (accumulator × 5) is unbounded. Ch. 5 §5.3.3 treats Q, the mean suitability around the camp, as running "from 0 … to 1" after division by 10 (code: `env_quality = current_env_value / 10.0`, L553). itay: this is relating to the base suitability
