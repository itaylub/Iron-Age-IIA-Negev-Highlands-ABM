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

## [2026-10-12] readings | mechanisms/enclosure-construction.md (chat round); session close | — | Claude (research-wiki)
- reading written: My rationale (0.6 marks "better than average conditions", set by face validation in the preliminary runs).
- answers recorded: manpower minima apply to free manpower; eligibility from the fifth year (`year >= 4`); reuse should require an unoccupied compound; a new build on a compound older than 15 years counts as new construction; ages run from last use; enclosure memory holds compounds the household has used; the +1 margin on the new-site criterion is intended.
- updated: mechanisms/enclosure-construction.md, model/assumptions.md (M16, M17), index.md (four rationales written)
- open for the next session: (1) range of Q: "yes" did not say whether to cap Q at 1 or log it first; (2) new-site criterion: mean within 20 cells of the camp or over the territory; (3) what counts as an occupied compound (deferral to the separate PR proposed).
- readings: 6 owed (herd dynamics, household economy, memory and territorial attachment, occupation history layers, site classification, within-year degradation).

## [2026-10-13] readings | enclosure construction round closed | — | Claude (research-wiki)
- answers recorded: range of Q: log Q in a test run first, then decide on a cap; new-site criterion: the average within 20 cells of the camp (the code matches); what counts as an occupied compound deferred to the separate PR (confirmed).
- updated: mechanisms/enclosure-construction.md, model/assumptions.md (M16, M17)
- separate-PR list (item 9): occupied-compound definition settled in the PR; log Q before deciding on a cap. Write-up list: Ch. 5 §5.3.3 new-site criterion = average within 20 cells of the camp, plus a margin.
- log.md: from this session, new entries go above the two consolidated lists, which stay at the end and are updated in place (dated).

## [2026-10-13] readings | mechanisms/herd-dynamics.md (chat round) | — | Claude (research-wiki)
- reading written: My rationale (the growth values come from the Dahl and Hjort book; Dahl & Hjort 1976 in Ch. 5 §5.2.2).
- answers recorded: capacity over the territory's cells; "up to 20%" should cap the realised rate (the code applies it before the multipliers); the taper to zero at 1,500 is intended and the text needs fixing; 10–30% decline is a typical range; heavily used ground should slow growth and speed decline (the code reverses it; settled here for both pages).
- updated: mechanisms/herd-dynamics.md, mechanisms/occupation-history-layers.md (stress direction settled), model/parameters.md, model/assumptions.md (M12), model/literature-cited.md, index.md
- separate-PR list: new item 12 (herd growth: territory capacity, realised-rate cap, inverted stress terms). Write-up list: Table A5.4 and Ch. 5 §5.3.2 herd ceiling and evaluation radius; decline "typically".
- open in this round: whether the 1,500 and the 10–30% decline also come from Dahl & Hjort; deferral of `calc_surplus`'s radius-25 capacity to the household-economy round (proposed).

## [2026-10-13] readings | herd dynamics round closed | — | Claude (research-wiki)
- answers recorded: the 1,500 taper and the 10–30% decline also come from Dahl & Hjort 1976, to be validated against the book before writing; `calc_surplus`'s radius-25 capacity deferred to the household-economy round (agreed).
- updated: mechanisms/herd-dynamics.md, mechanisms/household-economy.md (deferred item), model/assumptions.md (M12), model/literature-cited.md, model/parameters.md
- write-up list: validate the herd values against Dahl & Hjort 1976 before writing.

## [2026-10-13] readings | mechanisms/household-economy.md (chat round opened) | — | Claude (research-wiki)
- correction: the manpower-drift item said the random drift pushes manpower upward "until 55"; it rises about +0.9 a year up to 55 and +0.3 a year above (+0.3 more when surplus > 100), with no ceiling. Page corrected.
- presented: 8 items (My rationale; productive herd; capacity area, deferred from herds; stress cost; luxury consumption; 1% decay below 100; manpower deductions; manpower drift). Awaiting answers.

