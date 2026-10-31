#!/usr/bin/env python3
"""Self-contained checks for the 8-part, 60-chapter book source and output."""
from pathlib import Path
import json
import re
import sys
ROOT = Path(__file__).resolve().parents[1]


def assert_ok(test, message):
    if not test:
        raise AssertionError(message)


def main():
    book = json.loads((ROOT / 'data/catalog.json').read_text(encoding='utf-8'))
    assert_ok(len(book['parts']) == 8, 'Expect eight main parts')
    ids=[c['id'] for p in book['parts'] for c in p['chapters']]
    assert_ok(len(ids)==60 and sorted(ids)==list(range(1,61)), 'Expect 60 unique chapters')
    paths=[]
    for part in book['parts']:
        for ch in part['chapters']:
            path=ROOT/'content'/f'part-{part["id"]:02d}'/f'chapter-{ch["id"]:02d}.md'
            assert_ok(path.exists(), f'Missing {path}')
            paths.append(path)
    assert_ok(len(list((ROOT/'content').rglob('chapter-*.md')))==60, 'Unexpected extra or misnamed chapter')
    generated=(ROOT/'js/generated-content.js').read_text(encoding='utf-8')
    compiled=re.search(r'window\.TEYVAT_CONTENT\s*=\s*(\{.*\});\s*$',generated,re.DOTALL)
    assert_ok(compiled, 'Invalid compiled content')
    parsed=json.loads(compiled.group(1))
    assert_ok(set(parsed)=={str(i) for i in range(1,61)}, 'Compiled chapter coverage missing')
    for id_,obj in parsed.items():
        assert_ok(obj['blocks'], f'Empty chapter {id_}')
        for block in obj['blocks']:
            assert_ok(block.get('blockId') and block.get('sectionId'),f'Incomplete bookmark id in {id_}')
    index=(ROOT/'index.html').read_text(encoding='utf-8')
    for needle in ['id="floating-toc"','id="toc-drawer"','id="fullscreen-btn"',
                   'src="./js/generated-content.js"','src="./js/reader.js"']:
        assert_ok(needle in index, f'Missing DOM or script marker: {needle}')
    for asset in (ROOT/'assets').glob('*.svg'):
        text=asset.read_text(encoding='utf-8')
        assert_ok('<svg' in text and '</svg>' in text,f'Invalid SVG {asset}')
    # Screenshot substitutions are optional bytes, but their map must remain in sync.
    media_path=ROOT/'assets/game-media/sources.json'
    if media_path.exists():
        media=json.loads(media_path.read_text(encoding='utf-8'))['images']
        mapping=(ROOT/'js/game-media-data.js').read_text(encoding='utf-8')
        found=re.search(r'window\.TEYVAT_GAME_MEDIA\s*=\s*(\{.*\});\s*$',mapping,re.DOTALL)
        assert_ok(found,'Missing or invalid generated game-media map')
        decoded=json.loads(found.group(1))
        assert_ok(set(decoded)=={a['id'] for a in media},'Outdated screenshot mapping; rerun build')
        all_figures=[b['html'] for ch in parsed.values() for b in ch['blocks'] if b['kind']=='figure']
        for entry in media:
            expected=entry.get('placement','active')
            assert_ok(expected in {'active','staged'},f'Invalid screenshot placement {entry["id"]}')
            found_in_text=any('data-game-id="'+entry['id']+'"' in fig for fig in all_figures)
            assert_ok(found_in_text==(expected=='active'),f'Screenshot activity / mapping mismatch {entry["id"]}')
            assert_ok((ROOT/entry['figure']).is_file(),f'Missing SVG fallback for {entry["id"]}')
            assert_ok(decoded[entry['id']]['local']==entry['local'] and decoded[entry['id']]['caption']==entry['caption'], f'Mismatched screenshot mapping for {entry["id"]}')
    # The v0.7 reading positions must resolve to a current section, including moved topics.
    redirects_path=ROOT/'data/bookmark-migrations-v07.json'
    if redirects_path.exists():
        migrated=json.loads(redirects_path.read_text(encoding='utf-8'))
        saved_js=(ROOT/'js/bookmark-migrations.js').read_text(encoding='utf-8')
        match=re.search(r'window\.TEYVAT_BOOKMARK_MIGRATIONS\s*=\s*(\{.*\});\s*$',saved_js,re.DOTALL)
        assert_ok(match and json.loads(match.group(1))==migrated,'Bookmark migrations must be rebuilt from source JSON')
        valid_sections={f'{int(cid)}:{b["sectionId"]}' for cid,obj in parsed.items() for b in obj['blocks'] if b['kind']=='heading'}
        for key,dest in migrated['bySection'].items():
            assert_ok(f'{dest["chapterId"]}:{dest["sectionId"]}' in valid_sections,f'Broken legacy section redirect: {key}')
        for key,dest in migrated['byBlock'].items():
            assert_ok(f'{dest["chapterId"]}:{dest["sectionId"]}' in valid_sections,f'Broken legacy block redirect: {key}')
        assert_ok('src="./js/bookmark-migrations.js"' in index,'Missing reader bookmark migration script')
    print('VALIDATED: 1 book, 8 parts, 60 chapters, independent Markdown files, navigation, bookmarked blocks and illustrations')


if __name__=='__main__':
    try:
        main()
    except Exception as error:
        print('VALIDATION FAILED:',error,file=sys.stderr)
        sys.exit(1)
