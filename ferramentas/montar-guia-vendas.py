"""Gera manual/guia-de-vendas.html a partir do CSS do manual e dos prints em manual/guia-img/. O PDF sai abrindo o HTML no Chrome e imprimindo (A4, com fundo).
Uso:  python3 ferramentas/montar-guia-vendas.py"""
import re

base = open("manual/manual.html", encoding="utf-8").read()
css = re.search(r"<style>(.*?)</style>", base, re.S).group(1)
css += """
/* prints */
.fig{margin:0;break-inside:avoid}
.fig img{width:100%;display:block;border-radius:10px;border:1px solid var(--linha);box-shadow:0 8px 20px -12px rgba(14,21,38,.5)}
.fig figcaption{font-size:8.5pt;color:var(--suave);text-align:center;margin-top:5px;line-height:1.3}
.fones{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:10px 0 14px;break-inside:avoid}
.fones.q4{grid-template-columns:repeat(4,1fr);gap:8px}
.fones.q2{grid-template-columns:repeat(2,1fr);max-width:118mm;margin-inline:auto}
.tela{margin:10px 0 14px;break-inside:avoid}
.duas{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0 14px;break-inside:avoid}
.passo .ond{display:block;margin-top:5px;font-size:9.5pt;color:var(--suave)}
.passo .ond b{color:var(--ouro);font-family:'Poppins';font-size:8pt;letter-spacing:.1em;text-transform:uppercase}
.msg{background:#F3F6FA;border-left:4px solid var(--azul);border-radius:0 10px 10px 0;padding:10px 14px;font-size:10pt;margin:8px 0 12px;break-inside:avoid;white-space:pre-line}
.msg b.t{display:block;font:600 8pt 'Poppins';letter-spacing:.12em;text-transform:uppercase;color:#0B5B9E;margin-bottom:3px}
h3.sec{font-size:12pt;margin:16px 0 6px;color:var(--navy);border-left:4px solid var(--ouro);padding-left:10px}
.num{font:700 20pt 'Poppins';color:var(--ouro)}
td small{color:var(--suave)}
"""


def fig(img, cap):
    return f'<figure class="fig"><img src="guia-img/{img}.jpg" alt="{cap}"><figcaption>{cap}</figcaption></figure>'


def fones(*itens, cls=""):
    return f'<div class="fones {cls}">' + "".join(fig(i, c) for i, c in itens) + "</div>"


def tela(img, cap):
    return f'<div class="tela">{fig(img, cap)}</div>'


def cap(n, titulo, intro):
    return f'<div class="cap"><div class="n">{n}</div><h2>{titulo}</h2></div><p class="intro">{intro}</p>'


def passo(titulo, texto, onde=""):
    o = f'<span class="ond"><b>Por trás</b> {onde}</span>' if onde else ""
    return f'<div class="passo"><div><b class="t">{titulo}</b><p>{texto}</p>{o}</div></div>'


def av(tipo, titulo, texto):
    ic = {"dica": "i", "cuidado": "!", "ok": "✓"}[tipo]
    return f'<div class="av {tipo}"><div class="i">{ic}</div><div><b class="t">{titulo}</b>{texto}</div></div>'


def check(*itens, feito=False):
    return f'<ul class="check{" feito" if feito else ""}">' + "".join(f"<li><span>{i}</span></li>" for i in itens) + "</ul>"


def msg(titulo, texto):
    return f'<div class="msg"><b class="t">{titulo}</b>{texto}</div>'


P = []  # páginas
add = P.append

add('''<section class="pg capa">
  <div class="topo">Documento interno · Vendas</div>
  <div class="meio">
    <img src="logo-clara.png" alt="Bistrô Connect">
    <h1>Guia da venda</h1>
    <div class="linha"></div>
    <p class="sub">Do anúncio ao primeiro pedido: como o cliente compra, como ele entra no produto, como você cobra e como testar tudo antes de vender.</p>
  </div>
  <div class="rod"><span>bistroconnect.com.br</span><span>Outubro de 2026</span></div>
</section>''')

