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

The observed record comprises 463 Iron Age IIA sites, 32 of them enclosed compounds, taken from the sites table of the Negev Highlands (Lubel 2026). The table lists 510 sites, and the other 47 lie outside the model area. Most of them lie just across the border in Egypt, where the geological, rainfall and other environmental data the model needs are insufficient. The rest lie south and east of the Negev Highlands, close to them but outside their ecological zone.

**Pattern 1: the regional distribution of all sites.** The sites are clustered at every scale tested, with no sign of regular spacing, and they concentrate in an east–west band about 4–8 km wide that runs from the Avdat–Ramat Matred area through Ramat Barnea towards Tell el-Qudeirat (Lubel 2026). Secondary concentrations lie in the north-east (the Yeroham–Dimona syncline) and the south-west (the Horsha–Lotz area). The band coincides with the least-cost passage from the northern Arabah, through the Zin Valley and the central Negev Highlands, to Tell el-Qudeirat. Within it, site densities would exceed what the region could sustain at any one time (compare Rosen & Finkelstein, 1992). The palimpsest hypothesis explains this density as repeated, largely seasonal occupations, with favoured places revisited across generations. If the hypothesis holds, the households' accumulated occupation should concentrate in the same area and along the same axis.

The pattern is measured with a standard deviational ellipse, centred on the mean of the sites, with its two axes scaled to two standard deviations of their spread along the directions of greatest and least dispersion (Yuill, 1971). Its size, elongation and orientation describe where the sites concentrate and along which axis they are drawn out. The observed ellipse is 2.2 times as long as it is wide because of the east–west band, and the sites in the north-east turn its long axis northward, to 55.7° from east.

**Pattern 2: the site-type ratio.** Enclosed compounds, structures with a central courtyard enclosed by a casemate wall, are thought in the literature to be the central nodes of this phenomenon (e.g. Aharoni et al. 1960; Rothenberg 1967; Meshel 1975; Haiman 1992; Cohen & Cohen Amin, 2004; Finkelstein 2014). Sites with an enclosed compound are a small minority, and they may also include circular structures, rectangular structures, towers, four-room houses or unclassified structures. The other sites have no enclosed compound and consist of these structure types alone, singly or in combination. The site classification follows Lubel (2026). The two types are hypothesized to contribute to the archaeological record differently: the other sites record frequent, short-lived repositioning of small social units (e.g. nuclear families), whereas the enclosed compounds were probably reoccupied and reused over longer intervals (Ben-Yosef 2026; Lubel 2026). The palimpsest hypothesis takes the enclosed compounds to be communal, kin-based, multi-purpose territorial centres, built from accumulated household surplus and reused over the years. The ratio of compounds to other sites therefore tests whether the households' decisions to build and reuse compounds produce them at a frequency resembling the observed one.

| Pattern | Observed value (463 sites) | Test |
|---|---|---|
| 1. Regional distribution of all sites | Standard deviational ellipse at 2 SD: mean centre 168,385 E, 515,557 N (ITM); semi-axes 33.3 and 15.2 km (2.2:1); area 1,589 km²; long axis 55.7° anticlockwise from east | Overlap of the observed and simulated ellipses, as intersection over union (IoU) |
| 2. Site-type ratio | 32 enclosed compounds to 431 other sites: a ratio of 0.074 (1:13.5); 6.91% of all sites | Absolute difference between the observed and simulated ratios of enclosed compounds to other sites |

Matching both patterns at once reduces equifinality, since many parameter sets may reproduce one of them but far fewer reproduce both (Grimm et al., 2005; Gallagher et al., 2021). The simulated record is measured in the same way, from the sites that the households' accumulated occupation leaves on the grid (4.11 Observation; 7.10 Site classification). The calibration combines the two tests into one error, described in the section on calibration after the ODD.

The observed and simulated records are not symmetrical. The observed record is an accumulation of seasonal activity across the period, filtered further by differential preservation, variable survey coverage and post-depositional processes; the simulated record holds every household position and enclosed compound over the run. The model is therefore judged realistic enough not when it matches the observed patterns exactly, but when the remaining differences could plausibly be attributed to this asymmetry.

### 2. Entities, state variables, and scales

> **To write** (S1 pp. 6–10; checklist p. 10). The kinds of entities and what each represents, and why these were included and others left out. A table of each entity's state variables: meaning, units, dynamic or static, type, range. Time: discrete or continuous, step length, extent. Space: discrete or continuous, unit shape and size, extent. Any other dimensions. Why these scales.
>
> **Material.** [Overview › Entities and state variables](../wiki/model/overview.md#entities-and-state-variables) and [› Scales](../wiki/model/overview.md#scales). Household agents (about ten nuclear families each; the families are not agents); grid cells with the environmental layers; the model-level records (enclosures, this year's territories, occupation accumulator). No crisis flag. Grid 318 rows × 280 columns of 250 m; the extent (3,251.54 km²) includes the buffer. Annual steps, 75 years.

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
