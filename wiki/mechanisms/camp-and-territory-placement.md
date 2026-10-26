---
type: mechanism
created: 2026-10-08
code: "model.py › place_household, L333–366; place_members, L369–390; overlap_territory, L319–330; eval_neighborhood, L297–316; Household_Agent.year_initiation, L628–652"
odd: "Submodels; Design concepts › objectives, stochasticity, interaction"
body_code_commit: 2249331932b0a42ec47c33bca0ac94f4b8728813
---

# Camp and territory placement

> Status 2026-10-26: the body and the line numbers in the `code` field describe commit `2249331` (2026-10-05), before the 18 fixes of PR 8. Fixes that touch this mechanism are marked "Done in PR 8" under Things to check, with line numbers at `032c2a1`. The body is to be brought to the current code when its ODD submodel is written.

## What it does
Once a year each household, in random order:
1. **Draws a camp cell** with probability proportional to its [personalised suitability](memory-and-territorial-attachment.md) cubed (negatives set to 0). The cell must lie at least 20 cells from every grid edge and inside `place_raster` (L346–356). Draws are repeated until both conditions hold.
2. **Re-draws when the area is crowded and poor.** The draw is repeated while *both* `overlap_territory(...)` is true *and* `eval_neighborhood(...) < 1` (L361–364). The second test is the summed suitability of the 41 × 41 window divided by `manpower × (35 + number of occupied neighbouring cells)`.
3. **Sets a territory**: Moore neighbourhood of radius 20, 25 or 30 cells, chosen by the mean suitability within 20 cells of the camp (≥ 5.0, 3.5–5.0, < 3.5) (L631–641).
4. **Marks the camp** (`set_camp`): +0.5 to `target_raster`, −1 surplus (L277–280).
5. **Places nine family camps** inside the territory, each drawn from `place_raster`-valid cells with probability ∝ personalised suitability³. Each gets [radius-11 degradation](within-year-degradation.md), a memory entry, and +0.25 to `target_raster` (L645–649).
6. **Degrades the territory** around the main camp at the territory radius (L651) and records the camp in memory (L652).

## Where it lives
- `model.py › Household_Agent.year_initiation`, L618–652. Year 0 equivalent: `NomadModel.__init__`, L988–1003, with a fixed radius of 25.
- `place_household` L333–366, `place_members` L369–390, `overlap_territory` L319–330, `eval_neighborhood` L297–316, `calculate_carrying_capacity` L290–294, `set_camp` L277–280.
- Variant: `sensitivity_model.py › overlap_territory`, L264–272, and the fixed-territory branch of `year_initiation`, L528–539.

## Inputs and parameters
- Exponent 3 on suitability (L336, L379).
- Edge buffer of 20 cells (L351–354).
- Overlap threshold 0.25 (L328) and the capacity test with `n = 35` (L362).
- Territory radii 20/25/30 at quality cut-offs 5.0 and 3.5 (L632–638).
- Nine family camps (L645). Signals 0.5 (camp) and 0.25 (family).
- Documented in App. 5 Table A5.4: radii, cut-offs, overlap 25%, family camp radius 11, all "Assumed". The edge buffer of 20, the `n = 35` term and the exponent 3 are not in Table A5.4. Ch. 5 §5.3.1 describes the cube.

## What it changes
Agent `pos` and `territory`; `model.territories` (appended, L642); `target_raster`; agent `memory`; and, through degradation, the shared `suitability_raster`.

## Assumption it encodes
Ch. 5 §5.3.1: "The choice itself is probabilistic: more suitable cells are likelier to be picked, but not certain to be." The cube "sharpens the preference without making it deterministic". The territory widens on poor ground: "a household ranges more widely when resources are thin". Nuclear families "disperse across this territory, each placed by the same logic, so the household's presence is spread over its territory rather than fixed at a single point". Coordination between households is "modelled implicitly, arising through environmental limitation" (Ch. 5 §5.3.1).

## Justification
- Owner's documentation: Ch. 5 §5.3.1 and §5.2.3 (one move per year is "a simplification, since the real rhythm of movement is unknown").
- App. 5 Table A5.4: territory radii "Assumed (pastoral ranging)" and "Assumed (increased ranging needs)"; overlap threshold "Assumed (cooperative coexistence)".
- Sensitivity: fixed versus flexible territory (Ch. 5 §5.6; App. 5 §A5.7.4) is reported as showing region-wide repositioning to be "a stabilising one".

## My rationale
**My rationale** · Itay, 2026-10-12
> Q: Camp cells are drawn with probability proportional to personalised suitability cubed (place_household, L336; Ch. 5 §5.3.1). Where does the exponent 3 come from?

The 3 exponent is coming from face validation in the initial experimental runs.

