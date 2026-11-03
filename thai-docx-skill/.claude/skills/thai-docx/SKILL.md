---
name: thai-docx
description: "Render a Thai-language academic document (เอกสารคำสอน / textbook chapter / ตำรา / report) as an editable Word .docx in the Empire house style — thaiDistribute justification via ZWSP word-segmentation, TH Sarabun New, auto-numbered figure captions (รูปที่ N.M SEQ), 14pt body+symbols+equations, centered figures, and a 24/18/16/14pt heading ladder (บท / N.N / N.N.N / body). Use when the user says 'ทำเป็น Word', 'ทำ docx', 'เอกสารคำสอนเป็นเวิด', 'ทำไฟล์เวิดไทยสไตล์เรา', 'render docx', or needs an editable .docx for ก.พ.อ. submission rather than a PDF. For PDF output use /thai-latex instead."
argument-hint: "<input.md> <output.docx>"
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# /thai-docx — Thai academic Word (.docx) render pipeline, Empire house style

Empire-standard pipeline for turning a Thai academic markdown source into an
**editable Word .docx** that (a) justifies Thai+English text without the
"river-of-white" gaps Word normally produces, and (b) carries the full house
style the principal signed off through mid-2026: auto-numbered figure captions,
14pt body/math, centered figures, and a clean 4-level heading ladder.

**When to pick this over `/thai-latex`:** ก.พ.อ. promotion evaluation and any
reviewer who must edit in Word expect .docx. `/thai-latex` gives better
typography but PDF-only. Both consume the *same* ZWSP-segmented markdown, so a
project can produce both from one source.

**Why the ZWSP step exists:** `python-docx`, the docx skill, and plain pandoc do
not word-break Thai, so Word treats a whole sentence as one "word" and justify
spreads space unevenly. Segmenting with pythainlp and joining words with a
Zero-Width Space (U+200B) gives Word real break/distribute opportunities, and
`thaiDistribute` justify (not generic `DISTRIBUTE`) then spreads space only at
word edges. Full rationale: `admin/thai_docx_distribute_pattern.md`.

---

## Quick invocation

Two phases. Phase A builds the base docx; Phase B layers the house style.

```bash
# Phase A — md → base docx (segment + pandoc + thaiDistribute + font + strip)
tools/teaching/render_chapter_docx.sh  input.md  out.docx

# Phase B — apply the house style in place (captions, 14pt, spacing, center, H3)
tools/teaching/apply_house_style.sh  out.docx
```

For a single chapter, `input.md` is that chapter. For a whole book, concatenate
the chapter markdowns first (each starting `# บทที่ N ...`) and pass the combined
file — the SEQ figure numbers and Heading tracking reset per `บทที่ N`.

### Running from outside Empire

This skill is reachable from any workspace (it is junctioned into
`~/.claude/skills/`), but the commands above use paths relative to the Empire
checkout. When the session's working directory is somewhere else, call the
scripts by absolute path:

```bash
E="/path/to/your/project"   # folder that contains tools/teaching/
"$E"/tools/teaching/render_chapter_docx.sh  input.md  out.docx
"$E"/tools/teaching/apply_house_style.sh    out.docx
```

The scripts resolve their own helper tools from their own folder, so they run
correctly from any working directory. Only the invocation path needs to be
absolute.

After Phase B: **open in Word, Ctrl+A then F9** to compute the figure SEQ
numbers. That is the only manual step. The ZWSP red-squiggle problem is handled
inside Phase B now (stage 6), so no Google Docs round-trip is needed.

---

## Pipeline

### Phase A — `render_chapter_docx.sh` (base docx)

```
input.md
  ├── Stage 0: prep_docx_md.py       — \chaptersubtitle{X} → *X*; cap tall figures (aspect>1.85 → 18cm)
  ├── Stage 1: thai_segment_zwsp.py  — pythainlp newmm → ZWSP between Thai words
  ├── Stage 2: pandoc --reference-doc=reference_template.docx  (TH Sarabun base)
  ├── Stage 3: post_render_thai.py   — BODY_JC=thaiDistribute + force body font + center tables
  └── Stage 4: strip_orphan_media.py — drop 234 unreferenced wmf/emf carried by the reference doc
```

### Phase B — `apply_house_style.sh` (house style, in place, ordered)

| # | Tool | Effect |
|---|---|---|
| 1 | `add_figure_captions.py` | Prepend auto-updating `รูปที่ N.M` to each caption (per-chapter Word SEQ `Figure{N}`) |
| 2 | `set_font_size.py 32 28` | Body + inline symbols + equations 16pt → **14pt** (headings keep 40/36) |
| 3 | `add_caption_spacing.py` | One blank 14pt line below every figure caption |
| 4 | `center_figures_captions.py` | `jc=center` on each figure paragraph + its caption |
| 5 | `add_heading3_style.py` | Promote every `N.N.N` subsection to a real **Heading3** (16pt bold, outlineLvl 2) |
| 6 | `suppress_thai_proofing.py` | `noProof` + `lang th-TH` on docDefaults so Word stops underlining ZWSP-split Thai as misspelled |

