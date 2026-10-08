---
type: mechanism
created: 2026-10-08
code: "model.py › Household_Agent.handle_survival_crisis, L816–838; convert_livestock_to_surplus, L708–721; step, L589–593; NomadModel.create_replacement_agent, L1049–1058; move_year, L1039–1042"
odd: "Submodels; Design concepts › adaptation"
---

# Crisis and replacement

## What it does
- **Crisis** when surplus < 10 after the enclosure decision (L589–590). The household sells livestock at 0.3 surplus per head to close the gap to 10, keeping a reserve of `min(18 × manpower, 100)` head (L825–826, L708–721).
- **Failure** if afterwards surplus < 0, herd < 15 or manpower ≤ 0 (L828). The household's manpower (at least 1), surplus and herd are queued in `model.scheduled_new_agents`, and the household is removed (`self.remove()`, L592).
- **Replacement** at the next `move_year`, before placement. A new household gets the queued manpower and surplus, and the queued herd plus Σ₁₀ ⌊N(90, 15)⌋, about 900 head (L1039–1042, L1049–1058). It then places like any other household in `year_initiation`.
- The first branch of `handle_survival_crisis` (L817–823) applies only when surplus ≥ 10, which the caller never passes.

## Where it lives
`model.py`, as listed in the frontmatter. In `sensitivity_model.py`, fixed-territory mode resets the household in place instead of removing it (L491–496), and replacements are initialised at once (L966–989).

## Inputs and parameters
App. 5 Table A5.4 (all "Assumed"): crisis threshold 10; conversion 1 head → 0.3 surplus; minimum reserve "18 animals / person, capped at 100"; extinction surplus < 0 and livestock < 15. Ch. 5 §5.3.4: replacement herd "about 900 goats".

## What it changes
The household set (removal, creation), `flock_head`, `surplus`.

## Assumption it encodes
Ch. 5 §5.3.4: the herd is "the household's only liquid asset in the model", and distressed sales return less (0.3) than orderly culling (0.35), "reflecting a sale under pressure". A failed household's remnants seed a new one, "representing in a very simplified way the remnants of an expired household seeding a new one". Replacement is one-for-one "in keeping with the model's constant-population assumption" (Ch. 5 §5.3.4; §5.1).

## Justification
Owner's documentation: Ch. 5 §5.3.4 and §5.1 (constant population). The crisis floor is called "an tentative floor" in Ch. 5 §5.3.4. All values are "Assumed" (App. 5 Table A5.4).

## My rationale
**My rationale** · owed
> Q: A failed household is replaced one-for-one by a new one that inherits its remnants plus about 900 goats (create_replacement_agent, L1049–1058). Whom does the replacement household represent?

## Things to check
- Reserve. Ch. 5 §5.3.4 says selling "is limited by a minimum reserve of 18 animals per person, so a household does not fall below its subsistence needs". The code caps the reserve at 100 head (L712), as App. 5 Table A5.4 says, so for 6 or more people it is 100, well below 18 per person.
- Manpower at failure. The test `manpower <= 0` (L828) runs while manpower is reduced by 10 + herd//75 (L547–549), so a household with many animals relative to its people can fail on manpower. The replacement inherits that reduced manpower (L830, L1055) and does not recompute it from its new herd. Is that intended?
- Surplus < 0 cannot occur at that point, since `calc_surplus` floors it at 0 (L706) and the sale only adds. In practice failure comes from herd < 15 or manpower ≤ 0.
- Fixed-territory mode in `sensitivity_model.py`. When a household fails, `handle_survival_crisis` has already queued a replacement (the same code as `model.py` L834–836), and the fixed branch then resets the household instead of removing it (L491–496). Does each failure add a household in that mode? The reset also re-runs `year_initiation` in the middle of the step (L496).
- Replacements in `sensitivity_model.py` run `year_initiation` inside `create_replacement_agent` (L988) and again in the `shuffle_do("year_initiation")` that follows (L960). Does a new household camp twice in its first year?
- The "about 900" head is added on top of whatever herd the failed household had left, which may be under 15 (Ch. 5 §5.3.4 describes this as "on top of the inherited remainder").
