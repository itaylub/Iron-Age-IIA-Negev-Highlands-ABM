---
type: model
created: 2026-10-08
repository: "https://github.com/itaylub/Iron-Age-IIA-Negev-Highlands-ABM"
code_commit: 2249331932b0a42ec47c33bca0ac94f4b8728813
code_commit_date: 2026-10-05
version: "1.0.0 (CITATION.cff); CHANGELOG [Unreleased] reshaping since"
software_doi: "10.5281/zenodo.21336898"
data_doi: "10.5281/zenodo.20473345"
---

# Nomad ABM: overview

An agent-based model in Python on Mesa 3 (`Code/model.py`) in which nine nomadic households reposition once a year for 75 years over a 318 × 280 grid of 250 m cells in the Negev Highlands. The accumulated occupation is classified into sites and compared with the Iron Age IIA record. A variant (`Code/sensitivity_model.py`) runs the sensitivity tests. File-level detail is in the [inventory](inventory.md).

## Purpose

What the documentation says, in Itay's words:

> “The current model aspires to answer the following question: Can autochthonous nomadic processes, operating through temporal mobility and environmental feedbacks, sufficiently generate patterns similar to the observed Iron Age IIA archaeological record?” (Ch. 5 §5.1, p. 132; the question is in bold in the original)

Ch. 5 §5.1 frames the simulation more cautiously in the canonical version: the palimpsest model "cannot be tested directly in the field", but "it is possible to gain important insights regarding the observed archaeological record and the mechanisms that led to is formation through a series of computerised simulations that model locational decision making of participating social agents" (Ch. 5 §5.1). The behavioural rules "are set this way not because they are thought to truly and fully represent how the population of the Negev Highlands Iron Age IIA behaved, but as general, simplified, tentative behaviours" (Ch. 5 §5.1).

- README: the model "tests whether autochthonous nomadic processes — temporal cycling driven by environmental volatility and degradation feedback — can plausibly generate the spatial palimpsest documented in the Iron Age IIA archaeological record" (README › Overview).
- The research question has its own page: [palimpsest sufficiency](../questions/palimpsest-sufficiency.md).
- Patterns used to evaluate the model (Ch. 5 §5.5.1–5.5.3): (i) the spatial distribution of all sites, compared through standard deviational ellipse overlap; (ii) the ratio of enclosed compounds to other sites. See [calibration objective](../mechanisms/calibration-objective.md).

**My reading** · Itay, 2026-10-12
> Q: Ch. 5 §5.1 asks whether autochthonous nomadic processes can 'sufficiently generate' the Iron Age IIA pattern. How would you state the model's purpose for the journal ODD now?

Following Lake 2014, I would situate this model as a hypothesis testing kind of model, *though this need not be framed as a test of validation but a test of plausibility*. Hence, it is set to test if the palimpsest hypothesis, when operationalized to those certain rules, can reproduce similar patterns. The calibration here enters as to better understand the importance of different variables on the locational preferences that led the Iron Age IIA inhabitants.

## Entities and state variables

**Household agents** (`model.py › Household_Agent`, L515–949). Ch. 5 §5.2.2 defines a household as "a tentative group of about ten nuclear families". State in the code (`__init__`, L516–542):

| Variable | Code | Initial value | Documented in |
|---|---|---|---|
| Livestock | `flock_head` | sum of 10 draws of ⌊N(105, 15)⌋, about 1,050 (L519–522) | Ch. 5 §5.2.2; App. 5 Table A5.5 |
| Manpower | `manpower` | max(35, ⌊flock/20⌋) (L526–527) | Ch. 5 §5.2.2 |
| Surplus | `surplus` | 0 (L531–532) | Ch. 5 §5.2.2 |
| Camp location | `pos` (Mesa) | set by placement | Ch. 5 §5.2.2 |
| Territory | `territory` | list of cells; radius 25 at Year 0 (L993; intended, Itay 2026-10-12), 20/25/30 later (L632–641) | Ch. 5 §5.3.1 |
| Home-range centre | `general_territory_center` | None (L537) | Ch. 5 §5.3.1 |
| Camp memory | `memory`, entries `[cell, quality, year]` | empty | Ch. 5 §5.3.1 |
| Enclosure memory | `enc_memory`, entries `[cell, year]` | empty | Ch. 5 §5.3.3 |
| Personalised suitability | `own_suitability_raster` | None, rebuilt yearly | Ch. 5 §5.3.1 |
| Prosperity index | `prosperity_index` | None, set each step (L561–562) | Ch. 5 §5.3.3 |
| Enclosure surplus floor | `threshold` | 10 (model-level, L976) | Ch. 5 §5.3.3 |