add('''<section class="pg">
  <div class="cap"><div class="n">≡</div><h2>Sumário</h2></div>
  <p class="intro">Leia na ordem na primeira vez. Depois use como consulta.</p>
  <div class="sumario">
    <div><span>01</span><b>O que você vende</b></div>
    <div><span>02</span><b>A jornada do cliente, passo a passo</b></div>
    <div><span>03</span><b>Duas portas de entrada: sozinho ou com ajuda</b></div>
    <div><span>04</span><b>O que você enxerga (seus painéis)</b></div>
    <div><span>05</span><b>Como e quando cobrar</b></div>
    <div><span>06</span><b>Roteiro de teste antes de vender</b></div>
    <div><span>07</span><b>Respostas rápidas de suporte</b></div>
    <div><span>08</span><b>Hostinger sem Supabase? A resposta</b></div>
    <div><span>09</span><b>Lista final antes de abrir as vendas</b></div>
  </div>
  ''' + av("dica", "Como testar sem criar nada", "<p>Abra <code>bistroconnect.com.br/painel/</code> e toque em <b>Ver demonstração com dados fictícios</b>. Faça o mesmo em <code>/crm/</code>. Para testar de verdade, siga o capítulo 06.</p>") + '''
</section>''')

# ---------------- 01 ----------------
add('<section class="pg">' + cap("01", "O que você vende", "Dois produtos e um serviço. A ordem importa: o cliente entra pelo plano grátis, cresce com as vendas e só então paga.") + '''
  <table>
    <tr><th>O que é</th><th>Para quem</th><th>Quanto custa</th><th>Quem monta</th></tr>
    <tr><td><b>Loja na plataforma</b><br><small>cardápio online, pedido, rastreio e painel</small></td><td>Dono de padaria, café, hamburgueria, restaurante, pizzaria ou doceria que quer vender sem comissão</td><td>Grátis até R$ 3 mil de vendas no mês. Depois R$ 49, R$ 99 ou R$ 199 conforme as vendas do mês</td><td>O próprio dono, em cerca de 5 minutos</td></tr>
    <tr><td><b>Ajuda para montar</b><br><small>serviço</small></td><td>Quem não quer mexer em nada</td><td>Combinado com você. Sugestão: um valor único de implantação</td><td>Você, pelo WhatsApp e videochamada</td></tr>
    <tr><td><b>Site completo</b><br><small>Âmbar, Bruto Burger e Padaria &amp; Café</small></td><td>Quem quer site de marca, com domínio próprio, história e fotos</td><td>Sob orçamento</td><td>Você (implantação)</td></tr>
  </table>
  <h3 class="sec">Os planos da plataforma</h3>
  <table>
    <tr><th>Plano</th><th>Vendas da loja no mês, pela plataforma</th><th>Mensalidade</th></tr>
    <tr><td><b>Começo</b></td><td>até R$ 3.000</td><td>Grátis</td></tr>
    <tr><td><b>Crescendo</b></td><td>até R$ 10.000</td><td>R$ 49</td></tr>
    <tr><td><b>Forte</b></td><td>até R$ 30.000</td><td>R$ 99</td></tr>
    <tr><td><b>Sem limites</b></td><td>acima de R$ 30.000</td><td>R$ 199</td></tr>
  </table>
  <p>Todos os planos têm todos os recursos. Não existe comissão por pedido nem taxa de implantação na plataforma. A mensalidade nunca passa de R$ 199.</p>
  ''' + av("ok", "Por que o grátis vende", "<p>Tira o risco da decisão. O dono testa com clientes reais, e a mensalidade só aparece quando a loja já está vendendo bem. Esse é o argumento central dos seus anúncios.</p>") + av("cuidado", "O que a plataforma não faz", "<p><b>Não recebe o dinheiro dos pedidos:</b> o cliente paga direto ao lojista (Pix, cartão na entrega ou dinheiro). <b>Não faz entrega.</b> <b>Ainda não cobra a mensalidade sozinha</b>: hoje você cobra, e o capítulo 05 mostra como.</p>") + '</section>')

# ---------------- 02 ----------------
add('<section class="pg">' + cap("02", "A jornada do cliente", "Do clique no anúncio ao primeiro pedido, leva menos de 15 minutos. Em cada passo: o que o cliente vê e o que acontece por trás.") + '<div class="passos">'
    + passo("O dono clica no anúncio", "Ele cai numa página de vendas que fala do negócio dele (padaria, café, hamburgueria...), com o link que você colocou no anúncio, por exemplo <code>?para=padaria</code>.", "O sistema guarda de onde ele veio (anúncio, campanha, palavra-chave) por 90 dias. Meta e Google só medem depois do aceite dos cookies.")
    + passo("Cria a conta", "Nome, e-mail e senha de 10 caracteres ou mais, com medidor de força. Aceita os Termos de uso e a Política de privacidade.")
    + passo("Confirma o e-mail", "Recebe um e-mail, toca no link e volta para a tela de cadastro, já dentro da conta.", "Se o e-mail não chegar, veja spam e promoções. O capítulo 07 explica como destravar pelo Supabase.")
    + '</div>' + fones(("01-anuncio", "1. Página do anúncio"), ("02-criar-conta", "2. Criar conta"), ("03-confirme-email", "3. Confirmar e-mail"))
    + '<div class="passos">'
    + passo("Cria a loja", "Dá um nome (o endereço <code>/l/nome-da-loja</code> aparece sozinho e mostra se está livre), escolhe o <b>tipo de negócio</b> e informa o WhatsApp. O tipo define o visual (tema) e as categorias iniciais.")
    + passo("A loja está no ar", "Ele recebe o link, com botão para copiar, e a lista dos próximos passos. A vitrine já abre, mesmo vazia.")
    + '</div>' + fones(("04-criar-loja", "4. Criar a loja"), ("05-loja-no-ar", "5. Loja no ar"), ("10-vitrine", "A vitrine que o cliente final vê"))
    + '</section>')