## [2026-10-13] readings | mechanisms/household-economy.md (chat round answers) | — | Claude (research-wiki)
- reading written: My rationale (surplus units = the sum of all liquid economic resources, not livestock).
- answers recorded: productive herd = the herd left after culling (the code matches only at or below the working herd); `calc_surplus` capacity over the territory; stress coefficient 0.3; 5% extra consumption only when surplus is abundant (above 100); 1% decay below 100 intended; 10 people set aside for the yearly migration, 1 herder per 75 head from literature (perhaps Günther et al. 2021, to check); manpower should stay more or less stable, growing slightly in good years.
- checked: Ch. 5 §5.3.4 calls the herd "the household's only liquid asset in the model", which sits uneasily with the reading; new Things to check line.
- updated: mechanisms/household-economy.md, model/assumptions.md (M15, M20), model/parameters.md, model/literature-cited.md, index.md
- separate-PR list: new item 13. Write-up list: household-economy items.
- open in this round: the extra-consumption rule (which amount the 100 test applies to); the manpower rule; how Ch. 5 §5.3.4's "only liquid asset" should read.

## [2026-10-13] readings | household economy round closed | — | Claude (research-wiki)
- answers recorded: surplus is livestock translated into economic value ("like money") but nothing specific, so Ch. 5 §5.3.4's "only liquid asset" sentence stays; extra-consumption rule approved (5% of the available surplus when it is above 100); manpower drift with equal odds of gain and loss (option A), keeping the surplus > 100 bonus.
- checked: simulated manpower over 75 years from 52 without the surplus bonus: current rule about 81 ± 15; equal odds about 52 ± 19.
- updated: mechanisms/household-economy.md, model/assumptions.md (M20), model/parameters.md
- separate-PR list: item 13 complete. Write-up list: describe the manpower drift.

## [2026-10-13] check | Mesa grid behaviour | — | Claude (research-wiki)
- read the Mesa source at v3.0.0 and v3.3.0 (shallow clone of github.com/projectmesa/mesa; PyPI unreachable from this session): `MultiGrid.remove_agent` sets `agent.pos = None`; `Agent.remove()` only deregisters the agent from the model and leaves it on the grid.
- consequences recorded: the home-range bonus never applies in `model.py` (memory page); failed households stay on the grid as occupied cells, without effect until the re-draw loop is fixed (crisis and camp pages).
- updated: mechanisms/memory-and-territorial-attachment.md, mechanisms/crisis-and-replacement.md, mechanisms/camp-and-territory-placement.md; separate-PR list item 8.

## [2026-10-13] readings | mechanisms/memory-and-territorial-attachment.md (chat round answers) | — | Claude (research-wiki)
- reading written: My rationale (threshold 5 = midpoint of the 0–10 scale, good vs bad experience).
- answers recorded: the home-range bonus should work (fix in the PR); bonuses once a year (Itay asked whether family camps add smaller bonuses: they do not; smaller values are in degradation and the site signal); quality measured after occupation (code matches); cap the penalty for very poor camps; P = last year's camp; later family camps should see earlier camps' degradation.
- updated: mechanisms/memory-and-territorial-attachment.md, model/assumptions.md (M4, M5), index.md
- separate-PR list: new item 14. Write-up list: Ch. 5 §5.2.2 and §5.3.1.
- open in this round: the rule for once-per-draw bonuses with refreshed degradation; the penalty cap.

## [2026-10-13] readings | memory and territorial attachment round closed | — | Claude (research-wiki)
- approved: per-draw rebuild with each bonus once (later family camps see earlier camps' degradation), implemented efficiently (bonus arrays once a year; family draws look up only the territory's cells; −0.5 update per new family camp); penalty cap at 5 × w with negative values clipped in `place_members`.
- updated: mechanisms/memory-and-territorial-attachment.md; separate-PR list item 14 complete.

## [2026-10-13] readings | mechanisms/occupation-history-layers.md (chat round opened) | — | Claude (research-wiki)
- added to Things to check: the pasture-reduction formula in `move_year` (L1034–1037), undocumented, with a 10% floor.
- presented: My rationale (× 5 and 2), ×1.5 weight, smoothing window shape, unsmoothed reuse potential, pasture reduction. The stress-direction item was settled in the herd round.

