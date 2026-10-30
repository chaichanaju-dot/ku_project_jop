import puppeteer from 'puppeteer-core'
import { pathToFileURL } from 'node:url'
import { resolve } from 'node:path'

const [src, out] = process.argv.slice(2)
if (!src || !out) { console.error('usage: node render.mjs <in.html> <out.pdf>'); process.exit(1) }

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'

const browser = await puppeteer.launch({ executablePath: EDGE, headless: true, args: ['--disable-gpu', '--allow-file-access-from-files'] })
const page = await browser.newPage()
await page.goto(pathToFileURL(resolve(src)).href, { waitUntil: 'networkidle0' })
await page.evaluateHandle('document.fonts.ready')
await page.pdf({
  path: resolve(out),
  format: 'A4',
  printBackground: true,
  margin: { top: '18mm', bottom: '20mm', left: '18mm', right: '18mm' },
  displayHeaderFooter: true,
  headerTemplate: '<div></div>',
  footerTemplate: `<div style="width:100%;font-family:'Leelawadee UI',Tahoma,sans-serif;font-size:8pt;color:#888;padding:0 18mm;display:flex;justify-content:space-between;">
    <span>UAV + AI Crack Inspection — Platform &amp; Ranging Study</span>
    <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
  </div>`,
})
await browser.close()
console.log('ok ->', resolve(out))
