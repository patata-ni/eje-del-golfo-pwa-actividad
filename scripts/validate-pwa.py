"""Validate install assets and dimensions without third-party dependencies."""
from pathlib import Path
import json, struct

root=Path(__file__).resolve().parents[1]/'public/pwa'
manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
for key in ['id','name','short_name','start_url','scope','display','theme_color','background_color','icons']:
    assert manifest.get(key), f'Missing manifest field: {key}'
sizes=set()
for icon in manifest['icons']:
    path=root/icon['src']
    data=path.read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n', f'Invalid PNG: {path}'
    width,height=struct.unpack('>II',data[16:24])
    assert f'{width}x{height}'==icon['sizes'], f'Wrong dimensions: {path}'
    sizes.add(width)
assert {192,512}<=sizes
for name in ['index.html','app.js','db.js','app.css','sw.js','catalogo.json']:
    assert (root/name).is_file(), f'Missing resource: {name}'
json.loads((root/'catalogo.json').read_text(encoding='utf-8'))
print('PASS: Manifest, PNG icons 192/512, app shell and catalog.')
