# Nomad ABM — ODD Protocol

This document describes the Nomad ABM following the **ODD (Overview,
Design concepts, Details) protocol** of Grimm et al. (2020). It is the
canonical technical specification of the model for reviewers and
replicators. For the full archaeological framing and discussion, see
Chapter 4 of the thesis; for the complete parameter and equation
tables, see Appendix 4.

> **Cross-references** in this document use the form §N.N for thesis
> chapter sections and §A4.N for appendix sections. Parameter values
> reported here are the **calibrated/used values from the current
> manuscript** (single source of truth: Appendix 4 of the thesis).

---

## 1. Purpose and patterns

### Purpose

The model tests whether **autochthonous nomadic processes** —
specifically annual household repositioning, prosperity-driven
infrastructure investment, and crisis responses — are *sufficient* to
generate the Iron Age IIA archaeological palimpsest documented in the
Negev Highlands (c. 980–830 BCE). The model evaluates sufficiency, not
necessity: showing that the nomadic-development hypothesis *can*
reproduce observed patterns establishes its plausibility as an
interpretive framework, without claiming it is the only explanation
(§4.1.2).

### Patterns used as design criteria

Two archaeological patterns derived from 462 sites within the model
boundaries (Chapter 3) constrain the model and serve as calibration
targets (§4.6.2):

1. **Spatial distribution** — standard deviational ellipse of all sites,
   summarising regional extent, orientation, and centroid (1,585.02 km²
   ellipse; major axis 66.68 km at 55.66°; ITM centroid 168,369.37 E /
   515,592.33 N).
2. **Site-type ratio** — proportion of enclosed compounds (32 / 462,
   ≈ 6.93 %; ratio ≈ 1:13.3) among architectural site types.

The model is judged successful when both patterns can be reproduced
simultaneously under a stable parameter configuration (Pattern-Oriented
Modelling; Grimm et al. 2005).

---

## 2. Entities, state variables, and scales

### Spatial scale

- Grid: **318 × 280 cells**, each **250 m × 250 m** (6.25 ha cell, ~3 252 km² total).
- Coordinate system: **ITM** (Israel Transverse Mercator).
- Topology: bounded (non-toroidal). A buffer zone supports edge-effect
  smoothing for environmental layers; a binary `place_raster` masks
  valid placement cells (§4.2.1).

### Temporal scale

- Time step: **1 year**, representing one occupation season.
- Run length: **75 years** (Years 0–74), approximating the Iron Age IIA
  duration in the Negev Highlands (§4.2.4).

### Entities

**Household agents** are extended-family groups (~10 nuclear families,
~50–60 individuals). The model initialises **9 households**, derived
conservatively from Rosen & Finkelstein (1992); the population is held
constant by replacement of failed households (§4.5.1).

#### Household state variables (Table A4.5)

| Variable | Type | Units | Dynamic / static | Description |
|---|---|---|---|---|
| `flock_head` | int | goats | dynamic | Livestock holdings (≥15 for survival) |
| `surplus` | float | abstract units | dynamic | Accumulated economic resources |
| `manpower` | int | persons | dynamic | Available workforce |
| `territory` | list of cells | — | dynamic (annual reset) | Spatial claim around the camp |
| `memory` | list of `[pos, quality, year]` | — | dynamic | Personal encampment history |
| `enc_memory` | list of `[pos, year]` | — | dynamic | Collective enclosure knowledge |
| `in_severe_crisis` | bool | — | dynamic | Crisis flag (triggers emergency conversion) |
| `own_suitability_raster` | 318×280 array | 0–10+ | dynamic | Personalised landscape perception |
| `pos` | (x, y) | grid coords | dynamic | Current camp cell (None between years) |

#### Environment / model-level state variables (Table A4.6)

Static rasters loaded at initialisation: `mean_annual_rainfall`,
`slope`, `kb_distance` (cost-distance to Tel el-Qudeirat),
`pw_distance` (cost-distance to permanent water), `place_raster`
(valid-placement mask).

