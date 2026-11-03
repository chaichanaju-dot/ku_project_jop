#!/usr/bin/env python3
"""Prepend an auto-updating "รูปที่ N.M" number to each figure caption in a docx.

Each figure in our pandoc-built book sits in its own paragraph (the <w:drawing>),
followed immediately by a centered Normal paragraph holding the descriptive
caption (no number). This injects, at the front of each caption paragraph:

    รูปที่ {chapter}.{SEQ Figure{chapter}}  <space>

The number-within-chapter is a Word SEQ field (auto-updates on F9 / print), and
each chapter uses its own SEQ name (Figure5, Figure6, ...) so numbering restarts
at 1 each chapter and renumbers correctly when figures are added/removed.

Chapter is tracked from the Heading1 paragraphs ("บทที่ 5", "บทที่ 6", ...).

Pure string editing on word/document.xml (no XML parse) so namespace prefixes,
mc:Ignorable, equations, ZWSP survive byte-for-byte.

Usage: add_figure_captions.py <in.docx> <out.docx>
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path


def main():
    if len(sys.argv) != 3:
        print("usage: add_figure_captions.py <in.docx> <out.docx>", file=sys.stderr)
        sys.exit(2)
    sys.stdout.reconfigure(encoding="utf-8")
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])

    zin = zipfile.ZipFile(src)
    doc = zin.read("word/document.xml").decode("utf-8")

    para_re = re.compile(r"<w:p\b.*?</w:p>", re.DOTALL)

    def text_of(p):
        return "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)).replace("​", "")

    def is_heading1(p):
        return '<w:pStyle w:val="Heading1"/>' in p or '<w:pStyle w:val="Heading1">' in p

    # First pass: classify each paragraph match
    matches = list(para_re.finditer(doc))
    cur_chapter = None
    per_ch_count = {}
    edits = []  # (start, end, new_text)

    for idx, m in enumerate(matches):
        p = m.group(0)
        if is_heading1(p):
            hm = re.search(r"บทที่\s*(\d+)", text_of(p))
            if hm:
                cur_chapter = int(hm.group(1))
            continue
        if "<w:drawing>" not in p:
            continue
        # caption = next paragraph
        if idx + 1 >= len(matches):
            continue
        cap_m = matches[idx + 1]
        cap = cap_m.group(0)
        if cur_chapter is None:
            continue
        if text_of(cap).lstrip().startswith("รูปที่"):
            continue  # idempotent: already numbered

        ch = cur_chapter
        per_ch_count[ch] = per_ch_count.get(ch, 0) + 1
        n = per_ch_count[ch]

        # reuse the caption's first run rPr for consistent font on the prefix
        rpr_m = re.search(r"<w:r\b[^>]*>(<w:rPr>.*?</w:rPr>)", cap, re.DOTALL)
        rpr = rpr_m.group(1) if rpr_m else ""

        seq_name = f"Figure{ch}"
        field = (
            f'<w:r>{rpr}<w:t xml:space="preserve">รูปที่ {ch}.</w:t></w:r>'
            f'<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            f'<w:r><w:instrText xml:space="preserve"> SEQ {seq_name} \\* ARABIC </w:instrText></w:r>'
            f'<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
            f'<w:r>{rpr}<w:t>{n}</w:t></w:r>'
            f'<w:r><w:fldChar w:fldCharType="end"/></w:r>'
            f'<w:r>{rpr}<w:t xml:space="preserve"> </w:t></w:r>'
        )

        # insert field right after the caption paragraph's </w:pPr> (or after the
        # opening <w:p ...> tag if no pPr), so the number leads the caption.
        ppr_end = cap.find("</w:pPr>")
        if ppr_end != -1:
            ins = ppr_end + len("</w:pPr>")
        else:
            ins = cap.find(">") + 1
        new_cap = cap[:ins] + field + cap[ins:]
        edits.append((cap_m.start(), cap_m.end(), new_cap))

    # apply edits from end → start
    new_doc = doc
    for start, end, new_cap in sorted(edits, key=lambda e: -e[0]):
        new_doc = new_doc[:start] + new_cap + new_doc[end:]

    tmp = dst.with_suffix(".docx.tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = new_doc.encode("utf-8") if item.filename == "word/document.xml" else zin.read(item.filename)
            zout.writestr(item, data)
    zin.close()
    if dst.exists():
        dst.unlink()
    shutil.move(str(tmp), str(dst))

    total = sum(per_ch_count.values())
    print(f"figure captions numbered: {total}")
    for ch in sorted(per_ch_count):
        print(f"  บทที่ {ch}: รูปที่ {ch}.1 .. {ch}.{per_ch_count[ch]}  (SEQ Figure{ch})")
    print(f"output: {dst}  ({dst.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
