"""Gera manual/manual-venda-e-entrega.html (e o PDF, abrindo no Chrome) com o passo a passo de vender e entregar
a Plataforma Bistrô Connect e os sites de marca. Usa o CSS do manual principal e os prints de manual/manual-img/.
Uso:  python3 ferramentas/montar-manual-entrega.py   (depois: python3 ferramentas/pdf-manual-entrega.py)"""
import re

base = open("manual/manual.html", encoding="utf-8").read()
css = re.search(r"<style>(.*?)</style>", base, re.S).group(1)
css += r"""
@page{@bottom-right{content:counter(page);font:500 8.5pt 'DM Sans',Arial,sans-serif;color:#9AA3B2}@bottom-left{content:"Manual de Venda e Entrega · Bistrô Connect";font:500 8.5pt 'DM Sans',Arial,sans-serif;color:#9AA3B2}}
@page :first{@bottom-right{content:none}@bottom-left{content:none}}
/* divisória de parte */
.pg.parte{page:parte;width:210mm;height:297mm;margin:0;overflow:hidden;background:radial-gradient(120% 80% at 80% 0%,#1C3A63 0%,var(--navy) 55%,#080C17 100%);color:#fff;display:flex;flex-direction:column;justify-content:center;align-items:flex-start;padding:0 24mm;break-before:page;break-after:page}
@page parte{margin:0;@bottom-right{content:none}@bottom-left{content:none}}
.pg.parte .p{font:600 10pt 'Poppins';letter-spacing:.32em;color:var(--ouro);text-transform:uppercase}
.pg.parte h1{color:#fff;font-size:38pt;margin:6mm 0 5mm;letter-spacing:-.01em}
.pg.parte .linha{width:46mm;height:3px;background:var(--ouro);margin:2mm 0 7mm}
.pg.parte p.sub{font-size:13pt;color:#C9D3E3;max-width:125mm}
.pg.parte ul{list-style:none;padding:0;margin:9mm 0 0;color:#E6ECF5;font-size:11.5pt}.pg.parte li{margin:3mm 0}.pg.parte li b{color:var(--ouro);font-family:'Poppins';margin-right:8px}
/* fluxo horizontal */
.fluxo{display:flex;align-items:stretch;gap:0;margin:12px 0 16px;break-inside:avoid}
.fluxo .f{flex:1;background:#fff;border:1px solid var(--linha);border-radius:12px;padding:10px 10px 11px;position:relative;text-align:center;margin-right:16px}
.fluxo .f:last-child{margin-right:0}
.fluxo .f::after{content:"›";position:absolute;right:-14px;top:50%;transform:translateY(-55%);font:700 18pt 'Poppins';color:var(--ouro)}
.fluxo .f:last-child::after{display:none}
.fluxo .f i{display:block;font:700 13pt 'Poppins';font-style:normal;color:var(--ouro);margin-bottom:2px}
.fluxo .f b{display:block;font:600 9.5pt 'Poppins';color:var(--navy);line-height:1.25}
.fluxo .f span{display:block;font-size:8.5pt;color:var(--suave);margin-top:3px;line-height:1.3}
.fluxo.esc .f{background:var(--navy);border-color:var(--navy)}.fluxo.esc .f b{color:#fff}.fluxo.esc .f span{color:#C9D3E3}
/* linha do tempo */
.tl{margin:10px 0 14px;border-left:3px solid var(--ouro2);padding-left:0}
.tl .d{display:grid;grid-template-columns:62px 1fr;gap:14px;padding:8px 0 8px 0;position:relative;break-inside:avoid}
.tl .d::before{content:"";position:absolute;left:-8px;top:14px;width:13px;height:13px;border-radius:50%;background:var(--ouro);border:3px solid #fff;box-shadow:0 0 0 2px var(--ouro2)}
.tl .d>b{font:700 10.5pt 'Poppins';color:var(--navy);padding-left:14px}
.tl .d p{margin:0;font-size:10pt;color:var(--tinta)}.tl .d p b{font-family:'Poppins';font-size:10pt}
/* prints em celular e em tela */
.cels{display:flex;justify-content:center;gap:14px;margin:10px 0 14px;break-inside:avoid}
.cel{width:40mm;margin:0;text-align:center}
.cel .ph{height:68mm;overflow:hidden;border-radius:16px;border:3px solid #1B2438;box-shadow:0 10px 22px -14px rgba(14,21,38,.7);background:#fff}
.cel .ph img{width:100%;display:block}
.cel figcaption,.tl2 figcaption,.tela figcaption{font-size:8.5pt;color:var(--suave);margin-top:5px;line-height:1.3}
.cels.g .cel{width:56mm}.cels.g .cel .ph{height:106mm}
.tela{margin:10px 0 14px;break-inside:avoid;text-align:center}
.tela img{width:100%;display:block;border-radius:10px;border:1px solid var(--linha);box-shadow:0 8px 20px -12px rgba(14,21,38,.5)}
.tela.m img{width:78%;margin:0 auto}
.tela2{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0 14px;break-inside:avoid}
.tela2 .tela{margin:0}
.tela2 img{width:auto;max-width:100%;max-height:92mm;margin:0 auto;border-radius:10px;border:1px solid var(--linha)}
.passo .ond{display:block;margin-top:5px;font-size:9.5pt;color:var(--suave)}
.passo .ond b{color:var(--ouro);font-family:'Poppins';font-size:8pt;letter-spacing:.1em;text-transform:uppercase}
.msg{background:#F3F6FA;border-left:4px solid var(--azul);border-radius:0 10px 10px 0;padding:10px 14px;font-size:10pt;margin:8px 0 12px;break-inside:avoid;white-space:pre-line}
.msg b.t{display:block;font:600 8pt 'Poppins';letter-spacing:.12em;text-transform:uppercase;color:#0B5B9E;margin-bottom:3px}
h3.sec{font-size:12pt;margin:16px 0 6px;color:var(--navy);border-left:4px solid var(--ouro);padding-left:10px}
td small{color:var(--suave)}
.form td:first-child{width:46%;font-weight:600;color:var(--navy)}
.form td:last-child{height:9mm;background:#fff}
.assin{display:grid;grid-template-columns:1fr 1fr;gap:18mm;margin-top:16mm}
.assin div{border-top:1.5px solid var(--navy);padding-top:3mm;font-size:9.5pt;color:var(--suave);text-align:center}
.mini{font-size:9pt;color:var(--suave)}
/* compactação: menos páginas quase vazias */
td{padding:6px 10px!important;font-size:9.6pt}th{padding:7px 10px!important}
.passo{padding:7px 0!important}.passo p{font-size:10.3pt;margin-bottom:4px}
.av{margin:8px 0!important;padding:10px 13px!important}.av p{font-size:10.2pt;margin:0}
h3.sec{margin:12px 0 5px!important}.intro{margin-bottom:10px!important;padding-bottom:9px!important}
.check li{margin:4px 0}.tela.m img{width:60%}
.tela2 img{max-height:80mm}.tela2.p img{max-height:46mm}
.dois{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:10px 0}
.dois .card h4{font-size:12pt}
.selo{display:inline-block;font:600 8pt 'Poppins';letter-spacing:.1em;text-transform:uppercase;padding:3px 10px;border-radius:99px;background:var(--navy);color:var(--ouro);margin-bottom:6px}
.selo.v{background:var(--verde2);color:var(--verde)}
.rec{border:2px solid var(--ouro)!important;position:relative}
.rec::before{content:"RECOMENDADO";position:absolute;top:-9px;right:14px;background:var(--ouro);color:var(--navy);font:700 7.5pt 'Poppins';letter-spacing:.12em;padding:2px 10px;border-radius:99px}
"""


def cap(n, titulo, intro):
    return f'<div class="cap"><div class="n">{n}</div><h2>{titulo}</h2></div><p class="intro">{intro}</p>'


