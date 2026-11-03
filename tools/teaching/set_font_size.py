#!/usr/bin/env python3
"""Swap one run font-size to another throughout a docx (body text + math).

Targets run-level <w:sz>/<w:szCs> with a given half-point value and rewrites
them. Used to set body text + inline symbols + equations to 14pt: the Cordia
reference template renders body at 16pt (sz=32); the principal wants 14pt
(sz=28). Headings carry their own run sizes (40 = 20pt chapter, 36 = 18pt
section) so a targeted 32->28 swap leaves the heading hierarchy intact.

Math (OMML) runs carry the same w:sz/w:szCs, so they resize together with text.

Pure string edit on word/document.xml (no XML parse) so namespace prefixes,
mc:Ignorable, equations, ZWSP, SEQ fields survive byte-for-byte.

Usage: set_font_size.py <in.docx> <out.docx> <from_halfpt> <to_halfpt>
       (14pt = 28, 16pt = 32)
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path


def main():
    if len(sys.argv) != 5:
        print("usage: set_font_size.py <in.docx> <out.docx> <from_halfpt> <to_halfpt>", file=sys.stderr)
        sys.exit(2)
    sys.stdout.reconfigure(encoding="utf-8")
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    frm, to = sys.argv[3], sys.argv[4]

    zin = zipfile.ZipFile(src)
    doc = zin.read("word/document.xml").decode("utf-8")

    n_sz = len(re.findall(rf'<w:sz w:val="{frm}"\s*/>', doc))
    n_cs = len(re.findall(rf'<w:szCs w:val="{frm}"\s*/>', doc))

    doc = re.sub(rf'(<w:sz w:val=")({frm})("\s*/>)', rf'\g<1>{to}\g<3>', doc)
    doc = re.sub(rf'(<w:szCs w:val=")({frm})("\s*/>)', rf'\g<1>{to}\g<3>', doc)

    tmp = dst.with_suffix(".docx.tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = doc.encode("utf-8") if item.filename == "word/document.xml" else zin.read(item.filename)
            zout.writestr(item, data)
    zin.close()
    if dst.exists():
        dst.unlink()
    shutil.move(str(tmp), str(dst))

    fp_from, fp_to = int(frm) // 2, int(to) // 2
    print(f"font size {fp_from}pt -> {fp_to}pt (sz {frm}->{to}):")
    print(f"  w:sz runs changed   : {n_sz}")
    print(f"  w:szCs runs changed : {n_cs}")
    print(f"  output: {dst}  ({dst.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
