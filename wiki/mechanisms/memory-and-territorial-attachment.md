---
type: mechanism
created: 2026-10-08
code: "model.py › Household_Agent.update_own_suitability_raster, L917–949; Household_Agent.year_initiation, L618–627"
odd: "Submodels; Design concepts › learning, adaptation, sensing"
---

# Memory and territorial attachment (personalised suitability)

## What it does
Each household copies the shared [suitability surface](suitability-surface.md) and adds three adjustments before drawing its camp:
1. **Home-range bonus.** `5.0 × exp(−D² / (2 × 50²))` around `general_territory_center`, which is updated as `0.9 × previous + 0.1 × current position` (L620–627, L920–929).
2. **Territory bonus.** `2.5 / (d + 1)` for cells within 20 cells of last year's territory, with d = Euclidean distance to the nearest territory cell (`distance_transform_edt`) (L930–937).
3. **Camp memory.** For each remembered `[cell, quality q, year]`: −0.5 if from this year; otherwise weight `w = 1/√(years since)`, and `+q × w × 0.5` if q ≥ 5, or `−(1/q) × w × 0.5` if 0 < q < 5 (L938–949).

Memory is pruned at the start of each year: an entry of age a survives if `a × U(0,1) < 15` (L620), so entries under 15 years always survive and older ones survive with probability 15/a each year.

## Where it lives
- `model.py › Household_Agent.update_own_suitability_raster`, L917–949.
- Called by `place_household` (L334) and by `place_members` once per family camp (L370).
- Reset to `None` at the start of `year_initiation` (L619). Memory is pruned at L620 and the home-range centre updated at L621–627.
- Memory entries are written in `year_initiation` (L648, L652) and at Year 0 in `NomadModel.__init__` (L1000, L1003). Quality is `env_mean_val` over radius 5 for family camps and the territory radius for the main camp, measured after that camp's degradation.

## Inputs and parameters
See [parameters](../model/parameters.md#memory-and-territorial-attachment). All values below match App. 5 Table A5.4, which marks them "Assumed":
- Centre weighting 0.9 / 0.1; Gaussian peak 5.0, σ = 50 cells.
- Territory bonus 2.5/(d+1) up to 20 cells.
- Memory threshold q = 5; current-year penalty −0.5; factor 0.5; time weight 1/√Δy.
- Pruning: guaranteed retention under 15 years, retention probability ≈ 15/age.

## What it changes
`own_suitability_raster`, which [camp and territory placement](camp-and-territory-placement.md) reads.

## Assumption it encodes
Ch. 5 §5.3.1: attachment to territory represents "a household's tendency to keep to a familiar part of the region rather than range across it solely on environmental basis", a "spatial inertia" that is "widely reported in pastoral systems". Camp memory means households "prefer to return to camps which had good quality at the year of occupation and avoid bad ones". Memory "is imperfect and does not last indefinitely".

## Justification
- Owner's documentation: Ch. 5 §5.3.1, citing Avni 1996, Galilee 2013, Hammer 2014 and Meraiot et al. 2021 for spatial inertia in pastoral systems. App. 5 Table A5.4 gives "Assumed (intergenerational knowledge)" for the 15-year retention.
- The specific values (5.0, 50, 2.5, 20, 5, 0.5, 15) are recorded as "Assumed" (App. 5 Table A5.4).

## My rationale
**My rationale** · owed
> Q: Remembered camps of quality ≥ 5 add q × w × 0.5; poorer ones subtract (1/q) × w × 0.5 (update_own_suitability_raster, L938–949). What observation about pastoral camp reuse does the threshold of 5 stand for?

## Things to check
- Does the home-range bonus ever apply? `move_year` calls `reset_pos`, which runs Mesa's `grid.remove_agent` on every household (L1021, L1045–1047), before `year_initiation` reads `self.pos` to update `general_territory_center` (L621–627). If Mesa's `remove_agent` sets `agent.pos = None` (to check against the Mesa version used; I could not open the Mesa source from this session), the centre stays `None` and `if self.general_territory_center:` (L920) skips the bonus in every year. In fixed-territory mode `sensitivity_model.py` skips `reset_pos` (L936–937).
- Do adjustments pile up within a year? `update_own_suitability_raster` adds its bonuses to the existing personalised raster each time it is called (L918–949), and the raster is reset only once a year (L619). `place_members` calls it once per family camp (L370), so the territory bonus, the home-range bonus and the memory terms are added up to ten times per year. Inside the new territory every cell gains +2.5 per call, which flattens the cubic preference among family-camp cells. Is that intended?
- Remembered quality is measured after the camp's own degradation (family: `env_degrade` at L647, then `env_mean_val` at L648; main camp: L651 then L652). Is the remembered quality meant to be what the camp offered on arrival, as Ch. 5 §5.2.2 puts it ("the quality its close environs offered")?
- For very low q the penalty −(1/q) × w × 0.5 becomes large. Degraded cells sit at the 0.0001 floor ([within-year degradation](within-year-degradation.md)), so q can be close to 0 and the penalty in the thousands.
- Ch. 5 §5.3.1 defines P in the centre update as "the current year's territorial centre". The code uses the position held before this year's placement, which is last year's camp if `pos` survives `reset_pos`.
- The personalised copy is taken before the household's own family camps degrade the shared surface, so a household's family camps do not see each other's degradation except through the −0.5 current-year memory penalty.
