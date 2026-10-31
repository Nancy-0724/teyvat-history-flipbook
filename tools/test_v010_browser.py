#!/usr/bin/env python3
"""Embedded Chromium smoke tests, not a deployment/CDN/device certification.
Real source HTML/CSS/JS and SVG bytes are used; test-only navigation hooks,
SVG data URIs, offline flag and in-memory localStorage live only in this fixture.
"""
from pathlib import Path
import re,json,base64,shutil,sys
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1]; OUT=R/'docs/qa-v010'; OUT.mkdir(exist_ok=True)
ONLY=sys.argv[1] if len(sys.argv)>1 else 'desktop'; KEY='teyvat-reader-position-v03'
result={'viewport':ONLY,'mode':'Embedded real HTML/CSS/JS; local SVG bytes as data URIs; CSS fallback; memory storage fixture',
'limits':['Local HTTP navigation was blocked by browser administrator policy (ERR_BLOCKED_BY_ADMINISTRATOR).','StPageFlip CDN, external images, Windows file://, physical phones and persistent disk storage not tested.'],'checks':[],'errors':[]}
source=(R/'index.html').read_text().replace('<link rel="stylesheet" href="./css/style.css">','<style>'+(R/'css/style.css').read_text()+'</style>')
source=re.sub(r'<script defer src="https://[^\"]+"></script>','',source)
source=re.sub(r'<script defer src="\./([^\"]+)"></script>',lambda m:'<script>'+(R/m.group(1)).read_text().replace('</script','<\\/script')+'</script>',source)
for p in (R/'assets').rglob('*.svg'):
 source=source.replace('./'+p.relative_to(R).as_posix(),'data:image/svg+xml;base64,'+base64.b64encode(p.read_bytes()).decode())
source=source.replace('  buildOutline();buildToc();','  window.__qaGo=(loc)=>jumpTo(findPage(loc));\n  window.__qaFind=findPage;\n  window.__qaDoc=()=>doc;\n  buildOutline();buildToc();')
compiled=json.loads(re.search(r'window\.TEYVAT_CONTENT\s*=\s*(\{.*\});\s*$',(R/'js/generated-content.js').read_text(),re.S).group(1))
figure=next(b for b in compiled['5']['blocks'] if b['kind']=='figure')
redirects=json.loads((R/'docs/CH05_INTEGRATION_V010.json').read_text())['new_block_redirects']

def ck(name,ok=True,**data):
 result['checks'].append({'name':name,'passed':bool(ok),**data})
 assert ok,name

def load(page,loc=None,fragment='chapter-5'):
 fixture='''<script>
 const memory=new Map(Object.entries(INITIAL));
 Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>memory.get(k)??null,setItem:(k,v)=>memory.set(k,String(v)),removeItem:k=>memory.delete(k),clear:()=>memory.clear()}});
 Object.defineProperty(navigator,'onLine',{configurable:true,get:()=>false});
 window.location.hash=FRAGMENT;
 </script>'''.replace('INITIAL',json.dumps({KEY:json.dumps(loc,ensure_ascii=False)} if loc else {},ensure_ascii=False)).replace('FRAGMENT',json.dumps('#'+fragment))
 page.goto('about:blank');page.set_content(source.replace('<head>','<head>'+fixture,1),wait_until='domcontentloaded')
 page.wait_for_function('window.__qaGo && window.__teyvatDiagnostics && !document.querySelector("#reader").hidden')
 page.wait_for_timeout(100)

def go(page,loc):
 page.evaluate('(loc)=>window.__qaGo(loc)',loc)
 page.wait_for_timeout(60)

def saved(page): return page.evaluate('(k)=>JSON.parse(localStorage.getItem(k))',KEY)

