#!/usr/bin/env bash
# render_chapter_docx.sh — Thai docx pipeline (2026-05-31 "thaiDistribute" method)
#
# Implements admin/thai_docx_distribute_pattern.md:
#   md → prep (chaptersubtitle + tall-figure cap)
#      → thai_segment_zwsp.py (insert ZWSP between Thai words — REQUIRED so
#        Word's thaiDistribute justify spreads space at word edges, not inside)
#      → pandoc + reference docx (TH Sarabun base)
#      → post_render_thai.py BODY_JC=thaiDistribute (enum 9, not DISTRIBUTE 4)
#
# Red-squiggle handling now lives in Phase B (apply_house_style.sh stage 6:
# suppress_thai_proofing.py). The old Google Docs round-trip is retired.
#
# Usage: tools/teaching/render_chapter_docx.sh <input.md> <output.docx>

set -euo pipefail
export BODY_FONT="${BODY_FONT:-TH Sarabun New}"

# resolve this script's own folder so the pipeline runs from any cwd
D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <input.md> <output.docx>" >&2
    exit 2
fi

INPUT="$1"
OUTPUT="$2"
[[ -f "$INPUT" ]] || { echo "Input not found: $INPUT" >&2; exit 1; }

REFERENCE_DOC="${REFERENCE_DOC:-$D/reference_template.docx}"
[[ -f "$REFERENCE_DOC" ]] || { echo "Reference doc not found: $REFERENCE_DOC" >&2; exit 1; }

OUTDIR="$(dirname "$OUTPUT")"
mkdir -p "$OUTDIR"
STEM="$(basename "$OUTPUT" .docx)"
INPUT_DIR="$(dirname "$INPUT")"
FIG_DIR="$INPUT_DIR/figures"

PREPPED="$OUTDIR/${STEM}_prepped.md"
SEGMENTED="$OUTDIR/${STEM}_segmented.md"
RAW="$OUTDIR/${STEM}_raw.docx"

PY="py"; command -v py &>/dev/null || PY="python3"

echo ">>> Stage 0: prep (chaptersubtitle + tall-figure height cap) → $PREPPED"
"$PY" "$D"/prep_docx_md.py "$INPUT" "$PREPPED" "$FIG_DIR"

echo ">>> Stage 1: pythainlp ZWSP segment → $SEGMENTED"
"$PY" "$D"/thai_segment_zwsp.py "$PREPPED" "$SEGMENTED"

echo ">>> Stage 2: pandoc → $RAW (reference: $REFERENCE_DOC)"
pandoc "$SEGMENTED" \
    --reference-doc="$REFERENCE_DOC" \
    --resource-path="$INPUT_DIR" \
    -o "$RAW"

echo ">>> Stage 3: post_render_thai.py BODY_JC=thaiDistribute → $OUTPUT"
BODY_JC=thaiDistribute "$PY" "$D"/post_render_thai.py "$RAW" "$OUTPUT"

echo ">>> Stage 4: strip orphan media carried from reference docx"
"$PY" "$D"/strip_orphan_media.py "$OUTPUT"

echo ">>> Done. docx: $OUTPUT"
echo "    NEXT: run apply_house_style.sh on it (stage 6 there suppresses Thai proofing)."