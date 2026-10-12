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

## [2026-10-12] convention | canonical Ch. 5 / App. 5 versions | — | Claude (research-wiki)
- owner named the canonical documentation: Ch. 5 in `G:\My Drive\MA Thesis\context\thesis_reference\full_thesis.md` (Drive 2026-10-04); App. 5 = `G:\My Drive\MA Thesis\Thesis_submission\appendices\Appendix 5. ABM.docx` (Drive 2026-07-13, Word rev. 14). Both fetched through the Google Drive connector and compared with the repository copies in `thesis/`.
- App. 5: wording identical to `thesis/appendix-5-ABM.docx` (rev. 13); only caption punctuation (":" → ".") and the Table A5.2 caption formatting differ. Newly read: text-box captions that the earlier pandoc export skipped (Table A5.1 notes; eq. A5.1–A5.3 captions, which call d(x,y) "Manhattan distance"; Table A5.4–A5.7 and Fig. A5.1–A5.6 captions).
- Ch. 5: about 93% of words match `thesis/chapter-5-ABM.docx`. Substantive changes: §5.1 reframed (simulation gives "insights" into mechanisms rather than testing the palimpsest model directly; rules are "general, simplified, tentative behaviours"); assumptions revised (all stone-built structures incl. enclosed compounds seasonal; Tell el-Qudeirat as "central hub" and "primary fresh-water oasis"; multi-resourced nomadism after Rosen 2017; constant population by replacement); enclosed compounds now "communal kin-based, multi-purpose territorial centres" (seasonal storage, gatherings, perhaps exchange); the "communal places … rather than seats of authority" / "not from top-down planning" paragraph and its citations (Aharoni et al. 1960; Cohen & Cohen Amin 2004) removed; territory "~80 km²" note removed from §5.1; §5.5.1 sentence "the model is not built to predict individual site locations" removed; "tentative" → "user defined" values (§5.5.2); site-type ratio "relative to"; corridor "toward Faynan in the northern Arabah"; §5.7 retitled "Summary and Discussion"; figure captions 5.1–5.11 added; new citations Rosen 2017, Wachtel et al. 2018, Cortell-Nicolau et al. 2025. full_thesis.md has no equations (export).
- updated: AGENTS.md (Local conventions › canonical versions), model/overview.md (Purpose quote and framing, Fig. 5.3 / 5.6 schedule, crisis flag), model/inventory.md (Documentation, Things to check), model/assumptions.md (C3–C6, C10, new C11), model/parameters.md, model/experiments.md (Fig. 5.10–5.11; seed-173 check), model/odd-map.md, model/literature-cited.md, mechanisms/enclosure-construction.md, mechanisms/calibration-objective.md, mechanisms/within-year-degradation.md (Manhattan vs half-Manhattan; ~5 km radius), mechanisms/occupation-history-layers.md, mechanisms/suitability-surface.md (Table A5.1 notes), index.md
- quotes re-verified against the canonical texts: all match except two kept on purpose and labelled as from the older repository copy
- readings: unchanged, 0 written, 12 owed

