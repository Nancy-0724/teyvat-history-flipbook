#!/usr/bin/env python3
"""Acquire selected actual game screenshots. Run this ONCE WITH INTERNET for complete offline reading.

   Does not alter chapter text or overwrite existing SVG diagrams. Skips verified files.
   Images are from game cutscenes or officially published character images, not fan artwork.
   The original SVG stays available whenever a provider blocks downloads.
"""
from __future__ import annotations
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import argparse, hashlib, json, sys, time, shutil

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'assets/game-media/sources.json'
ITEMS=json.loads(MANIFEST.read_text('utf-8'))['images']
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'

def detected_format(data:bytes):
    if data.startswith(b'\xff\xd8\xff'): return 'jpg'
    if data.startswith(b'\x89PNG\r\n\x1a\n'): return 'png'
    if data.startswith(b'RIFF') and data[8:12]==b'WEBP': return 'webp'
    return None

def fetch_one(item):
    final=ROOT/item['local']
    format_expected=final.suffix[1:].lower()
    if final.is_file() and final.stat().st_size>4096:
        if detected_format(final.read_bytes()[:64]) is not None:
            print('已存在:',final.relative_to(ROOT)); return True
    final.parent.mkdir(parents=True,exist_ok=True)
    for idx,url in enumerate(item['urls'],1):
        try:
            headers={'User-Agent':UA,'Accept':'image/webp,image/png,image/jpeg,image/*,*/*;q=0.8'}
            if 'hoyolab' in url or 'hoyoverse' in url:headers['Referer']='https://www.hoyolab.com/'
            req=Request(url,headers=headers)
            with urlopen(req,timeout=16) as rsp:
                content=rsp.read(12_000_000)
                mime=rsp.headers.get('Content-Type','')
            fmt=detected_format(content[:64])
            if not fmt or len(content)<4096:
                raise ValueError('回傳資料不是有效圖片（'+mime+'）')
            # A mirror might have another format; keep local extension aligned via simple rename
            # and retain the intended original filename for browser lookup by transcoding with Pillow, if available.
            if fmt!=format_expected:
                try:
                    from PIL import Image
                    from io import BytesIO
                    from PIL import ImageOps
                    original=Image.open(BytesIO(content)).convert('RGB')
                    buf=BytesIO()
                    if format_expected=='jpg':original.save(buf,'JPEG',quality=91,optimize=True)
                    elif format_expected=='png':original.save(buf,'PNG',optimize=True)
                    elif format_expected=='webp':original.save(buf,'WEBP',quality=90)
                    else:raise ValueError('不支援的圖片格式')
                    content=buf.getvalue(); fmt=format_expected
                except ImportError:
                    # Cannot convert without Pillow; the browser sniffs bytes and will still display correctly.
                    print('備註：副來源格式',fmt,'但瀏覽器可正常辨識',file=sys.stderr)
            temp=final.with_suffix(final.suffix+'.part')
            temp.write_bytes(content)
            temp.replace(final)
            site=ROOT/'_site'/item['local']
            if (ROOT/'_site').is_dir():
                site.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(final,site)
            print('完成:',final.relative_to(ROOT),f'({len(content)//1024} KB)')
            return True
        except Exception as exc:
            print(f'  [{idx}/{len(item["urls"])}] {item["id"]} 來源無法下載：{str(exc)[:180]}')
    print('未取得圖片，保留載入提示卡：' if item.get('fallback_only') else '未取得圖片，保留原創示意：',item['id'])
    return False

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='下載已登錄的來源圖；不改正文，不覆蓋原創示意。')
    parser.add_argument('--chapter',type=int,choices=range(1,61),help='只處理指定章，如 --chapter 5')
    parser.add_argument('--check',action='store_true',help='只檢查本機檔案，不連網')
    args=parser.parse_args()
    items=[it for it in ITEMS if args.chapter is None or it['chapter']==args.chapter]
    done=0;records=[]
    for item in items:
        path=ROOT/item['local']
        ok=(path.is_file() and path.stat().st_size>4096 and detected_format(path.read_bytes()[:64]) is not None) if args.check else fetch_one(item)
        done+=bool(ok)
        records.append({'id':item['id'],'local':item['local'],'exists':bool(ok),'bytes':path.stat().st_size if ok else 0,'sha256':hashlib.sha256(path.read_bytes()).hexdigest() if ok else None})
    if not args.check:
        log=ROOT/'assets/game-media/download-status.json'
        log.write_text(json.dumps({'checked_at':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'results':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'mode':'check' if args.check else 'download','chapter':args.chapter,'available':done,'total':len(items),'results':records},ensure_ascii=False,indent=2))
    if done<len(items):
        print('未成功的來源圖不算完成；可從來源頁合法另存至 local 路徑。第五章缺圖時顯示提示卡，不假裝是人物肖像。')
    sys.exit(0 if done==len(items) else 1)
