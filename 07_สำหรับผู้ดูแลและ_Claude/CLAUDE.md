# CLAUDE.md

This file gives Claude Code context for this repository. Keep it short — link out to files under `03_เปเปอร์งานวิจัย/` rather than pasting their contents here.

> **⚠️ This file lives at `07_สำหรับผู้ดูแลและ_Claude/CLAUDE.md`, not repo root — Claude Code does NOT auto-load it.** Point Claude here explicitly at the start of a session (e.g. "read docs/CLAUDE.md first"). Moved out of root by user request to keep root-level clutter down to just `README.md`; `workmen's_diary/` stays at repo root since it's already its own organized folder.

> **⚠️ Read [rule_of_tune.md](rule_of_tune.md) before touching anything in `03_เปเปอร์งานวิจัย/` or `01_เล่มรายงาน/`** — it protects the original literature-review/report source files from accidental edits and covers citation-integrity rules.

## Project

KU senior project (ป.ตรี, อ้างอิงรายวิชา 203499) building on an NRCT-funded research project (วช. ปีงบ 68) on **bridge/pier structural condition inspection using AI** — synthesizing existing bridge-inspection standards (Thai BMMS, US NBI/AASHTO) with a T-BHI (Thailand Bridge Health Index) evaluation criteria, and a deep-learning / MLLM approach (UAV imagery → damage detection/classification → condition rating) to close gaps in current manual inspection practice.

> Project title, exact scope, and current milestone are not yet filled in here — update this section directly once finalized; the description above is inferred from the literature-review folder structure and source titles.

## Scope and report structure (updated 2026-10-23)

Main work (as stated by the user, 2026-10-23): (1) classify damage types with an LLM or VLM; (2) segment and classify bridge components; (3) measure crack distance/size with a laser. The user confirmed there are 3 main items.

**The report follows the advisor-approved Pre-project table of contents:** [สารบัญ_Pre-project_ที่อาจารย์ปรับ.md](../02_สรุปและบันทึกประกอบการเขียน/2_บันทึกการตัดสินใจและโน้ตเขียนเล่ม/สารบัญ_Pre-project_ที่อาจารย์ปรับ.md) — read it before drafting any chapter. Conventions from it:
- Headings in Thai only, no English in parentheses. In body text the first use of a technical term gets the English in parentheses, e.g. โฟโตแกรมเมตรี (photogrammetry); afterwards Thai or the abbreviation only.
- Chapter 1 is written last.
- Section 3.7 gives the EHI / T-BHI calculation and must cite the advisor's reference exactly as written in that file.
- Older docs (`สรุปโครงงาน_T-BHI_ฉบับอัปเดต.md`, `05_โค้ดและการทดลอง/ทดลอง_YOLO_*`) describe the previous plan (YOLO/RT-DETR detector) plus an earlier ToC draft (`bridge_damage_yolo_rtdetr/สรุป/โครงเล่มรายงาน.md`). The user confirmed on 2026-10-23 that there is a new plan, so treat them as history; three entry-point files carry a "superseded" banner. The new plan's details for damage detection are not specified yet — ask before assuming (VLM replaces the detector entirely vs. alongside it).

## Repo layout (reorganized 2026-10-30 — numbered Thai folders; see `00_เริ่มตรงนี้.md` at repo root for the click-here map)

```
00_เริ่มตรงนี้.md                  — entry map: "I want to X → go to folder Y"
01_เล่มรายงาน/                     — 1_ฉบับที่ส่งอาจารย์แล้ว · 2_ความเห็นอาจารย์ · 3_ฉบับร่างเก่า_v1-v5 · 4_เกณฑ์และตัวอย่างเล่มจากภาควิชา
02_สรุปและบันทึกประกอบการเขียน/     — 1_อ่านก่อนสอบ · 2_บันทึกการตัดสินใจและโน้ตเขียนเล่ม · 3_แผนและสรุปเก่า
03_เปเปอร์งานวิจัย/                — literature (start at 00_อ่านก่อน_Reading_Guide.docx; 0_เปเปอร์ที่ใช้อ้างอิงในเล่ม = the curated 5)
04_ภาพและข้อมูลสนาม/               — field photos (faces, git-ignored), drone images (Agisoft), 3D prints
05_โค้ดและการทดลอง/                — YOLO / RT-DETR trials, senior's code+dataset (git-ignored), UAV/laser study
06_บันทึกงานรายวัน/                — workmen's diary (format: its README.md)
07_สำหรับผู้ดูแลและ_Claude/         — this file, rule_of_tune.md, INVENTORY.csv
99_ไฟล์ซ้ำ_ลบได้/                  — verified byte-identical duplicates, safe to delete
```

Old path -> new path (for reading older diary entries): `rawdata/01 Literature Review/` -> `03_เปเปอร์งานวิจัย/`; `rawdata/03 Reports/` + `เล่มใหม่_2026-10-24/` + `งานใหม่/หลักการทำproposal/` -> `01_เล่มรายงาน/`; `rawdata/agisoft/`, `photo/`, `3d_model/` -> `04_ภาพและข้อมูลสนาม/`; `yolo trial/`, `bridge_damage_yolo_rtdetr/`, `rawdata/งานของรุ่นพี่/`, `rawdata/02 Methodology & Work/` -> `05_โค้ดและการทดลอง/`; `docs/*.md` -> `02_สรุปและบันทึกประกอบการเขียน/2_...`; `workmen's_diary/` -> `06_บันทึกงานรายวัน/`.

Don't read whole PDFs into context speculatively — ask which file/section is relevant, or use the "อ่านก่อน" files as the entry point. `03_เปเปอร์งานวิจัย/` is ~650MB.

## Known housekeeping (ask before touching)

- Large folders (04, 05/โค้ดและโมเดลของรุ่นพี่) are git-ignored; 03 is NOT ignored (~650MB) — decide before `git add`.
- Git history still holds the pre-reorg paths; the reorg itself is uncommitted.

## Workmen's Diary

Day-by-day log of what changed and why — see [../06_บันทึกงานรายวัน/README.md](../06_บันทึกงานรายวัน/README.md) for format/rules. Check the most recent file(s) there before starting work; add your own entry when you finish a session.

## Working conventions

- Comments/docs mix Thai and English — follow existing usage per file/folder.
- Research + report-writing project, not application code — most work is literature synthesis, writing chapters, or model/data work under `05_โค้ดและการทดลอง/`.
