#!/usr/bin/env python3
"""Embedded Chromium QA: real project HTML/CSS/JS, CSS fallback and SVG bytes.
Requires Playwright + Chromium. In-memory storage is a test fixture; real CDN,
external image retrieval, real disk persistence and Windows are NOT tested.
"""
from pathlib import Path
import base64,json,re,shutil,sys
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];OUT=R/'docs/qa-v09';OUT.mkdir(exist_ok=True)
KEY='teyvat-reader-position-v03'
ONLY=sys.argv[1] if len(sys.argv)>1 else 'all'
results={'mode':'embedded project HTML/CSS/JS; SVG data URIs; in-memory storage fixture; CSS fallback',
'not_tested':['localhost/file navigation blocked by browser policy','StPageFlip CDN','third-party images','disk persistence','Windows/physical phones'],'checks':[],'errors':[]}
compiled=json.loads(re.search(r'window\.TEYVAT_CONTENT\s*=\s*(\{.*\});\s*$',(R/'js/generated-content.js').read_text(),re.S).group(1))
figures=[b for b in compiled['4']['blocks'] if b['kind']=='figure']
source=(R/'index.html').read_text().replace('<link rel="stylesheet" href="./css/style.css">','<style>'+(R/'css/style.css').read_text()+'</style>')
source=re.sub(r'<script defer src="https://[^\"]+"></script>','',source)
source=re.sub(r'<script defer src="\./([^\"]+)"></script>',lambda m:'<script>'+(R/m.group(1)).read_text().replace('</script','<\\/script')+'</script>',source)
for p in (R/'assets').rglob('*.svg'):
 uri='data:image/svg+xml;base64,'+base64.b64encode(p.read_bytes()).decode()
 source=source.replace('./'+p.relative_to(R).as_posix(),uri)
# Expose only test hooks in the embedded copy; production files remain unchanged.
source=source.replace('  buildOutline();buildToc();', '  window.__qaGo=(loc)=>jumpTo(findPage(loc));\n  buildOutline();buildToc();')
def load(page,fragment='read',loc=None):
 if page.evaluate('Boolean(window.__qaGo)'):
  target=loc
  if target is None and fragment.startswith('ch'):
   match=re.match(r'ch(\d{2})-',fragment)
   target={'type':'body','chapterId':int(match.group(1)),'sectionId':fragment}
  page.evaluate('(loc)=>window.__qaGo(loc)',target)
  page.wait_for_timeout(90)
  return
 fixture='''<script>
 const memory=new Map(Object.entries(INITIAL));
 Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>memory.get(k)??null,setItem:(k,v)=>memory.set(k,String(v)),removeItem:k=>memory.delete(k),clear:()=>memory.clear()}});
 Object.defineProperty(navigator,'onLine',{configurable:true,get:()=>false});
 window.location.hash=FRAGMENT;
 </script>'''.replace('INITIAL',json.dumps({KEY:json.dumps(loc,ensure_ascii=False)} if loc else {},ensure_ascii=False)).replace('FRAGMENT',json.dumps('#'+fragment))
 page.goto('about:blank')
 page.set_content(source.replace('<head>','<head>'+fixture,1),wait_until='domcontentloaded')
 page.wait_for_function('window.__teyvatDiagnostics && !document.querySelector("#reader").hidden')
 page.wait_for_timeout(80)
