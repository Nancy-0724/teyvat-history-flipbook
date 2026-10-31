#!/usr/bin/env python3
"""Full-book embedded Chromium regression. No claims of live CDN/device testing.
Networking is denied by the execution environment; SVGs use original bytes via
fixture data URIs and storage uses a memory shim. A separate simulated-response
case tests successful swaps, without pretending fixture images are real photos.
"""
from pathlib import Path
import base64,html,json,re,shutil,sys,time
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'docs/qa-v012';O.mkdir(parents=True,exist_ok=True)
KEY='teyvat-reader-position-v03'
source=(R/'index.html').read_text().replace('<link rel="stylesheet" href="./css/style.css">','<style>'+(R/'css/style.css').read_text()+'</style>')
source=re.sub(r'<script defer src="https://[^"]+"></script>','',source)
source=re.sub(r'<script defer src="\./([^"]+)"></script>',lambda m:'<script>'+(R/m.group(1)).read_text().replace('</script','<\\/script')+'</script>',source)
for p in (R/'assets').rglob('*.svg'):
 source=source.replace('./'+p.relative_to(R).as_posix(),'data:image/svg+xml;base64,'+base64.b64encode(p.read_bytes()).decode())
source=source.replace('  buildOutline();buildToc();','  window.__qaGo=loc=>jumpTo(findPage(loc)); window.__qaFind=findPage; window.__qaDoc=()=>doc;\n  buildOutline();buildToc();')
compiled=json.loads(re.search(r'window\.TEYVAT_CONTENT\s*=\s*(\{.*\});\s*$',(R/'js/generated-content.js').read_text(),re.S).group(1))
figures=[]
for cid,item in compiled.items():
 for b in item['blocks']:
  if b['kind']=='figure':
   for caption in re.findall(r'data-caption="([^"]+)"',b['html']):figures.append((int(cid),b,html.unescape(caption)))

def load(page,loc=None,fragment='chapter-5',simulate=False):
 fixture='''<script>
 const memory=new Map(Object.entries(INITIAL));
 Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>memory.get(k)??null,setItem:(k,v)=>memory.set(k,String(v)),removeItem:k=>memory.delete(k),clear:()=>memory.clear()}});
 Object.defineProperty(navigator,'onLine',{configurable:true,get:()=>ONLINE});
 window.location.hash=FRAGMENT;
 </script>'''.replace('INITIAL',json.dumps({KEY:json.dumps(loc)} if loc else {})).replace('FRAGMENT',json.dumps('#'+fragment)).replace('ONLINE','true' if simulate else 'false')
 s=source
 if simulate:
  # Stub only candidate URLs with a neutral test image. This is not a live source download.
  sample='data:image/svg+xml;base64,'+base64.b64encode(b'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="562"><rect width="1000" height="562" fill="#ddd"/><text x="40" y="80" font-size="30">TEST FIXTURE / NOT SOURCE IMAGE</text></svg>').decode()
  db=json.loads((R/'assets/game-media/sources.json').read_text())
  for it in db['images']:
   for u in it['urls']:s=s.replace(u,sample)
 page.goto('about:blank');page.set_content(s.replace('<head>','<head>'+fixture,1),wait_until='domcontentloaded')
 page.wait_for_function('window.__qaGo && window.__teyvatDiagnostics && !document.querySelector("#reader").hidden')
 page.evaluate('document.fonts.ready');page.wait_for_timeout(80)

def go(page,loc):page.evaluate('loc=>__qaGo(loc)',loc);page.wait_for_timeout(20)
def saved(page):return page.evaluate('key=>JSON.parse(localStorage.getItem(key))',KEY)

def check(out,name,value,**detail):out['checks'].append({'name':name,'passed':bool(value),**detail})

