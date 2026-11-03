#!/usr/bin/env python3
"""Pre-process a markdown file by segmenting Thai text with zero-width spaces.

Why: XeTeX (even with polyglossia + Thai) does NOT word-segment Thai text
automatically — long Thai sentences without spaces overflow the right margin
in justify mode (135+ overfull-hbox cases observed in chapter05.md). Inserting
ZWSP (U+200B) between Thai words via pythainlp's newmm tokenizer gives XeTeX
explicit break opportunities → clean line wrap.

Usage:
    py tools/teaching/thai_segment_zwsp.py <input.md> <output.md>

Skips text inside code blocks, inline code, math (`$...$` / `$$...$$`), and
LaTeX commands so we don't break their syntax.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from pythainlp.tokenize import word_tokenize

ZWSP = "​"
THAI_RANGE = range(0x0E00, 0x0E80)


def is_thai(ch: str) -> bool:
    return ord(ch) in THAI_RANGE


def segment_thai_chunk(text: str) -> str:
    """Walk text char by char; collect Thai runs and segment with ZWSP between
    pythainlp newmm-tokenized words. Non-Thai chars pass through unchanged.
    """
    out_parts = []
    buf = []
    for ch in text:
        if is_thai(ch):
            buf.append(ch)
        else:
            if buf:
                segment = "".join(buf)
                words = word_tokenize(segment, engine="newmm")
                out_parts.append(ZWSP.join(words))
                buf = []
            out_parts.append(ch)
    if buf:
        segment = "".join(buf)
        words = word_tokenize(segment, engine="newmm")
        out_parts.append(ZWSP.join(words))
    return "".join(out_parts)


# Regex patterns for fenced content (DO NOT segment inside these)
CODE_FENCE_RE = re.compile(r"^```", re.MULTILINE)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
INLINE_MATH_RE = re.compile(r"\$[^\$\n]+\$")
DISPLAY_MATH_RE = re.compile(r"\$\$[\s\S]+?\$\$")


def process_markdown(text: str) -> str:
    """Process markdown, skipping code blocks + inline code + math."""
    # Stage 1: split on code fence blocks (```...```)
    parts = []
    lines = text.split("\n")
    in_fence = False
    fence_buf = []
    code_buf = []
    for line in lines:
        if line.startswith("```"):
            if in_fence:
                # End fence — flush code_buf as a fenced block (DON'T segment)
                fence_buf.append("\n".join(code_buf))
                fence_buf.append(line + "\n")
                code_buf = []
                in_fence = False
            else:
                # Start fence — flush fence_buf as regular (segment Thai)
                if fence_buf:
                    parts.append(("text", "\n".join(fence_buf)))
                    fence_buf = []
                in_fence = True
                fence_buf.append(line + "\n")
        else:
            if in_fence:
                code_buf.append(line)
            else:
                fence_buf.append(line)
    # Flush remainder
    if in_fence:
        # Unterminated fence — treat as code, don't segment
        fence_buf.append("\n".join(code_buf))
        parts.append(("code", "\n".join(fence_buf)))
    else:
        if fence_buf:
            parts.append(("text", "\n".join(fence_buf)))

    # Stage 2: for each text part, mask inline code + math, segment Thai, restore
    out = []
    for kind, chunk in parts:
        if kind == "code":
            out.append(chunk)
            continue
        # Mask inline code + display math + inline math with placeholders
        masks = []

        def mask(pat, label):
            def repl(m):
                masks.append(m.group(0))
                return f"\x00{label}{len(masks)-1}\x00"
            return pat.sub(repl, chunk)

        masked = chunk
        masked = mask(DISPLAY_MATH_RE, "DMATH")
        masked = mask(INLINE_MATH_RE, "IMATH")
        masked = mask(INLINE_CODE_RE, "ICODE")
        # nonlocal chunk references won't work in nested functions across lines;
        # rewrite without inner masking factory
        pass

        # Re-do without factory due to nonlocal issue
        masked = chunk
        masks = []
        for pat, label in [
            (DISPLAY_MATH_RE, "DMATH"),
            (INLINE_MATH_RE, "IMATH"),
            (INLINE_CODE_RE, "ICODE"),
        ]:
            def make_repl(m_list, l):
                def repl(m):
                    m_list.append(m.group(0))
                    return f"\x00{l}{len(m_list)-1}\x00"
                return repl
            masked = pat.sub(make_repl(masks, label), masked)

        # Segment Thai
        segmented = segment_thai_chunk(masked)

        # Restore masks
        # Track which list each label maps to
        seen = {"DMATH": 0, "IMATH": 0, "ICODE": 0}
        def restore(m):
            label = m.group(1)
            idx = int(m.group(2))
            return masks[idx]  # mixed indexing, but masks order matches insertion order
        # Actually masks list order matches insertion order across the 3 patterns,
        # but the placeholder uses per-label indices counting independently. Need
        # to re-implement correctly:
        out.append(segmented)
        # FIXME: restoration done below — see Stage 3
    full = "".join(out)
    return full


def process_markdown_v2(text: str) -> str:
    """Cleaner re-implementation: split on code fences, then for non-code
    sections mask math/inline-code with sequential placeholders, segment Thai,
    restore via sequential lookup.
    """
    out_lines = []
    in_fence = False
    fence_lines = []
    for line in text.split("\n"):
        if line.startswith("```"):
            if in_fence:
                # End fence — emit fence_lines + closing line as-is
                out_lines.append(line)
                in_fence = False
            else:
                # Start fence
                out_lines.append(line)
                in_fence = True
            continue
        if in_fence:
            out_lines.append(line)  # code block content — no segmentation
            continue
        # Non-code line — mask inline code + math, segment, restore
        masks: list[str] = []
        def stash(m):
            masks.append(m.group(0))
            return f"\x01{len(masks)-1}\x01"
        masked = line
        # Display math (rare on single line) → mask whole
        masked = DISPLAY_MATH_RE.sub(stash, masked)
        masked = INLINE_MATH_RE.sub(stash, masked)
        masked = INLINE_CODE_RE.sub(stash, masked)
        # Segment Thai
        segmented = segment_thai_chunk(masked)
        # Restore
        def unstash(m):
            return masks[int(m.group(1))]
        restored = re.sub(r"\x01(\d+)\x01", unstash, segmented)
        out_lines.append(restored)
    return "\n".join(out_lines)


def main():
    if len(sys.argv) != 3:
        print("Usage: thai_segment_zwsp.py <input.md> <output.md>", file=sys.stderr)
        sys.exit(2)
    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    if not in_path.exists():
        print(f"Not found: {in_path}", file=sys.stderr)
        sys.exit(1)
    text = in_path.read_text(encoding="utf-8")
    segmented = process_markdown_v2(text)
    out_path.write_text(segmented, encoding="utf-8")
    # Report stats
    zwsp_count = segmented.count(ZWSP)
    print(f"Wrote: {out_path}")
    print(f"  ZWSP inserted: {zwsp_count}")
    print(f"  Input size:  {len(text):,} chars")
    print(f"  Output size: {len(segmented):,} chars")


if __name__ == "__main__":
    main()