def passo(titulo, texto, onde=""):
    o = f'<span class="ond"><b>Onde</b> {onde}</span>' if onde else ""
    return f'<div class="passo"><div><b class="t">{titulo}</b><p>{texto}</p>{o}</div></div>'


def av(tipo, titulo, texto):
    ic = {"dica": "i", "cuidado": "!", "ok": "✓"}[tipo]
    return f'<div class="av {tipo}"><div class="i">{ic}</div><div><b class="t">{titulo}</b>{texto}</div></div>'


def check(*itens):
    return '<ul class="check">' + "".join(f"<li><span>{i}</span></li>" for i in itens) + "</ul>"


def msg(titulo, texto):
    return f'<div class="msg"><b class="t">{titulo}</b>{texto}</div>'


def fluxo(*itens, esc=False):
    h = '<div class="fluxo' + (' esc' if esc else '') + '">'
    for i, (t, s) in enumerate(itens, 1):
        h += f'<div class="f"><i>{i}</i><b>{t}</b><span>{s}</span></div>'
    return h + '</div>'


def tl(*itens):
    return '<div class="tl">' + "".join(f'<div class="d"><b>{d}</b><p>{t}</p></div>' for d, t in itens) + '</div>'


def cel(img, cap, topo=0):
    return f'<figure class="cel"><div class="ph"><img src="manual-img/{img}.jpg" alt="{cap}" style="margin-top:-{topo}px"></div><figcaption>{cap}</figcaption></figure>'


def cels(*itens, g=False):
    return '<div class="cels' + (' g' if g else '') + '">' + "".join(cel(*i) for i in itens) + '</div>'


def tela(img, capt, m=False):
    return f'<figure class="tela{" m" if m else ""}"><img src="manual-img/{img}.jpg" alt="{capt}"><figcaption>{capt}</figcaption></figure>'


def tela2(*itens, cls=''):
    return '<div class="tela2 ' + cls + '">' + "".join(tela(i, c) for i, c in itens) + '</div>'


def parte(p, titulo, sub, itens):
    li = "".join(f"<li><b>{n}</b>{t}</li>" for n, t in itens)
    return f'<section class="pg parte"><div class="p">{p}</div><h1>{titulo}</h1><div class="linha"></div><p class="sub">{sub}</p><ul>{li}</ul></section>'


P = []
add = P.append

# ---------------------------------------------------------------- capa
add('''<section class="pg capa">
  <div class="topo">Documento interno · Vendas e entrega</div>
  <div class="meio">
    <img src="logo-clara.png" alt="Bistrô Connect">
    <h1>Manual de Venda<br>e Entrega</h1>
    <div class="linha"></div>
    <p class="sub">Como vender e entregar a Plataforma Bistrô Connect e os sites de marca, do primeiro contato ao pós-venda, com mensagens prontas e listas para marcar.</p>
  </div>
  <div class="rod"><span>bistroconnect.com.br</span><span>Edição de outubro de 2026</span></div>
</section>''')

# ---------------------------------------------------------------- sumário
add('<section class="pg">' + cap("≡", "Sumário", "Leia a Parte 1 e a Parte 2 na primeira vez. Depois use o manual como consulta: cada capítulo termina com uma lista para marcar.") + '''
  <div class="sumario">
    <div><span>01</span><b>O que você vende</b></div>
    <div><span>02</span><b>Qual produto oferecer</b></div>
    <div><span>03</span><b>O que precisa estar pronto</b></div>
    <div><span>04</span><b>Da conversa ao “sim”</b></div>
    <div><span>05</span><b>Entrega da plataforma: visão geral</b></div>
    <div><span>06</span><b>Entrega da plataforma: passo a passo</b></div>
    <div><span>07</span><b>O dia a dia da loja</b></div>
    <div><span>08</span><b>Pós-venda: dia 1, 7 e 30</b></div>
    <div><span>09</span><b>Site de marca: proposta e escopo</b></div>
    <div><span>10</span><b>Site de marca: entrega passo a passo</b></div>
    <div><span>11</span><b>Site completo com banco próprio</b></div>
    <div><span>12</span><b>Aceite e termo de entrega</b></div>
    <div><span>13</span><b>Cobrança e contratos</b></div>
    <div><span>14</span><b>Suporte: problemas e soluções</b></div>
    <div><span>15</span><b>Segurança e LGPD</b></div>
    <div><span>A–E</span><b>Anexos: mensagens, listas e modelos</b></div>
  </div>''' + av("dica", "Como este manual está organizado", "<p><b>Parte 1</b> explica o que existe. <b>Parte 2</b> é a venda e a entrega da plataforma (o produto principal). <b>Parte 3</b> é a venda e a entrega de sites. <b>Parte 4</b> cobre cobrança, suporte e segurança. Os <b>anexos</b> têm tudo para copiar e imprimir.</p>") + '</section>')

# ================================================================ PARTE 1
add(parte("Parte 1", "Visão geral", "O que você vende, para quem e o que precisa estar pronto antes da primeira conversa.", [("01", "O que você vende"), ("02", "Qual produto oferecer"), ("03", "O que precisa estar pronto")]))

add('<section class="pg">' + cap("01", "O que você vende", "Três formatos, uma mesma ideia: o dono vende direto pelo WhatsApp, sem pagar comissão sobre cada pedido.") + '''
  <div class="grid3">
    <div class="card"><span class="selo">Produto principal</span><h4>Plataforma</h4><p>A loja do cliente fica pronta em <code>/l/nome-da-loja</code>: cardápio com fotos, pedido, cartão do pedido em imagem, rastreio e painel com equipe.</p></div>
    <div class="card rec"><span class="selo">Para marcas</span><h4>Site de marca + plataforma</h4><p>Site institucional no domínio do cliente (história, fotos, contato) com botão “Pedir agora” que leva à loja na plataforma.</p></div>
    <div class="card"><span class="selo">Sob medida</span><h4>Site completo independente</h4><p>Site e painel próprios, com banco de dados exclusivo do cliente. Modelo dos sites Âmbar, Bruto Burger e Padaria &amp; Café.</p></div>
  </div>
  <h3 class="sec">Comparativo rápido</h3>
  <table>
    <tr><th></th><th>Plataforma</th><th>Site de marca + plataforma</th><th>Site completo independente</th></tr>
    <tr><td><b>Para quem</b></td><td>Quem quer vender logo, com cardápio e pedidos</td><td>Quem quer marca forte e domínio próprio</td><td>Quem exige controle total ou dados separados</td></tr>
    <tr><td><b>Tempo de entrega</b></td><td>1 a 2 horas</td><td>3 a 7 dias úteis</td><td>5 a 10 dias úteis</td></tr>
    <tr><td><b>Domínio</b></td><td>bistroconnect.com.br/l/…</td><td>Do cliente (ex.: padariaflor.com.br)</td><td>Do cliente</td></tr>
    <tr><td><b>Banco de dados</b></td><td>Compartilhado, cada loja isolada por regras de acesso</td><td>O mesmo da plataforma</td><td>Projeto próprio no Supabase</td></tr>
    <tr><td><b>Novidades do produto</b></td><td>Chegam sozinhas</td><td>Chegam sozinhas na loja</td><td>Precisam ser aplicadas uma a uma</td></tr>
    <tr><td><b>Custo fixo para você</b></td><td>Quase zero por loja</td><td>Domínio do cliente</td><td>Domínio e banco por cliente</td></tr>
    <tr><td><b>Cobrança</b></td><td>Mensalidade pela faixa de vendas</td><td>Implantação + mensalidade da plataforma</td><td>Implantação + manutenção mensal</td></tr>
  </table>
  ''' + av("ok", "Regra de ouro", "<p>Venda a plataforma primeiro. O site de marca entra como complemento, para quem já está vendendo e quer fortalecer a marca. O site independente é exceção: dá mais trabalho e mais custo, então precifique à parte.</p>") + '</section>')

