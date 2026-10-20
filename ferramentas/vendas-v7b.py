"""Página de vendas v7b: o celular "depois" mostra o cartão do pedido como ele aparece no painel da loja
(itens, total em destaque, entrega, pagamento, cliente e link de rastreio), no estilo do cartão de referência.
Não finge ser mensagem de WhatsApp: o WhatsApp comum só recebe texto (a mensagem de texto continua sendo enviada).
Uso: python3 ferramentas/vendas-v7b.py && python3 ferramentas/csp.py plataforma/index.html
Pode rodar de novo: não duplica nada."""
ARQ = "plataforma/index.html"
MARCA = "/* ===== v7b: cartão do pedido ===== */"
s = open(ARQ, encoding="utf-8").read()
if MARCA in s:
    raise SystemExit("plataforma/index.html já está na v7b")

ini = s.index('<div class="wa-topo">', s.index('<div class="ad2-lado revela dir">'))
barra = '<div class="wa-barra" aria-hidden="true"><span class="wa-campo">Mensagem</span><span class="wa-mic"></span></div>'
fim = s.index(barra, ini) + len(barra)

NOVO = '''<div class="pc-topo"><span class="pc-loja" aria-hidden="true">P</span><div><b>Pedidos</b><small>Padaria da Ana · ao vivo</small></div><span class="pc-novo">1 novo</span></div>
              <div class="pc-chat">
                <div class="pc-card">
                  <div class="pc-cab"><span class="pc-ico grande" aria-hidden="true">🥐</span><div><small>PEDIDO #128</small><b>Padaria da Ana</b></div></div>
                  <div class="pc-sec"><span class="pc-ico" aria-hidden="true">🛒</span><div class="pc-corpo"><b>Itens do pedido</b>
                    <p><span>2× Pão de queijo</span><i>R$ 12,00</i></p><p><span>1× Cappuccino</span><i>R$ 14,90</i></p></div></div>
                  <div class="pc-soma"><p><span>Subtotal</span><i>R$ 26,90</i></p><p><span>Entrega</span><i>R$ 5,00</i></p></div>
                  <div class="pc-total"><span>Total</span><b>R$ 31,90</b></div>
                  <div class="pc-sec"><span class="pc-ico" aria-hidden="true">📍</span><div class="pc-corpo"><small>Entrega</small><span>Rua das Flores, 120 · Centro</span></div></div>
                  <div class="pc-sec"><span class="pc-ico" aria-hidden="true">💳</span><div class="pc-corpo"><small>Pagamento</small><span>Pix</span></div></div>
                  <div class="pc-sec"><span class="pc-ico" aria-hidden="true">👤</span><div class="pc-corpo"><small>Cliente</small><span>Juliana · (42) 99876-5432</span></div></div>
                  <div class="pc-sec ult"><span class="pc-ico" aria-hidden="true">🔗</span><div class="pc-corpo"><small>Rastreio para o cliente</small><span class="pc-link">bistroconnect.com.br/pedido…</span></div></div>
                </div>
              </div>
              <div class="pc-acao" aria-hidden="true"><span class="pc-btn">Confirmar e avisar a Juliana</span></div>'''

CSS = """
/* ===== v7b: cartão do pedido ===== */
.pc-topo{display:flex;align-items:center;gap:10px;padding:8px 14px 10px 14px;background:#fff;border-bottom:1px solid #E6E1D9;color:#111}
.pc-topo b{display:block;font-size:15.5px;font-weight:600}.pc-topo small{font-size:12px;color:#667781}
.pc-loja{width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#B9774B,#8A5230);color:#fff;font:700 15px var(--f-body);display:grid;place-items:center;flex:none}
.pc-novo{margin-left:auto;background:#E7F8EE;color:#128C4F;font:700 11px var(--f-body);padding:5px 10px;border-radius:999px}
.pc-chat{flex:1;min-height:0;padding:10px 10px 0;background:#EFEAE2;overflow:hidden}
.pc-card{background:#fff;border-radius:18px;padding:12px 14px 4px;box-shadow:0 2px 8px rgba(17,24,39,.08);color:#111827}
.pc-cab{display:flex;align-items:center;gap:10px;padding-bottom:9px;border-bottom:1px solid #EEE9E1}
.pc-cab small{display:block;font-size:10.5px;letter-spacing:.06em;color:#7B8794;font-weight:600}.pc-cab b{font-size:17px;font-weight:700}
.pc-ico{width:26px;height:26px;border-radius:50%;background:#F1EEE8;display:grid;place-items:center;font-size:13px;flex:none}
.pc-ico.grande{width:38px;height:38px;font-size:19px;background:#F6E9DC}
.pc-sec{display:flex;gap:10px;padding:8px 0;border-bottom:1px solid #EEE9E1;font-size:12.5px}
.pc-sec.ult{border-bottom:0}
.pc-corpo{flex:1;min-width:0;line-height:1.35}.pc-corpo b{display:block;font-size:13px;margin-bottom:2px}.pc-corpo small{display:block;font-size:11.5px;color:#667781;font-weight:600}
.pc-corpo p,.pc-soma p{display:flex;justify-content:space-between;gap:8px;margin:1px 0}.pc-corpo i,.pc-soma i{font-style:normal;font-variant-numeric:tabular-nums}
.pc-soma{padding:7px 0 7px 36px;font-size:12.5px;color:#374151}
.pc-total{display:flex;justify-content:space-between;align-items:center;background:#DDF5E6;border-radius:10px;padding:8px 12px;margin:0 0 4px}
.pc-total span{font-weight:700;font-size:14px}.pc-total b{font-size:18px;font-weight:800}
.pc-link{display:inline-block;margin-top:3px;background:#E3EEFB;color:#1D5FB4;border-radius:7px;padding:4px 8px;text-decoration:underline;font-size:12px;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.pc-acao{padding:10px 12px 14px;background:#EFEAE2}
.pc-btn{display:block;text-align:center;background:#12A150;color:#fff;font:700 14px var(--f-body);padding:12px;border-radius:14px;box-shadow:0 4px 12px rgba(18,161,80,.35)}
.js-efeitos .ad2-lado .pc-card{opacity:0;transform:translateY(14px) scale(.98)}
.js-efeitos .ad2-lado.visto .pc-card{animation:waEntra .55s cubic-bezier(.2,.7,.2,1) 1s forwards}
@media (max-width:400px){.pc-sec{font-size:12px}.pc-card{padding:10px 12px 2px}}
@media (prefers-reduced-motion:reduce){.js-efeitos .ad2-lado .pc-card{opacity:1;transform:none;animation:none!important}}
"""
s = s[:ini] + NOVO + s[fim:]
k = s.index("</style>"); s = s[:k] + CSS + s[k:]
s = s.replace("<b>Com a Bistrô Connect:</b> 1 mensagem com tudo, conta feita e link de rastreio. Sem comissão.",
              "<b>Com a Bistrô Connect:</b> o pedido chega pronto, com a conta feita e o link de rastreio. Sem comissão.")
open(ARQ, "w", encoding="utf-8").write(s)
print("v7b aplicada em", ARQ)
