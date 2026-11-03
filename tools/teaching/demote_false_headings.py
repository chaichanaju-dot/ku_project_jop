#!/usr/bin/env python3
"""Take the Heading style off paragraphs that are not headings.

add_heading3_style.py promotes a numbered subsection into a real Heading3. This
is the inverse, for a docx somebody wrote by hand: Word hands out Heading styles
whenever a paragraph is retyped near one, so a table cell, a figure caption or a
stray blank line ends up styled Heading2 or Heading3. Nothing looks wrong on the
page - the author overrides the bold and the size back to body - but every one of
them lands in the Navigation pane and in any automatic table of contents, and the
ladder that the house style is built on stops meaning anything.

A heading earns its style by being numbered: "บทที่ N" at Heading1, "N.N" at
Heading2, "N.N.N" at Heading3. A paragraph carrying the style without the number
loses the style and keeps everything else - alignment, run overrides, tracked
revisions - so it renders exactly as before and simply stops claiming to be a
heading. Nothing is promoted here; a real heading that was never styled is
add_heading3_style.py's job.

Pure string edit on word/document.xml (no XML parse) so namespace prefixes,
mc:Ignorable, equations, SEQ fields, tracked revisions and ZWSP survive
byte-for-byte.

Usage: demote_false_headings.py <in.docx> <out.docx> [--dry-run]
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

NUMBERED = {
    "Heading1": re.compile(r"^\s*บทที่\s*\d"),
    "Heading2": re.compile(r"^\s*\d+\.\d+\s"),
    "Heading3": re.compile(r"^\s*\d+\.\d+\.\d+\s"),
    "Heading4": re.compile(r"^\s*\d+\.\d+\.\d+\.\d+\s"),
}
PSTYLE = re.compile(r'<w:pStyle w:val="(Heading\d)"\s*/>')
# a heading takes the style's own alignment; an explicit left is noise from an editor
HEADING_JC = re.compile(r'(<w:pStyle w:val="Heading\d"\s*/>)<w:jc w:val="(?:left|start)"\s*/>')


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 3:
        print("usage: demote_false_headings.py <in.docx> <out.docx> [--dry-run]", file=sys.stderr)
        sys.exit(2)
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    dry = "--dry-run" in sys.argv
    zin = zipfile.ZipFile(src)
    doc = zin.read("word/document.xml").decode("utf-8")

    out, prev, demoted = [], 0, []
    for i, j in paragraphs(doc):
        para = doc[i:j]
        m = PSTYLE.search(para)
        if not m:
            continue
        level = m.group(1)
        rule = NUMBERED.get(level)
        if rule and rule.match(text_of(para)):
            continue
        out.append(doc[prev:i])
        out.append(para[:m.start()] + para[m.end():])
        prev = j
        demoted.append((level, text_of(para).strip()[:60]))
    out.append(doc[prev:])
    doc = "".join(out)

    doc, n_jc = HEADING_JC.subn(r"\1", doc)

    print(f"  {len(demoted)} paragraphs demoted to body")
    for level, text in demoted[:12]:
        print(f"    {level}: {text!r}" if text else f"    {level}: (blank)")
    if len(demoted) > 12:
        print(f"    ... and {len(demoted) - 12} more")
    if n_jc:
        print(f"  {n_jc} explicit left-alignments dropped from real headings")

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