## [2026-10-12] convention | thesis PDF as canonical documentation; answering in place | — | Claude (research-wiki)
- repository: `thesis/chapter-5-ABM.docx`, `thesis/chapter-5-tables-and-figures.docx`, `thesis/appendix-5-ABM.docx` replaced by `thesis/Lubel_Itay_MA_Thesis_ABM.pdf` (owner's choice, 67 pp.: Ch. 5 printed pp. 131–176, Table 5.1 p. 229, Appendices note and App. 5 pp. 235–254). README and CHANGELOG updated.
- compared the PDF with the working copies: Ch. 5 identical to full_thesis.md apart from layout, hyphenation and bullets, and the PDF carries the equations (C, B, territory bonus, w, A, Sₜ, Capacity, Need, Working herd, S_products, S_culling, Total surplus, Prosperity index, IoU, errors), all matching the forms used on the mechanism pages; App. 5 identical to `Appendix 5. ABM.docx`, plus an "Appendices" note on p. 235.
- updated: AGENTS.md (Local conventions: PDF canonical with page map; locators may add printed pages; working copies; new "Answering in place" convention for the owner's edits and how the next session integrates them), model/inventory.md, model/overview.md, model/parameters.md, model/assumptions.md, model/literature-cited.md, mechanisms/enclosure-construction.md, mechanisms/occupation-history-layers.md, questions/palimpsest-sufficiency.md
- quotes re-verified against the PDF text layer: all match except one kept on purpose (earlier-draft wording in assumptions C5) and table cells that the PDF interleaves
- readings: 0 written, 12 owed; the owner will answer in place and integrate in a new session

## [2026-10-12] readings | answers written in place (overview, inventory, suitability surface) | — | Claude (research-wiki)
- integrated Itay's in-place answers from commits `e00665f`, `dde1ba3` and `1d70181` (all dated 2026-10-12): 2 readings (overview › Purpose; suitability surface › My rationale) and 17 `Itay:` replies to Things to check (overview 4, inventory 7, suitability surface 6). `> A:` prefixes removed; replies moved onto their own signed lines under each item; only spelling and capitalisation fixed ("prefrences", "updtaed", "shoud", "generaly", "dont", "its, ok", lowercase "i" and sentence starts).
- checked against the code, git history and the thesis PDF: `in_severe_crisis` existed in `run_numpy.ipynb` until commit `8e7a865` (2025-12-10), where it cut the territory to radius 15 in crisis; App. 5 equation objects on p. 237 still read "eq 4.1 / 4.2 / 4.3 + 2" (rendered page); yearly array 0 feeds herd pasture and enclosure scoring in both model files.
- new Things to check where a reply leaves a conflict with the code or the thesis: one pass vs two passes (Ch. 5 §5.4); Year-0 rule absent from Ch. 5 §5.3.1 / Table A5.4 and different in `sensitivity_model.py`; 75 vs 76 rainfall groups; "drawing independently" (Ch. 5 §5.2.1.2) vs once-per-run draws; "validation" in §5.5 headings vs the Purpose reading; code vs Ch. 5 §5.5.2 on ratio vs proportion; `metadata` group required by the code; sensitivity-file differences not tied to switches; array 0 used as pasture; App. 5 tables still describing the point layer; A5.3 rainfall wording; `ext_raster` vs `place_raster`; Table A5.1 note "suitability 0.5"; which layers "base suitability" means for Q.
- updated: model/overview.md, model/inventory.md, mechanisms/suitability-surface.md (answers and checks); model/assumptions.md (C5, C7, M1, M6), model/odd-map.md (rows 1, 2, 3, 5, 6), model/parameters.md (Year-0 radius), model/experiments.md (time horizon), mechanisms/herd-dynamics.md, mechanisms/calibration-objective.md, index.md
- not done, needs the owner's go-ahead (outside the wiki): stale module names in `Code/` docstrings and calibration.ipynb; output paths for reproduction; rewriting docs/objective_function.md and docs/DATA.md; the array 0 / array 2 code fix; AGENTS.md equation-label convention
- readings: 2 written, 10 owed

## [2026-10-12] convention | answering in chat replaces answering in place | — | Claude (research-wiki)
- AGENTS.md › Local conventions: "Answering in place" replaced by "Answering in chat". Owed items are presented one file at a time with links, code items carry a snippet, a new round opened by an answer is resolved (or deferred by agreement) before moving on, and edits outside the wiki go to a later, separate PR.
- deferred to a separate PR (Itay, 2026-10-12): stale module names in `Code/` docstrings and calibration.ipynb; output paths for reproduction; docs/objective_function.md and docs/DATA.md (now also the 76 → 75 yearly groups); pasture from yearly array 2 instead of array 0 in both model files.

## [2026-10-12] readings | model/overview.md (chat round) | — | Claude (research-wiki)
- answers recorded: italics in the Purpose reading are emphasis, not a quote; Year-0 radius 25 confirmed; ODD follows the code's two passes; "simulated data" = processed IMS years plus derived pasture and agriculture; "validation" kept in its technical sense; essence of the rainfall-draw wording.
- checked: `yearly_data_10_25.h5` and `per_data_10_25.h5` from the repository history (commit `14cb755^`, SHA-256 equal to docs/DATA.md), read with the HDF5 C library: 75 year groups plus `metadata` (`num_groups` = 75); DATA.md's 76 counts `metadata`. Zenodo is blocked from this session.
- updated: model/overview.md, model/inventory.md (input data, metadata check), model/odd-map.md (rows 1, 3, 5), model/assumptions.md (C7), model/experiments.md (time horizon; new check on the rainfall replay)
- open in this round: journal wording for the rainfall draw (proposal awaiting approval); deferral of the 150-year rainfall replay to the experiments round (proposed)

## [2026-10-12] readings | model/overview.md round closed; conventions folder | — | Claude (research-wiki)
- approved: journal wording for the rainfall draw (approved Claude draft, recorded on overview Things to check; carried to assumptions C7 and the ODD map).
- deferred by agreement: the 150-year rainfall replay, to the experiments round (model/experiments.md, Things to check).
- AGENTS.md › Local conventions: Itay's `ABMA_Skill` folder (on Itay's computer) named as the reference to confer with when a convention is needed; not reachable from cloud sessions.

## [2026-10-12] readings | model/inventory.md (chat round) | — | Claude (research-wiki)
- answers recorded: ratio vs proportion deferred to calibration objective; docs/DATA.md to be treated with suspicion; the sensitivity file's Year-0 rule is a mistake; the overlap rule never firing in `model.py` is a bug; differences 1, 4 and 6 deferred to the camp and crisis pages; App. 5 equations should be numbered A5.x; figure images need no comparison.
- checked: Year-0 territory radius under the sensitivity file's rule, with the calibration data and best-trial weights (numpy rebuild of the year-0 surface): first camp gets radius 20 ≈ 52%, 25 ≈ 43%, 30 ≈ 6%.
- AGENTS.md › Local conventions: equation numbering A5.x confirmed; docs/objective_function.md outdated, docs/DATA.md to be treated with suspicion.
- updated: model/inventory.md, model/assumptions.md (M7), model/odd-map.md (interaction), model/experiments.md, mechanisms/camp-and-territory-placement.md, mechanisms/crisis-and-replacement.md, mechanisms/calibration-objective.md, AGENTS.md
- added to the separate-PR list: align `sensitivity_model.py`'s Year-0 territory with `model.py`; the overlap-rule bug in `model.py` (fix to be decided, it changes calibrated behaviour). Thesis text (owner's PDF, not the repository): renumber the App. 5 equation objects to A5.1–A5.3.
- open in this round: deferral of the Year-0 effect on §5.6 to the experiments round (proposed)

