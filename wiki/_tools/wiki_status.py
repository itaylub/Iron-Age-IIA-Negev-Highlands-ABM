#!/usr/bin/env python3
"""wiki_status.py - to-do and health report for a research wiki.

Usage:
  python _tools/wiki_status.py [WIKI_ROOT] [--brief] [--json]

Reports readings owed, unreviewed drafts / translations / syntheses, open
debates, metadata to confirm, broken links, orphan pages, pages missing from
index.md, and source pages missing a citekey or BibTeX entry.
Standard library only; runs on Windows, macOS and Linux.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT_FILES = {"agents.md", "claude.md", "gemini.md", "index.md", "log.md"}
SKIP_DIRS = {"_tools", "_guide", ".git", ".obsidian", "node_modules", "__pycache__"}
READING_RE = re.compile(
    r"^\*\*(My (?:reading|rationale|understanding|position))\*\*\s*[\u00b7\-\u2013\u2014]\s*(.+?)\s*$")
DRAFT_RE = re.compile(
    r"^\*\*Claude's draft (?:reading|rationale|understanding|position)\*\*\s*[\u00b7\-\u2013\u2014]\s*unreviewed",
    re.I)
TRANS_RE = re.compile(r"\*Translation \(Claude, unreviewed\)", re.I)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(\s*<?([^)>\s]+)>?(?:\s+\"[^\"]*\")?\s*\)")
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")
BIB_KEY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,")


def parse_frontmatter(text):
    """Minimal YAML frontmatter reader: scalars, inline lists, block lists."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip("\n")
    body = text[end + 4:]
    data, key = {}, None
    for line in block.split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1] in (" ", "\t") and key:
            item = line.strip()
            if item.startswith("- "):
                if not isinstance(data.get(key), list):
                    data[key] = []
                data[key].append(item[2:].strip().strip("\"'"))
            continue
        m = re.match(r"^([A-Za-z0-9_\-]+):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if "#" in val and not val.startswith(("\"", "'")):
            val = val.split(" #")[0].strip()
        if val.startswith("[") and val.endswith("]"):
            data[key] = [v.strip().strip("\"'") for v in val[1:-1].split(",") if v.strip()]
        else:
            data[key] = val.strip("\"'")
    return data, body


def iter_pages(root):
    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts[:-1]):
            continue
        yield p, rel


