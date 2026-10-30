#!/bin/sh
# ประกอบ src/part*.html -> report.html -> PDF
# ต้องมี: Node.js, Microsoft Edge, ฟอนต์ Leelawadee UI (มากับ Windows)
set -e
cd "$(dirname "$0")"

# puppeteer-core เล็กมาก (ไม่โหลด Chromium) — ขับ Edge ที่มีอยู่แล้วในเครื่อง
[ -d node_modules/puppeteer-core ] || npm i --silent puppeteer-core

python - <<'PY'
import io
order=['part1.html','part2.html','part_verified.html','part3.html','part4.html','part4b.html',
       'part_appendix.html','part5_refs.html','part6_open.html']
buf=[io.open('src/'+f,encoding='utf-8').read() for f in order]
buf.append('\n</body>\n</html>\n')
io.open('report.html','w',encoding='utf-8').write('\n\n'.join(buf))
PY
node render.mjs report.html UAV_platform_and_ranging_study.pdf