## [2026-10-13] readings | occupation history layers round closed | — | Claude (research-wiki)
- reading written: My rationale (× 5 and 2 from face validation in the preliminary runs).
- answers recorded: × 1.5 for very attractive, heavily invested cells; a circular smoothing window is better (a one-line change, so it goes to the PR); per-cell reuse potential intended (attractiveness grows with occupation on the cell, negative effects spread to the surroundings); pasture curve "nothing empirical, just my abstract understanding".
- updated: mechanisms/occupation-history-layers.md, model/assumptions.md (M9, M10), model/parameters.md, index.md
- separate-PR list: new item 15 (circular kernel). Write-up list: × 1.5 and the pasture curve.

## [2026-10-13] readings | mechanisms/site-classification.md (chat round opened) | — | Claude (research-wiki)
- checked: `Data/distac_pw.tif` and `.tfw` from the repository history (281 × 319 cells, pixel-is-area): the `to_gdf` origin lies within 3 m and 9 m of its lower-left corner, so it reads as a corner; simulated sites would then sit 125 m south-west of cell centres.
- presented: My rationale (0.5 / 0.25 increments), threshold test without code (deferral to experiments proposed), enclosure overwrite, 0.75 combination, origin.

## [2026-10-13] readings | site classification round closed | — | Claude (research-wiki)
- reading written: My rationale (seasonal camps leave traces, main camps more; a single visit is almost unidentifiable, only a few repeated visits make a site).
- answers recorded: threshold test deferred to experiments (agreed); enclosure asymmetry intended; no need to name the 0.75 combination in Ch. 5 §5.5.3; sites stay at the cell corner (no change to `to_gdf`).
- updated: mechanisms/site-classification.md, model/experiments.md, model/assumptions.md (O1, O2), index.md

## [2026-10-13] readings | mechanisms/within-year-degradation.md (chat round opened) | — | Claude (research-wiki)
- My rationale question reworded before it was answered: Ch. 5 §5.3.1 already names the processes, so it now asks where D = 0.5 and 0.3 come from (AGENTS.md › Rationale questions).
- noted: the main camp's degradation (L651) comes after the family camps are placed (L645–649).
- presented: My rationale, P, distance metric, radius, family camps and the order of degradation.

## [2026-10-13] readings | within-year degradation round closed; mechanism pages done | — | Claude (research-wiki)
- reading written: My rationale (households have a greater effect over a bigger area than a nuclear family; values assumed from the preliminary runs).
- answers recorded: D should not act at the camp cell (kernel centre to 0 in the PR, so P takes effect); follow the code's half-Manhattan distance (fix the caption); degradation across the territory (fix Fig. 5.4 and Table A5.2); the main camp degrades after its family camps, as now.
- updated: mechanisms/within-year-degradation.md, model/assumptions.md (M8), model/parameters.md, index.md
- separate-PR list: new item 16. Write-up list: A5.1–A5.2 caption, Fig. 5.4, Table A5.2.
- all eleven mechanism rationales are now written.

## [2026-10-13] check | reproducibility of runs; null baseline | — | Claude (research-wiki)
- read through the Drive connector (read-only): sizes of `household_data.csv` in trial 173's calibration replicates and the 30 validation runs; `null_baseline_scores.csv`; `best_params_30iter_stats.csv` (household summaries only, no scores).
- found: all ten seed-matched pairs differ. `NomadModel` calls `super().__init__()` without a seed (L955), so Mesa's own generator (used by `shuffle_do`, L1015, L1043) is seeded from OS entropy in Mesa 3.0.0 and 3.3.0: no run reproduces from its seed, and the no-interference check cannot be done with these runs.
- null baseline: mean 0.318, 95% CI 0.309–0.328, as reported; 36.7% uses 0.2013, 33.1% against 0.213.
- updated: model/experiments.md

