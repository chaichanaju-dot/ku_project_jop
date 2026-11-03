#!/usr/bin/env python3
"""Insert one blank line (empty paragraph) below every figure caption in a docx.

"ใต้แคปชันรูปภาพ ให้เว้น 1 บรรทัด" — add a single blank paragraph after each
figure caption to separate it from the following body text.

Caption = the paragraph immediately after each <w:drawing> paragraph. We insert
an empty 14pt paragraph right after that caption (skipping if one is already
there, so re-running is safe).

Pure string edit on word/document.xml (no XML parse) so namespace prefixes,
mc:Ignorable, equations, SEQ fields, ZWSP survive byte-for-byte.

Usage: add_caption_spacing.py <in.docx> <out.docx>
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path

# minimal empty paragraph carrying a 14pt paragraph-mark (so the blank line is
# one body line tall)
BLANK_P = '<w:p><w:pPr><w:rPr><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr></w:pPr></w:p>'


def main():
    if len(sys.argv) != 3:
        print("usage: add_caption_spacing.py <in.docx> <out.docx>", file=sys.stderr)
        sys.exit(2)
    sys.stdout.reconfigure(encoding="utf-8")
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])

    zin = zipfile.ZipFile(src)
    doc = zin.read("word/document.xml").decode("utf-8")

    para_re = re.compile(r"<w:p\b.*?</w:p>", re.DOTALL)
    matches = list(para_re.finditer(doc))

    def text_of(p):
        return "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)).replace("​", "")

    def is_empty(p):
        return text_of(p).strip() == "" and "<w:drawing>" not in p

    inserts = []  # positions (end-of-caption) to insert a blank paragraph
    added = 0
    for idx, m in enumerate(matches):
        if "<w:drawing>" not in m.group(0):
            continue
        if idx + 1 >= len(matches):
            continue
        cap = matches[idx + 1]
        # idempotent: skip if paragraph after the caption is already blank
        if idx + 2 < len(matches) and is_empty(matches[idx + 2].group(0)):
            continue
        inserts.append(cap.end())
        added += 1

    new_doc = doc
    for pos in sorted(inserts, reverse=True):
        new_doc = new_doc[:pos] + BLANK_P + new_doc[pos:]

    tmp = dst.with_suffix(".docx.tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = new_doc.encode("utf-8") if item.filename == "word/document.xml" else zin.read(item.filename)
            zout.writestr(item, data)
    zin.close()
    if dst.exists():
        dst.unlink()
    shutil.move(str(tmp), str(dst))

    print(f"blank line inserted below figure captions: {added}")
    print(f"output: {dst}  ({dst.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
