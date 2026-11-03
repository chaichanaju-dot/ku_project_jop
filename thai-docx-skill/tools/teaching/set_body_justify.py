#!/usr/bin/env python3
"""Put thaiDistribute justification on the body paragraphs of an existing docx.

segment_docx_zwsp.py only re-segments paragraphs that already carry
thaiDistribute, because that is the justification whose spacing the ZWSP is
there to feed. A docx that was typed straight into Word (a student's report, a
draft someone mailed in) has no thaiDistribute anywhere, so the segmenter finds
nothing to do and the house style never lands. This is the missing first step:
mark the body paragraphs, then segment them.

Body means prose the author wrote to be read across the measure. Headings keep
their own alignment, a paragraph deliberately centred or right-aligned keeps it,
figure paragraphs keep it, and anything inside a table or a textbox is left
alone - a cell's width is already fixed, which is the same line segment_docx_zwsp
draws.

Pure string edit on word/document.xml (no XML parse) so namespace prefixes,
mc:Ignorable, equations, SEQ fields, tracked revisions and existing ZWSP survive
byte-for-byte.

Usage: set_body_justify.py <in.docx> <out.docx> [--dry-run]
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

JC = '<w:jc w:val="thaiDistribute"/>'
# CT_PPr children that sort after w:jc; the new tag goes before the first one present
AFTER_JC = ("w:textDirection", "w:textAlignment", "w:textboxTightWrap", "w:outlineLvl",
            "w:divId", "w:cnfStyle", "w:rPr", "w:sectPr", "w:pPrChange")
# styles that own their alignment
NOT_BODY = re.compile(r'<w:pStyle w:val="(Heading\d|Title|Subtitle|Caption|TOC\d|Header|Footer)"')
KEEP_JC = re.compile(r'<w:jc w:val="(center|right|end)"')
PPR = re.compile(r"<w:pPr>(.*?)</w:pPr>", re.S)
MIN_CHARS = 20


def is_thai(ch):
    return 0x0E00 <= ord(ch) < 0x0E80


def set_jc(para: str) -> str:
    """Return the paragraph with thaiDistribute asserted in its pPr."""
    m = PPR.search(para)
    if not m:
        # no pPr at all: open one straight after the <w:p ...> tag
        opener = re.match(r"<w:p(?:\s[^>]*)?>", para)
        if not opener:
            return para
        return para[:opener.end()] + f"<w:pPr>{JC}</w:pPr>" + para[opener.end():]
    inner = m.group(1)
    if re.search(r"<w:jc\b[^>]*/>", inner):
        new_inner = re.sub(r"<w:jc\b[^>]*/>", JC, inner, count=1)
    else:
        cut = len(inner)
        for tag in AFTER_JC:
            t = re.search(rf"<{tag}\b", inner)
            if t and t.start() < cut:
                cut = t.start()
        new_inner = inner[:cut] + JC + inner[cut:]
    if new_inner == inner:
        return para
    return para[:m.start()] + f"<w:pPr>{new_inner}</w:pPr>" + para[m.end():]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 3:
        print("usage: set_body_justify.py <in.docx> <out.docx> [--dry-run]", file=sys.stderr)
        sys.exit(2)
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    dry = "--dry-run" in sys.argv
    zin = zipfile.ZipFile(src)
    doc = zin.read("word/document.xml").decode("utf-8")

    protected = []
    for tag in ("w:txbxContent", "w:tbl"):
        protected += list(spans(doc, tag))

    def inside(pos):
        return any(a <= pos < b for a, b in protected)

    out, prev, n_set, n_skip = [], 0, 0, 0
    for i, j in paragraphs(doc):
        if inside(i):
            continue
        para = doc[i:j]
        if NOT_BODY.search(para) or KEEP_JC.search(para) or "<w:drawing>" in para:
            n_skip += 1
            continue
        text = text_of(para)
        if len(text) < MIN_CHARS or not any(is_thai(c) for c in text):
            n_skip += 1
            continue
        fixed = set_jc(para)
        if fixed == para:
            continue
        out.append(doc[prev:i])
        out.append(fixed)
        prev = j
        n_set += 1
    out.append(doc[prev:])
    doc = "".join(out)

    print(f"  thaiDistribute set on {n_set} body paragraphs ({n_skip} left as they were)")
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
