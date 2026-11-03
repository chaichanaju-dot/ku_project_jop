#!/usr/bin/env python3
"""Post-render polish for Thai academic .docx produced by thai-academic-docx skill.

Runs AFTER patch_seq.py. Applies two Thai-academic-house-style adjustments:

1. Body paragraphs use **justify** (`jc=both`) justification — spreads space
   between words to fill lines, standard for Thai engineering textbooks.
   The last line of each paragraph stays left-aligned (not stretched), and
   lines containing inline equations distribute space between words around
   the equation rather than stretching characters. This replaces an earlier
   `thaiDistribute` pass that caused weird character spacing on short last
   lines + lines with inline math (principal feedback 2026-05-20).

2. **Tables centered** with single-line borders on all sides + inside.

   Skipped (principal removed via Ctrl+A on smoke-test v2):
   - Table caption indent to align with centered table left edge
   - Figure paragraph center alignment
   - Image caption center alignment

Usage:
    py tools/teaching/post_render_thai.py <input.docx> <output.docx>

Env vars:
    BODY_JC — alignment for body paragraphs (default "both"; "thaiDistribute"
              or "" to disable body alignment patch)

Pure stdlib (zipfile + xml.etree). No deps.
"""

from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M_NS = "http://www.w3.org/1998/Math/MathML"  # not used; oMath ns is below
OMATH_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"

ET.register_namespace("w", W_NS)
ET.register_namespace("m", OMATH_NS)

W = lambda tag: f"{{{W_NS}}}{tag}"
OM = lambda tag: f"{{{OMATH_NS}}}{tag}"

# Heading / special styles that should NOT receive body-jc patch.
# Note: "FirstParagraph" intentionally NOT skipped — Pandoc applies it to the
# first body paragraph after each heading; in Thai textbook convention these
# should justify like any other body paragraph (caught by Pandoc 2026-05-21).
SKIP_STYLES = {
    "Heading1", "Heading2", "Heading3", "Heading4", "Heading5",
    "Title", "Subtitle", "TOC1", "TOC2", "TOC3",
    "TableCaption", "ImageCaption", "Caption",
    "Quote", "IntenseQuote",
}


def get_pstyle(p):
    """Return the pStyle val of paragraph p, or empty string."""
    pPr = p.find(W("pPr"))
    if pPr is None:
        return ""
    pStyle = pPr.find(W("pStyle"))
    if pStyle is None:
        return ""
    return pStyle.get(W("val"), "")


def get_or_create_pPr(p):
    """Return pPr for p, creating it as first child if absent."""
    pPr = p.find(W("pPr"))
    if pPr is None:
        pPr = ET.SubElement(p, W("pPr"))
        # Move pPr to first position
        p.remove(pPr)
        p.insert(0, pPr)
    return pPr


def set_jc(elem_pPr_or_tblPr, val):
    """Set <w:jc w:val='val'/> on a pPr or tblPr element (replace if present).

    OOXML schema requires pPr children in specific order. We append jc at the
    end — Word tolerates trailing position better than leading. (Earlier we
    prepended it which placed jc BEFORE pStyle, an invalid order that Word
    interpreted oddly — flagged as one root cause of river-of-white justify
    artifacts.)
    """
    existing = elem_pPr_or_tblPr.find(W("jc"))
    if existing is not None:
        elem_pPr_or_tblPr.remove(existing)
    jc = ET.SubElement(elem_pPr_or_tblPr, W("jc"))
    jc.set(W("val"), val)


def set_pPr_child(pPr, tag_local: str, val: str | None = None):
    """Set <w:{tag_local}/> or <w:{tag_local} w:val='val'/> in pPr (replace if present)."""
    existing = pPr.find(W(tag_local))
    if existing is not None:
        pPr.remove(existing)
    el = ET.SubElement(pPr, W(tag_local))
    if val is not None:
        el.set(W("val"), val)


def force_run_font(r, font_name: str):
    """Force a run's rFonts (ascii / hAnsi / cs) to a single font name.
    Creates rPr if absent; preserves other run properties.
    """
    rpr = r.find(W("rPr"))
    if rpr is None:
        rpr = ET.SubElement(r, W("rPr"))
        # rPr must come first in r
        r.remove(rpr)
        r.insert(0, rpr)
    rfonts = rpr.find(W("rFonts"))
    if rfonts is None:
        rfonts = ET.SubElement(rpr, W("rFonts"))
    rfonts.set(W("ascii"), font_name)
    rfonts.set(W("hAnsi"), font_name)
    rfonts.set(W("cs"), font_name)


