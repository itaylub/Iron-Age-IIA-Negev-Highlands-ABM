# Page formats

## General

- Markdown, UTF-8, YAML frontmatter on every page.
- Links are relative markdown links, `[Caple & Løvschal 2025](../sources/caple2025agropastoral.md)`. Don't use `[[wikilinks]]`, since not every agent or viewer resolves them.
- File names are lowercase ASCII with hyphens. Source pages are named by citekey.
- Locators look like `(p. 12)`, `(pp. 12–14)`, `(Fig. 3, p. 9)`, `(Table 2, p. 11)`, `(n. 21, p. 44)` for notes, and `(model.py › Household.step, L210–245)` for code. Use printed page numbers and record the mapping to PDF pages in `locator_basis`.
- Attribution verbs match the source's certainty, and hedges stay (Part 1, rule 1 of the skill: show only with evidence, otherwise argue, propose, suggest).
- Dates are ISO (2026-10-07).
- Follow the Style line in AGENTS.md › Profile for prose on pages.

## Reading blocks

The status script reads this exact syntax.

```
**My reading** · owed
> Q: One pointed question, understandable without this conversation.

**My reading** · Itay, 2026-10-07
The owner's words.

**Claude's draft reading** · unreviewed, 2026-10-07
Draft text, only when the owner asked.
```

Variants: `My rationale` (model mechanisms), `My understanding` (concept, method and entity pages), `My position` (debates). An approved draft becomes `**My reading** · Itay, 2026-10-08 (approved Claude draft)`.

## Quotes and translations

```
> “Original wording exactly as printed.” (p. 7)
> *Translation (Claude, unreviewed):* English rendering.
```

Once the owner has checked a translation, it becomes `*Translation (checked by Itay):*`. Quotes keep the source's spelling and punctuation. Use `…` for omissions and `[ ]` for insertions.

## Source page (`sources/<citekey>.md`)

```
---
type: source
kind: paper              # paper | chapter | book | thesis | report | dataset | web | grey
citekey: caple2025agropastoral
title: "Agropastoral possibilism and the trajectorial affordances of Danish inland heaths: a study of deep-time entrapment"
title_en:                # only for non-English titles, with "(Claude translation)" if you translated it
authors: ["Caple, Zachary", "Løvschal, Mette"]
year: 2025
venue: "Journal of the Royal Anthropological Institute"
volume_pages:            # e.g. "31(2): 345-368", or unknown
doi: "10.xxxx/xxxx"      # or none | unknown
doi_verified: yes        # yes = printed in the source, or checked to resolve to this work
url:
file: "G:\\…\\file.pdf"  # where the user keeps it; never a copy in the wiki
language: en
locator_basis: "printed pp. 1–24 = PDF pp. 1–24"
ingested: 2026-10-07
ingest_mode: close       # close | quick
user_has_read: yes       # yes | no | unknown
tags: []
---

# Caple & Løvschal 2025: Agropastoral possibilism and Danish inland heaths

One descriptive sentence on what kind of work this is and what it does. No evaluation.

## At a glance
- Study area:
- Period:
- Material and data:
- Methods:
- Main claim (authors'):

## Scope and caveats (authors' own)
- Each scope condition, limitation or hedge the authors state, with locator.
- If they state none, write "None stated explicitly." Don't add your own here (those go under Things to check).

## Overall takeaway
**My reading** · owed
> Q: …

## Theoretical approach
- Attributed, located bullets of what the authors do and say.

**My reading** · owed
> Q: …

## Methodology
…
## Results and evidence
…
## Discussion and conclusions
…

## Relevance to my research
- Links to `questions/` pages this may bear on, as links only with no claims.

**My reading** · owed
> Q: …

## Key quotes
> “…” (p. N)

## Things to check
- Questions you noticed while extracting, such as figures that don't match the text, a general claim resting on one site, or a term used differently from other sources in the wiki. Phrase them as questions with locators, never as verdicts.

## Mentions
- Terms, sites, people and works mentioned that have no page, as plain text.

## Links
- Concepts, methods, entities and debates this source feeds, as relative links.
```