add('<section class="pg">' + cap("02", "Qual produto oferecer", "Duas ou três perguntas na primeira conversa já mostram o caminho certo.") + '''
  <h3 class="sec">O caminho de decisão</h3>
  <div class="fluxo esc">
    <div class="f"><i>?</i><b>O cliente já vende no WhatsApp ou no Instagram?</b><span>Sim: ele precisa de organização, não de site.</span></div>
    <div class="f"><i>→</i><b>Quer começar logo, sem investir muito?</b><span>Plataforma.</span></div>
    <div class="f"><i>→</i><b>Quer marca, história e domínio próprio?</b><span>Site de marca + plataforma.</span></div>
    <div class="f"><i>→</i><b>Exige dados separados ou recursos próprios?</b><span>Site completo independente.</span></div>
  </div>
  <h3 class="sec">Sinais que aparecem na conversa</h3>
  <table>
    <tr><th>O cliente diz…</th><th>Ofereça</th><th>Por quê</th></tr>
    <tr><td>“Perco pedido no meio das mensagens do WhatsApp”</td><td><b>Plataforma</b></td><td>O pedido chega organizado, com cartão em imagem e status.</td></tr>
    <tr><td>“Pago muito para o iFood / app de entrega”</td><td><b>Plataforma</b></td><td>Sem comissão por pedido. A mensalidade só cresce com as vendas.</td></tr>
    <tr><td>“Quero um site bonito com a minha cara”</td><td><b>Site de marca + plataforma</b></td><td>Marca no domínio dele, venda dentro da plataforma.</td></tr>
    <tr><td>“Tenho várias unidades” ou “quero tudo isolado”</td><td><b>Site completo independente</b></td><td>Banco próprio, sem compartilhar nada com outras lojas.</td></tr>
    <tr><td>“Só quero ver como funciona”</td><td><b>Demonstração</b></td><td>Mostre uma loja de exemplo no celular, em 10 minutos.</td></tr>
  </table>
  ''' + av("cuidado", "O que não prometer", "<p>Não prometa pedido automático para o WhatsApp da loja sem o cliente tocar em nada: o WhatsApp não permite isso fora da API oficial (paga). Hoje o cliente final toca em <b>Enviar no WhatsApp</b> e escolhe o contato da loja; o cartão do pedido vai como imagem.</p>") + '</section>')

add('<section class="pg">' + cap("03", "O que precisa estar pronto", "Antes de vender, confira o seu lado. Isso evita travar a entrega no meio.") + '''
  <div class="dois">
    <div class="card"><span class="tag">Contas</span><h4>Acessos que você usa</h4>''' + check("Hostinger (hPanel) com acesso ao Gerenciador de Arquivos", "Supabase: projeto da plataforma e, se vender site independente, uma conta com limite para novos projetos", "GitHub, o cofre do código (repositório Command-AI)", "Celular com aplicativo autenticador (Google Authenticator)", "Gerenciador de senhas para guardar tudo") + '''</div>
    <div class="card"><span class="tag">Material</span><h4>O que mostrar ao cliente</h4>''' + check("Link de uma loja de demonstração pronta, aberta no celular", "Painel de demonstração (botão “Ver demonstração” em /painel/)", "Fotos de exemplo da plataforma e do site Âmbar, Bruto e Padaria", "Termos de uso e Política de privacidade publicados", "Dados da empresa preenchidos em <code>assets/config.js</code>") + '''</div>
  </div>
  <h3 class="sec">Dados da empresa nos Termos e na Privacidade</h3>
  <p>Estes campos ficam no arquivo <code>assets/config.js</code>, dentro de <code>empresa</code>. Enquanto estiverem vazios, os documentos mostram o texto “a preencher”. Preencha antes da primeira venda.</p>
  <table class="form">
    <tr><td>Razão social</td><td></td></tr><tr><td>CNPJ</td><td></td></tr><tr><td>E-mail de suporte e privacidade</td><td></td></tr><tr><td>Cidade e estado (foro)</td><td></td></tr>
  </table>
  ''' + av("dica", "Modo convite", "<p>Por enquanto a plataforma funciona em <b>modo convite</b>: você escolhe quem entra e entrega o link de cadastro pessoalmente. Não divulgue o cadastro aberto nem a palavra “grátis” em anúncios. A mensalidade do plano inicial é zero, mas isso é uma condição que você oferece, não uma promessa pública.</p>") + '</section>')

# ================================================================ PARTE 2
add(parte("Parte 2", "Plataforma", "Do primeiro contato à loja no ar: como vender, entregar, treinar o cliente e acompanhar depois.", [("04", "Da conversa ao “sim”"), ("05", "Entrega: visão geral"), ("06", "Entrega: passo a passo"), ("07", "O dia a dia da loja"), ("08", "Pós-venda")]))

add('<section class="pg">' + cap("04", "Da conversa ao “sim”", "A venda da plataforma é curta: uma conversa, uma demonstração de dez minutos e uma proposta de uma tela.") + fluxo(("Abordagem", "mensagem curta no Instagram ou WhatsApp"), ("Demonstração", "10 minutos, loja de exemplo no celular"), ("Proposta", "o que está incluso e quanto custa"), ("Fechamento", "cadastro ao vivo e combinado de data")) + '''
  <h3 class="sec">Roteiro da demonstração (10 minutos)</h3>
  <div class="passos">''' + passo("Comece pelo cliente final", "Abra a loja de exemplo no celular. Mostre o cardápio com fotos, escolha um prato com opcionais e vá até o final do pedido.", "Mostre a vitrine, a sacola, os dados do pedido e a tela “Pedido recebido”.") + passo("Mostre o cartão do pedido", "Na tela “Pedido recebido” o cliente vê o cartão com os itens e toca em <b>Enviar no WhatsApp</b>. Pause aqui: é o diferencial. A loja recebe uma imagem organizada, não um texto solto.") + passo("Passe para o painel da loja", "No painel de demonstração, mostre o pedido chegando, o quadro de etapas e o botão que muda o status. O cliente final acompanha tudo pelo link de rastreio.") + passo("Fale do custo sem rodeio", "Sem comissão por pedido. A mensalidade depende de quanto a loja vende no mês, e o plano inicial não tem mensalidade.") + passo("Feche com o próximo passo", "“Posso criar a sua agora, com você aqui? Leva uns quinze minutos.”") + '''</div>
  ''' + '</section>')

add('<section class="pg">' + cap("04", "Objeções e respostas", "As seis dúvidas mais comuns e a resposta curta que funciona.") + '''
  <table>
    <tr><th>O cliente diz</th><th>Responda</th></tr>
    <tr><td>“Já uso iFood / Anota Aí / outro app”</td><td>“Continue usando. Aqui o cliente pede direto de você, sem comissão. É a venda que o app não cobra.”</td></tr>
    <tr><td>“Não tenho tempo de montar cardápio”</td><td>“Montamos juntos. Mande o cardápio e as fotos que eu deixo pronto, e você só aprova.”</td></tr>
    <tr><td>“E se não funcionar para mim?”</td><td>“Você começa sem mensalidade e sem contrato longo. Se não ajudar, pausa a loja e pronto.”</td></tr>
    <tr><td>“Meu cliente não vai baixar app”</td><td>“Não precisa de app. Abre o link no celular, igual ao que você manda no WhatsApp hoje.”</td></tr>
    <tr><td>“Preciso de um site também”</td><td>“Dá para ter. O site de marca fica no seu domínio e leva o cliente para pedir na plataforma.”</td></tr>
    <tr><td>“É seguro? Meus dados ficam onde?”</td><td>“Login em duas etapas, cada loja só vê os próprios dados e o preço de cada pedido é conferido no servidor.”</td></tr>
  </table>
  <h3 class="sec">Proposta em uma tela</h3>
  ''' + msg("Modelo de proposta (WhatsApp)", "Combinado, [Nome]. Resumo do que montamos para a [Loja]:\n\n- Loja online com o seu cardápio, fotos e opcionais\n- Pedido organizado, com cartão em imagem para o WhatsApp\n- Painel para acompanhar e mudar o status\n- Link de rastreio para o seu cliente\n- Treinamento de 15 minutos\n\nMensalidade: começa em R$ 0 e só aumenta se a loja passar de R$ 3.000 em vendas no mês pela plataforma. Sem comissão por pedido.\n\nPosso criar agora com você? Preciso do nome da loja, do WhatsApp, do cardápio e das fotos.") + av("dica", "Quando o cliente some", "<p>Mande uma mensagem de acompanhamento em 24 horas (modelo no Anexo A) e outra em 3 dias. Depois disso, pare. Insistir demais queima a relação.</p>") + '</section>')

