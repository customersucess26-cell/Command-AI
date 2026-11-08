"""Gera as peças de gráfica de uma loja: cartão de volta (9 × 5 cm, frente e verso) e display de balcão (A5).
Saída em PDF com 3 mm de sangria (o que a gráfica pede) e prévias em PNG.
Uso: python3 ferramentas/grafica/gerar.py ferramentas/grafica/bruto.json manual/materiais-vendas/grafica-bruto
O JSON da loja: nome, link (endereço do cardápio), cupom {codigo, pct, minimo}, cores {fundo, destaque, amarelo, texto},
logo (arquivo), textos opcionais. Depois rode o node que o próprio script chama (precisa do Playwright)."""
import json, os, sys, subprocess, base64, io
import qrcode, qrcode.image.svg

cfg_path, saida = sys.argv[1], sys.argv[2]
C = json.load(open(cfg_path, encoding='utf-8'))
base = os.path.dirname(os.path.abspath(cfg_path))
os.makedirs(saida, exist_ok=True)
cor = C['cores']
cup = C['cupom']
link_cupom = f"{C['link']}?cupom={cup['codigo']}"
link_balcao = C['link']

def qr_svg(url, cor_qr):
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=0)
    q.add_data(url); q.make(fit=True)
    m = q.get_matrix(); n = len(m)
    rects = ''.join(f'<rect x="{x}" y="{y}" width="1.02" height="1.02"/>' for y, l in enumerate(m) for x, v in enumerate(l) if v)
    return f'<svg viewBox="0 0 {n} {n}" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges"><g fill="{cor_qr}">{rects}</g></svg>'

def data_uri(arq):
    ext = os.path.splitext(arq)[1].lower().strip('.')
    mime = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'webp': 'image/webp'}[ext]
    return f"data:{mime};base64," + base64.b64encode(open(arq, 'rb').read()).decode()

fontes = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
def fonte(nome, arq, peso):
    return f"@font-face{{font-family:'{nome}';font-weight:{peso};src:url(data:font/woff2;base64,{base64.b64encode(open(os.path.join(fontes, arq), 'rb').read()).decode()})}}"
FONTES = (fonte('Anton', 'anton-latin-400-normal.woff2', 400) + fonte('Barlow', 'barlow-latin-500-normal.woff2', 500)
          + fonte('Barlow', 'barlow-latin-600-normal.woff2', 600) + fonte('Barlow', 'barlow-latin-700-normal.woff2', 700))
logo = data_uri(os.path.join(base, C['logo']))
foto = data_uri(os.path.join(base, C['foto'])) if C.get('foto') else ''
minimo = f"Pedido mínimo de R$ {cup['minimo']:.0f}. " if cup.get('minimo') else ''
regra = f"Válido 1 vez por cliente, só no cardápio online. {minimo}Não vale nos aplicativos de delivery."

BASE_CSS = f"""{FONTES}
*{{box-sizing:border-box;margin:0;padding:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
body{{background:#777}}
.pg{{position:relative;overflow:hidden;page-break-after:always;background:{cor['fundo']};color:{cor['texto']};font-family:Barlow,Arial,sans-serif}}
.pg:last-child{{page-break-after:auto}}
.seg{{position:absolute;inset:3mm;}} /* área final (sem sangria) */
.guia{{position:absolute;inset:3mm;outline:.2mm dashed rgba(255,255,255,.5);pointer-events:none}}
.guia.int{{inset:6mm;outline-color:rgba(0,255,200,.45)}}
body.final .guia{{display:none}}
"""

