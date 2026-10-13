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
Ch. 5 §5.1 (behavioural rules): "Enclosed compounds are taken to express a form of household investment of accumulated surplus from economic activities, that function as communal kin-based, multi-purpose territorial centres. I hypothesize that these centres served purposes such as seasonal storage, social gatherings, and perhaps also exchange (see Chapter 6)." Ch. 5 §5.3.3: the compounds "are read here not as fortresses or seats of authority but as communal infrastructure", so building one "is therefore treated as a non-essential investment".

## Justification
- Owner's documentation: Ch. 5 §5.1 and §5.3.3, with Fig. 5.5 (decision logic). The thresholds "were set during model construction as plausible working values; they stand in for a process the archaeological record cannot specify and are deliberately kept simple" (Ch. 5 §5.3.3).
- Archaeological framing: Ch. 5 points to Chapter 6 for the functions of the compounds. An earlier draft of §5.1 (formerly in `thesis/`) cited Aharoni et al. 1960 and Cohen & Cohen Amin 2004 for the architecture; the final text no longer has that paragraph.

## My rationale
**My rationale** · Itay, 2026-10-12
> Q: Enclosure activity needs a prosperity index above 0.6, combining surplus per worker and local suitability (Household_Agent.step, L555–564). What real-world condition is 0.6 meant to capture?

A better than average conditions. The value is stemming from face validation in the preliminary runs.

## Things to check
- Manpower minima. The reuse (≥ 15) and new-build (≥ 30) tests run after 10 + herd//75 have been subtracted (L547–549, L565, L576). An initial household has about 52 manpower and about 14 herders, so about 28 at test time, below the new-build minimum. Are the documented minima (App. 5 Table A5.4) meant for this reduced workforce?
  - Asked whether 15 and 30 are meant for the free manpower. Itay, 2026-10-12: Yes.
- Start year. Ch. 5 §5.3.3 says eligibility starts "from the fifth year onward". The code tests `model.year > 5`, with Year 0 as the first step, which is the seventh step (L564).
  - Itay, 2026-10-12: Oh, so fix it so the statement will hold (.year>=4).
  - For the separate PR: `self.model.year >= 4` (L564; same in `sensitivity_model.py`).
- Unoccupied? Ch. 5 §5.3.3 speaks of reusing "an existing, unoccupied enclosed compound". The code does not check whether another household is at or near the compound this year.
  - Asked whether reuse should require that. Itay, 2026-10-12: Yes, it should.
  - For the separate PR: what counts as occupied (another household's main camp on the cell, a family camp, or the compound lying inside another territory this year). Deferred to the PR (agreed, Itay, 2026-10-13: confirmed).
- A "new build" can land on an existing compound's cell: own enclosures of any age, or others' older than 15 years, are candidates in `build_enclosure` (L842–875). The event is recorded as new construction with the larger signal (L577–586).
  - Asked whether that is intended. Itay, 2026-10-12: Yes, as it is hypothesized that reuse after such long time requires more resources.
- "Built within the previous 35 years" (Ch. 5 §5.3.3). Each reuse appends a fresh entry with the current year to `model.enclosures` and `enc_memory` (L573–574), so the age windows run from the last use, not from construction.
  - Asked which should count. Itay, 2026-10-12: Age from last use.
  - For the write-up: Ch. 5 §5.3.3's "built within the previous 35 years" should describe use rather than construction.
- Enclosure memory. Ch. 5 §5.2.2 calls it "a longer, shared record … both the household's own and others' it has come across". In the code `enc_memory` gains entries only when the household itself builds or reuses (L574, L586).
  - Itay, 2026-10-12: It is meant to hold only enclosed compounds that the household have used (built either by him or other).
  - The code matches. For the write-up: Ch. 5 §5.2.2's "others' it has come across" should say compounds the household has used.
- New-site criterion. Ch. 5 §5.3.3 says the household "selects a location above the average environmental quality of its territory". The code compares with `mean_val + 1`, where `mean_val` is the mean suitability within 20 cells of the camp, not over the territory (L577, L896–897).
  - Itay, 2026-10-12: Above the average by a significant margin (hence +1).
  - The reply settles the margin. The mean is taken within 20 cells of the camp (`env_mean_val`, a 41 × 41 Moore window, L255–263), while the territory may be 25 or 30.
  - Asked whether the average should be the one within 20 cells of the camp or over the territory. Itay, 2026-10-13: Average within 20 cells.
  - The code matches. For the write-up: Ch. 5 §5.3.3's "average environmental quality of its territory" should say the average within 20 cells of the camp, plus a margin.
- Ch. 5 §5.5.4 and §5.7 report about 2.4 times the observed share of enclosed compounds. The bullets above are the places in the code where enclosure frequency is set.
- Range of Q. Q (`env_quality`) is the mean of the shared surface within 20 cells, divided by 10 (L552–553); "base suitability" means the shared surface, without each household's own perception (Itay, 2026-10-12). That surface can exceed 10 where reuse potential is high, so Q can exceed 1 in principle, while Ch. 5 §5.3.3 gives it as running "from 0 … to 1". Not checked in runs. Raised in the suitability round and deferred here (agreed 2026-10-12).
  - Asked whether Q should be capped at 1, or the separate PR should first log Q in a test run and decide from that. Itay, 2026-10-12: Yes.
  - The reply did not say which of the two options; asked again. Itay, 2026-10-13: Log Q.
  - For the separate PR: log Q (`env_quality`, L552–553) in a test run, then decide whether to cap it at 1. Until then Ch. 5 §5.3.3's "from 0 … to 1" stands unchecked.
