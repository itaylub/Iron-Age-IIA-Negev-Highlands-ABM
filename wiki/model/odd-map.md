---
type: model
created: 2026-10-08
---

# ODD map

ODD elements after Grimm et al. (2020), the protocol the README names for the journal version. For each element: where the material is in this wiki and in the owner's documentation, and what is missing. "Gap" means something the ODD needs that neither the code nor Ch. 5 / App. 5 supplies yet, or where they disagree.

| ODD element | Wiki pages | Owner's documentation | Gaps |
|---|---|---|---|
| **1. Purpose and patterns** | [overview › Purpose](overview.md#purpose), [question](../questions/palimpsest-sufficiency.md), [calibration objective](../mechanisms/calibration-objective.md) | Ch. 5 §5.1, §5.5.1–5.5.3 | Purpose reading owed. Ratio vs proportion definition of the site-type pattern. |
| **2. Entities, state variables, scales** | [overview › Entities](overview.md#entities-and-state-variables), [overview › Scales](overview.md#scales) | Ch. 5 §5.2; App. 5 Tables A5.5–A5.6 | Crisis flag listed but absent in code. `stress_ras` meaning (10 = untouched). Grid orientation (DATA.md says 318 columns). |
| **3. Process overview and scheduling** | [overview › Process](overview.md#process-overview-and-scheduling) | Ch. 5 §5.2.3, §5.4; Figures 5.3, 5.6 (not read) | Two separate shuffled passes in the code vs one pass in §5.4; enclosure-before-herd order in §5.2.3. |
| **4. Design concepts** | see rows below | Ch. 5 §5.1, §5.3 | Not yet written as a design-concepts section anywhere. |
| › Basic principles | [question](../questions/palimpsest-sufficiency.md), [assumptions C1–C10](assumptions.md) | Ch. 5 §5.1 (palimpsest model, carrying capacity) | — |
| › Emergence | [site classification](../mechanisms/site-classification.md) | Ch. 5 §5.1, §5.2.3, §5.7 | — |
| › Adaptation | [camp placement](../mechanisms/camp-and-territory-placement.md), [enclosures](../mechanisms/enclosure-construction.md), [crisis](../mechanisms/crisis-and-replacement.md) | Ch. 5 §5.3 | — |
| › Objectives | [camp placement](../mechanisms/camp-and-territory-placement.md) (suitability³), [enclosures](../mechanisms/enclosure-construction.md) (prosperity) | Ch. 5 §5.3.1, §5.3.3 | Households have no explicit objective function; the ODD should say so. |
| › Learning | [memory and attachment](../mechanisms/memory-and-territorial-attachment.md) | Ch. 5 §5.3.1 | Whether the home-range bonus applies (Mesa `pos` reset). |
| › Prediction | — | — | None in the model (no forecasting by agents); state explicitly. |
| › Sensing | [suitability](../mechanisms/suitability-surface.md), [degradation](../mechanisms/within-year-degradation.md) | Ch. 5 §5.3.1 | Households sense the whole map (no sensing radius for camp choice). Local radii: 20 (prosperity, territory size), 25/30 (pasture). |
| › Interaction | [degradation](../mechanisms/within-year-degradation.md), [history layers](../mechanisms/occupation-history-layers.md), [enclosures](../mechanisms/enclosure-construction.md) | Ch. 5 §5.3.1 ("modelled implicitly") | Overlap rule inactive in `model.py`. |
| › Stochasticity | all mechanism pages | Ch. 5 §5.1 | List of random draws (rain-year order, camp draws, herd noise, manpower drift, memory pruning, enclosure choice, initial herds). Thread-shared RNG in calibration. |
| › Collectives | [enclosures](../mechanisms/enclosure-construction.md) | Ch. 5 §5.1 (households of ~10 families) | Families are not agents; say so. |
| › Observation | [site classification](../mechanisms/site-classification.md), [calibration objective](../mechanisms/calibration-objective.md), [inventory › Outputs](inventory.md#outputs-not-in-git) | Ch. 5 §5.5.3 | — |
| **5. Initialisation** | [overview › Initialisation](overview.md#initialisation), [parameters](parameters.md#population-and-initialisation) | Ch. 5 §5.2.4 | Year-0 territory radius 25 vs 20/25/30. |
| **6. Input data** | [suitability](../mechanisms/suitability-surface.md), [inventory › Input data](inventory.md) | Ch. 5 §5.2.1; App. 5 Table A5.1; docs/DATA.md | Which yearly array is rainfall vs pasture. The `ext_raster` definition. Corridor vs point for the Tell el-Qudeirat layer. |
| **7. Submodels** | the eleven [mechanism pages](overview.md#mechanisms), [parameters](parameters.md) | Ch. 5 §5.3; App. 5 §A5.2, Table A5.4 | Code–documentation differences listed under each mechanism's Things to check. Owed rationales. |

## Beyond the ODD core
- Calibration and sensitivity analysis: [experiments](experiments.md), [calibration objective](../mechanisms/calibration-objective.md).
- Software and data availability: Zenodo DOIs in [overview](overview.md) frontmatter.
