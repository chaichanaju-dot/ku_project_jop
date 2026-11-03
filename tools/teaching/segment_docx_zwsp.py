#!/usr/bin/env python3
"""Put the zero-width spaces back into Thai prose that was written straight into a docx.

thaiDistribute justifies by spreading a line to the full measure. Thai has no spaces
between words, so unless the text carries U+200B break opportunities Word cannot wrap
mid-phrase and stretches the few gaps it has instead: "การกระจายของตัวอักษรแปลก ๆ",
as he put it. The book's original text came through the pandoc pipeline, which
segments with pythainlp; a paragraph typed in later by a tool does not, and stands out
on the page.

A paragraph qualifies when it is justified with thaiDistribute and holds a stretch of
Thai long enough that a line could not be broken inside it. That covers both a
paragraph written from scratch with no ZWSP at all and one where a sentence was
appended to text that had been segmented earlier: the run is re-segmented from
scratch, so a partly-segmented paragraph comes out whole rather than patched.

Only <w:t> runs are touched: <m:t> is equation text, and text inside <w:txbxContent>
or <w:tbl> belongs to artwork or a cell whose width is already fixed.

Usage: segment_docx_zwsp.py <in.docx> <out.docx> [--dry-run]
"""
from __future__ import annotations

import re
import shutil
import sys
import xml.dom.minidom as minidom
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from set_paragraph_text import paragraphs, text_of  # noqa: E402
from set_table_cells import spans  # noqa: E402

from pythainlp.tokenize import word_tokenize  # noqa: E402

ZWSP = "​"
WT = re.compile(r"(<w:t(?:\s[^>]*)?>)([^<]*)(</w:t>)")
# a stretch this long cannot be broken, so the line it lands on gets stretched instead
UNBREAKABLE = re.compile(r"[฀-๿’“”()]{25,}")
# a break opportunity between a consonant and the vowel or tone mark that sits on it
# detaches the mark on the page: สร้าง comes out as สร ้าง
COMBINING = "ั" + "".join(chr(c) for c in range(0x0E34, 0x0E3B)) + \
            "".join(chr(c) for c in range(0x0E47, 0x0E4F))
SPLIT_CLUSTER = re.compile(f"{ZWSP}+(?=[{COMBINING}])")


def is_thai(ch):
    return 0x0E00 <= ord(ch) < 0x0E80


def segment(text):
    """ZWSP between words of every Thai run in the text; other characters pass through."""
    out, buf = [], []
    for ch in text:
        if is_thai(ch):
            buf.append(ch)
        else:
            if buf:
                out.append(ZWSP.join(word_tokenize("".join(buf), engine="newmm")))
                buf = []
            out.append(ch)
    if buf:
        out.append(ZWSP.join(word_tokenize("".join(buf), engine="newmm")))
    return "".join(out)


def unsplit_clusters(doc):
    """Drop every break opportunity that sits between a consonant and its mark.

    The pipeline parks each ZWSP in a run of its own, so the offending pair is split
    across two elements and a plain regex over the text cannot see it. Walk the text
    runs in order instead: whenever a run's text opens with a combining mark, clear
    the ZWSP off the end of whatever came before it.
    """
    runs = list(re.finditer(r"(<w:t(?:\s[^>]*)?>)([^<]*)(</w:t>)", doc))
    texts = [m.group(2) for m in runs]
    drop = 0
    for n, t in enumerate(texts):
        if not t or t[0] not in COMBINING:
            continue
        for k in range(n - 1, -1, -1):          # step back over empty runs
            if texts[k] == "":
                continue
            if texts[k].endswith(ZWSP):
                texts[k] = texts[k].rstrip(ZWSP)
                drop += 1
            break
    if not drop:
        return doc, 0
    out, prev = [], 0
    for m, t in zip(runs, texts):
        if t == m.group(2):
            continue
        out.append(doc[prev:m.start()])
        sp = ' xml:space="preserve"' if t != t.strip() else ""
        out.append(f"<w:t{sp}>{t}</w:t>")
        prev = m.end()
    out.append(doc[prev:])
    return "".join(out), drop


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    dry = "--dry-run" in sys.argv
    zin = zipfile.ZipFile(src)
    doc = zin.read("word/document.xml").decode("utf-8")

    protected = []
    for tag in ("w:txbxContent", "w:tbl"):
        protected += list(spans(doc, tag))

    def inside(pos):
        return any(a <= pos < b for a, b in protected)

    doc, n_split = unsplit_clusters(doc)
    if n_split:
        print(f"  {n_split} break opportunities removed from inside a character cluster")

    out, prev, n_par, n_zwsp = [], 0, 0, 0
    for i, j in paragraphs(doc):
        if inside(i):
            continue
        para = doc[i:j]
        if 'w:val="thaiDistribute"' not in para:
            continue
        raw = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", para))
        if not UNBREAKABLE.search(raw):
            continue

        def fix(m):
            # the pandoc pipeline parks each ZWSP in a run of its own, so a run with
            # no Thai in it may be nothing but the break opportunity; stripping and
            # re-segmenting that run empties it and undoes the segmentation
            nonlocal n_zwsp
            text = m.group(2)
            if not any(is_thai(ch) for ch in text):
                return m.group(0)
            seg = segment(text.replace(ZWSP, ""))
            n_zwsp += seg.count(ZWSP)
            return m.group(1) + seg + m.group(3)

        fixed = WT.sub(fix, para)
        if fixed == para:
            continue
        out.append(doc[prev:i])
        out.append(fixed)
        prev = j
        n_par += 1
    out.append(doc[prev:])
    doc = "".join(out)

    doc, n_after = unsplit_clusters(doc)
    print(f"  {n_zwsp} break opportunities inserted across {n_par} paragraphs"
          + (f", {n_after} more removed from clusters" if n_after else ""))
    minidom.parseString(doc.encode("utf-8"))
    if dry:
        print("(dry run, nothing written)")
        return
    tmp = dst.with_suffix(".docx.tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = doc.encode("utf-8") if item.filename == "word/document.xml" else zin.read(item.filename)
            zout.writestr(item, data)
    zin.close()
    if dst.exists():
        dst.unlink()
    shutil.move(str(tmp), str(dst))
    print(f"output: {dst}  ({dst.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