add('<section class="pg"><div class="passos">'
    + passo("Entra no painel e ativa o login em 2 etapas", "Abre <code>/painel/</code> com o mesmo e-mail e senha. No primeiro acesso, lê um QR code com um aplicativo autenticador (Google Authenticator, Authy) e digita o código de 6 números. É obrigatório e protege a loja.", "O banco só deixa dono e gerente mudarem cardápio e dados da loja com a 2ª etapa feita.")
    + '</div>' + tela("06-painel-login", "Entrada do painel do lojista")
    + '<div class="passos">'
    + passo("Segue o guia “Primeiros passos”", "Enviar o logo, cadastrar 3 produtos, colocar fotos, definir horário e entrega, divulgar o link. Quem não tem produtos pode tocar em <b>Usar exemplo com fotos</b>: a loja ganha de 12 a 19 produtos do tipo dela, com preço, descrição e foto, e o dono só troca pelos dele.")
    + '</div>' + tela("07-painel-primeiros-passos", "Início do painel, com o guia Primeiros passos") + tela("08-painel-cardapio", "Cardápio depois de “Usar exemplo com fotos”") + '</section>')

add('<section class="pg"><div class="passos">'
    + passo("Divulga o link", "Na tela inicial ele copia o link da loja ou divulga direto no WhatsApp. O link vai para a bio do Instagram, o perfil do Google e o status do WhatsApp.", "O guia Primeiros passos marca esse item como feito quando ele copia o link.")
    + '</div>' + tela("09-painel-inicio", "Início: link da loja, plano do mês e números do dia")
    + '<div class="passos">'
    + passo("O cliente final faz o pedido", "Abre o link no celular, escolhe os itens, informa nome e WhatsApp, entrega ou retirada, endereço e forma de pagamento, e toca em <b>Enviar pedido</b>.", "O preço é recalculado no servidor (taxa, pedido mínimo, formas de pagamento da loja), então ninguém altera valor pelo navegador. Há proteção contra robôs e contra clique duplo.")
    + '</div>' + fones(("10-vitrine", "Vitrine"), ("12-pedido-carrinho", "Sacola"), ("13-pedido-dados", "Dados"), ("14-pedido-recebido", "Pedido recebido"), cls="q4")
    + av("dica", "Confira a promessa antes de anunciar", "<p><b>O pedido sempre fica salvo no painel do lojista</b>, com alerta sonoro e notificação, mesmo que o cliente não envie nada. Em seguida o celular dele abre o WhatsApp com o resumo pronto, mas <b>é o cliente quem toca em enviar</b>. Por isso, nos anúncios, prefira “pedido organizado no painel e no WhatsApp” a “o pedido sempre chega no seu WhatsApp”.</p>")
    + '</section>')

add('<section class="pg"><div class="passos">'
    + passo("O lojista recebe e atende", "O pedido aparece em <b>Pedidos</b>, na coluna Novos, com som e aviso. Ele toca em <b>Confirmar</b> e vai avançando: Em preparo, Pronto ou saiu para entrega, Entregue. O botão verde abre o WhatsApp do cliente com a mensagem de cada etapa e o link de acompanhamento.", "Cada mudança de status fica registrada com quem fez. A equipe não consegue alterar itens nem valores de um pedido.")
    + '</div>' + tela("15-painel-pedidos", "Pedidos do lojista") + tela("15b-painel-pedido-aberto", "Detalhe do pedido, com itens, pagamento e histórico")
    + '</section>')

