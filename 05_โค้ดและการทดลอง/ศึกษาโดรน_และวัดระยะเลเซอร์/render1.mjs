import puppeteer from 'puppeteer-core'
import { pathToFileURL } from 'node:url'
import { resolve } from 'node:path'
const b=await puppeteer.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true,args:['--disable-gpu']})
const p=await b.newPage()
await p.goto(pathToFileURL(resolve(process.argv[2])).href,{waitUntil:'networkidle0'})
await p.evaluateHandle('document.fonts.ready')
await p.pdf({path:resolve(process.argv[3]),format:'A4',printBackground:true,margin:{top:'12mm',bottom:'12mm',left:'12mm',right:'12mm'}})
await p.setViewport({width:794,height:1123,deviceScaleFactor:2})
await p.screenshot({path:resolve(process.argv[4]),fullPage:true})
await b.close(); console.log('ok')
