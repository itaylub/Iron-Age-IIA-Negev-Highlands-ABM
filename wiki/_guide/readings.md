# Readings

Readings are the owner's own account of what a source, or a part of it, means, how good it is, and how it bears on their research. Agents never write them in the owner's name. Agents ask for them.

## Parts

| Source kind | Reading parts |
|---|---|
| Paper, chapter | Overall takeaway · Theoretical approach · Methodology · Results and evidence · Discussion and conclusions · Relevance to my research |
| Book, thesis | Overall takeaway · one part per chapter that matters (ask which) · Relevance to my research |
| Report (excavation, survey, grey literature) | Aims and scope · Methods and recording · Findings · Reliability and gaps · Relevance to my research |
| Dataset | What it measures · How it was produced · Coverage and resolution · Known problems · Relevance to my research |
| Web page, blog, talk | Overall takeaway · Reliability · Relevance to my research |
| Concept, method or entity page | My understanding |
| Debate page | My position |
| Model or code | Purpose (once, on the overview) · one My rationale per key mechanism |
| The owner's own notes | none, since the note is already theirs |

Skip parts the source doesn't have. A review paper has no methodology of its own, so write "review, no own methodology" in the extract rather than inventing one.

## Asking

- Take one part at a time, with one question per part. Keep it under about 35 words with a single question mark, so it can be answered in a line.
- Ground every question in something specific from the extract, with its locator. Aim it where the owner's judgement matters most, such as the evidence behind the main claim, a methodological choice that limits what the results can show, a term used differently elsewhere in the wiki, or a point touching the owner's research questions (read `questions/` first).
- Point at the spot, but leave the verdict to the owner. Don't build your own critique into the question ("…or do the gaps leave room for other paths?"), and don't offer "X or Y?" options where one of them is your view. An owner answering quickly will agree with whatever the question suggests, and then the reading is yours again.
  - Weak (vague): "What did you think of the methodology?"
  - Weak (leading): "Can three snapshots 500 and 1,600 years apart support a continuous contraction, or do the gaps leave room for other paths?"
  - Strong: "The curvature of each map is set from three snapshots, about 500 and 1,600 years apart (pp. 5, 8–9). How far does that carry their contraction claim?"
  - Strong, for relevance: "They argue manuring narrowed later options (p. 17). How does that compare with the case in your first research question?"
- If the owner has read the source, ask for the overall takeaway first, before showing your extract. A first impression stated before seeing a summary is the thing most worth capturing and the easiest to overwrite.
- In conversation, ask one question at a time, or a short numbered batch if the owner prefers. Don't bury questions under a long extract.

## Recording

- Write the answer under the part's heading in a reading block, signed with the owner's name and today's date (syntax in page-formats).
- Use the owner's words. Fix typos and obvious slips, and do nothing else. Don't expand, smooth, add hedges or citations, translate, or merge the answer with the extract. Keep the language they answered in.
- One line is a complete answer.
- If the answer contradicts the extract (they remember the source saying X, the extract has Y at p. N), point to the locator and ask once whether to amend either. Record what they decide.
- If they say skip, later, or don't answer, the block stays `· owed` with its question. Write questions that will still make sense months later without this conversation.

## Drafted readings

Draft only when the owner asks ("draft my reading of the methods"). Put the draft in a `**Claude's draft reading** · unreviewed, date` block next to the My reading block, which stays owed. If they approve it as is, replace the owed block with `**My reading** · Name, date (approved Claude draft)` holding the draft text, and remove the draft block. If they rewrite it, record their version and remove the draft. Drafts never count as readings.

## Keeping the pressure on

The owner asked to be pushed.

- End every close ingest with the interview unless the owner explicitly says skip. Quick ingests write owed blocks instead and say how many were added.
- The session-start brief lists owed readings with their questions.
- With five or more owed, offer one short reading session per session ("5 questions, about ten minutes?"). If they decline, leave it until the next session.
- When an answer depends on a part whose reading is owed, say so in one line.
- Don't moralise, and don't repeat reminders within a session.

## Reading sessions

Get the owed blocks with `python _tools/wiki_status.py . --json`, oldest first, or by source or question if the owner prefers. Ask one at a time, record, move on, and stop when told. Close with "N written, M still owed" and log the session.
