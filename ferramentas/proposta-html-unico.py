"""Gera a versão HTML de arquivo único da proposta (imagens em WebP e fontes embutidas).
Uso: python3 ferramentas/proposta-html-unico.py [entrada.html] [saida.html]"""
import sys, re, base64, io, os
from PIL import Image
ent = sys.argv[1] if len(sys.argv) > 1 else 'propostas/digital-experience/proposta.html'
sai = sys.argv[2] if len(sys.argv) > 2 else 'manual/materiais-vendas/proposta-digital-experience-v14.html'
base = os.path.dirname(ent); s = open(ent, encoding='utf-8').read(); cache = {}
def img(m):
    f = m.group(1)
    if f not in cache:
        im = Image.open(os.path.join(base, f)); im.thumbnail((1400, 3200))
        b = io.BytesIO(); im.save(b, 'WEBP', quality=80, method=6)
        cache[f] = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
    return 'src="' + cache[f] + '"'
s = re.sub(r'src="(img/[^"]+)"', img, s)
s = re.sub(r'url\((fonts/[^)]+\.woff2)\)', lambda m: 'url(data:font/woff2;base64,' + base64.b64encode(open(os.path.join(base, m.group(1)), 'rb').read()).decode() + ')', s)
open(sai, 'w', encoding='utf-8').write(s); print(sai, len(s) // 1024, 'KB')
