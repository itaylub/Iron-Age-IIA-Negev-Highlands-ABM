---
type: mechanism
created: 2026-10-08
code: "model.py › Yi_params, L427–466; get_suitability_raster, L491; NomadModel.move_year, L1023–1037"
odd: "Submodels; Design concepts › adaptation, interaction"
---

# Occupation history layers: reuse potential and resource exhaustion

## What it does
One accumulator records past occupation. Each year it is halved, and last year's occupation signal (`target_raster`) is added to it, with cells at 2 or more multiplied by 1.5. Two suitability layers are derived from it, pulling in opposite directions:
- **Reuse potential** (`return_ras`) = accumulator × 5, unsmoothed, so it attracts households back to the exact cells used.
- **Resource exhaustion** (`yi_hu_stressed_z`) is the accumulator convolved with a normalised 1/(d+1)² kernel over a ±20-cell window, then rescaled by a decreasing fuzzy-linear function: 10 where the smoothed value is 0, falling to 0 where it reaches 2. Heavily used surroundings therefore score low.

The exhaustion layer also scales pasture for herds: `veg_map = veg_ras × (1 − 0.1 × min(10/stress − 1, 9))` (L1034–1037). It is passed to herd growth as `stress_ras` ([herd dynamics](herd-dynamics.md)).

## Where it lives
- `model.py › Yi_params`, L427–466: update (L431–437), convolution kernel built once into the global `CONV_KERNEL` (L440–448), fuzzy rescaling (L452–464), reuse output (L465).
- Year 0 (`year == 0`): smoothed field all zeros, so exhaustion = 10 everywhere and reuse = 0 (L449–454).
- The accumulator is stored on the model as `return_raster` (`move_year`, L1023–1025). `get_suitability_raster` returns `new_accumulator` in that slot, not `return_arr`.
- `eval_neighborhood` also reads `return_raster` and adds raw accumulator values ≥ 2 to suitability when testing a candidate camp's capacity (L309–313).

## Inputs and parameters
| Parameter | Value | Where | Documented |
|---|---|---|---|
| Temporal decay of accumulator | 0.5 per year | L437 | App. 5 Table A5.1 and A5.4 ("Temporal decay factor 0.5"); Ch. 5 §5.3.1 (`Sₜ = 0.5 × Sₜ₋₁ + Oₜ`) |
| Extra weight for cells ≥ 2 | × 1.5 | L433–434 | not documented |
| Smoothing window | ±20 cells (square, 41 × 41), weights 1/(d+1)², normalised | L442–446 | App. 5: "spatial radius = 5 km", "inverse-distance weighting" |
| Fuzzy exhaustion range | 0 → 10, 2 → 0 (linear, clipped) | L458–463 | Ch. 5 §5.3.1 ("cells far from any occupation score 10 and heavily occupied ones approach 0"); the value 2 is not documented |
| Reuse multiplier | × 5 | L465 | not documented; App. 5 Table A5.1: "Recent constructions weighted higher than older ones" |
| Occupation increments feeding the accumulator | camp 0.5, family camp 0.25, enclosure reuse +1, new enclosure +(1 + 2 × prosperity) | L280, L649, L572, L581–584 | Ch. 5 §5.5.3 (0.5 and 0.25); Ch. 5 §5.3.3 ("far more weight … than an ordinary camp") |

## What it changes
The `return_ras` and `yi_hu_stressed_z` terms of the [suitability surface](suitability-surface.md), the `stress_ras` used in [herd dynamics](herd-dynamics.md), and pasture `veg_map` used in herd growth and surplus.

## Assumption it encodes
Ch. 5 §5.2.1.2: occupation has "a negative effect on its immediate environment", decaying with distance and over time, and also "add[s] to the built infrastructure there, raising its value for future use". At any time "some locations are overexploited while others have already recovered", and this "shifting patchwork of depletion and inherited investment is one of the temporal mechanisms at the core of the palimpsest reading". The 0.5 decay is "the model's stand-in for the slow environmental recovery" (Ch. 5 §5.3.1).

## Justification
- Owner's documentation: Ch. 5 §5.2.1.2 and §5.3.1; App. 5 §A5.2 (eq. 4.3: `w(t) = 0.5^(T−t)`).
- App. 5 Table A5.4 marks the decay factor and smoothing radius "Assumed".
- Ch. 5 §5.3.1 cites Boles et al. 2019 and Meroz et al. 2023 for overgrazing in arid and Negev settings, as context for degradation in general, not for these values.

## My rationale
**My rationale** · owed
> Q: The same occupation record drives reuse potential (accumulator × 5) and exhaustion (fuzzy scale reaching 0 at a smoothed value of 2) (Yi_params, L437–465). What fixes the × 5 and the 2?

## Things to check
- Direction of `stress_ras` in herd growth. `stress_ras` holds `yi_hu_stressed_z`, which is 10 where there has been no recent occupation and near 0 where occupation was heaviest (L452–464). `update_flock_size` treats higher values as more stress: growth falls (`stress_factor = 1 − min(0.5, avg_stress/20)`, L755) and decline rises (`stress_impact = 1 + avg_stress/20`, L772). The `veg_map` update in `move_year` uses the opposite reading, where low values reduce pasture (L1034–1037). Which direction is intended for the herd terms? App. 5 Table A5.6 describes `stress_ras` as "Cumulative human degradation pressure".
- The ×1.5 weight for cells ≥ 2 (L433–434) is not in Ch. 5 or App. 5. In practice it mostly picks out enclosure cells and heavily reused camps.
- The smoothing window is a ±20-cell square, so its corners reach about 28 cells (7 km). App. 5 gives "spatial radius = 5 km".
- Ch. 5 §5.3.1 says the stress record is "smoothed" before rescaling, which matches the code. Reuse potential, however, uses the unsmoothed accumulator (L465), so it acts on single cells.