add('<section class="pg">' + cap("05", "Entrega da plataforma: visão geral", "A entrega é feita ao vivo, em videochamada, e leva de uma a duas horas. O cliente cria a própria conta: você nunca fica com a senha dele.") + fluxo(("Briefing", "coletar dados e fotos"), ("Conta e loja", "o cliente cria ao vivo"), ("Dados e cardápio", "horário, entrega, produtos"), ("Visual", "logo, capa e páginas"), ("Teste", "pedido real do começo ao fim"), ("Treino", "15 minutos"), esc=True) + '''
  <h3 class="sec">Cronograma sugerido</h3>
  ''' + tl(("Dia 0", "<b>Briefing.</b> Mande o formulário (Anexo D) e peça logo o cardápio com preços e as fotos dos pratos."), ("Dia 1", "<b>Montagem.</b> Videochamada de uma a duas horas: o cliente cria a conta e a loja, você cadastra categorias e produtos."), ("Dia 1", "<b>Teste e treino.</b> Pedido real pelo celular do cliente, treino de 15 minutos e entrega dos acessos."), ("Dia 2", "<b>Acompanhamento.</b> Mensagem perguntando como foi o primeiro dia, e ajuste do que apareceu."), ("Dia 7", "<b>Revisão.</b> Olhar os pedidos da semana, ajustar o cardápio e pedir um depoimento.")) + av("cuidado", "Senha e dados são do cliente", "<p>Nunca crie a conta com o seu e-mail para depois “transferir”. O cliente cria com o e-mail dele, define a senha dele e configura o autenticador no celular dele. Depois ele pode convidar o seu e-mail como <b>gerente</b> na aba <b>Equipe</b>, para você ajudar no suporte.</p>") + '''
  <h3 class="sec">O que você precisa na mão no início</h3>
  ''' + check("Nome da loja e tipo de negócio (padaria, cafeteria, hamburgueria, pizzaria, doceria, restaurante)", "WhatsApp que recebe os pedidos (55 + DDD + número)", "Endereço, horário e se faz entrega (taxa) ou só retirada", "Formas de pagamento aceitas", "Logo e foto de capa (se não tiver, a plataforma usa as iniciais e uma capa padrão)", "Cardápio com nome, descrição e preço, e uma foto por produto") + '</section>')

add('<section class="pg">' + cap("06", "Entrega: passo a passo", "Siga na ordem. Cada passo diz o que fazer e onde fica no sistema.") + '<div class="passos">' + passo("Cliente cria a conta", "Abra <code>bistroconnect.com.br/entrar.html</code> e peça para ele criar a conta com o e-mail dele. Senha com 10 caracteres ou mais. Ele confirma o e-mail pelo link que chega e volta à tela.", "Tela de cadastro. Se o e-mail não chegar, olhe Spam e Promoções.") + passo("Cliente cria a loja", "Nome da loja (o endereço <code>/l/nome-da-loja</code> aparece sozinho e mostra se está livre), tipo de negócio e WhatsApp. O tipo define o visual (tema) e as categorias iniciais.", "Tela “Criar a sua loja”.") + passo("Ligar o login em duas etapas", "No primeiro acesso ao painel, ele escaneia o código com o aplicativo autenticador e digita os seis números. Nunca peça print desse código.", "Painel › primeira entrada.") + '</div>' + cels(("vitrine-sacola", "A loja no ar, com a sacola"), ("carrinho", "Resumo do pedido"), ("dados", "Dados do cliente final")) + '</section>')

add('<section class="pg">' + '<div class="passos">' + passo("Dados da loja", "Preencha horário, se faz entrega, a taxa, o pedido mínimo, as formas de pagamento, o endereço e o Instagram. Envie a logo e a capa.", "Painel › Dados da loja.") + passo("Cardápio: categorias e produtos", "Crie as categorias na ordem em que o cliente vai ver. Em cada produto: nome, descrição curta, preço e foto. Para começar rápido, use o botão <b>Usar cardápio de exemplo com fotos</b> e depois troque o que for diferente.", "Painel › Produtos e categorias.") + passo("Opcionais por produto", "Para hambúrguer, pizza ou café: ponto da carne, adicionais, tamanho. Cada grupo tem mínimo e máximo de escolhas, e o preço extra de cada item.", "Painel › Produtos › editar › Opcionais.") + passo("Páginas do site", "Texto e foto da seção Sobre, até 8 fotos na Galeria e depoimentos reais com autorização do cliente. Sem preencher, a loja mostra seções padrão.", "Painel › Dados da loja › Páginas do site.") + '</div>' + av("dica", "Fotos que vendem", "<p>Fotos quadradas, com luz natural e fundo limpo. Uma foto por produto já muda o resultado. Evite foto de baixa resolução ou escura: o cartão do pedido também usa essas imagens.</p>") + '</section>')

add('<section class="pg">' + '<h3 class="sec">Teste real: o pedido de ponta a ponta</h3><p>Faça o teste com o cliente ainda na chamada. Se algum item falhar, corrija antes de entregar.</p>' + check("Abrir o link da loja no celular e conferir logo, capa e cardápio", "Escolher um produto com opcional e conferir o preço na sacola", "Fechar um pedido de retirada e outro de entrega, com telefone e endereço", "Tocar em <b>Enviar no WhatsApp</b> e confirmar que a imagem do cartão chega", "Conferir o pedido no painel, com som e aviso de pedido novo", "Mudar o status até “Entregue” e ver o link de rastreio acompanhar", "Abrir o link de rastreio no celular, em uma aba anônima", "Pausar a loja e ver que o cardápio avisa que os pedidos estão pausados", "Reabrir a loja e apagar os pedidos de teste, se o cliente preferir") + tela2(("cartao-padaria", "O cartão do pedido, gerado na hora"), ("rast-burger", "O rastreio no tema escuro da hamburgueria")) + '<div class="passos">' + passo("Entregue os acessos", "Mande ao cliente: o link da loja, o QR code para imprimir, o endereço do painel (<code>bistroconnect.com.br/painel/</code>) e um lembrete de guardar a senha em um gerenciador. Peça para ele convidar o seu e-mail como gerente em <b>Equipe</b>.", "Painel › Equipe › Convidar.") + passo("Treino de 15 minutos", "Ensine só o que ele vai usar todo dia: receber o pedido, mudar o status, compartilhar o cartão, pausar a loja e mudar um preço. Deixe o resto para depois.", "Veja o roteiro no capítulo 07.") + '</div></section>')

