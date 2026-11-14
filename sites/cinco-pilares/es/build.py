"""Gera um único arquivo HTML (CSS, JS e imagens embutidos) a partir de index.html.
Uso: python3 build.py  ->  ../los-5-pilares-v19-es.html"""
import re, base64, hashlib, mimetypes, pathlib
here = pathlib.Path(__file__).parent
s = (here / 'index.html').read_text()
css = (here / 'assets/site.css').read_text()
js = (here / 'assets/app.js').read_text()
s = re.sub(r'<link rel="stylesheet" href="assets/site\.css[^"]*">', lambda m: '<style>' + css + '</style>', s)
s = re.sub(r'<script src="assets/app\.js[^"]*" defer></script>', lambda m: '<script>' + js + '</script>', s)
def data(m):
    f = here / m.group(1)
    mt = mimetypes.guess_type(f.name)[0] or 'image/webp'
    return 'data:' + mt + ';base64,' + base64.b64encode(f.read_bytes()).decode()
s = re.sub(r'(?<=["\'( ])(assets/img/[\w.-]+)', data, s)
scr = re.findall(r'<script(?![^>]*(?:\bsrc=|application/json))[^>]*>(.*?)</script>', s, flags=re.S)
hs = ["'sha256-" + base64.b64encode(hashlib.sha256(x.encode()).digest()).decode() + "'" for x in scr]
s = re.sub(r"script-src 'self'(?: 'sha256-[^']+')*", "script-src " + ' '.join(hs), s, count=1)
out = here.parent / 'los-5-pilares-v19-es.html'
out.write_text(s)
print(out, len(s) // 1024, 'KB', len(hs), 'scripts')
