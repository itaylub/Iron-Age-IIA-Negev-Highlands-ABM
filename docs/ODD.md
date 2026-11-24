# Iron Age IIA Negev Highlands ABM: ODD model description

> **Skeleton (2026-10-26).** Headings follow Grimm et al. (2020), supplement S1 (ODD guidance and checklists); the section after the ODD follows supplement S7 (describing simulation experiments). Each "To write" block paraphrases the S1 checklist for that part, with S1 page numbers; S1 asks authors to reuse its own checklist wording, so take the exact phrases from S1 when writing. "Material" points to the wiki pages and settled decisions to draw on. Delete both kinds of block as each part is written. The text describes the code on branch `claude/separate-pr-code-fixes` (model code as of `5a83e8d`; see `wiki/model/overview.md` for the commit).

<!-- Opening sentence: S1 p. 2 asks every ODD to begin with a fixed sentence citing Grimm et al. 2006 and Grimm et al. 2020. Copy it verbatim from S1 p. 2 here. -->

## Overview

### 1. Purpose and patterns

<!-- Agreed 2026-10-26. Open: the citation for the Iron Age IIA intensification in 1.1 ("[citation to add]"); naming and citing the competing interpretation after "sedentary settlement" in 1.1 is deferred. -->

#### 1.1 Purpose

Following the classification of Lake (2014), the model is of the hypothesis-testing type. It assesses the plausibility of the palimpsest hypothesis, testing whether a proposed mechanism can produce the observed archaeological pattern.

The palimpsest hypothesis, as tested here, holds that the stone-built sites of the Negev Highlands accumulated over decades during the economic intensification of the Iron Age IIA [citation to add]. Both site types, the enclosed compounds and the other sites, represent the repeated seasonal returns of a few mobile pastoral households. They therefore do not record a single horizon of contemporaneous sedentary settlement. The model asks whether such local households, moving each year in response to the environment and to their own past use of the land, can generate a regional distribution of sites and a share of enclosed compounds similar to those observed.

This is a test of plausibility rather than of validity. Reproducing the patterns would show that the mechanisms suffice to generate them, but would not rule out other explanations. A secondary purpose is to estimate, through calibration, the relative importance of the environmental and historical factors that shaped where households camped.

#### 1.2 Patterns

Two patterns in the observed record serve as criteria for judging whether the model suits its purpose. Both are regional, so the model is not judged on where any single site lies.

The observed record comprises 463 Iron Age IIA sites, 32 of them enclosed compounds, taken from the sites table of the Negev Highlands (Lubel, 2026). The table lists 510 sites, and the other 47 lie outside the model area. Most of them lie just across the border in Egypt, where the geological, rainfall and other environmental data the model needs are insufficient. The rest lie south and east of the Negev Highlands, close to them but outside their ecological zone.

**Pattern 1: the regional distribution of all sites.** The sites are clustered at every scale tested, with no sign of regular spacing, and they concentrate in an east–west band about 4–8 km wide that runs from the Avdat–Ramat Matred area through Ramat Barnea towards Tell el-Qudeirat (Lubel and Davidovich, in press). Secondary concentrations lie in the north-east (the Yeroham–Dimona syncline) and the south-west (the Horsha–Lotz area). The band coincides with the least-cost passage from the northern Arabah, through the Zin Valley and the central Negev Highlands, to Tell el-Qudeirat. Within it, site densities would exceed what the region could sustain at any one time (compare Rosen and Finkelstein, 1992). The palimpsest hypothesis explains this density as repeated, largely seasonal occupations, with favoured places revisited across generations. If the hypothesis holds, the households' accumulated occupation should concentrate in the same area and along the same axis.

The pattern is measured with a standard deviational ellipse, centred on the mean of the sites, with its two axes scaled to two standard deviations of their spread along the directions of greatest and least dispersion (Yuill, 1971). Its size, elongation and orientation describe where the sites concentrate and along which axis they are drawn out. The observed ellipse is 2.2 times as long as it is wide because of the east–west band, and the sites in the north-east turn its long axis northward, to 55.7° from east.

