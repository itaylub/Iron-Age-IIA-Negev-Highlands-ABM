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
**My rationale** · Itay, 2026-10-12
> Q: A failed household is replaced one-for-one by a new one that inherits its remnants plus about 900 goats (create_replacement_agent, L1049–1058). Whom does the replacement household represent?

It is thought to represent some kind of successor - in very abstract way.

## Things to check
- Reserve. Ch. 5 §5.3.4 says selling "is limited by a minimum reserve of 18 animals per person, so a household does not fall below its subsistence needs". The code caps the reserve at 100 head (L712), as App. 5 Table A5.4 says, so for 6 or more people it is 100, well below 18 per person.
  - Asked which reserve is intended. Itay, 2026-10-12: The 100 cap is in place, the idea is that 100 goats is big enough herd that the household 'can work with' and compensate somehow.
  - For the write-up: Ch. 5 §5.3.4 gives the reserve as 18 animals per person without the cap.
- Manpower at failure. The test `manpower <= 0` (L828) runs while manpower is reduced by 10 + herd//75 (L547–549), so a household with many animals relative to its people can fail on manpower. The replacement inherits that reduced manpower (L830, L1055) and does not recompute it from its new herd. Is that intended?
  - Asked whether the test and the replacement should use manpower before or after the set-aside. Itay, 2026-10-12: After it as if the household is below 0 manpower it means it lacks people to do needed chores. Tell me if it makes sense.
  - The test reads as described: after the set-aside, manpower is the people left for other chores, and ≤ 0 means there are too few. Open: the replacement starts from that post-set-aside figure, `max(1, manpower)` (L830), so after a manpower failure it has 1 person for about 900 goats. The end-of-step restoration, `max(1, manpower + 10) + herders` (L600–601), then holds it near herders + 1, so its free manpower stays below 0. It would fail at its first crisis and could not reuse or build enclosures (15 free needed). This is a reading of the code, not run. Should a replacement start with manpower as a new household does, `max(35, herd / 20)` (L526–527)?
- Surplus < 0 cannot occur at that point, since `calc_surplus` floors it at 0 (L706) and the sale only adds. In practice failure comes from herd < 15 or manpower ≤ 0.
  - Asked whether that is acceptable. Itay, 2026-10-12: Yes but it should be = or < 0.
  - For the separate PR: `surplus <= 0` (L828). Since surplus is floored at 0, this criterion can then trigger.
- Fixed-territory mode in `sensitivity_model.py`. When a household fails, `handle_survival_crisis` has already queued a replacement (the same code as `model.py` L834–836), and the fixed branch then resets the household instead of removing it (L491–496). Does each failure add a household in that mode? The reset also re-runs `year_initiation` in the middle of the step (L496).
  - Confirmed by reading (2026-10-12): `handle_survival_crisis` queues a replacement before returning False, and the fixed branch then keeps the household (L488–496), so each failure adds one household.
  - Asked whether fixed-territory runs should keep the population constant. Itay, 2026-10-12: Yes the population should be constant.
  - For the separate PR. The territory test (Ch. 5 §5.6; App. 5 §A5.7.4) ran with this; see [experiments](../model/experiments.md).
- Replacements in `sensitivity_model.py` run `year_initiation` inside `create_replacement_agent` (L988) and again in the `shuffle_do("year_initiation")` that follows (L960). Does a new household camp twice in its first year?
  - Asked whether `model.py`'s way (placed once, with everyone else) is intended for both files. Itay, 2026-10-12: It should be the same as all the others.
  - For the separate PR: drop the immediate placement in `sensitivity_model.py › create_replacement_agent` (L983–988).
- The "about 900" head is added on top of whatever herd the failed household had left, which may be under 15 (Ch. 5 §5.3.4 describes this as "on top of the inherited remainder").
- Deferred here from the inventory round (agreed 2026-10-12): differences 4 (failure handling) and 6 (replacement placement) between `model.py` and `sensitivity_model.py`. See [inventory](../model/inventory.md#how-the-two-model-files-differ).
- Deferred here from the camp-placement round (agreed 2026-10-12): whether Mesa's `Agent.remove()` (`model.py` L592) also takes a failed household off the grid; if not, it counts as an occupied cell in `eval_neighborhood` (L299–301). To test in the separate PR.
