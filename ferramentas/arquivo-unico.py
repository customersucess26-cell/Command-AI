#!/usr/bin/env python3
"""Gera uma cópia do site em UM arquivo .html, com as fotos de img/ embutidas.
Serve para abrir direto no celular ou mandar pelo WhatsApp. Para publicar, use a pasta normal.
    python3 ferramentas/arquivo-unico.py sites/hamburgueria-bruto saida.html
"""
import base64, mimetypes, os, re, sys
pasta, saida = sys.argv[1], sys.argv[2]
html = open(os.path.join(pasta, "index.html"), encoding="utf-8").read()
cache = {}
def embute(m):
    rel = m.group(0)
    if rel not in cache:
        caminho = os.path.join(pasta, rel)
        if not os.path.isfile(caminho):
            return rel
        tipo = mimetypes.guess_type(caminho)[0] or "image/jpeg"
        cache[rel] = f"data:{tipo};base64," + base64.b64encode(open(caminho, "rb").read()).decode()
    return cache[rel]
html = re.sub(r"img/[A-Za-z0-9_./-]+\.(?:jpg|jpeg|png|webp|svg)", embute, html)
html = html.replace('<script src="assets/config.js"></script>', "")
open(saida, "w", encoding="utf-8").write(html)
print(f"{saida}: {len(cache)} fotos embutidas, {len(html)//1024} KB")
