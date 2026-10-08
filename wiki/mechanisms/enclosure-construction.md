---
type: mechanism
created: 2026-10-08
code: "model.py › Household_Agent.step, L550–587; find_recent_enclosure, L779–814; build_enclosure, L840–915"
odd: "Submodels; Design concepts › emergence, objectives, collectives"
---

# Enclosure construction (prosperity, reuse, new builds)

## What it does
In each household's step, after herd, surplus and manpower deductions:
1. **Prosperity index** = `surplus / (2 × (manpower + 10 + herders)) × env_quality`, where `env_quality` = mean shared suitability within 20 cells of the camp ÷ 10 (L552–562). The denominator restores the manpower deducted earlier in the step.
2. **Eligible** if the index > 0.6 and `model.year > 5` (L563–564).
3. **Reuse** if manpower ≥ 15 and surplus ≥ 10 (`threshold`) and `find_recent_enclosure` returns a cell (L565–575). Candidates are the household's own `enc_memory` entries under 35 years old (score 35 − age) and any `model.enclosures` entry under 25 years old from a previous year (score 0.8 × (25 − age)), all within 20 cells (Chebyshev) of the camp. Scores are multiplied by `1 + 0.02 × veg + 0.02 × ag` and U(0.8, 1.2), and one is drawn by weight (L779–814). Cost: 10 manpower, 6 surplus; +1 to `target_raster`; 90% of the manpower returns.
4. **Otherwise build new** if the index > 0.8, manpower ≥ 30 and surplus ≥ 30 (L576–587). `build_enclosure` scores: own enclosures in the territory (age-based score, ×1.5 "ownership bias"); others' enclosures in the territory older than 15 years; and, if there are no strong reuse candidates (average score ≤ 8) or with probability 0.3, any territory cell without an enclosure from the last 25 years whose `0.7 × suit + 0.15 × veg + 0.15 × ag` exceeds the camp's mean suitability + 1. One candidate is drawn by weight; with no candidates the camp cell is used (L840–915). Cost: 20 manpower, 25 surplus; +(1 + 2 × prosperity) to `target_raster`; 90% of the manpower returns.
5. Both reuse and new builds append `[cell, year, agent]` to `model.enclosures` and `[cell, year]` to the household's `enc_memory`.

## Where it lives
`model.py › Household_Agent.step`, L550–587; `find_recent_enclosure`, L779–814; `build_enclosure`, L840–915. Enclosure cells become value-2 sites in [site classification](site-classification.md) (L1136–1139), and their signal feeds reuse potential ([occupation history layers](occupation-history-layers.md)).

## Inputs and parameters
All in App. 5 Table A5.4 and marked "Assumed": prosperity thresholds 0.6 and 0.8; manpower ≥ 15 (reuse) and ≥ 30 (new); costs 10/6 and 20/25; 90% manpower recovery; reuse windows 35 (own) and 25 (others'); others' weighting 80%; selection noise ±20%. Not in App. 5: start year (> 5), enclosure signal `1 + 2 × prosperity`, the 1.5 ownership bias, the average-score cut of 8, the 0.3 / 0.4 probabilities of considering new cells, and the `mean + 1` site criterion.

## What it changes
`surplus`, `manpower`, `model.enclosures`, `enc_memory`, `target_raster`.

## Assumption it encodes
Ch. 5 §5.1: enclosed compounds are read "as communal places, plausibly periodic gathering points for otherwise dispersed groups, rather than seats of authority", and "building an enclosed compound reflects infrastructure investment depending on surplus of available resources". "The leading premise is that enclosed compounds arise from local decisions, not from top-down planning." Building is "a non-essential investment" (Ch. 5 §5.3.3).

## Justification
- Owner's documentation: Ch. 5 §5.1 and §5.3.3. The thresholds "were set during model construction as plausible working values; they stand in for a process the archaeological record cannot specify and are deliberately kept simple" (Ch. 5 §5.3.3).
- Archaeological framing: Ch. 5 §5.1 cites Aharoni et al. 1960 and Cohen & Cohen Amin 2004 for the architecture, and Chapter 3's spatial analysis for the communal reading.

## My rationale
**My rationale** · owed
> Q: Enclosure activity needs a prosperity index above 0.6, combining surplus per worker and local suitability (Household_Agent.step, L555–564). What real-world condition is 0.6 meant to capture?

## Things to check
- Manpower minima. The reuse (≥ 15) and new-build (≥ 30) tests run after 10 + herd//75 have been subtracted (L547–549, L565, L576). An initial household has about 52 manpower and about 14 herders, so about 28 at test time, below the new-build minimum. Are the documented minima (App. 5 Table A5.4) meant for this reduced workforce?
- Start year. Ch. 5 §5.3.3 says eligibility starts "from the fifth year onward". The code tests `model.year > 5`, with Year 0 as the first step, which is the seventh step (L564).
- Unoccupied? Ch. 5 §5.3.3 speaks of reusing "an existing, unoccupied enclosed compound". The code does not check whether another household is at or near the compound this year.
- A "new build" can land on an existing compound's cell: own enclosures of any age, or others' older than 15 years, are candidates in `build_enclosure` (L842–875). The event is recorded as new construction with the larger signal (L577–586).
- "Built within the previous 35 years" (Ch. 5 §5.3.3). Each reuse appends a fresh entry with the current year to `model.enclosures` and `enc_memory` (L573–574), so the age windows run from the last use, not from construction.
- Enclosure memory. Ch. 5 §5.2.2 calls it "a longer, shared record … both the household's own and others' it has come across". In the code `enc_memory` gains entries only when the household itself builds or reuses (L574, L586).
- New-site criterion. Ch. 5 §5.3.3 says the household "selects a location above the average environmental quality of its territory". The code compares with `mean_val + 1`, where `mean_val` is the mean suitability within 20 cells of the camp, not over the territory (L577, L896–897).
- Ch. 5 §5.5.4 and §5.7 report about 2.4 times the observed share of enclosed compounds. The bullets above are the places in the code where enclosure frequency is set.