## [2026-10-13] readings | model/experiments.md (chat round answers) | — | Claude (research-wiki)
- answers recorded: results may be re-run after the separate PR; §5.6 need not describe `sensitivity_model.py`'s differences (closes the Year-0 item); the threshold sweep was run manually; compare the null baseline with 0.213 (33.1%); seed Mesa's generator in the PR and close the no-interference check, but leave App. 5 §A5.3's statement for now; the exact rainfall replay is not intended but not critical; "seed-173" is trial 173 (replicate not remembered); swap calibration.ipynb cells 5 and 6.
- Itay's correction on the chat summary: the validation runs were never meant to repeat the calibration replicates (settled 2026-10-12); recorded on the page, with the note that the unseeded Mesa generator keeps them distinct in any case.
- updated: model/experiments.md; separate-PR list items 17 and 18; write-up list.
- open in this round: the null-baseline seed wording (Itay asked which notebook; answered: `sensitivity_analysis.ipynb` cell 9).

## [2026-10-13] readings | experiments round closed | — | Claude (research-wiki)
- answer recorded: App. 5 §A5.7.1's seed formula refers to the calibration; the null baseline is a separate experiment (read as: the sentence stands).
- updated: model/experiments.md

## [2026-10-13] lint | model/odd-map.md, model/parameters.md, model/assumptions.md | — | Claude (research-wiki)
- none of the three pages has open Things to check items. Refreshed stale gap notes from this session's answers and checks: ODD map rows Entities (stress direction), Learning (home-range bonus never applies), Sensing (pasture over the territory), Interaction (family camps see earlier degradation), Stochasticity (unseeded Mesa generator), Submodels (all rationales written; values to validate); parameters row Start (`year >= 4` intended).

## [2026-10-13] session close | mechanism rounds and experiments complete | — | Claude (research-wiki)
- this session: closed the enclosure round; chat rounds on herd dynamics, household economy, memory and territorial attachment, occupation history layers, site classification, within-year degradation and experiments; refreshed the ODD map and parameters. All eleven mechanism rationales are written; readings owed: none.
- checks this session: Mesa 3.0.0 / 3.3.0 source (grid removal, unseeded model generator); `distac_pw.tif` georeferencing; Itay's results on Drive (household data sizes, null-baseline scores).
- next: the separate PR, from the consolidated list below (18 items), in a new session. Environment note: this session had numpy and pandas but not scipy, mesa, geopandas or optuna, and pypi.org did not resolve, so the model could not be run here.

## [2026-10-13] convention | no running code | — | Claude (research-wiki)
- AGENTS.md › Local conventions: agents do not run the model or parts of its code, and do not install packages to do so (Itay, 2026-10-13). The environment note in the session-close entry above no longer applies.

