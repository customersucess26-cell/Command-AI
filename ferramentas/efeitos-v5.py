"""Aplica os efeitos v5 (cabeçalho de vidro, contadores, celular flutuando, aurora no topo,
campos do formulário mais bonitos) na página inicial da plataforma e no site oficial.
Pode rodar de novo: não duplica nada.  Uso: python3 ferramentas/efeitos-v5.py"""
import re, sys
MARCA = "/* ===== v5: efeitos extras ===== */"
CSS = MARCA + r"""
header.nav{transition:background .35s ease,box-shadow .35s ease}
header.nav .in{transition:height .35s ease}
header.nav.rolou{background:rgba(255,255,255,.78)!important;-webkit-backdrop-filter:blur(18px) saturate(1.6);backdrop-filter:blur(18px) saturate(1.6);box-shadow:0 1px 0 rgba(201,162,74,.3),0 14px 34px -22px rgba(14,21,38,.55)!important}
.hero{overflow:hidden}
.hero::after{content:"";position:absolute;inset:-25%;z-index:0;pointer-events:none;filter:blur(50px);opacity:.75;
  background:radial-gradient(28% 32% at 22% 28%,rgba(43,168,255,.22),transparent 70%),radial-gradient(24% 30% at 78% 70%,rgba(201,162,74,.18),transparent 70%),radial-gradient(22% 26% at 60% 18%,rgba(124,92,255,.14),transparent 70%);
  animation:aurora 22s ease-in-out infinite alternate}
@keyframes aurora{0%{transform:translate(0,0) rotate(0)}50%{transform:translate(4%,-3%) rotate(6deg)}100%{transform:translate(-4%,3%) rotate(-5deg)}}
.hero>.in{position:relative;z-index:1}
.stage .phone{animation:flutua 6.5s ease-in-out infinite}
@keyframes flutua{0%,100%{translate:0 0}50%{translate:0 -12px}}
.btn{transition:transform .15s cubic-bezier(.3,1.5,.5,1),box-shadow .2s ease,background .2s ease}
.btn:active{transform:translateY(1px) scale(.97)!important}
.btn-mint:hover{box-shadow:0 14px 34px -12px rgba(43,168,255,.85)}
.plan .price [data-conta]{font-variant-numeric:tabular-nums}
form.lead{box-shadow:0 40px 80px -40px rgba(0,0,0,.6)}
form.lead label{transition:color .2s}
form.lead label:focus-within{color:var(--mint-deep)}
form.lead input,form.lead select{min-height:52px;border-radius:14px;transition:border-color .2s,box-shadow .25s,background .2s;-webkit-appearance:none;appearance:none}
form.lead select{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%234C5668' stroke-width='2.2' stroke-linecap='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 14px center;background-size:18px;padding-right:40px}
form.lead input:hover,form.lead select:hover{border-color:#B9C3D3}
form.lead input:focus,form.lead select:focus{outline:none;border-color:var(--mint);background-color:#fff;box-shadow:0 0 0 4px rgba(43,168,255,.16),0 10px 24px -14px rgba(43,168,255,.6)}
form.lead input:not(:placeholder-shown):valid{border-color:#2F9E6B;padding-right:44px;background:#fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Ccircle cx='12' cy='12' r='11' fill='%232F9E6B'/%3E%3Cpath d='M7 12.5l3.2 3.2L17 9' fill='none' stroke='%23fff' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") no-repeat right 12px center/22px}
form.lead input:not(:placeholder-shown):not(:focus):invalid{border-color:#B4372F;box-shadow:0 0 0 4px rgba(180,55,47,.1)}
@media (prefers-reduced-motion:reduce){.hero::after,.stage .phone{animation:none!important}}
"""
def aplica(caminho, prefixo):
    s = open(caminho, encoding="utf-8").read()
    if MARCA in s:
        print(caminho, "já tem os efeitos v5"); return
    i = s.index("</style>"); s = s[:i] + CSS + s[i:]
    s = s.replace('<header class="nav">', '<header class="nav vidro-ao-rolar">', 1)
    s = re.sub(r'<p class="price"([^>]*)>R\$ (\d+)<small>', r'<p class="price"\1>R$ <span data-conta="\2">\2</span><small>', s)
    s = s.replace('<input id="lNome" name="nome" autocomplete="name" maxlength="80" required>', '<input id="lNome" name="nome" autocomplete="name" maxlength="80" placeholder="Ex.: Ana Souza" required>')
    s = s.replace('<input id="lEst" name="estabelecimento" maxlength="100" required>', '<input id="lEst" name="estabelecimento" maxlength="100" placeholder="Ex.: Padaria da Ana" required>')
    s = s.replace('placeholder="(42) 9 9999-9999" maxlength="20" required>', 'placeholder="(42) 99999-9999" maxlength="20" pattern=".{14,}" data-mascara="zap" required>')
    j = s.rindex("</body>"); s = s[:j] + '<script src="%sassets/efeitos.js"></script>\n' % prefixo + s[j:]
    open(caminho, "w", encoding="utf-8").write(s); print(caminho, "ok")
aplica("plataforma/index.html", "/")
aplica("index.html", "")
