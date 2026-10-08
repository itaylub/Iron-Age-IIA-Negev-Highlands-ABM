<!-- research-wiki v1 -->
# AGENTS.md — Nomad ABM wiki

This folder is a research wiki that AI agents maintain for Itay. Read this file fully before doing anything here, and read the relevant file in `_guide/` before each operation.

## Profile
- Purpose: Keep a traceable account of the Nomad ABM (Iron Age IIA Negev Highlands Human-Environment Dynamics Model) in this repository: what each mechanism does, where it lives in the code, what assumption it encodes and what justifies it, so the model can be written up as an ODD / journal paper and its mechanisms reused elsewhere.
- Kind: model
- Owner: Itay (Itay Lubel) (signs reading blocks)
- Aims (setup interview, 2026-10-08): write the ODD / journal paper; reuse mechanisms elsewhere.
- Research questions: see `questions/`
- Parent wiki: none
- Working language: English. Quotes are kept in the original language with a translation.
- Bibliography: `references.bib`, citekeys generated: firstauthor + year + first title word
- Ingest mode default: ask
- Drafted readings: only when the owner asks
- Style: none stated

## The rule this wiki runs on
Agents extract, link and keep the books. Itay interprets.
- Write what sources say, attributed, with locators (printed pages, figures, tables; `file › function, lines` for code), keeping the authors' hedges and their scope conditions.
- Never write a `My reading`, `My rationale`, `My understanding` or `My position` block in the owner's name. Ask for them, one pointed question per part, and record the answers in the owner's words. Unanswered questions stay as `· owed` blocks.
- Draft readings only on request, marked `Claude's draft … · unreviewed`.
- Quotes stay verbatim in the original language. Translations are marked `*Translation (Claude, unreviewed):*`.
- Record disagreements on debate pages and never resolve them. Only the owner settles a debate.
- Agent-written interpretation (drafts, syntheses, translations, Things to check) is never cited as evidence on another page.
- Never invent metadata, DOIs, page numbers or quotes. Write `unknown` and ask.
- Create new pages sparingly (they must bear on the research questions, or a second source must discuss the topic, or the owner must ask). Otherwise list the topic under Mentions.
- Never copy source files into the wiki. Link them.

## Every session
1. Run `python _tools/wiki_status.py . --brief` and show the result to the owner.
2. Do the task, following the guide for it.
3. Update `index.md`, append to `log.md` (naming yourself as the agent), update `references.bib`, and re-run the status script. Tell the owner what changed in a few lines.

## Guides
- `_guide/readings.md` covers reading interviews, drafts and reading sessions.
- `_guide/page-formats.md` covers frontmatter, page templates, reading-block syntax, index and log formats.
- `_guide/ingest-sources.md` covers papers, books, theses, reports, datasets, web pages and the owner's notes.
- `_guide/ingest-code.md` covers repositories and models (NetLogo, Python).
- `_guide/queries-and-maintenance.md` covers answering questions, filing answers and health checks.

The guides come from the research-wiki skill and may be refreshed. Wiki-specific changes go below, never into the guides.

## Local conventions
These were agreed with the owner, and they override the guides.
- **The wiki lives inside the model repository** (`wiki/` at the repo root), at the owner's choice, rather than in a sibling `<repo>-wiki` folder. Paths to repository files are written relative to the repo root (`Code/model.py`, `thesis/appendix-5-ABM.docx`); links from wiki pages to them are relative (`../../Code/model.py`).
- **Thesis Chapter 5 and Appendix 5 are the owner's own model documentation** (`thesis/chapter-5-ABM.docx`, `thesis/appendix-5-ABM.docx`, `thesis/chapter-5-tables-and-figures.docx`). Treat them like a NetLogo Info tab or README: quote and cite them as the owner's words, compare them with the code, and record where they disagree under Things to check. They get no source pages and no reading interviews. Locators are section, table and equation numbers as printed in the documents, since the .docx files carry no fixed page numbers: `(Ch. 5 §5.3.1)`, `(App. 5 Table A5.4)`, `(App. 5 §A5.2, eq. 4.1)`. The literature they cite gets source pages only when a source is ingested from the original (see `model/literature-cited.md`).
- **Code locators** name the file relative to `Code/`, the class or function, and line numbers at the commit recorded in `model/overview.md`: `(model.py › Household_Agent.step, L544–616)`. `model.py` is the calibrated model; `sensitivity_model.py` is the variant the sensitivity notebook imports. When the commit changes, re-check line numbers (see `_guide/ingest-code.md` › Updates).
- **Rationale questions** for mechanisms aim at what Chapter 5 and Appendix 5 do not already say (values marked "Assumed" in App. 5 Table A5.4, and places where code and documentation differ), since the documented reasoning is already the owner's own account.
