#!/usr/bin/env python3
"""Rewrite the cells of a Word table by row, without disturbing anything else.

The document-wide find/replace in replace_math_text.py is the wrong instrument for
a moment-distribution table: cell values repeat ("+3.6" occurs in half the rows), a
row's cells are separate <w:tc> elements whose text only looks contiguous once
extracted, and an edit that straddles two cells has no way to know where the
boundary was. This addresses cells positionally instead, which is how a table is
actually read.

Each target names the table by a string only that table contains, the row by index,
and asserts the row's current first cell before touching it. A cell's new text goes
into its first <w:t>, the rest are blanked; a cell that has no run yet borrows one
from a sibling so it inherits the row's formatting.

Usage: set_table_cells.py <in.docx> <out.docx> <spec.json> [--dry-run]
    spec.json: [{"marker": "...", "row": 11, "expect": "Final M_O",
                 "cells": ["Final M_O", "-12.0", null, ...]}, ...]   null = keep
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import xml.dom.minidom as minidom
import zipfile
from pathlib import Path

ZWSP = "​"


def spans(s: str, tag: str):
    """(start, end) of every balanced <tag …>…</tag>, attributes allowed."""
    # self-closing <tag .../> is an empty element, never the start of a span
    op = re.compile(rf"<{tag}(?:\s[^>]*[^/])?>")
    cl = f"</{tag}>"
    i = 0
    while True:
        m = op.search(s, i)
        if not m:
            return
        depth, j = 0, m.end()
        while True:
            o = op.search(s, j)
            c = s.find(cl, j)
            if c < 0:
                return
            if o and o.start() < c:
                depth += 1
                j = o.end()
            elif depth:
                depth -= 1
                j = c + len(cl)
            else:
                j = c + len(cl)
                break
        yield m.start(), j
        i = j


def text_of(frag: str) -> str:
    s = "".join(re.findall(r"<[wm]:t[^>]*>([^<]*)</[wm]:t>", frag)).replace(ZWSP, "")
    for ent, ch in (("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'),
                    ("&apos;", "'"), ("&amp;", "&")):
        s = s.replace(ent, ch)
    return s


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def set_cell(cell: str, new: str, donor: str) -> str:
    """Put `new` in the cell's first text run and empty the others."""
    runs = list(re.finditer(r"<([wm]):t[^>]*>([^<]*)</\1:t>", cell))
    if not runs:
        if not donor:
            raise SystemExit("empty cell and no donor run to copy formatting from")
        end = cell.rfind("</w:p>")
        if end < 0:
            raise SystemExit("cell has no paragraph to insert into")
        run = re.sub(r"<w:t[^>]*>[^<]*</w:t>",
                     lambda _: f"<w:t>{esc(new)}</w:t>", donor, count=1)
        return cell[:end] + run + cell[end:]
    out, prev = [], 0
    for n, m in enumerate(runs):
        out.append(cell[prev:m.start()])
        body = esc(new) if n == 0 else ""
        sp = ' xml:space="preserve"' if body != body.strip() else ""
        out.append(f"<{m.group(1)}:t{sp}>{body}</{m.group(1)}:t>")
        prev = m.end()
    out.append(cell[prev:])
    return "".join(out)


def donor_run(row: str) -> str:
    """A run element from this row, retexted empty, to seed a cell that has none.

    Taken from a data cell rather than the row label, so a value written into a
    previously empty cell is set like the values beside it and not like the caption.
    """
    cells = [row[a:b] for a, b in spans(row, "w:tc")]
    pat = re.compile(r"<w:r(?:\s[^>]*)?>(?:(?!</w:r>).)*?<w:t[^>]*>[^<]*</w:t>.*?</w:r>", re.S)
    for cell in cells[1:] + cells[:1]:
        m = pat.search(cell)
        if m:
            return re.sub(r"<w:t[^>]*>[^<]*</w:t>", "<w:t></w:t>", m.group(0), count=1)
    return ""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    sys.stdout.reconfigure(encoding="utf-8")
    src, dst, spec = Path(args[0]), Path(args[1]), Path(args[2])
    targets = json.loads(spec.read_text(encoding="utf-8"))

    zin = zipfile.ZipFile(src)
    doc = zin.read("word/document.xml").decode("utf-8")

    for t in targets:
        tables = [(i, j) for i, j in spans(doc, "w:tbl") if t["marker"] in text_of(doc[i:j])]
        if len(tables) != 1:
            raise SystemExit(f"[{len(tables)} tables] marker {t['marker']!r}")
        ti, tj = tables[0]
        table = doc[ti:tj]
        rows = list(spans(table, "w:tr"))
        if t.get("delete"):
            doc = doc[:ti] + doc[tj:]
            print(f"  deleted table {t['marker'][:44]!r} ({len(rows)} rows)")
            continue
        if "clone_row" in t:
            a, b = rows[t["clone_row"]]
            model = table[a:b]
            cells = list(spans(model, "w:tc"))
            donor = donor_run(model)
            out, prev = [], 0
            for (ca, cb), new in zip(cells, t["cells"]):
                out.append(model[prev:ca])
                out.append(model[ca:cb] if new is None else set_cell(model[ca:cb], new, donor))
                prev = cb
            out.append(model[prev:])
            at = rows[t.get("after", len(rows) - 1)][1]
            table = table[:at] + "".join(out) + table[at:]
            doc = doc[:ti] + table + doc[tj:]
            print(f"  added row to {t['marker'][:36]!r}: {t['cells']}")
            continue
        ri, rj = rows[t["row"]]
        row = table[ri:rj]
        cells = list(spans(row, "w:tc"))
        first = text_of(row[cells[0][0]:cells[0][1]])
        if first != t["expect"]:
            raise SystemExit(f"row {t['row']} starts with {first!r}, expected {t['expect']!r}")
        if len(t["cells"]) != len(cells):
            raise SystemExit(f"row {t['row']} has {len(cells)} cells, spec gives {len(t['cells'])}")
        donor = donor_run(row)
        out, prev = [], 0
        for (a, b), new in zip(cells, t["cells"]):
            out.append(row[prev:a])
            out.append(row[a:b] if new is None else set_cell(row[a:b], new, donor))
            prev = b
        out.append(row[prev:])
        table = table[:ri] + "".join(out) + table[rj:]
        doc = doc[:ti] + table + doc[tj:]
        print(f"  row {t['row']:>2} of {t['marker'][:34]!r:38} -> {t['cells']}")

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
