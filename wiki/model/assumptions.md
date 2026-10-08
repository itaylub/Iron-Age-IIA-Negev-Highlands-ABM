---
type: model
created: 2026-10-08
---

# Assumptions register

Each assumption the model encodes, where it is encoded, and what justifies it so far. This is the list the ODD and the methods section will need.

Status:
- **sourced**: the owner's documentation cites literature for it. The literature is not yet ingested in this wiki.
- **owner's rationale**: Ch. 5 or App. 5 gives reasoning without a citation.
- **none recorded**: only "Assumed" in App. 5 Table A5.4, or not documented at all (the guide's "unjustified").

The `My rationale` blocks on the mechanism pages will move items from "none recorded" to "owner's rationale" as they are answered.

## Conceptual assumptions (Ch. 5 §5.1)
| # | Assumption | Encoded in | Status |
|---|---|---|---|
| C1 | Nomadic groups characterised the Negev Highlands population and produced the observed pattern | whole model | owner's rationale (Ch. 5 §5.1, from Ch. 3) |
| C2 | Part of the population moved seasonally between the Arabah and the Highlands; one move per year | annual `move_year` / `year_initiation` | owner's rationale (Ch. 5 §5.1, §5.2.3) |
| C3 | Multi-resource nomadism: pastoralism, copper and desert trade, opportunistic agriculture | 18 goats/person, agricultural offset | sourced (Ch. 5 §5.2.2: Dahl & Hjort 1976; Rosen & Finkelstein 1992) |
| C4 | Stone-built structures represent seasonal, not permanent, occupation | site classification | owner's rationale (Ch. 5 §5.1) |
| C5 | Tell el-Qudeirat was the central site and main destination from the Arabah | `dist_to_kb` layer | sourced (Ch. 5 §5.1: Ch. 3; Ben-Dor Evian 2017) |
| C6 | Population constant | `Num_agents`, one-for-one replacement | owner's rationale (Ch. 5 §5.1, §5.2.4) |
| C7 | Climate similar to the present; modern rainfall years drawn at random | yearly stack, shuffled `inds` (L1254–1255) | sourced (Ch. 5 §5.1: Goldsmith et al. 2023; Langgut & Finkelstein 2023) |
| C8 | The system lasted at least 75 years | run length | sourced (Ch. 5 §5.2.3: Boaretto et al. 2010; Finkelstein & Piasetzky 2011) |
| C9 | The household (about ten nuclear families) is the decision unit | `Household_Agent` | sourced (Ch. 5 §5.2.2: Khazanov 1984; Salzman 2004; Hammer 2025) |
| C10 | Enclosed compounds are communal, built from surplus by local decision | [enclosure construction](../mechanisms/enclosure-construction.md) | owner's rationale (Ch. 5 §5.1, §5.3.3) |

## Mechanism assumptions
| # | Assumption | Encoded in | Status |
|---|---|---|---|
| M1 | Households read one weighted, additive suitability score | `get_suitability_raster` L501–506 | owner's rationale (Ch. 5 §5.2.1.2) |
| M2 | Very steep cells (slope suitability < 1) are unusable | L505 | none recorded (threshold) |
| M3 | Camp choice is probabilistic, ∝ suitability³ | `place_household` L336 | owner's rationale (Ch. 5 §5.3.1); exponent: none recorded |
| M4 | Spatial inertia: home-range centre and territory bonus | L917–937 | sourced (Ch. 5 §5.3.1: Avni 1996; Galilee 2013; Hammer 2014; Meraiot et al. 2021); values none recorded |
| M5 | Camp memory: good camps attract, poor ones repel, fading as 1/√years; pruned after ~15 years | L938–949, L620 | owner's rationale (Ch. 5 §5.3.1); values none recorded |
| M6 | Territories widen on poor ground (20/25/30) | L631–641 | owner's rationale (Ch. 5 §5.3.1); values none recorded |
| M7 | Territories should not overlap by more than 25% | `overlap_territory` | none recorded ("cooperative coexistence"); see camp page on whether it fires |
| M8 | Occupation degrades its surroundings at once, decaying with distance | `env_degrade` | sourced in general (Ch. 5 §5.3.1: Boles et al. 2019; Meroz et al. 2023); magnitudes none recorded |
| M9 | Degradation persists with half-life of one year, spread over ~5 km | `Yi_params` | owner's rationale (Ch. 5 §5.3.1); values none recorded |
| M10 | Past occupation raises reuse potential (built infrastructure) | `Yi_params` L465 | owner's rationale (Ch. 5 §5.2.1.2); ×5 none recorded |
| M11 | Herd capacity 1.125 goats per 250 m cell at medium pasture | `update_flock_size`, `calc_surplus` | sourced (Seligman et al. 1962 via Rosen & Finkelstein 1992; Ch. 5 §5.2.4) |
| M12 | Herd growth up to ~20%/yr, decline 10–30%, faster for small herds | `update_flock_size` | "Literature-based" (A5.4), no source named |
| M13 | 18 goats/person subsistence (half of pastoral-only 37) | `calc_surplus` L664 | sourced (Dahl & Hjort 1976; Rosen & Finkelstein 1992) plus owner's rationale for halving |
| M14 | Cultivation offsets up to 40% of livestock need | L663 | sourced (Rosen & Finkelstein 1992; Günther et al. 2021) |
| M15 | Surplus is abstract wealth: 30% yearly loss, 1.2/person consumption, progressive decay above 100, cap 200 + 2.5M | `calc_surplus`, `step` | owner's rationale (Ch. 5 §5.3.2); values none recorded |
| M16 | Enclosures need prosperity (surplus per worker × local suitability) > 0.6, or > 0.8 to build new | `step` L552–587 | owner's rationale (Ch. 5 §5.3.3: "plausible working values"); values none recorded |
| M17 | Households prefer reusing their own enclosures, then others' | `find_recent_enclosure`, `build_enclosure` | owner's rationale (Ch. 5 §5.3.3); values none recorded |
| M18 | Crisis at surplus < 10; distress sale at 0.3 per head | `handle_survival_crisis` | owner's rationale (Ch. 5 §5.3.4); values none recorded |
| M19 | Failed households are replaced by one seeded with their remnants plus ~900 goats | `create_replacement_agent` | owner's rationale (Ch. 5 §5.3.4) |
| M20 | Manpower: 10 people and one herder per 75 head are set aside each step; random drift | `step` L547–549, L600–605 | none recorded |

## Observation assumptions
| # | Assumption | Encoded in | Status |
|---|---|---|---|
| O1 | A cell is a site once its summed signal reaches 0.6 (camp 0.5, family 0.25) | `to_gdf` | owner's rationale (Ch. 5 §5.5.3, face validation) |
| O2 | Any enclosure event makes an enclosed-compound site | `to_gdf` L1136–1139 | owner's rationale (Ch. 5 §5.5.3) |
| O3 | Spatial similarity is judged by 2-SD ellipse IoU, not point locations | `obj_func` | sourced (Ch. 5 §5.5.1–5.5.2: Grimm et al. 2005; Gallagher et al. 2021; Yuill 1971) |
| O4 | The survey record is representative despite preservation and coverage | calibration targets | owner's rationale (Ch. 5 §5.5.3) |
