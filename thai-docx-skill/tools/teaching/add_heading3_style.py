#!/usr/bin/env python3
"""Promote level-3 subsections (N.N.N) to a real Heading3 style in a docx.

The pandoc-built book renders subsection titles like "5.1.1 ที่มาและประวัติของวิธี"
as plain Normal body paragraphs: 14pt, not bold, indistinguishable from the body
text around them. This:

  1. Registers a Word paragraph style "Heading3" (cloned from Heading2 but
     16pt / TH Sarabun New / bold / outlineLvl=2 / spacing 6pt-before 3pt-after),
     so the subsections show in the Navigation pane + any auto table of contents
     and the whole level restyles from one place.
  2. Re-tags every N.N.N body paragraph with that style and updates its inline
     runs (sz/szCs 28->32 = 14pt->16pt, add b/bCs bold) so the style's look
     actually wins over the existing inline run properties. Any justify
     (thaiDistribute) or first-line indent is stripped — a heading is left-set.

"Option A": 16pt bold, black, left-aligned. Ladder becomes
chapter 24 > section 18 > subsection 16 > body 14 (pt, Thai/szCs governed).

Pure string edit on document.xml + styles.xml (no XML parse) so namespace
prefixes, mc:Ignorable, equations, SEQ fields, ZWSP, bookmarks survive
byte-for-byte.

Usage: add_heading3_style.py <in.docx> <out.docx>
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path

HEADING3_STYLE = (
    '<w:style w:type="paragraph" w:styleId="Heading3">'
    '<w:name w:val="heading 3"/>'
    '<w:basedOn w:val="Normal"/>'
    '<w:next w:val="Normal"/>'
    '<w:qFormat/>'
    '<w:pPr><w:keepNext/><w:spacing w:before="120" w:after="60"/>'
    '<w:outlineLvl w:val="2"/></w:pPr>'
    '<w:rPr><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" w:cs="TH Sarabun New"/>'
    '<w:b/><w:bCs/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr>'
    '</w:style>'
)

# inline pPr bits to inject (pStyle first child, then spacing) — matches the
# CT_PPr child order (pStyle ... spacing ... jc ... rPr)
PPR_INJECT = '<w:pStyle w:val="Heading3"/><w:spacing w:before="120" w:after="60"/>'

L3_RE = re.compile(r"^\s*\d+\.\d+\.\d+(\s|$)")


def text_of(p):
    return "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)).replace("​", "")


def convert_para(p):
    """Return (new_para, changed) with Heading3 look applied to an N.N.N paragraph.

    Safe to re-run: if the paragraph is already tagged Heading3 we skip the
    structural injection but STILL re-assert 16pt+bold on the runs. That repairs
    the case where a later set_font_size 32->28 pass (part of the house-style
    chain) shrank the heading runs back to body size — without this, a second
    chain run would silently leave all Heading3 lines at 14pt.
    """
    already = '<w:pStyle w:val="Heading3"/>' in p
    before = p

    if not already:
        # 1. pStyle + spacing into the paragraph's own pPr (first <w:pPr>)
        if "<w:pPr>" in p:
            p = p.replace("<w:pPr>", "<w:pPr>" + PPR_INJECT, 1)
        else:
            open_end = p.find(">") + 1
            p = p[:open_end] + "<w:pPr>" + PPR_INJECT + "</w:pPr>" + p[open_end:]
        # 2. strip any justify + first-line indent (heading is left-set)
        p = re.sub(r'<w:jc w:val="[^"]*"\s*/>', "", p)
        p = re.sub(r"<w:ind\b[^>]*/>", "", p)

    # 3. resize 14pt -> 16pt on every run (and the paragraph mark)
    p = p.replace('<w:sz w:val="28"/>', '<w:sz w:val="32"/>')
    p = p.replace('<w:szCs w:val="28"/>', '<w:szCs w:val="32"/>')

    # 4. bold every run: add <w:b/><w:bCs/> after each rFonts not already bold
    p = re.sub(r"(<w:rFonts\b[^>]*/>)(?!<w:b/>)", r"\1<w:b/><w:bCs/>", p)

    return p, (p != before) or (not already)


def main():
    if len(sys.argv) != 3:
        print("usage: add_heading3_style.py <in.docx> <out.docx>", file=sys.stderr)
        sys.exit(2)
    sys.stdout.reconfigure(encoding="utf-8")
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])

    zin = zipfile.ZipFile(src)
    doc = zin.read("word/document.xml").decode("utf-8")
    styles = zin.read("word/styles.xml").decode("utf-8")

    # --- styles.xml: add Heading3 after the Heading2 block (idempotent) ---
    if 'w:styleId="Heading3"' not in styles:
        m = re.search(r'<w:style [^>]*w:styleId="Heading2".*?</w:style>', styles, re.DOTALL)
        if not m:
            print("ERROR: Heading2 style not found to anchor Heading3", file=sys.stderr)
            sys.exit(1)
        styles = styles[: m.end()] + HEADING3_STYLE + styles[m.end():]
        style_added = True
    else:
        style_added = False

    # --- document.xml: re-tag N.N.N paragraphs ---
    para_re = re.compile(r"<w:p\b.*?</w:p>", re.DOTALL)
    converted = []

    def repl(m):
        p = m.group(0)
        sm = re.search(r'<w:pStyle w:val="([^"]+)"', p)
        # leave other styled paragraphs (Heading1/2, captions, ...) alone; but
        # DO revisit paragraphs already tagged Heading3 so a re-run can repair
        # their font size (see convert_para docstring).
        if sm and sm.group(1) != "Heading3":
            return p
        if not L3_RE.match(text_of(p).strip()):
            return p
        new_p, changed = convert_para(p)
        if changed:
            converted.append(text_of(p).strip()[:55])
        return new_p

    new_doc = para_re.sub(repl, doc)

    tmp = dst.with_suffix(".docx.tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == "word/document.xml":
                data = new_doc.encode("utf-8")
            elif item.filename == "word/styles.xml":
                data = styles.encode("utf-8")
            else:
                data = zin.read(item.filename)
            zout.writestr(item, data)
    zin.close()
    if dst.exists():
        dst.unlink()
    shutil.move(str(tmp), str(dst))

    print(f"Heading3 style registered: {style_added}")
    print(f"N.N.N paragraphs promoted to Heading3: {len(converted)}")
    for t in converted:
        print(f"  {t}")
    print(f"output: {dst}  ({dst.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