## [2026-10-14] code | separate PR: the 18 listed items | — | Claude (Claude Code)
- done on branch `claude/separate-pr-code-fixes`, from `28478fc` of this wiki branch: draft PR 8 (<https://github.com/itaylub/Iron-Age-IIA-Negev-Highlands-ABM/pull/8>) against the wiki branch, not `main`. One commit per item; the commits are marked on the Separate-PR list below (hashes as on the branch, before any merge).
- nothing was run (AGENTS.md › No running code): changes checked by reading the code and the diffs; both model files and the notebook cells parsed, not executed, with Python's `ast` and checked for undefined names with `symtable`; Mesa behaviour read in the Mesa 3.0.0 and 3.3.0 source.
- answers in chat (Itay, 2026-10-14): items whose spec names only `model.py` but whose code is in both files (3, 4, 14, 15, 16, 17) are changed in both files, so `sensitivity_model.py` stays `model.py` plus its two switches; per-run random generators: yes (item 10, second commit); item 3 guard: at most 100 draws, then the least crowded candidate, preferring those that pass the capacity test; item 8: off the grid, then Mesa's `self.remove()`, in both files; item 9, occupied compound: another household's main or family camp on the cell this year, or its reuse or build there this year.
- choices made in the PR, for Itay to confirm: year 74's no-data pasture cells set to 0 (item 1); each household's `territory` attribute is kept until it places again, because the main-camp draw reads last year's territory for the territory bonus, and the overlap test reads only `model.territories`, cleared each year (item 3); a manpower loss keeps at least 1 person (item 13); the occupied test applies to reuse only, not to `build_enclosure`'s existing-compound candidates (item 9); the null-baseline comparison value 0.213 is set in the notebook cell (item 18).
- found while coding: in `sensitivity_model.py` (flexible mode) `model.agents.remove(self)` took a failed household out of `model.agents` only, so it kept camping and stepping in `shuffle_do` beside its replacement and was missing from `household_data.csv` (fixed by item 8; it affected the flexible-mode sensitivity runs); `Agent.create_agents`, which `model.py`'s replacements use, is in Mesa 3.3.0 but not 3.0.0, while `requirements.txt` allows 3.0; at Year 0 `model.py` measures the main camp's remembered quality within 20 cells and the sensitivity file within the territory radius (now 25); README's example `model.run_model_opt(seed=42)` lacks required arguments. None of these is changed beyond item 8.
- Q (`env_quality`) is now logged in `household_data.csv` (item 9); the decision on a cap at 1 waits on Itay's test run.
- to do: the wiki's code line numbers were recorded at commit `2249331` (`model/overview.md`, `model/inventory.md`) and need re-checking against the PR's head commit (`_guide/ingest-code.md` › Updates); the mechanism pages still describe the old code, and their "For the separate PR" lines are not yet marked done. Item 7 and item 8 also change `model.py` runs in which households fail, and items 17 and 10b change the random streams (not the distributions).
- not changed: the thesis PDF; the write-up list below is Itay's thesis text.

### Separate-PR list as of 2026-10-14 (code and repository docs; done in PR 8, draft, not merged)
1. Pasture: read yearly array 2 instead of array 0 in both model files; handle year 74's no-data cells ("a big red flag"). Done: `4bd3dd0` (no-data cells set to 0).
2. `sensitivity_model.py` Year-0 territory: fixed radius 25, as in `model.py`. Done: `6a3a981`.
3. Overlap rule: share of the radius-20 candidate area in the union of this year's other territories, rejected at ≥ 25%; clear `model.territories` and stale `territory` attributes each year; re-draw when crowded *or* very poor (`and` → `or`), with a guard against endless re-draws. Done: `1be0dcd` (guard: 100 draws, then the least crowded candidate, preferring those that pass the capacity test; `territory` attributes kept for the territory bonus).
4. Failure test: `surplus <= 0`. Done: `864dbd9` (both files).
5. Fixed-territory mode: keep the population constant (no replacement queued when a household is reset). Done: `7b129d1`.
6. Replacements in `sensitivity_model.py`: placed once, with everyone else. Done: `1a60dab` (removes the temporary centre placement).
7. Successors start with manpower like a new household, `max(35, herd / 20)`. Done: `7fae564`.
8. Mesa `Agent.remove()` does not take a failed household off the grid (checked in the Mesa 3.0.0 and 3.3.0 source, 2026-10-13): remove it from the grid before `self.remove()` in `model.py`, as `sensitivity_model.py` does (proposed); check the sensitivity file's temporary centre placement. Done: `5284465` (both files; the sensitivity file's `model.agents.remove(self)` replaced by `self.remove()`).
9. Enclosure eligibility `year >= 4`; reuse only of unoccupied compounds (what counts as occupied to be settled in the PR); log Q (`env_quality`) in a test run, then decide whether to cap it at 1. Done: `cfbcacc` (occupied: another household's camp on the cell this year, or its reuse or build there this year; Q logged in `household_data.csv`, cap decision pending the test run).
10. Remove `CUDA_VISIBLE_DEVICES` from `objective`. Consider per-run random generators (under consideration). Done: `8b3483e` (CUDA) and `d27116c` (per-run generators, agreed 2026-10-14).
11. Stale module names in `Code/` docstrings and calibration.ipynb; output paths for reproduction; docs/objective_function.md from the code and Ch. 5; docs/DATA.md (75 yearly groups plus `metadata`, grid orientation, metadata use). Done: `7bb336e`.
12. Herd growth (`update_flock_size`, both files): capacity and mean pasture over the territory's cells instead of the radius-30 window; cap the realised growth rate at 0.2 after all multipliers; invert the stress terms so heavily used ground (low `stress_ras`) slows growth and speeds decline. Done: `a2c8f8e`.
13. Household economy (`calc_surplus`, `step`, both files): `productive_herd = flock_head − cull_amount`; capacity in `calc_surplus` over the territory's cells; 5% extra consumption only when the available surplus (0.7 × previous + this year's products and culling) is above 100, as 5% of it (approved); manpower drift with equal odds of gain and loss (⌈5U⌉, probability 0.3 each, at any size; drop the `> 55` condition), keeping +1 with probability 0.3 when surplus > 100. Done: `3c71690` (a manpower loss keeps at least 1 person).
14. Memory and territorial attachment: keep each household's last camp through `reset_pos` so the home-range bonus applies (centre starts at the Year-0 camp; P = last year's camp); for each draw, the personalised surface = the current shared surface (with this year's earlier degradation) + each bonus once (approved), implemented as: HM (home-range + capped memory) and T (last year's territory) built once a year at the main draw; family draws read the shared surface for the new territory's cells only, with + HM + 2.5; −0.5 in HM at each new family camp (approved); cap the penalty for very poor remembered camps at 5 × w (q no lower than 0.1) and clip negative values to 0 in `place_members` before cubing (approved). Done: `df4776c`.
15. Occupation history: circular smoothing kernel (weights 0 where d > 20, before normalising; `Yi_params` L442–446). Done: `5dd711b` (both files).
16. Within-year degradation: kernel centre 0 (`get_degrade_kernel` L241), so the camp cell loses only P. Done: `5a83e8d` (both files).
17. Reproducibility: pass each run's seed to Mesa (`NomadModel` → `super().__init__(seed=seed)`; L955), so `shuffle_do` is seeded. Done: `2a34132` (both files).
18. Notebooks: swap `calibration.ipynb` cells 5 and 6; `sensitivity_analysis.ipynb` cell 9 compares the null baseline with the 30-replicate mean (0.213) rather than `study.best_value`; (low priority) a new shuffle of the rainfall years for each further 75-year cycle (`sensitivity_model.py` L399, L945). Done: `cbd1fb7` (the markdown heading of former cell 5 moves with it).
Several of these change calibrated behaviour (1, 3, 4, 9, 12, 13, 14, 15, 16; also 7 and 8 in runs where households fail); the calibration ran with the code before PR 8.

