---
type: mechanism
created: 2026-10-08
code: "model.py › env_degrade, L393–420; get_degrade_kernel, L235–243"
odd: "Submodels; Design concepts › interaction"
---

# Within-year degradation

## What it does
When a camp is set, suitability around it is lowered at once in the shared `suitability_raster`, so households placed later in the same year see a degraded landscape. For each cell in a square window of half-width r around the camp:

`S' = max(S − D / (dist + 0.001), 0.0001)`, with `dist = (|dx| + |dy|) / 2`

Then the centre cell gets `S' = max(S − P, 0.0001)`.
- Main camp: r = territory radius (20/25/30; 25 at Year 0), D = 0.5, P = 0.9 (L651, L1002).
- Family camp: r = 11, D = 0.3, P = 0.5 (L647, L999).

The surface is rebuilt from scratch at the next `move_year` ([suitability surface](suitability-surface.md)), so this drop lasts until the end of the year. Degradation across years runs through the [occupation history layers](occupation-history-layers.md).

## Where it lives
- `model.py › env_degrade`, L393–420; kernel `get_degrade_kernel`, L235–243 (cached in `KERNEL_CACHE`).
- Calls: `year_initiation` L647, L651; `NomadModel.__init__` L999, L1002. The fixed-territory branch in `sensitivity_model.py` calls it at L534 and L537.

## Inputs and parameters
| Parameter | Value | Documented (App. 5 Table A5.4) |
|---|---|---|
| Household D | 0.5 | Household degradation intensity (D) = 0.5; Assumed |
| Household P | 0.9 | Household centre penalty (P) = 0.9; Assumed |
| Family D | 0.3 | Nuclear family degradation intensity (D) = 0.3; Assumed |
| Family P | 0.5 | Nuclear family centre penalty (P) = 0.5; Assumed |
| Family radius | 11 cells | Nuclear family camp radius = 11 cells; Assumed |
| Floor | 0.0001 | Minimum suitability floor = 0.0001; Assumed |
| Distance metric | (\|dx\| + \|dy\|)/2 (half Manhattan), +0.001 | App. 5 eq. A5.1–A5.2 caption: "d(x,y) is Manhattan distance from the occupied cell" |

## What it changes
`model.suitability_raster` in place. This affects every later reader in the same year: other households' placement, territory radius, `env_mean_val` in the economic step (prosperity index) and `build_enclosure` scores.

## Assumption it encodes
Ch. 5 §5.3.1: "Grazing, trampling, and the gathering of wood and water deplete a cell's resources." The reduction "is largest at the occupied cell and decays with distance from it". Because reductions are written at once, "households positioned later in the same year face an already-degraded landscape and are less likely to make camp nearby", the coordination between households being "modelled implicitly".

## Justification
- Owner's documentation: Ch. 5 §5.3.1 and Fig. 5.4 (caption: "within-year inverse-distance suitability reduction across household territory (~5 km radius; eq. A5.1) and nuclear family sub-camp (11-cell radius; eq. A5.2)"); App. 5 §A5.2, eq. A5.1–A5.2 and their caption ("Households use D = 0.5 and P = 0.9; nuclear family camps use D = 0.3 and P = 0.5. Minimum suitability is 0.0001."). Ch. 5 cites Boles et al. 2019 and Meroz et al. 2023 for overgrazing in arid environments.
- All magnitudes are "Assumed" (App. 5 Table A5.4).

## My rationale
**My rationale** · owed
> Q: Each camp lowers suitability by D/distance (D = 0.5 household, 0.3 family; L235–243, L393–420). Ch. 5 §5.3.1 names the processes, and App. 5 Table A5.4 marks both values "Assumed". Where do the 0.5 and the 0.3 come from?

## Things to check
- Does P have any effect? At the centre the kernel term is D/0.001, so 500 for D = 0.5 and 300 for D = 0.3 (L240–241). That already takes the centre cell to the 0.0001 floor before the centre penalty P is applied (L418–420), so P = 0.9 and P = 0.5 change nothing. App. 5 Table A5.2 describes D as "fixed at 0.5, weight 0.9", and Table A5.4 lists P as a separate parameter.
- Distance metric. The App. 5 eq. A5.1–A5.2 caption says "d(x,y) is Manhattan distance from the occupied cell". The kernel uses half the Manhattan distance, `(|dx| + |dy|) / 2` (L240), so the reduction at a given cell is twice what the caption's formula gives. The window is a square. Which is intended?
- Radius. Ch. 5 Fig. 5.4 gives the household reduction a "~5 km radius" (20 cells). The code uses the territory radius, 20, 25 or 30 cells (L651).
- The degradation window for the main camp equals the territory radius, so it is larger on poor ground. Ch. 5 §5.3.1 says the reduction extends "across the household's territory", which matches. App. 5 Table A5.2 gives no radius for households.
- The household's own family camps are drawn from its personalised copy taken before its own degradation ([memory and territorial attachment](memory-and-territorial-attachment.md)), so the coordination effect works between households but not among one household's family camps.
  - Settled on [memory and territorial attachment](memory-and-territorial-attachment.md) (Itay, 2026-10-13): later family camps should see the degradation earlier ones caused; for the separate PR (item 14).
  - Noted 2026-10-13: the main camp degrades its surroundings only after all nine family camps are placed (family loop L645–649, main camp L651; Year 0: L997–1002). Even after that fix, family camps would not see their own main camp's degradation.