Order matters: font-shrink (2) runs before Heading3 (5) so H3's 16pt is set
*after* the global shrink. The chain is re-runnable: stage 2 would shrink the
stage-5 headings, but stage 5 re-asserts 16pt on each run.


### Phase A' — a docx somebody else typed (no markdown source)

A student's report, a draft mailed in, anything written straight into Word never
went through Phase A, so it has no thaiDistribute and no ZWSP and Phase B's
stages have nothing to bite on. Three tools stand in for Phase A on a file that
already exists. Run them in this order, then Phase B if the document also needs
captions and the 14pt ladder:

| # | Tool | Effect |
|---|---|---|
| 1 | `set_body_justify.py` | `thaiDistribute` on every body paragraph (skips headings, deliberate centring, figures, tables, textboxes) |
| 2 | `segment_docx_zwsp.py` | ZWSP between Thai words in those paragraphs, and off any consonant/mark cluster it would split |
| 3 | `demote_false_headings.py` | Strip the Heading style from paragraphs that carry no `บทที่ N` / `N.N` / `N.N.N` number |

Order matters: stage 2 only re-segments paragraphs that already carry
thaiDistribute, so stage 1 is what gives it work to do.

Stage 3 exists because Word hands out Heading styles to whatever is retyped near
one. A hand-written report routinely has dozens of table cells and figure
captions styled Heading3 with the bold and size overridden back to body: nothing
looks wrong on the page, but each one lands in the Navigation pane and in any
automatic table of contents. (วิน's Task 4 report, Aug 2026: 72 of 108 heading-
styled paragraphs were not headings, 70 of them cells inside one BMMS table.)

All three preserve tracked revisions, comments and content byte-for-byte, so
they are safe on a file that is mid-review. Verify with `text_of(before) ==
text_of(after)`: the plain text must be identical, since every one of these is a
formatting change.

---

## The one hard rule: string-edit, never XML-parse (for Phase B)

Every Phase-B tool edits `word/document.xml` as **raw text** (regex/string ops),
never through `xml.etree`/ElementTree. A full ElementTree round-trip renames
namespace prefixes (`w14`→`ns0`, `m:oMath`→`ns3:oMath`) but leaves the
`mc:Ignorable="w14 w15 ..."` attribute untouched → those prefixes become
undeclared → **Word throws a "repair" prompt on open**. Raw-text edits preserve
every prefix, `mc:Ignorable`, `m:oMath` equation, SEQ field, and ZWSP
byte-for-byte.

(`post_render_thai.py` in Phase A *does* use ElementTree — safe there because it
runs on fresh pandoc output before any SEQ fields / w14-heavy content exist. Do
not reuse that approach for anything that runs after Phase A.)

Any new house-style tweak MUST follow the Phase-B pattern. After writing one,
verify: XML well-formed, `mc:Ignorable` intact, and the invariant counts
(drawings / m:oMath / SEQ / ZWSP) unchanged.

---

## The heading ladder (Thai/complex-script size = szCs)

| Level | Example | Size | Weight | Style |
|---|---|---|---|---|
| Chapter | บทที่ 5 ... | 24pt | bold | `Heading1` |
| Section | 5.1 บทนำ | 18pt | bold | `Heading2` |
| Subsection | 5.1.1 ที่มา... | 16pt | bold | `Heading3` (added by stage 5) |
| Body | เนื้อหา | 14pt | regular | Normal, `thaiDistribute` |

`add_heading3_style.py` also *registers* the `Heading3` style in `styles.xml`
(cloned from Heading2, `outlineLvl=2`), so subsections show in the Word
Navigation pane and map into any auto table of contents.

---

## Source markdown conventions

Same source shape as `/thai-latex` (one .md feeds both paths):

```markdown
# บทที่ 5 วิธีมุมหมุนและการโก่งตัว

\chaptersubtitle{Slope-Deflection Method}

## วัตถุประสงค์ของบท
## 5.1 บทนำ
### 5.1.1 ที่มาและประวัติของวิธี      ← becomes Heading3 in Phase B

ข้อความมี inline math $\theta$ $\psi$ $\Delta$ ได้ตามปกติ.

$$\psi = \frac{\Delta}{L} \qquad\qquad (5.1)$$

![คำบรรยายรูป](figures/fig_5_1.png){ width=70% }   ← caption gets "รูปที่ 5.1 " prefixed
```

- **Figures:** put PNGs in `figures/` next to the source .md. The paragraph
  right after each `<w:drawing>` is treated as its caption.
- **Subsections:** any paragraph whose text starts `N.N.N` (e.g. `5.1.1`) is
  promoted to Heading3 — so do not start ordinary body paragraphs that way.