add('<section class="pg">' + cap("07", "O dia a dia da loja", "É isto que o cliente faz depois que você entrega. Use este capítulo como roteiro do treino.") + '''
  <h3 class="sec">Receber e acompanhar pedidos</h3>
  <p>Cada pedido novo toca um som e aparece em <b>Novos</b>. O dono confirma, prepara e marca a saída com um toque. A cada mudança, o link de rastreio do cliente se atualiza sozinho.</p>
  ''' + tela("painel-quadro", "Quadro: pedidos por etapa, com a esteira de andamento em cada um") + tela2(("painel-lista", "Lista: uma linha por pedido"), ("painel-grade", "Grade: cartões lado a lado"), cls="p") + '''
  <h3 class="sec">Outras rotinas</h3>
  <table>
    <tr><th>Quando</th><th>O que o dono faz</th><th>Onde</th></tr>
    <tr><td>Fechar para almoço ou imprevisto</td><td>Pausa a loja. O cardápio continua visível, mas avisa que os pedidos estão pausados.</td><td>Menu lateral › botão da loja</td></tr>
    <tr><td>Mudou preço ou acabou um item</td><td>Edita o preço ou desativa o produto.</td><td>Produtos e categorias</td></tr>
    <tr><td>Quer saber quanto vendeu</td><td>Olha a Visão geral e o Financeiro, por período.</td><td>Início e Financeiro</td></tr>
    <tr><td>Quer chamar clientes de volta</td><td>Abre a lista de Clientes e manda mensagem no WhatsApp.</td><td>Clientes</td></tr>
    <tr><td>Contrata alguém</td><td>Convida o e-mail da pessoa e escolhe a função: gerente, atendente ou cozinha.</td><td>Equipe</td></tr>
    <tr><td>Prefere tela escura</td><td>Escolhe Claro ou Escuro no topo do painel.</td><td>Topo do painel</td></tr>
  </table>
  ''' + av("ok", "A regra do status", "<p>Peça ao cliente para <b>sempre mudar o status</b>, mesmo nos dias corridos. É isso que mantém o cliente final tranquilo no rastreio e reduz as mensagens perguntando “cadê meu pedido?”.</p>") + '</section>')

add('<section class="pg">' + cap("08", "Pós-venda: dia 1, 7 e 30", "A plataforma só dá resultado se o dono usar. O pós-venda é o que faz ele usar.") + tl(("Dia 1", "<b>Como foi o primeiro dia?</b> Pergunte se chegou pedido, se teve dúvida e ajuste o que apareceu. Peça um print do painel."), ("Dia 7", "<b>Revisão da semana.</b> Veja quantos pedidos entraram, quais produtos vendem mais e o que falta no cardápio. Peça um depoimento curto."), ("Dia 30", "<b>Balanço do mês.</b> Mostre o total vendido, o plano em que a loja está e o que dá para melhorar. Peça indicação de outro dono de loja."), ("Todo mês", "<b>Aviso de faixa.</b> Se a loja está perto do teto da faixa de vendas, avise antes: a mensalidade só muda quando o mês fecha acima do limite.")) + '''
  <h3 class="sec">Oportunidades que nascem do pós-venda</h3>
  <div class="dois">
    <div class="card"><span class="tag">Venda adicional</span><h4>Site de marca</h4><p>Quando a loja já vende bem, ofereça o site no domínio dela, com a história e as fotos. É a continuação natural.</p></div>
    <div class="card"><span class="tag">Indicação</span><h4>Outro dono de loja</h4><p>Quem está satisfeito conhece outros donos. Peça com naturalidade, no balanço do mês.</p></div>
  </div>
  ''' + msg("Mensagem do dia 1", "Oi, [Nome]! Passando para saber como foi o primeiro dia da loja online. Chegou algum pedido? Se tiver qualquer dúvida no painel, me chama aqui que resolvo na hora.") + msg("Mensagem do dia 30", "Oi, [Nome]! Fechamos o primeiro mês. A loja recebeu [N] pedidos e vendeu R$ [valor]. Quer revisar o cardápio juntos e ver o que pode vender mais no próximo mês? E se você conhece outro dono de loja que precisa organizar os pedidos, me apresenta?") + '</section>')

# ================================================================ PARTE 3
add(parte("Parte 3", "Sites", "Quando o cliente quer marca própria, domínio e mais controle: como propor, montar e entregar.", [("09", "Proposta e escopo"), ("10", "Site de marca: entrega"), ("11", "Site completo com banco próprio"), ("12", "Aceite e termo de entrega")]))

add('<section class="pg">' + cap("09", "Site de marca: proposta e escopo", "O site é uma venda de projeto. Combine escopo, prazo e valor por escrito antes de começar.") + '''
  <h3 class="sec">O que entra no site de marca</h3>
  <div class="dois">
    <div class="card"><span class="tag">Incluso</span><h4>Escopo padrão</h4>''' + check("Página inicial com identidade da loja", "Seções: história, cardápio em destaque, galeria e contato", "Botão “Pedir agora” levando à loja na plataforma", "Domínio do cliente com HTTPS", "Ajuste de cores, textos e fotos enviados pelo cliente", "Uma rodada de revisão após a primeira versão") + '''</div>
    <div class="card"><span class="tag">À parte</span><h4>O que cobrar como extra</h4>''' + check("Fotografia dos pratos e do espaço", "Redação de textos longos", "Páginas além do escopo padrão", "Integrações com outros sistemas", "Rodadas extras de revisão", "Registro do domínio, pago pelo cliente", "Fotos, textos e depoimentos: só com direito de uso e autorização de quem falou") + '''</div>
  </div>
  <h3 class="sec">Formato da proposta</h3>
  <table class="form">
    <tr><td>Cliente e CNPJ ou CPF</td><td></td></tr>
    <tr><td>Produto contratado</td><td></td></tr>
    <tr><td>Prazo de entrega e data de início</td><td></td></tr>
    <tr><td>Valor de implantação (R$)</td><td></td></tr>
    <tr><td>Mensalidade de manutenção (R$)</td><td></td></tr>
    <tr><td>Forma de pagamento</td><td></td></tr>
    <tr><td>Número de revisões incluídas</td><td></td></tr>
  </table>
  ''' + av("dica", "Como precificar sem chutar", "<p>Some as horas que você gasta em cada etapa e multiplique pelo valor da sua hora. Some o custo dos domínios e do banco, se houver. Cobre a implantação em duas parcelas: metade ao fechar, metade na entrega. A manutenção mensal cobre pequenas mudanças, backup e suporte.</p>") + '</section>')

add('<section class="pg">' + cap("10", "Site de marca: entrega passo a passo", "O site fica no domínio do cliente e leva os pedidos para a loja dele na plataforma.") + fluxo(("Briefing", "marca, textos e fotos"), ("Loja", "monta na plataforma (Parte 2)"), ("Domínio", "no nome do cliente"), ("Site", "monta e publica"), ("Teste", "do site ao pedido"), ("Aceite", "termo de entrega"), esc=True) + '<div class="passos">' + passo("Briefing e materiais", "Peça o formulário (Anexo D) preenchido, a logo, as cores da marca, as fotos e os textos da história. Combine o que entra e o que não entra.", "Anexo D.") + passo("Monte a loja na plataforma", "Faça os passos do capítulo 06: conta, loja, dados, cardápio e páginas. É a loja que recebe os pedidos.", "Capítulo 06.") + passo("Domínio no nome do cliente", "O cliente registra o domínio no Registro.br (cerca de R$ 40 por ano) usando o CPF ou CNPJ dele. Você nunca deve registrar no seu nome: o domínio é patrimônio da loja.", "registro.br.") + passo("Aponte o domínio para a hospedagem", "Na Hostinger, adicione o domínio ao plano. No Registro.br, troque os servidores DNS pelos que a Hostinger informa. Pode levar até algumas horas para propagar.", "hPanel › Domínios.") + passo("Monte, publique e teste", "Ajuste textos, cores e fotos. No botão “Pedir agora”, use o link da loja (<code>bistroconnect.com.br/l/nome-da-loja</code>). Envie o zip, extraia na pasta do domínio, ative o SSL e faça um pedido até o fim.", "Gerenciador de Arquivos › Upload › Extrair; hPanel › SSL.") + '</div>' + av("cuidado", "Hoje isto exige um ajuste", "<p>Os sites prontos (Âmbar, Bruto e Padaria) usam pedido próprio. Para ligá-los à plataforma, troque o botão de pedido pelo link da loja: cerca de uma hora por site.</p>") + '</section>')