## [2026-10-12] readings | inventory round closed; conventions reference; suitability data checks | — | Claude (research-wiki)
- deferred by agreement: the effect of the sensitivity file's Year-0 rule on §5.6, to the experiments round.
- AGENTS.md › Local conventions: the conventions reference is the `ABMA_Skill` folder on Google Drive (`G:\My Drive\skills\ABMA_Skill`), a reference distilled from Romanowska, Wren & Crabtree 2021, readable through the Drive connector; never cited as evidence.
- checked in the calibration data (numpy, HDF5 C library): yearly array 2 ≈ veg_fit × array 0 / 10; group 74's array 2 has no-data cells (359 inside ext); the Tell el-Qudeirat layer's top zone is an east–west strip ~59 × 14 km; place_raster (2,347 km²) sits inside ext_raster (3,251 km²) with a 905 km² band between them.
- updated: mechanisms/suitability-surface.md (checks), model/inventory.md, model/experiments.md, AGENTS.md
- added to the separate-PR list: if pasture switches to array 2, handle group 74's no-data cells.

## [2026-10-12] readings | mechanisms/suitability-surface.md (chat round) | — | Claude (research-wiki)
- answers recorded: pasture array fix goes in the separate PR ("a big red flag"); the A5.3 sentence is a preliminary observation and can go; `ext_raster` is the Negev Highlands outline, `place_raster` the valid placement, the band between them the buffer (earlier reply marked superseded); "base suitability" = the shared surface, without each household's perception; the slope cut at ≤ 1 marks uninhabitable slopes such as cliffs (≈ 31° by Table A5.1's parameters, calculated); addition chosen as the simplest form (KISS), with all layers on one 0–10 scale.
- AGENTS.md: GitHub organisation ABMArchaeologists added to the conventions reference.
- updated: mechanisms/suitability-surface.md, mechanisms/herd-dynamics.md, mechanisms/enclosure-construction.md (range of Q), model/assumptions.md (M1, M2, M11), model/odd-map.md, model/overview.md (environment), model/experiments.md (pasture input in every run), AGENTS.md
- open in this round: what excludes the eastern part of the mask band (map shared); deferral of Q's range to the enclosure round (proposed)

## [2026-10-12] readings | suitability round closed (model extent) | — | Claude (research-wiki)
- answers recorded: the eastern part of the mask band is lowland, not Negev Highlands; the range of Q deferred to the enclosure round; the household count keeps the 3,251.54 km² `ext_raster` area (buffer included), halved for a minimal population.
- new for the write-up: Table A5.4 and Ch. 5 §5.2.4 describe the 3,251.54 km² as bounded by the Negev Highlands and the border, while it also holds the buffer.
- AGENTS.md: the conventions reference now names <https://github.com/SantaFeInstitute/ABMA> (replacing the organisation link).
- updated: mechanisms/suitability-surface.md, mechanisms/enclosure-construction.md, model/overview.md, model/parameters.md, model/odd-map.md, AGENTS.md