def run(label,vp,browser):
 out={'viewport':vp,'label':label,'checks':[],'errors':[]}
 ctx=browser.new_context(viewport=vp,device_scale_factor=1);ctx.route('https://**/*',lambda r:r.abort());ctx.route('http://**/*',lambda r:r.abort())
 page=ctx.new_page();page.set_default_timeout(10000);page.on('pageerror',lambda e:out['errors'].append(str(e)))
 load(page);check(out,'book_structure',page.evaluate('__teyvatDiagnostics.chapterCount===60&&__teyvatDiagnostics.partCount===8&&Object.values(TEYVAT_CONTENT).filter(x=>x.status==="draft").length===5'))
 out['pages']=page.evaluate('__qaDoc().pages.length')
 # Every generated leaf, including all 60 chapter openers.
 layout=page.evaluate('''()=>{const d=__qaDoc(),out=[];for(let i=0;i<d.pages.length;i++){__qaGo({type:'page',index:i});for(const leaf of document.querySelectorAll('#book .book-page')){const b=leaf.querySelector('.page-body');if(!b)continue;const v=b.scrollHeight-b.clientHeight,h=b.scrollWidth-b.clientWidth;if(v>2||h>2)out.push({requested:i,meta:d.pageInfo[i],v,h,overflowY:getComputedStyle(b).overflowY,text:b.innerText.slice(0,150),className:leaf.className});}}return out}''')
 out['layout_warnings']=list({json.dumps([x['text'],x['v'],x['h']]):x for x in layout}.values())
 check(out,'no_clipped_overflow',not any(x['overflowY']=='hidden' for x in out['layout_warnings']),warnings=out['layout_warnings'])
 check(out,'chapter_openers_fit',not any('page-chapter-open' in x['className'] for x in out['layout_warnings']))
 check(out,'all_pages_fit',not out['layout_warnings'])
 for cid,b,caption in figures:
  go(page,{'type':'body','chapterId':cid,'blockId':b['blockId'],'sectionId':b['sectionId']})
  btn=next(x for x in page.locator('#book .zoom-image').all() if x.get_attribute('data-caption')==caption)
  short=btn.evaluate('(e)=>e.closest("figure").innerText')
  check(out,'short_caption_'+caption.split('｜')[0],len(short.strip())<=40 and not any(t in short for t in ['不代表','不表示','非官方','連網來源','點圖查看','來源圖待載入']),visible_text=short)
  btn.scroll_into_view_if_needed();im=btn.locator('img');im.evaluate('(e)=>e.loading="eager"');page.wait_for_timeout(30)
  valid=im.evaluate('(e)=>e.complete&&e.naturalWidth>0&&getComputedStyle(e).objectFit==="contain"')
  before=saved(page);counter=page.locator('#page-count').inner_text();btn.click();opened=page.locator('#picture-layer').is_visible()
  if cid==5 and '5-3' in caption:page.screenshot(path=str(O/f'{label}-source-status.png'))
  page.locator('#picture-dismiss').click();stable=saved(page)==before and counter==page.locator('#page-count').inner_text()
  check(out,'figure_'+caption.split('｜')[0],valid and opened and stable,loaded=valid,zoom=opened,preserved=stable)
 # All legacy mapping rows, not merely a few sample IDs.
 errors=page.evaluate('''()=>{const d=__qaDoc(),m=TEYVAT_BOOKMARK_MIGRATIONS,e=[];for(const[k,t]of Object.entries(m.byBlock)){if(d.blockStarts[k]!==undefined)continue;if(__qaFind({type:'body',chapterId:t.chapterId,sectionId:'unknown',blockId:k})!==d.sectionStarts[t.chapterId+':'+t.sectionId])e.push(k)}for(const[k,t]of Object.entries(m.bySection)){const[c,s]=k.split(':');if(__qaFind({type:'body',chapterId:+c,sectionId:s})!==d.sectionStarts[t.chapterId+':'+t.sectionId])e.push(k)}return e}''')
 check(out,'all_bookmark_migrations',not errors,errors=errors)
 page.locator('#top-toc').click();out['search_results']={}
 for q in ['人類','天使','仙靈','尼可','妮可','四執政','原始胎海']:
  page.locator('#toc-search').fill(q)
  cids=page.locator('.toc-entry').evaluate_all('(es)=>es.filter(e=>!e.hidden&&e.getBoundingClientRect().height>0).map(e=>e.dataset.chapter)')
  out['search_results'][q]=cids;check(out,'search_'+q,bool(cids),chapter_ids=cids)
 page.locator('#toc-search').fill('妮可');page.screenshot(path=str(O/f'{label}-search-nicole.png'))
 hit=page.locator('.toc-search-hit[data-search-chapter="5"]').first
 target=hit.get_attribute('data-search-block');expected=page.evaluate('id=>__qaDoc().blockStarts[id]',target)
 hit.click();actual=page.evaluate('()=>__qaFind(JSON.parse(localStorage.getItem("teyvat-reader-position-v03")))');check(out,'search_direct_jump',page.locator('#toc-drawer').is_hidden() and saved(page)['chapterId']==5 and actual==expected)
 # Exercise malicious query as inert text.
 page.locator('#top-toc').click();page.locator('#toc-search').fill('<img src=x onerror=alert(1)>');check(out,'search_no_html_injection',page.locator('.toc-search-hits img').count()==0);page.locator('#toc-close').click()
 pair=next(b for b in compiled['5']['blocks'] if 'media-pair' in b['html'])
 go(page,{'type':'body','chapterId':5,'blockId':pair['blockId']});page.screenshot(path=str(O/f'{label}-angel-pair-offline.png'))
 for cid in [5,22,60]:go(page,{'type':'chapter','chapterId':cid});page.screenshot(path=str(O/f'{label}-chapter-{cid:02}-opening.png'))
 resume=saved(page);load(page,resume,'read');check(out,'resume_after_reload',saved(page)==resume)
 load(page,fragment='ch01-humanity');check(out,'old_hash',saved(page)['chapterId']==5)
 # Successful swap branch with a transparent, explicitly simulated source.
 load(page,simulate=True)
 for mid in ['angel-example','ordinary-seelie','nicole-reeyn','tollan','three-moons','four-shades','primordial-sea-scene']:
  cid,b=next((c,b) for c,b,cap in figures if f'data-game-id="{mid}"' in b['html'])
  go(page,{'type':'body','chapterId':cid,'blockId':b['blockId']});btn=page.locator(f'#book [data-game-id="{mid}"]').first
  fixed=mid in ['tollan','three-moons','four-shades']
  page.wait_for_function('(id)=>{let e=document.querySelector(`#book [data-game-id="${id}"]`);return e&&["diagram","remote"].includes(e.dataset.mediaState)}',arg=mid)
  state=btn.get_attribute('data-media-state');check(out,'mock_swap_'+mid,state==('diagram' if fixed else 'remote'))
  if mid=='primordial-sea-scene':check(out,'figure_number_unchanged','圖 1-1｜' in btn.get_attribute('data-caption') and '1-1a' not in btn.get_attribute('data-caption'))
  btn.click();check(out,'source_links_'+mid,page.locator('#picture-source a').count()>=1)
  check(out,'notes_collapsed_'+mid,page.locator('#picture-source details[open]').count()==0)
  details=page.locator('#picture-source details')
  if details.count():
   details.locator('summary').click();check(out,'notes_expand_'+mid,details.get_attribute('open') is not None and len(details.inner_text())>8)
  page.locator('#picture-dismiss').click()
  bodies=page.locator('#book .page-body').evaluate_all('(es)=>es.map(e=>({v:e.scrollHeight-e.clientHeight,h:e.scrollWidth-e.clientWidth}))')
  check(out,'mock_swap_stable_layout_'+mid,all(x['v']<=2 and x['h']<=2 for x in bodies),metrics=bodies)
 go(page,{'type':'body','chapterId':5,'blockId':pair['blockId']})
 pair_metrics=page.locator('#book .media-pair').first.evaluate('''e=>({captions:e.querySelectorAll('figcaption').length,text:e.innerText.trim(),statuses:e.querySelectorAll('.media-state').length,labels:e.querySelectorAll('.media-tile-label').length,captionHeight:e.querySelector('figcaption').getBoundingClientRect().height,imageHeight:e.querySelector('img').getBoundingClientRect().height})''')
 check(out,'one_pair_caption',pair_metrics['captions']==1 and pair_metrics['statuses']==0 and pair_metrics['labels']==0 and pair_metrics['captionHeight']<pair_metrics['imageHeight']*.4,metrics=pair_metrics)
 check(out,'no_javascript_errors',not out['errors'],errors=out['errors'])
 out['passed']=all(x['passed'] for x in out['checks']);ctx.close()
 (O/f'browser-{label}.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'viewport':label,'checks':len(out['checks']),'passed':out['passed'],'warnings':len(out['layout_warnings']),'failed':[x['name'] for x in out['checks'] if not x['passed']]},ensure_ascii=False),flush=True)
 return out

if __name__=='__main__':
 chosen=sys.argv[1] if len(sys.argv)>1 else 'all'
 configurations=[('desktop',{'width':1440,'height':900}),('mobile',{'width':390,'height':844}),('small-mobile',{'width':360,'height':640})]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  results=[run(name,vp,browser) for name,vp in configurations if chosen in ['all',name]];browser.close()
 report={'version':'V0.12','mode':'Embedded source HTML/CSS/JS; local SVG data URIs; memory storage; CSS fallback. Simulated image swaps are NOT live network tests.','results':results}
 (O/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 sys.exit(0 if all(r['passed'] for r in results) else 1)