add('<section class="pg"><div class="passos">'
    + passo("O cliente acompanha pelo celular", "Ele abre o link de rastreio e vê as etapas: recebido, confirmado, em preparo, saiu para entrega, entregue. A página atualiza sozinha.", "O link usa um código secreto de 64 caracteres e não mostra telefone nem endereço do cliente.")
    + passo("A mensalidade acompanha as vendas", "No começo do mês seguinte, o plano da loja é definido pelo que ela vendeu pela plataforma (pedidos não cancelados). Em até R$ 3 mil é grátis. O dono vê no painel, em <b>Plano do mês</b>, quanto já vendeu e quanto falta para mudar de faixa.", "Cobrança: capítulo 05.")
    + '</div>' + fones(("16-rastreio", "Rastreio do pedido"), ("11-vitrine-sacola", "Barra “Ver pedido”"), cls="q2") + '</section>')

# ---------------- 03 ----------------
add('<section class="pg">' + cap("03", "Duas portas de entrada", "O lead pode fazer sozinho ou pedir ajuda. As duas chegam ao mesmo produto.") + '''
  <table>
    <tr><th></th><th>Porta A · Sozinho</th><th>Porta B · “Quero ajuda para montar”</th></tr>
    <tr><td><b>Onde começa</b></td><td>Botão “Criar minha loja grátis”</td><td>Formulário da página de vendas, ou o assistente Bia</td></tr>
    <tr><td><b>O que acontece</b></td><td>Cria conta e loja em minutos, sem falar com ninguém</td><td>O lead cai no seu painel <code>/crm/</code>, com a origem do anúncio, e o WhatsApp abre com os dados dele</td></tr>
    <tr><td><b>Quem faz</b></td><td>O dono</td><td>O dono, com você guiando</td></tr>
    <tr><td><b>Custo</b></td><td>Grátis até R$ 3 mil de vendas</td><td>Igual, mais a ajuda, se você cobrar implantação</td></tr>
  </table>
  <h3 class="sec">Como atender a Porta B, passo a passo</h3>
  <div class="passos">''' + passo("Responda rápido", "O lead chega no <code>/crm/</code> e no seu WhatsApp. Responder em poucos minutos, em horário comercial, faz muita diferença na conversão.")
    + passo("Proponha 20 minutos de videochamada", "O dono cria a conta na frente de você, escolhe o tipo, usa “Exemplo com fotos” e troca os primeiros produtos.")
    + passo("Se precisar mexer por ele, use o convite de gerente", "No painel dele: <b>Equipe › Convidar pessoa</b>, com o seu e-mail e a função <b>Gerente</b>. Você aceita pelo link e entra na loja dele com a sua própria conta (que precisa ter o login em 2 etapas). Terminado, ele remove o seu acesso em Equipe.")
    + passo("Entregue o checklist do primeiro dia", "Logo, 3 produtos com foto, horário e taxa de entrega, divulgar o link no Instagram e no status do WhatsApp.")
    + '</div>' + msg("Mensagem pronta para o primeiro contato", "Oi, {nome}! Aqui é o Adilson, da Bistrô Connect. Vi seu pedido de ajuda para montar a loja da {estabelecimento}. Posso te chamar hoje às __h ou amanhã às __h? Em cerca de 20 minutos deixamos o seu cardápio no ar, com pedido pelo celular. Se preferir ir fazendo, é só entrar em bistroconnect.com.br/entrar.html que eu te acompanho por aqui.")
    + av("cuidado", "Nunca peça nem guarde a senha do cliente", "<p>Use sempre o convite de gerente. Hoje não existe criar a loja “em nome” do cliente nem transferir uma loja de uma conta para outra, por segurança.</p>") + '</section>')

# ---------------- 04 ----------------
add('<section class="pg">' + cap("04", "O que você enxerga", "Você tem três lugares para acompanhar o negócio.") + '''
  <table>
    <tr><th>Onde</th><th>Para quê</th></tr>
    <tr><td><code>/admin/</code></td><td><b>Suas lojas.</b> Todas as lojas, dono, data de criação, <b>origem (qual anúncio trouxe)</b>, pedidos e vendas do mês, plano, mensalidade e situação. Tem seletor de mês e botão Exportar (planilha).</td></tr>
    <tr><td><code>/crm/</code></td><td><b>Seus leads.</b> Pedidos de ajuda do formulário e da Bia, orçamentos, funil de vendas e metas.</td></tr>
    <tr><td>Supabase › Authentication › Users</td><td><b>Contas.</b> Quem se cadastrou, se confirmou o e-mail, e as ações de suporte (confirmar usuário, remover).</td></tr>
  </table>
  ''' + tela("17-admin-lojas", "Seu painel /admin/: lojas, origem, vendas e plano") + tela("18-crm-demo", "Seu painel /crm/ (aqui em demonstração)")
    + av("dica", "Como saber qual anúncio traz lojas", "<p>Na coluna <b>Origem</b> do <code>/admin/</code> aparece, por exemplo, <i>google / cpc / padaria-pg</i>. Cruze com o que você gastou em cada campanha e corte as que não trazem lojas.</p>") + '</section>')

