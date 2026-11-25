# เก็บภาพหน้าจอโปรแกรมสำหรับใส่ใน PDF (ไม่ทำเนื้อภาพเป็นสีดำ — ไฟล์เก็บในเครื่อง ไม่ได้เปิดดูในแชต)
# พร้อมตรวจตัวเตือน "รอยต่อเปราะ" จาก DOM
import glob, json
from playwright.sync_api import sync_playwright

DONE_JS = "() => document.querySelector('#status').textContent.startsWith('เสร็จใน') || !!document.querySelector('.banner.bad')"
OUT = '../doc2/'
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge')
    pg = b.new_page(viewport={'width': 1320, 'height': 900}, device_scale_factor=1.5)
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:8765/')
    pg.set_input_files('#file', sorted(glob.glob('t21/*.JPG')))
    pg.wait_for_function(DONE_JS, timeout=240000)
    pg.wait_for_timeout(800)
    pg.locator('section.card').first.screenshot(path=OUT + 'ui_input.png')
    pg.locator('#seg0').screenshot(path=OUT + 'ui_result.png')
    pg.locator('#stats').screenshot(path=OUT + 'ui_stats.png')
    print('21 ภาพ:', pg.inner_text('#status'), '| banners:', pg.locator('#banners .banner').count())
    # ชุดซ้อนน้อย: ต้องมีป้ายตัดคู่หลอก
    pg.click('#clearBtn')
    pg.set_input_files('#file', sorted(glob.glob('t13/*.JPG')))
    pg.wait_for_timeout(500)
    pg.wait_for_function(DONE_JS, timeout=240000)
    print('13 ภาพ:', [x[:90] for x in pg.locator('#banners .banner').all_inner_texts()])
    pg.click('#detail > summary')
    print('   ป้ายในตาราง:', pg.evaluate("[...document.querySelectorAll('#pairBody .chip')].map(c => c.textContent).reduce((a, t) => (a[t] = (a[t] || 0) + 1, a), {})"))
    b.close()
print('console errors:', errs)
