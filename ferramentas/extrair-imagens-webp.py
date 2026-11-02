#!/usr/bin/env python3
"""Tira as imagens embutidas (base64) do index.html da página de vendas e grava cada uma como WebP em img/.
O HTML fica leve e as imagens fora da primeira tela carregam só quando aparecem (loading="lazy").
Uso: python3 ferramentas/extrair-imagens-webp.py [pasta]   (padrão: sites-personalizados)"""
import base64, hashlib, io, os, re, sys
from PIL import Image

PASTA = sys.argv[1] if len(sys.argv) > 1 else "sites-personalizados"
P = os.path.join(PASTA, "index.html")
IMG = os.path.join(PASTA, "img")
os.makedirs(IMG, exist_ok=True)
s = open(P, encoding="utf-8").read()
antes = len(s.encode())
feitos = {}

def grava(tipo, b64):
    h = hashlib.sha1(b64.encode()).hexdigest()[:12]
    if h in feitos: return feitos[h]
    im = Image.open(io.BytesIO(base64.b64decode(b64)))
    nome = h + (".png" if tipo == "png" and im.size[0] <= 64 else ".webp")
    caminho = os.path.join(IMG, nome)
    if nome.endswith(".png"):
        open(caminho, "wb").write(base64.b64decode(b64))
    else:
        if im.mode not in ("RGB", "RGBA"): im = im.convert("RGBA" if "transparency" in im.info else "RGB")
        lim = 1400
        if max(im.size) > lim:
            k = lim / max(im.size); im = im.resize((round(im.size[0] * k), round(im.size[1] * k)), Image.LANCZOS)
        im.save(caminho, "WEBP", quality=78, method=6)
    feitos[h] = "img/" + nome
    return feitos[h]

# 1) imagens em <img src="data:..."> viram arquivo; fora da primeira tela, carregamento sob demanda
def troca_img(m):
    tag = m.group(0)
    mm = re.search(r'src="data:image/([a-z+]+);base64,([A-Za-z0-9+/=]+)"', tag)
    url = grava(mm.group(1), mm.group(2))
    tag = tag.replace(mm.group(0), 'src="' + url + '"')
    primeira = 'i-rest' in tag   # a primeira imagem do notebook do topo
    if primeira:
        tag = re.sub(r'\sloading="lazy"', '', tag)
        if 'fetchpriority' not in tag: tag = tag.replace('<img ', '<img fetchpriority="high" ', 1)
    else:
        if 'loading=' not in tag: tag = tag.replace('<img ', '<img loading="lazy" ', 1)
    if 'decoding=' not in tag: tag = tag.replace('<img ', '<img decoding="async" ', 1)
    return tag
s = re.sub(r'<img\b[^>]*src="data:image/[^"]+"[^>]*>', troca_img, s)
# 2) o resto (ícone da aba e as fotos do cardápio de demonstração dentro do script) também vira arquivo
s = re.sub(r'data:image/([a-z+]+);base64,([A-Za-z0-9+/=]+)', lambda m: grava(m.group(1), m.group(2)), s)
open(P, "w", encoding="utf-8").write(s)
tam = sum(os.path.getsize(os.path.join(IMG, f)) for f in os.listdir(IMG))
print("index.html: %d KB -> %d KB | %d imagens em img/ (%d KB no total)" % (antes // 1024, len(s.encode()) // 1024, len(feitos), tam // 1024))