# ---------------- 05 ----------------
add('<section class="pg">' + cap("05", "Como e quando cobrar", "Hoje a cobrança é manual e leva uns 10 minutos por mês. A automática (Asaas) é a próxima fase.") + '''
  <h3 class="sec">O calendário do mês</h3>
  <div class="passos">''' + passo("Dias 1 a 3: feche o mês anterior", "Em <code>/admin/</code>, escolha o <b>mês anterior</b> no seletor. A tela mostra a venda de cada loja e a mensalidade que cabe. Toque em <b>Exportar</b> para guardar a planilha.", "O seletor de mês exige rodar o arquivo <code>02-admin-por-mes.sql</code> uma vez no Supabase.")
    + passo("Cobre só quem tem mensalidade", "Lojas no plano Começo (mensalidade zero) não pagam nada. Para as demais, mande a cobrança por WhatsApp, com a sua chave Pix, vencendo no dia 10.")
    + passo("Dia 25: lembrete", "Para quem não pagou, um lembrete curto e simpático.")
    + passo("Mais de 15 dias de atraso: suspenda", "Em <code>/admin/</code>, mude a Situação da loja para <b>Suspensa</b>. A vitrine sai do ar e o cardápio fica oculto, mas nada é apagado. Quando pagar, volte para <b>Ativa</b>.")
    + '</div>' + msg("Mensagem de cobrança", "Oi, {nome}! A {loja} vendeu R$ {vendas} em {mês} pela Bistrô Connect, então a mensalidade do plano {plano} é R$ {valor}. Chave Pix: {sua chave}. Vencimento dia 10. Obrigado por vender com a gente!")
    + tela("17b-admin-mes", "Seletor de mês no /admin/: abrir o mês fechado para cobrar")
    + av("cuidado", "Nota fiscal e impostos", "<p>Converse com o seu contador sobre como emitir a nota da mensalidade e sobre o enquadramento. Isso depende de você ter CNPJ e do regime da empresa, e eu não consigo decidir por você.</p>")
    + '</section>')

add('''<section class="pg">
  <h3 class="sec" style="margin-top:0">Simulação (não é promessa de resultado)</h3>
  <table>
    <tr><th>Cenário</th><th>Lojas pagantes</th><th>Receita mensal</th></tr>
    <tr><td>Começando</td><td>10 lojas no plano de R$ 49</td><td>R$ 490</td></tr>
    <tr><td>Crescendo</td><td>10 de R$ 49 + 15 de R$ 99 + 5 de R$ 199</td><td>R$ 2.970</td></tr>
  </table>
  <p>Fora isso, o serviço de implantação e os sites completos entram à parte. Os custos fixos principais são o Supabase Pro (cerca de US$ 25 por mês, ver capítulo 08), a hospedagem e o domínio.</p>
  <h3 class="sec">Fase seguinte: cobrança automática</h3>
  <p>Com uma conta <b>Asaas</b> (precisa de CNPJ), a assinatura mensal passa a ser gerada pela faixa de vendas do mês, o aviso de vencimento sai sozinho e a loja é suspensa automaticamente por falta de pagamento. Vale fazer quando você passar de umas 10 lojas pagantes: antes disso a cobrança manual é mais simples.</p>
</section>''')

