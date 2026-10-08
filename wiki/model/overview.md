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

> “The model aspires to answer the question: *“Can autochthonous nomadic processes, operating through temporal mobility and environmental feedbacks, sufficiently generate patterns similar to the observed Iron Age IIA archaeological record?”*” (Ch. 5 §5.1)

- README: the model "tests whether autochthonous nomadic processes — temporal cycling driven by environmental volatility and degradation feedback — can plausibly generate the spatial palimpsest documented in the Iron Age IIA archaeological record" (README › Overview).
- The research question has its own page: [palimpsest sufficiency](../questions/palimpsest-sufficiency.md).
- Patterns used to evaluate the model (Ch. 5 §5.5.1–5.5.3): (i) the spatial distribution of all sites, compared through standard deviational ellipse overlap; (ii) the ratio of enclosed compounds to other sites. See [calibration objective](../mechanisms/calibration-objective.md).

**My reading** · owed
> Q: Ch. 5 §5.1 asks whether autochthonous nomadic processes can 'sufficiently generate' the Iron Age IIA pattern. How would you state the model's purpose for the journal ODD now?

## Entities and state variables

**Household agents** (`model.py › Household_Agent`, L515–949). Ch. 5 §5.2.2 defines a household as "a tentative group of about ten nuclear families". State in the code (`__init__`, L516–542):

| Variable | Code | Initial value | Documented in |
|---|---|---|---|
| Livestock | `flock_head` | sum of 10 draws of ⌊N(105, 15)⌋, about 1,050 (L519–522) | Ch. 5 §5.2.2; App. 5 Table A5.5 |
| Manpower | `manpower` | max(35, ⌊flock/20⌋) (L526–527) | Ch. 5 §5.2.2 |
| Surplus | `surplus` | 0 (L531–532) | Ch. 5 §5.2.2 |
| Camp location | `pos` (Mesa) | set by placement | Ch. 5 §5.2.2 |
| Territory | `territory` | list of cells; radius 25 at Year 0 (L993), 20/25/30 later (L632–641) | Ch. 5 §5.3.1 |
| Home-range centre | `general_territory_center` | None (L537) | Ch. 5 §5.3.1 |
| Camp memory | `memory`, entries `[cell, quality, year]` | empty | Ch. 5 §5.3.1 |
| Enclosure memory | `enc_memory`, entries `[cell, year]` | empty | Ch. 5 §5.3.3 |
| Personalised suitability | `own_suitability_raster` | None, rebuilt yearly | Ch. 5 §5.3.1 |
| Prosperity index | `prosperity_index` | None, set each step (L561–562) | Ch. 5 §5.3.3 |
| Enclosure surplus floor | `threshold` | 10 (model-level, L976) | Ch. 5 §5.3.3 |

Ch. 5 §5.2.2 and App. 5 Table A5.5 also list a crisis flag (`in_severe_crisis`), which the code does not have. See Things to check.

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

## Initialisation

- Number of households: `Num_agents()` returns ⌊(3,251.54 / 18) / 20⌋ = 9 (L283–287). Ch. 5 §5.2.4 derives it from 18 km² per nuclear family (Rosen & Finkelstein 1992 on Seligman et al. 1962), ten families per household (about 180 km²), so about 18 households at carrying capacity, halved "again to be on the conservative side".
- In Year 0, households choose "on environmental suitability alone" (Ch. 5 §5.2.4). In the code, memory and territory are empty at Year 0, so the personalised raster equals the shared one.
- Rainfall years: the indices of the yearly stack (76 groups per docs/DATA.md) are shuffled once per run (L1254–1255) and read in order, so a run uses each observed year at most once.

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
- Schedule order. The code runs placement for all households, then the economic step for all, in two separate random orders (L1015, L1043). Ch. 5 §5.4 describes each household placing and then managing its herd in turn. Ch. 5 §5.2.3 gives a third order, enclosure decision before the livestock update, while the code updates the herd first (L545–546, then L564–587). Which order should the ODD describe?
- Crisis flag. Ch. 5 §5.2.2 lists a "Crisis flag" state variable and App. 5 Table A5.5 names it `in_severe_crisis`. No such attribute exists in `model.py` or `sensitivity_model.py`, where crisis is handled inside `step` (L589–593). Should the tables drop it, or is it meant to be added?
- Year-0 territory. At initialisation the territory radius is fixed at 25 and the degradation radius at 25 (L993, L1002). From Year 1, `year_initiation` uses 20/25/30 by local suitability (L632–641). `sensitivity_model.py` uses 20/25/30 at Year 0 too (L895–908). Which is intended?
- Run length versus data. `model.py` reads `inds[self.year]` with no wrap-around (L486, L1029). A run longer than the number of yearly groups (76 per docs/DATA.md) would fail. `sensitivity_model.py` cycles with a modulo (L399, L945), which is how the 150-year test ran.
