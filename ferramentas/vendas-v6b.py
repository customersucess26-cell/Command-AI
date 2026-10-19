"""Página de vendas v6b: o "Antes e depois" vira dois celulares de verdade com o WhatsApp no tema claro.
O "depois" mostra a mensagem igual à que o sistema manda (assets/loja.js, mensagemZap).
Roda depois do vendas-v6.py. Pode rodar de novo: não duplica nada.
Uso: python3 ferramentas/vendas-v6b.py && python3 ferramentas/csp.py plataforma/index.html"""
import re

ARQ = "plataforma/index.html"
MARCA = "/* ===== v6b: antes e depois em celulares ===== */"
s = open(ARQ, encoding="utf-8").read()
if MARCA in s:
    raise SystemExit("plataforma/index.html já está na v6b")

CHECK = '<svg class="wa-ticks" viewBox="0 0 18 11" aria-hidden="true"><path d="M1 6l3 3 6-7M7 9l1 1 6-8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def bolha(lado, texto, hora, i, extra=""):
    t = CHECK if lado == "sai" else ""
    return ('<div class="wa-b %s%s" style="--i:%d"><div class="wa-txt">%s</div><span class="wa-h">%s%s</span></div>'
            % (lado, extra, i, texto, hora, t))


AUDIO = ('<span class="wa-audio"><span class="wa-play" aria-hidden="true"></span><span class="wa-onda" aria-hidden="true">'
         + "".join('<i style="height:%dpx"></i>' % h for h in (6, 12, 18, 9, 14, 20, 11, 7, 16, 22, 13, 8, 17, 10, 6, 12, 19, 9, 14, 7))
         + '</span><span class="wa-dur">1:48</span></span>')

ANTES = [
    ("entra", "Boa noite! Vcs ainda tão aceitando pedido?", "21:42"),
    ("entra", "Tem pão de queijo?", "21:42"),
    ("entra", AUDIO, "21:44"),
    ("entra", "Quanto fica 2 pão de queijo e 1 cappuccino? E a entrega?", "21:47"),
    ("entra", "Oi??", "21:55"),
    ("sai", "Oi, Ju! Desculpa, tava no forno 🙏 Ainda quer?", "21:58"),
    ("entra", "Já pedi pelo app, obrigada", "21:59"),
]
PEDIDO = ('Olá, Padaria da Ana! Fiz o pedido <b>#128</b> pelo site.<br><br>'
          '• 2× Pão de queijo — R$ 12,00<br>• 1× Cappuccino — R$ 14,90<br><br>'
          'Entrega: R$ 5,00<br>Total: <b>R$ 31,90</b><br>Entregar em: Rua das Flores, 120 · Centro<br>'
          'Pagamento: Pix<br>Nome: Juliana · (42) 99876-5432<br><br>'
          'Acompanhe: <span class="wa-link">bistroconnect.com.br/pedido…</span>')
DEPOIS = [
    ("entra", PEDIDO, "21:43", " pedido"),
    ("sai", "Pedido confirmado, Juliana! Já está no forno 🥐", "21:44", ""),
    ("entra", "Obrigada!! 😍", "21:44", ""),
]


def celular(titulo, status, bolhas, avatar, rot, classe_rot, notif=""):
    return '''<figure class="cel-wa">
          <div class="cel-moldura">
            <div class="cel-ilha" aria-hidden="true"></div>
            <div class="cel-tela">
              <div class="cel-status" aria-hidden="true"><b>21:43</b><span class="cel-ic"><i></i><i></i><i></i><i></i><u></u></span></div>%s
              <div class="wa-topo"><span class="wa-volta" aria-hidden="true">‹</span><span class="wa-av">%s</span><div><b>%s</b><small>%s</small></div></div>
              <div class="wa-chat">
                <span class="wa-dia">HOJE</span>
                %s
              </div>
              <div class="wa-barra" aria-hidden="true"><span class="wa-campo">Mensagem</span><span class="wa-mic"></span></div>
            </div>
          </div>
          <figcaption class="cel-leg %s">%s</figcaption>
        </figure>''' % (notif, avatar, titulo, status, "\n                ".join(bolhas), classe_rot, rot)


