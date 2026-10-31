#!/usr/bin/env python3
"""Build the book's independent Markdown chapters into browser-ready JS.

Only Python's standard library is required. HTML/CSS/JS are static and can be opened
locally or hosted on GitHub Pages. The input Markdown grammar is intentionally small
and documented in docs/CONTENT_GUIDE.md, so editorial work stays predictable.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GAME_MEDIA_MANIFEST = ROOT / 'assets/game-media/sources.json'
GAME_MEDIA_ENTRIES = json.loads(GAME_MEDIA_MANIFEST.read_text(encoding='utf-8'))['images'] if GAME_MEDIA_MANIFEST.is_file() else []
GAME_MEDIA_FIGURES = {item['figure']: item['id'] for item in GAME_MEDIA_ENTRIES}
GAME_MEDIA_BY_ID = {item['id']: item for item in GAME_MEDIA_ENTRIES}
GAME_MEDIA_OUTPUT = ROOT / 'js' / 'game-media-data.js'
CATALOG = ROOT / 'data' / 'catalog.json'
BOOKMARK_MIGRATIONS = ROOT / 'data' / 'bookmark-migrations-v07.json'
BOOKMARK_MIGRATIONS_OUTPUT = ROOT / 'js' / 'bookmark-migrations.js'
OUTPUT = ROOT / 'js' / 'generated-content.js'
CATALOG_JS = ROOT / 'js' / 'book-data.js'
VALID_STATUSES = {'outline', 'draft', 'reviewed'}
HEADING = re.compile(r'^(#{2,3})\s+(.+?)(?:\s+\{#([a-zA-Z][\w-]*)\})?\s*$')
FIGURE = re.compile(r'^!\[([^\]]+)\]\((assets/[a-zA-Z0-9_./-]+\.(?:svg|png|jpe?g|webp|gif))\)(\{float\})?$')
LIST = re.compile(r'^(?:\s*(-)\s+|\s*(\d+)\.\s+)(.+)$')
INLINE = re.compile(r'(\[\[(\d{1,2})(?:\|([^\]]+))?\]\])|(\[([^\]]+)\]\((https?://[^\s)]+)\))|(\*\*([^*]+)\*\*)|(`([^`]+)`)')


def safe(s: str) -> str:
    return html.escape(s, quote=True)


def inline(s: str) -> str:
    out = []
    end = 0
    for m in INLINE.finditer(s):
        out.append(safe(s[end:m.start()]))
        if m.group(2):
            chapter_id = int(m.group(2))
            if not 1 <= chapter_id <= 60:
                raise ValueError(f'Cross-chapter link out of range: {chapter_id}')
            text = m.group(3) or f'第 {chapter_id} 章'
            out.append(f'<button type="button" class="book-inline-link" data-jump-chapter="{chapter_id}">{safe(text)}</button>')
        elif m.group(6):
            out.append(f'<a href="{safe(m.group(6))}" rel="noopener noreferrer" target="_blank">{safe(m.group(5))}</a>')
        elif m.group(8):
            out.append(f'<strong>{safe(m.group(8))}</strong>')
        elif m.group(10):
            out.append(f'<code>{safe(m.group(10))}</code>')
        end = m.end()
    out.append(safe(s[end:]))
    return ''.join(out)


def parse_frontmatter(source: str, filename: str):
    lines = source.replace('\r\n', '\n').split('\n')
    if not lines or lines[0].strip() != '---':
        raise ValueError(f'{filename}: needs --- YAML-like header at beginning')
    close = next((i for i in range(1, len(lines)) if lines[i].strip() == '---'), None)
    if close is None:
        raise ValueError(f'{filename}: unclosed front matter')
    meta = {}
    for line in lines[1:close]:
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if ':' not in line:
            raise ValueError(f'{filename}: malformed metadata line: {line!r}')
        key, value = line.split(':', 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, lines[close + 1:]


def parse_markdown(lines: list[str], chapter_id: int, used_images: set[str]):
    blocks = []
    seen_anchors = set()
    unique_blocks = Counter()
    current_section = f'ch{chapter_id:02d}-start'

    def push(kind: str, raw: str, rendered: str, section: str | None = None):
        section = current_section if section is None else section
        digest = hashlib.sha1((kind + ':' + raw).encode('utf-8')).hexdigest()[:12]
        unique_blocks[digest] += 1
        blocks.append({'kind': kind, 'html': rendered, 'sectionId': section,
                       'blockId': f'c{chapter_id:02d}-{digest}-{unique_blocks[digest]}'})

    def add_para(raw: list[str]):
        if raw:
            source = ' '.join(x.strip() for x in raw)
            push('paragraph', source, '<p>' + inline(source) + '</p>')

    i = 0
    para = []
    while i < len(lines):
        row = lines[i].strip()
        if not row:
            add_para(para)
            para = []
            i += 1
            continue
        heading = HEADING.fullmatch(row)
        figure = FIGURE.fullmatch(row)
        match_list = LIST.fullmatch(row)
        if heading:
            add_para(para)
            para = []
            level, label, anchor = heading.groups()
            anchor = anchor or f'ch{chapter_id:02d}-section-{len(seen_anchors)+1:02d}'
            if anchor in seen_anchors:
                raise ValueError(f'Chapter {chapter_id}: duplicate section anchor {anchor}')
            seen_anchors.add(anchor)
            current_section = anchor
            tag = 'h2' if len(level) == 2 else 'h3'
            push('heading', row, f'<{tag} id="{safe(anchor)}">{inline(label)}</{tag}>', anchor)
            i += 1
            continue
        if figure:
            add_para(para)
            para = []
            caption, image_path, float_mode = figure.groups()
            if not (ROOT / image_path).is_file():
                raise ValueError(f'Chapter {chapter_id}: missing figure: {image_path}')
            used_images.add(image_path)
            cls = 'page-figure figure-float' if float_mode else 'page-figure'
            if chapter_id == 1 and image_path.startswith('assets/illustrations/ch01/'):
                cls += ' ch01-figure'
            if chapter_id == 2 and image_path.startswith('assets/illustrations/ch02/'):
                cls += ' ch02-figure'
            if chapter_id == 3 and image_path.startswith('assets/illustrations/ch03/'):
                cls += ' ch03-figure'
            if chapter_id == 4 and image_path.startswith('assets/illustrations/ch04/'):
                cls += ' ch04-figure'
            if chapter_id == 5 and image_path.startswith('assets/illustrations/ch05/'):
                cls += ' ch05-figure'
            if GAME_MEDIA_FIGURES.get(image_path) in {'naberius','ronova','istaroth','asmoday'}:
                cls += ' shade-portrait'
            src = './' + image_path
            info = GAME_MEDIA_BY_ID.get(GAME_MEDIA_FIGURES.get(image_path), {})
            loaded_caption = info.get('caption', caption)
            state = '來源圖待載入 · 點圖查看出處' if info.get('fallback_only') else '原創示意 · 點圖查看圖源'
            media_state = f'<span class="media-state">{safe(state)}</span>' if info else ''
            rendered = (f'<figure class="{cls}"><button type="button" class="zoom-image" '
                        f'data-src="{safe(src)}" data-caption="{safe(caption)}" data-game-id="{safe(GAME_MEDIA_FIGURES.get(image_path, ""))}" '
                        f'aria-label="檢視圖片：{safe(caption)}">'
                        f'<img src="{safe(src)}" alt="{safe(caption)}" loading="lazy"></button>'
                        f'{media_state}<figcaption class="switch-caption"><span class="caption-original">{safe(caption)}</span>'
                        f'<span class="caption-loaded" aria-hidden="true">{safe(loaded_caption)}</span></figcaption></figure>')
            push('figure', row, rendered)
            i += 1
            continue
        if row.startswith(':::gallery '):
            add_para(para)
            para = []
            gallery_caption = row[len(':::gallery '):].strip()
            raw_gallery = [row]
            tiles = []
            i += 1
            while i < len(lines) and lines[i].strip() != ':::':
                panel = lines[i].strip()
                i += 1
                if not panel:
                    continue
                match = FIGURE.fullmatch(panel)
                if not match:
                    raise ValueError(f'Chapter {chapter_id}: gallery contains a non-image line')
                label, path, floating = match.groups()
                if floating or not (ROOT / path).is_file():
                    raise ValueError(f'Chapter {chapter_id}: invalid gallery image {path}')
                used_images.add(path)
                raw_gallery.append(panel)
                media_id = GAME_MEDIA_FIGURES.get(path, '')
                loaded_caption = GAME_MEDIA_BY_ID.get(media_id, {}).get('caption', label)
                tiles.append(f'<div class="media-tile"><button type="button" class="zoom-image" '
                    f'data-src="./{safe(path)}" data-caption="{safe(label)}" data-game-id="{safe(media_id)}" '
                    f'aria-label="檢視圖片：{safe(label)}"><img src="./{safe(path)}" alt="{safe(label)}" loading="lazy"></button>'
                    f'<span class="media-tile-label switch-caption"><span class="caption-original">{safe(label)}</span>'
                    f'<span class="caption-loaded" aria-hidden="true">{safe(loaded_caption)}</span></span>'
                    f'<span class="media-state">來源圖待載入</span></div>')
            if i >= len(lines) or len(tiles) != 2:
                raise ValueError(f'Chapter {chapter_id}: gallery must have exactly two images and a closing :::')
            raw_gallery.append(':::')
            rendered = (f'<figure class="page-figure ch{chapter_id:02d}-figure media-pair"><div class="media-grid">'
                + ''.join(tiles) + f'</div><figcaption>{safe(gallery_caption)}</figcaption></figure>')
            push('figure', '\n'.join(raw_gallery), rendered)
            i += 1
            continue
        if row.startswith(':::'):
            add_para(para)
            para = []
            m = re.match(r'^:::(source|dispute|note|lead)(?:\s+(.+))?$', row)
            if not m:
                raise ValueError(f'Chapter {chapter_id}: unknown callout: {row}')
            style, label = m.groups()
            callout = []
            i += 1
            while i < len(lines) and lines[i].strip() != ':::':
                callout.append(lines[i].strip())
                i += 1
            if i == len(lines):
                raise ValueError(f'Chapter {chapter_id}: unclosed ::: block')
            body = '</p><p>'.join(inline(x) for x in '\n'.join(callout).strip().split('\n\n') if x.strip())
            if style == 'lead':
                rendered = f'<p class="lead">{body}</p>'
            else:
                rendered = f'<aside class="margin-script source-{style}"><b>{safe(label or {"source":"史料","dispute":"史學爭議","note":"編輯註記"}[style])}</b><p>{body}</p></aside>'
            push('callout', row + '\n'.join(callout), rendered)
            i += 1
            continue
        if match_list:
            add_para(para)
            para = []
            ordered = bool(match_list.group(2))
            items = []
            while i < len(lines):
                m = LIST.fullmatch(lines[i].strip())
                if not m or bool(m.group(2)) != ordered:
                    break
                items.append(m.group(3))
                i += 1
            tag = 'ol' if ordered else 'ul'
            rendered = '<' + tag + ' class="book-list">' + ''.join('<li>' + inline(x) + '</li>' for x in items) + '</' + tag + '>'
            push('list', '\n'.join(items), rendered)
            continue
        if row.startswith('|') and row.endswith('|'):
            add_para(para)
            para = []
            raw_rows = []
            while i < len(lines) and lines[i].strip().startswith('|') and lines[i].strip().endswith('|'):
                raw_rows.append([c.strip() for c in lines[i].strip()[1:-1].split('|')])
                i += 1
            if not raw_rows:
                continue
            cols = len(raw_rows[0])
            if any(len(r) != cols for r in raw_rows):
                raise ValueError(f'Chapter {chapter_id}: inconsistent table columns')
            # Skip markdown alignment row if present.
            if len(raw_rows) > 1 and all(re.fullmatch(r':?-{3,}:?', x or '') for x in raw_rows[1]):
                raw_rows.pop(1)
            header = '<thead><tr>' + ''.join('<th>' + inline(x) + '</th>' for x in raw_rows[0]) + '</tr></thead>'
            body = '<tbody>' + ''.join('<tr>' + ''.join('<td>' + inline(x) + '</td>' for x in row) + '</tr>' for row in raw_rows[1:]) + '</tbody>'
            push('table', repr(raw_rows), '<div class="table-scroll"><table class="history-table">' + header + body + '</table></div>')
            continue
        if row.startswith('>'):
            add_para(para)
            para = []
            quote = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            push('quote', '\n'.join(quote), '<blockquote class="reading-quote">' + inline(' '.join(quote)) + '</blockquote>')
            continue
        if row == '---':
            add_para(para)
            para = []
            push('rule', row, '<hr class="chapter-rule">')
            i += 1
            continue
        if row.startswith('# '):
            raise ValueError(f'Chapter {chapter_id}: top-level # title is managed by the catalog; use ## for sections')
        para.append(row)
        i += 1
    add_para(para)
    return blocks


def main():
    book = json.loads(CATALOG.read_text(encoding='utf-8'))
    parts = book['parts']
    chapters = [c for part in parts for c in part['chapters']]
    ids = [c['id'] for c in chapters]
    if len(parts) != 8 or len(chapters) != 60 or sorted(ids) != list(range(1, 61)):
        raise ValueError('Catalog must have exactly eight parts and 60 unique chapters (1-60)')
    output = {}
    status_count = Counter()
    used_images = set()
    for part in parts:
        for chapter in part['chapters']:
            chapter_id = chapter['id']
            path = ROOT / 'content' / f'part-{part["id"]:02d}' / f'chapter-{chapter_id:02d}.md'
            if not path.is_file():
                raise ValueError(f'Missing chapter Markdown: {path.relative_to(ROOT)}')
            meta, lines = parse_frontmatter(path.read_text(encoding='utf-8-sig'), str(path.relative_to(ROOT)))
            if int(meta.get('chapter', -1)) != chapter_id:
                raise ValueError(f'{path}: metadata chapter id mismatch')
            status = meta.get('status', 'outline')
            if status not in VALID_STATUSES:
                raise ValueError(f'{path}: unsupported status {status!r}')
            updated = meta.get('updated', '')
            if updated:
                date.fromisoformat(updated)
            blocks = parse_markdown(lines, chapter_id, used_images)
            if not blocks:
                raise ValueError(f'{path}: empty chapter; use an outline placeholder instead')
            output[str(chapter_id)] = {
                'status':status, 'updated':updated, 'blocks':blocks,
                'sections':[{'id':b['sectionId'],'title':re.sub(r'<[^>]+>','',b['html'])}
                            for b in blocks if b['kind'] == 'heading'],
            }
            status_count[status] += 1
    CATALOG_JS.write_text('/* Generated from data/catalog.json — do not edit here. */\n'
                          + 'window.TEYVAT_BOOK = ' + json.dumps(book, ensure_ascii=False, separators=(',', ':')) + ';\n',
                          encoding='utf-8')
    json_data = json.dumps(output,ensure_ascii=False,separators=(',',':'))
    OUTPUT.write_text('/* Auto-generated by python tools/build.py. Edit the source Markdown chapter files, not this file. */\n'
                      + 'window.TEYVAT_CONTENT = ' + json_data + ';\n',encoding='utf-8')
    # Keep browser game-image mappings reproducible from the same manifest as build-time figure tags.
    if GAME_MEDIA_MANIFEST.is_file():
        entries = json.loads(GAME_MEDIA_MANIFEST.read_text(encoding='utf-8'))['images']
        keys = [item['id'] for item in entries]
        figures = [item['figure'] for item in entries]
        if len(keys) != len(set(keys)) or len(figures) != len(set(figures)):
            raise ValueError('Duplicate game-media ID or SVG figure mapping')
        for item in entries:
            placement = item.get('placement', 'active')
            if placement not in {'active', 'staged'}:
                raise ValueError(f'Invalid game-media placement {placement!r}: {item["id"]}')
            if placement == 'active' and item['figure'] not in used_images:
                raise ValueError(f'Unused active game-media figure: {item["figure"]}')
            if placement == 'staged' and item['figure'] in used_images:
                raise ValueError(f'Staged game-media figure is already active in text: {item["figure"]}')
            if not (ROOT/item['figure']).is_file():
                raise ValueError(f'Missing mapped SVG fallback: {item["figure"]}')
            if not item.get('urls') or not item.get('local') or not item.get('caption'):
                raise ValueError(f'Incomplete game-media source: {item["id"]}')
        payload = {item['id']:item for item in entries}
        GAME_MEDIA_OUTPUT.write_text('/* Generated from assets/game-media/sources.json; do not edit directly. */\n'
            + 'window.TEYVAT_GAME_MEDIA = ' + json.dumps(payload,ensure_ascii=False,separators=(',',':')) + ';\n',encoding='utf-8')
    if BOOKMARK_MIGRATIONS.is_file():
        payload=json.loads(BOOKMARK_MIGRATIONS.read_text(encoding='utf-8'))
        if not all(key in payload for key in ('bySection','byBlock')):
            raise ValueError('Incomplete saved bookmark migration table')
        BOOKMARK_MIGRATIONS_OUTPUT.write_text('/* Generated from data/bookmark-migrations-v07.json; do not edit. */\n'
            + 'window.TEYVAT_BOOKMARK_MIGRATIONS = ' + json.dumps(payload,ensure_ascii=False,separators=(',',':')) + ';\n',encoding='utf-8')
    print(f'OK 8 parts, {len(chapters)} chapters, {sum(len(x["blocks"]) for x in output.values())} content blocks, {len(used_images)} referenced illustration(s).')
    print('Statuses:', ', '.join(f'{status}={status_count[status]}' for status in ['outline','draft','reviewed']))
    print('Updated:', CATALOG_JS.relative_to(ROOT), OUTPUT.relative_to(ROOT), 'and', GAME_MEDIA_OUTPUT.relative_to(ROOT))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('BUILD FAILED:', exc, file=sys.stderr)
        sys.exit(1)