# ---------------- cartão de volta: 90 × 50 mm + 3 mm de sangria = 96 × 56 mm ----------------
cartao = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Cartão de volta · {C['nome']}</title><style>
@page{{size:96mm 56mm;margin:0}}
{BASE_CSS}
.pg{{width:96mm;height:56mm}}
.frente .foto{{position:absolute;right:0;top:0;bottom:0;width:44mm;background:url({foto}) center/cover;}}
.frente .foto::after{{content:"";position:absolute;inset:0;background:linear-gradient(90deg,{cor['fundo']} 0%,rgba(0,0,0,.25) 55%,rgba(0,0,0,.05) 100%)}}
.frente .tx{{position:absolute;left:8mm;top:7mm;width:52mm}}
.frente img.logo{{height:10mm;display:block}}
.frente .k{{margin-top:3.2mm;font:700 6.2pt/1 Barlow;letter-spacing:.22em;text-transform:uppercase;color:{cor['amarelo']}}}
.frente h1{{margin-top:1.6mm;font:400 17pt/0.98 Anton;text-transform:uppercase;letter-spacing:.01em}}
.frente h1 em{{font-style:normal;color:{cor['destaque']}}}
.frente p{{margin-top:2mm;font:500 7pt/1.3 Barlow;color:{cor['suave']}}}
.verso{{background:{cor['claro']};color:#141414}}
.verso .qr{{position:absolute;left:8mm;top:8.5mm;width:39mm;height:39mm;padding:2mm;background:#fff;border-radius:2.4mm}}
.verso .qr svg{{width:100%;height:100%;display:block}}
.verso .tx{{position:absolute;left:51mm;top:8mm;right:7.5mm}}
.verso .k{{font:700 6pt/1 Barlow;letter-spacing:.2em;text-transform:uppercase;color:{cor['destaque']}}}
.verso h2{{margin-top:1.6mm;font:400 12.5pt/1 Anton;text-transform:uppercase}}
.verso .cod{{display:inline-block;margin-top:2.4mm;border:.45mm dashed {cor['destaque']};border-radius:1.6mm;padding:1.1mm 2.4mm;font:400 12pt/1 Anton;letter-spacing:.08em;color:{cor['destaque']}}}
.verso .cod small{{display:block;font:700 4.8pt/1 Barlow;letter-spacing:.18em;color:#555;margin-bottom:.8mm}}
.verso p{{margin-top:2.2mm;font:500 5.2pt/1.35 Barlow;color:#444}}
.verso .url{{position:absolute;left:8mm;bottom:5.2mm;font:600 5.4pt/1 Barlow;letter-spacing:.04em;color:#666}}
</style></head><body>
<section class="pg frente"><div class="foto"></div><div class="tx">
  <img class="logo" src="{logo}" alt="">
  <p class="k">{C['textos'].get('cartao_k', 'Obrigado pelo pedido')}</p>
  <h1>Na próxima,<br>peça direto<br>e ganhe <em>{cup['pct']}% OFF</em></h1>
  <p>{C['textos'].get('cartao_sub', 'Pelo nosso cardápio online. Vire o cartão.')}</p>
</div><div class="guia"></div><div class="guia int"></div></section>
<section class="pg verso"><div class="qr">{qr_svg(link_cupom, '#141414')}</div><div class="tx">
  <p class="k">Aponte a câmera</p>
  <h2>Cupom já<br>aplicado no<br>cardápio</h2>
  <span class="cod"><small>Ou digite o cupom</small>{cup['codigo']}</span>
  <p>{regra}</p>
</div><span class="url">{link_balcao.replace('https://', '')}</span><div class="guia"></div><div class="guia int"></div></section>
</body></html>"""

# ---------------- display de balcão: A5 148 × 210 mm + 3 mm = 154 × 216 mm ----------------
display = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Display de balcão · {C['nome']}</title><style>
@page{{size:154mm 216mm;margin:0}}
{BASE_CSS}
.pg{{width:154mm;height:216mm}}
.topo{{position:absolute;left:0;right:0;top:0;height:72mm;background:url({foto}) center 40%/cover}}
.topo::after{{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.15) 0%,rgba(0,0,0,.2) 55%,{cor['fundo']} 100%)}}
img.logo{{position:absolute;left:50%;top:11mm;height:20mm;transform:translateX(-50%);z-index:2}}
.tx{{position:absolute;left:14mm;right:14mm;top:58mm;text-align:center;z-index:2}}
.k{{font:700 10pt/1 Barlow;letter-spacing:.28em;text-transform:uppercase;color:{cor['amarelo']}}}
h1{{margin-top:2.6mm;font:400 40pt/0.95 Anton;text-transform:uppercase}}
h1 em{{font-style:normal;color:{cor['destaque']}}}
.sub{{margin-top:3mm;font:500 11.5pt/1.35 Barlow;color:{cor['suave']}}}
.qrbox{{position:absolute;left:50%;top:118mm;width:58mm;margin-left:-29mm;padding:3.6mm;background:#fff;border-radius:5mm;box-shadow:0 0 0 1.2mm {cor['destaque']}}}
.qrbox svg{{display:block;width:100%;height:auto}}
.passos{{position:absolute;left:12mm;right:12mm;top:183mm;display:flex;justify-content:center;gap:5mm;font:600 9pt/1.2 Barlow;color:{cor['texto']}}}
.passos span b{{display:inline-grid;place-items:center;width:5.4mm;height:5.4mm;border-radius:50%;background:{cor['amarelo']};color:#141414;font:700 8pt/1 Barlow;margin-right:1.4mm}}
.rod{{position:absolute;left:0;right:0;bottom:10mm;text-align:center;font:600 7.5pt/1 Barlow;letter-spacing:.12em;text-transform:uppercase;color:{cor['suave']}}}
</style></head><body>
<section class="pg"><div class="topo"></div><img class="logo" src="{logo}" alt="">
<div class="tx"><p class="k">{C['textos'].get('display_k', 'Sem fila. Sem esperar.')}</p>
<h1>Peça pelo<br><em>celular</em></h1>
<p class="sub">{C['textos'].get('display_sub', 'Veja as fotos, monte do seu jeito e envie. A gente já começa a preparar.')}</p></div>
<div class="qrbox">{qr_svg(link_balcao, '#141414')}</div>
<div class="passos"><span><b>1</b>Aponte a câmera</span><span><b>2</b>Escolha</span><span><b>3</b>Envie</span></div>
<p class="rod">{link_balcao.replace('https://', '')}</p>
<div class="guia"></div><div class="guia int"></div></section>
</body></html>"""

arqs = {'cartao-de-volta.html': cartao, 'display-balcao.html': display}
for n, h in arqs.items():
    open(os.path.join(saida, n), 'w', encoding='utf-8').write(h)

js = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exportar.js')
subprocess.run(['node', js, saida], check=True)
print('pronto:', saida)