Dynamic rasters updated each year: `annual_rainfall`,
`arable_soil_distance`, `veg_ras` (annual pasture), `ag_ras` (annual
agricultural potential), `suitability_raster` (weighted combined
suitability), `stress_ras` (cumulative degradation, spatially
smoothed), `return_raster` (reuse potential), `target_raster`
(cumulative occupation tracker over all 75 years).

Lists maintained at the model level: `enclosures` (all constructed
compounds with year and builder) and `territories` (active claims for
the current year).

---

## 3. Process overview and scheduling

Each year executes a **two-phase cycle** (§4.5.2):

### Phase A — Household decision-making

Households are processed in **random order** to avoid systematic
advantages. Each household, in turn, executes:

1. Resource calculation and stochastic scenario application (§4.3.2).
2. Prosperity assessment and enclosure decision — reuse or new build
   if thresholds met (§4.3.3).
3. Crisis response if `surplus < 10` (livestock conversion) or if
   `surplus > 100` and `flock_head < 25` (livestock acquisition)
   (§4.3.5).
4. Livestock dynamics: grow up to 20 % when carrying-capacity ratio
   > 1.1, decline 10–30 % when ratio < 0.9 (§4.3.2).
5. Manpower demographic update and surplus decay (30 % baseline,
   progressive 5–25 % above 100 units).

After all households act, agent states and the `target_raster` are
recorded.

### Phase B — Environmental transition

1. `pos` reset for all households.
2. `annual_rainfall` stochastically resampled from IMS records.
3. Derived annual rasters recomputed (`veg_ras`, `ag_ras`,
   `arable_soil_distance`).
4. `stress_ras` updates from cumulative degradation (§4.4.1) and is
   spatially smoothed over a 5 km radius.
5. `return_raster` updates with any newly constructed enclosures.
6. `suitability_raster` recomputes from current calibrated weights.
7. **Household repositioning**: each household prunes its memory
   stochastically, then runs the location-selection algorithm
   (§4.3.1), establishes a territory (§4.3.4), places nuclear-family
   sub-camps, and triggers immediate degradation.

The simulation terminates after Year 74's Phase A (no Phase B at the
end), preserving the final spatial configuration for analysis.

---

## 4. Design concepts

