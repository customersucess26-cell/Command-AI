"""Página de vendas da plataforma, v6: copy de dor → agravamento → solução, com seções novas
(as dores do dono, a soma de um ano, antes e depois no WhatsApp, risco zero, ajuda nas perguntas,
rodapé completo e botão fixo no celular).
Pode rodar de novo: não duplica nada.  Uso: python3 ferramentas/vendas-v6.py && python3 ferramentas/csp.py plataforma/index.html"""
import re

ARQ = "plataforma/index.html"
MARCA = "/* ===== v6: página de vendas ===== */"
s = open(ARQ, encoding="utf-8").read()
if MARCA in s:
    raise SystemExit("plataforma/index.html já está na v6")


def troca(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


def ico(d):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true">' + d + '</svg>')


# ---------- topo: a dor na primeira frase ----------
troca('<h1 style="margin-top:14px">Seu balcão fecha às 19h. Seu cardápio <em>continua vendendo</em>.</h1>',
      '<h1 style="margin-top:14px">Você cozinha, atende e entrega. O app fica com <em class="risca">até 23%</em> de cada pedido.</h1>')
troca('<p class="lead">Às 22h, alguém no sofá está escolhendo o café da manhã de amanhã. Com a Bistrô Connect, essa pessoa vê suas fotos, monta o pedido e ele chega pronto no seu WhatsApp, com o total e o link para acompanhar. Você cria a loja sozinho, em minutos. Sem comissão por pedido.</p>',
      '<p class="lead">Comissão comendo a margem, WhatsApp lotado de áudio, pedido anotado errado e cliente ligando para saber se já saiu. Com a Bistrô Connect, o cliente monta o pedido sozinho no <b>seu</b> cardápio online e ele chega pronto no seu WhatsApp, com o total e o link de rastreio. <b>Sem comissão. Nunca.</b></p>')
troca('''          <a class="btn btn-mint" href="/entrar.html" data-track="cta-hero">Criar minha loja grátis</a>
          <a class="btn btn-ghost" href="#modelos">Ver os 4 modelos</a>''',
      '''          <a class="btn btn-mint" href="/entrar.html" data-track="cta-hero">Quero vender sem comissão</a>
          <a class="btn btn-ghost" href="#dor">Ver quanto eu perco hoje</a>''')
troca('<p style="margin-top:12px;font-size:14px;color:var(--on-navy-soft)">Grátis enquanto você vender até R$ 3 mil por mês. Sem cartão de crédito.</p>',
      '<p class="garantias-mini"><span>✓ Grátis até R$ 3 mil por mês</span><span>✓ Sem cartão de crédito</span><span>✓ Sem fidelidade</span></p>')

# ---------- seções novas: dores, soma de um ano, antes e depois ----------
DORES = [
    ('<path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>', 'O app come a sua margem',
     'Num pedido de R$ 80, até R$ 18,40 ficam com o app. Você paga o ingrediente, o gás e o funcionário, e divide o lucro com quem não fez nada disso.',
     'até 23% de cada pedido'),
    ('<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/><path d="M9 10h.01M12 10h.01M15 10h.01"/>', 'O WhatsApp vira um caos',
     'Áudio de 2 minutos, “tem pão de queijo?”, “quanto fica?”, endereço pela metade. Enquanto você responde um, outro desiste de esperar.',
     'pedido perdido no meio da conversa'),
    ('<path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><path d="M10 13l4 4M14 13l-4 4"/>', 'Pedido anotado errado',
     'Faltou o refrigerante, trocou o sabor, esqueceu o troco. O cliente reclama, você refaz e paga o prejuízo do próprio bolso.',
     'retrabalho e cliente insatisfeito'),
    ('<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>', '“Meu pedido já saiu?”',
     'O cliente liga três vezes. Cada ligação para a cozinha, atrasa o próximo pedido e deixa todo mundo nervoso.',
     'equipe interrompida o dia todo'),
    ('<circle cx="9" cy="7" r="4"/><path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/><path d="M17 11l4 4M21 11l-4 4"/>', 'O cliente não é seu',
     'No app, ele vê o seu concorrente logo abaixo, e você nem fica com o contato dele para chamar de volta numa promoção.',
     'cliente que não volta'),
    ('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>', 'Fora do horário, ninguém atende',
     'Às 22h alguém quer encomendar o café da manhã ou o bolo de sábado. Sem cardápio online, essa venda vai para outra casa.',
     'venda que você nem viu passar'),
]
cards = "\n".join(
    '        <article class="dor revela"><span class="dor-ico">%s</span><h3>%s</h3><p>%s</p><span class="dor-custo">%s</span></article>' % (ico(i), t, p, c)
    for i, t, p, c in DORES)

CHAT_ANTES = [
    ('e', 'Oi, boa noite! Vcs tão abertos?', '21:42'),
    ('e', 'Tem pão de queijo?', '21:42'),
    ('a', '🎤 Áudio · 1:48', '21:44'),
    ('e', 'Quanto fica 2 pão de queijo e 1 cappuccino?', '21:47'),
    ('e', 'Oi??', '21:55'),
    ('s', 'Oi! Desculpa a demora, tava no forno 🙏', '21:58'),
    ('e', 'Ah, já pedi em outro lugar', '21:59'),
]
bolhas_antes = "\n".join('            <div class="bolha %s" style="--i:%d"><span>%s</span><small>%s</small></div>' % (q, k, t, h)
                         for k, (q, t, h) in enumerate(CHAT_ANTES))

NOVAS = '''
  <section id="dor" class="dor-sec">
    <div class="in">
      <div class="head centro revela">
        <p class="eyebrow">Você se reconhece?</p>
        <h2>O problema não é falta de cliente. É tudo o que acontece entre o “oi” e a entrega.</h2>
        <p>Quem tem padaria, café, hamburgueria ou restaurante conhece bem esta rotina:</p>
      </div>
      <div class="dores">
%s
      </div>
      <div class="soma revela zoom">
        <div class="soma-txt">
          <p class="eyebrow">Agora some um ano</p>
          <h3>Quem vende R$ 10 mil por mês pelo app, no plano de entrega, deixa até <b class="vermelho" data-conta="2300" data-antes="R$ ">R$ 2.300</b> por mês em comissão.</h3>
          <p>Em 12 meses, são <b class="vermelho grande" data-conta="27600" data-antes="R$ " data-dur="1800">R$ 27.600</b> que saem do seu caixa. Dá uma reforma, uma moto de entrega ou um funcionário a mais.</p>
        </div>
        <div class="soma-acoes">
          <a class="btn btn-mint brilho-v6" href="/entrar.html" data-track="cta-dor">Quero parar de perder dinheiro</a>
          <a class="btn btn-ghost" href="#calculadora">Calcular o meu caso</a>
        </div>
      </div>
    </div>
  </section>

  <section class="dark ad-sec" id="antes-depois">
    <div class="in">
      <div class="head centro revela">
        <p class="eyebrow">Antes e depois</p>
        <h2>Do caos no WhatsApp ao pedido pronto em uma mensagem</h2>
        <p>A mesma cliente, no mesmo horário. A diferença é ter um cardápio onde ela escolhe sozinha.</p>
      </div>
      <div class="ad">
        <div class="ad-lado antes revela esq">
          <div class="ad-rot"><span class="pino ruim"></span>Hoje: pelo WhatsApp</div>
          <div class="chat">
            <div class="chat-topo"><b>Cliente</b><small>visto por último às 21:59</small></div>
%s
          </div>
          <p class="ad-res ruim">7 mensagens, 17 minutos e <b>uma venda perdida</b></p>
        </div>
        <div class="ad-seta" aria-hidden="true">→</div>
        <div class="ad-lado depois revela dir">
          <div class="ad-rot"><span class="pino bom"></span>Com a Bistrô Connect</div>
          <div class="chat">
            <div class="chat-topo"><b>Cliente</b><small>online</small></div>
            <div class="bolha e pedido" style="--i:0"><span><b>Pedido #128 · Padaria da Ana</b><br>2× Pão de queijo · R$ 12,00<br>1× Cappuccino · R$ 14,90<br>Entrega: Rua das Flores, 120<br>Pagamento: Pix<br><b>Total: R$ 31,90</b><br><u>Acompanhe o seu pedido</u></span><small>21:43</small></div>
            <div class="bolha s" style="--i:1"><span>Confirmado! Já está no forno 🥐</span><small>21:44</small></div>
            <div class="bolha e" style="--i:2"><span>Perfeito, obrigada! ❤️</span><small>21:44</small></div>
          </div>
          <p class="ad-res bom">1 mensagem, 2 minutos e <b>a venda é sua, sem comissão</b></p>
        </div>
      </div>
    </div>
  </section>
''' % (cards, bolhas_antes)
troca('''  <section id="modelos">''', NOVAS.rstrip('\n') + '\n\n  <section id="modelos">')

# ---------- calculadora: agravar ----------
troca('''        <p class="eyebrow">A conta que pouca gente faz</p>
        <h2 style="margin-top:12px">O app fica com até 23% de cada pedido. Faça a conta do seu.</h2>''',
      '''        <p class="eyebrow">Quanto isso custa para você</p>
        <h2 style="margin-top:12px">Mova a barra e veja quanto do seu dinheiro fica no app.</h2>''')
troca('''        <p>Continue no app para ser encontrado. O cliente que já conhece a sua casa pode pedir direto, e essa comissão fica com você.</p>''',
      '''        <p>Você não precisa sair do app: ele traz o cliente novo. Mas o cliente que <b>já conhece</b> a sua casa pode pedir direto no seu cardápio, e essa comissão volta para o seu bolso.</p>
        <p class="aviso-custo">Cada mês esperando é uma comissão que não volta mais.</p>''')
troca('''          <div class="good"><span>Fica com você se 1 em cada 3 pedidos vier direto</span><strong id="rEco">R$ 251</strong></div>
        </div>''',
      '''          <div class="good"><span>Fica com você se 1 em cada 3 pedidos vier direto</span><strong id="rEco">R$ 251</strong></div>
        </div>
        <div class="ano"><span>Comissão paga ao app em 12 meses</span><strong id="rAno">R$ 14.400</strong></div>''')
troca("document.getElementById('rCom').textContent=brl(com);",
      "document.getElementById('rCom').textContent=brl(com);document.getElementById('rAno').textContent=brl(com*12);")

# ---------- como funciona ----------
troca('<h2>O cliente faz o pedido sozinho. Você só confere e prepara.</h2>',
      '<h2>Em 3 passos o pedido para de dar trabalho. O cliente faz sozinho, você só confere e prepara.</h2>')

# ---------- risco zero ----------
troca('''        <p class="eyebrow">Comece hoje</p>
        <h2 style="margin-top:12px">Grátis até R$ 3 mil em vendas por mês</h2>
        <p style="color:var(--ink-soft);margin-top:16px;max-width:46ch">Crie a loja, cadastre o cardápio e divulgue o link. Você só paga quando a loja vender mais, e a mensalidade tem teto.</p>''',
      '''        <div class="selo-garantia" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/></svg></div>
        <p class="eyebrow">Risco zero</p>
        <h2 style="margin-top:12px">Se a sua loja não vender, você não paga.</h2>
        <p style="color:var(--ink-soft);margin-top:16px;max-width:46ch">O plano Começo é grátis até R$ 3 mil em vendas por mês. Sem cartão de crédito, sem taxa de implantação e sem fidelidade. Você testa com os seus clientes de verdade e decide depois.</p>''')

# ---------- perguntas: cartão de ajuda ao lado ----------
troca('''      <div class="faq">''', '''      <div class="faq-grade">
      <div class="faq">''')
troca('''        <details><summary>Os meus dados e os dos meus clientes ficam seguros?</summary>''',
      '''        <details><summary>E se eu não gostar?</summary><p>Você para quando quiser. Não tem fidelidade, multa nem taxa de cancelamento. E enquanto vender até R$ 3 mil por mês, não paga nada.</p></details>
        <details><summary>Os meus dados e os dos meus clientes ficam seguros?</summary>''')
j = s.index('</div>', s.index('Os meus dados e os dos meus clientes ficam seguros?'))
s = s[:j + 6] + '''
      <aside class="ajuda revela dir">
        <span class="ajuda-ico">''' + ico('<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/>') + '''</span>
        <h3>Ainda com dúvida?</h3>
        <p>Fale com uma pessoa de verdade no WhatsApp. A gente responde e, se você quiser, ajuda a montar o cardápio com você.</p>
        <a class="btn btn-mint" id="faqZap" href="#" target="_blank" rel="noopener" data-track="whatsapp-faq">Chamar no WhatsApp</a>
        <a class="btn btn-ghost-claro" href="/entrar.html">Ou criar a loja agora</a>
      </aside>
      </div>''' + s[j + 6:]
troca("  wf.addEventListener('click',function(){track('Contact')});",
      "  wf.addEventListener('click',function(){track('Contact')});\n  var fz=document.getElementById('faqZap');if(fz){fz.href=waLink('Olá! Tenho uma dúvida sobre a Bistrô Connect antes de criar a minha loja.');fz.addEventListener('click',function(){track('Contact')})}")

# ---------- chamada final ----------
troca('''        <p class="eyebrow">Prefere ajuda?</p>
        <h2 style="margin-top:12px">Crie sozinho em minutos, ou mande seus dados que a gente te ajuda a montar.</h2>
        <p style="color:var(--on-navy-soft);margin-top:16px;max-width:42ch">A conversa continua no WhatsApp: tiramos as dúvidas e ajudamos a cadastrar o cardápio e as fotos.</p>''',
      '''        <p class="eyebrow">A decisão é sua</p>
        <h2 style="margin-top:12px">Amanhã vai chegar mais um pedido pelo app. Ele vai te custar até 23%.</h2>
        <p style="color:var(--on-navy-soft);margin-top:16px;max-width:44ch">Ou você pode começar hoje a trazer os seus clientes para o seu próprio cardápio. Leva 5 minutos e é grátis. Prefere ajuda? Mande seus dados ao lado que a gente monta com você pelo WhatsApp.</p>''')
troca('<a class="btn btn-mint" href="/entrar.html" data-track="cta-final">Criar minha loja grátis</a>',
      '<a class="btn btn-mint" href="/entrar.html" data-track="cta-final">Criar minha loja grátis agora</a>')

# ---------- rodapé completo e botão fixo no celular ----------
i = s.index('<footer>'); j = s.index('</footer>') + len('</footer>')
s = s[:i] + '''<footer>
  <div class="in rodape-v6">
    <div class="rod-marca">
      <img src="/assets/img/logo-bistro-connect-clara.png" alt="Bistrô Connect" width="302" height="170" loading="lazy">
      <p>Cardápio digital, pedido pronto no WhatsApp e painel completo para padarias, cafés, hamburguerias e restaurantes. Sem comissão por pedido.</p>
    </div>
    <nav aria-label="Produto"><b>Produto</b><a href="#modelos">Modelos</a><a href="#como-funciona">Como funciona</a><a href="#calculadora">Quanto você economiza</a><a href="#planos">Planos</a></nav>
    <nav aria-label="Sua conta"><b>Sua conta</b><a href="/entrar.html">Criar loja grátis</a><a href="/painel/">Entrar no painel</a><a href="#contato">Pedir ajuda</a></nav>
    <nav aria-label="Informações"><b>Informações</b><a href="/termos.html">Termos de uso</a><a href="/privacidade.html">Política de privacidade</a></nav>
    <p class="rod-copy">© <span id="ano"></span> Bistrô Connect · Feito para quem vive de comida</p>
  </div>
</footer>

<div class="cta-fixa" id="ctaFixa" data-aparece-apos=".hero"><a class="btn btn-mint" href="/entrar.html" data-track="cta-fixo">Criar minha loja grátis</a></div>''' + s[j:]

# ---------- estilos ----------
CSS = MARCA + r"""
.centro{margin-left:auto;margin-right:auto;text-align:center;align-items:center}
.hero .lead b{color:#fff}
.hero h1{font-size:clamp(32px,4.3vw,56px)!important}
@media (max-width:560px){.hero h1{font-size:34px!important}.hero .lead{font-size:17px}}
.risca{position:relative;white-space:nowrap}
.risca::after{content:"";position:absolute;left:-2%;right:-2%;top:54%;height:.09em;border-radius:4px;background:#FF5A4E;transform:scaleX(0);transform-origin:left;animation:riscar .7s 1.1s cubic-bezier(.6,0,.2,1) forwards;box-shadow:0 0 18px rgba(255,90,78,.6)}
@keyframes riscar{to{transform:scaleX(1)}}
.garantias-mini{display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:14px;font-size:14px;color:var(--on-navy-soft)}
.garantias-mini span{white-space:nowrap}
/* dores */
.dor-sec{background:linear-gradient(180deg,#FFF6F4 0%,var(--paper) 70%)}
.dores{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}
@media (max-width:980px){.dores{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:620px){.dores{grid-template-columns:1fr}}
.dor{background:#fff;border:1px solid #F1DCD8;border-radius:20px;padding:26px 24px 22px;display:flex;flex-direction:column;gap:10px;position:relative;overflow:hidden;
  box-shadow:0 18px 40px -32px rgba(120,30,20,.45);transition:transform .3s cubic-bezier(.2,.7,.2,1),box-shadow .3s,border-color .3s}
.dor::before{content:"";position:absolute;inset:0 0 auto;height:4px;background:linear-gradient(90deg,#E5484D,#FF8A5B);transform:scaleX(.18);transform-origin:left;transition:transform .5s cubic-bezier(.2,.7,.2,1)}
.dor:hover{transform:translateY(-6px);border-color:#F3B7AE;box-shadow:0 30px 60px -34px rgba(160,40,25,.55)}
.js-efeitos .dor.revela.visto:hover{transform:translateY(-6px)}
.dor:hover::before{transform:scaleX(1)}
.dor-ico{width:52px;height:52px;border-radius:16px;display:grid;place-items:center;background:#FFE9E5;color:#D93A2F}
.dor-ico svg{width:26px;height:26px}
.dor:hover .dor-ico svg{animation:tremer .5s ease}
@keyframes tremer{20%{transform:rotate(-12deg)}40%{transform:rotate(10deg)}60%{transform:rotate(-6deg)}80%{transform:rotate(3deg)}}
.dor h3{font-size:20px;color:var(--ink)}
.dor p{color:var(--ink-soft);font-size:15.5px;line-height:1.55;flex:1}
.dor-custo{align-self:flex-start;display:inline-flex;align-items:center;gap:8px;font-size:13px;font-weight:700;color:#B4231A;background:#FFF0ED;border:1px solid #F7CFC8;padding:6px 12px;border-radius:99px}
.dor-custo::before{content:"";width:7px;height:7px;border-radius:50%;background:#E5484D;box-shadow:0 0 0 0 rgba(229,72,77,.6);animation:pulsa 1.8s infinite}
@keyframes pulsa{70%{box-shadow:0 0 0 8px rgba(229,72,77,0)}100%{box-shadow:0 0 0 0 rgba(229,72,77,0)}}
.soma{margin-top:34px;border-radius:26px;padding:clamp(26px,4vw,44px);background:radial-gradient(60% 120% at 100% 0%,rgba(229,72,77,.28),transparent 60%),var(--navy);color:var(--on-navy);
  display:grid;grid-template-columns:minmax(0,1.5fr) auto;gap:28px;align-items:center;box-shadow:0 40px 80px -40px rgba(14,21,38,.7);position:relative;overflow:hidden}
.soma::after{content:"";position:absolute;right:-60px;bottom:-60px;width:220px;height:220px;border-radius:50%;border:2px dashed rgba(255,255,255,.08);animation:gira 40s linear infinite}
@keyframes gira{to{transform:rotate(360deg)}}
@media (max-width:860px){.soma{grid-template-columns:1fr}}
.soma h3{font-size:clamp(21px,2.4vw,28px);line-height:1.3;margin-top:10px;color:#fff}
.soma p{color:var(--on-navy-soft);margin-top:12px;font-size:17px}
.vermelho{color:#FF6B5E;font-variant-numeric:tabular-nums;white-space:nowrap}
.vermelho.grande{font-size:1.35em;font-family:var(--f-display)}
.soma-acoes{display:flex;flex-direction:column;gap:10px;position:relative;z-index:1}
@media (max-width:860px){.soma-acoes{flex-direction:row;flex-wrap:wrap}}
.brilho-v6{background:linear-gradient(90deg,#FF7A59,#E5484D)!important;color:#fff!important;box-shadow:0 14px 34px -12px rgba(229,72,77,.8)!important}
/* antes e depois */
.ad{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);gap:22px;align-items:start;max-width:980px;margin:0 auto}
@media (max-width:820px){.ad{grid-template-columns:1fr}.ad-seta{transform:rotate(90deg);justify-self:center}}
.ad-seta{align-self:center;font-size:34px;color:var(--mint);animation:empurra 1.6s ease-in-out infinite}
@keyframes empurra{50%{translate:6px 0}}
.ad-rot{display:flex;align-items:center;gap:8px;font-weight:700;font-size:14px;letter-spacing:.06em;text-transform:uppercase;margin-bottom:12px;color:var(--on-navy)}
.pino{width:10px;height:10px;border-radius:50%}.pino.ruim{background:#FF6B5E}.pino.bom{background:#3DDC84}
.chat{background:#0B141A;border-radius:22px;padding:0 12px 14px;min-height:430px;border:1px solid #1F2C34;box-shadow:0 30px 60px -30px rgba(0,0,0,.8);overflow:hidden;
  background-image:radial-gradient(rgba(255,255,255,.03) 1px,transparent 1px);background-size:18px 18px}
.chat-topo{display:flex;flex-direction:column;padding:12px 6px;margin:0 -12px 12px;padding-left:18px;background:#1F2C34;color:#E9EDEF}
.chat-topo b{font-size:15px}.chat-topo small{font-size:12px;color:#8696A0}
.bolha{display:flex;flex-direction:column;max-width:86%;margin:6px 0;padding:7px 10px 5px;border-radius:12px;font-size:14px;line-height:1.4;color:#E9EDEF;position:relative}
.bolha small{align-self:flex-end;font-size:10.5px;color:#8696A0;margin-top:2px}
.bolha.e{background:#202C33;border-top-left-radius:4px}
.bolha.a{background:#202C33;border-top-left-radius:4px;font-style:italic;color:#B9C5CB}
.bolha.s{background:#005C4B;margin-left:auto;border-top-right-radius:4px}
.bolha.pedido{background:#202C33;max-width:92%;font-size:13.5px}
.bolha.pedido u{color:#53BDEB;text-decoration:none}
.js-efeitos .ad-lado .bolha{opacity:0;transform:translateY(10px) scale(.96)}
.js-efeitos .ad-lado.visto .bolha{animation:bolhaEntra .45s cubic-bezier(.2,.7,.2,1) forwards;animation-delay:calc(var(--i) * .55s + .3s)}
@keyframes bolhaEntra{to{opacity:1;transform:none}}
.ad-res{margin-top:14px;font-size:15px;padding:12px 14px;border-radius:14px}
.ad-res.ruim{background:rgba(255,107,94,.12);color:#FFB4AC}
.ad-res.bom{background:rgba(61,220,132,.12);color:#A6F0C6}
.ad-res b{color:#fff}
/* calculadora */
.aviso-custo{margin-top:16px;font-weight:700;color:#B4231A;display:flex;align-items:center;gap:8px}
.aviso-custo::before{content:"!";display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;background:#E5484D;color:#fff;font-size:13px;flex:none}
.calc-box .ano{margin-top:12px;display:flex;justify-content:space-between;align-items:center;gap:12px;padding:14px 16px;border-radius:14px;background:#FFF0ED;border:1px dashed #F3B7AE}
.calc-box .ano span{font-size:14px;color:#7A2A22;font-weight:600}
.calc-box .ano strong{font-family:var(--f-display);font-size:24px;color:#C62F24;font-variant-numeric:tabular-nums}
/* risco zero */
.selo-garantia{width:64px;height:64px;border-radius:20px;display:grid;place-items:center;background:var(--mint-soft);color:var(--mint-deep);margin-bottom:16px;position:relative}
.selo-garantia svg{width:34px;height:34px}
.selo-garantia::after{content:"";position:absolute;inset:-6px;border-radius:24px;border:2px solid var(--mint);opacity:0;animation:onda 2.4s ease-out infinite}
@keyframes onda{0%{opacity:.7;transform:scale(.9)}100%{opacity:0;transform:scale(1.25)}}
/* perguntas com ajuda */
.faq-grade{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:28px;align-items:start}
@media (max-width:900px){.faq-grade{grid-template-columns:1fr}}
.faq-grade .faq{max-width:none}
.ajuda{position:sticky;top:96px;background:var(--navy);color:var(--on-navy);border-radius:24px;padding:28px;display:flex;flex-direction:column;gap:12px;box-shadow:0 30px 60px -36px rgba(14,21,38,.8);overflow:hidden}
.ajuda::before{content:"";position:absolute;right:-50px;top:-50px;width:180px;height:180px;border-radius:50%;background:radial-gradient(circle,rgba(37,211,102,.35),transparent 70%)}
.ajuda-ico{width:52px;height:52px;border-radius:16px;display:grid;place-items:center;background:#25D366;color:#fff;position:relative}
.ajuda-ico svg{width:28px;height:28px}
.ajuda h3{font-size:22px;color:#fff}.ajuda p{color:var(--on-navy-soft)}
.ajuda .btn{width:100%}
.btn-ghost-claro{background:transparent;color:var(--on-navy);border:1px solid var(--navy-3)}
/* rodapé */
.rodape-v6{display:grid!important;grid-template-columns:minmax(0,1.6fr) repeat(3,minmax(0,1fr));gap:28px;align-items:start!important;padding-top:20px}
@media (max-width:900px){.rodape-v6{grid-template-columns:1fr 1fr}.rod-marca{grid-column:1/-1}}
.rod-marca img{height:64px;width:auto;margin-bottom:12px}
.rod-marca p{max-width:40ch;line-height:1.6}
.rodape-v6 nav{display:flex;flex-direction:column;gap:8px}
.rodape-v6 nav b{color:#fff;font-size:13px;letter-spacing:.08em;text-transform:uppercase;margin-bottom:4px}
.rodape-v6 nav a{color:var(--on-navy-soft);text-decoration:none;transition:color .2s,translate .2s}
.rodape-v6 nav a:hover{color:#fff;translate:3px 0}
.rod-copy{grid-column:1/-1;border-top:1px solid var(--navy-2);padding-top:18px;margin-top:6px;font-size:13px}
/* botão fixo no celular */
.cta-fixa{display:none}
@media (max-width:760px){
  .cta-fixa{display:block;position:fixed;left:12px;right:84px;bottom:calc(14px + env(safe-area-inset-bottom,0px));z-index:60;transform:translateY(140%);transition:transform .4s cubic-bezier(.2,.7,.2,1)}
  .cta-fixa.mostra{transform:none}
  .cta-fixa .btn{width:100%;box-shadow:0 16px 34px -12px rgba(43,168,255,.9)}
  body{padding-bottom:84px}
}
@media (prefers-reduced-motion:reduce){.risca::after{animation:none;transform:scaleX(1)}.js-efeitos .ad-lado .bolha{opacity:1;transform:none;animation:none!important}.dor-custo::before,.soma::after,.ad-seta,.selo-garantia::after{animation:none}}
"""
i = s.index("</style>"); s = s[:i] + CSS + s[i:]
open(ARQ, "w", encoding="utf-8").write(s)
print("v6 aplicada em", ARQ)
