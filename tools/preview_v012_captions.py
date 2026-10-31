#!/usr/bin/env python3
"""Render captions using the user's supplied screenshot as preview-only image fixtures.
The cropped images never enter assets/game-media and do not replace original sources.
"""
from pathlib import Path
import base64,io,json,shutil
from PIL import Image
from playwright.sync_api import sync_playwright
import test_v012_browser as qa

R=Path(__file__).resolve().parents[1];O=R/'docs/qa-v012'
im=Image.open(O/'user-before.png')
# These are the two images in the user's screenshot, not newly downloaded assets.
boxes={'angel-example':(55,130,335,285),'ordinary-seelie':(347,130,626,285)}
db=json.loads((R/'assets/game-media/sources.json').read_text())
for item in db['images']:
    if item['id'] not in boxes:continue
    b=io.BytesIO();im.crop(boxes[item['id']]).save(b,format='PNG')
    uri='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
    for u in item['urls']:qa.source=qa.source.replace(u,uri)
pair=next(b for b in qa.compiled['5']['blocks'] if 'media-pair' in b['html'])
results=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    for name,vp in [('desktop',{'width':1440,'height':900}),('mobile',{'width':390,'height':844}),('small-mobile',{'width':360,'height':640})]:
        ctx=browser.new_context(viewport=vp,device_scale_factor=2)
        ctx.route('https://**/*',lambda r:r.abort());ctx.route('http://**/*',lambda r:r.abort())
        p=ctx.new_page();qa.load(p,simulate=True);qa.go(p,{'type':'body','chapterId':5,'blockId':pair['blockId']})
        p.wait_for_function('''()=>{const es=[...document.querySelectorAll('#book .media-pair img')];return es.length===2&&es.every(e=>e.complete&&e.naturalWidth>0&&e.src.startsWith('data:image/png'))}''')
        figure=p.locator('#book .media-pair');figure.scroll_into_view_if_needed()
        leaf=figure.locator('xpath=ancestor::*[contains(concat(" ",normalize-space(@class)," ")," book-page ")]').first
        leaf.screenshot(path=str(O/f'{name}-short-captions.png'))
        figure.screenshot(path=str(O/f'{name}-caption-detail.png'))
        metrics=figure.evaluate('''e=>({caption:e.innerText.trim(),height:e.getBoundingClientRect().height,imageHeight:e.querySelector('img').getBoundingClientRect().height,captionHeight:e.querySelector('figcaption').getBoundingClientRect().height})''')
        results.append({'viewport':vp,**metrics})
        if name=='mobile':
            figure.locator('[data-game-id="angel-example"]').click();p.screenshot(path=str(O/'mobile-zoom-sources.png'))
        ctx.close()
    browser.close()
(O/'preview-metrics.json').write_text(json.dumps({'image_basis':'Two crops from user-before.png, preview fixtures only; not included as source image files.','results':results},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False))