antes = celular("Juliana", "visto por último às 21:59",
                [bolha(l, t, h, i) for i, (l, t, h) in enumerate(ANTES)], "JU",
                '<span class="pino ruim"></span><span><b>Hoje, sem cardápio online:</b> 7 mensagens, 17 minutos e a venda foi para o app.</span>', "ruim")
depois = celular("Juliana", "online",
                 [bolha(l, t, h, i, x) for i, (l, t, h, x) in enumerate(DEPOIS)], "JU",
                 '<span class="pino bom"></span><span><b>Com a Bistrô Connect:</b> 1 mensagem com tudo, conta feita e link de rastreio. Sem comissão.</span>', "bom",
                 '\n              <div class="cel-notif" aria-hidden="true"><span class="cel-notif-ic"></span><div><b>WhatsApp · agora</b><span>Juliana: Fiz o pedido #128 pelo site…</span></div></div>')

SECAO = '''<section class="dark ad-sec" id="antes-depois">
    <div class="in">
      <div class="head centro revela">
        <p class="eyebrow">Antes e depois</p>
        <h2>A mesma cliente, no mesmo horário. Só muda onde ela faz o pedido.</h2>
        <p>À esquerda, o que acontece hoje no seu WhatsApp. À direita, a mensagem que chega quando ela pede pelo seu cardápio.</p>
      </div>
      <div class="ad2">
        <div class="ad2-lado revela esq">
        %s
        </div>
        <div class="ad2-vs" aria-hidden="true"><span>VS</span></div>
        <div class="ad2-lado revela dir">
        %s
        </div>
      </div>
    </div>
  </section>''' % (antes, depois)

i = s.index('<section class="dark ad-sec" id="antes-depois">')
j = s.index('</section>', i) + len('</section>')
s = s[:i] + SECAO + s[j:]

# tira o CSS antigo do antes e depois
a = s.index('/* antes e depois */'); b = s.index('/* calculadora */', a)
s = s[:a] + s[b:]

