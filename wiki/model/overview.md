---
type: model
created: 2026-10-08
repository: "https://github.com/itaylub/Iron-Age-IIA-Negev-Highlands-ABM"
code_commit: 032c2a1fbd26ec47017c65939ca372e02a575938
code_commit_date: 2026-10-26
code_branch: claude/separate-pr-code-fixes
code_note: "model.py last changed in 5a83e8d (2026-10-14, the PR 8 fixes); sensitivity_model.py in 5f415eb (2026-10-25). Re-pinned 2026-10-26 from 2249331 (2026-10-05)."
previous_code_commit: 2249331932b0a42ec47c33bca0ac94f4b8728813
version: "1.0.0 (CITATION.cff); CHANGELOG [Unreleased] reshaping since"
software_doi: "10.5281/zenodo.21336898"
data_doi: "10.5281/zenodo.20473345"
---

# Nomad ABM: overview

An agent-based model in Python on Mesa 3 (`Code/model.py`) in which nine nomadic households reposition once a year for 75 years over a 318 × 280 grid of 250 m cells in the Negev Highlands. The accumulated occupation is classified into sites and compared with the Iron Age IIA record. A variant (`Code/sensitivity_model.py`) runs the sensitivity tests. File-level detail is in the [inventory](inventory.md).

This page describes the code after the 18 fixes of PR 8 (separate-PR list in `log.md`, 2026-10-14), at the commit in the frontmatter. Line numbers in the dated Things to check entries refer to the earlier commit `2249331`.

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

- On the italics (asked whether they mark a quote from Lake 2014). Itay, 2026-10-12: No, it is in italic because it is important nuance, as if I just told you it is of the hypothesis testing type it could have been interpreted as a test of validity.

## Entities and state variables

**Household agents** (`model.py › Household_Agent`, L544–1018). Ch. 5 §5.2.2 defines a household as "a tentative group of about ten nuclear families". State in the code (`__init__`, L545–574):

| Variable | Code | Initial value | Documented in |
|---|---|---|---|
| Livestock | `flock_head` | sum of 10 draws of ⌊N(105, 15)⌋, about 1,050 (L548–551) | Ch. 5 §5.2.2; App. 5 Table A5.5 |
| Manpower | `manpower` | max(35, ⌊flock/20⌋) (L555–556); also for a successor household (PR 8 item 7) | Ch. 5 §5.2.2 |
| Surplus | `surplus` | 0 (L560–561) | Ch. 5 §5.2.2 |
| Camp location | `pos` (Mesa) | set by placement | Ch. 5 §5.2.2 |
| Last camp | `last_camp` | None (L572); set to `pos` by `reset_pos` before the household leaves the grid each year (L1124) | Ch. 5 §5.3.1 ("P is last year's camp", write-up list) |
| Territory | `territory` | list of cells; radius 25 at Year 0 (L1066; intended, Itay 2026-10-12), 20/25/30 later (L674–683); kept until the household places again, for the territory bonus | Ch. 5 §5.3.1 |
| Home-range centre | `general_territory_center` | None (L566); the Year-0 camp from Year 1, then moved toward the last camp (L663–669) | Ch. 5 §5.3.1 |
| Camp memory | `memory`, entries `[cell, quality, year]` | empty | Ch. 5 §5.3.1 |
| Enclosure memory | `enc_memory`, entries `[cell, year]` | empty | Ch. 5 §5.3.3 |
| Personalised suitability | `own_suitability_raster` | None, rebuilt yearly for the main-camp draw (L975–1018) | Ch. 5 §5.3.1 |
| Home-range and memory bonus | `home_memory_bonus` | None (L571), built with the surface above and reused for the family-camp draws (L1009, L388) | Ch. 5 §5.3.1 |
| Prosperity index | `prosperity_index` | None, set each step (L594–595) | Ch. 5 §5.3.3 |
| Environmental quality Q | `env_quality` | None, set each step (L574, L586); logged in `household_data.csv` | Ch. 5 §5.3.3 |
| Enclosure surplus floor | `threshold` | 10 (model-level, L1049) | Ch. 5 §5.3.3 |

Ch. 5 §5.2.2 and App. 5 Table A5.5 also list a crisis flag (`in_severe_crisis`), which the code no longer has: it was removed in December 2025, and Itay (2026-10-12) accepts adjusting the text to the code. See Things to check.

**Nuclear families** are not agents. Each year nine family camps are drawn inside the household's territory (`year_initiation`, L687–691).

