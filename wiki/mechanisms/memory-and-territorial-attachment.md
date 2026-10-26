---
type: mechanism
created: 2026-10-08
code: "model.py › Household_Agent.update_own_suitability_raster, L917–949; Household_Agent.year_initiation, L618–627"
odd: "Submodels; Design concepts › learning, adaptation, sensing"
body_code_commit: 2249331932b0a42ec47c33bca0ac94f4b8728813
---

# Memory and territorial attachment (personalised suitability)

> Status 2026-10-26: the body and the line numbers in the `code` field describe commit `2249331` (2026-10-05), before the 18 fixes of PR 8. Fixes that touch this mechanism are marked "Done in PR 8" under Things to check, with line numbers at `032c2a1`. The body is to be brought to the current code when its ODD submodel is written.

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
**My rationale** · Itay, 2026-10-13
> Q: Remembered camps of quality ≥ 5 add q × w × 0.5; poorer ones subtract (1/q) × w × 0.5 (update_own_suitability_raster, L938–949). What observation about pastoral camp reuse does the threshold of 5 stand for?

It is just straight common sense logic, that if the env value was above 5 (the middle point of the 0–10 scale) it counts as good experience and if less it counts as bad.

## Things to check
- Does the home-range bonus ever apply? `move_year` calls `reset_pos`, which runs Mesa's `grid.remove_agent` on every household (L1021, L1045–1047), before `year_initiation` reads `self.pos` to update `general_territory_center` (L621–627). If Mesa's `remove_agent` sets `agent.pos = None` (to check against the Mesa version used; I could not open the Mesa source from this session), the centre stays `None` and `if self.general_territory_center:` (L920) skips the bonus in every year. In fixed-territory mode `sensitivity_model.py` skips `reset_pos` (L936–937).
  - Checked 2026-10-13 in the Mesa source, v3.0.0 and v3.3.0 (`mesa/space.py › MultiGrid.remove_agent`; the model uses `MultiGrid`, L958): `remove_agent` sets `agent.pos = None`. `general_territory_center` starts as `None` (L537) and the Year-0 placement does not set it (L988–1003), so each year L621–622 sets it to the `None` position again and L920 skips the bonus. The home-range bonus never applies in `model.py`, nor in `sensitivity_model.py` outside fixed-territory mode. The calibration ran without it.
  - Asked whether the separate PR should make it work. Itay, 2026-10-13: Yes.
  - For the separate PR: keep each household's last camp through `reset_pos` so the centre update has a position, starting from the Year-0 camp (Ch. 5 §5.3.1: "in the first year, C is the first camp"). Changes calibrated behaviour.
  - Done in PR 8 (item 14, `df4776c`): `reset_pos` stores `last_camp` (L1124); the centre starts at the Year-0 camp and then moves toward the last camp (L663–669).
- Do adjustments pile up within a year? `update_own_suitability_raster` adds its bonuses to the existing personalised raster each time it is called (L918–949), and the raster is reset only once a year (L619). `place_members` calls it once per family camp (L370), so the territory bonus, the home-range bonus and the memory terms are added up to ten times per year. Inside the new territory every cell gains +2.5 per call, which flattens the cubic preference among family-camp cells. Is that intended?
  - Asked whether the bonuses should be added once a year. Itay, 2026-10-13: Yes, they should, but don't each family adds a smaller bonus (both spatially and value wise)?
  - Answered in chat: no. Every call adds the same bonuses; `update_own_suitability_raster` has no family-specific values (L917–949). Family camps are smaller elsewhere: degradation (radius 11 with 0.3 / 0.5, against the territory radius with 0.5 / 0.9; L647, L651) and the site signal (0.25 against 0.5; L649, L280).
  - Proposed with the item on the household's own degradation below: for each draw (main camp and each family camp), rebuild the personalised surface from the current shared surface, which already holds this year's earlier degradation, then add each bonus once. Itay, 2026-10-13: Approve, but think of how to make it efficient, maybe update rather than recalculate the personalized copy?
  - Proposed implementation: once a year at the main-camp draw, build HM (home-range Gaussian + capped memory terms) and T (territory bonus from last year's territory, one distance transform); the main draw uses `max(shared + HM + T, 0) ** 3`. Each family draw reads the shared surface fresh for the new territory's cells only and uses `max(shared[c] + HM[c] + 2.5, 0) ** 3` (inside the territory the territory bonus is 2.5/(0+1)). After each family camp is placed, subtract 0.5 at its cell in HM instead of re-running the memory loop. Same numbers as rebuilding and adding once; about a tenth of today's work in this function. Itay, 2026-10-13: Approved.
  - For the separate PR (item 14).
  - Done in PR 8 (item 14, `df4776c`): HM and T are built once a year at the main-camp draw (`update_own_suitability_raster`, L975–1018); each family draw reads the shared surface on the new territory's cells and adds HM + 2.5 (`place_members`, L386–388), and each new family camp takes −0.5 in HM (L403).
- Remembered quality is measured after the camp's own degradation (family: `env_degrade` at L647, then `env_mean_val` at L648; main camp: L651 then L652). Is the remembered quality meant to be what the camp offered on arrival, as Ch. 5 §5.2.2 puts it ("the quality its close environs offered")?
  - Itay, 2026-10-13: Quality after occupation (as this is the point of the memory start).
  - The code matches. For the write-up: Ch. 5 §5.2.2's "the quality its close environs offered" should say the quality after the stay.
- For very low q the penalty −(1/q) × w × 0.5 becomes large. Degraded cells sit at the 0.0001 floor ([within-year degradation](within-year-degradation.md)), so q can be close to 0 and the penalty in the thousands.
  - Noted 2026-10-13: `place_household` clips negative values to 0 (L335), but `place_members` cubes the values without clipping (L379), so a large penalty on a territory cell would give a negative weight, which `np.random.choice` rejects with an error. Whether q gets that low in runs is not checked.
  - Asked whether the penalty should be capped. Itay, 2026-10-13: Yes.
  - Proposed: cap the penalty at 5 × w, the largest bonus (q = 10), i.e. compute it with q no lower than 0.1; and clip negative values to 0 in `place_members` before cubing (L379), as `place_household` does (L335). Itay, 2026-10-13: Approve.
  - For the separate PR (item 14).
  - Done in PR 8 (item 14, `df4776c`): q counts as no lower than 0.1 (L1008), and `place_members` clips negative values to 0 before cubing (L390).
- Ch. 5 §5.3.1 defines P in the centre update as "the current year's territorial centre". The code uses the position held before this year's placement, which is last year's camp if `pos` survives `reset_pos`.
  - Asked whether P should be this year's new camp or last year's. Itay, 2026-10-13: P is last year's camp - the idea is that the general territory center shifts a bit towards the most recent camp.
  - The code reads last year's camp once the home-range fix above keeps it. For the write-up: Ch. 5 §5.3.1's "the current year's territorial centre" should say last year's camp.
- The personalised copy is taken before the household's own family camps degrade the shared surface, so a household's family camps do not see each other's degradation except through the −0.5 current-year memory penalty.
  - Asked whether later family camps should see the degradation the earlier ones caused. Itay, 2026-10-13: Yes.
  - Settled with the pile-up item above (approved 2026-10-13).
