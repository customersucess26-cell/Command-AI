"""Gera as peças de divulgação em PNG: imagem de prévia do link (og), avatar, capas de destaques e 6 posts do Instagram.
Saída: plataforma/assets/img/og-bistro-connect.jpg e manual/kit-instagram/*.png
Usa Playwright (Chromium) para transformar HTML em imagem.  Uso:  python3 ferramentas/montar-kit-divulgacao.py
Os prints dos celulares vêm de manual/kit-instagram/base/ (capturas das vitrines de exemplo)."""
import os, subprocess, sys, json, shutil, tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(RAIZ, "manual/kit-instagram/base")
SAIDA = os.path.join(RAIZ, "manual/kit-instagram")
OG = os.path.join(RAIZ, "plataforma/assets/img/og-bistro-connect.jpg")
LOGO_CLARA = os.path.join(RAIZ, "manual/logo-clara.png")
ICONE = os.path.join(RAIZ, "admin/img/icone.png")
os.makedirs(SAIDA, exist_ok=True)

FONTES = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&display=swap">'
CSS = """
*{box-sizing:border-box;margin:0}
:root{--navy:#0E1526;--navy2:#18223A;--azul:#2BA8FF;--ouro:#C9A24A;--ouro2:#F3E3B8;--creme:#FAF7F0;--verm:#FF6B5E;--verde:#3DDC84}
html,body{width:var(--w);height:var(--h);overflow:hidden;font-family:'DM Sans',Arial,sans-serif;color:#fff}
body{background:radial-gradient(90% 60% at 85% 0%,#1D3A66 0%,var(--navy) 58%,#080C17 100%);position:relative}
h1,h2,h3,.p{font-family:'Poppins',Arial,sans-serif}
.pad{position:absolute;inset:0;padding:84px 78px;display:flex;flex-direction:column}
.logo{height:84px;width:auto;align-self:flex-start}
.sel{font:600 26px 'Poppins';letter-spacing:.2em;text-transform:uppercase;color:var(--ouro)}
.grande{font-weight:800;line-height:1.02;letter-spacing:-.02em}
.sub{font-size:38px;line-height:1.35;color:#C9D3E3}
.az{color:var(--azul)}.ou{color:var(--ouro2)}.vm{color:var(--verm)}.vd{color:var(--verde)}
.risc{position:relative;display:inline-block}
.risc::after{content:"";position:absolute;left:-3%;right:-3%;top:54%;height:.1em;background:#FF5A4E;border-radius:6px;box-shadow:0 0 22px rgba(255,90,78,.7)}
.rodape{margin-top:auto;display:flex;justify-content:space-between;align-items:center;font:600 28px 'Poppins';color:#8E9AB0}
.btn{display:inline-block;background:var(--azul);color:#06101F;font:700 34px 'Poppins';padding:26px 44px;border-radius:20px}
.fone{position:absolute;background:#05080F;border-radius:76px;padding:18px;box-shadow:0 50px 110px -30px #000,0 0 0 2px #2A3550 inset}
.fone img{display:block;width:100%;border-radius:60px}
.chip{display:inline-block;background:rgba(255,255,255,.08);border:1.5px solid rgba(255,255,255,.18);border-radius:999px;padding:12px 26px;font:600 28px 'Poppins'}
.card{background:rgba(255,255,255,.06);border:1.5px solid rgba(255,255,255,.14);border-radius:30px;padding:36px 40px}
.bol{max-width:84%;padding:18px 24px;border-radius:22px;font-size:34px;line-height:1.3;margin:12px 0;background:#fff;color:#111B21}
.bol.s{background:#D9FDD3;margin-left:auto}
.bol small{display:block;text-align:right;font-size:22px;color:#667781;margin-top:4px}
"""


def pagina(w, h, corpo, extra_css=""):
    return f'<!doctype html><html><head><meta charset="utf-8">{FONTES}<style>:root{{--w:{w}px;--h:{h}px}}{CSS}{extra_css}</style></head><body>{corpo}</body></html>'


def img(nome):
    return "file://" + os.path.join(BASE, nome)


LOGO = f'<img class="logo" src="file://{LOGO_CLARA}">'
RODAPE = '<div class="rodape"><span>bistroconnect.com.br</span><span class="ou">Link na bio</span></div>'

PECAS = {}  # nome -> (w, h, html)

# ---------- imagem de prévia do link ----------
PECAS["og"] = (1200, 630, pagina(1200, 630, f'''
<div class="pad" style="padding:56px 64px;flex-direction:row;gap:40px">
  <div style="flex:1;display:flex;flex-direction:column;justify-content:center">
    <img class="logo" src="file://{LOGO_CLARA}" style="height:74px;margin-bottom:34px">
    <h1 class="grande" style="font-size:66px">Venda direto.<br><span class="az">Sem comissão.</span></h1>
    <p class="sub" style="font-size:28px;margin-top:22px;max-width:560px">Cardápio online e pedido no WhatsApp para padarias, cafés, hamburguerias e restaurantes.</p>
    <p style="margin-top:26px"><span class="chip" style="font-size:24px">Grátis até R$ 3 mil em vendas por mês</span></p>
  </div>
  <div style="width:330px;position:relative"><div class="fone" style="left:0;top:-10px;width:330px;transform:rotate(3deg)"><img src="{img('padaria.png')}"></div></div>
</div>'''))