def resolve_link(page, target, root):
    target = target.split("#")[0].split("?")[0]
    if not target or re.match(r"^[a-z]+:", target, re.I) and not re.match(r"^[a-z]:[\\/]", target, re.I):
        return None  # http:, mailto:, file: etc.
    if not target.lower().endswith(".md"):
        return None  # only check links to wiki pages
    path = Path(target)
    if not path.is_absolute():
        path = (page.parent / path)
    try:
        return path.resolve()
    except OSError:
        return path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--brief", action="store_true", help="short session-start summary")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    root = Path(args.root).resolve()
    if not (root / "AGENTS.md").exists():
        print(f"warning: no AGENTS.md in {root} - is this a wiki root?", file=sys.stderr)

    wiki_name = root.name
    agents = root / "AGENTS.md"
    if agents.exists():
        for line in agents.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"^#\s+AGENTS\.md\s*[\u2014\-:]\s*(.+)$", line)
            if m:
                wiki_name = m.group(1).strip()
                break

    bib_keys = set()
    bib = root / "references.bib"
    if bib.exists():
        bib_keys = set(BIB_KEY_RE.findall(bib.read_text(encoding="utf-8", errors="replace")))

    pages, inbound, broken, wikilinks = {}, {}, [], []
    owed, drafts, translations, debates, syntheses, unknown_meta, source_issues = [], [], [], [], [], [], []
    index_targets = set()

    for path, rel in iter_pages(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        fm, body = parse_frontmatter(text)
        rel_s = rel.as_posix()
        is_root_file = len(rel.parts) == 1 and rel.name.lower() in ROOT_FILES
        pages[path.resolve()] = (rel_s, fm, is_root_file)

        # readings, drafts, translations (root files only describe the syntax)
        heading_stack = {}
        lines = [] if is_root_file else body.splitlines()
        for i, line in enumerate(lines):
            hm = HEADING_RE.match(line)
            if hm:
                level = len(hm.group(1))
                heading_stack = {k: v for k, v in heading_stack.items() if k < level}
                heading_stack[level] = hm.group(2)
                continue
            rm = READING_RE.match(line.strip())
            if rm:
                status = rm.group(2)
                if status.lower().startswith("owed"):
                    q = ""
                    for nxt in lines[i + 1:i + 4]:
                        s = nxt.strip()
                        if s.startswith(">"):
                            q = re.sub(r"^>\s*(Q:)?\s*", "", s)
                            break
                        if s:
                            break
                    part = " \u203a ".join(heading_stack[k] for k in sorted(heading_stack)[1:]) or \
                        (heading_stack[min(heading_stack)] if heading_stack else "")
                    owed.append({"page": rel_s, "part": part, "kind": rm.group(1),
                                 "question": q, "since": fm.get("ingested") or fm.get("created") or ""})
                continue
            if DRAFT_RE.match(line.strip()):
                drafts.append(rel_s)
        n_tr = 0 if is_root_file else len(TRANS_RE.findall(body))
        if n_tr:
            translations.append((rel_s, n_tr))

        ptype = (fm.get("type") or "").lower()
        if ptype == "debate" and fm.get("status", "open").lower() != "settled-by-user":
            title = next((l[2:].strip() for l in lines if l.startswith("# ")), rel_s)
            debates.append({"page": rel_s, "title": title})
        if ptype == "synthesis" and fm.get("status", "unreviewed").lower() == "unreviewed":
            syntheses.append(rel_s)
        for k, v in fm.items():
            if isinstance(v, str) and v.strip().lower() in ("unknown", "tbd", "?"):
                unknown_meta.append(f"{rel_s}: {k}")
        if ptype == "source":
            key = fm.get("citekey", "")
            if not key:
                source_issues.append(f"{rel_s}: no citekey")
            elif bib.exists() and key not in bib_keys:
                source_issues.append(f"{rel_s}: citekey '{key}' not in references.bib")

        # links
        for target in LINK_RE.findall(body):
            res = resolve_link(path, target, root)
            if res is None:
                continue
            if rel_s.lower() == "index.md":
                index_targets.add(res)
            if not res.exists():
                broken.append(f"{rel_s} -> {target}")
            elif not is_root_file:
                inbound.setdefault(res, set()).add(rel_s)
        for w in WIKILINK_RE.findall(body):
            wikilinks.append(f"{rel_s}: [[{w}]]")

    content_pages = [(p, v) for p, v in pages.items() if not v[2]]
    orphans = sorted(v[0] for p, v in content_pages
                     if not (inbound.get(p, set()) - {v[0]}) and v[1].get("type", "").lower() != "question")
    not_indexed = sorted(v[0] for p, v in content_pages if p not in index_targets)
    n_sources = sum(1 for _, v in content_pages if v[1].get("type", "").lower() == "source")
    owed.sort(key=lambda o: (o["since"] or "9999", o["page"]))

    report = {
        "wiki": wiki_name, "root": str(root), "pages": len(content_pages), "sources": n_sources,
        "readings_owed": owed, "draft_readings_unreviewed": drafts,
        "translations_unreviewed": [{"page": p, "count": n} for p, n in translations],
        "syntheses_unreviewed": syntheses, "open_debates": debates,
        "metadata_to_confirm": unknown_meta, "source_issues": source_issues,
        "broken_links": broken, "orphans": orphans, "not_in_index": not_indexed,
        "wikilinks_used": wikilinks,
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    n_tr = sum(n for _, n in translations)
    if args.brief:
        print(f"{wiki_name}: {len(content_pages)} pages, {n_sources} sources")
        if owed:
            print(f"Readings owed: {len(owed)}")
            for o in owed[:3]:
                q = f" - {o['question']}" if o["question"] else ""
                print(f"  \u2022 {Path(o['page']).stem} \u203a {o['part']}{q}")
        else:
            print("Readings owed: none")
        print(f"Unreviewed: {len(drafts)} draft readings, {n_tr} translations, {len(syntheses)} syntheses"
              f" | open debates: {len(debates)}")
        issues = len(broken) + len(source_issues) + len(unknown_meta)
        if issues or orphans or not_indexed:
            print(f"Housekeeping: {len(broken)} broken links, {len(orphans)} orphans, "
                  f"{len(not_indexed)} not in index, {len(unknown_meta)} metadata to confirm, "
                  f"{len(source_issues)} bibliography issues")
        return

    def section(title, items, fmt=str):
        print(f"\n## {title} ({len(items)})")
        for it in items:
            print(f"- {fmt(it)}")

    print(f"# Wiki status: {wiki_name}\n{root}\n{len(content_pages)} pages, {n_sources} sources")
    section("Readings owed", owed,
            lambda o: f"{o['page']} \u203a {o['part']} [{o['kind']}]" + (f"\n  Q: {o['question']}" if o['question'] else ""))
    section("Unreviewed draft readings", drafts)
    section("Unreviewed translations", [f"{p} ({n})" for p, n in translations])
    section("Unreviewed syntheses", syntheses)
    section("Open debates", debates, lambda d: f"{d['page']} - {d['title']}")
    section("Metadata to confirm", unknown_meta)
    section("Bibliography issues", source_issues)
    section("Broken links", broken)
    section("Orphans (no inbound links except index/log)", orphans)
    section("Not in index.md", not_indexed)
    if wikilinks:
        section("[[wikilinks]] used (convention is relative markdown links)", wikilinks)


if __name__ == "__main__":
    main()