## [2026-10-12] readings | mechanisms/calibration-objective.md (chat round) | — | Claude (research-wiki)
- reading written: My rationale (the site-type error is a ratio, enclosed to other sites).
- answers recorded: GPU leftover goes in the separate PR; the 200 trials were run in small batches; App. 5 should read 1:13.4; the fewer-than-three-sites score is a guardrail that does not occur in full runs; the trials "did not" run with n_jobs above 1.
- checked through the Drive connector: `opt_2_26_v1.csv` and `optimization_summary.csv` (Itay's Optuna exports). 218 trials (143 complete, 57 pruned, 18 failed), 2026-02-17 to 2026-03-05, best trial 173. The timestamps show trials running concurrently (10, then 4 at a time), as App. 5 §A5.3 also states; this contradicts the n_jobs reply. Ch. 5 §5.6 reports a 56% enclosed share at thresholds 0.8–1.0, so the ratio error's 0–1 bound is not guaranteed.
- updated: mechanisms/calibration-objective.md, model/odd-map.md (row 1), model/experiments.md (calibration outputs; seed-173)
- added to the separate-PR list: remove the CUDA_VISIBLE_DEVICES assignment in `objective`. Thesis text: Ch. 5 §5.5.2 and App. 5 §A5.7.2 to describe the ratio; App. 5 §A5.7.3 to read 1:13.4.
- open in this round: how to handle concurrent trials sharing the global random generators; recording the ratio bound as conditional.

## [2026-10-12] readings | calibration objective: correction | — | Claude (research-wiki)
- correction to the previous entry: Itay's reply was misread. Itay confirms the trials ran in parallel and does not think they interfered; the timestamps agree with that reply rather than contradicting it. Recorded on the page as a clarification.
- answers recorded: (b) per-run generators under consideration for the separate PR; (c) already done in the validation; the ratio bound recorded as conditional (0–1 while other sites outnumber enclosed ones).
- proposed: test the no-interference reply by comparing trial 173's ten calibration replicates (seeds 17300–17309) with validation runs 0–9 (same seeds, run one after another); deferral to the experiments round proposed.

## [2026-10-12] readings | calibration objective round closed | — | Claude (research-wiki)
- correction: the validation (Ch. 5 §5.5.4) re-ran the best combination for 30 additional replicates to test robustness across seeds; it was wrongly described in chat as a re-run of trial 173's seeds. Page reworded.
- deferred by agreement: the no-interference check (trial 173's calibration seeds vs the validation runs), to the experiments round, with the open question of which seeds the validation used (cell 6 as it stands repeats 17300–17309).
- updated: mechanisms/calibration-objective.md, model/experiments.md

## [2026-10-12] readings | mechanisms/camp-and-territory-placement.md (chat round) | — | Claude (research-wiki)
- reading written: My rationale (exponent 3 from face validation in the initial runs).
- answers recorded: the sensitivity file's overlap measure is the intended one; only this year's territories count; reject when crowded or very poor (the code's `and` should be `or`); fixed-territory mode stays as is; the order effect on territory size is not intended but acceptable; Mesa `remove()` question deferred to the crisis page.
- updated: mechanisms/camp-and-territory-placement.md, mechanisms/crisis-and-replacement.md, model/assumptions.md (M3, M6, M7), model/parameters.md (exponent)
- added to the separate-PR list: overlap test as in `sensitivity_model.py`, counting this year's territories only (clear `model.territories` and stale `territory` attributes each year); `and` → `or` in the re-draw loop, with a guard against endless re-draws; test whether `Agent.remove()` leaves the grid. Write-up: Ch. 5 §5.6 wording on fixed territories.
- open in this round: overlap counted per territory or in total.

## [2026-10-12] readings | camp and territory placement round closed | — | Claude (research-wiki)
- answers recorded: the 25% overlap counts all other territories combined; the radius-20 candidate area is intended (the base radius).
- updated: mechanisms/camp-and-territory-placement.md, model/assumptions.md (M7)
- separate-PR list: overlap = share of the candidate area in the union of this year's other territories, rejected at ≥ 25%.

## [2026-10-12] readings | mechanisms/crisis-and-replacement.md (chat round) | — | Claude (research-wiki)
- reading written: My rationale (the replacement is an abstract successor).
- answers recorded: reserve capped at 100 (a herd the household "can work with"); failure tested on manpower after the set-aside; surplus criterion should be ≤ 0; population constant in fixed-territory runs too; replacements placed like all others.
- updated: mechanisms/crisis-and-replacement.md, model/assumptions.md (M18, M19), model/experiments.md (fixed-territory households)
- added to the separate-PR list: `surplus <= 0` in the failure test; no replacement queued when a fixed-territory household is reset (or no reset); replacements in `sensitivity_model.py` placed once with the others. Write-up: Ch. 5 §5.3.4 reserve cap.
- open in this round: the replacement's starting manpower.

## [2026-10-12] readings | crisis and replacement round closed | — | Claude (research-wiki)
- answer recorded: a successor starts with manpower as a new household does, max(35, herd / 20).
- separate-PR list: replacements no longer inherit the failed household's manpower (both files).
