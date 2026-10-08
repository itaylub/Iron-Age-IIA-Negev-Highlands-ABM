---
type: mechanism
created: 2026-10-08
code: "model.py › Household_Agent.calc_surplus, L654–706; Household_Agent.step, L544–616; buy_livestock_with_surplus, L723–733"
odd: "Submodels"
---

# Household economy: subsistence, surplus, manpower

## What it does
**Surplus** (`calc_surplus`, run right after [herd dynamics](herd-dynamics.md)):
- Agricultural offset `a = min(0.4, 0.04 × mean ag_ras over territory)`. Need = `M × 18 × (1 − a)` (L657–665).
- Capacity over a radius-25 neighbourhood (`n × 1.125 × PV/5`) and stress ratio `s = max(0, 1 − capacity/herd)` (L667–675).
- Working herd = `Need × 1.5 × (1 + 0.3 s)` (L677–679).
- Products: `0.15 × productive_herd`, where `productive_herd = max(0, H − Need × non_cull_fraction)` and `non_cull_fraction = max(0, (H − working herd)/H)` (L680–687).
- Culling: 80% of the excess above the working herd is culled, at 0.35 surplus per head, and removed from the herd (L689–694).
- Balance: `0.7 × previous + products + culling − (1.2 × M + 0.05 × (0.7 × previous + products + culling))`, floored at 0 and capped at `200 + 2.5 × M` (L696–706).

**Later in `step`:**
- Livestock purchase if surplus > 80 and herd < 600: spend `min(0.2 × surplus, 40)` at 0.3 surplus per head (L594–596, L723–733).
- Extra surplus decay at the end of the step: if surplus > 100, a rate of `min(0.25, 0.05 + 0.001 × (surplus − 100))`; otherwise 1% (L607–616).
- `set_camp` charges 1 surplus per year (L279).

**Manpower within the step** (L547–549, L598–605):
- At the start, `manpower −= 10` and `manpower −= herd // 75` ("herders").
- After enclosure and crisis handling it is restored: `max(1, M + 10) + herders`.
- Random drift: +⌈5U⌉ with probability 0.3; −⌈5U⌉ with probability 0.2 if M > 55; +1 with probability 0.3 if surplus > 100.

## Where it lives
`model.py › Household_Agent.calc_surplus`, L654–706; `Household_Agent.step`, L544–616; `buy_livestock_with_surplus`, L723–733. Initial manpower `max(35, ⌊herd/20⌋)` (L526–527); initial surplus 0.

## Inputs and parameters
Documented in App. 5 Table A5.4 and Ch. 5 §5.3.2: 18 goats/person ("Modified from Rosen & Finkelstein (1992)"); agricultural offset up to 40% (Rosen & Finkelstein 1992; Günther et al. 2021); 1.2 consumption per person (Assumed); 30% annual surplus decay (Assumed); progressive decay 5–25% above 100 (Assumed); acquisition when surplus > 80 and herd < 600, up to 20% (maximum 40) at 0.3 (Assumed). Ch. 5 §5.3.2 gives buffer 1.5, products 0.15 and culling 0.8 × 0.35.

Not in Ch. 5 or App. 5: the 5% `luxury_consumption` (L701), the 1% decay below 100 (L614–616), the −1 surplus per camp (L279), the −10 and herd//75 manpower deductions, and the random manpower drift.

## What it changes
`surplus`, `flock_head` (culling, purchase) and `manpower`.

## Assumption it encodes
Ch. 5 §5.3.2: surplus is "stored wealth … held as an abstract quantity rather than in any one commodity". The 18 goats per person is about half the pastoral-only 37, "based on the assumption that a group leaning partly on trade and farming needed fewer animals per head to subsist" (Ch. 5 §5.2.2). Losses represent "spoilage and sharing", and large holdings decay faster because of "the difficulty of storing and the social pressure to redistribute" (Ch. 5 §5.3.2).

## Justification
- Owner's documentation: Ch. 5 §5.2.2, §5.2.4, §5.3.2. Sources cited: Dahl & Hjort 1976 and Rosen & Finkelstein 1992 (37 goats per person under pure pastoralism); Rosen & Finkelstein 1992 and Günther et al. 2021 (agricultural offset); Bruins 2012 and Garty et al. 2025 (runoff farming, for the cultivable-patch layer).
- App. 5 Table A5.4 marks consumption, decay, acquisition and the 0.15 yield ("adopted for simplicity", Ch. 5 §5.3.2) as assumed.

## My rationale
**My rationale** · owed
> Q: Each household eats 1.2 surplus units per person a year and loses 30% of its stored surplus (calc_surplus, L696–704). What do 'surplus units' correspond to in the Iron Age IIA economy?

## Things to check
- Productive herd. Ch. 5 §5.3.2 defines H_productive as "the milk- and wool-yielding part of the herd (those beyond the subsistence core)". The code subtracts `Need × non_cull_fraction` (L681–685). When the herd is at or below the working herd, `non_cull_fraction` = 0 and the whole herd counts as productive. Which is intended?
- Stress cost. Ch. 5 §5.3.2 and the code use `1 + 0.3 s` (L678). App. 5 Table A5.4 lists the stress maintenance cost as 15% × stress ratio.
- Consumption. Ch. 5 §5.3.2 writes Consumption = 1.2 × M. The code adds 5% of the year's available surplus as `luxury_consumption` (L701–702).
- Decay happens twice a year: 30% at the start of `calc_surplus` (L696–697) and 1–25% at the end of `step` (L607–616). Ch. 5 §5.3.2 describes both ("drawn down by consumption and by loss … above 100 units a household loses an additional 5–25%"). The 1% below 100 is not described.
- Manpower deductions. `step` subtracts 10 and one herder per 75 animals before the enclosure tests and the failure test, and adds them back afterwards (L547–549, L598–599). The 10 and the 75 are not documented. What do they stand for?
- Manpower drift. The random gains and losses (L600–605) push manpower upward on average until 55, which affects the manpower thresholds for enclosure building. They are not described in Ch. 5 or App. 5.
