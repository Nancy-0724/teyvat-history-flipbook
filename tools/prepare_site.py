#!/usr/bin/env python3
"""Prepare the smallest set of deployable static files for GitHub Pages."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / '_site'
if PUBLIC.exists():
    shutil.rmtree(PUBLIC)
PUBLIC.mkdir()
shutil.copy2(ROOT / 'index.html', PUBLIC / 'index.html')
shutil.copy2(ROOT / '.nojekyll', PUBLIC / '.nojekyll')
for name in ['css','assets','js']:
    shutil.copytree(ROOT / name, PUBLIC / name, ignore=shutil.ignore_patterns('vendor') if name == 'js' else None)
print('Prepared clean GitHub Pages output at', PUBLIC)
