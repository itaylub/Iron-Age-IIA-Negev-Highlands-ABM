# Comparison: Thesis Text (Chapter 4) vs. Model Code (model_code_26.ipynb)

This document details the discrepancies between the model description in Chapter 4 of the thesis and the actual Python implementation provided in `model_code_26.ipynb`.

## 1. Agent Initialization and Demographics (Sections 4.2.2 & 4.5.1)

| Feature | Text Description | Code Implementation |
| :--- | :--- | :--- |
| **Manpower Calculation** | Calculated as $manpower = \max(\sqrt{\frac{livestock}{18}}, 5)$. | Calculated as `max(35, np.floor(self.flock_head / 20))`. The code enforces a significantly higher minimum (35 vs 5) and uses a linear divisor (20) instead of a square root. |
| **Livestock per Person** | States **18** livestock units per person. | The `Household_Agent` initialization implies **20** livestock per person (`flock_head / 20`). |
| **Initial Surplus** | Households begin with zero surplus. | Matches (defaults to 0), though code allows inheritance if initialized via `create_replacement_agent`. |

## 2. Resource Management (Section 4.3.2)

| Feature | Text Description | Code Implementation |
| :--- | :--- | :--- |
| **Consumption Rates** | Baseline is **0.8** surplus units per person + 30% communal costs. | `consumption_per_person` is set to **1.2**. |
| **Stochastic Events** | Describes annual scenarios: Adverse (25%), Neutral (50%), Favourable (25%) affecting costs/herds. | **Absent**. `calc_surplus` is deterministic based on manpower and a small luxury factor (5%). |
| **Surplus Decay** | Large surpluses (>50 units) decay up to **40%**. | Threshold is **>100** units. Decay rate is capped at **25%** (`min(0.25, ...)`). |
| **Herd Growth** | Herds grow up to **10%** annually. | `max_growth_rate` is set to **0.2** (20%). |

## 3. Prosperity and Enclosures (Section 4.3.3)

| Feature | Text Description | Code Implementation |
| :--- | :--- | :--- |
| **Prosperity Formula** | $P = \frac{surplus + manpower + \text{env quality}}{3}$ | `prosperity_index = (self.surplus / (denominator * 2)) * env_quality`. Uses a ratio of surplus to population scaled by environment. |
| **Eligibility Threshold** | Index > **0.7**. | Index > **0.6** (`is_prosperous`). |
| **New Construction** | Requires Manpower ≥ **40**. | Requires Manpower ≥ **30**. |

## 4. Crisis Response (Section 4.3.5)

| Feature | Text Description | Code Implementation |
| :--- | :--- | :--- |
| **Culling Hierarchy** | Detailed biological hierarchy (juvenile males first, then adult males, etc.) with specific values. | **Simplified**. `convert_livestock_to_surplus` uses a flat `conversion_rate = 0.3` without age/sex distinction. |
| **Territorial Contraction** | Crisis households contract territory to a **15-cell radius**. | **Missing**. `handle_survival_crisis` does not alter the `territory` attribute. |

## 5. Environmental Feedbacks (Section 4.4)

| Feature | Text Description | Code Implementation |
| :--- | :--- | :--- |
| **Degradation Decay** | Uses a decay factor of **0.7** ($w(t) = 0.7^{(T-t)}$). | Uses a decay factor of **0.5** in `Yi_params` (`decay_factor = 0.5`), implying faster recovery. |
| **Memory Decay** | Decays hyperbolically as $\frac{1}{(T - t) + 1}$. | Decays based on square root: `time_factor = 1 / (diff_y**0.5)`. |

## 6. Spatial Logic (Section 4.2.1 & 4.2.3)

| Feature | Text Description | Code Implementation |
| :--- | :--- | :--- |
| **Suitability Integration** | "Proximity to arable soils and available pasture are excluded from the suitability calculation". | **Matches**. `get_suitability_raster` excludes pasture/ag weights from the summation. |
| **Annual Parameters** | Lists pasture/ag potential as annual parameters updating the map. | While updated in `move_year`, `veg_map` and `ag_ras` are **not** used in the weighted suitability sum (`get_suitability_raster`). Only `Yearly_rain` and `humen_stress` are used. |