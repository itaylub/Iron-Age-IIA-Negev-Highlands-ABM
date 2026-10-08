# Log

Append-only record of operations on this wiki. Format: `## [YYYY-MM-DD] operation | subject | mode | agent`, then bullets listing created and updated pages.

## [2026-10-08] setup | Nomad ABM wiki | — | Claude (research-wiki)
- created: AGENTS.md (Profile from setup interview; local conventions: wiki inside the repo, thesis Ch. 5 / App. 5 as owner's documentation, code locators, rationale-question focus), CLAUDE.md, GEMINI.md, index.md, log.md, references.bib, _guide/ (5 guides), _tools/ (wiki_status.py, verify_quotes.py)
- created: questions/palimpsest-sufficiency.md (research question copied verbatim from Ch. 5 §5.1)
- interview: location wiki/ at repo root; aims = write the ODD / journal paper, reuse mechanisms elsewhere; thesis docs = owner's model documentation; rationale interview after the build; other answers defaults

## [2026-10-08] code | Code/ at 2249331 | read-only | Claude (research-wiki)
- read: Code/model.py, Code/sensitivity_model.py (diffed against model.py), 3 notebooks, README, CHANGELOG, CITATION.cff, docs/DATA.md, docs/objective_function.md, script headers, thesis Ch. 5 and App. 5 (text; figures not read). Nothing was run.
- created: model/overview.md, model/inventory.md, model/parameters.md, model/assumptions.md, model/experiments.md, model/odd-map.md, model/literature-cited.md
- created: mechanisms/ suitability-surface, occupation-history-layers, memory-and-territorial-attachment, camp-and-territory-placement, within-year-degradation, herd-dynamics, household-economy, enclosure-construction, crisis-and-replacement, site-classification, calibration-objective
- updated: index.md
- readings: 0 written, 12 owed (Purpose + 11 mechanism rationales)
- to check (highest stakes): yearly array 0 used both as annual rainfall (suitability) and as pasture (herds); stress_ras direction in herd growth; overlap rule cannot fire in model.py; home-range bonus may never apply if Mesa resets pos; bonuses accumulate across family placements; Optuna n_jobs threads share the global RNG; fixed-territory mode may add households on failure; docs/objective_function.md describes a different objective
- not verified: Mesa remove_agent behaviour (PyPI and GitHub raw blocked from this session)
