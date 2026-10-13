# Ingesting sources and notes

## 0. Before reading

- Settle the source kind and the mode. **Close** means one source with discussion and the reading interview, the default for sources that matter or that the owner knows well. **Quick** means extract and link only, with all reading parts written as owed blocks, for batches and peripheral sources. If the owner didn't say, ask in one line: "Close or quick? And have you read it already?"
- Check for an existing page (index.md, references.bib, DOI, file name). In a spin-off, check the parent wiki too. Update existing pages; never create duplicates.

## 1. Reading the source

- **PDFs.** Run `pdffonts` first. With fonts present, extract text (`pdftotext -layout`). With no fonts it's a scan, so read rendered page images (or OCR). Look at the pages where figures or tables carry results.
- **Locators.** Use the printed page numbers, not PDF page indices. A chapter or thesis excerpt often starts at page 44, not 1. Record the mapping in `locator_basis`.
- **Hebrew, Arabic and other RTL PDFs.** The text layer often garbles digits and punctuation while the letters come out fine. In a tested Hebrew chapter, "1967–1968" was extracted as "5900-5902", "Bar-Adon 1972" as "5908" and section "4.1" as "1.1". Take every number, date, section number, page reference and citation year from the rendered page image, not from the text layer. `verify_quotes.py` reports `DIGITS?` when a quote matches only with digits ignored.
- **Long sources.** Work chapter by chapter. Either use one source page with a section per chapter, or chapter pages (`citekey-ch03.md`) linked from the book page when chapters matter separately.
- **Images inside documents** (diagrams in a Google Doc, figures you can't render). Say on the page that they weren't read, and ask the owner.
- **Web pages.** Record the URL and access date. Pages change, so quote what matters.

## 2. Metadata

- Fill the frontmatter (page-formats).
- **DOI.** Take it from the source itself. If it isn't printed, look it up (Crossref or the publisher's page) and set `doi_verified: yes` only when the landing page is this work. Never assemble a DOI from patterns.
- **Unknowns.** A missing author, year, title or venue gets `unknown`, and you ask the owner in your report. A file name such as `uri_phd_…` is a hint to confirm, not metadata. If you fill a gap from outside the file (the owner's description, an author's publication list, a catalogue), record where it came from in a `metadata_basis` field and ask the owner to confirm it.
- **Citekey.** Take it from the owner's BibTeX export if AGENTS.md names one. Otherwise use lowercase first-author surname + year + first significant title word, ASCII only (`caple2025agropastoral`). For Hebrew-language authors, use the transliteration the author uses in English publications, and ask if unsure.
- **Non-English titles.** Keep `title` in the original and put the English in `title_en`, marked "(Claude translation)" if you translated it.

## 3. Close mode

1. If the owner has read the source, ask for their overall takeaway now, before reading or showing anything (`_guide/readings.md`). Record it.
2. Read the whole source and write the extract into the source page: At a glance, Scope and caveats (authors' own), the extract under each part, Key quotes, Things to check, Mentions.
3. Check the quotes: `python _tools/verify_quotes.py sources/<citekey>.md <extracted-text.txt>`. Fix anything NOT FOUND, or confirm it on the page image if the text layer is unreliable. Check `DIGITS?` results against the page image. `LOOSE` and `SPLIT` (a quote running across a page break or caption) are fine.
4. Report to the owner in a short message (about 300 words) covering what the source claims (four to eight attributed, located bullets), the authors' scope conditions, the three to five most important things to check (the page holds the rest), unknown metadata, and the wiki changes you propose (pages to create or update; at most five new pages without asking).
5. Run the reading interview for the remaining parts, with Relevance to my research last (read `questions/` first so the question can name their actual research question).
6. Update concept, method, entity and question pages with attributed, scoped, located entries. If a new entry contradicts an existing one, create or update a debate page instead of editing the older entry.
7. Bookkeeping (index, log, bibliography, status).

## 4. Quick mode

Do steps 2, 3, 6 and 7 with a lighter extract, one the owner can scan in two minutes. That means At a glance, Scope and caveats, three to six bullets per part, up to five key quotes, and up to five Things to check, with Mentions on one line. Spend the effort on correctness (numbers, locators, quotes), not coverage. A quick ingest of a 20-page paper should be a fraction of the work of a close one. In step 6, touch only pages that already exist plus at most two new ones, and list further candidates in your report. Write every reading part as an owed block with a pointed question. Report in a few lines what was filed and how many readings are owed.

## 5. The owner's own notes

- Create a page of `type: note` in `notes/`. Keep the text verbatim as a dated snapshot, with a link to the original (which may keep changing). Formatting can be converted to markdown, but the words don't change, including headings and emphasis.
- Run no reading interview, since the note already is the owner's reading. Ask at most two short questions. The first is whether the note is current, a draft, or superseded by something else. The second, only if part of it couldn't be read (a diagram, an attachment), asks the owner to share it. Propose links yourself rather than asking where they should go.
- Extract links, not facts. On concept, method, entity and question pages, add entries attributed to the owner and the note's date, phrased as what the note does ("Itay's note plans to use dung pellets as a multi-proxy for diet, vegetation and chronology"). Plans and ideas stay plans and ideas. They don't become findings on concept pages.
- Where the note makes empirical claims that sources in the wiki address, add a Things to check line on the note page linking the source with its locator. Never edit the note.
- If the note refers to parts you couldn't read, record that in Things to check as well as asking.

## 6. Concept, method and entity entries

- Use the entry format in page-formats. Name the source, its definition or claim (quoted where wording matters), the locator and the scope.
- Create a page only under Part 1 rule 7 (bears on the research questions, a second source, or the owner asks). Otherwise list the term under Mentions.
- New pages get an owed `My understanding` block with a question that relates the concept to the owner's research.

## 7. Contradictions and outdated sources

When a new source disagrees with something already in the wiki, or is newer evidence on the same point, don't edit the older extract and don't decide which is right. Create or update a debate page recording each position with its basis, scope and date, link it from both source pages, and add an owed `My position` block. Age is information, not a verdict. An old source can be outdated, or it can be the one that was right.
