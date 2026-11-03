#!/usr/bin/env python3
"""Strip orphan media from a docx (in-place).

pandoc --reference-doc carries ALL media from the reference docx into the
output, even media our content never references (e.g. อ.ธิดารัตน์'s 232 WMF
equation images + 2 EMF from Ch2). They're invisible but bloat the file.

This removes image media whose relationship Id is NOT referenced anywhere in
word/document.xml, AND removes the matching relationship entry (so no dangling
rel → no Word "repair" prompt). Referenced media (our figures) are kept.

Usage: strip_orphan_media.py <file.docx>
"""
import re
import sys
import zipfile
import shutil
from pathlib import Path

if len(sys.argv) != 2:
    print("usage: strip_orphan_media.py <file.docx>", file=sys.stderr)
    sys.exit(2)

sys.stdout.reconfigure(encoding="utf-8")
path = Path(sys.argv[1])

zin = zipfile.ZipFile(path)
doc = zin.read("word/document.xml").decode("utf-8")
rels_name = "word/_rels/document.xml.rels"
rels = zin.read(rels_name).decode("utf-8")

# rIds referenced anywhere in the document body (embed="rIdN", r:id="rIdN", etc.)
referenced = set(re.findall(r'(?:embed|link|r:id|:id)="([^"]+)"', doc))
# also catch generic ="rIdNNN" tokens used as image refs
referenced |= set(re.findall(r'"(rId\d+)"', doc))

# Parse relationships: <Relationship Id=".." Type=".." Target=".."/>
rel_pat = re.compile(r'<Relationship\b[^>]*?/>')
drop_targets = []
kept_rels = []
removed = 0
for m in rel_pat.finditer(rels):
    tag = m.group(0)
    rid = (re.search(r'Id="([^"]+)"', tag) or [None, None])[1]
    typ = (re.search(r'Type="([^"]+)"', tag) or [None, ""])[1]
    tgt = (re.search(r'Target="([^"]+)"', tag) or [None, ""])[1]
    is_image = typ.endswith("/image")
    is_vector = tgt.lower().endswith((".wmf", ".emf"))
    if is_image and is_vector and rid not in referenced:
        drop_targets.append("word/" + tgt.replace("\\", "/").lstrip("/"))
        removed += 1
    else:
        kept_rels.append(tag)

if removed == 0:
    print(f"{path.name}: no orphan vector media found (nothing to strip).")
    sys.exit(0)

# Rebuild rels xml keeping only non-dropped relationships
new_rels = re.sub(
    r"(<Relationships\b[^>]*>).*(</Relationships>)",
    lambda mm: mm.group(1) + "".join(kept_rels) + mm.group(2),
    rels,
    flags=re.DOTALL,
)

drop_set = set(t.replace("word/word/", "word/") for t in drop_targets)

tmp = path.with_suffix(".docx.tmp")
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        name = item.filename
        # normalize media target comparison
        norm = name
        if norm in drop_set:
            continue
        if name == rels_name:
            zout.writestr(item, new_rels)
        else:
            zout.writestr(item, zin.read(name))
zin.close()
shutil.move(str(tmp), str(path))

before_mb = "?"
print(f"{path.name}: stripped {removed} orphan vector media + their rels entries.")
print(f"  new size: {path.stat().st_size:,} bytes")