| Concept | Implementation |
|---|---|
| **Emergence** | The regional palimpsest, the enclosed-compound:other-site ratio, and the temporal cycling pattern all emerge from local household decisions. No global pattern is imposed. |
| **Adaptation** | Households adjust territory radius (20 / 25 / 30 cells) to local environmental quality (§4.3.4), and adjust herd size to carrying capacity. Crisis responses are conditional behavioural switches. |
| **Objectives** | Households implicitly maximise prosperity (`P = surplus + manpower + environmental_quality / 3`) subject to subsistence constraints. No global utility function is optimised. |
| **Learning** | Households learn through experience-weighted memory (decay `w = 1 / (T − t + 1)`, max age 15 yr) and a long-term *territorial centre* (90 % previous / 10 % current weighting). |
| **Sensing** | Households sense suitability of cells within their potential territory (20–30 cell radius) and the global enclosure registry within their memory horizon. Sensing is perfect within the radius — no perception error is modelled. |
| **Prediction** | None (myopic). Households react to current and past conditions only. |
| **Interaction** | (i) **Direct**: territorial overlap rejection (25 % threshold). (ii) **Indirect**: shared degradation of overlapping cells; competition for high-suitability locations through sequential placement; shared enclosure registry (other households' enclosures reusable at 80 % weighting). |
| **Stochasticity** | Random seed controls (a) processing order each year; (b) annual rainfall draw from IMS records; (c) stochastic events (25 % adverse / 50 % neutral / 25 % favourable); (d) probabilistic placement (suitability³); (e) memory decay; (f) enclosure selection (±20 %); (g) herd-decline rates within range. |
| **Collectives** | The household is the unit of decision-making (cooperative aggregation of ~10 nuclear families). No higher-level collectives are modelled. |
| **Observation** | Per-year: agent states (`flock_head`, `surplus`, `manpower`, `pos`, `enc_memory`), `target_raster` cumulative occupation. End-of-run: classified sites (signal ≥ 0.6) with binary enclosure flag from the `enclosures` registry; standard deviational ellipse and enclosure ratio for objective scoring. |

---

## 5. Initialisation

Order of operations at Year 0 (§4.5.1):

1. Load permanent rasters (`mean_annual_rainfall`, `slope`,
   `kb_distance`, `pw_distance`, soil layers).
2. Draw the Year-0 rainfall from IMS records → derive `veg_ras`,
   `ag_ras`, `arable_soil_distance`.
3. Initialise dynamic anthropogenic layers (`stress_ras`,
   `return_raster`) to zero.
4. Compute initial `suitability_raster` from calibrated weights —
   purely environmental, no experience modifications.
5. Create **9 household agents** with:
   - `flock_head ~ N(μ ≈ 1 050, σ)` (Rosen & Finkelstein 1992).
   - `manpower = max(√(flock_head / 18), 5)`.
   - `surplus = 0`.
   - empty `memory`, `enc_memory`, `territory`.
6. Place households in random order: each draws a position with
   probability ∝ suitability³ over valid placement cells; establishes
   a territory (Moore neighbourhood, radius 20/25/30 by quality);
   spawns nuclear-family sub-camps inside the territory; **immediately
   degrades** the landscape so later households see a modified
   surface.

All seeds are derived from the run-level seed for full reproducibility
(`seed_replicate = seed_trial × 100 + replicate_index`; §A4.3).

---

## 6. Input data

The model consumes pre-processed geospatial inputs (Table A4.1) plus
the IMS rainfall record. All rasters share the 318 × 280 grid in ITM.

### Permanent rasters

| Layer | Source | Pre-processing |
|---|---|---|
| `mean_annual_rainfall` | IMS station data | IDW interpolation, linear fuzzy (0–100 mm → 0–10) |
| `slope` | JAXA ALOS PALSAR DEM, 12.5 m | Resampled to 250 m, FuzzySmall (mid = 15°, spread = 3) |
| `kb_distance` | Tel el-Qudeirat point | Tobler cost-distance (hours), FuzzySmall (mid = 4 h, spread = 1) |
| `pw_distance` | Springs/wells (topo maps) | Tobler cost-distance (hours), FuzzySmall (mid = 3 h, spread = 1) |
| Arable soil polygons | Israeli Geological Survey (loess, Hatzeva Fm.) | Zonal statistics with annual rainfall |
| Vegetation polygons | Danin (1983); Ron et al. (2024) | Categorical, drives `veg_ras` |
| `place_raster` | Modern Israel-Egypt boundary + valid extent | Binary mask |

### Annual driver

Historical rainfall years from IMS (Aug–Jul), filtered to years with
≥ 20 active stations, are drawn uniformly at random each simulation
year. The drawn year's interpolated grid is normalised identically to
the permanent rainfall layer.

### Calibration target

`P_for_calib.shp` — 462 archaeological sites within the model boundary,
each with `value ∈ {1, 2}` (1 = other site type, 2 = enclosed
compound). Used by the objective function (`docs/objective_function.md`)
to compute spatial-ellipse and ratio scores.

---

## 7. Submodels

References are to Appendix 4 of the thesis (read-only on Drive) for
full equations and parameter values. Selected key equations are
restated here for self-containment.

### 7.1 Location selection (§4.3.1)

Each household evaluates a personalised suitability surface:

```
S_personal(x, y) = S_global(x, y)
                 + GaussianPeak(home-range centre, +5.0, σ = 50 cells)
                 + TerritoryEdgeBonus (within 20 cells of last year)
                 + Σ_memory MemoryAdjustment(quality, age)
                 − 0.5 if (x, y) was occupied in the current year
```

Memory adjustments are positive for cells with past quality ≥ 5 and
negative for past quality < 5; they decay as `1 / (T − t + 1)`.
Memories survive a year with probability declining linearly with age,
zero at 15 years; effective mean lifespan ≈ 7–8 years.

Cell selection is then probabilistic: `P(x, y) ∝ S_personal(x, y)³`
over the valid placement mask. After provisional placement, the
household evaluates territorial overlap with already-placed
households; positions with > 25 % overlap are rejected and the draw is
repeated.

### 7.2 Environmental degradation (§A4.2)

Within-year, per-household degradation:

```
S'(x, y) = max( S(x, y) − D / (d(x, y) + 1) , 0.0001 )    # eq A4.1
S'(centre) = max( S(centre) · (1 − P) , 0.0001 )           # eq A4.2
```

with `D = 0.5, P = 0.9` for the household centre and `D = 0.3, P = 0.5`
for each nuclear-family camp. `d` is Manhattan distance in cells.

Inter-annual cumulative degradation:

```
w(t) = 0.5^(T − t)    # eq A4.3
```

Cumulative degradation is spatially smoothed with an IDW convolution
over a 5 km radius before entering `stress_ras`.

### 7.3 Resource management (§4.3.2)

Surplus and herd dynamics evolve annually:

- Annual surplus generation: `manpower × 18` goats per person is the
  subsistence target; agricultural offset reduces this by up to 40 %.
  Stress (carrying-capacity overshoot) adds maintenance cost equal to
  `0.15 × flock_head × stress_ratio`.
- Consumption: `1.2 surplus per person`.
- Surplus decay: 30 % baseline; additional 5–25 % above 100 units.
- Herd growth ≤ 20 % when CC/`flock_head` > 1.1; decline 10–30 % when
  ratio < 0.9.
- Annual stochastic scenario: P(0.25) adverse / P(0.50) neutral /
  P(0.25) favourable (modifies costs and herd ±5–12 %).

### 7.4 Prosperity and enclosure construction (§4.3.3)

```
P = (surplus + manpower + environmental_quality) / 3
```

Reuse: `P ≥ 0.6`, manpower ≥ 15, surplus ≥ baseline — cost 10 manpower
+ 6 surplus. Searches own enclosures (≤ 35 yr) preferentially, then
others' (≤ 25 yr, 80 % weighting); ±20 % stochastic noise; recent
enclosures (≤ 25 yr) are excluded from new-construction candidate
cells.

New construction: `P ≥ 0.8`, manpower ≥ 30, surplus ≥ 3 × baseline —
cost 20 manpower + 25 surplus. 90 % of manpower returns after
construction.

### 7.5 Crisis response and extinction (§4.3.5)

- `surplus < 10` → emergency livestock conversion at 1 head → 0.3
  surplus, protecting a reserve herd of `18 × manpower` (capped at
  100).
- `surplus > 100` and `flock_head < 25` → livestock acquisition at
  0.3 surplus → 1 head, targeting a 30-head baseline.
- Extinction when `surplus < 0`, `flock_head < 15`, or `manpower = 0`.
  Residual resources seed a replacement household at year-end,
  keeping the regional population at 9.

### 7.6 Calibration objective (§4.6.3, see also `docs/objective_function.md`)

A simulated site is any cell whose cumulative `target_raster` signal
≥ 0.6 across the 75-year run (filtering ephemeral activity). Each such
cell is labelled `value = 2` (enclosed compound) if it appears in the
final `enclosures` registry, otherwise `value = 1` (other architecture).

Spatial error: `1 − IoU(ellipse_simulated, ellipse_observed)`.
Ratio error: `|p_simulated − p_observed|` with `p_observed = 0.0693`.
Composite: `(spatial_error + ratio_error) / 2`. Each parameter trial
averages this over 10 replicates with seeds
`seed = trial × 100 + replicate`.

---

## References (this document)

- Grimm V., Railsback S. F., Vincenot C. E. et al. (2020). *The ODD
  protocol for describing agent-based and other simulation models: A
  second update to improve clarity, replication, and structural
  realism.* JASSS 23(2):7.
- Grimm V., Revilla E., Berger U. et al. (2005). *Pattern-oriented
  modeling of agent-based complex systems: Lessons from ecology.*
  Science 310:987–991.
- See Chapter 4 of the thesis and Appendix 4 for full literature
  citations.