add('<section class="pg">' + cap("11", "Site completo com banco próprio", "É o modelo dos sites Âmbar, Bruto Burger e Padaria &amp; Café: cada cliente tem o seu painel e o seu Supabase. Use quando o cliente exigir dados separados.") + '''
  <h3 class="sec">Quando faz sentido</h3>
  <p>Rede com várias unidades, cliente que exige dados isolados por contrato, ou recursos que só existem naquele site. Para todos os outros casos, a plataforma é mais barata para você e mais completa para o cliente.</p>
  <h3 class="sec">Ordem dos arquivos de banco por tipo de site</h3>
  <table>
    <tr><th>Site</th><th>Rode no SQL Editor do Supabase, nesta ordem</th></tr>
    <tr><td><b>Hamburgueria</b><br><small>pedidos + rastreio</small></td><td><code>01-admins</code> › <code>05-loja-tabelas</code> › <code>03-loja-pedidos</code> › <code>seed-hamburgueria</code></td></tr>
    <tr><td><b>Âmbar</b><br><small>reservas pelo WhatsApp</small></td><td><code>01-admins</code> › <code>05-loja-tabelas</code> › <code>03-loja-pedidos</code> › <code>seed-ambar</code></td></tr>
    <tr><td><b>Padaria &amp; Café</b><br><small>encomendas + rastreio</small></td><td><code>01-admins</code> › <code>06-padaria</code> › <code>seed-padaria</code></td></tr>
  </table>
  <div class="passos">''' + passo("Crie o projeto do cliente no Supabase", "Novo projeto, região São Paulo, senha forte. Anote o endereço (Project URL) e a chave <b>anon public</b>. Nunca use ou mostre a chave <b>service_role</b>.", "supabase.com › New project.") + passo("Rode os arquivos SQL na ordem da tabela", "Cole cada arquivo no SQL Editor e toque em Run. Pode rodar mais de uma vez sem estragar.", "SQL Editor.") + passo("Crie o administrador", "Em Authentication › Users, crie o usuário com o e-mail do dono. Depois rode o comando que está no final do arquivo <code>01-admins</code>, trocando o e-mail. Ligue “Confirm email” e configure o <b>Site URL</b> com o endereço do site.", "Authentication › Users e URL Configuration.") + passo("Preencha o <code>assets/config.js</code> do site", "<code>nome</code>, <code>whatsapp</code>, <code>supabaseUrl</code>, <code>supabaseKey</code> e <code>cor</code>. Este arquivo é público: só a chave anon vai nele.", "Pasta assets do site.") + passo("Troque os dados de exemplo", "Endereço, telefone, depoimentos, cardápio e fotos. Nunca entregue o site com dados da demonstração.", "Arquivos do site e painel em <code>/admin/</code>.") + passo("Publique e teste", "Envie o zip, extraia na pasta do domínio, entre no painel, ligue o login em duas etapas e faça um pedido completo.", "Gerenciador de Arquivos.") + '''</div>
  ''' + av("cuidado", "Projeto gratuito do Supabase pausa", "<p>Projetos gratuitos pausam depois de cerca de uma semana sem uso. Para cliente pagante, use o plano Pro do Supabase ou combine um acesso de manutenção. Sem isso, o site pode ficar fora do ar sem aviso.</p>") + av("dica", "Novidades do produto", "<p>Os recursos novos (cartão do pedido em imagem, rastreio no novo modelo e painel atual) existem na plataforma. No site independente eles precisam ser aplicados à parte. Combine isso com o cliente na proposta.</p>") + '</section>')

add('<section class="pg">' + cap("12", "Aceite e termo de entrega", "A entrega só termina quando o cliente confirma por escrito. Isso protege os dois lados.") + '''
  <h3 class="sec">Checklist de aceite</h3>
  ''' + check("O site ou a loja abre no celular e no computador", "O endereço está certo e o HTTPS está ativo", "WhatsApp, endereço e horário conferidos", "Cardápio com preços e fotos aprovados pelo cliente", "Pedido de teste feito até o fim, com cartão e rastreio", "Painel aberto pelo próprio cliente, com login em duas etapas ligado", "Cliente sabe mudar o status, pausar a loja e editar um preço", "Cliente recebeu os acessos e sabe onde pedir ajuda", "Domínio registrado no nome do cliente", "Primeira cobrança combinada") + '''
  <h3 class="sec">Termo de aceite (modelo)</h3>
  <p>Declaro que recebi o <b>[produto]</b> da loja <b>[nome]</b> funcionando, conforme combinado na proposta de <b>[data]</b>, e que fui treinado(a) para usar o painel. Os acessos foram entregues e a senha é de uso exclusivo do(a) responsável pela loja.</p>
  <table class="form"><tr><td>Data da entrega</td><td></td></tr><tr><td>Link da loja ou do site</td><td></td></tr><tr><td>Responsável pela loja</td><td></td></tr></table>
  <div class="assin"><div>Responsável pela loja</div><div>Bistrô Connect</div></div>
  </section>''')

# ================================================================ PARTE 4
add(parte("Parte 4", "Operação", "Depois da venda: como cobrar, dar suporte e proteger o cliente e você.", [("13", "Cobrança e contratos"), ("14", "Suporte: problemas e soluções"), ("15", "Segurança e LGPD")]))

add('<section class="pg">' + cap("13", "Cobrança e contratos", "Seja claro desde o começo sobre o que é cobrado e quando. A maioria dos problemas de cobrança nasce de combinado verbal.") + '''
  <h3 class="sec">Plano da plataforma (pela faixa de vendas)</h3>
  <table>
    <tr><th>Plano</th><th>Vendas da loja no mês</th><th>Mensalidade</th></tr>
    <tr><td><b>Começo</b></td><td>até R$ 3.000</td><td>R$ 0</td></tr>
    <tr><td><b>Crescendo</b></td><td>até R$ 10.000</td><td>R$ 49</td></tr>
    <tr><td><b>Forte</b></td><td>até R$ 30.000</td><td>R$ 99</td></tr>
    <tr><td><b>Sem limites</b></td><td>acima de R$ 30.000</td><td>R$ 199</td></tr>
  </table>
  <p>Todos os planos têm todos os recursos. Não há comissão por pedido. O plano do mês é o da faixa de vendas daquele mês, e o painel da loja mostra o quanto falta para mudar de faixa. A tabela de preços está na tabela <code>planos</code> do Supabase da plataforma.</p>
  <h3 class="sec">Como cobrar hoje</h3>
  <div class="dois">
    <div class="card"><span class="tag">Plataforma</span><h4>Mensalidade</h4><p>No fechamento do mês, mande a cobrança por Pix ou link de pagamento. Combine o dia do vencimento no início e envie lembrete um dia antes.</p></div>
    <div class="card"><span class="tag">Sites</span><h4>Implantação e manutenção</h4><p>Implantação em duas parcelas (início e entrega). A manutenção mensal cobre pequenas mudanças, backup e suporte.</p></div>
  </div>
  ''' + av("cuidado", "Cobrança automática ainda não existe", "<p>A plataforma não cobra o cliente sozinha. Por enquanto a cobrança é manual. Quando tiver clientes suficientes, integre um meio de cobrança recorrente. Para nota fiscal e enquadramento, consulte o seu contador: este manual não dá orientação fiscal.</p>") + av("ok", "Contrato simples", "<p>Os <b>Termos de uso</b> e a <b>Política de privacidade</b> da plataforma já estão publicados. Para sites, use a proposta com o termo de aceite deste manual. Registre sempre por escrito: o valor, o prazo e o que está incluído.</p>") + '</section>')

