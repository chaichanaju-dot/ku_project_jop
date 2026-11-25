# ทดสอบหน้าเว็บใน Edge จริง: ใส่ภาพชื่อมั่ว → ต้องได้ผืนและลำดับถูกเอง
# ภาพหน้าจอถูกทำให้เนื้อภาพเป็นสีดำก่อนถ่าย (ดูเฉพาะการจัดวางหน้าจอ ไม่ดูเนื้อภาพ)
import glob, json, sys, time
from playwright.sync_api import sync_playwright

key = json.load(open('key.json'))
MASK = 'img{filter:brightness(0)!important}'
SUMMARY_JS = """() => ({
  status: document.querySelector('#status').textContent,
  stats: [...document.querySelectorAll('.stat')].map(s => s.innerText.replace(/\\n+/g, ' | ')),
  banners: [...document.querySelectorAll('#banners .banner')].map(b => b.innerText.slice(0, 150)),
  segs: [...document.querySelectorAll('#segs > section')].map(s => ({id: s.id, title: s.querySelector('h2').innerText,
         names: [...s.querySelectorAll('.strip li')].map(li => li.title), check: (s.querySelector('.check') || {}).innerText || ''})),
  funnel: document.querySelector('#funnel').innerText,
  rows: document.querySelectorAll('#pairBody tr').length,
  overflow: document.documentElement.scrollWidth - innerWidth })"""
DONE_JS = "() => document.querySelector('#status').textContent.startsWith('เสร็จใน') || !!document.querySelector('.banner.bad')"


def order_ok(names):
    v = [int(key[n].replace('N:', '')) for n in names]
    return v == sorted(v) or v == sorted(v, reverse=True)


def wait_done(pg, timeout=240000):
    pg.wait_for_function(DONE_JS, timeout=timeout)


def clear_status(pg):
    pg.evaluate("document.querySelector('#status').textContent = ''")


