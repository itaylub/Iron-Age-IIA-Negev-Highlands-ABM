---
type: mechanism
created: 2026-10-08
code: "model.py › to_gdf, L1131–1157; set_camp, L277–280; year_initiation, L649; NomadModel.step, L1016"
odd: "Design concepts › observation"
---

# Site classification (from occupation signal to simulated sites)

## What it does
Turns a run into a point pattern comparable with the survey record:
1. Each year's `target_raster` holds the occupation signal: main camp +0.5, family camp +0.25, enclosure reuse +1, new enclosure +(1 + 2 × prosperity). It is stored at the end of each `step` (L1016) and reset in `move_year` (L1038).
2. `to_gdf` sums the 75 yearly rasters. Cells below 0.6 are dropped and the rest set to 1 (L1132–1134).
3. Every cell in `model.enclosures` is set to 2 (L1136–1139).
4. Cells become points in EPSG:2039, with lower-left origin (139,554.93, 478,515.53) and 250 m cells (L1131, L1141–1156).

## Where it lives
`model.py › to_gdf`, L1131–1157. The increments are written in `set_camp` (L280), `year_initiation` (L649), `NomadModel.__init__` (L992, L1001) and `Household_Agent.step` (L572, L584).

## Inputs and parameters
Threshold 0.6; increments 0.5 / 0.25; origin and cell size. Ch. 5 §5.5.3 documents the threshold and the 0.5 / 0.25 increments. The threshold is not in App. 5 Table A5.4.

## What it changes
Nothing in the model. It produces the GeoDataFrame scored by the [calibration objective](calibration-objective.md).

## Assumption it encodes
Ch. 5 §5.5.3: a cell "counts as a site once its signal reaches 0.6 (a threshold set by face validation), which takes at least two seasons at a main camp or three nuclear-family stays". Above the threshold "a cell counts as a site whether it was occupied just enough to qualify or intensively for decades, mirroring how the archaeological record is read". Enclosed compounds are marked "from the model's construction list".

## Justification
Owner's documentation: Ch. 5 §5.5.3 (face validation). Sensitivity: Ch. 5 §5.6 "Site-Classification Threshold" varied it from 0.1 to 1.0 on a single run. Site counts went from 245 at 0.6 to nearly 6,000 at 0.1–0.2 and 73 at 0.8–1.0. The enclosure share went from under 1% to 56%, and "The observed share of 6.93% is not replicated at any level of this discretisation".

## My rationale
**My rationale** · owed
> Q: A main camp adds 0.5 and a family camp 0.25 to its cell's signal (set_camp, L280; year_initiation, L649). What archaeological trace do these two increments stand for?

## Things to check
- The threshold sensitivity test reported in Ch. 5 §5.6 has no code in the repository; neither notebook varies the 0.6 in `to_gdf`, which is hard-coded (L1133). See [experiments](../model/experiments.md).
- Enclosure cells are overwritten with 2 whatever their summed signal (L1136–1139), so a single enclosure event makes a site. Ordinary camps need repeated use to pass 0.6. Ch. 5 §5.6 names this asymmetry when discussing the threshold.
- One main camp plus one family camp on the same cell (0.75) also passes the threshold, a combination Ch. 5 §5.5.3 does not mention.
- Is the origin (139,554.93, 478,515.53) the raster's lower-left corner or the centre of the lower-left cell (L1131, L1144–1145)? If it is the corner, points sit at cell corners, 125 m from the centres in x and y.
