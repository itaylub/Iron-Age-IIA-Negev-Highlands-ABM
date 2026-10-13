---
type: mechanism
created: 2026-10-08
code: "model.py › Household_Agent.update_flock_size, L735–777; pasture_val, L266–274"
odd: "Submodels"
---

# Herd dynamics

## What it does
At the start of each household's economic step, the herd (`flock_head`, in goats) grows or shrinks against a local carrying capacity:

- Capacity = `n × 1.125 × (PV / 5)`. PV is the mean of `veg_map` (pasture, already reduced by [exhaustion](occupation-history-layers.md)) over a 61 × 61 window around the camp, and n = 3,720 cells in the radius-30 Moore neighbourhood (L736–744).
- `ratio = capacity / herd`.
- **Growth if ratio > 1.1**: rate = `0.2 × stress_factor × small_flock_factor × (1 − herd/1500) × min(ratio, 2) × U(0.7, 1.3)`, where `stress_factor = 1 − min(0.5, avg_stress/20)` over the territory, and `small_flock_factor = 2 − herd/500` below 500 head. The gain is limited to `1.2 × capacity − herd` and is never negative (L761–767).
- **Decline if ratio < 0.9**: rate = `(0.05 + 0.5 × (0.9 − ratio)) × (1 + avg_stress/20) × U(0.8, 1.2)`, capped at 0.3. It is damped for herds under 100 by `max(0.4, herd/100)` (L769–777).
- Between 0.9 and 1.1 the herd is unchanged.

## Where it lives
`model.py › Household_Agent.update_flock_size`, L735–777, called first in `Household_Agent.step` (L545). Initial herds: ⌊N(105,15)⌋ summed over 10 families, about 1,050 (L519–522).

## Inputs and parameters
- 1.125 goats per cell at PV = 5; evaluation radius 30.
- Growth: thresholds 1.1 / 0.9; max rate 0.2; diminishing-returns term 1,500; small-herd threshold 500; noise U(0.7,1.3); cap 1.2 × capacity.
- Decline: base 0.05 + 0.5 × gap; stress term /20; noise U(0.8,1.2); cap 0.3; small-herd damping below 100.
- App. 5 Table A5.4: pasture carrying capacity 1.125 goats/cell (Ethnographic, Rosen & Finkelstein 1992); carrying capacity evaluation radius 25 cells (Assumed); maximum herd growth rate up to 20% (Literature-based); herd decline rate 10–30% (Literature-based); maximum herd size 1,000 (Assumed).

## What it changes
`flock_head`. The new herd feeds [household economy](household-economy.md) in the same step.

## Assumption it encodes
Ch. 5 §5.3.2: the model "evaluates the pasture across the territory and converts it into a carrying capacity". Where the environment "offers comfortably more than the herd needs … the herd grows; when it falls short … the herd contracts". "small herds recover faster (below 500), as they are easier to manage; very large herds (above 1,000) present the household with diminishing marginal returns, reflecting their unwieldiness."

## Justification
- Owner's documentation: Ch. 5 §5.3.2 and §5.2.4. The 1.125 goats per cell follows from Seligman et al. 1962 by way of Rosen & Finkelstein 1992 (about 5.5 head/km² at the marginal end; Ch. 5 §5.2.4). The growth and decline rates are "Literature-based" in App. 5 Table A5.4, without a named source.
- Owner's rationale (Itay, 2026-10-13, My rationale below): the growth values come from the Dahl and Hjort book, which Ch. 5 §5.2.2 cites as Dahl & Hjort 1976 for goats per person ([literature cited](../model/literature-cited.md)). Not ingested.

## My rationale
**My rationale** · Itay, 2026-10-13
> Q: Herds grow by up to 20% a year when capacity exceeds 1.1× the herd, scaled by (1 − herd/1,500) (update_flock_size, L761–767). Where do the 20% and the 1,500 come from?

Dahl and Hjort book.