add('<section class="pg">' + cap("14", "Suporte: problemas e soluções", "As dúvidas que mais aparecem e a resposta direta. Combine um prazo de resposta: um dia útil é razoável.") + '''
  <table>
    <tr><th>O problema</th><th>O que fazer</th></tr>
    <tr><td><b>E-mail de confirmação não chega</b></td><td>Peça para olhar Spam e Promoções. Se não estiver, no Supabase use Authentication › Users › enviar confirmação de novo.</td></tr>
    <tr><td><b>Esqueci a senha</b></td><td>Supabase › Authentication › Users › usuário › enviar recuperação de senha. Exige o Site URL configurado.</td></tr>
    <tr><td><b>Autenticador mostra “localhost”</b></td><td>Renomear a conta no aplicativo e configurar o Site URL no Supabase.</td></tr>
    <tr><td><b>Pedido não aparece no painel</b></td><td>Atualizar a página e conferir o filtro de busca. Confirmar que o cliente concluiu o pedido (tela “Pedido recebido”).</td></tr>
    <tr><td><b>O link de rastreio não atualiza</b></td><td>Pedir atualização forçada (Ctrl+F5) e confirmar que o status foi mudado no painel. O rastreio consulta o banco a cada poucos segundos.</td></tr>
    <tr><td><b>O cartão do pedido não abre para compartilhar</b></td><td>No computador a imagem é baixada. No celular, abrir pelo Chrome ou Safari, não pelo navegador de dentro de outros aplicativos.</td></tr>
    <tr><td><b>Telefone do cliente com números faltando</b></td><td>Corrigido: o “+55” colado automaticamente é ignorado. Atualize a página da loja com Ctrl+F5.</td></tr>
    <tr><td><b>Foto do produto não aparece</b></td><td>Enviar de novo em JPG, PNG ou WebP, com menos de 5 MB. Atualizar o painel.</td></tr>
    <tr><td><b>Loja “não está recebendo pedidos”</b></td><td>A loja foi pausada. Reativar no botão do menu lateral.</td></tr>
    <tr><td><b>Mudei um arquivo e nada mudou</b></td><td>Cache do navegador. Atualizar com Ctrl+F5 e, se precisar, aumentar o número de versão do arquivo.</td></tr>
  </table>
  ''' + av("dica", "Quando subir arquivos na Hostinger", "<p>O Gerenciador de Arquivos não substitui arquivo existente: <b>apague o antigo e suba o novo</b>. Nunca apague a pasta <code>assets</code> inteira nem o <code>config.js</code> com as chaves. Se aparecer erro 409, é conflito com arquivo que já existe.</p>") + '</section>')

add('<section class="pg">' + cap("15", "Segurança e LGPD", "O que já protege o sistema, o que você precisa explicar ao cliente e como agir se algo der errado.") + '''
  <h3 class="sec">O que já protege o sistema</h3>
  ''' + check("Login em duas etapas nos painéis, com saída automática após 30 minutos parado", "Cada loja só enxerga os próprios dados: as regras ficam no banco de dados, não no navegador", "O preço de cada pedido é recalculado no servidor, então mexer no navegador não adianta", "Limites contra robôs na criação de pedidos", "Conexão protegida (HTTPS) e proteção contra script injetado") + '''
  <h3 class="sec">O que explicar ao cliente</h3>
  <div class="dois">
    <div class="card"><span class="tag">Dado do cliente final</span><h4>Quem é o responsável</h4><p>Nome, telefone e endereço dos clientes da loja pertencem ao lojista. A plataforma guarda e protege, mas quem decide o uso é a loja. A Política de privacidade explica isso.</p></div>
    <div class="card"><span class="tag">Senha</span><h4>Cuidados do dono</h4><p>Senha longa e única, guardada em gerenciador. Nunca compartilhar a senha nem o código do autenticador. Quem trabalha na loja entra com o próprio e-mail, pela aba Equipe.</p></div>
  </div>
  <h3 class="sec">Se algo der errado</h3>
  <div class="passos">''' + passo("Suspeita de acesso indevido", "Troque a senha, saia de todas as sessões e remova da Equipe quem não deve mais ter acesso. Anote data e o que aconteceu.") + passo("Cliente pede para apagar dados", "Atenda por escrito, no prazo combinado com a loja. O pedido de um cliente final deve ser tratado com a loja, que é a responsável pelos dados dele.") + passo("Aviso ao cliente", "Se houver vazamento real, avise a loja imediatamente e registre o que foi feito. Um e-mail de suporte ativo e respondido é parte da proteção.") + '''</div>
  ''' + av("cuidado", "Regra inegociável", "<p>Nunca coloque no código, em mensagens ou em prints a chave <b>service_role</b> do Supabase nem o QR code do autenticador. Quem tem essas informações controla tudo.</p>") + '</section>')

# ================================================================ ANEXOS
add('<section class="pg">' + cap("A", "Anexo A · Mensagens prontas", "Doze modelos para copiar e colar no WhatsApp. Troque o que está entre colchetes e leia antes de enviar.") + msg("1 · Primeiro contato", "Oi, [Nome]! Vi que a [Loja] vende pelo Instagram e pelo WhatsApp. Ajudo lojas como a sua a receber os pedidos organizados, com cardápio online e sem pagar comissão por pedido. Posso te mostrar em 10 minutos?") + msg("2 · Quando perguntam o preço", "O plano inicial não tem mensalidade e só passa a cobrar se a loja vender mais de R$ 3.000 por mês pela plataforma. Sem comissão por pedido. Quer ver funcionando no celular antes?") + msg("3 · Convite para demonstração", "Fechado! Te chamo em vídeo amanhã às [horário] e mostro a loja de exemplo e o painel. Leva dez minutos. Se gostar, já criamos a sua na mesma chamada.") + msg("4 · Acompanhamento em 24 horas", "Oi, [Nome]! Tudo bem? Conseguiu ver a demonstração? Se quiser, crio a sua loja agora com você. Só preciso do nome da loja, do WhatsApp, do cardápio e das fotos.") + msg("5 · Proposta da plataforma", "Resumo para a [Loja]: loja online com cardápio e fotos, pedido organizado com cartão em imagem, painel para acompanhar, rastreio para o cliente e treino de 15 minutos. Mensalidade começa em R$ 0. Combinado?") + msg("6 · Proposta do site", "Para a [Loja] proponho um site no domínio [dominio] com a sua história, galeria e botão “Pedir agora” levando para a loja online. Implantação de R$ [valor], em duas parcelas, prazo de [N] dias úteis após receber textos e fotos.") + '</section>')

add('<section class="pg">' + msg("7 · Pedido de briefing", "Para começar, preciso de:\n1. Nome da loja e tipo (padaria, café, hamburgueria...)\n2. WhatsApp que recebe os pedidos\n3. Endereço, horário e taxa de entrega\n4. Cardápio com nome, descrição e preço\n5. Uma foto de cada produto, logo e capa\nPode mandar por aqui mesmo.") + msg("8 · Cardápio pronto para aprovação", "Oi, [Nome]! O cardápio da [Loja] está montado. Abre aqui para conferir os preços e as fotos: [link]. Me diz o que ajustar e eu corrijo hoje.") + msg("9 · Loja no ar", "Sua loja está no ar! Link para divulgar: [link]. Coloque na bio do Instagram, nos status e nos grupos do WhatsApp. Vou te mandar também o QR code para imprimir e colocar no balcão.") + msg("10 · Dia 1", "Oi, [Nome]! Como foi o primeiro dia da loja online? Chegou pedido? Qualquer dúvida no painel, me chama.") + msg("11 · Dia 7 e depoimento", "Oi, [Nome]! A semana foi boa: [N] pedidos pelo site. Você toparia gravar uma frase curta contando como foi usar a loja? Pode ser por texto mesmo.") + msg("12 · Dia 30 e indicação", "Oi, [Nome]! Fechamos o mês: [N] pedidos e R$ [valor] vendidos. Você conhece algum dono de loja que também precisa organizar os pedidos? Se me apresentar, faço o primeiro mês de acompanhamento dele sem custo.") + av("dica", "Sobre o tom", "<p>Escreva como falaria pessoalmente: curto, direto e sem exagero. Evite emojis nos modelos: alguns celulares mostram um símbolo quebrado no lugar.</p>") + '</section>')