# ---------------- 06 ----------------
add('<section class="pg">' + cap("06", "Roteiro de teste", "Teste os três papéis antes de vender: o dono da loja, o cliente final e você. Reserve uma hora.") + '''
  <h3 class="sec">Como criar contas de teste sem ter vários e-mails</h3>
  <p>Com Gmail, <code>seunome+loja1@gmail.com</code> e <code>seunome+loja2@gmail.com</code> contam como e-mails diferentes para o sistema, mas chegam todos na sua caixa. O mesmo aplicativo autenticador guarda quantas contas você quiser.</p>
  <h3 class="sec">Parte A · Só olhar (5 minutos, sem criar nada)</h3>''' + check("Abra <code>/painel/</code> e toque em <b>Ver demonstração com dados fictícios</b>. Chegam pedidos falsos sozinhos para você ver o alerta.", "Abra <code>/crm/</code> e toque em <b>Ver demonstração</b>.", "Abra a vitrine de uma loja de exemplo no celular (<code>/l/nome-da-loja</code>) e adicione um item.")
    + '<h3 class="sec">Parte B · Como dono da loja</h3>' + check("Crie uma conta com <code>seunome+loja1@gmail.com</code>. <i>Esperado: tela “Confirme seu e-mail”.</i>", "Confirme pelo e-mail. <i>Esperado: volta para o site na etapa “Agora, a sua loja”.</i>", "Crie a loja <b>Loja Teste 1</b>, tipo Padaria. <i>Esperado: “Sua loja está no ar” com confete e o link.</i>", "Entre em <code>/painel/</code> e ative o login em 2 etapas. <i>Esperado: abre o painel, com “Primeiros passos”.</i>", "Toque em <b>Usar exemplo com fotos</b>. <i>Esperado: cardápio com 17 produtos e fotos.</i>", "Em <b>Dados da loja</b>, coloque logo, horário e taxa de entrega.", "Em <b>Equipe</b>, convide <code>seunome+loja2@gmail.com</code> como Atendente e aceite o convite em outro navegador.")
    + '<h3 class="sec">Parte C · Como cliente final (no celular)</h3>' + check("Abra o link da loja. <i>Esperado: visual escuro dourado (tema artesanal), capa, categorias e fotos.</i>", "Adicione 2 itens. <i>Esperado: o item “voa” até a barra “Ver pedido”.</i>", "Faça o pedido com entrega e Pix. <i>Esperado: tela “Pedido recebido” e o WhatsApp abre com o resumo.</i>", "Toque em <b>Acompanhar pedido</b>. <i>Esperado: página de rastreio sem telefone nem endereço.</i>", "Tente pedir abaixo do pedido mínimo. <i>Esperado: aviso e botão bloqueado.</i>")
    + '</section>')

add('<section class="pg">' + '<h3 class="sec" style="margin-top:0">Parte C (continuação) · De volta ao painel do dono</h3>' + check("O pedido aparece em <b>Pedidos</b>, com som. <i>Esperado: coluna Novos.</i>", "Avance: Confirmar, Em preparo, Pronto, Entregue. <i>Esperado: o rastreio do cliente acompanha cada etapa.</i>", "Pause os pedidos (botão verde no topo). <i>Esperado: a vitrine avisa que está pausada.</i>")
    + '<h3 class="sec">Parte D · Como você, dono da plataforma</h3>' + check("Rode no SQL do Supabase o comando que te torna administrador (um e-mail só).", "Entre em <code>/painel/</code> e depois em <code>/admin/</code>. <i>Esperado: a lista mostra Loja Teste 1, com origem e vendas.</i>", "Mude a Situação da loja para Suspensa. <i>Esperado: a vitrine mostra “não encontramos esta loja”.</i> Volte para Ativa.", "Abra um link de anúncio com <code>?para=padaria&utm_source=teste&utm_campaign=t1</code>, crie outra conta e confira a origem no <code>/admin/</code>.", "Preencha o formulário “Quero ajuda para montar”. <i>Esperado: lead no <code>/crm/</code> e WhatsApp aberto.</i>")
    + '<h3 class="sec">Parte E · Falhas que precisam estar sob controle</h3>' + check("Senha errada. <i>Esperado: “E-mail ou senha incorretos”.</i>", "Entrar sem confirmar o e-mail. <i>Esperado: pede a confirmação.</i>", "Loja 2 tentando ver a Loja 1. <i>Esperado: impossível. Cada loja só enxerga os próprios dados.</i>", "Usuário de função Cozinha. <i>Esperado: vê só Pedidos, sem pagamento.</i>")
    + '<h3 class="sec">Como limpar o teste</h3><p>Em <code>/admin/</code>, mude a loja para <b>Cancelada</b>. Para apagar de vez, no SQL Editor do Supabase:</p><pre>delete from public.lojas where slug = \'loja-teste-1\';</pre><p>Apaga a loja e tudo que é dela (produtos, pedidos, equipe). Depois, em Authentication › Users, apague o usuário de teste.</p>'
    + av("ok", "Passou em tudo?", "<p>Então a jornada está pronta para vender. Se algo falhar, anote em qual passo e me mande um print.</p>") + '</section>')