## Things to check
- Does the overlap rule ever fire in `model.py`? `overlap_territory` adds 1 per *household* whose territory touches the candidate neighbourhood, then divides by the number of *cells* in that neighbourhood, 1,680 at radius 20 (L322–328). With nine households the share cannot exceed 8/1,680, about 0.005, so the `> 0.25` test (L328) is never true and the re-draw loop (L361–364) never runs. `sensitivity_model.py` measures the share of shared cells instead (L264–272). App. 5 Table A5.4 lists the threshold as "Maximum acceptable territory overlap before location rejected".
  - Itay, 2026-10-12 (inventory round): On the overlap rule never firing - yes this is a bug I didn't notice at the time.
  - The two files' different overlap tests (inventory, difference 1) were deferred to this page (agreed 2026-10-12).
  - Asked whether `sensitivity_model.py`'s measure (each territory's share of the candidate area's cells) is the intended one. Itay, 2026-10-12: If I understood correctly the sensitivity one is correct. The idea is that if a given territory overlaps 25% or more with other households territories, it is not valid.
  - As coded, the sensitivity test checks each other territory separately (`> 0.25` with any one of them, L268–270), always over a radius-20 candidate area, whatever radius the territory then gets.
  - Asked whether the 25% applies to each other territory separately or to the total. Itay, 2026-10-12: In total, all other territories combined.
  - On the radius-20 candidate area. Itay, 2026-10-12: This is intended as it is the base diameter.
  - For the separate PR: share of the candidate area's cells that fall in the union of this year's other territories, rejected at 25% or more (Itay's wording; the code tests `> 0.25`).
  - Done in PR 8 (item 3, `1be0dcd`), both files: `overlap_territory(nbr, taken)` returns the share of the candidate area's cells in this year's other territories, and a candidate is re-drawn at 25% or more (`model.py` L325–328, L360, L365–367).
- `model.territories` is appended every year and never cleared in either file (L642; `sensitivity_model.py` L561–563). `sensitivity_model.py` tests overlap against this whole history, so territories from past years count. App. 5 Table A5.6 describes it as the "Registry of all active household territories for the current year".
  - Asked which territories the overlap test should count. Itay, 2026-10-12: Only this year.
  - Neither file does that now: `model.territories` is never cleared, and `reset_pos` takes households off the grid but leaves each household's `territory` from last year until it places again (L1045–1047; `territory` reset only in `__init__`, L536). For the separate PR.
  - Done in PR 8 (item 3, `1be0dcd`): `move_year` clears `model.territories` each year (L1098). Each household's `territory` attribute is kept until it places again, because the main-camp draw reads last year's territory for the territory bonus; the overlap test reads only `model.territories` (a choice made in the PR, log.md 2026-10-14).
- The re-draw needs both conditions (`and`, L361–362): a crowded but rich location is accepted. App. 5 Table A5.4 describes overlap alone as grounds for rejection.
  - Asked which rule is intended. Itay, 2026-10-12: Both, so a crowded but rich env is rejected and also a free and very poor env is rejected.
  - So the code's `and` should be `or` (L361). For the separate PR: with `or`, the re-draw loop has no exit if no cell passes both tests, so it needs a guard. Because the `model.py` overlap test never fires, the calibration ran with no re-draws at all.
  - Done in PR 8 (item 3, `1be0dcd`): a candidate is re-drawn when crowded or poor, for at most 100 draws; if none passes both tests, the least crowded candidate is taken, preferring those that pass the capacity test (L356–371).
- Fixed-territory mode (`sensitivity_model.py`, L528–539) keeps the main camp on the same cell every year (`set_camp` at the unchanged `pos`); only family camps move. Ch. 5 §5.6 says households "could move freely only within" their territory.
  - Asked whether the main camp should also move within the territory in that mode. Itay, 2026-10-12: No, leave as is.
  - For the write-up: Ch. 5 §5.6's "could move freely only within" their territory fits the family camps, while the main camp stays on one cell.
- The territory radius depends on mean suitability within 20 cells *after* earlier households have degraded the surface this year (L631), so placement order affects territory size.
  - Asked whether that is intended. Itay, 2026-10-12: Not intended, the main idea behind the adaptable size of the territory was to reflect an adaptive behavior in cases of stress. So it is not necessarily bad.
- In `model.py` a failed household calls `self.remove()` (L592). In Mesa 3, `Agent.remove` deregisters the agent from the model, but whether it also leaves the grid depends on the Mesa version (not checked here). If it stays, it would count as an occupied cell in `eval_neighborhood` (L299–301). `sensitivity_model.py` removes it from the grid explicitly (L500).
  - Deferred to [crisis and replacement](crisis-and-replacement.md) with differences 4 and 6, to be tested in the separate PR (agreed 2026-10-12).
  - Checked 2026-10-13 in the Mesa source (v3.0.0, v3.3.0): `Agent.remove()` does not take the agent off the grid. Details on [crisis and replacement](crisis-and-replacement.md).
  - Done in PR 8: a failed household leaves the grid before `self.remove()` (item 8, `5284465`), and the sensitivity file's replacements are placed once, with everyone else (item 6, `1a60dab`). See [crisis and replacement](crisis-and-replacement.md).