**Pattern 2: the site-type ratio.** Enclosed compounds, structures with a central courtyard enclosed by a casemate wall, are thought in the literature to be the central nodes of this phenomenon (e.g. Aharoni et al., 1960; Rothenberg, 1967; Meshel, 1975; Haiman, 1992; Cohen and Cohen Amin, 2004; Finkelstein, 2014). Sites with an enclosed compound are a small minority, and they may also include circular structures, rectangular structures, towers, four-room houses or unclassified structures. The other sites have no enclosed compound and consist of these structure types alone, singly or in combination. The site classification follows Lubel (2026). The two types are hypothesized to contribute to the archaeological record differently: the other sites record frequent, short-lived repositioning of small social units (e.g. nuclear families), whereas the enclosed compounds were probably reoccupied and reused over longer intervals (Ben-Yosef, 2026; Lubel and Davidovich, in press). The palimpsest hypothesis takes the enclosed compounds to be communal, kin-based, multi-purpose territorial centres, built from accumulated household surplus and reused over the years. The ratio of enclosed compounds to other sites therefore tests whether the households' decisions to build and reuse enclosed compounds produce them at a frequency resembling the observed one.

| Pattern | Observed value (463 sites) | Test |
|---|---|---|
| 1. Regional distribution of all sites | Standard deviational ellipse at 2 SD: mean centre 168,385 E, 515,557 N (ITM); semi-axes 33.3 and 15.2 km (2.2:1); area 1,589 km²; long axis 55.7° anticlockwise from east | Overlap of the observed and simulated ellipses, as intersection over union (IoU) |
| 2. Site-type ratio | 32 enclosed compounds to 431 other sites: a ratio of 0.074 (1:13.5); 6.91% of all sites | Absolute difference between the observed and simulated ratios of enclosed compounds to other sites |

Matching both patterns at once reduces equifinality, since many parameter sets may reproduce one of them but far fewer reproduce both (Grimm et al., 2005; Gallagher et al., 2021). The simulated record is measured in the same way, from the sites that the households' accumulated occupation leaves on the grid (4.11 Observation; 7.10 Site classification). The calibration combines the two tests into one error, described in the section on calibration after the ODD.

The observed and simulated records are not symmetrical. The observed record is an accumulation of seasonal activity across the period, filtered further by differential preservation, variable survey coverage and post-depositional processes; the simulated record holds every household position and enclosed compound over the run. The model is therefore judged realistic enough not when it matches the observed patterns exactly, but when the remaining differences could plausibly be attributed to this asymmetry.

### 2. Entities, state variables, and scales

<!-- Agreed 2026-11-24 in the Claude doc "ODD Element 2: Entities, state variables, and scales". -->

#### 2.1 Entities

The model contains three types of entities: Households, Environment (represented as a raster grid) and Enclosed compounds. Each of the following entities has distinct attributes and roles in the model, as detailed below:

