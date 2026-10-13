# Ingesting code and models

The goal is a wiki that lets the owner explain the model, trace every modelling assumption to its justification, and write the model up (ODD protocol, methods section, paper).

## 0. Getting the code

- **GitHub URL.** Shallow-clone if the session can reach GitHub, otherwise ask for a local path. Record the repository URL and commit (`git rev-parse HEAD`) in `model/overview.md`.
- **Local folder.** Record the path as the owner knows it and the newest file date. Note whether it is under version control.
- **Read only.** Don't modify, reformat or "fix" the code. Don't run it unless the owner asks, since models can run long, need environments and write files.

## 1. Inventory (`model/inventory.md`)

List languages, entry points, model files, notebooks, documentation (README, NetLogo Info tab, docstrings, markdown), input data, outputs and results files, and environment files. Flag empty (0-byte) files, stubs and placeholders, and duplicated or diverging copies of the same module.

- **NetLogo.** A `.nlogo` file is sections separated by `@#$#@#$#@`, holding the code, interface widgets (sliders, switches and choosers are parameters with min, max and default), the Info tab (the author's own description, to be quoted as theirs), and BehaviorSpace experiments (XML). `.nlogox` is XML with the same parts.
- **Python (Mesa and similar).** The model class's `__init__` arguments are parameters. Agent classes' `step` methods are behaviours. Scheduler and activation order make the process schedule. DataCollector reporters are outputs. Notebooks are experiments and analyses, so read the code and markdown cells, and look at outputs only to see what was produced.

## 2. Pages

- `model/overview.md` covers purpose (the author's words where they exist), entities and their state variables, spatial and temporal scales, and process overview and schedule. Ask the owner the Purpose question before you show your overview (`_guide/readings.md`).
- `mechanisms/<slug>.md` gets one page per key mechanism or algorithm, not per function. "Key" means it drives the dynamics (decision rules, resource dynamics, demography, learning, exchange, environment generation) or the owner's questions hinge on it. Each page holds what it does in plain language, where it lives (file › function, lines), inputs and parameters, what it changes, the assumption it encodes, its justification (a source link with locator, the owner's rationale, or "none recorded"), and an owed `My rationale` block. Utility code (plotting, I/O, dashboards) gets one line in the inventory.
- `model/parameters.md` is a table of name, default, range or options, units, where defined (file:line), used by (mechanism links) and justification. Copy values from the code. If defaults differ between files (interface, code, notebook), list each one.
- `model/assumptions.md` is a register of each assumption with where it is encoded and its status (sourced, owner's rationale, or unjustified). This is the list the owner will need for the paper.
- `model/experiments.md` records, per experiment or notebook, the question, parameter settings and sweeps, outputs, where results are stored, and whether they are present.
- `model/odd-map.md` maps each ODD element to wiki pages and lists the gaps. The elements are Purpose and patterns; Entities, state variables and scales; Process overview and scheduling; Design concepts (basic principles, emergence, adaptation, objectives, learning, prediction, sensing, interaction, stochasticity, collectives, observation); Initialization; Input data; Submodels.
- `sources/` holds the literature the model draws on (cited in code, docs or by the owner), ingested per `_guide/ingest-sources.md`. In a spin-off, these live in the parent.

## 3. Discrepancies

Code that disagrees with its docs, defaults that differ between files, docstrings promising things that aren't there ("based on the NetLogo implementation", "citation to be filled"), dead code, empty modules, and notebooks that reference missing files all go under Things to check on the relevant page, with locations. Report them, but don't resolve them.

## 4. The rationale interview

One question per key mechanism, grounded in the code. For example: "Stored food decays by `decay_rate` = 0.1 each tick (model.py › Household.step, L210). What real process does that stand for, and where does 0.1 come from?" Recording rules are the same as for readings. Unanswered questions stay owed.

## 5. Updates

On re-ingest, compare against the recorded commit or file dates, update the affected pages, and log what changed in the code and in the wiki.
