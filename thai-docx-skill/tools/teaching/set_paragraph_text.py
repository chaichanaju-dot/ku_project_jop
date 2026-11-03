#!/usr/bin/env python3
"""Replace a whole paragraph's text, for when the old wording has to go entirely.

Diff-aligned find/replace is right for correcting numbers inside a sentence, and
wrong for discarding a paragraph: a paragraph of a worked example is a chain of
prose runs and small equation zones, and a rewrite long enough to have no common
substrings gets scattered across both. Thai then lands inside <m:t>, where it
renders in Cambria Math with its vowel marks misplaced.

This drops every run in the paragraph and writes one prose run instead, cloning the
run properties of the paragraph's first prose run so the result matches the page.
Use it only when the replacement is prose; equations belong in the other tools.

Usage: set_paragraph_text.py <in.docx> <out.docx> <spec.json> [--dry-run]
    spec.json: [{"find": "<text the paragraph starts with>", "text": "..."}, ...]
               "text": null deletes the paragraph, unless it carries a comment
               {"insert_before": "...", "label": "...", "text": "..."} adds a new
               paragraph above that one, cloning its layout and its bold run style
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
# 32 half-points is the book's body size since he asked for 16 pt on 2026-08-10; a
# rebuilt run that falls back to the old 28 lands two points under everything round it
FALLBACK_RPR = ('<w:rPr><w:rFonts w:ascii="TH Sarabun New" w:hAnsi="TH Sarabun New" '
                'w:cs="TH Sarabun New"/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr>')


def paragraphs(doc: str):
    """(start, end) of each <w:p>, tracking textbox nesting so labels drawn inside
    a figure are not mistaken for the end of the paragraph that contains them."""
    # a self-closing <w:p .../> is an empty paragraph, not an opening tag. Word writes
    # them freely; reading one as an open tag left the depth count permanently unbalanced
    # and the whole scan returned nothing
    tok = re.compile(r"<w:p(?:\s[^>]*[^/])?>|<w:p\s[^>]*/>|</w:p>"
                     r"|<w:txbxContent>|</w:txbxContent>")
    stack, box = [], 0
    for m in tok.finditer(doc):
        t = m.group(0)
        if t == "<w:txbxContent>":
            box += 1
        elif t == "</w:txbxContent>":
            box -= 1
        elif t.startswith("</"):
            if stack:
                s = stack.pop()
                if not stack:
                    yield s, m.end()
        elif t.endswith("/>"):
            if not stack:            # an empty paragraph, opened and closed at once
                yield m.start(), m.end()
        else:
            stack.append(m.start())


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text_of(frag: str) -> str:
    s = "".join(re.findall(r"<[wm]:t[^>]*>([^<]*)</[wm]:t>", frag)).replace(ZWSP, "")
    for ent, ch in (("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'),
                    ("&apos;", "'"), ("&amp;", "&")):
        s = s.replace(ent, ch)
    return s


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    sys.stdout.reconfigure(encoding="utf-8")
    src, dst, spec = Path(args[0]), Path(args[1]), Path(args[2])
    jobs = json.loads(spec.read_text(encoding="utf-8"))

    zin = zipfile.ZipFile(src)
    doc = zin.read("word/document.xml").decode("utf-8")
    dropped: set[str] = set()

    for job in jobs:
        if "delete_from" in job:
            # removing a whole worked example means removing dozens of paragraphs,
            # most of them equations whose extracted text is impractical to name
            paras = list(paragraphs(doc))
            a = [k for k, (i, j) in enumerate(paras)
                 if text_of(doc[i:j]).startswith(job["delete_from"])]
            b = [k for k, (i, j) in enumerate(paras)
                 if text_of(doc[i:j]).startswith(job["delete_to"])]
            if len(a) != 1 or len(b) != 1:
                raise SystemExit(f"[{len(a)}/{len(b)} paragraphs] range "
                                 f"{job['delete_from'][:34]!r} .. {job['delete_to'][:34]!r}")
            i, j = paras[a[0]][0], paras[b[0]][1]
            span = doc[i:j]
            ids = re.findall(r'<w:commentRangeStart w:id="(\d+)"', span)
            if ids and not job.get("drop_comments"):
                raise SystemExit(f"range carries comment(s) {ids}")
            if "<w:drawing>" in span and not job.get("drop_figures"):
                raise SystemExit('range contains a figure; pass "drop_figures": true '
                                 "if it should go too")
            doc = doc[:i] + doc[j:]
            dropped.update(ids)
            print(f"  deleted {b[0]-a[0]+1} paragraphs: "
                  f"{job['delete_from'][:30]!r} .. {job['delete_to'][:30]!r}")
            continue
        if "append_to" in job:
            # a sentence that explains an equation belongs after it in the same
            # paragraph; writing it through the run map instead would land it inside
            # the equation's <m:t>, where Thai renders in Cambria Math
            hits = [(i, j) for i, j in paragraphs(doc)
                    if text_of(doc[i:j]).startswith(job["append_to"])]
            if len(hits) != 1:
                raise SystemExit(f"[{len(hits)} paragraphs] start {job['append_to'][:60]!r}")
            i, j = hits[0]
            para = doc[i:j]
            rpr = re.search(r"<w:r(?:\s[^>]*)?>\s*(<w:rPr>(?:(?!<w:i/>).)*?</w:rPr>)\s*<w:t",
                            para, re.S)
            run = (f'<w:r>{rpr.group(1) if rpr else FALLBACK_RPR}'
                   f'<w:t xml:space="preserve">{esc(job["text"])}</w:t></w:r>')
            doc = doc[:j - len("</w:p>")] + run + doc[j - len("</w:p>"):]
            print(f"  appended to {text_of(para)[:40]!r}: {job['text'][:44]}")
            continue
        if "insert_before" in job:
            hits = [(i, j) for i, j in paragraphs(doc)
                    if text_of(doc[i:j]).startswith(job["insert_before"])]
            if len(hits) != 1:
                raise SystemExit(f"[{len(hits)} paragraphs] start "
                                 f"{job['insert_before'][:60]!r}")
            i, j = hits[0]
            model = doc[i:j]
            ppr = re.search(r"<w:pPr>.*?</w:pPr>", model, re.S)
            head = re.match(r"<w:p(?:\s[^>]*)?>", model).group(0)
            bold = re.search(r"(<w:rPr>(?:(?!</w:rPr>).)*?<w:b/>.*?</w:rPr>)", model, re.S)
            plain = re.search(r"<w:r(?:\s[^>]*)?>\s*(<w:rPr>.*?</w:rPr>)\s*<w:t", model, re.S)
            runs = ""
            if job.get("label"):
                runs += (f'<w:r>{bold.group(1) if bold else FALLBACK_RPR}'
                         f'<w:t xml:space="preserve">{esc(job["label"])}</w:t></w:r>')
            if job.get("text"):
                runs += (f'<w:r>{plain.group(1) if plain else FALLBACK_RPR}'
                         f'<w:t xml:space="preserve">{esc(job["text"])}</w:t></w:r>')
            doc = doc[:i] + head + (ppr.group(0) if ppr else "") + runs + "</w:p>" + doc[i:]
            print(f"  inserted before {text_of(model)[:44]!r}: {job.get('label', '')[:40]}")
            continue
        hits = [(i, j) for i, j in paragraphs(doc)
                if text_of(doc[i:j]).startswith(job["find"])]
        if len(hits) != 1:
            raise SystemExit(f"[{len(hits)} paragraphs] start {job['find'][:60]!r}")
        i, j = hits[0]
        para = doc[i:j]
        if job["text"] is None:
            ids = re.findall(r'<w:commentRangeStart w:id="(\d+)"', para)
            if ids and not job.get("drop_comments"):
                raise SystemExit(f"paragraph carries comment(s) {ids}; delete them too "
                                 f'with "drop_comments": true, or rewrite instead: '
                                 f"{job['find'][:50]!r}")
            doc = doc[:i] + doc[j:]
            dropped.update(ids)
            print(f"  deleted : {text_of(para)[:56]!r}"
                  + (f"   (with comment {', '.join(ids)})" if ids else ""))
            continue
        m_ppr = re.search(r"<w:pPr>.*?</w:pPr>", para, re.S)
        m_rpr = re.search(r"<w:r(?:\s[^>]*)?>\s*(<w:rPr>.*?</w:rPr>)\s*<w:t", para, re.S)
        head = re.match(r"<w:p(?:\s[^>]*)?>", para).group(0)
        ppr_text = m_ppr.group(0) if m_ppr else ""
        if "label" in job:
            # a heading demoted to body text keeps its paragraph but loses the style
            # that made it bold, so the label carries bold run properties of its own
            ppr_text = re.sub(r"<w:pStyle[^/]*/>|<w:outlineLvl[^/]*/>", "", ppr_text)
            bold = FALLBACK_RPR.replace("</w:rPr>", "<w:b/><w:bCs/></w:rPr>")
            run = f'<w:r>{bold}<w:t xml:space="preserve">{esc(job["label"])}</w:t></w:r>'
            if job["text"]:
                run += (f'<w:r>{FALLBACK_RPR}'
                        f'<w:t xml:space="preserve">{esc(job["text"])}</w:t></w:r>')
        else:
            run = (f'<w:r>{m_rpr.group(1) if m_rpr else FALLBACK_RPR}'
                   f'<w:t xml:space="preserve">{esc(job["text"])}</w:t></w:r>')
        # a comment anchored here outlives the wording it was attached to; dropping
        # the range markers with the runs would orphan the entry in comments.xml
        opens = "".join(re.findall(r"<w:commentRangeStart[^>]*/>", para))
        closes = "".join(re.findall(r"<w:commentRangeEnd[^>]*/>", para))
        refs = "".join(re.findall(
            r"<w:r(?:\s[^>]*)?>(?:(?!</w:r>).)*?<w:commentReference[^>]*/>.*?</w:r>",
            para, re.S))
        # a caption's number is a SEQ field, not text: rewriting the wording must keep
        # the "รูปที่ N." lead-in and the field whole, or the figure loses its number
        field = ""
        if "SEQ " in para:
            end = para.find('<w:fldChar w:fldCharType="end"/>')
            field = para[:para.find("</w:r>", end) + len("</w:r>")]
            field = field[field.index("</w:pPr>") + len("</w:pPr>"):] if "</w:pPr>" in field \
                else field[len(head):]
            run = run.replace("<w:t xml:space=\"preserve\">", "<w:t xml:space=\"preserve\"> ", 1)
        doc = (doc[:i] + head + ppr_text
               + opens + field + run + closes + refs + "</w:p>" + doc[j:])
        if opens:
            print(f"    (kept {len(re.findall('<w:commentRangeStart', opens))} comment anchor(s))")
        print(f"  replaced: {text_of(para)[:56]!r}")

    comments = None
    if dropped:
        comments = zin.read("word/comments.xml").decode("utf-8")
        for cid in dropped:
            comments = re.sub(rf'<w:comment [^>]*w:id="{cid}"[^>]*>.*?</w:comment>',
                              "", comments, count=1, flags=re.S)
        minidom.parseString(comments.encode("utf-8"))
        print(f"  comments.xml: removed {len(dropped)} entr(y|ies) {sorted(dropped)}")

    minidom.parseString(doc.encode("utf-8"))
    if dry:
        print("(dry run, nothing written)")
        return
    tmp = dst.with_suffix(".docx.tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == "word/document.xml":
                data = doc.encode("utf-8")
            elif item.filename == "word/comments.xml" and comments is not None:
                data = comments.encode("utf-8")
            else:
                data = zin.read(item.filename)
            zout.writestr(item, data)
    zin.close()
    if dst.exists():
        dst.unlink()
    shutil.move(str(tmp), str(dst))
    print(f"output: {dst}  ({dst.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
