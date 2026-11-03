#!/usr/bin/env bash
# apply_house_style.sh — Phase B of the Empire Thai-textbook docx pipeline.
#
# Takes a base docx already produced by render_chapter_docx.sh (Phase A:
# ZWSP-segment + pandoc + thaiDistribute + font + orphan-media strip) and layers
# on the accumulated house style the principal signed off through 2026-06:
#
#   1. add_figure_captions.py     — prepend auto-updating "รูปที่ N.M" (Word SEQ)
#   2. set_font_size.py 32 28     — body + inline symbols + equations → 14pt
#   3. add_caption_spacing.py     — one blank line below every figure caption
#   4. center_figures_captions.py — center each figure + its caption on the page
#   5. add_heading3_style.py      — promote N.N.N subsections to Heading3 (16pt bold)
#   6. suppress_thai_proofing.py  — noProof + lang th-TH so ZWSP stops triggering
#                                   red spell-check squiggles (replaces the old
#                                   manual Google Docs round-trip)
#
# Each stage is a pure string edit on word/document.xml (never an XML parse) so
# w14 paraIds, mc:Ignorable, m:oMath equations, SEQ fields and ZWSP survive
# byte-for-byte — the hard-won rule that keeps Word from throwing a "repair"
# prompt. Every stage is individually idempotent, and the chain is re-runnable:
# stage 2 would shrink the stage-5 headings, but stage 5 re-asserts 16pt each run.
#
# Edits the docx IN PLACE. Order matters (font before Heading3, so H3's 16pt is
# set after the global shrink, not shrunk by it).
#
# Usage: apply_house_style.sh <docx>

set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <docx>" >&2
    exit 2
fi

DOC="$1"
[[ -f "$DOC" ]] || { echo "Not found: $DOC" >&2; exit 1; }

D="$(cd "$(dirname "$0")" && pwd)"
PY="py"; command -v py &>/dev/null || PY="python3"

echo ">>> 1/6 figure captions — รูปที่ N.M (SEQ auto-number)"
"$PY" "$D/add_figure_captions.py"     "$DOC" "$DOC"
echo ">>> 2/6 font size — body + symbols + equations → 14pt (sz 32→28)"
"$PY" "$D/set_font_size.py"           "$DOC" "$DOC" 32 28
echo ">>> 3/6 blank line below each caption"
"$PY" "$D/add_caption_spacing.py"     "$DOC" "$DOC"
echo ">>> 4/6 center figures + captions"
"$PY" "$D/center_figures_captions.py" "$DOC" "$DOC"
echo ">>> 5/6 Heading3 for N.N.N subsections (16pt bold)"
"$PY" "$D/add_heading3_style.py"      "$DOC" "$DOC"
echo ">>> 6/6 suppress Thai proofing (noProof + lang th-TH, kills ZWSP squiggles)"
"$PY" "$D/suppress_thai_proofing.py"  "$DOC" "$DOC"

echo ">>> House style applied: $DOC"
echo "    Reminder: open in Word, Ctrl+A then F9 to compute figure SEQ numbers."