### Write-up list as of 2026-10-13 (thesis / journal text, Itay's)
- Ch. 5 §5.2.2, Fig. 5.2, App. 5 Table A5.5: drop the crisis flag. Ch. 5 §5.2.2: enclosure memory = compounds the household has used.
- Ch. 5 §5.4: two passes (placement, then economic step). State the Year-0 territory radius of 25.
- Ch. 5 §5.2.1.2: approved rainfall-draw wording (overview, Things to check).
- App. 5: equation objects A5.1–A5.3; Tables A5.1 and A5.6 describe the corridor; Table A5.1 note "membership 0.5 (suitability 5)"; §A5.3 rainfall sentence may go; §A5.3 reproducibility statement vs parallel trials; §A5.7.3 1:13.4.
- Table A5.4 and Ch. 5 §5.2.4: the 3,251.54 km² extent includes the buffer.
- Ch. 5 §5.5.2 and App. 5 §A5.7.2: ratio, not proportion; the 0–1 bound holds while other sites outnumber enclosed ones.
- App. 5 Table A5.4 and Ch. 5 §5.3.2: herd growth tapers to zero at 1,500 (no cap at 1,000); capacity over the territory (not radius 25); decline "typically" 10–30%. Validate the 20%, the 1,500 and the 10–30% against Dahl & Hjort 1976 (pages) before writing.
- Ch. 5 §5.3.2 and App. 5 Table A5.4 (household economy): productive herd = the herd left after culling; stress cost 30% × s (A5.4 says 15%); 1% decay at or below 100; extra consumption above 100; the 10-person migration set-aside and 1 herder per 75 head (validate against Günther et al. 2021 before writing). Ch. 5 and App. 5: describe the manpower drift.
- Ch. 5 §5.2.2: camp memory holds the quality after the stay. Ch. 5 §5.3.1: P is last year's camp.
- App. 5 (Table A5.4 or §A5.2) and Ch. 5 §5.3.2: the × 1.5 for cells at 2 or more; the pasture-reduction curve and its 10% floor.
- App. 5 eq. A5.1–A5.2 caption: half the Manhattan distance. Ch. 5 Fig. 5.4 caption and App. 5 Table A5.2: household degradation across the territory (20–30 cells), not ~5 km.
- Ch. 5 §5.6 and App. 5 Table A5.7: compare the null baseline with 0.213 (33.1% reduction), not 0.201 (36.7%). App. 5 §A5.7: no section on the manual site-threshold sweep, though §5.6 points there. Fig. 5.11 caption: trial 173, not "seed-173". App. 5 §A5.3 reproducibility statement: left for now (Itay, 2026-10-13).
- Ch. 5 §5.6: in fixed-territory mode the main camp stays on one cell. Ch. 5 §5.3.4: reserve capped at 100. Ch. 5 §5.3.3: ages count from last use; the new-site criterion compares with the average within 20 cells of the camp, plus a margin, not the territory's average.