# ---------------- 07 ----------------
add('<section class="pg">' + cap("07", "Respostas rápidas de suporte", "O que os clientes mais vão perguntar e o que fazer.") + '''
  <table>
    <tr><th>O cliente diz</th><th>O que fazer</th></tr>
    <tr><td>“Esqueci a senha”</td><td>Na tela de entrar, ele toca em <b>Esqueci a senha</b>, digita o e-mail e recebe o link para criar outra.</td></tr>
    <tr><td>“O e-mail de confirmação não chegou”</td><td>Veja spam e promoções. Se não chegar em alguns minutos, no Supabase abra Authentication › Users, ache o e-mail, toque nos três pontinhos e escolha <b>Confirm user</b>. Se acontecer com todo mundo, falta o SMTP (capítulo 09).</td></tr>
    <tr><td>“Perdi o celular do código de 2 etapas”</td><td>No Supabase, em Authentication › Users, abra o usuário e remova os fatores de autenticação (confira o nome exato da opção na tela). No próximo acesso ele configura de novo.</td></tr>
    <tr><td>“Quero trocar logo, capa ou cor”</td><td>Painel › <b>Dados da loja</b>. A foto é reduzida automaticamente.</td></tr>
    <tr><td>“O pedido não chegou no meu WhatsApp”</td><td>O pedido sempre fica em <b>Pedidos</b> no painel. A mensagem do WhatsApp só sai se o cliente tocar em enviar.</td></tr>
    <tr><td>“Um item acabou”</td><td>Painel › Produtos e categorias, e desligue a chave do item. Ele some da vitrine na hora.</td></tr>
    <tr><td>“Quero cancelar”</td><td>Sem fidelidade e sem multa. Mude a Situação para Cancelada em <code>/admin/</code>. Se pedir, exporte os dados antes.</td></tr>
    <tr><td>“Posso usar meu domínio?”</td><td>Ainda não na plataforma: a loja fica em <code>bistroconnect.com.br/l/nome</code>. Domínio próprio é o serviço de site completo.</td></tr>
    <tr><td>“Quem vê meus dados?”</td><td>Só quem está na equipe da loja. Os dados dos clientes não são vendidos nem compartilhados. Veja a Política de privacidade.</td></tr>
  </table>
</section>''')

# ---------------- 08 ----------------
add('<section class="pg">' + cap("08", "Hostinger sem Supabase?", "A pergunta é boa, e a resposta curta é: não, e não vale a pena tentar.") + '''
  <div class="grid2">
    <div class="card"><span class="tag">Hostinger</span><h4>O prédio e a vitrine</h4><p>Páginas, imagens, domínio, certificado de segurança (SSL) e e-mails. Entrega os arquivos do site para muita gente ao mesmo tempo, sem esforço.</p></div>
    <div class="card escuro"><span class="tag">Supabase</span><h4>O cofre e a caixa registradora</h4><p>Contas e senhas, login em 2 etapas, lojas, cardápios, pedidos em tempo real, fotos enviadas e a separação entre uma loja e outra.</p></div>
  </div>
  <p><b>A Hostinger aguenta o site, inclusive com milhares de visitas por dia.</b> O que nenhuma hospedagem comum faz sozinha é guardar cadastros, logins e pedidos com segurança. Isso é papel do banco de dados, e é o que o Supabase entrega pronto.</p>
  <h3 class="sec">E se eu usar o MySQL que vem na Hostinger?</h3>
  <p>Tecnicamente dá, mas não seria “trocar o Supabase”. Seria <b>construir um sistema novo</b>, porque hoje o Supabase faz por nós:</p>
  <ul><li>login seguro e a 2ª etapa;</li><li>a regra que impede uma loja de ver os dados de outra;</li><li>a conferência do preço de cada pedido no servidor;</li><li>os limites contra robôs e contra pedido duplicado;</li><li>o alerta de pedido novo em tempo real;</li><li>o envio e a guarda das fotos;</li><li>os backups.</li></ul>
  <p>São semanas ou meses de trabalho, e depois <b>você passa a ser responsável por corrigir qualquer falha de segurança</b>, com dados de clientes dentro. A hospedagem compartilhada também limita processos simultâneos e memória por conta, e o horário de almoço junta muitos pedidos ao mesmo tempo.</p>
  ''' + av("ok", "Minha recomendação", "<p>Manter Hostinger para o site e Supabase para o banco. Cada um faz o que faz melhor, e o custo é baixo.</p>") + '</section>')