# ---------- avatar ----------
PECAS["avatar"] = (1080, 1080, pagina(1080, 1080, f'''
<div style="position:absolute;inset:0;display:grid;place-items:center"><img src="file://{ICONE}" style="width:620px;filter:drop-shadow(0 20px 50px rgba(201,162,74,.4))"></div>'''))

# ---------- capas de destaques ----------
ICONES = {
    "como": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "planos": '<path d="M12 3v18M17 7H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
    "lojas": '<path d="M3 9l1.5-5h15L21 9M4 9v11h16V9M10 20v-5h4v5"/><path d="M3 9a3 3 0 0 0 6 0 3 3 0 0 0 6 0 3 3 0 0 0 6 0"/>',
    "duvidas": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.7.4-1 .9-1 1.7M12 17h.01"/>',
    "comece": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
}
NOMES = {"como": "Como funciona", "planos": "Planos", "lojas": "Lojas", "duvidas": "Dúvidas", "comece": "Comece"}
for k, d in ICONES.items():
    PECAS[f"destaque-{k}"] = (1080, 1920, pagina(1080, 1920, f'''
<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:50px">
  <div style="width:520px;height:520px;border-radius:50%;border:8px solid var(--ouro);display:grid;place-items:center;background:rgba(201,162,74,.08)">
    <svg viewBox="0 0 24 24" width="260" height="260" fill="none" stroke="#F3E3B8" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{d}</svg></div>
  <div class="p" style="font-size:64px;font-weight:700">{NOMES[k]}</div></div>'''))

# ---------- posts ----------
PECAS["post-1-dor"] = (1080, 1350, pagina(1080, 1350, f'''
<div class="pad">{LOGO}
  <div style="margin-top:100px"><div class="sel">Para quem vende comida</div>
  <h1 class="grande" style="font-size:128px;margin-top:26px">O app de delivery fica com <span class="vm risc">até 23%</span> do seu pedido.</h1>
  <p class="sub" style="margin-top:40px">Você faz a comida, a entrega e o atendimento. Ele leva uma fatia de cada venda.</p>
  <p style="margin-top:34px"><span class="chip">Existe outro jeito</span></p></div>
  {RODAPE}</div>'''))

PECAS["post-2-conta"] = (1080, 1350, pagina(1080, 1350, f'''
<div class="pad">{LOGO}
  <div style="margin-top:70px"><div class="sel">Faça a conta</div>
  <h1 class="grande" style="font-size:78px;margin-top:20px">Quem vende R$ 10 mil por mês pelo app deixa até</h1>
  <div class="p vm" style="font-size:190px;font-weight:800;line-height:1;margin-top:18px;letter-spacing:-.03em">R$ 27.600</div>
  <p class="sub" style="margin-top:20px;font-size:44px"><b style="color:#fff">por ano</b> em comissão.</p>
  <p style="margin-top:40px;font:500 26px 'DM Sans';color:#8E9AB0">Cálculo com plano de entrega de 23%. Confira as taxas do seu plano no app.</p></div>
  {RODAPE}</div>'''))

PECAS["post-3-solucao"] = (1080, 1350, pagina(1080, 1350, f'''
<div class="pad" style="padding-right:0">{LOGO}
  <div style="margin-top:80px;max-width:470px"><div class="sel">A saída</div>
  <h1 class="grande" style="font-size:74px;margin-top:22px">Sua loja online em <span class="az">5 minutos.</span></h1>
  <p class="sub" style="margin-top:34px;font-size:32px">Cardápio com fotos, pedido pronto e rastreio para o cliente.</p>
  <p style="margin-top:34px"><span class="chip">Sem comissão</span> <span class="chip" style="margin-top:12px">Grátis até R$ 3 mil</span></p></div>
  <div class="fone" style="right:34px;top:280px;width:440px;transform:rotate(3deg)"><img src="{img('padaria.png')}"></div>
  <div class="rodape" style="position:absolute;left:78px;right:78px;bottom:84px"><span>bistroconnect.com.br</span><span class="ou">Link na bio</span></div></div>'''))