- **Chapter tracking:** Heading1 text `บทที่ N` drives the per-chapter figure
  SEQ name (`Figure5`, `Figure6`, ...) so numbering restarts each chapter.

---

## The ZWSP spell-check squiggles (solved in stage 6)

The ZWSP that makes justify look good also makes Word underline every Thai word
red, because it reads each split as a misspelling. Stage 6 fixes this at the
source: it writes `<w:noProof/>` plus `<w:lang w:val="th-TH" .../>` into the
document's default run properties in `styles.xml`, so Word never proofs the text
at all. Our pandoc books ship a `lang w:val="en-US"` there by default (which is
what made Thai get checked against English), so the tool **replaces** that tag
rather than adding a second one.

This supersedes the old manual workaround (copy into Google Docs, copy back) that
was the standard handoff flow from 2026-05-31 until 2026-07-30. Borrowed from
`tools/thai_office_doc/build_thai_office_doc.py`, which shipped the fix first.

Do **not** solve the red by removing ZWSP and letting Word justify Thai itself:
that reintroduces the ugly paragraphs (proven bad, principal rejected).

Note: ZWSP still breaks in-docx text search (`"วันชัย"` is stored `"วัน​ชัย"`).
When verifying, `.replace('​','')` before matching.

---

## Verification checklist (after Phase B)

```python
# XML well-formed (both parts), invariants intact
import zipfile, re, xml.dom.minidom as m
d = zipfile.ZipFile(DOCX).read('word/document.xml').decode('utf-8')
s = zipfile.ZipFile(DOCX).read('word/styles.xml').decode('utf-8')
m.parseString(d.encode()); m.parseString(s.encode())          # no exception
assert 'w:styleId="Heading3"' in s                            # style registered
# spot counts: drawings, SEQ figures, centered figs+caps, equations, ZWSP,
# mc:Ignorable present and unchanged
```

Windows has no LibreOffice render → you can only check the XML. **The principal
must open the file in Word for visual sign-off** before it is considered done.

---

## Required system tools

| Tool | Install |
|---|---|
| `pandoc` 3.9+ | https://pandoc.org/ (`winget install JohnMacFarlane.Pandoc`) |
| `py` (Python 3.10+) | Python.org — NOT the WindowsApps stub |
| `pythainlp` | `py -m pip install pythainlp` |
| TH Sarabun New | Windows font (for correct on-screen render; the docx names it regardless) |

No LaTeX needed (that is the `/thai-latex` path).

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Word shows a "repair" prompt on open | A tool XML-parsed instead of string-edited → broken `mc:Ignorable` | Rebuild that stage as a raw-text edit (see hard rule) |
| Figure numbers show as `รูปที่ 5.{ }` blank | SEQ fields not computed yet | In Word: Ctrl+A then F9 |
| Justify still uneven / river-of-white | ZWSP segmentation didn't run | Confirm Stage 1 — segmented .md has `​` between Thai words |
| Red squiggles under every Thai word | stage 6 did not run, or a run-level `lang` overrides the default | Re-run Phase B; check `styles.xml` docDefaults has `<w:noProof/>` |
| Heading3 lines look 14pt after re-run | (fixed) stage 2 shrank them | `add_heading3_style.py` re-asserts 16pt — just re-run Phase B |
| In-docx search misses a word | ZWSP inside the word | `.replace('​','')` before searching |
| Tall figure overflows the page | full-page scan (aspect >1.85) | Stage 0 caps it at 18cm; adjust in `prep_docx_md.py` if needed |

---

## Comparison with `/thai-latex`

| Path | Output | Use for |
|---|---|---|
| **thai-docx (this skill)** | .docx | ก.พ.อ. submission, any Word-editing reviewer, the working/handoff file |
| thai-latex | PDF | Best typography, native math, สำนักพิมพ์/ISBN "proof" output |

Both read the same ZWSP-segmented source. Neither needs a Google Docs round-trip
any more: PDF has no spell-check, and docx suppresses proofing in stage 6.

---

## Files

Phase A: `render_chapter_docx.sh`, `prep_docx_md.py`, `thai_segment_zwsp.py`,
`reference_template.docx`, `post_render_thai.py`, `strip_orphan_media.py`.

Phase A' (existing docx): `set_body_justify.py`, `segment_docx_zwsp.py`,
`demote_false_headings.py`.

Phase B: `apply_house_style.sh`, `add_figure_captions.py`, `set_font_size.py`,
`add_caption_spacing.py`, `center_figures_captions.py`, `add_heading3_style.py`,
`suppress_thai_proofing.py`.

All under `tools/teaching/` (originated with the struct_analysis_2 textbook); the
skill makes them callable from any Thai academic docx project. Pattern rationale:
`admin/thai_docx_distribute_pattern.md`.
