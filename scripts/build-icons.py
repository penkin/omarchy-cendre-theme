#!/usr/bin/env python3
"""Render the Cendre recoloring of Yaru's folder sheet. Requires rsvg-convert."""
from pathlib import Path
import copy
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / 'icons/Cendre'
SVG = '{http://www.w3.org/2000/svg}'
INK = '{http://www.inkscape.org/namespaces/inkscape}'
sheet = ET.parse(THEME / 'source/folders.svg').getroot()
directories = set()
for group in sheet:
    if group.tag != SVG + 'g':
        continue
    plate = next((e for e in group.iter() if e.get(INK + 'label') == 'Baseplate'), None)
    if plate is None:
        continue
    name = next(''.join(e.itertext()).strip() for e in plate if e.get(INK + 'label') == 'icon-name')
    offset = re.fullmatch(r'translate\(([-\d.e]+)[, ]+([-\d.e]+)\)', group.get('transform', 'translate(0,0)'))
    if offset is None:
        raise ValueError('Unsupported sheet transform')
    dx, dy = map(float, offset.groups())
    for rect in plate:
        if rect.tag != SVG + 'rect':
            continue
        size = int(float(rect.get('width')))
        x, y = float(rect.get('x')) + dx, float(rect.get('y')) + dy
        root = copy.deepcopy(sheet)
        root.set('viewBox', f'{x} {y} {size} {size}')
        root.set('width', str(size))
        root.set('height', str(size))
        with tempfile.NamedTemporaryFile(suffix='.svg') as source:
            source.write(ET.tostring(root))
            source.flush()
            for scale in (1, 2):
                directory = f'{size}x{size}' + ('@2x' if scale == 2 else '') + '/places'
                directories.add((size, scale, directory))
                target = THEME / directory
                target.mkdir(parents=True, exist_ok=True)
                subprocess.run(['rsvg-convert', '-w', str(size * scale), '-h', str(size * scale), '-o', str(target / (name + '.png')), source.name], check=True)

aliases = {'inode-directory': 'folder', 'folder-downloads': 'folder-download', 'folder-saved-search': 'folder', 'folder-recent': 'folder', 'folder-visiting': 'folder-open'}
sections = []
for size, scale, directory in sorted(directories):
    for alias, original in aliases.items():
        # Regular files also survive Omarchy's safe repository staging.
        (THEME / directory / (alias + '.png')).write_bytes((THEME / directory / (original + '.png')).read_bytes())
    sections.append(f'[{directory}]\nSize={size}\nScale={scale}\nContext=Places\nType=Fixed\n')
index = '[Icon Theme]\nName=Cendre\nComment=Copper and ash folders, adapted from Yaru\nInherits=Yaru,Adwaita,hicolor\nExample=folder\nDirectories=' + ','.join(d for _, _, d in sorted(directories)) + '\n\n' + '\n'.join(sections)
(THEME / 'index.theme').write_text(index)
print(f'Rendered Cendre folders in {len(directories)} size/scale directories.')