Ch. 5 §5.2.2 and App. 5 Table A5.5 also list a crisis flag (`in_severe_crisis`), which the code no longer has: it was removed in December 2025, and Itay (2026-10-12) accepts adjusting the text to the code. See Things to check.

**Nuclear families** are not agents. Each year nine family camps are drawn inside the household's territory (`year_initiation`, L645–649).

**Environment** (`NomadModel`, L952–1058): `suitability_raster`, `return_raster` (the occupation accumulator), `stress_ras` (resource-exhaustion layer, 10 = untouched), `veg_ras`/`veg_map` (pasture), `ag_ras` (agricultural potential), `target_raster` (this year's occupation signal), `place_raster` (valid-placement mask), `enclosures` (list of `[cell, year, agent]`), `territories`. App. 5 Table A5.6 documents these.

## Scales

- Space: 318 rows × 280 columns of 250 m cells. `NomadModel` builds `MultiGrid(width=280, height=318, torus=False)` from the raster shape (L957–958), and Ch. 5 §5.2.1.1 says space is bounded, not toroidal. Model extent 3,251.54 km² (`Num_agents`, L284; App. 5 Table A5.4). CRS is ITM, EPSG:2039 (`to_gdf`, L1150–1156; docs/DATA.md).
- Time: annual steps for 75 years in calibration (`objective_function`, `n_years=75`, L1294). Each step is "a single episode of occupation within a given year" (Ch. 5 §5.2.3).

## Process overview and scheduling

As implemented in `run_model_opt` (L1242–1291), with `model.step` and `model.move_year`:

1. **Initialise** (`NomadModel.__init__`, L953–1012): compute this year's suitability from shuffled rainfall years, then place nine households one after another in creation order. For each: draw a camp, set a radius-25 territory, place nine family camps, degrade the surroundings.
2. **Each year t = 0…74, `step`** (L1014–1018): all households run `Household_Agent.step` in random order (`shuffle_do`). Each does [herd update](../mechanisms/herd-dynamics.md), [surplus](../mechanisms/household-economy.md), [enclosure reuse/build](../mechanisms/enclosure-construction.md), [crisis](../mechanisms/crisis-and-replacement.md), livestock purchase, manpower and surplus decay. The year's `target_raster` is stored, then `year += 1`.
3. **Between years, `move_year`** (L1020–1043): remove all households from the grid. Rebuild the [suitability surface](../mechanisms/suitability-surface.md) with this year's rainfall draw and the [occupation history layers](../mechanisms/occupation-history-layers.md). Update pasture (`veg_map`) for exhaustion and reset `target_raster`. Create [replacement households](../mechanisms/crisis-and-replacement.md). Then all households run `year_initiation` in a new random order: [memory pruning and personalised suitability](../mechanisms/memory-and-territorial-attachment.md), [camp and territory placement](../mechanisms/camp-and-territory-placement.md), and [within-year degradation](../mechanisms/within-year-degradation.md).
4. **After 75 steps**: [classify sites](../mechanisms/site-classification.md) and score against the record ([calibration objective](../mechanisms/calibration-objective.md)).

Placement and the economic step are two separate passes over the households, each in its own random order. Ch. 5 §5.4 describes one pass in which each household places and then manages its herd. See Things to check.

Itay (2026-10-12): the herd update at the start of `step` (L545) counts as the "resource calculation" stage of Ch. 5 Fig. 5.3.

Ch. 5 Fig. 5.3 lists "Eight sequential stages" per year: "environmental update; household repositioning in randomised order; territory establishment; resource calculation; prosperity assessment and enclosure decision; crisis check; livestock and demographic adjustment; and end-of-year bookkeeping". Ch. 5 Fig. 5.6 gives the outer loop: "model.move_year() resets household grid positions and updates dynamic environmental layers, followed by model.step() executing the full annual household decision sequence". Captions as printed on pp. 146 and 160 of the thesis PDF; the figure images have not been examined.

## Initialisation

- Number of households: `Num_agents()` returns ⌊(3,251.54 / 18) / 20⌋ = 9 (L283–287). Ch. 5 §5.2.4 derives it from 18 km² per nuclear family (Rosen & Finkelstein 1992 on Seligman et al. 1962), ten families per household (about 180 km²), so about 18 households at carrying capacity, halved "again to be on the conservative side".
- In Year 0, households choose "on environmental suitability alone" (Ch. 5 §5.2.4). In the code, memory and territory are empty at Year 0, so the personalised raster equals the shared one.
- Rainfall years: the indices of the yearly stack (76 groups per docs/DATA.md) are shuffled once per run (L1254–1255) and read in order, so a run uses each observed year at most once. Itay (2026-10-12): 75 years were prepared so that each year of a run is different; only the longer sensitivity runs reuse years.

## Input data

Inputs are fetched from Zenodo into `Data/` (`scripts/download_data.py`; docs/DATA.md). Permanent layers come from `per_data_10_25.h5` (six arrays, of which four enter the suitability sum). The yearly stack is `yearly_data_10_25.h5` (three arrays per year). There are two masks (`ext_raster.npy`, `place_raster.npy`) and the calibration points (`P_for_calib.shp`). See [inventory](inventory.md) and [suitability surface](../mechanisms/suitability-surface.md).

## Mechanisms
- [Suitability surface](../mechanisms/suitability-surface.md): seven weighted layers, the calibrated part of the model
- [Occupation history layers](../mechanisms/occupation-history-layers.md): reuse potential and multi-annual resource exhaustion
- [Memory and territorial attachment](../mechanisms/memory-and-territorial-attachment.md): home-range centre, territory bonus, camp memory
- [Camp and territory placement](../mechanisms/camp-and-territory-placement.md): cubic weighted draw, territory radius, family camps
- [Within-year degradation](../mechanisms/within-year-degradation.md)
- [Herd dynamics](../mechanisms/herd-dynamics.md)
- [Household economy](../mechanisms/household-economy.md): surplus, consumption, manpower, livestock purchase
- [Enclosure construction](../mechanisms/enclosure-construction.md): prosperity index, reuse, new builds
- [Crisis and replacement](../mechanisms/crisis-and-replacement.md)
- [Site classification](../mechanisms/site-classification.md)
- [Calibration objective](../mechanisms/calibration-objective.md)

## Other model pages
- [Inventory](inventory.md) · [Parameters](parameters.md) · [Assumptions register](assumptions.md) · [Experiments](experiments.md) · [ODD map](odd-map.md) · [Literature cited](literature-cited.md)

## Things to check
- Schedule order. The code runs placement for all households, then the economic step for all, in two separate random orders (L1015, L1043). Ch. 5 §5.4 describes each household placing and then managing its herd in turn. Ch. 5 §5.2.3 gives a third order, enclosure decision before the livestock update, while the code updates the herd first (L545–546, then L564–587). Ch. 5 Fig. 5.3 puts "resource calculation" before the enclosure decision and "livestock and demographic adjustment" after the crisis check. That matches the code if the herd update (L545) counts as resource calculation and the purchase and manpower changes (L594–605) as the later adjustment. Which order should the ODD describe?
  - Itay, 2026-10-12: Initial herd update count as a resource update.
- Still open after that reply: one pass or two? Ch. 5 §5.4 says "the households act one after another, in a random order. First, each household selects a camp, sets its territory and disperses the nuclear families within it (Section 5.3.1); then it works through the following behaviours". The code places all households in one random order (`move_year`, L1043) and runs all economic steps in another (`step`, L1015).
- Crisis flag. Ch. 5 §5.2.2 lists a "Crisis flag" state variable, Ch. 5 Fig. 5.2 has a "Crisis Status" node, and App. 5 Table A5.5 names it `in_severe_crisis`. The Table A5.5 caption says "Variable names reflect Python implementation". No such attribute exists in `model.py` or `sensitivity_model.py`, where crisis is handled inside `step` (L589–593). Should the tables drop it, or is it meant to be added?
  - Itay, 2026-10-12: It was in previous code versions, please check carefully as I don't remember I removed it. What is important is that the crisis loop is functioning, if the flag has been removed it's ok and the text can be adjusted to it.
  - Checked 2026-10-12 (git history). `in_severe_crisis` was set in `handle_survival_crisis` in `run_numpy.ipynb` (commits `de80181`, 2025-11-18, and `f754d9c`, 2025-12-08). It was set when the household had to cull adult females, and it then cut the territory to radius 15 "for conservative grazing". Commit `8e7a865` (2025-12-10, "simplify and other functionality (optuna dashboard) - continue") removed it, together with culling by age class. Ch. 5 §5.3.4 describes no crisis-time territory cut. The current crisis path, read but not run: surplus < 10 (L589) → `handle_survival_crisis` sells head at 0.3 (L825–826, L708–721) → failure if surplus < 0, herd < 15 or manpower ≤ 0, which queues a replacement (L828–837) → `self.remove()` (L592) → replacement in the next `move_year` (L1039–1042). Known differences from Ch. 5 §5.3.4 are on [crisis and replacement](../mechanisms/crisis-and-replacement.md). The flag now appears only in Ch. 5 §5.2.2, Fig. 5.2 and App. 5 Table A5.5.
- Year-0 territory. At initialisation the territory radius is fixed at 25 and the degradation radius at 25 (L993, L1002). From Year 1, `year_initiation` uses 20/25/30 by local suitability (L632–641). `sensitivity_model.py` uses 20/25/30 at Year 0 too (L895–908). Which is intended?
  - Itay, 2026-10-12: The first one.
  - The first option is `model.py`'s fixed radius 25 at Year 0. Ch. 5 §5.3.1 and App. 5 Table A5.4 give the 20/25/30 rule with no Year-0 exception. The sensitivity tests ran `sensitivity_model.py`, which applies 20/25/30 at Year 0 (L895–908).
- Run length versus data. `model.py` reads `inds[self.year]` with no wrap-around (L486, L1029). A run longer than the number of yearly groups (76 per docs/DATA.md) would fail. `sensitivity_model.py` cycles with a modulo (L399, L945), which is how the 150-year test ran.
  - Itay, 2026-10-12: As the simulated data was prepared specifically for this, I made only 75 years so each year is different, but for longer runs (only in the sensitivity analysis) I reused some of the years.
  - 75 or 76? docs/DATA.md lists 76 yearly groups (`group_0`…`group_75`). A 75-year run reads 75 of them: `inds[0]` at Year 0 (L1257), then `inds[1]`…`inds[74]` in 74 `move_year` calls (L1272–1273, L1029).
  - "Independently"? Ch. 5 §5.2.1.2 says each year's rainfall "is taken from a randomly chosen observed year (August–July) in the IMS record" and speaks of "Drawing independently each year from measured present-day rainfall". The code shuffles the years once and uses each at most once (L1254–1255), which matches the reply ("so each year is different").
- Validation or plausibility? Itay's Purpose reading (2026-10-12) says the test "need not be framed as a test of validation but a test of plausibility". Ch. 5 titles §5.5 "Model Calibration and Validation" and §5.5.4 "Validation Results: Model-Data Comparison". Should the journal version keep "validation" for the model–data comparison?
