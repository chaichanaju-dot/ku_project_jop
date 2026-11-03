#!/usr/bin/env python3
"""Stop Word from underlining Thai text as misspelled, document-wide.

The ZWSP we inject between Thai words (so `thaiDistribute` justify spreads space
at word edges) also makes Word's spell checker read every Thai word as a
misspelling, so the whole document renders with red squiggles while editing.
The old workaround was a manual Google Docs round-trip. This removes the need:
set `noProof` + Thai `lang` on the document's DEFAULT run properties, so nothing
is proofed in the first place.

Borrowed from tools/thai_office_doc/build_thai_office_doc.py (which shipped this
fix first), with one addition: our pandoc-built books already carry a
`<w:lang w:val="en-US" .../>` in docDefaults, so we REPLACE that tag rather than
inject a second one (two w:lang in one rPr is invalid).

The red squiggles never printed anyway; this is about the editing experience.

Pure string edit on word/styles.xml (no XML parse) so namespace prefixes,
mc:Ignorable, equations, SEQ fields and ZWSP survive byte-for-byte.

Usage: suppress_thai_proofing.py <in.docx> <out.docx>
"""
import re
import shutil
import sys
import xml.dom.minidom as minidom
import zipfile
from pathlib import Path

LANG = '<w:lang w:val="th-TH" w:eastAsia="th-TH" w:bidi="th-TH"/>'
NOPROOF = "<w:noProof/>"


def patch_default_rpr(rpr_inner):
    """Return (new_inner, changed) with noProof + Thai lang asserted."""
    before = rpr_inner
    # noProof goes after rFonts per the CT_RPr child order
    if NOPROOF not in rpr_inner:
        m = re.search(r"<w:rFonts\b[^>]*/>", rpr_inner)
        if m:
            rpr_inner = rpr_inner[: m.end()] + NOPROOF + rpr_inner[m.end():]
        else:
            rpr_inner = NOPROOF + rpr_inner
    # lang is near the end of the order; replace an existing one in place
    if re.search(r"<w:lang\b[^>]*/>", rpr_inner):
        rpr_inner = re.sub(r"<w:lang\b[^>]*/>", LANG, rpr_inner, count=1)
    else:
        rpr_inner = rpr_inner + LANG
    return rpr_inner, rpr_inner != before


def main():
    if len(sys.argv) != 3:
        print("usage: suppress_thai_proofing.py <in.docx> <out.docx>", file=sys.stderr)
        sys.exit(2)
    sys.stdout.reconfigure(encoding="utf-8")
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])

    zin = zipfile.ZipFile(src)
    styles = zin.read("word/styles.xml").decode("utf-8")

    changed = False
    m = re.search(r"<w:rPrDefault>\s*<w:rPr>(.*?)</w:rPr>\s*</w:rPrDefault>", styles, re.DOTALL)
    if m:
        new_inner, changed = patch_default_rpr(m.group(1))
        styles = styles[: m.start(1)] + new_inner + styles[m.end(1):]
    else:
        # empty or absent default rPr: build one
        block = f"<w:rPrDefault><w:rPr>{NOPROOF}{LANG}</w:rPr></w:rPrDefault>"
        m2 = re.search(r"<w:rPrDefault>\s*<w:rPr\s*/>\s*</w:rPrDefault>", styles)
        if m2:
            styles = styles[: m2.start()] + block + styles[m2.end():]
            changed = True
        else:
            m3 = re.search(r"<w:docDefaults>", styles)
            if not m3:
                print("ERROR: styles.xml has no <w:docDefaults>", file=sys.stderr)
                sys.exit(1)
            styles = styles[: m3.end()] + block + styles[m3.end():]
            changed = True

    minidom.parseString(styles.encode("utf-8"))  # well-formed or raise

    tmp = dst.with_suffix(".docx.tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = styles.encode("utf-8") if item.filename == "word/styles.xml" else zin.read(item.filename)
            zout.writestr(item, data)
    zin.close()
    if dst.exists():
        dst.unlink()
    shutil.move(str(tmp), str(dst))

    print("Thai proofing suppressed (docDefaults noProof + lang th-TH):")
    print(f"  styles.xml changed : {changed}")
    print(f"  output: {dst}  ({dst.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