**Environment** (`NomadModel`, L1021–1135): `suitability_raster`, `return_raster` (the occupation accumulator), `stress_ras` (resource-exhaustion layer, 10 = untouched), `veg_ras` (pasture: the year's array 2, no-data cells set to 0; `pasture_layer`, L273–280) and `veg_map` (`veg_ras` reduced for exhaustion, L1111–1114), `ag_ras` (agricultural potential), `target_raster` (this year's occupation signal), `place_raster` (valid-placement mask: the Israeli Negev Highlands, leaving out the Egyptian side for lack of data and the eastern lowlands, per Itay 2026-10-12), `ext_raster` (the Negev Highlands outline; the band between the two masks is the buffer, per Itay 2026-10-12), `enclosures` (list of `[cell, year, agent]`), `territories` (the territories set so far this year, cleared in `move_year`, L1098). App. 5 Table A5.6 documents these. The model also holds `np_rng`, its numpy generator (L1028; see Initialisation).

## Scales

- Space: 318 rows × 280 columns of 250 m cells. `NomadModel` builds `MultiGrid(width=280, height=318, torus=False)` from the raster shape (L1030–1031), and Ch. 5 §5.2.1.1 says space is bounded, not toroidal. Model extent 3,251.54 km² (`Num_agents`, L290; App. 5 Table A5.4). CRS is ITM, EPSG:2039 (`to_gdf`, L1227–1233; docs/DATA.md).
- Time: annual steps for 75 years in calibration (`objective_function`, `n_years=75`, L1370). Each step is "a single episode of occupation within a given year" (Ch. 5 §5.2.3).

## Process overview and scheduling

As implemented in `run_model_opt` (L1319–1367), with `model.step` and `model.move_year`:

1. **Initialise** (`NomadModel.__init__`, L1022–1086): compute this year's suitability from shuffled rainfall years, then place nine households one after another in creation order. For each: draw a camp (re-drawn while the candidate area is crowded by the territories already set or poor; see [placement](../mechanisms/camp-and-territory-placement.md)), set a radius-25 territory, place nine family camps, degrade the surroundings.
2. **Each year t = 0…74, `step`** (L1088–1092): all households run `Household_Agent.step` in random order (`shuffle_do`, on Mesa's seeded generator). Each does [herd update](../mechanisms/herd-dynamics.md), [surplus](../mechanisms/household-economy.md), [enclosure reuse/build](../mechanisms/enclosure-construction.md), [crisis](../mechanisms/crisis-and-replacement.md) (a household that fails leaves the grid and the schedule, L628–629), livestock purchase, manpower and surplus decay. The year's `target_raster` is stored, then `year += 1`.
3. **Between years, `move_year`** (L1094–1120): remove all households from the grid, keeping each one's last camp (`reset_pos`, L1122–1125), and clear this year's territories. Rebuild the [suitability surface](../mechanisms/suitability-surface.md) with this year's rainfall draw and the [occupation history layers](../mechanisms/occupation-history-layers.md). Update pasture (array 2, then `veg_map` for exhaustion) and reset `target_raster`. Create [replacement households](../mechanisms/crisis-and-replacement.md). Then all households run `year_initiation` in a new random order: [memory pruning and personalised suitability](../mechanisms/memory-and-territorial-attachment.md), [camp and territory placement](../mechanisms/camp-and-territory-placement.md), and [within-year degradation](../mechanisms/within-year-degradation.md).
4. **After 75 steps**: [classify sites](../mechanisms/site-classification.md) and score against the record ([calibration objective](../mechanisms/calibration-objective.md)).

Placement and the economic step are two separate passes over the households, each in its own random order. Ch. 5 §5.4 describes one pass in which each household places and then manages its herd. See Things to check.

Itay (2026-10-12): the herd update at the start of `step` (L577) counts as the "resource calculation" stage of Ch. 5 Fig. 5.3, and the ODD follows the code's two passes rather than the single pass of Ch. 5 §5.4.

Ch. 5 Fig. 5.3 lists "Eight sequential stages" per year: "environmental update; household repositioning in randomised order; territory establishment; resource calculation; prosperity assessment and enclosure decision; crisis check; livestock and demographic adjustment; and end-of-year bookkeeping". Ch. 5 Fig. 5.6 gives the outer loop: "model.move_year() resets household grid positions and updates dynamic environmental layers, followed by model.step() executing the full annual household decision sequence". Captions as printed on pp. 146 and 160 of the thesis PDF; the figure images have not been examined.

## Initialisation

- Number of households: `Num_agents()` returns ⌊(3,251.54 / 18) / 20⌋ = 9 (L289–293). Ch. 5 §5.2.4 derives it from 18 km² per nuclear family (Rosen & Finkelstein 1992 on Seligman et al. 1962), ten families per household (about 180 km²), so about 18 households at carrying capacity, halved "again to be on the conservative side".
- In Year 0, households choose "on environmental suitability alone" (Ch. 5 §5.2.4). In the code, memory, territory and home-range centre are empty at Year 0, so the personalised raster equals the shared one. Each household's Year-0 camp memory holds the mean suitability within 20 cells of the camp (L1076); later years use the territory radius (L694). From Year 1 the home-range centre starts at the Year-0 camp (L663–664).
- Random numbers: each run derives two numpy generators from its seed (`run_generators`, L530–541), one for the order of the rainfall years and one for camp-cell draws (`np_rng`). Mesa's own generator, seeded with the same seed (`super().__init__(seed=seed)`, L1027), sets the household order in `shuffle_do` and makes every Python-level draw. Runs therefore reproduce from their seeds and share no random state with other runs in the same process (PR 8 items 10 and 17).
- Rainfall years: the indices of the yearly stack (76 groups per docs/DATA.md) are shuffled once per run (L1328–1330) and read in order, so a run uses each observed year at most once. The file holds 75 years (`num_groups` = 75; DATA.md's 76 counts the `metadata` group), so a 75-year run uses each exactly once. Itay (2026-10-12): 75 years were prepared so that each year of a run is different; only the longer sensitivity runs reuse years. The year's pasture and agriculture arrays derive from the same rainfall year (Itay, 2026-10-12).

## Input data

Inputs are fetched from Zenodo into `Data/` (`scripts/download_data.py`; docs/DATA.md). Permanent layers come from `per_data_10_25.h5` (six arrays, of which four enter the suitability sum). The yearly stack is `yearly_data_10_25.h5` (three arrays per year: array 0 enters the suitability sum as current-year rainfall, array 1 is agricultural potential, array 2 is the herds' pasture). There are two masks (`ext_raster.npy`, `place_raster.npy`) and the calibration points: `P_for_calib.shp` by default (`NOMAD_ABM_CALIB_SHP` overrides it), and `P_for_calib_strict.shp`, built from the sites table by `scripts/make_calib_sites.py` (commit `87dd382`) and passed with `--calib-shp` to the calibration scripts. See [inventory](inventory.md) and [suitability surface](../mechanisms/suitability-surface.md).

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
Dated entries below keep the line numbers of commit `2249331` (2026-10-05), as checked then. Lines starting "Done in PR 8" were added on 2026-10-26.
- Schedule order. The code runs placement for all households, then the economic step for all, in two separate random orders (L1015, L1043). Ch. 5 §5.4 describes each household placing and then managing its herd in turn. Ch. 5 §5.2.3 gives a third order, enclosure decision before the livestock update, while the code updates the herd first (L545–546, then L564–587). Ch. 5 Fig. 5.3 puts "resource calculation" before the enclosure decision and "livestock and demographic adjustment" after the crisis check. That matches the code if the herd update (L545) counts as resource calculation and the purchase and manpower changes (L594–605) as the later adjustment. Which order should the ODD describe?
  - Itay, 2026-10-12: Initial herd update count as a resource update.
- Still open after that reply: one pass or two? Ch. 5 §5.4 says "the households act one after another, in a random order. First, each household selects a camp, sets its territory and disperses the nuclear families within it (Section 5.3.1); then it works through the following behaviours". The code places all households in one random order (`move_year`, L1043) and runs all economic steps in another (`step`, L1015).
  - Itay, 2026-10-12: Follow the code.
- Crisis flag. Ch. 5 §5.2.2 lists a "Crisis flag" state variable, Ch. 5 Fig. 5.2 has a "Crisis Status" node, and App. 5 Table A5.5 names it `in_severe_crisis`. The Table A5.5 caption says "Variable names reflect Python implementation". No such attribute exists in `model.py` or `sensitivity_model.py`, where crisis is handled inside `step` (L589–593). Should the tables drop it, or is it meant to be added?
  - Itay, 2026-10-12: It was in previous code versions, please check carefully as I don't remember I removed it. What is important is that the crisis loop is functioning, if the flag has been removed it's ok and the text can be adjusted to it.
  - Checked 2026-10-12 (git history). `in_severe_crisis` was set in `handle_survival_crisis` in `run_numpy.ipynb` (commits `de80181`, 2025-11-18, and `f754d9c`, 2025-12-08). It was set when the household had to cull adult females, and it then cut the territory to radius 15 "for conservative grazing". Commit `8e7a865` (2025-12-10, "simplify and other functionality (optuna dashboard) - continue") removed it, together with culling by age class. Ch. 5 §5.3.4 describes no crisis-time territory cut. The current crisis path, read but not run: surplus < 10 (L589) → `handle_survival_crisis` sells head at 0.3 (L825–826, L708–721) → failure if surplus < 0, herd < 15 or manpower ≤ 0, which queues a replacement (L828–837) → `self.remove()` (L592) → replacement in the next `move_year` (L1039–1042). Known differences from Ch. 5 §5.3.4 are on [crisis and replacement](../mechanisms/crisis-and-replacement.md). The flag now appears only in Ch. 5 §5.2.2, Fig. 5.2 and App. 5 Table A5.5.
- Year-0 territory. At initialisation the territory radius is fixed at 25 and the degradation radius at 25 (L993, L1002). From Year 1, `year_initiation` uses 20/25/30 by local suitability (L632–641). `sensitivity_model.py` uses 20/25/30 at Year 0 too (L895–908). Which is intended?
  - Itay, 2026-10-12: The first one.
  - The first option is `model.py`'s fixed radius 25 at Year 0. Ch. 5 §5.3.1 and App. 5 Table A5.4 give the 20/25/30 rule with no Year-0 exception. The sensitivity tests ran `sensitivity_model.py`, which applies 20/25/30 at Year 0 (L895–908).
  - Asked whether "the first one" meant `model.py`'s fixed radius 25. Itay, 2026-10-12: Yes.
  - The sensitivity-file difference is taken up with the two model files ([inventory](inventory.md), Things to check).
  - Done in PR 8: `sensitivity_model.py` uses radius 25 at Year 0 (item 2, `6a3a981`) and measures the Year-0 camp memory within 20 cells, as `model.py` does (`5f415eb`, 2026-10-25). The check that `sensitivity_model.py` at its default switches reproduces the calibrated model's runs is in `sensitivity\check\check.csv` of the strict calibration's results folder on the PC (not read in this session).
- Run length versus data. `model.py` reads `inds[self.year]` with no wrap-around (L486, L1029). A run longer than the number of yearly groups (76 per docs/DATA.md) would fail. `sensitivity_model.py` cycles with a modulo (L399, L945), which is how the 150-year test ran.
  - Itay, 2026-10-12: As the simulated data was prepared specifically for this, I made only 75 years so each year is different, but for longer runs (only in the sensitivity analysis) I reused some of the years.
  - Asked whether "simulated data" means the observed IMS years processed for the model (Ch. 5 §5.2.1.2). Itay, 2026-10-12: Yes, and the other arrays that derive from it (pasture and agriculture).
  - 75 or 76? docs/DATA.md lists 76 yearly groups (`group_0`…`group_75`). A 75-year run reads 75 of them: `inds[0]` at Year 0 (L1257), then `inds[1]`…`inds[74]` in 74 `move_year` calls (L1272–1273, L1029).
  - Itay, 2026-10-12: I am not sure the extra group is real at all, maybe it is just 75 groups. We need to check the actual file.
  - Checked 2026-10-12. `yearly_data_10_25.h5` from the repository history (commit `14cb755^`; SHA-256 equal to docs/DATA.md, so the calibration file) has 76 top-level groups: `group_0`…`group_74` (75 years, each with `array_0`–`array_2`) and `metadata` (`num_groups` = 75, `arrays_per_group` = 3). DATA.md counted `metadata` as a year. `LazyYearlyData` takes its length from `num_groups` (L76, L79–80), so a 75-year run uses every year exactly once. Read with the HDF5 C library; Zenodo is not reachable from this session.
  - Deferred to the [experiments](experiments.md) round (agreed 2026-10-12): in the 150-year run the modulo replays years 0–74 in the same shuffled order for years 75–149 (`sensitivity_model.py` L399, L945).
  - Done in PR 8 (item 18, `cbd1fb7`): each further 75-year cycle gets a new shuffle of the year order (`sensitivity_model.py › NomadModel.move_year`, L1018–1024 at the current commit).
  - "Independently"? Ch. 5 §5.2.1.2 says each year's rainfall "is taken from a randomly chosen observed year (August–July) in the IMS record" and speaks of "Drawing independently each year from measured present-day rainfall". The code shuffles the years once and uses each at most once (L1254–1255), which matches the reply ("so each year is different").
  - Asked which wording the journal version should use. Itay, 2026-10-12: "A random year from a list of 75(?) years, each only once" - feel free to improve the phrasing, but this is the essence.
  - Wording for the journal version, Itay, 2026-10-12 (approved Claude draft): "Each simulated year takes its rainfall, and the pasture and arable-land layers derived from it, from one of 75 observed years in the IMS record (August–July, years with at least 20 active stations). The years are drawn at random without replacement, so no year repeats within a 75-year run." It replaces Ch. 5 §5.2.1.2's "drawing independently each year".
- Validation or plausibility? Itay's Purpose reading (2026-10-12) says the test "need not be framed as a test of validation but a test of plausibility". Ch. 5 titles §5.5 "Model Calibration and Validation" and §5.5.4 "Validation Results: Model-Data Comparison". Should the journal version keep "validation" for the model–data comparison?
  - Itay, 2026-10-12: Yes, this is validation in technical meaning not in the broad sense.
- Model extent. `Num_agents` derives nine households from 3,251.54 km² (L283–287), which App. 5 Table A5.4 calls the "Total model extent", bounded by the "Natural topographic boundaries of Negev Highlands; western limit imposed by Israel–Egypt border", and Ch. 5 §5.2.4 "the study area". In the calibration masks that figure matches `ext_raster` (52,012 cells, 3,250.8 km²). By Itay's replies (2026-10-12, [suitability surface](../mechanisms/suitability-surface.md), Things to check), `ext_raster` also holds the buffer: the Egyptian side and the eastern lowlands, which are not Negev Highlands. The placement area (`place_raster`) is 2,347.2 km²; by the same formula, ⌊2,347.2 / 18 / 20⌋ = 6 households. Raised in the suitability round, 2026-10-12.
  - Asked whether the household count, and the "model extent" in the text, should rest on `ext_raster`'s 3,251 km² or on the 2,347 km² placement area. Itay, 2026-10-12: Keep the current one, anyway I take there a minimalistic approach and divides it by 2 (it could have been 18, as each household contains 10 nuclear families not 20).
  - The code's `/ 20` is the ten families per household times that halving. For the write-up: Table A5.4 and Ch. 5 §5.2.4 describe the 3,251.54 km² as bounded by the Negev Highlands and the Israel–Egypt border, while it also holds the buffer.
- Observed site count: 462 or 463? Ch. 5 §5.5.3 ("Of the 462 sites analysed within model boundaries … 32 (6.93%) contain enclosed compounds", p. 166) and the article note give 510 sites, 48 excluded, 462 in the model area. `P_for_calib_strict.shp` (2026-10-24) holds 463 sites, 32 of them compounds (6.91%).
  - Checked 2026-10-26 in `Data/P_for_calib_strict_sites.csv` (written by `scripts/make_calib_sites.py`; every table site with its area tests). Of the 510 table sites, 462 lie on `place_raster` (32 compounds, 6.93%) and 463 match a point of the older `P_for_calib.shp`, the script's default area test (32 compounds, 6.91%). The extra site is 378 ("Other", ITM 175563.7, 499235.5): inside `ext_raster`, outside `place_raster`, so on the buffer band. All 510 lie on `ext_raster`. The site-type target changes from 32/430 = 0.0744 to 32/431 = 0.0742.
  - Some of the 48 sites outside `place_raster` lie south and east of it rather than on the Egyptian side (e.g. sites 57, 60, 107, 372, 462, 496), while Ch. 5 and the article note describe the 48 as on the Egyptian side.
  - Itay, 2026-10-26: Go with 463.
  - Itay, 2026-10-26, on the description of the excluded sites: Yes I know, we can refine it to strictly in the Negev Highlands and in the Israeli side, as sites on the south and east that were excluded are nearby but outside of the strict ecological zone.
  - For the write-up (ODD and article): 463 sites in the model area, 32 enclosed compounds (6.91%), the calibration target; the excluded sites are those outside the strict Negev Highlands zone on the Israeli side, including nearby sites to the south and east. Site 378, counted among the 463, lies on the buffer band outside `place_raster`.