## [2026-10-26] code | re-pin to the fixed code (032c2a1); PR 8 fixes marked done | — | Claude (Claude Code, research-wiki)
- trigger: first subtask of the ODD direction note (owner's vault): bring the wiki to the code after PR 8 before writing the ODD.
- code: branch `claude/separate-pr-code-fixes` at `032c2a1` (2026-10-26). `Code/model.py` unchanged since `5a83e8d` (2026-10-14, the last PR 8 item); `Code/sensitivity_model.py` since `5f415eb` (2026-10-25, Year-0 camp memory within 20 cells, as `model.py`). Since `2249331`: the 18 PR 8 items, notebook outputs (`180883d`, `a83420c`), and the calibration and sensitivity scripts in `scripts/` (`22b082b` … `032c2a1`).
- method: old line numbers mapped to new ones from `git diff -U0 2249331 032c2a1` (a Perl helper in the session scratchpad); every reference inside changed code read by hand in the new file. Nothing was run (AGENTS.md › No running code); the laptop has no Python, so the status script was not run and links and owed blocks were checked with Perl and grep instead.
- updated, re-pinned to `032c2a1`: model/overview.md (frontmatter; entities table with `last_camp`, `home_memory_bonus`, `env_quality`; environment; schedule; Year-0 memory; random generators; input data with the calibration target files), model/inventory.md (frontmatter; Mesa 3.3 need; notebooks; new "Entry points (scripts)" table; file sizes; the two-file differences rewritten for the current code; docs status; input data; outputs), model/parameters.md (all line numbers; rows changed by PR 8 marked with their item; new rows for Year-0 memory radius, random generators, pasture source, family-camp territory bonus, penalty cap, re-draw guard, grazing pressure, productive herd, Q, unoccupied reuse; the thesis weights labelled as such).
- updated, PR 8 marked: 37 "Done in PR 8" lines (item, commit, line at `032c2a1`) at the end of the Things to check items they close, on 10 mechanism pages and model/experiments.md; one "Partly done" (Q logged; the cap at 1 still open). model/odd-map.md gaps marked "done in PR 8". Dated entries keep their `2249331` line numbers, with a note saying so on overview and inventory.
- mechanism pages: bodies not rewritten. Each has `body_code_commit: 2249331…` in its frontmatter and a status note under its title; the bodies are to be brought to the current code with the ODD submodels (direction-note subtasks 7a–c).
- not done, for the owner: the October 2026 calibrated weights (study `opt_fixed_strict_2026_10`, trial 197) are not on parameters.md, because `analysis\rerun_top10.csv` is on the PC and was not read; model/experiments.md does not yet record the October 2026 studies. docs/DATA.md, docs/objective_function.md and README as revised in PR 8 item 11 were not re-read.
- readings: none written; none owed outside the guides' templates.

## [2026-10-26] code | model/parameters.md: calibrated weights of the fixed code (trial 197) | — | Claude (Claude Code, research-wiki)
- added: the trial 197 table (integers, normalised weights, mean ± SD across the 10 leading distinct sets) and its scores, from `rerun_top10.csv` and `rerun_top10_runs.csv` (Drive copies of the study's `analysis\` files), under "Calibration of the fixed code (October 2026)". The trial 197 values were checked against both files; the 30-run mean and SD recomputed from the per-run file.
- Itay, 2026-10-26: approved the values; the integers are 0–7 importance scores and only the normalised values matter, so their sum carries no meaning.
- not added: the leading-20 means from the settle check (`settle_check.json`, on the PC only).