add('<section class="pg">' + cap("B", "Anexo B · Lista de entrega da plataforma", "Imprima uma por cliente. Marque cada item na hora e guarde a folha assinada.") + '<table class="form"><tr><td>Cliente / loja</td><td></td></tr><tr><td>Data da entrega</td><td></td></tr><tr><td>Link da loja</td><td></td></tr></table>' + '''
  <div class="grid2">
    <div class="card"><span class="tag">Antes</span><h4>Preparação</h4>''' + check("Briefing recebido", "Logo e capa recebidas", "Cardápio e fotos recebidos", "Videochamada marcada") + '''</div>
    <div class="card"><span class="tag">Montagem</span><h4>Na videochamada</h4>''' + check("Conta criada pelo cliente", "Autenticador ligado no celular dele", "Dados da loja preenchidos", "Cardápio cadastrado com fotos e opcionais", "Páginas do site preenchidas") + '''</div>
    <div class="card"><span class="tag">Teste</span><h4>Pedido real</h4>''' + check("Retirada e entrega testadas", "Cartão chegou no WhatsApp", "Status mudado até Entregue", "Rastreio acompanhou", "Loja pausada e reaberta") + '''</div>
    <div class="card"><span class="tag">Entrega</span><h4>Fechamento</h4>''' + check("Link e QR code enviados", "Seu e-mail convidado como gerente", "Treino de 15 minutos feito", "Cobrança combinada", "Aviso do dia 1 agendado") + '''</div>
  </div>
  <div class="assin"><div>Responsável pela loja</div><div>Bistrô Connect</div></div>
  </section>''')

add('<section class="pg">' + cap("C", "Anexo C · Lista de entrega do site", "Para site de marca e para site completo. Marque o que se aplica.") + '<table class="form"><tr><td>Cliente / loja</td><td></td></tr><tr><td>Endereço do site</td><td></td></tr><tr><td>Tipo (marca ou independente)</td><td></td></tr></table>' + '''
  <div class="grid2">
    <div class="card"><span class="tag">Antes</span><h4>Contratação</h4>''' + check("Proposta aceita por escrito", "Primeira parcela recebida", "Briefing, textos e fotos recebidos", "Domínio registrado no nome do cliente") + '''</div>
    <div class="card"><span class="tag">Montagem</span><h4>Site</h4>''' + check("Textos, cores e fotos aplicados", "Botão “Pedir agora” com o link certo", "WhatsApp, endereço e horário conferidos", "Dados de exemplo trocados") + '''</div>
    <div class="card"><span class="tag">Técnico</span><h4>Publicação</h4>''' + check("Domínio apontado para a hospedagem", "HTTPS ativo", "Se independente: Supabase criado e SQL rodado na ordem", "Se independente: <code>config.js</code> preenchido e admin criado") + '''</div>
    <div class="card"><span class="tag">Fechamento</span><h4>Aceite</h4>''' + check("Teste do site ao pedido", "Termo de aceite assinado", "Segunda parcela recebida", "Acessos entregues", "Plano de manutenção combinado") + '''</div>
  </div>
  <div class="assin"><div>Responsável pela loja</div><div>Bistrô Connect</div></div>
  </section>''')

add('<section class="pg">' + cap("D", "Anexo D · Briefing do cliente", "Mande este formulário logo depois do “sim”. Quanto mais completo, menos retrabalho.") + '''
  <table class="form">
    <tr><td>Nome da loja</td><td></td></tr><tr><td>Tipo de negócio</td><td></td></tr><tr><td>Responsável e e-mail</td><td></td></tr>
    <tr><td>WhatsApp que recebe os pedidos</td><td></td></tr><tr><td>Endereço completo</td><td></td></tr><tr><td>Horário de funcionamento</td><td></td></tr>
    <tr><td>Faz entrega? Taxa e pedido mínimo</td><td></td></tr><tr><td>Formas de pagamento</td><td></td></tr><tr><td>Instagram</td><td></td></tr>
    <tr><td>Cores da marca (se tiver)</td><td></td></tr><tr><td>Logo e foto de capa enviadas?</td><td></td></tr><tr><td>Cardápio com preços enviado?</td><td></td></tr>
    <tr><td>Fotos dos produtos enviadas?</td><td></td></tr><tr><td>Produtos com opcionais (adicionais, tamanhos)</td><td></td></tr>
    <tr><td>História da loja em poucas linhas</td><td></td></tr><tr><td>Para site: domínio desejado</td><td></td></tr>
  </table>
  ''' + av("dica", "Sobre as fotos", "<p>Peça fotos originais, não as do Instagram (que perdem qualidade). Se o cliente não tiver, use a plataforma com o cardápio de exemplo e combine a troca depois.</p>") + '</section>')

add('<section class="pg">' + cap("E", "Anexo E · Referência rápida", "Endereços, arquivos e comandos que você usa sempre.") + '''
  <table>
    <tr><th>O que</th><th>Endereço ou nome</th></tr>
    <tr><td>Loja de um cliente</td><td><code>bistroconnect.com.br/l/nome-da-loja</code></td></tr>
    <tr><td>Cadastro e entrada</td><td><code>bistroconnect.com.br/entrar.html</code></td></tr>
    <tr><td>Painel da loja</td><td><code>bistroconnect.com.br/painel/</code></td></tr>
    <tr><td>Painel da plataforma (todas as lojas)</td><td><code>bistroconnect.com.br/admin/</code></td></tr>
    <tr><td>Painel de leads (CRM)</td><td><code>bistroconnect.com.br/crm/</code></td></tr>
    <tr><td>Rastreio de um pedido</td><td><code>bistroconnect.com.br/p/código-de-16-caracteres</code></td></tr>
    <tr><td>Configuração pública do site</td><td><code>assets/config.js</code> (só a chave anon)</td></tr>
    <tr><td>Arquivos de banco da plataforma</td><td><code>01-plataforma</code> até <code>08-rastreio-completo</code>, pasta <code>plataforma/supabase</code></td></tr>
    <tr><td>Repositório do código</td><td><code>customersucess26-cell/Command-AI</code></td></tr>
  </table>
  <h3 class="sec">Regras que nunca mudam</h3>
  ''' + check("Só a chave <b>anon</b> vai no <code>config.js</code>. A <b>service_role</b> nunca sai do Supabase", "O cliente cria a conta com o e-mail dele e guarda a senha dele", "Domínio no nome do cliente, sempre", "Apague o arquivo antigo antes de subir o novo na Hostinger", "Teste um pedido real antes de entregar", "Registre valor, prazo e escopo por escrito") + '</section>')

html = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Manual de Venda e Entrega · Bistrô Connect</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&family=DM+Mono:wght@400;500&display=swap">
<style>{css}</style>
</head>
<body>
{chr(10).join(P)}
</body>
</html>'''
open("manual/manual-venda-e-entrega.html", "w", encoding="utf-8").write(html)
print("manual/manual-venda-e-entrega.html gerado:", len(html) // 1024, "KB,", len(P), "seções")