Section names follow the reading parts for the source kind (`_guide/readings.md`). A source whose text is unreliable gets a line in Things to check (for example "numbers read from page images; text layer garbles digits").

## Concept, method and entity pages

```
---
type: concept            # concept | method | entity
entity_kind:             # entities only: site | region | period | person | organisation | species | dataset
aliases: []
created: 2026-10-07
---

# Possibility space

## As used in the sources
- **Caple & Løvschal 2025** ([source](../sources/caple2025agropastoral.md)) define it as “…” (p. 2). Scope: West Jutland heaths, c.1600 BCE–1850 CE.
- **Itay, note "model data needs" (2025-10)** ([note](../notes/model-data-needs.md)) plans to … (a plan, not a finding)

## Tensions
- One line per related debate, with link.

## My understanding
**My understanding** · owed
> Q: …

## Related
- Links.
```

Site entities record location as the source gives it, including coordinates with their reference system (for example ITM, EPSG:2039). Don't convert coordinates unless asked, and label any conversion as yours.

## Debate page (`debates/`)

```
---
type: debate
status: open             # open | settled-by-user
created: 2026-10-07
---

# Phrase the disagreement as a question?

## Positions
### A: short label
- **Source (year)** ([link](…)) argues … Basis: evidence type and locator. Scope: …
### B: short label
- …

## What each side cites
- Only from the sources' own arguments. No verdict.

## My position
**My position** · owed
> Q: …
```

When the owner settles it, set `status: settled-by-user` and record their reasoning in the My position block. Both positions stay.

## Question page (`questions/`)

The owner's research questions and hypotheses, in their words, with frontmatter `type: question` and `created`. Agents add a "Sources bearing on this" list (link plus one attributed, located line each) and an "Open threads" list. Agents don't edit the question itself.

## Note page (`notes/`)

```
---
type: note
title: "model data needs"
origin: "Google Doc <url>; path as the owner knows it"
note_date: 2025-10-08    # last modified date of the original, if known
snapshot: 2026-10-07
status: current          # current | draft | superseded (ask the owner)
---

# model data needs (Itay's note)

## Note (verbatim snapshot, 2026-10-07)
The owner's text exactly, converted to markdown only.

## Linked in the wiki
- Which pages now point to this note, and for what.

## Things to check
- E.g. "The original contains a diagram that wasn't readable from the export."
```

## Synthesis page (`syntheses/`)

Filed answers, only when the owner asks.

```
---
type: synthesis
status: unreviewed       # unreviewed | reviewed
question: "…"
created: 2026-10-07
---

> Claude's synthesis, unreviewed. Built from the pages linked below. It is not a source and isn't cited as evidence elsewhere in the wiki.
```

## index.md

```
# Index: <wiki name>

## Sources
- [Caple & Løvschal 2025](sources/caple2025agropastoral.md): Danish heath agropastoral regimes c.1600 BCE–1850 CE, possibility space · close · readings 1/6
## Concepts
## Methods
## Entities
## Debates
## Questions
## Notes
## Model
## Syntheses
```

One line per page. For sources, add mode and readings written out of total.

## log.md

Append only, newest at the bottom.

```
## [2026-10-07] ingest | caple2025agropastoral | close | Claude (research-wiki)
- created: sources/caple2025agropastoral.md, concepts/possibility-space.md
- updated: index.md, references.bib
- readings: 1 written, 5 owed
- to check: DOI not printed in PDF, looked up and verified
```

Operation names: setup, ingest, note, code, query, synthesis, readings, lint, refresh, convention. Always name the agent.

## references.bib

Standard BibTeX, one entry per source, key equal to the citekey. Include `doi`, `url` and `language` where known, and `note = {original title in Hebrew: …}` for translated titles. Paperpile, Zotero, Word citation add-ins and LaTeX can all import this file.
