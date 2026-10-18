#!/usr/bin/env python3
"""Grava a Content-Security-Policy (CSP) dentro de cada página HTML.

A CSP diz ao navegador de onde a página pode carregar scripts, fotos,
fontes e conexões. Os scripts escritos dentro do HTML só rodam se o
"resumo" (hash SHA-256) deles estiver na política. Assim, um script
injetado por um invasor (XSS) é bloqueado.

IMPORTANTE: rode de novo sempre que editar um <script> de uma página,
senão aquele script deixa de funcionar.

    python3 ferramentas/csp.py index.html modelos/*.html
"""
import base64
import hashlib
import os
import re
import sys
from html.parser import HTMLParser

META_RE = re.compile(r'\s*<meta http-equiv="Content-Security-Policy"[^>]*>')


class Scripts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.inline, self._on, self._buf = [], False, []

    def handle_starttag(self, tag, attrs):
        if tag == "script" and "src" not in dict(attrs):
            self._on, self._buf = True, []

    def handle_endtag(self, tag):
        if tag == "script" and self._on:
            self.inline.append("".join(self._buf))
            self._on = False

    def handle_data(self, data):
        if self._on:
            self._buf.append(data)


def politica(html, hashes):
    usa = lambda txt: txt in html
    script = ["'self'"] + [f"'sha256-{h}'" for h in hashes]
    connect = ["'self'"]
    img = ["'self'", "data:", "blob:", "https:"]
    frame = ["'none'"]
    if usa("fbevents.js"):  # Meta Pixel
        script.append("https://connect.facebook.net")
        connect += ["https://connect.facebook.net", "https://www.facebook.com"]
    if usa("supabase"):  # leads, painel e chat
        connect += ["https://*.supabase.co", "wss://*.supabase.co"]
    if usa("youtube.com/embed") or usa("instagram.com/reel"):  # vídeos do modelo padaria
        frame = ["https://www.youtube.com", "https://www.youtube-nocookie.com",
                 "https://www.instagram.com", "https://www.facebook.com"]
    regras = {
        "default-src": ["'self'"],
        "script-src": script,
        "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
        "font-src": ["'self'", "data:", "https://fonts.gstatic.com"],
        "img-src": img,
        "media-src": ["'self'", "data:", "blob:", "https:"],
        "connect-src": connect,
        "frame-src": frame,
        "object-src": ["'none'"],
        "base-uri": ["'self'"],
        "form-action": ["'self'"],
    }
    return "; ".join(f"{k} {' '.join(v)}" for k, v in regras.items())


def aplicar(caminho):
    html = open(caminho, encoding="utf-8").read()
    limpo = META_RE.sub("", html, count=1)
    p = Scripts()
    p.feed(limpo)
    hashes = [base64.b64encode(hashlib.sha256(s.encode("utf-8")).digest()).decode()
              for s in p.inline]
    # scripts locais (<script src="assets/app.js">) também contam para saber o que a página usa
    texto = limpo
    pasta = os.path.dirname(caminho)
    for src in re.findall(r'<script[^>]+src="([^":]+)"', limpo):
        arq = os.path.join(pasta, src)
        if os.path.isfile(arq):
            texto += open(arq, encoding="utf-8", errors="ignore").read()
    meta = f'\n<meta http-equiv="Content-Security-Policy" content="{politica(texto, hashes)}">'
    m = re.search(r'<meta charset="?utf-8"?\s*/?>', limpo, re.I)
    if not m:
        sys.exit(f"{caminho}: falta <meta charset=\"utf-8\"> no <head>")
    novo = limpo[:m.end()] + meta + limpo[m.end():]
    open(caminho, "w", encoding="utf-8").write(novo)
    print(f"{caminho}: {len(hashes)} script(s) liberado(s)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for arq in sys.argv[1:]:
        aplicar(arq)