def paragraph_contains_drawing(p):
    """Return True if paragraph contains <w:drawing> (a picture)."""
    for r in p.iter(W("r")):
        if r.find(W("drawing")) is not None:
            return True
    return False


def paragraph_is_display_equation(p):
    """Return True if paragraph's main content is a display oMath."""
    # Display equations from pandoc end up as <m:oMathPara>
    return p.find(OM("oMathPara")) is not None


def get_sect_pr(body):
    """Find sectPr inside body (usually last child or inside last paragraph)."""
    # First check body-level sectPr (last child)
    direct = body.find(W("sectPr"))
    if direct is not None:
        return direct
    # Otherwise inside the last paragraph's pPr
    for p in reversed(list(body.findall(W("p")))):
        pPr = p.find(W("pPr"))
        if pPr is not None:
            sp = pPr.find(W("sectPr"))
            if sp is not None:
                return sp
    return None


def compute_printable_width_dxa(sect_pr):
    """Compute printable width (page width minus left + right margin) in DXA (1/1440")."""
    if sect_pr is None:
        # Fallback: A4 portrait minus 1.25in left + 1in right margin
        # A4 = 8.27" x 11.69" → 11906 x 16838 dxa
        # Printable = 11906 - 1800 (1.25") - 1440 (1") = 8666 dxa
        return 8666
    pgSz = sect_pr.find(W("pgSz"))
    pgMar = sect_pr.find(W("pgMar"))
    page_w = int(pgSz.get(W("w"), "11906")) if pgSz is not None else 11906
    left = int(pgMar.get(W("left"), "1800")) if pgMar is not None else 1800
    right = int(pgMar.get(W("right"), "1440")) if pgMar is not None else 1440
    return page_w - left - right


def table_width_dxa(tbl):
    """Sum gridCol widths to get table total width in DXA."""
    tblGrid = tbl.find(W("tblGrid"))
    if tblGrid is None:
        return None
    total = 0
    for gc in tblGrid.findall(W("gridCol")):
        try:
            total += int(gc.get(W("w"), "0"))
        except ValueError:
            pass
    return total if total > 0 else None


def get_or_create_tblPr(tbl):
    """Return tblPr for table, creating as first child if absent."""
    tblPr = tbl.find(W("tblPr"))
    if tblPr is None:
        tblPr = ET.SubElement(tbl, W("tblPr"))
        tbl.remove(tblPr)
        tbl.insert(0, tblPr)
    return tblPr


def set_table_borders_single(tblPr):
    """Set all 6 borders (top/left/bottom/right/insideH/insideV) to single 4pt black."""
    existing = tblPr.find(W("tblBorders"))
    if existing is not None:
        tblPr.remove(existing)
    tblBorders = ET.SubElement(tblPr, W("tblBorders"))
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = ET.SubElement(tblBorders, W(side))
        b.set(W("val"), "single")
        b.set(W("sz"), "4")
        b.set(W("space"), "0")
        b.set(W("color"), "auto")


def set_left_indent(pPr, twips):
    """Set <w:ind w:left='twips'/> on pPr (replace if present)."""
    existing = pPr.find(W("ind"))
    if existing is not None:
        existing.set(W("left"), str(twips))
    else:
        ind = ET.SubElement(pPr, W("ind"))
        ind.set(W("left"), str(twips))