def saved(page):return page.evaluate('(k)=>JSON.parse(localStorage.getItem(k))',KEY)
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for label,viewport in [('desktop',{'width':1440,'height':900}),('mobile',{'width':390,'height':844})]:
   if ONLY!='all' and ONLY!=label:continue
   print('START',label,flush=True)
   ctx=browser.new_context(viewport=viewport,device_scale_factor=1)
   ctx.route('https://**/*',lambda route:route.abort());ctx.route('http://**/*',lambda route:route.abort())
   page=ctx.new_page();page.set_default_timeout(7000);page.set_default_navigation_timeout(7000);page.on('pageerror',lambda e:results['errors'].append(str(e)))
   load(page,'chapter-4')
   assert page.locator('#book.fallback-mode').count()==1
   diag=page.evaluate('window.__teyvatDiagnostics')
   assert diag['chapterCount']==60 and diag['partCount']==8
   results['checks'].append({'viewport':label,'book_initialized':True,'pages':diag['pageCount']})
   page.locator('#top-toc').click();page.locator('#toc-search').fill('四執政')
   assert page.locator('.toc-entry[data-chapter="4"]').is_visible()
   page.locator('.toc-entry[data-chapter="4"]').click()
   assert '第 04 章' in page.locator('#current-location').inner_text()
   assert page.locator('#toc-drawer').is_hidden()
   results['checks'].append({'viewport':label,'toc_search_and_jump':True})
   for i,b in enumerate(figures,1):
    print(label,'figure',i,flush=True)
    load(page,loc={'type':'body','chapterId':4,'sectionId':b['sectionId'],'blockId':b['blockId']})
    gid=re.search(r'data-game-id="([^"]+)"',b['html']).group(1)
    btn=page.locator(f'#book .zoom-image[data-game-id="{gid}"]').first
    assert btn.count()==1,(label,gid,'missing')
    img=btn.locator('img');img.scroll_into_view_if_needed()
    page.wait_for_function('(id)=>{const i=document.querySelector(`#book .zoom-image[data-game-id="${id}"] img`);return i&&i.complete&&i.naturalWidth>0}',arg=gid)
    assert img.get_attribute('src').startswith('data:image/svg+xml')
    count=page.locator('#page-count').inner_text();pos=saved(page)
    btn.click();assert page.locator('#picture-layer').is_visible()
    page.wait_for_function('document.querySelector("#picture-large").complete && document.querySelector("#picture-large").naturalWidth>0')
    if i==1:page.screenshot(path=str(OUT/f'{label}-figure-4-1-zoom.png'))
    page.locator('#picture-dismiss').click();assert page.locator('#picture-layer').is_hidden()
    assert page.locator('#page-count').inner_text()==count
    assert saved(page)==pos
    over=page.locator('#book .page-body').evaluate_all('(els)=>els.map(e=>e.scrollHeight-e.clientHeight)')
    results['checks'].append({'viewport':label,'figure':gid,'local_svg_loaded':True,'zoom_close_preserves_page':True,'overflow_px':over})
    if i in (1,2,4):page.screenshot(path=str(OUT/f'{label}-figure-4-{i}.png'))
   for fragment,target in [('ch01-naberius','ch04-naberius'),('ch01-ronova','ch04-ronova'),('ch01-istaroth','ch04-istaroth'),('ch01-asmoday','ch04-asmoday'),('ch04-todo','ch04-rules'),('ch01-phanes','ch03-arrival')]:
    print(label,'anchor',fragment,flush=True)
    load(page,fragment)
    assert saved(page)['chapterId']==(3 if fragment=='ch01-phanes' else 4)
    assert page.locator('#'+target).count()>0,(fragment,target)
    results['checks'].append({'viewport':label,'legacy_location_resolution':fragment,'target':target,'passed':True})
   mig=json.loads((R/'data/bookmark-migrations-v07.json').read_text())
   sample=next(k for k,v in mig['byBlock'].items() if k.startswith('c01-') and v['chapterId']==4)
   load(page,loc={'type':'body','chapterId':1,'sectionId':'ch01-naberius','blockId':sample})
   assert page.locator('#ch04-naberius').count()>0
   results['checks'].append({'viewport':label,'legacy_storage_record_specific_section':True})
   marker=page.locator('#page-count').inner_text()
   page.keyboard.press('ArrowRight');page.wait_for_timeout(850)
   assert page.locator('#page-count').inner_text()!=marker
   page.keyboard.press('ArrowLeft');page.wait_for_timeout(850)
   assert page.locator('#page-count').inner_text()==marker
   results['checks'].append({'viewport':label,'keyboard_forward_back':True})
   ctx.close()
  browser.close()
 assert not results['errors'],results['errors']
 results['passed']=True
finally:
 (OUT/f'browser-results-{ONLY}.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':results.get('passed',False),'checks':len(results['checks']),'errors':results['errors']},ensure_ascii=False))
