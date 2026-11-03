#!/usr/bin/env python3
"""Center every figure and its caption on the page in a docx.

"จัดทุกแคปชัน+รูปภาพ ให้อยู่กึ่งกลางหน้ากระดาษ" — set <w:jc w:val="center"/> on
both (a) every paragraph that holds a <w:drawing> (the figure) and (b) the
caption paragraph that follows it (the one starting "รูปที่ N.M"). Inline
images center horizontally when their paragraph is centered, so this is the
right mechanism.

OOXML pPr child order puts w:jc before w:rPr (rPr is the last child of pPr), so
we insert the jc immediately before <w:rPr>. If a paragraph already carries a
jc, we rewrite its value to center (idempotent / safe to re-run).

Pure string edit on word/document.xml (no XML parse) so namespace prefixes,
mc:Ignorable, equations, SEQ fields, ZWSP survive byte-for-byte.

Usage: center_figures_captions.py <in.docx> <out.docx>
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path

JC_CENTER = '<w:jc w:val="center"/>'


def text_of(p):
    return "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)).replace("​", "")


def set_center(p):
    """Return paragraph p with its pPr jc forced to center. Adds a pPr if none."""
    # already centered?
    if re.search(r'<w:jc w:val="center"\s*/>', p):
        return p, False
    # existing jc with a different value -> rewrite to center
    if re.search(r"<w:jc\b[^>]*/>", p):
        return re.sub(r"<w:jc\b[^>]*/>", JC_CENTER, p, count=1), True
    # has a pPr but no jc -> insert before <w:rPr> if present, else at pPr end
    m = re.search(r"<w:pPr>(.*?)</w:pPr>", p, re.DOTALL)
    if m:
        inner = m.group(1)
        rpr = re.search(r"<w:rPr>", inner)
        if rpr:
            new_inner = inner[: rpr.start()] + JC_CENTER + inner[rpr.start():]
        else:
            new_inner = inner + JC_CENTER
        return p[: m.start(1)] + new_inner + p[m.end(1):], True
    # no pPr at all -> add one right after the opening <w:p ...> tag
    open_end = p.find(">") + 1
    return p[:open_end] + f"<w:pPr>{JC_CENTER}</w:pPr>" + p[open_end:], True


def main():
    if len(sys.argv) != 3:
        print("usage: center_figures_captions.py <in.docx> <out.docx>", file=sys.stderr)
        sys.exit(2)
    sys.stdout.reconfigure(encoding="utf-8")
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])

    zin = zipfile.ZipFile(src)
    doc = zin.read("word/document.xml").decode("utf-8")

    para_re = re.compile(r"<w:p\b.*?</w:p>", re.DOTALL)
    matches = list(para_re.finditer(doc))

    edits = []  # (start, end, new_text)
    fig_centered = 0
    cap_centered = 0
    cap_missing = 0

    for idx, m in enumerate(matches):
        p = m.group(0)
        if "<w:drawing>" not in p:
            continue
        new_p, changed = set_center(p)
        if changed:
            fig_centered += 1
        edits.append((m.start(), m.end(), new_p))
        # caption = next paragraph (must start with "รูปที่")
        if idx + 1 < len(matches):
            cap_m = matches[idx + 1]
            cap = cap_m.group(0)
            if text_of(cap).lstrip().startswith("รูปที่"):
                new_cap, cap_changed = set_center(cap)
                if cap_changed:
                    cap_centered += 1
                edits.append((cap_m.start(), cap_m.end(), new_cap))
            else:
                cap_missing += 1

    # apply edits from end -> start so positions stay valid
    new_doc = doc
    for start, end, txt in sorted(edits, key=lambda e: -e[0]):
        new_doc = new_doc[:start] + txt + new_doc[end:]

    tmp = dst.with_suffix(".docx.tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = new_doc.encode("utf-8") if item.filename == "word/document.xml" else zin.read(item.filename)
            zout.writestr(item, data)
    zin.close()
    if dst.exists():
        dst.unlink()
    shutil.move(str(tmp), str(dst))

    print("center figures + captions:")
    print(f"  figures centered : {fig_centered}")
    print(f"  captions centered: {cap_centered}")
    if cap_missing:
        print(f"  drawings whose next para is NOT a รูปที่ caption: {cap_missing}")
    print(f"  output: {dst}  ({dst.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
