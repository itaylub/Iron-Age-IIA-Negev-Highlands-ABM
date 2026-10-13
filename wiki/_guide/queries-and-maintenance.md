# Queries, filed answers and health checks

## Answering questions from the wiki

1. Read index.md, open the relevant pages, and follow their links down to source pages.
2. Answer with links to wiki pages and source locators. Keep three things visibly apart: what sources say (attributed, located, with scope), what the owner has written (readings, notes), and your own inference (labelled as such).
3. If the answer leans on a source part whose reading is owed, say so in one line.
4. If the wiki doesn't cover something, say so. Knowledge from outside the wiki is labelled as such. It enters the wiki only through a source (ask for one), never as a bare claim.
5. When an answer took real work (a comparison, a timeline, a table), offer to file it as a synthesis. File it only if the owner says yes, as `status: unreviewed`.
6. Answers can be markdown, a table, or a chart or slide built from wiki content. The format follows the question.

## Health check (lint)

Run `python _tools/wiki_status.py .` and then read for what the script can't see:

- claims without locators, quotes not verified, source pages without a Scope and caveats section
- concept or debate entries that say more than their source extract (certainty upgraded, scope dropped)
- contradictions between entries that have no debate page yet
- terms that appear on two or more source pages without a page of their own, and pages that should merge
- syntheses, drafts or translations cited as evidence (laundering)
- older extracts that a later source updates (add a debate or a cross-link, but leave the older extract alone)
- sources with unknown metadata, and DOIs not verified

Fix mechanical problems directly and log them (links, index, bibliography, formatting, missing frontmatter). List interpretive problems for the owner and leave them alone. Finish by suggesting a few questions to pursue or sources to look for, if the check surfaced gaps.

## Filing back

A filed answer is a synthesis page. Every claim in it links to the page and locator it came from. It is never cited as evidence on concept or debate pages. When the owner reviews it, set `status: reviewed`, or turn their conclusions into their own reading or position blocks.