CSS = MARCA + r"""
.ad2{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);gap:26px;align-items:start;max-width:960px;margin:0 auto}
.ad2-lado{display:flex;justify-content:center}
.ad2-vs{align-self:center;width:64px;height:64px;border-radius:50%;display:grid;place-items:center;background:var(--navy-2);border:1px solid var(--navy-3);color:#fff;font:800 16px var(--f-display);box-shadow:0 0 0 8px rgba(43,168,255,.06),0 20px 40px -20px rgba(0,0,0,.8)}
@media (max-width:860px){.ad2{grid-template-columns:1fr;gap:18px}.ad2-vs{justify-self:center;width:52px;height:52px}}
.cel-wa{margin:0;width:100%;max-width:340px}
.pino{width:10px;height:10px;border-radius:50%;flex:none;margin-top:6px}.pino.ruim{background:#FF6B5E;box-shadow:0 0 0 4px rgba(255,107,94,.18)}.pino.bom{background:#3DDC84;box-shadow:0 0 0 4px rgba(61,220,132,.18)}
.cel-moldura{position:relative;border-radius:52px;padding:11px;background:linear-gradient(145deg,#3A3F48,#0B0D11 45%,#262A31);box-shadow:0 0 0 1.5px #555B66 inset,0 50px 90px -40px rgba(0,0,0,.9),0 0 0 6px rgba(255,255,255,.03)}
.cel-moldura::before{content:"";position:absolute;right:-3px;top:150px;width:3px;height:70px;border-radius:0 3px 3px 0;background:#2A2F37}
.cel-ilha{position:absolute;top:21px;left:50%;translate:-50% 0;width:96px;height:28px;border-radius:20px;background:#000;z-index:5}
.cel-tela{position:relative;border-radius:42px;overflow:hidden;background:#EFEAE2;height:640px;display:flex;flex-direction:column;font-family:-apple-system,"SF Pro Text","Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.cel-status{display:flex;justify-content:space-between;align-items:center;padding:16px 26px 6px 30px;background:#fff;color:#111;font-size:14px}
.cel-status b{font-weight:600;letter-spacing:.02em}
.cel-ic{display:flex;align-items:flex-end;gap:2px}
.cel-ic i{width:3px;background:#111;border-radius:1px}.cel-ic i:nth-child(1){height:4px}.cel-ic i:nth-child(2){height:6px}.cel-ic i:nth-child(3){height:8px}.cel-ic i:nth-child(4){height:10px}
.cel-ic u{display:inline-block;width:22px;height:11px;border:1.5px solid #111;border-radius:3px;margin-left:6px;position:relative;text-decoration:none;background:linear-gradient(90deg,#111 70%,transparent 70%) padding-box content-box;padding:1px}
.wa-topo{display:flex;align-items:center;gap:10px;padding:8px 14px 10px 8px;background:#fff;border-bottom:1px solid #E6E1D9;color:#111}
.wa-volta{font-size:30px;line-height:1;color:#007AFF;margin-right:-2px}
.wa-av{width:36px;height:36px;border-radius:50%;display:grid;place-items:center;background:linear-gradient(135deg,#F7B267,#F25C54);color:#fff;font:700 13px/1 inherit}
.wa-topo b{display:block;font-size:15.5px;font-weight:600}.wa-topo small{font-size:12px;color:#667781}
.wa-chat{flex:1;padding:10px 10px 6px;overflow:hidden;display:flex;flex-direction:column;justify-content:flex-end;gap:4px;
  background-color:#EFEAE2;background-image:radial-gradient(rgba(0,0,0,.035) 1.2px,transparent 1.4px),radial-gradient(rgba(0,0,0,.025) 1px,transparent 1.2px);background-size:22px 22px,15px 15px;background-position:0 0,7px 9px}
.wa-dia{align-self:center;font-size:11.5px;font-weight:600;color:#54656F;background:#fff;padding:4px 10px;border-radius:8px;margin:2px 0 6px;box-shadow:0 1px .5px rgba(11,20,26,.13)}
.wa-b{position:relative;max-width:84%;padding:6px 8px 7px 9px;border-radius:9px;font-size:14px;line-height:1.38;color:#111B21;box-shadow:0 1px .5px rgba(11,20,26,.13);display:flex;flex-wrap:wrap;align-items:flex-end;gap:2px 10px}
.wa-b.entra{background:#fff;align-self:flex-start;border-top-left-radius:2px}
.wa-b.sai{background:#D9FDD3;align-self:flex-end;border-top-right-radius:2px}
.wa-b.entra::before,.wa-b.sai::before{content:"";position:absolute;top:0;width:8px;height:10px}
.wa-b.entra::before{left:-7px;background:linear-gradient(225deg,#fff 50%,transparent 50%)}
.wa-b.sai::before{right:-7px;background:linear-gradient(135deg,#D9FDD3 50%,transparent 50%)}
.wa-b.pedido{max-width:92%;font-size:13.2px}
.wa-txt{flex:1 1 auto}
.wa-b b{font-weight:700}
.wa-h{margin-left:auto;font-size:11px;color:#667781;display:inline-flex;align-items:center;gap:3px;white-space:nowrap;line-height:1}
.wa-ticks{width:16px;height:11px;color:#53BDEB}
.wa-link{color:#027EB5;text-decoration:underline;word-break:break-all}
.wa-audio{display:flex;align-items:center;gap:8px;min-width:190px}
.wa-play{width:0;height:0;border-left:12px solid #54656F;border-top:7px solid transparent;border-bottom:7px solid transparent;margin-left:4px}
.wa-onda{display:flex;align-items:center;gap:2px;height:24px}
.wa-onda i{width:3px;border-radius:2px;background:#9AA7AE}
.wa-dur{font-size:11.5px;color:#667781}
.wa-barra{display:flex;align-items:center;gap:8px;padding:8px 10px 22px;background:#F0F2F5}
.wa-campo{flex:1;background:#fff;border-radius:20px;padding:9px 14px;font-size:14px;color:#8696A0}
.wa-mic{width:38px;height:38px;border-radius:50%;background:#00A884;position:relative}
.wa-mic::after{content:"";position:absolute;left:50%;top:50%;width:8px;height:14px;border-radius:5px;background:#fff;translate:-50% -60%}
.cel-notif{position:absolute;left:10px;right:10px;top:46px;z-index:6;display:flex;gap:10px;align-items:center;padding:10px 12px;border-radius:18px;
  background:rgba(245,245,245,.92);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);box-shadow:0 12px 30px -10px rgba(0,0,0,.45);color:#111;font-size:13px;line-height:1.3}
.cel-notif b{display:block;font-size:12px;color:#555;font-weight:600}
.cel-notif span{display:block}
.cel-notif-ic{width:34px;height:34px;flex:none;border-radius:9px;background:#25D366 url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23fff'%3E%3Cpath d='M12 3a9 9 0 0 0-7.8 13.5L3 21l4.6-1.2A9 9 0 1 0 12 3z'/%3E%3C/svg%3E") center/20px no-repeat}
.cel-leg{display:flex;gap:10px;align-items:flex-start;margin-top:18px;padding:14px 16px;border-radius:16px;font-size:15px;line-height:1.45}
.cel-leg.ruim{background:rgba(255,107,94,.1);border:1px solid rgba(255,107,94,.28);color:#FFC2BC}
.cel-leg.bom{background:rgba(61,220,132,.1);border:1px solid rgba(61,220,132,.28);color:#B5F2CF}
.cel-leg b{color:#fff}
/* animação: as mensagens chegam uma a uma; a notificação desce e some */
.js-efeitos .ad2-lado .wa-b{opacity:0;transform:translateY(12px) scale(.97)}
.js-efeitos .ad2-lado.visto .wa-b{animation:waEntra .42s cubic-bezier(.2,.7,.2,1) forwards;animation-delay:calc(var(--i) * .6s + .4s)}
@keyframes waEntra{to{opacity:1;transform:none}}
.js-efeitos .ad2-lado .cel-notif{opacity:0;transform:translateY(-120%)}
.js-efeitos .ad2-lado.visto .cel-notif{animation:notif 3.2s .1s cubic-bezier(.2,.7,.2,1) forwards}
@keyframes notif{0%{opacity:0;transform:translateY(-120%)}14%,72%{opacity:1;transform:none}100%{opacity:0;transform:translateY(-120%)}}
.ad2-lado .cel-wa{transition:transform .4s cubic-bezier(.2,.7,.2,1)}
@media (hover:hover){.ad2-lado:hover .cel-wa{transform:translateY(-6px) rotate(-.6deg)}.ad2-lado.dir:hover .cel-wa{transform:translateY(-6px) rotate(.6deg)}}
@media (max-width:400px){.cel-tela{height:600px}.wa-b{font-size:13.5px}.wa-b.pedido{font-size:12.8px}}
@media (prefers-reduced-motion:reduce){.js-efeitos .ad2-lado .wa-b{opacity:1;transform:none;animation:none!important}.js-efeitos .ad2-lado .cel-notif{display:none}}
"""
k = s.index("</style>"); s = s[:k] + CSS + s[k:]
open(ARQ, "w", encoding="utf-8").write(s)
print("v6b aplicada em", ARQ)
