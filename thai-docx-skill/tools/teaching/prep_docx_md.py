#!/usr/bin/env python3
"""Pre-process a chapter .md for the Thai docx (thaiDistribute) pipeline.

Handles the few LaTeX-isms used by the /thai-latex PDF path that don't belong
in a pandoc->docx render, and caps tall figures so they fit a Word page:

  1. \\chaptersubtitle{X}  ->  *X* (italic subtitle paragraph)
  2. tall figures (aspect h/w > 1.85): swap `{ width=NN% }` -> `{ height=18cm }`
     so full-page reference scans don't overflow several Word pages.

Usage: prep_docx_md.py <in.md> <out.md> <figures_dir>
"""
import re
import sys
from pathlib import Path
from PIL import Image

if len(sys.argv) != 4:
    print("usage: prep_docx_md.py <in.md> <out.md> <figures_dir>", file=sys.stderr)
    sys.exit(2)

sys.stdout.reconfigure(encoding="utf-8")

in_md, out_md, fig_dir = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
s = in_md.read_text(encoding="utf-8")

# 1. \chaptersubtitle{X} -> italic subtitle line
n_sub = len(re.findall(r"\\chaptersubtitle\{[^}]*\}", s))
s = re.sub(r"\\chaptersubtitle\{([^}]*)\}", r"*\1*", s)

# 2. Cap tall figures by height instead of width
TALL = 1.85
HEIGHT = "18cm"
capped = []

def cap_fig(m):
    alt, path, attrs = m.group(1), m.group(2), m.group(3)
    fname = path.split("/")[-1]
    fpath = fig_dir / fname
    if fpath.exists():
        try:
            w, h = Image.open(fpath).size
            if h / w > TALL:
                # replace any width=.. with height=18cm
                new_attrs = re.sub(r"width=\s*[0-9.]+%?", f"height={HEIGHT}", attrs)
                if "height=" not in new_attrs:
                    new_attrs = (new_attrs.rstrip() + f" height={HEIGHT}").strip()
                capped.append(fname)
                return f"![{alt}]({path}){{{new_attrs}}}"
        except Exception as e:
            print(f"  warn: {fname}: {e}", file=sys.stderr)
    return m.group(0)

# match ![alt](path){ attrs }
s = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)\{([^}]*)\}", cap_fig, s)

out_md.write_text(s, encoding="utf-8")
print(f"Prepped: {out_md}")
print(f"  \\chaptersubtitle -> italic: {n_sub}")
print(f"  tall figures height-capped ({HEIGHT}): {len(capped)} -> {capped}")
