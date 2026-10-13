#!/usr/bin/env python3
"""verify_quotes.py - check that quotes on a wiki page appear in the source text.

Usage:
  python _tools/verify_quotes.py PAGE.md SOURCE.txt [MORE_SOURCE.txt ...]

Get SOURCE.txt with e.g.  pdftotext -layout source.pdf source.txt
Checks quotes written as
  > "quote" (p. 12)            blockquote line, straight or curly quotes
  ... \u201cquote\u201d (p. 12) ...    inline, curly quotes only
Quotes split at ellipses (... or \u2026) and [bracketed insertions]; each
segment of 12+ characters is checked.

Result per quote:
  EXACT      found after normalising case, whitespace, ligatures, quote marks
  LOOSE      found only when hyphens and spaces are ignored (line-break
             hyphenation); fine, but glance at it
  SPLIT      found in two pieces with other text between them, usually a
             page break, running footer or figure caption; fine
  DIGITS?    found only when digits are ignored. Either the quote's numbers
             are wrong or the PDF text layer garbles digits (common in Hebrew
             and Arabic PDFs). Check the numbers against the page image.
  NOT FOUND  not in the text. Fix the quote, or check the page image if the
             text layer is unreliable (scans, RTL legacy fonts).
Exit code 1 if anything is NOT FOUND.
"""
import re
import sys
import unicodedata
from pathlib import Path

BIDI = dict.fromkeys(map(ord, "\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069\u00ad\ufeff"), None)
QUOTES = str.maketrans({"\u201c": '"', "\u201d": '"', "\u201e": '"', "\u2018": "'", "\u2019": "'",
                        "\u05f4": '"', "\u05f3": "'", "\u00ab": '"', "\u00bb": '"'})
DASHES = str.maketrans({"\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-", "\u2014": "-", "\u2212": "-"})
BLOCK_RE = re.compile(r'^>\s*["\u201c\u201e\u00ab](.+)["\u201d\u00bb]\s*\((?:p|pp|PDF p|fig|table)\.?[^)]*\)', re.I)
INLINE_RE = re.compile(r"\u201c([^\u201d]{12,}?)\u201d\s*\((?:p|pp)\.", re.I)


def norm(s):
    s = unicodedata.normalize("NFKC", s).translate(BIDI).translate(QUOTES).translate(DASHES)
    s = re.sub(r"-\s*\n\s*", "-", s)          # keep hyphen, drop the line break
    s = re.sub(r"\s+", " ", s)
    return s.lower().strip()


def loose(s):
    return re.sub(r"[\s\-]+", "", s)


def nodigits(s):
    return re.sub(r"[\d\s\-.,()]+", "", s)


def split_match(n, src):
    """Quote found as two pieces (page break, footer or figure caption in between)."""
    words = n.split(" ")
    for k in range(3, len(words) - 2):
        a, b = " ".join(words[:k]), " ".join(words[k:])
        if len(a) >= 12 and len(b) >= 12 and a in src and b in src and src.find(a) < src.rfind(b):
            return True
    return False


def segments(q):
    parts = re.split(r"\.\.\.|\u2026|\[[^\]]*\]", q)
    return [p.strip(" ,;:") for p in parts if len(p.strip(" ,;:")) >= 12]


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    page = Path(sys.argv[1]).read_text(encoding="utf-8")
    src_raw = "\n".join(Path(p).read_text(encoding="utf-8", errors="replace") for p in sys.argv[2:])
    src = norm(src_raw)
    src_loose, src_nd = loose(src), nodigits(src)

    quotes = []
    for line in page.splitlines():
        m = BLOCK_RE.match(line.strip())
        if m:
            quotes.append(m.group(1))
            continue
        quotes.extend(INLINE_RE.findall(line))

    worst = {"EXACT": 0, "LOOSE": 1, "SPLIT": 1, "DIGITS?": 2, "NOT FOUND": 3}
    counts = {k: 0 for k in worst}
    for q in quotes:
        segs = segments(q) or [q]
        status = "EXACT"
        for seg in segs:
            n = norm(seg)
            if n in src:
                s = "EXACT"
            elif loose(n) in src_loose:
                s = "LOOSE"
            elif split_match(n, src):
                s = "SPLIT"
            elif nodigits(n) and nodigits(n) in src_nd:
                s = "DIGITS?"
            else:
                s = "NOT FOUND"
            if worst[s] > worst[status]:
                status = s
        counts[status] += 1
        short = q if len(q) <= 90 else q[:87] + "..."
        print(f"{status:9}  {short}")
    print(f"\n{len(quotes)} quotes: " + ", ".join(f"{k} {v}" for k, v in counts.items() if v))
    if not quotes:
        print("No quotes found. Expected  > \"quote\" (p. N)  or inline \u201cquote\u201d (p. N).")
    sys.exit(1 if counts["NOT FOUND"] else 0)


if __name__ == "__main__":
    main()