- **Households:** The only agent type, representing an aggregation of closely related families, implemented as 10 nuclear families, each about 5-6 people. The families are not agents: they have no state of their own and appear in the model only as camps, the household's main camp and nine family camps placed within its territory each year. One of those families acts as the main branch of the household which stands for the leader of such social unit. The household communally manages its herd and all its sub-units revolve around the main household camp, bounded in a territory around it. The households are taken to represent the social level where decisions on where to move and camp, whether to build or reuse an enclosed compound and when to sell animals were taken (Khazanov, 1984; Salzman, 2004; Hammer, 2025), and thus are key for the emergence of the palimpsest pattern. The household is a modelling simplification, not a reconstruction of any specific tribal organisation. The model holds a stable population of nine households throughout a run; a household that fails is replaced by a new one (7.9). Nine is half the roughly 18 households the study area could support at carrying capacity: if the palimpsest forms from so few households, a larger population is expected to reinforce it (5).
- **Environment:** The model's environment is represented as a raster grid of 318 × 280 cells, whose main layer (`suitability_raster`) is the composite score of the following environmental variables:
  - Proximity to the Tell el-Qudeirat–Faynan corridor (permanent): walking-time cost-distance to the least-cost route between Tell el-Qudeirat and the Faynan copper district.
  - Proximity to permanent water (permanent): walking-time cost-distance to springs and wells.
  - Mean annual rainfall (permanent): the long-term mean, interpolated from IMS station records.
  - Slope (permanent): from the ALOS PALSAR DEM; cells too steep for camping (slope suitability below 1) are set to zero in the composite.
  - Current-year rainfall (annual): the rainfall of one observed year at a time, interpolated in the same way; the years come in a random order, each used once per run.
  - Resource exhaustion (dynamic): the degradation that past occupation has accumulated around each cell, recent occupation weighing more.
  - Reuse potential (dynamic): the accumulated occupation of each cell, which draws households back to used locations, above all to enclosed compounds.

  Those variables are taken to represent the set of considerations that guided the locational decisions of the agents as well as their ability to invest in non-essential building (enclosed compounds). The environment is dynamic and updates landscape-wide once a year (according to the year's rainfall and the occupation history) and locally in relation to the agents' actions (e.g. a camp lowers the suitability of the cells around it for the rest of the year (7.5)). This dynamic representation of the environment is meant to capture the temporal dimension and considerations that led the agents' locational decisions. The environment records the agents' camps and enclosed compounds through the yearly occupation layer (`target_raster`), added each year to the occupation history (`return_raster`), which in turn alters the environmental values.

  Besides the composite, the grid holds two annual layers that are kept out of it: the year's pasture and cultivable land. Both derive from that year's rainfall, so weighting them beside it would count rainfall twice. The households read them directly instead: pasture, reduced where resources are exhausted, sets what the herds can graze; cultivable land lowers the herd a household needs; and both help rank the sites for enclosed compounds (7.6, 7.7, 7.8).
- **Enclosed compounds:** Built structures that represent the enclosed compounds of the archaeological record (1.2), an architectural type that has been attributed significant importance throughout the research history (1.2). In the model, following the palimpsest hypothesis, they are taken to be communal infrastructure built from accumulated household surplus, rather than fortresses or seats of authority, and they are hypothesized to have served for seasonal storage, social gatherings and perhaps also exchange (Lubel and Davidovich, in press). They are the model's only lasting trace of household wealth, and through them the yearly decisions of a few households can fix places in the landscape for decades. No enclosed compounds exist at the start of a run; their number is an outcome of the households' prosperity rather than a parameter (7.8). Enclosed compounds have no behaviour of their own. Each occupies a single cell and holds a history of use, the year and household of every build or reuse, so one enclosed compound can record many visits by several households. A build or reuse is assumed to weigh more in the occupation history than a camp, so standing enclosed compounds draw households back (7.2), and in the output every cell that has held one becomes an enclosed compound site (7.10).

#### 2.2 State variables

The state variables in the model are split for convenience of presentation by entity: households, environment and enclosed compounds.

**Households** (`Household_Agent`; values from `Code/model.py` at `b5a951f`)

| Variable (code) | Type and units | Static or dynamic | Initial value | Meaning |
|---|---|---|---|---|
| Herd size (`flock_head`) | integer; goats (all animals counted as goats) | dynamic, yearly | sum of ten draws of ⌊N(105, 15)⌋, one per family; a replacement inherits the failed household's herd plus ten draws of ⌊N(90, 15)⌋ | the household's main productive asset |
| Manpower (`manpower`) | integer; people | dynamic, yearly | max(35, ⌊herd / 20⌋) | the people available for herding, moving and building |
| Surplus (`surplus`) | real number; surplus units (a model unit with no real-world equivalent) | dynamic, yearly | 0; a replacement inherits the failed household's surplus | accumulated wealth, drawn on in lean years and spent on enclosed compounds |
| Main camp (`pos`) | grid cell, (x, y) integers | dynamic, drawn each year | drawn on the shared suitability surface alone at Year 0 | where the household camps this year |
| Last camp (`last_camp`) | grid cell, (x, y) integers | dynamic | none until the first year ends | last year's main camp, kept to move the home-range centre |
| Home-range centre (`general_territory_center`) | (x, y) real numbers; grid cells | dynamic | the first camp | the centre of the area the household returns to; moved a tenth of the way towards each year's camp |
| Territory (`territory`) | set of grid cells, each (x, y) integers | dynamic, set each year | radius 25 around the camp at Year 0 | the cells within 20, 25 or 30 cells of the main camp, the radius larger where local suitability is low; the family camps lie inside it |
| Camp memory (`memory`) | list of (cell, (x, y) integers; local mean suitability, real number on the 0–10 scale; year, integer) | dynamic | the Year-0 main and family camps | past main and family camps; each entry is forgotten at random, the more likely the older it is |
| Enclosure memory (`enc_memory`) | list of (cell, (x, y) integers; year, integer) | dynamic | empty | the enclosed compounds the household has built or reused |
| Prosperity index (`prosperity_index`) | real number; dimensionless | derived, each year | none | surplus per worker × Q; gates enclosed compound building and reuse |
| Environmental quality, Q (`env_quality`) | real number; dimensionless | derived, each year | none | mean shared suitability within 20 cells of the camp ÷ 10 |
| Personal suitability surface (`own_suitability_raster`, `home_memory_bonus`) | 318 × 280 grid of real numbers; suitability scale | derived, rebuilt each year | none | the shared surface plus the household's home-range, camp-memory and territory bonuses; the household draws its camps from it |

**Environment: global variables** (`NomadModel`)

| Variable (code) | Type and units | Static or dynamic | Meaning |
|---|---|---|---|
| Year (`year`) | integer; years | dynamic | the current year, counted from 0; a run lasts 75 years |
| Rainfall order (`inds`) | list of integers; indices of the rainfall years | static within a run | the order of the observed rainfall years, shuffled once per run so that each is used once |
| Suitability weights (`weights`) | seven real numbers summing to 1; dimensionless | static | the weights of the seven layers in the composite, and the only parameters fitted in the calibration |
| Territories this year (`territories`) | list of sets of grid cells, each (x, y) integers | dynamic, reset each year | the territories already set this year, which later households avoid overlapping |
| Enclosed compound events (`enclosures`) | list of (cell, (x, y) integers; year, integer; household) | dynamic | every build and reuse so far; this list is the state of the enclosed compounds |
| Waiting replacements (`scheduled_new_agents`) | list of (herd, integer goats; surplus, real number in surplus units) | dynamic | the herd and surplus of households that failed this year, handed to their replacements at the start of the next |

**Environment: grid layers** (318 × 280 cells)

| Layer (code) | Type and scale | Static or dynamic | Meaning |
|---|---|---|---|
| Corridor proximity (`kb_suitability_raster`) | real number, 0–10 | static | walking-time cost-distance to the least-cost route between Tell el-Qudeirat and the Faynan copper district (2.1) |
| Permanent water (`pw_suitability_raster`) | real number, 0–10 | static | walking-time cost-distance to springs and wells (2.1) |
| Mean annual rainfall (`rain_suitability_raster`) | real number, 0–10 | static | the long-term mean, interpolated from IMS station records (2.1) |
| Slope (`slp_suitability_raster`) | real number, 0–10 | static | from the ALOS PALSAR DEM; where it is below 1 the composite is set to 0 (2.1) |
| Current-year rainfall (`YrainFuzzyMember_calc`) | real number, 0–10 | yearly | the rainfall of the year in turn |
| Resource exhaustion (`yi_hu_stressed_z`, kept as `stress_ras`) | real number, 0–10 | yearly | the occupation history smoothed over a 20-cell radius and rescaled: 10 where the surroundings are unused, falling to 0 where they are heavily used |
| Reuse potential (`return_ras`) | real number, 0 upwards, no upper bound | yearly | the occupation history × 5, cell by cell |
| Shared suitability (`suitability_raster`) | real number, 0–10, higher only where reuse potential is high | yearly, and lowered within the year around each camp | the weighted sum of the seven layers, set to 0 on slopes too steep for camping and outside the Negev Highlands outline |
| Occupation history (`return_raster`) | real number, 0 upwards | yearly | halved each year, with last year's occupation added (cells at 2 or more weighted × 1.5) |
| Occupation this year (`target_raster`) | real number, 0 upwards | within the year, reset each year | +0.5 per main camp, +0.25 per family camp, +1 per enclosed compound reuse, +(1 + 2 × prosperity index) per new enclosed compound |
| Pasture (`veg_ras`) and grazable pasture (`veg_map`) | real number, 0 upwards | yearly | the year's pasture, and the same reduced where resources are exhausted |
| Cultivable land (`ag_ras`) | real number, 0–10 | yearly | the year's cultivable land |
| Negev Highlands outline (`ext_raster`) | integer, 0 or 1 | static | suitability is 0 outside it |
| Placement area (`place_raster`) | integer, 0 or 1 | static | where camps may be placed; the band between it and the outline is the buffer |

**Enclosed compounds** (records in `enclosures`)

| Variable | Type and units | Static or dynamic | Meaning |
|---|---|---|---|
| Location | grid cell, (x, y) integers | static once built | the cell the enclosed compound occupies |
| History of use | list of (year, integer; household) | dynamic | one entry per build or reuse at that cell |
| Time since last use | integer; years | derived | sets whether a household may reuse it: its own within 35 years, others' within 25 (7.8) |

#### 2.3 Scales

The model's space is a discrete grid of 318 × 280 square cells, each 250 × 250 m, covering 79.5 km from north to south and 70 km from east to west. All layers share the Israel Transverse Mercator projection (EPSG:2039), consistent with the sites database (Lubel, 2026) and with the spatial analysis (Lubel and Davidovich, in press). The cell size balances computational cost against two spatial limits. The positional error of survey coordinates can be roughly 100–500 m, as most were taken by hand (Sion, 2014; Davidovich, 2014). Moreover, the remains of a site can often extend over some 400 m (e.g. Rothenberg, 1967; Bruins et al., 2012). A finer cell size would therefore suggest more precise site locations than the recorded coordinates and their own spread represent.

The modelled area follows the natural topographic limits of the Negev Highlands, except in the west, where the placement area is cut at the modern Israel–Egypt border for lack of comparable environmental data (1.2). The Negev Highlands outline (3,251 km²) bounds the suitable landscape, and the placement area (2,347 km²) confines camps to the Israeli part. Space is bounded, not toroidal (Lake, 2020). The band between the masks acts as a buffer: degradation and resource availability are computed across it, but no camp is placed in it, which is meant to keep the region's edge from leaving an artefact in the simulated record. At this scale, the households' working distances of 5–7.5 km for territories and 5 km for Q and the enclosed compound search tie each decision to a local neighbourhood, while the pattern the model is judged on is regional (1.2).

Time advances in annual steps; each step is one episode of occupation in the Negev Highlands, in which every household sets a main camp and its family camps. The model does not specify where a move begins (the Arabah, the previous camp or elsewhere). One move a year simplifies an unknown and diverse rhythm of movement. Annual steps are fine enough to simulate the decisions hypothesized to generate the record, and a finer resolution would add uncertainty and computational cost without need (KISS; Romanowska et al., 2021). The order of the processes within a year is given in section 3.

A run lasts 75 steps (Years 0–74), and each step uses one of the observed rainfall years, drawn in a random order so that each is used once (2.2). Seventy-five years is the minimum duration attributed to the Iron Age IIA activity under the low chronology (Boaretto et al., 2010; Finkelstein and Piasetzky, 2011), although radiocarbon dates suggest it persisted considerably longer (Bruins and van der Plicht, 2007; Mamalya and Erickson-Gini, 2019). The minimal span is a deliberate choice: if the palimpsest can emerge within the shortest span the record allows, a longer duration is expected to reinforce it.

### 3. Process overview and scheduling

> **To write** (S1 pp. 11–14; checklist p. 14). The full schedule of one time step as a hierarchy of actions: which entities run which process, which variables are updated, and in what order the entities act. The reasons for the processes included and for their order.
>
> **Material.** [Overview › Process overview and scheduling](../wiki/model/overview.md#process-overview-and-scheduling). Two shuffled passes each year: placement (`move_year` → `year_initiation`), then the economic step (`step`); the herd update counts as the resource calculation (Itay, 2026-10-12).

## Design concepts

> **To write** (S1 pp. 14–15). At a conceptual level, with cross-references to Element 7 for detail. A concept the model does not use gets one sentence saying so. Give the reasoning behind design choices here where it is short.

### 4.1 Basic principles

> **To write** (S1 p. 15). The concepts, theories, hypotheses or modelling approaches behind the design, at system and agent level; how they enter the model; whether the agent behaviours rest on new or existing theory.
>
> **Material.** The palimpsest model and carrying capacity (Ch. 5 §5.1); [assumptions C1–C10](../wiki/model/assumptions.md); [palimpsest sufficiency](../wiki/questions/palimpsest-sufficiency.md).

### 4.2 Emergence

> **To write** (S1 p. 16). Which key outputs emerge from agent behaviour, and from which behaviours and variables; which outputs are imposed by rules, and by which; why.
>
> **Material.** [Site classification](../wiki/mechanisms/site-classification.md): the site pattern and the compound share emerge from accumulated occupation.

### 4.3 Adaptation

> **To write** (S1 pp. 16–17). For each adaptive behaviour: the decision, the alternatives, the inputs, whether objective-seeking is direct or indirect, and how the choice is made.
>
> **Material.** [Camp and territory placement](../wiki/mechanisms/camp-and-territory-placement.md), [enclosure construction](../wiki/mechanisms/enclosure-construction.md), [crisis and replacement](../wiki/mechanisms/crisis-and-replacement.md).

### 4.4 Objectives

> **To write** (S1 pp. 17–18). For behaviours that seek an objective directly: what the measure represents, what drives it, how it is calculated, and why.
>
> **Material.** No explicit objective function (odd-map). Placement draws in proportion to suitability³; enclosure decisions use the prosperity index (Q uncapped; never above 1 in the calibrated runs, Itay 2026-10-26).

### 4.5 Learning

> **To write** (S1 pp. 18–19). Which behaviours include learning, how it is represented, and why.
>
> **Material.** [Memory and territorial attachment](../wiki/mechanisms/memory-and-territorial-attachment.md): the home-range centre (from last year's camp) and the camp memory change where a household camps.

### 4.6 Prediction

> **To write** (S1 p. 19). How behaviours use explicit or implicit prediction, and why.
>
> **Material.** None in the model; state it.

### 4.7 Sensing

> **To write** (S1 pp. 19–20). What agents sense about themselves and others, the range of sensing, whether values are known exactly, and why.
>
> **Material.** Camp choice senses the whole map; local radii: 20 cells (prosperity, territory size), the territory (pasture, herd capacity). [Suitability](../wiki/mechanisms/suitability-surface.md), [degradation](../wiki/mechanisms/within-year-degradation.md).

### 4.8 Interaction

> **To write** (S1 pp. 20–21). The kinds of interaction, direct or mediated; their range; who interacts with whom; why.
>
> **Material.** Mediated through the environment: within-year degradation, the occupation history layers, the overlap rule, shared compounds (reuse only of unoccupied compounds). [Degradation](../wiki/mechanisms/within-year-degradation.md), [history layers](../wiki/mechanisms/occupation-history-layers.md), [enclosures](../wiki/mechanisms/enclosure-construction.md).

### 4.9 Stochasticity

> **To write** (S1 p. 21). Which processes are stochastic and why.
>
> **Material.** Every random draw: rainfall-year order, camp draws, initial and replacement herds, herd-growth and decline noise, manpower drift, memory pruning, enclosure scoring and choice, household order. Per-run generators and the seeded Mesa schedule ([overview › Initialisation](../wiki/model/overview.md#initialisation)).

### 4.10 Collectives

> **To write** (S1 pp. 21–22). Any collectives, whether they emerge or are explicit entities, and how they interact with agents.
>
> **Material.** The model includes no collectives: the nuclear families inside a household are not agents.

### 4.11 Observation

> **To write** (S1 pp. 22–23). The key outputs used in analysis and how they are collected from the runs; any techniques that make model output comparable with the record.
>
> **Material.** [Site classification](../wiki/mechanisms/site-classification.md) (threshold 0.6), [calibration objective](../wiki/mechanisms/calibration-objective.md), per-run outputs ([inventory › Outputs](../wiki/model/inventory.md#outputs-not-in-git)).

## Details

### 5. Initialization

> **To write** (S1 pp. 23–25; checklist p. 25). Which entities are created and how many, how all state variables get their starting values, how initial locations are set, any initial structures, site-specific data used and how it was prepared, whether experiments vary the initialization, and the reasons for the main choices.
>
> **Material.** [Overview › Initialisation](../wiki/model/overview.md#initialisation), [parameters › Population and initialisation](../wiki/model/parameters.md#population-and-initialisation). Nine households from the extent; Year-0 territory radius 25; Year-0 camp memory within 20 cells; 75 observed rainfall years, each used once per run.

### 6. Input data

> **To write** (S1 pp. 25–26; checklist p. 26). Whether input data drive variables or events during a run; what each input represents, its units and source; how it was collected or prepared; any input produced by another model.
>
> **Material.** [Inventory › Input data](../wiki/model/inventory.md#input-data-not-in-git-zenodo-105281zenodo20473345), [suitability surface](../wiki/mechanisms/suitability-surface.md). Yearly array 0 rainfall, array 1 agricultural potential, array 2 pasture (year 74's no-data cells set to 0); the Tell el-Qudeirat layer is the corridor; masks `ext_raster` and `place_raster`; calibration sites `P_for_calib_strict.shp`. Data DOI 10.5281/zenodo.20473345.

### 7. Submodels

> **To write** (S1 pp. 27–28; checklist p. 28). Every submodel in its own subsection: equations, algorithms, parameters and how their values were chosen; any tests, calibration or analysis of the submodel on its own. Bring each wiki page to the current code first (the bodies still describe `2249331`).

#### 7.1 Suitability surface

> **Material.** [Suitability surface](../wiki/mechanisms/suitability-surface.md).

#### 7.2 Occupation history layers

> **Material.** [Occupation history layers](../wiki/mechanisms/occupation-history-layers.md).

#### 7.3 Memory and territorial attachment

> **Material.** [Memory and territorial attachment](../wiki/mechanisms/memory-and-territorial-attachment.md).

#### 7.4 Camp and territory placement

> **Material.** [Camp and territory placement](../wiki/mechanisms/camp-and-territory-placement.md).

#### 7.5 Within-year degradation

> **Material.** [Within-year degradation](../wiki/mechanisms/within-year-degradation.md).

#### 7.6 Herd dynamics

> **Material.** [Herd dynamics](../wiki/mechanisms/herd-dynamics.md). Herd values to validate against Dahl & Hjort (1976).

#### 7.7 Household economy

> **Material.** [Household economy](../wiki/mechanisms/household-economy.md). The 1:75 herder ratio to confirm (perhaps Günther et al. 2021).

#### 7.8 Enclosure construction

> **Material.** [Enclosure construction](../wiki/mechanisms/enclosure-construction.md).

#### 7.9 Crisis and replacement

> **Material.** [Crisis and replacement](../wiki/mechanisms/crisis-and-replacement.md).

#### 7.10 Site classification

> **Material.** [Site classification](../wiki/mechanisms/site-classification.md).

#### 7.11 Parameters

> **To write.** One table: name, value, units, submodel, source or justification.
>
> **Material.** [Parameters](../wiki/model/parameters.md), including the calibrated weights (trial 197 of `opt_fixed_strict_2026_10`).

## Calibration, simulation experiments, and model analysis

> Not part of the ODD itself; organised after Grimm et al. (2020), supplement S7.

### Calibration and model output verification

> **To write** (S7 pp. 1–2). Which parameters were calibrated, why and how: full or submodel, together or separately; the ranges and the sampling method; initial conditions and run settings; the patterns matched; the fitting criteria and strategy; technical details such as replicates and software.
>
> **Material.** [Calibration objective](../wiki/mechanisms/calibration-objective.md), [experiments](../wiki/model/experiments.md), [parameters › Calibrated weights](../wiki/model/parameters.md#calibrated-weights). Optuna TPE (`constant_liar`), Median pruner (10 startup trials, 5 warm-up steps), 10 runs per trial, seeds trial × 100 + i, stopping rule, 30-run re-runs of the 10 leading distinct sets; `scripts/calibrate.py`, `scripts/analyse_calibration.py`.

### Model output corroboration

> **To write** (S7 p. 2). Comparison of model output with data or patterns not used in calibration.
>
> **Material.** To decide which outputs serve here.

### Sensitivity analysis

> **To write** (S7 pp. 2–3). Which parameters were varied, how, and what the outputs showed about the model's sensitivity.
>
> **Material.** Null baseline, run length, site threshold, number of households, territory; `scripts/sensitivity.py` (`aefbae5`), `Code/sensitivity_model.py` and its two switches.

### Simulation experiments for model analysis

> **To write** (S7 p. 3 on). The experiments run to analyse the model and answer its question.

## Software and data availability

> **Material.** Code: <https://github.com/itaylub/Iron-Age-IIA-Negev-Highlands-ABM> (Zenodo software DOI 10.5281/zenodo.21336898; new version to come). Data: Zenodo 10.5281/zenodo.20473345. Python with Mesa 3.5.1 (`requirements.txt`, `environment.yml`).

## References

> Grimm et al. 2006; Grimm et al. 2020; Lake 2014; the sources cited in the sections above.
