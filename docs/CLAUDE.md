# CLAUDE.md

This file gives Claude Code context for this repository. Keep it short — link out to files under `rawdata/` rather than pasting their contents here.

> **⚠️ This file lives at `docs/CLAUDE.md`, not repo root — Claude Code does NOT auto-load it.** Point Claude here explicitly at the start of a session (e.g. "read docs/CLAUDE.md first"). Moved out of root by user request to keep root-level clutter down to just `README.md`; `workmen's_diary/` stays at repo root since it's already its own organized folder.

> **⚠️ Read [rule_of_tune.md](rule_of_tune.md) before touching anything in `rawdata/`** — it protects the original literature-review/report source files from accidental edits and covers citation-integrity rules.

## Project

KU senior project (ป.ตรี, อ้างอิงรายวิชา 203499) building on an NRCT-funded research project (วช. ปีงบ 68) on **bridge/pier structural condition inspection using AI** — synthesizing existing bridge-inspection standards (Thai BMMS, US NBI/AASHTO) with a T-BHI (Thailand Bridge Health Index) evaluation criteria, and a deep-learning / MLLM approach (UAV imagery → damage detection/classification → condition rating) to close gaps in current manual inspection practice.

> Project title, exact scope, and current milestone are not yet filled in here — update this section directly once finalized; the description above is inferred from the literature-review folder structure and source titles.

## Repo layout

```
README.md
CLAUDE.md
rawdata/
  01 Literature Review/
    00_บริบทโครงการ/            — background: full NRCT report + last year's senior project (both PDF)
    0_Reading Guide (อ่านก่อน).docx  — READ THIS FIRST before other literature review files
    1_Foundation (การตรวจสอบ+เกณฑ์)/  — inspection standards: T-BHI criteria (synthesized), NBI/AASHTO, Thai BMMS
    2_AI Landscape (DL+MLLM)/    — CNN/deep-learning structural damage detection literature
    3_Gap+Method (Gou foil+UAV+eval)/ — gap analysis + candidate method papers (coding systems, segmentation-to-rating, UAV multi-stage inspection)
  02 Methodology & Work/         — empty so far — methodology + actual project work goes here
  03 Reports/                    — empty so far — deliverable reports go here
```

**`rawdata/` is ~121MB of reference PDFs, already committed to git (no `.gitignore`/LFS previously in place).** Don't read whole PDFs into context speculatively — ask the user which specific file/section is relevant, or use the "อ่านก่อน" (read first) files in each subfolder as the entry point.

## Known housekeeping (not yet actioned — ask before touching)

- `README.md` was a placeholder (`"123"`) — replaced with a real stub; still needs the user to fill in the actual project title/team/timeline.
- No `.github/workflows/` — nothing to build/test yet since this is a literature-review/report-stage project, not code. Add CI later if `02 Methodology & Work/` ends up with a runnable pipeline (e.g. Python training/eval scripts).
- `rawdata/` (~121MB) is already committed to git from before `.gitignore` existed — not retroactively cleaned up (rewriting history is destructive; needs an explicit user decision).

## Workmen's Diary

Day-by-day human-readable log of what changed and why — see [workmen's_diary/README.md](../workmen's_diary/README.md) for format/rules (stays at repo root, not moved into `docs/`). Check the most recent file(s) there before starting work to catch any in-progress/handed-off state; add your own entry when you finish a work session.

## Working conventions

- Comments/docs mix Thai and English — follow existing usage per file/folder.
- This is a research + report-writing project, not application code — expect most Claude Code work here to be literature synthesis, writing methodology sections, or (once `02 Methodology & Work/` has code) data pipeline / model work.