errs = []
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge')
    pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:8765/')
    pg.add_style_tag(content=MASK)
    pg.screenshot(path='shot_a0_empty.png')

    # A: 21 ภาพ ชื่อมั่ว → ต่อเองทันที
    t = time.time()
    pg.set_input_files('#file', sorted(glob.glob('t21/*.JPG')))
    pg.wait_for_timeout(1500)
    pg.screenshot(path='shot_a1_prep.png')
    wait_done(pg)
    dt = time.time() - t
    s = pg.evaluate(SUMMARY_JS)
    print('A) 21 ภาพ ชื่อมั่ว: ใช้เวลารวม %.1f วิ |' % dt, s['status'])
    print('   ', s['stats'])
    print('    banners', s['banners'])
    print('    funnel:', s['funnel'][:260])
    for g in s['segs']:
        print('   ', g['id'], g['title'], '| ลำดับถูก:', order_ok(g['names']), '|', ' '.join(key[n] for n in g['names']))
        print('    check:', g['check'].replace('\n', ' / ')[:360])
    print('    rows', s['rows'], 'overflow', s['overflow'])
    pg.wait_for_timeout(600)
    pg.screenshot(path='shot_a2_result.png')
    pg.locator('#seg0').screenshot(path='shot_a3_seg.png')
    # โต้ตอบ
    pg.click('#seg0 .strip li:nth-child(5)')
    print('    strip click → hl', pg.locator('polygon.hl').count(), 'sel', pg.locator('.strip li.sel').count())
    pg.click('#detail > summary')
    pg.click('#pairBody tr:nth-child(3)')
    pg.wait_for_timeout(500)
    print('    row click → hl', pg.locator('polygon.hl').count())
    pg.locator('#detail').screenshot(path='shot_a4_detail.png')
    pg.check('#seg0 [data-t="heat"]')
    pg.click('#seg0 [data-z="fit"]')
    pg.wait_for_timeout(300)
    pg.locator('#seg0').screenshot(path='shot_a5_heat_fit.png')
    with pg.expect_download() as d:
        pg.click('#csvBtn')
    print('    csv', d.value.suggested_filename)
    with pg.expect_download() as d:
        pg.click('#seg0 a.btn.primary')
    print('    download', d.value.suggested_filename)
    # เอาภาพออก 1 ภาพ → ต้องต่อใหม่เอง เหลือ 20
    clear_status(pg)
    pg.click('#thumbs .thumb:nth-child(4) .x', force=True)
    wait_done(pg)
    s = pg.evaluate(SUMMARY_JS)
    print('    หลังเอาออก 1 ภาพ:', s['stats'][0], '| ลำดับถูก:', order_ok(s['segs'][0]['names']))
    pg.set_viewport_size({'width': 1280, 'height': 900})
    pg.wait_for_timeout(300)
    print('    overflow@1280:', pg.evaluate('document.documentElement.scrollWidth - innerWidth'))

    # B: เพิ่มอีก 13 ภาพ (รอบบินที่ 1) → รวมสองรอบ
    pg.set_viewport_size({'width': 1440, 'height': 900})
    clear_status(pg)
    t = time.time()
    pg.set_input_files('#file', sorted(glob.glob('t13/*.JPG')))
    pg.wait_for_timeout(500)
    wait_done(pg)
    dt = time.time() - t
    s = pg.evaluate(SUMMARY_JS)
    print('B) เพิ่ม 13 ภาพของอีกรอบบิน: %.1f วิ |' % dt, s['status'])
    print('   ', s['stats'])
    print('    banners', s['banners'])
    for g in s['segs']:
        print('   ', g['id'], g['title'], '|', ' '.join(key[n] for n in g['names']))
        print('    check:', g['check'].replace('\n', ' / ')[:360])
    pg.screenshot(path='shot_b_result.png')

    # C: ล้าง แล้วใส่เฉพาะรอบบินที่ 1 (ภาพซ้อนน้อย)
    pg.click('#clearBtn')
    print('C) ล้างแล้ว: results hidden =', pg.evaluate("document.querySelector('#results').hidden"), '| thumbs', pg.locator('.thumb').count())
    pg.set_input_files('#file', sorted(glob.glob('t13/*.JPG')))
    pg.wait_for_timeout(500)
    wait_done(pg)
    s = pg.evaluate(SUMMARY_JS)
    print('   ', s['stats'])
    print('    banners', s['banners'])
    for g in s['segs']:
        print('   ', g['id'], g['title'], '|', ' '.join(key[n] for n in g['names']))
    pg.evaluate("window.scrollTo(0, document.querySelector('#results').offsetTop - 10)")
    pg.wait_for_timeout(300)
    pg.screenshot(path='shot_c_result.png')
    pg.locator('#lone').screenshot(path='shot_c_lone.png')
    pg.close()

    # D: ภาพที่ไม่มี metadata (ย่อแล้ว EXIF หาย) + โหมดมืด + ปิดต่ออัตโนมัติ
    pg = b.new_page(viewport={'width': 1440, 'height': 900}, color_scheme='dark')
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:8765/')
    pg.add_style_tag(content=MASK)
    pg.click('#adv > summary')
    pg.uncheck('#auto')
    small = [f for f in sorted(glob.glob('small/*.jpg')) if 'N_' not in f]
    pg.set_input_files('#file', small)
    pg.wait_for_function('document.querySelectorAll(".thumb img").length === %d' % len(small), timeout=60000)
    pg.wait_for_timeout(1200)
    print('D) ปิดต่ออัตโนมัติ: results hidden =', pg.evaluate("document.querySelector('#results').hidden"), '| ปุ่มกดได้ =', pg.is_enabled('#runBtn'))
    pg.click('#runBtn')
    wait_done(pg)
    s = pg.evaluate(SUMMARY_JS)
    print('   ', s['status'], s['stats'][:2])
    print('    banners', s['banners'])
    print('    funnel:', s['funnel'][-170:])
    print('    check block:', repr(s['segs'][0]['check'][:80]), '| names', len(s['segs'][0]['names']))
    pg.screenshot(path='shot_d_dark.png')
    b.close()
print('console errors:', errs)