PECAS["post-4-antes-depois"] = (1080, 1350, pagina(1080, 1350, f'''
<div class="pad">{LOGO}
  <div style="margin-top:56px"><div class="sel">Antes e depois</div>
  <h1 class="grande" style="font-size:70px;margin-top:16px">Pedido no WhatsApp:<br>caos ou <span class="az">organizado?</span></h1></div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:26px;margin-top:44px">
    <div class="card" style="padding:26px"><div class="p vm" style="font-size:28px;font-weight:700;letter-spacing:.08em">HOJE</div>
      <div class="bol" style="font-size:27px;margin-top:14px">Tem pão de queijo?</div><div class="bol" style="font-size:27px">🎤 Áudio 1:48</div><div class="bol" style="font-size:27px">Oi?? Ninguém responde</div><div class="bol s" style="font-size:27px">Desculpa a demora!</div>
      <div class="bol" style="font-size:27px">Já pedi em outro lugar</div></div>
    <div class="card" style="padding:26px"><div class="p vd" style="font-size:28px;font-weight:700;letter-spacing:.08em">COM CARDÁPIO ONLINE</div>
      <div class="bol" style="font-size:27px;margin-top:14px"><b>Pedido #128</b><br>2× Pão de queijo<br>1× Cappuccino<br>Entrega: Rua das Flores<br>Pix · <b>Total R$ 31,90</b></div>
      <div class="bol s" style="font-size:27px">Confirmado! Já está no forno 🥐</div></div>
  </div>
  {RODAPE}</div>'''))

PECAS["post-5-como-funciona"] = (1080, 1350, pagina(1080, 1350, f'''
<div class="pad">{LOGO}
  <div style="margin-top:56px"><div class="sel">Como funciona</div>
  <h1 class="grande" style="font-size:84px;margin-top:16px">3 passos. Sem programador.</h1></div>
  <div style="display:flex;flex-direction:column;gap:26px;margin-top:50px">
    <div class="card" style="display:flex;gap:34px;align-items:center"><div class="p" style="font-size:80px;font-weight:800;color:var(--ouro)">1</div><div><div class="p" style="font-size:42px;font-weight:700">Crie a conta e a loja</div><div class="sub" style="font-size:30px">Dá o nome e escolhe o tipo de negócio.</div></div></div>
    <div class="card" style="display:flex;gap:34px;align-items:center"><div class="p" style="font-size:80px;font-weight:800;color:var(--ouro)">2</div><div><div class="p" style="font-size:42px;font-weight:700">Use o cardápio de exemplo</div><div class="sub" style="font-size:30px">Já vem com fotos. É só trocar pelos seus.</div></div></div>
    <div class="card" style="display:flex;gap:34px;align-items:center"><div class="p" style="font-size:80px;font-weight:800;color:var(--ouro)">3</div><div><div class="p" style="font-size:42px;font-weight:700">Divulgue o seu link</div><div class="sub" style="font-size:30px">Instagram, Google e status do WhatsApp.</div></div></div>
  </div>
  {RODAPE}</div>'''))

PECAS["post-6-chamada"] = (1080, 1350, pagina(1080, 1350, f'''
<div class="pad" style="align-items:center;text-align:center">{LOGO.replace('align-self:flex-start','')}
  <div style="margin-top:120px"><div class="sel">Comece hoje</div>
  <h1 class="grande" style="font-size:118px;margin-top:26px">Venda direto.<br><span class="az">Sem comissão.</span></h1>
  <p class="sub" style="margin-top:40px">Grátis até R$ 3 mil em vendas por mês. Sem cartão de crédito.</p>
  <p style="margin-top:56px"><span class="btn">Crie sua loja grátis</span></p>
  <p class="p ou" style="margin-top:34px;font-size:34px;font-weight:600">Link na bio</p></div>
  <div class="rodape" style="width:100%"><span style="margin:auto">bistroconnect.com.br</span></div></div>'''))

# ---------- renderização ----------
tmp = tempfile.mkdtemp()
lista = []
for nome, (w, h, html) in PECAS.items():
    p = os.path.join(tmp, nome + ".html")
    open(p, "w", encoding="utf-8").write(html)
    lista.append({"arq": p, "w": w, "h": h, "saida": os.path.join(tmp, nome + ".png"), "nome": nome})
json.dump(lista, open(os.path.join(tmp, "lista.json"), "w"))
js = r'''
const { chromium } = require('playwright'); const fs = require('fs');
(async () => { const L = JSON.parse(fs.readFileSync(process.argv[2])); const b = await chromium.launch();
  for (const x of L) { const p = await b.newPage({ viewport: { width: x.w, height: x.h } });
    await p.goto('file://' + x.arq); await p.waitForTimeout(1800); await p.screenshot({ path: x.saida }); await p.close(); }
  await b.close(); })();'''
open(os.path.join(tmp, "render.js"), "w").write(js)
env = dict(os.environ, NODE_PATH=os.environ.get("NODE_PATH", ""))
r = subprocess.run(["node", os.path.join(tmp, "render.js"), os.path.join(tmp, "lista.json")], capture_output=True, text=True, env=env, cwd=os.environ.get("PW_DIR", RAIZ))
if r.returncode:
    sys.exit(r.stderr)

from PIL import Image
for x in lista:
    n = x["nome"]
    im = Image.open(x["saida"]).convert("RGB")
    if n == "og":
        im.save(OG, quality=86, optimize=True)
    else:
        im.save(os.path.join(SAIDA, n + ".png"), optimize=True)
shutil.rmtree(tmp)
print("og:", round(os.path.getsize(OG) / 1024), "KB;", len(lista) - 1, "peças em manual/kit-instagram/")