add('''<section class="pg">
  <h3 class="sec" style="margin-top:0">Quanto o Supabase aguenta</h3>
  <table>
    <tr><th></th><th>Gratuito</th><th>Pro (cerca de US$ 25/mês)</th></tr>
    <tr><td><b>Banco de dados</b></td><td>500 MB</td><td>8 GB</td></tr>
    <tr><td><b>Fotos e arquivos</b></td><td>1 GB</td><td>100 GB</td></tr>
    <tr><td><b>Tráfego por mês</b></td><td>cerca de 5 GB</td><td>cerca de 250 GB</td></tr>
    <tr><td><b>Pausa por falta de uso</b></td><td>Sim, após cerca de 1 semana sem acesso</td><td>Não</td></tr>
    <tr><td><b>Backup diário</b></td><td>Não</td><td>Sim</td></tr>
    <tr><td><b>Serve para</b></td><td>Testes e as primeiras lojas</td><td>Dezenas a centenas de lojas pequenas (estimativa)</td></tr>
  </table>
  <p><small>Valores aproximados. Confirme os números atuais em supabase.com/pricing antes de decidir.</small></p>
  <p>Pedidos são só texto e ocupam pouco. O que pesa é <b>foto</b> e a quantidade de visitas à vitrine. O painel reduz as fotos de produto para no máximo 900 px antes de enviar (cerca de 60 a 100 KB cada), e o navegador guarda a foto por 1 ano, então quem volta à vitrine quase não gasta tráfego.</p>
  ''' + av("cuidado", "Quando passar para o Pro", "<p><b>No dia em que o primeiro cliente começar a pagar.</b> O plano gratuito pausa o projeto após uma semana sem uso e não tem backup diário. Com clientes pagando, isso não é aceitável. Três lojas no plano de R$ 49 já cobrem a mensalidade do Pro, dependendo do câmbio.</p>") + '''
  <h3 class="sec">E o futuro?</h3>
  <p>Se um dia a plataforma tiver centenas de lojas e você quiser controlar tudo, existe a opção de instalar o próprio Supabase num servidor virtual (VPS) da Hostinger. Dá certo, mas você assume atualizações, backups e segurança. Só faz sentido com escala grande.</p>
</section>''')

# ---------------- 09 ----------------
add('<section class="pg">' + cap("09", "Lista final antes de abrir as vendas", "Marque cada item. Os três primeiros destravam o resto.") + check(
    "<b>Rodar <code>02-admin-por-mes.sql</code></b> no SQL Editor do Supabase da plataforma (ativa o seletor de mês para cobrança).",
    "<b>Configurar o SMTP</b> (e-mail de confirmação com o seu domínio), em Authentication › Emails › SMTP Settings. Sem isso, o Supabase manda poucos e-mails por hora e os cadastros travam.",
    "<b>Preencher o <code>config.js</code></b> da plataforma: WhatsApp de suporte e dados da empresa (razão social, CNPJ, e-mail, cidade), que aparecem nos Termos e na Privacidade.",
    "<b>Revisão jurídica</b> dos Termos de uso e da Política de privacidade por um advogado.",
    "<b>Definir a cobrança:</b> chave Pix (de preferência da empresa), dia de vencimento e quem emite nota.",
    "<b>Supabase Pro</b> assim que houver o primeiro cliente pagando.",
    "<b>Conectar o CRM</b> ao banco do site oficial (bloco <code>window.BISTRO</code> do <code>config.js</code>), para o formulário gravar os leads.",
    "<b>Criar as conversões</b> no Google Ads (“Loja criada” e “Pedido de ajuda”) e preencher os IDs do Pixel e do Google no <code>config.js</code>.",
    "<b>Revisar os anúncios:</b> use “app de delivery”, nunca a marca do concorrente, e prefira “pedido organizado no painel e no WhatsApp”.",
    "<b>Subir o pacote de atualização</b> (temas das lojas e painel) na Hostinger.",
    "<b>Fazer o roteiro de teste</b> do capítulo 06 inteiro, ao menos uma vez.") + av("ok", "Pronto para vender", "<p>Com tudo marcado, você pode ligar os anúncios. Comece com um orçamento pequeno por nicho, acompanhe a coluna Origem do <code>/admin/</code> e dobre o que funciona.</p>") + '</section>')

# só a capa e a abertura de cada capítulo começam em página nova; o resto flui
P = [x if ('class="cap"' in x or "capa" in x[:40]) else x.replace('<section class="pg">', '<section class="fl">', 1) for x in P]
css += ".fl{break-before:auto}\n"
html = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Guia da venda · Bistrô Connect</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&family=DM+Mono:wght@400;500&display=swap">
<style>{css}</style>
</head>
<body>
{chr(10).join(P)}
</body>
</html>'''
open("manual/guia-de-vendas.html", "w", encoding="utf-8").write(html)
print("manual/guia-de-vendas.html gerado:", len(html) // 1024, "KB,", len(P), "seções")
