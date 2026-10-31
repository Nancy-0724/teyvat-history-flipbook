#!/usr/bin/env python3
"""Unit test using synthetic JPEG and HTML responses, never external downloads."""
from pathlib import Path
import importlib.util, tempfile, io, json
from PIL import Image
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('fetch',R/'tools/fetch_game_art.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
buf=io.BytesIO();Image.effect_noise((320,240),80).convert('RGB').save(buf,format='JPEG',quality=90);jpeg=buf.getvalue()
class Response:
 def __init__(self,content,mime):self.content=content;self.headers={'Content-Type':mime}
 def __enter__(self):return self
 def __exit__(self,*args):return False
 def read(self,n):return self.content[:n]
checks=[]
with tempfile.TemporaryDirectory() as tmp:
 f.ROOT=Path(tmp);(f.ROOT/'_site').mkdir()
 item={'id':'fixture','local':'assets/game-media/ch05/fixture.jpg','urls':['https://invalid.example/fixture'],'fallback_only':True}
 f.urlopen=lambda *a,**k:Response(jpeg,'image/jpeg')
 ok=f.fetch_one(item);checks.append({'name':'mock_jpeg_saved_and_site_synced','passed':ok and (f.ROOT/item['local']).read_bytes()==jpeg and (f.ROOT/'_site'/item['local']).read_bytes()==jpeg})
 f.urlopen=lambda *a,**k:(_ for _ in ()).throw(AssertionError('Should reuse a valid cached image'))
 checks.append({'name':'cached_image_reused','passed':f.fetch_one(item)})
 item['local']='assets/game-media/ch05/rejected.jpg';f.urlopen=lambda *a,**k:Response(b'<html>not an image</html>','text/html')
 checks.append({'name':'rejects_html_no_fake_success','passed':not f.fetch_one(item) and not (f.ROOT/item['local']).exists()})
assert all(c['passed'] for c in checks)
report={'mode':'Synthetic response unit test; NOT actual source downloads','checks':checks}
(R/'docs/qa-v011/download-unit-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
