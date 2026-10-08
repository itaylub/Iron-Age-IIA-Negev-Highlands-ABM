---
type: mechanism
created: 2026-10-08
code: "model.py › place_household, L333–366; place_members, L369–390; overlap_territory, L319–330; eval_neighborhood, L297–316; Household_Agent.year_initiation, L628–652"
odd: "Submodels; Design concepts › objectives, stochasticity, interaction"
---

# Camp and territory placement

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
**My rationale** · owed
> Q: Camp cells are drawn with probability proportional to personalised suitability cubed (place_household, L336; Ch. 5 §5.3.1). Where does the exponent 3 come from?

## Things to check
- Does the overlap rule ever fire in `model.py`? `overlap_territory` adds 1 per *household* whose territory touches the candidate neighbourhood, then divides by the number of *cells* in that neighbourhood, 1,680 at radius 20 (L322–328). With nine households the share cannot exceed 8/1,680, about 0.005, so the `> 0.25` test (L328) is never true and the re-draw loop (L361–364) never runs. `sensitivity_model.py` measures the share of shared cells instead (L264–272). App. 5 Table A5.4 lists the threshold as "Maximum acceptable territory overlap before location rejected".
- `model.territories` is appended every year and never cleared in either file (L642; `sensitivity_model.py` L561–563). `sensitivity_model.py` tests overlap against this whole history, so territories from past years count. App. 5 Table A5.6 describes it as the "Registry of all active household territories for the current year".
- The re-draw needs both conditions (`and`, L361–362): a crowded but rich location is accepted. App. 5 Table A5.4 describes overlap alone as grounds for rejection.
- Fixed-territory mode (`sensitivity_model.py`, L528–539) keeps the main camp on the same cell every year (`set_camp` at the unchanged `pos`); only family camps move. Ch. 5 §5.6 says households "could move freely only within" their territory.
- The territory radius depends on mean suitability within 20 cells *after* earlier households have degraded the surface this year (L631), so placement order affects territory size.
- In `model.py` a failed household calls `self.remove()` (L592). In Mesa 3, `Agent.remove` deregisters the agent from the model, but whether it also leaves the grid depends on the Mesa version (not checked here). If it stays, it would count as an occupied cell in `eval_neighborhood` (L299–301). `sensitivity_model.py` removes it from the grid explicitly (L500).