try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  viewport={'width':1440,'height':900} if ONLY=='desktop' else {'width':390,'height':844}
  ctx=browser.new_context(viewport=viewport,device_scale_factor=1)
  ctx.route('https://**/*',lambda r:r.abort());ctx.route('http://**/*',lambda r:r.abort())
  page=ctx.new_page();page.set_default_timeout(10000);page.on('pageerror',lambda e:result['errors'].append(str(e)))
  load(page)
  diag=page.evaluate('window.__teyvatDiagnostics');ck('book_initialized',diag['chapterCount']==60 and diag['partCount']==8,pages=diag['pageCount'])
  ck('CSS_fallback',page.locator('#book.fallback-mode').count()==1)
  ck('five_draft_chapters',page.evaluate('Object.values(window.TEYVAT_CONTENT).filter(x=>x.status==="draft").length')==5)
  page.locator('#top-toc').click();page.locator('#toc-search').fill('人類');ck('toc_search',page.locator('.toc-entry[data-chapter="5"]').is_visible())
  page.locator('.toc-entry[data-chapter="5"]').click();ck('toc_jump', '第 05 章' in page.locator('#current-location').inner_text() and page.locator('#toc-drawer').is_hidden())
  for sec in ['ch05-outline','ch05-harvest','ch05-angels','ch05-cities','ch05-learning','ch05-supplements','ch05-sources']:
   go(page,{'type':'body','chapterId':5,'sectionId':sec})
   ck('section_'+sec,page.locator('#'+sec).count()>0 and saved(page)['chapterId']==5)
   if sec=='ch05-angels':page.screenshot(path=str(OUT/f'{ONLY}-angels.png'))
  go(page,{'type':'body','chapterId':5,'sectionId':figure['sectionId'],'blockId':figure['blockId']})
  btn=page.locator('#book .zoom-image[data-caption^="圖 5-1"]').first
  btn.scroll_into_view_if_needed();page.wait_for_function('(()=>{const i=document.querySelector("#book .ch05-figure img");return i&&i.complete&&i.naturalWidth>0})()')
  ck('local_figure_load',btn.locator('img').evaluate('(e)=>e.naturalWidth')==1200)
  ck('figure_not_cropped',btn.locator('img').evaluate('(e)=>getComputedStyle(e).objectFit')=='contain')
  page.screenshot(path=str(OUT/f'{ONLY}-figure-5-1.png'))
  before=saved(page);counter=page.locator('#page-count').inner_text();btn.click();ck('figure_zoom',page.locator('#picture-layer').is_visible())
  page.wait_for_function('document.querySelector("#picture-large").naturalWidth>0')
  page.screenshot(path=str(OUT/f'{ONLY}-figure-5-1-zoom.png'))
  page.locator('#picture-dismiss').click();ck('figure_close_preserves_location',page.locator('#picture-layer').is_hidden() and before==saved(page) and counter==page.locator('#page-count').inner_text())
  # Exercise each rewritten/removed block through the actual reader resolver.
  for item in redirects:
   req={'type':'body','chapterId':item['chapterId'],'sectionId':'old-unknown','blockId':item['oldBlockId']}
   out=page.evaluate('loc=>{const d=__qaDoc();const p=__qaFind(loc);return {p,meta:d.pageInfo[p]}}',req)
   expected=page.evaluate('(t)=>__qaDoc().sectionStarts[t]',f'{item["chapterId"]}:{item["sectionId"]}')
   ck('old_block_'+item['oldBlockId'],out['p']==expected and out['meta']['chapterId']==item['chapterId'])
  for cid,sec,targetcid,targetsec in [(1,'ch01-humanity',5,'ch05-outline'),(5,'ch05-todo',5,'ch05-outline'),(1,'ch01-naberius',4,'ch04-naberius'),(1,'ch01-phanes',3,'ch03-arrival')]:
   out=page.evaluate('loc=>__qaFind(loc)',{'type':'body','chapterId':cid,'sectionId':sec})
   target=page.evaluate('key=>__qaDoc().sectionStarts[key]',f'{targetcid}:{targetsec}')
   ck('legacy_section_'+sec,out==target)
  # Inspect all chapter-5 leaves, including supplementary material and sources.
  indices=page.evaluate('__qaDoc().pageInfo.filter(p=>p.chapterId===5).map(p=>p.index)')
  overflow=[]
  for idx in indices:
   go(page,{'type':'page','index':idx})
   visible=page.locator('#book .page-body').evaluate_all('(els)=>els.filter(e=>e.getBoundingClientRect().width>0&&e.getBoundingClientRect().height>0).map(e=>({v:e.scrollHeight-e.clientHeight,h:e.scrollWidth-e.clientWidth,text:e.innerText.slice(0,220)}))')
   overflow.extend({'page':idx,**x} for x in visible if x['v']>2 or x['h']>2)
  ck('chapter5_layout',not overflow,chapter_pages=len(indices),overflow=overflow)
  go(page,{'type':'body','chapterId':5,'sectionId':'ch05-angels'});marker=page.locator('#page-count').inner_text()
  page.keyboard.press('ArrowRight');page.wait_for_timeout(850);ck('keyboard_next',page.locator('#page-count').inner_text()!=marker)
  page.keyboard.press('ArrowLeft');page.wait_for_timeout(850);ck('keyboard_back',page.locator('#page-count').inner_text()==marker)
  resume=saved(page);load(page,resume,'read');ck('resume_from_storage_fixture',saved(page)==resume)
  # Deep-link parsing on fresh initialization, not merely the test navigation hook.
  load(page,fragment='ch01-humanity');ck('actual_legacy_hash_init',saved(page)['chapterId']==5)
  ck('javascript_no_errors',not result['errors'],errors=result['errors'])
  browser.close()
 result['passed']=True
finally:
 (OUT/f'browser-results-{ONLY}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'viewport':ONLY,'passed':result.get('passed',False),'checks':len(result['checks']),'errors':result['errors']},ensure_ascii=False))
