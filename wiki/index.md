# Index: Nomad ABM wiki

## Sources
(none ingested yet; candidates in [literature cited](model/literature-cited.md))
## Concepts
## Questions
- [Can autochthonous nomadic processes generate the Iron Age IIA pattern?](questions/palimpsest-sufficiency.md): the model's research question, Ch. 5 §5.1
## Notes
## Model
- [Overview](model/overview.md): purpose, entities, scales, schedule, initialisation · Purpose reading owed
- [Inventory](model/inventory.md): files, notebooks, docs, data, outputs; how `model.py` and `sensitivity_model.py` differ
- [Parameters](model/parameters.md): every value in the code against App. 5 Table A5.4; calibrated weights
- [Assumptions register](model/assumptions.md): 34 assumptions with where encoded and justification status
- [Experiments](model/experiments.md): calibration, best-trial replication, four sensitivity tests, smoke test
- [ODD map](model/odd-map.md): ODD elements → wiki pages and gaps
- [Literature cited](model/literature-cited.md): works Ch. 5 / App. 5 cite per component; none ingested
## Mechanisms
- [Suitability surface](mechanisms/suitability-surface.md): seven weighted 0–10 layers, slope cut, mask · rationale owed
- [Occupation history layers](mechanisms/occupation-history-layers.md): reuse potential (×5) and resource exhaustion (fuzzy, 0.5 decay) · rationale owed
- [Memory and territorial attachment](mechanisms/memory-and-territorial-attachment.md): home-range centre, territory bonus, camp memory · rationale owed
- [Camp and territory placement](mechanisms/camp-and-territory-placement.md): suitability³ draw, territory 20/25/30, family camps, overlap rule · rationale owed
- [Within-year degradation](mechanisms/within-year-degradation.md): D/distance kernel, floor 0.0001 · rationale owed
- [Herd dynamics](mechanisms/herd-dynamics.md): capacity 1.125 goats/cell, growth and decline · rationale owed
- [Household economy](mechanisms/household-economy.md): subsistence 18/person, surplus, consumption, manpower · rationale owed
- [Enclosure construction](mechanisms/enclosure-construction.md): prosperity index, reuse vs new build · rationale owed
- [Crisis and replacement](mechanisms/crisis-and-replacement.md): distress sales, failure, one-for-one replacement · rationale owed
- [Site classification](mechanisms/site-classification.md): 0.6 threshold, enclosure sites · rationale owed
- [Calibration objective](mechanisms/calibration-objective.md): ellipse IoU + site-type ratio, Optuna · rationale owed
## Syntheses