def patch_document_xml(xml_bytes: bytes) -> tuple[bytes, dict]:
    """Apply 3 polish passes to word/document.xml. Return (new_bytes, stats)."""

    # Parse with namespace awareness
    root = ET.fromstring(xml_bytes)
    body = root.find(W("body"))
    if body is None:
        raise RuntimeError("word/document.xml has no <w:body>")

    import os
    body_jc = os.environ.get("BODY_JC", "both")
    body_font = os.environ.get("BODY_FONT", "Cordia New")
    disable_autospace = os.environ.get("DISABLE_AUTOSPACE", "1") == "1"

    sect_pr = get_sect_pr(body)
    printable_w = compute_printable_width_dxa(sect_pr)

    stats = {
        "justified_paragraphs": 0,
        "autospace_disabled_paragraphs": 0,
        "font_forced_runs": 0,
        "centered_tables": 0,
        "bordered_tables": 0,
        "body_jc_value": body_jc or "(disabled)",
        "body_font": body_font or "(unchanged)",
        "disable_autospace": disable_autospace,
        "printable_width_dxa": printable_w,
    }

    # First pass: body-paragraph polish — applied to every paragraph that is
    # NOT a heading/caption/figure/equation/empty paragraph.
    # Three changes:
    #   (1) jc = both (justify) — body text alignment
    #   (2) autoSpaceDE=0 + autoSpaceDN=0 — disable East-Asian auto-spacing,
    #       which Word adds at Thai-Latin boundaries and causes "river-of-white"
    #       gaps when justify expands those auto-spaces (root cause of the
    #       artifact principal flagged 2026-05-21)
    #   (3) Force single-font rFonts on every run — Word renders Thai and
    #       Latin chars with different metrics when ascii/cs fonts differ
    #       (Normal style had ascii="Times New Roman" + cs="Angsana New"),
    #       which interacts with justify to make gaps look uneven. Forcing
    #       all chars to a single Thai-aware font (Cordia New default)
    #       gives uniform character widths → smoother justify.
    for p in body.iter(W("p")):
        pstyle = get_pstyle(p)

        if paragraph_contains_drawing(p):
            continue
        if pstyle in SKIP_STYLES:
            continue
        if paragraph_is_display_equation(p):
            continue
        text = "".join(t.text or "" for t in p.iter(W("t")))
        if not text.strip():
            continue

        pPr = get_or_create_pPr(p)

        if body_jc:
            # PRESERVE_EXISTING_JC=1 → only set jc if paragraph has none.
            # Useful when input already encodes proper alignment (e.g. docx-js
            # output marks display-equation paragraphs as centered and we
            # don't want post-render to overwrite them with justify).
            preserve = os.environ.get("PRESERVE_EXISTING_JC", "0") == "1"
            existing_jc = pPr.find(W("jc"))
            if preserve and existing_jc is not None:
                pass  # keep existing alignment
            else:
                set_jc(pPr, body_jc)
                stats["justified_paragraphs"] += 1

        if disable_autospace:
            set_pPr_child(pPr, "autoSpaceDE", "0")
            set_pPr_child(pPr, "autoSpaceDN", "0")
            stats["autospace_disabled_paragraphs"] += 1

        if body_font:
            for r in p.findall(W("r")):
                force_run_font(r, body_font)
                stats["font_forced_runs"] += 1

    # Second pass: table-level changes (center + borders)
    # Caption indent is intentionally skipped — principal removed it in Word
    # via Ctrl+A on smoke-test v2 (2026-05-20).
    for tbl in body.iter(W("tbl")):
        tblPr = get_or_create_tblPr(tbl)
        set_jc(tblPr, "center")
        stats["centered_tables"] += 1
        set_table_borders_single(tblPr)
        stats["bordered_tables"] += 1

    # Serialize back. Manually emit XML declaration with standalone="yes" to
    # match docx convention. ET.tostring does not accept `standalone` kwarg
    # across Python versions.
    body_bytes = ET.tostring(root, encoding="UTF-8")
    out = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n' + body_bytes
    return out, stats


def patch_docx(input_path: Path, output_path: Path) -> dict:
    """Read input docx, patch word/document.xml, write output docx."""
    if input_path.resolve() == output_path.resolve():
        raise RuntimeError("input and output paths must differ")
    shutil.copy2(input_path, output_path)
    stats = {}
    # Edit in place: zipfile cannot rewrite a single entry, so do read-then-rewrite
    tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    with zipfile.ZipFile(input_path, "r") as zin, zipfile.ZipFile(
        tmp_path, "w", zipfile.ZIP_DEFLATED
    ) as zout:
        for item in zin.namelist():
            data = zin.read(item)
            if item == "word/document.xml":
                data, stats = patch_document_xml(data)
            zout.writestr(item, data)
    shutil.move(str(tmp_path), str(output_path))
    return stats


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: post_render_thai.py <input.docx> <output.docx>",
            file=sys.stderr,
        )
        sys.exit(2)
    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    if not in_path.exists():
        print(f"Input not found: {in_path}", file=sys.stderr)
        sys.exit(1)
    stats = patch_docx(in_path, out_path)
    print("post_render_thai stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
