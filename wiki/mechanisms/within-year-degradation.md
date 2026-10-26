---
type: mechanism
created: 2026-10-08
code: "model.py › env_degrade, L393–420; get_degrade_kernel, L235–243"
odd: "Submodels; Design concepts › interaction"
body_code_commit: 2249331932b0a42ec47c33bca0ac94f4b8728813
---

# Within-year degradation

> Status 2026-10-26: the body and the line numbers in the `code` field describe commit `2249331` (2026-10-05), before the 18 fixes of PR 8. Fixes that touch this mechanism are marked "Done in PR 8" under Things to check, with line numbers at `032c2a1`. The body is to be brought to the current code when its ODD submodel is written.

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
**My rationale** · Itay, 2026-10-13
> Q: Each camp lowers suitability by D/distance (D = 0.5 household, 0.3 family; L235–243, L393–420). Ch. 5 §5.3.1 names the processes, and App. 5 Table A5.4 marks both values "Assumed". Where do the 0.5 and the 0.3 come from?

From the idea that households have greater effect and for bigger area than a single nuclear family. The values themselves are assumed by myself from the preliminary runs.

## Things to check
- Does P have any effect? At the centre the kernel term is D/0.001, so 500 for D = 0.5 and 300 for D = 0.3 (L240–241). That already takes the centre cell to the 0.0001 floor before the centre penalty P is applied (L418–420), so P = 0.9 and P = 0.5 change nothing. App. 5 Table A5.2 describes D as "fixed at 0.5, weight 0.9", and Table A5.4 lists P as a separate parameter.
  - Asked which is intended at the camp cell: drop to the floor, or lose only P. Itay, 2026-10-13: D should not affect at the camp cell.
  - For the separate PR: set the kernel's centre to 0 (`get_degrade_kernel`, L241), so the camp cell loses only P (0.9 or 0.5). Changes calibrated behaviour: camp cells no longer drop to the floor within the year.
  - Done in PR 8 (item 16, `5a83e8d`), both files: `get_degrade_kernel` L241.
- Distance metric. The App. 5 eq. A5.1–A5.2 caption says "d(x,y) is Manhattan distance from the occupied cell". The kernel uses half the Manhattan distance, `(|dx| + |dy|) / 2` (L240), so the reduction at a given cell is twice what the caption's formula gives. The window is a square. Which is intended?
  - Asked whether to fix the caption or the code. Itay, 2026-10-13: Follow the code.
  - For the write-up: the App. 5 eq. A5.1–A5.2 caption should say half the Manhattan distance.
- Radius. Ch. 5 Fig. 5.4 gives the household reduction a "~5 km radius" (20 cells). The code uses the territory radius, 20, 25 or 30 cells (L651).
  - Asked whether the write-up should say "across the territory (20–30 cells)". Itay, 2026-10-13: Yes, should be across the territory.
  - The code matches. For the write-up: Ch. 5 Fig. 5.4 caption ("~5 km radius") and App. 5 Table A5.2 (no household radius) should give the territory radius, 20–30 cells.
- The degradation window for the main camp equals the territory radius, so it is larger on poor ground. Ch. 5 §5.3.1 says the reduction extends "across the household's territory", which matches. App. 5 Table A5.2 gives no radius for households.
- The household's own family camps are drawn from its personalised copy taken before its own degradation ([memory and territorial attachment](memory-and-territorial-attachment.md)), so the coordination effect works between households but not among one household's family camps.
  - Settled on [memory and territorial attachment](memory-and-territorial-attachment.md) (Itay, 2026-10-13): later family camps should see the degradation earlier ones caused; for the separate PR (item 14).
  - Noted 2026-10-13: the main camp degrades its surroundings only after all nine family camps are placed (family loop L645–649, main camp L651; Year 0: L997–1002). Even after that fix, family camps would not see their own main camp's degradation.
  - Asked whether the main camp's degradation should come before the family camps are drawn. Itay, 2026-10-13: No, it should come after, as it simulates the activity of the main camp and its centrality within the camps.
  - The code matches.
  - Done in PR 8 (item 14, `df4776c`): each family draw reads the current shared surface, with this year's earlier degradation, on the territory's cells (`place_members`, L386–388). The main camp still degrades its surroundings after the nine family camps (L687–693).