## Things to check
- Evaluation area. Ch. 5 §5.3.2 defines n as "the number of cells in the territory". The code uses a fixed radius-30 window around the camp whatever the territory radius (L736–738). App. 5 Table A5.4 gives an evaluation radius of 25, the radius `calc_surplus` uses (L667–669).
  - Asked over which area capacity should be computed. Itay, 2026-10-13: The number of cells in the territory.
  - For the separate PR: capacity and its mean pasture value over `self.territory` (a Moore square of radius 20, 25 or 30 with the centre, 1,681 / 2,601 / 3,721 cells, L640–641). At radius 20 and 25 this lowers capacity to about 45% and 70% of the present radius-30 value at equal mean pasture, so it changes calibrated behaviour. For the write-up: App. 5 Table A5.4's "evaluation radius 25" should describe the territory.
- Can the growth rate exceed 20%? The documented "Up to 20%" (App. 5 Table A5.4) is the base 0.2. The multipliers can raise it, up to 2 for small herds, up to 2 for `min(ratio, 2)` and up to 1.3 for noise (L762–764), while `stress_factor` and the diminishing term lower it.
  - Calculated 2026-10-13, every multiplier at its maximum (still under the 1.2 × capacity cap): a 250-head herd up to 33% a year on unused ground and 65% on heavily used ground; 100 head up to 87%; about 1,050 head up to 8% or 16%.
  - Asked whether "up to 20%" is a ceiling on the realised rate or the base before the multipliers. Itay, 2026-10-13: Before, but it should be after.
  - For the separate PR: cap the realised growth rate at 0.2, after all multipliers and noise (`min(growth_rate, 0.2)`), alongside the 1.2 × capacity cap. Changes calibrated behaviour.
- Herd ceiling. App. 5 Table A5.4 lists a maximum herd size of 1,000, described as "Upper cap for herd growth (diminishing returns threshold)", and Ch. 5 §5.3.2 says diminishing returns act above 1,000. In the code the diminishing term `1 − herd/1500` acts at all sizes and stops growth only at 1,500 (L763, L766–767). There is no cap at 1,000.
  - Asked whether herds should be capped at 1,000 or the taper to zero at 1,500 is intended. Itay, 2026-10-13: The taper to zero at 1,500 is intended; text need fix then.
  - The code matches. For the write-up: App. 5 Table A5.4 (maximum herd size 1,000; growth "diminishing returns approaching 1,000 animals") and Ch. 5 §5.3.2 ("very large herds (above 1,000)") should describe growth tapering with herd size and reaching zero at 1,500.
- Decline range. App. 5 gives 10–30%. The code's rate can go as low as about 4%, from the base 0.05 × 0.8 noise, or lower for herds under 100 (L771–776).
  - Asked whether 10–30% is a floor and cap or a typical range. Itay, 2026-10-13: A typical range.
  - The code stands. For the write-up: Table A5.4 may say "typically" 10–30%, since the rate can fall to about 4% (2.4% below 100 head).
- Stress direction: see [occupation history layers](occupation-history-layers.md), Things to check. `avg_stress` is the mean of `stress_ras` over the territory, and `stress_ras` is 10 where there is *no* recent occupation.
  - As coded, unused ground halves growth (`stress_factor` 0.5, L755) and raises decline by half (`stress_impact` 1.5, L772). Settled here rather than on both pages (proposed 2026-10-13).
  - Asked which ground should slow growth and speed decline. Itay, 2026-10-13: Heavily used ground should slow herd growth and speed decline.
  - The code does the opposite. For the separate PR: invert both terms so that low `stress_ras` (heavily used ground) counts as stress, for example with `10 − avg_stress` in place of `avg_stress` (L755, L772). Changes calibrated behaviour.
- Capacity is computed from `veg_map`, the yearly array 0 scaled by exhaustion (L1037). Itay (2026-10-12): array 0 is the year's rainfall membership and pasture is array 2, so reading array 0 here is "probably a mistake or mismatch of some kind". Details on [suitability surface](suitability-surface.md), Things to check. Itay (2026-10-12): "a big red flag"; to be fixed in the separate PR.
