"""Gera manual/plano-de-divulgacao.html a partir do CSS do manual.  O PDF sai abrindo o HTML no Chrome e imprimindo (A4, com fundo).
Os textos de anúncio têm limite de caracteres: este script confere cada um e para se algum passar.
Uso:  python3 ferramentas/montar-plano-divulgacao.py"""
import re, os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base = open(os.path.join(RAIZ, "manual/manual.html"), encoding="utf-8").read()
css = re.search(r"<style>(.*?)</style>", base, re.S).group(1)
css += """
h3.sec{font-size:12pt;margin:16px 0 6px;color:var(--navy);border-left:4px solid var(--ouro);padding-left:10px}
.msg{background:#F3F6FA;border-left:4px solid var(--azul);border-radius:0 10px 10px 0;padding:10px 14px;font-size:10pt;margin:8px 0 12px;break-inside:avoid;white-space:pre-line}
.msg b.t{display:block;font:600 8pt 'Poppins';letter-spacing:.12em;text-transform:uppercase;color:#0B5B9E;margin-bottom:3px}
.fl{break-before:auto}
td small,li small{color:var(--suave)}
.kit{display:grid;grid-template-columns:repeat(6,1fr);gap:6px;margin:8px 0 12px;break-inside:avoid}
.kit img{width:100%;border-radius:6px;border:1px solid var(--linha)}
.kit2{display:grid;grid-template-columns:repeat(6,1fr);gap:6px;margin:6px 0 12px;break-inside:avoid}
.kit2 img{width:100%;border-radius:8px;border:1px solid var(--linha)}
.kit2.l img{aspect-ratio:9/16;object-fit:cover}
table.c td{font-size:9.5pt}
.mono{font:9pt 'DM Mono',monospace}
"""


def cap(n, titulo, intro):
    return f'<div class="cap"><div class="n">{n}</div><h2>{titulo}</h2></div><p class="intro">{intro}</p>'


def av(tipo, titulo, texto):
    ic = {"dica": "i", "cuidado": "!", "ok": "✓"}[tipo]
    return f'<div class="av {tipo}"><div class="i">{ic}</div><div><b class="t">{titulo}</b>{texto}</div></div>'


def check(*itens):
    return '<ul class="check">' + "".join(f"<li><span>{i}</span></li>" for i in itens) + "</ul>"


def msg(titulo, texto):
    return f'<div class="msg"><b class="t">{titulo}</b>{texto}</div>'


def passo(t, p):
    return f'<div class="passo"><div><b class="t">{t}</b><p>{p}</p></div></div>'


def limite(textos, n, nome):
    for t in textos:
        if len(t) > n:
            raise SystemExit(f"{nome} passa de {n} caracteres ({len(t)}): {t}")
    return textos


def tabela(cabecalho, linhas, cls=""):
    h = "".join(f"<th>{c}</th>" for c in cabecalho)
    r = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in l) + "</tr>" for l in linhas)
    return f'<table class="{cls}"><tr>{h}</tr>{r}</table>'


P = []
add = P.append

# ------------------------------------------------------------------ capa e sumário
add('''<section class="pg capa">
  <div class="topo">Documento interno · Marketing</div>
  <div class="meio">
    <img src="logo-clara.png" alt="Bistrô Connect">
    <h1>Plano de divulgação</h1>
    <div class="linha"></div>
    <p class="sub">Instagram, Meta Ads e Google Ads, com orçamento, metas e regras de parada para o dinheiro não ser jogado fora.</p>
  </div>
  <div class="rod"><span>bistroconnect.com.br</span><span>Outubro de 2026</span></div>
</section>''')

add('''<section class="pg">
  <div class="cap"><div class="n">≡</div><h2>Sumário</h2></div>
  <p class="intro">Faça o capítulo 01 antes de gastar qualquer real. Os demais seguem a ordem em que você vai executar.</p>
  <div class="sumario">
    <div><span>01</span><b>O que falta antes de divulgar</b></div>
    <div><span>02</span><b>A estratégia em uma página</b></div>
    <div><span>03</span><b>A mensagem: dor, conta e saída</b></div>
    <div><span>04</span><b>Perfil do Instagram, passo a passo</b></div>
    <div><span>05</span><b>Conteúdo: 30 dias de postagens</b></div>
    <div><span>06</span><b>Meta Ads (Instagram e Facebook)</b></div>
    <div><span>07</span><b>Google Ads (Pesquisa)</b></div>
    <div><span>08</span><b>Divulgação sem gastar</b></div>
    <div><span>09</span><b>Scripts de venda e respostas</b></div>
    <div><span>10</span><b>Orçamento, metas e regras de decisão</b></div>
    <div><span>11</span><b>Roteiro de 90 dias e rotina semanal</b></div>
    <div><span>12</span><b>Lista de lançamento</b></div>
  </div>
  ''' + av("cuidado", "Sobre a palavra “infalível”", "<p>Nenhum plano de marketing é infalível, e quem promete isso está vendendo ilusão. O que este plano faz é <b>reduzir o risco</b>: testa pouco, mede cada etapa, define de antemão quando parar, quando corrigir e quando investir mais. Os números de exemplo são <b>hipóteses para você testar</b>, não promessas de resultado.</p>") + '''
  <div class="kit2" style="margin-top:14px"><img src="kit-instagram/post-1-dor.png"><img src="kit-instagram/post-2-conta.png"><img src="kit-instagram/post-3-solucao.png"><img src="kit-instagram/post-4-antes-depois.png"><img src="kit-instagram/post-5-como-funciona.png"><img src="kit-instagram/post-6-chamada.png"></div>
  <p style="font-size:9pt;color:var(--suave)">Os 6 primeiros posts já estão prontos na pasta <code>kit-instagram</code>, na identidade da marca.</p>
</section>''')

# ------------------------------------------------------------------ 01
add('<section class="pg">' + cap("01", "O que falta antes de divulgar", "Anúncio em página incompleta desperdiça dinheiro. Os itens “bloqueiam” até estarem feitos.") + '''
  <h3 class="sec">Bloqueadores (sem isto, não ligue anúncio)</h3>''' + check(
    "<b>Subir o pacote de atualização na Hostinger</b> (<code>bistroconnect-ATUALIZACAO.zip</code>), com os temas das lojas, as fotos menores, a imagem de prévia do link e o <code>robots.txt</code>.",
    "<b>Rodar <code>plataforma-02-admin-por-mes.sql</code></b> no SQL Editor do Supabase da plataforma.",
    "<b>Configurar o SMTP</b> (e-mail de confirmação com o seu domínio). Sem isso, o cadastro em rajada trava justamente quando o anúncio dá certo.",
    "<b>Preencher o <code>config.js</code></b>: WhatsApp de suporte (sem ele o botão de WhatsApp da página não funciona), dados da empresa (Termos e Privacidade). Rode também o <code>03-crm.sql</code> no Supabase, para o CRM e o formulário de leads funcionarem.",
    "<b>Criar as contas de anúncio</b> (detalhes abaixo) e colocar os IDs no <code>config.js</code>.",
    "<b>Fazer o roteiro de teste</b> do Guia da venda, capítulo 06, inteiro, pelo menos uma vez, e conferir que o Pixel e a tag do Google registram os eventos.",
    "<b>Conferir o percentual do app de delivery</b> (12% e 23%) numa fonte atual e anotar a data. É o argumento central e precisa ser verdadeiro quando o anúncio rodar.") + '''
  <h3 class="sec">Contas que você precisa criar (nesta ordem)</h3>
  <table class="c"><tr><th>Conta</th><th>Para quê</th><th>Dica</th></tr>
  <tr><td><b>Instagram profissional</b> (empresa) e <b>Página do Facebook</b></td><td>Perfil e base dos anúncios da Meta</td><td>Crie a Página primeiro e ligue o Instagram a ela</td></tr>
  <tr><td><b>Gerenciador de Negócios da Meta</b></td><td>Pixel, domínio e contas de anúncio</td><td>Use o e-mail da empresa</td></tr>
  <tr><td><b>Pixel da Meta</b> e <b>verificação do domínio</b></td><td>Medir cadastros e lojas criadas</td><td>Copie o ID (só números) para <code>pixelId</code>. Verifique o domínio <code>bistroconnect.com.br</code> no Gerenciador de Negócios.</td></tr>
  <tr><td><b>Google Ads</b></td><td>Campanhas de Pesquisa</td><td>Crie a conta no modo “completo”, não “campanha inteligente”</td></tr>
  <tr><td><b>Conversões do Google Ads</b></td><td>Medir o que importa</td><td>Crie duas: <b>Loja criada</b> (principal) e <b>Pedido de ajuda</b> (secundária). Cada uma gera um rótulo para <code>googleAdsRotuloLoja</code> e <code>googleAdsRotuloLead</code>.</td></tr>
  <tr><td><b>Google Analytics 4</b></td><td>Ver de onde vem o tráfego</td><td>ID que começa com G-, em <code>googleAnalyticsId</code></td></tr>
  <tr><td><b>Perfil da Empresa no Google</b></td><td>Aparecer no Google e no Maps</td><td>Grátis. Veja o capítulo 08.</td></tr>
  <tr><td><b>WhatsApp Business</b></td><td>Atender os leads</td><td>Mensagem de saudação, de ausência e etiquetas de funil</td></tr></table>
  ''' + av("dica", "Como conferir que a medição funciona", "<p>Instale as extensões gratuitas <b>Meta Pixel Helper</b> e <b>Tag Assistant</b> no Chrome. Abra o site, aceite os cookies, crie uma conta de teste e veja os eventos aparecerem (cadastro, loja criada). Se não aparecerem, não ligue o anúncio.</p>") + '</section>')

add('''<section class="fl">
  <h3 class="sec">Recomendados (faça na primeira semana)</h3>''' + check(
    "<b>Revisão jurídica</b> dos Termos de uso e da Política de privacidade, antes de escalar o gasto.",
    "<b>Supabase Pro</b> assim que o primeiro cliente pagar (ou antes, se a plataforma passar de 15 a 20 lojas).",
    "<b>Domínio de e-mail profissional</b> (<code>contato@bistroconnect.com.br</code>), usado no SMTP, nos Termos e nos anúncios.",
    "<b>Três lojas de demonstração</b> publicadas (padaria, hamburgueria e restaurante), para mostrar em qualquer conversa.",
    "<b>Vídeo curto de 40 segundos</b> mostrando o celular do cliente fazendo o pedido e o painel recebendo. É o melhor criativo que você pode ter.") + '''
  ''' + av("ok", "Diagnóstico honesto do que já está pronto", "<p>A página de vendas, o cadastro, as lojas nos três temas, o painel, o rastreio, o CRM, os Termos e a Privacidade, a medição de Meta e Google e a página por nicho (<code>?para=padaria</code>) <b>já existem e foram testados</b>. O que falta é configuração e conta, não construção.</p>") + '''
</section>''')

# ------------------------------------------------------------------ 02
add('<section class="pg">' + cap("02", "A estratégia em uma página", "Quem, o quê, por que ele compra e como o dinheiro entra.") + '''
  <div class="grid2">
    <div class="card escuro"><span class="tag">Quem</span><h4>Dono de comida pequena</h4><p>Padaria, cafeteria, hamburgueria, restaurante, pizzaria, doceria e marmitaria, com 1 a 3 lojas, que já vende por WhatsApp e Instagram e/ou paga comissão a app de delivery.</p></div>
    <div class="card"><span class="tag">Dor</span><h4>Margem e bagunça</h4><p>Comissão de até 23% por pedido, WhatsApp lotado de áudio, pedido errado e cliente perguntando “já saiu?”.</p></div>
    <div class="card"><span class="tag">Oferta</span><h4>Venda direta, sem comissão</h4><p>Loja online em 5 minutos, grátis até R$ 3 mil em vendas por mês, sem cartão de crédito, com cardápio de exemplo já com fotos.</p></div>
    <div class="card escuro"><span class="tag">Prova</span><h4>Mostrar, não prometer</h4><p>Vitrines reais nos 3 temas, antes e depois do WhatsApp, a conta do ano e o vídeo do pedido chegando no painel.</p></div>
  </div>
  <h3 class="sec">O funil, com cada etapa medida</h3>
  <table class="c"><tr><th>Etapa</th><th>O que acontece</th><th>Onde você mede</th></tr>
  <tr><td><b>1. Atenção</b></td><td>Vê o anúncio, o Reels ou o post</td><td>Alcance e visualizações (Instagram e Meta)</td></tr>
  <tr><td><b>2. Clique</b></td><td>Abre a página de vendas do nicho dele</td><td>Cliques e custo por clique (Meta e Google)</td></tr>
  <tr><td><b>3. Cadastro</b></td><td>Cria a conta</td><td>Evento “cadastro” (Meta e Google)</td></tr>
  <tr><td><b>4. Loja criada</b></td><td>Termina o cadastro da loja. <b>É a conversão principal.</b></td><td>Evento “loja criada” e coluna Origem no <code>/admin/</code></td></tr>
  <tr><td><b>5. Ativação</b></td><td>Cadastra produtos e divulga o link</td><td>Primeiros passos no painel e vitrine com pedidos</td></tr>
  <tr><td><b>6. Receita</b></td><td>Compra a ajuda, o site completo ou passa de R$ 3 mil e paga a mensalidade</td><td>Seu controle de cobrança</td></tr></table>
  ''' + av("cuidado", "A verdade sobre o dinheiro", "<p>Quem se cadastra no plano grátis <b>não gera receita</b> até vender mais de R$ 3 mil por mês. A receita do começo vem do <b>serviço de ajuda para montar</b> e dos <b>sites completos</b>. Por isso, o anúncio precisa trazer lojas e o seu WhatsApp precisa converter parte delas em serviço. A conta de equilíbrio está no capítulo 10.</p>") + '</section>')

# ------------------------------------------------------------------ 03
add('<section class="pg">' + cap("03", "A mensagem: dor, conta e saída", "Toda peça segue a mesma sequência. Mostre o problema, faça o dono ver a conta e só então apresente a saída.") + '''
  <h3 class="sec">Os 5 ângulos de comunicação</h3>
  <table class="c"><tr><th>Ângulo</th><th>Frase-base</th><th>Melhor para</th></tr>
  <tr><td><b>A. A comissão</b></td><td>“O app de delivery fica com até 23% do seu pedido.”</td><td>Quem já vende por app</td></tr>
  <tr><td><b>B. A conta do ano</b></td><td>“Quem vende R$ 10 mil por mês pelo app deixa até R$ 27.600 por ano em comissão.”</td><td>Todos. Convence pelo número.</td></tr>
  <tr><td><b>C. O caos do WhatsApp</b></td><td>“Áudio, ‘quanto fica?’ e pedido anotado errado.”</td><td>Quem vende só por WhatsApp e Instagram</td></tr>
  <tr><td><b>D. O cliente é seu</b></td><td>“No app, o cliente é deles. Na sua loja, o contato fica com você.”</td><td>Quem quer fidelizar</td></tr>
  <tr><td><b>E. Sem risco</b></td><td>“Grátis até R$ 3 mil em vendas por mês. Sem cartão de crédito.”</td><td>Quem tem medo de gastar</td></tr></table>
  <h3 class="sec">Regras de ouro da comunicação</h3>''' + check(
    "<b>Nunca escreva “iFood” ou outra marca de concorrente</b> no texto do anúncio. Use “app de delivery”. Isso evita reprovação por marca registrada na Meta e no Google. Na página de vendas pode continuar.",
    "<b>Todo número precisa ser verdadeiro e verificável.</b> “Até 23%” é o teto do plano de entrega do app; confira e anote a fonte e a data.",
    "<b>Fale de pedido “organizado no painel e no WhatsApp”</b>, e não que “o pedido sempre chega no seu WhatsApp”: o pedido sempre fica salvo no painel, mas o WhatsApp só recebe a mensagem se o cliente tocar em enviar.",
    "<b>Não prometa faturamento</b> (“venda o dobro”, “fature R$ 10 mil”). Prometa o que o produto faz: organizar, tirar a comissão, dar o link.",
    "<b>Mostre o produto.</b> A vitrine nos três temas é o seu melhor visual; use fotos de comida de verdade, não banco de imagem genérico.") + '</section>')

# ------------------------------------------------------------------ 04 Instagram
nome_ig = "Bistrô Connect | Cardápio Digital"
bios = limite([
    "Cardápio online e pedido no WhatsApp p/ padaria, café e restaurante 🍞☕\nSem comissão. Grátis até R$ 3 mil/mês 👇",
    "Pare de pagar comissão ao app 💸\nSua loja online em 5 min, com pedido no WhatsApp.\nGrátis até R$ 3 mil/mês 👇",
    "Vendas diretas para quem vive de comida 🍔🥐\nCardápio digital + rastreio + painel.\nCrie sua loja grátis 👇",
], 150, "Bio do Instagram")
limite([nome_ig], 64, "Nome do Instagram")

add('<section class="pg">' + cap("04", "Perfil do Instagram, passo a passo", "O perfil é a sua vitrine para quem clica no anúncio ou ouve falar. Em 5 segundos ele precisa entender o que você faz e para quem.") + '''
  <h3 class="sec">Os campos do perfil</h3>
  <table class="c"><tr><th>Campo</th><th>O que colocar</th></tr>
  <tr><td><b>Tipo de conta</b></td><td>Profissional, categoria <i>Serviço de internet</i> ou <i>Software</i></td></tr>
  <tr><td><b>Nome</b> (até 64)</td><td>''' + nome_ig + ''' <small>(o nome é pesquisável, então leva a palavra-chave)</small></td></tr>
  <tr><td><b>@ de usuário</b></td><td>Tente <code>@bistroconnect</code>. Se estiver ocupado: <code>@bistroconnect.br</code> ou <code>@usebistroconnect</code>.</td></tr>
  <tr><td><b>Foto</b></td><td><code>kit-instagram/avatar.png</code> (o “B” dourado)</td></tr>
  <tr><td><b>Link</b></td><td><code>https://bistroconnect.com.br/?utm_source=instagram&amp;utm_medium=bio</code></td></tr>
  <tr><td><b>Botão de contato</b></td><td>WhatsApp (o do suporte)</td></tr>
  <tr><td><b>Destaques</b></td><td>Como funciona · Planos · Lojas · Dúvidas · Comece (capas em <code>kit-instagram/destaque-*.png</code>)</td></tr></table>
  <h3 class="sec">Três opções de bio (até 150 caracteres)</h3>''' + "".join(msg(f"Opção {i + 1} · {len(b)} caracteres", b) for i, b in enumerate(bios)) + '''
  <h3 class="sec">Primeiros 9 posts (a grade que convence)</h3>
  <p>Publique nesta ordem para o perfil já nascer com cara de negócio sério: <b>1</b> dor, <b>2</b> conta do ano, <b>3</b> solução com o celular, <b>4</b> antes e depois, <b>5</b> como funciona, <b>6</b> chamada. Depois, 1 Reels mostrando a vitrine, 1 Reels do pedido chegando no painel e 1 depoimento (quando tiver).</p>
  ''' + av("dica", "Destaques", "<p>Crie cada destaque com 3 a 5 stories: <b>Como funciona</b> (3 passos), <b>Planos</b> (a tabela), <b>Lojas</b> (as 3 vitrines), <b>Dúvidas</b> (sem cartão, sem fidelidade, o cliente paga direto a você) e <b>Comece</b> (o link).</p>") + '</section>')

legendas = [
    ("Post 1 · A dor", "O app de delivery fica com até 23% do seu pedido. 💸\n\nVocê faz a comida, a entrega e o atendimento. Ele leva uma fatia de cada venda.\n\nExiste outro jeito: vender direto, no seu cardápio online, sem comissão.\n\n👉 Link na bio. Crie sua loja grátis.\n\n#cardapiodigital #padaria #hamburgueria #restaurante #delivery #empreendedorismo #vendasonline"),
    ("Post 2 · A conta do ano", "Faça a conta. 🧮\n\nQuem vende R$ 10 mil por mês pelo app, no plano de entrega de 23%, deixa até R$ 27.600 por ano em comissão.\n\nÉ reforma, é moto, é funcionário a mais.\n\n(Confira as taxas do plano do seu app.)\n\n👉 Link na bio: venda direto, sem comissão.\n\n#cardapiodigital #comissao #delivery #donodenegocio"),
    ("Post 3 · A solução", "Sua loja online em 5 minutos. 📱\n\nCardápio com fotos, pedido pronto e rastreio para o cliente. Sem comissão. Grátis até R$ 3 mil em vendas por mês.\n\n👉 Link na bio.\n\n#lojaonline #cardapiodigital #padaria #cafeteria"),
    ("Post 4 · Antes e depois", "Pedido no WhatsApp: caos ou organizado? 💬\n\nÀ esquerda, o que acontece hoje. À direita, o pedido que chega pronto, com itens, endereço, forma de pagamento e total.\n\nMenos áudio. Menos erro. Mais venda.\n\n👉 Crie sua loja grátis. Link na bio."),
    ("Post 5 · Como funciona", "3 passos. Sem programador. ✅\n\n1) Crie a conta e a loja\n2) Use o cardápio de exemplo (já vem com fotos)\n3) Divulgue o seu link\n\nSalve este post e mande para quem tem um negócio de comida. 🍞\n\n👉 Link na bio."),
    ("Post 6 · Chamada", "Venda direto. Sem comissão. 🚀\n\nGrátis até R$ 3 mil em vendas por mês. Sem cartão de crédito.\n\nToque no link da bio e crie sua loja agora.\n\nQuer ajuda para montar? Chame no direct ou no WhatsApp."),
]
add('<section class="pg"><h3 class="sec" style="margin-top:0">Legendas prontas dos 6 posts do kit</h3>' + "".join(msg(t, x) for t, x in legendas) + '</section>')

# ------------------------------------------------------------------ 05 conteúdo
add('<section class="pg">' + cap("05", "Conteúdo: 30 dias de postagens", "Cinco pilares, cinco publicações por semana. Constância vale mais que perfeição.") + '''
  <h3 class="sec">Os 5 pilares</h3>
  <table class="c"><tr><th>Pilar</th><th>Objetivo</th><th>Formato</th></tr>
  <tr><td><b>1. A conta e a dor</b></td><td>Fazer o dono se enxergar</td><td>Imagem e Reels curto</td></tr>
  <tr><td><b>2. Como fazer</b></td><td>Mostrar que é fácil</td><td>Reels de tela e carrossel</td></tr>
  <tr><td><b>3. Vitrines e antes e depois</b></td><td>Mostrar o resultado</td><td>Reels e stories</td></tr>
  <tr><td><b>4. Gestão para dono de comida</b></td><td>Gerar autoridade e salvamentos</td><td>Carrossel</td></tr>
  <tr><td><b>5. Oferta e prova</b></td><td>Levar ao cadastro</td><td>Imagem, stories e depoimentos</td></tr></table>
  <h3 class="sec">Calendário das 4 semanas</h3>''' + tabela(["Dia", "Formato", "Tema", "Chamada"], [
    ["S1 seg", "Imagem", "Post 1 do kit: a dor dos 23%", "Link na bio"],
    ["S1 ter", "Reels", "Roteiro 1: “Quanto você paga ao app?”", "Comente “CONTA”"],
    ["S1 qua", "Imagem", "Post 2 do kit: a conta do ano", "Salve o post"],
    ["S1 qui", "Carrossel", "5 erros do cardápio no WhatsApp", "Compartilhe"],
    ["S1 sex", "Imagem", "Post 3 do kit: sua loja em 5 minutos", "Link na bio"],
    ["S2 seg", "Reels", "Roteiro 2: o pedido chegando no painel", "Link na bio"],
    ["S2 ter", "Imagem", "Post 4 do kit: antes e depois", "Link na bio"],
    ["S2 qua", "Carrossel", "Como montar um cardápio que vende (fotos, nomes, preço)", "Salve"],
    ["S2 qui", "Reels", "Roteiro 3: tour pelo painel", "Comente “PAINEL”"],
    ["S2 sex", "Stories", "Enquete: “Você vende por app, WhatsApp ou os dois?”", "Direct"],
    ["S3 seg", "Reels", "Roteiro 4: loja de padaria, hamburgueria e restaurante lado a lado", "Link na bio"],
    ["S3 ter", "Imagem", "Post 5 do kit: 3 passos", "Link na bio"],
    ["S3 qua", "Carrossel", "Como precificar sem perder margem", "Salve"],
    ["S3 qui", "Reels", "Roteiro 5: por que o cliente é seu e não do app", "Compartilhe"],
    ["S3 sex", "Stories", "Perguntas e respostas (caixinha)", "Direct"],
    ["S4 seg", "Reels", "Bastidores: criando uma loja ao vivo em 5 minutos", "Link na bio"],
    ["S4 ter", "Imagem", "Depoimento ou caso de uma loja de teste (com autorização)", "Link na bio"],
    ["S4 qua", "Carrossel", "Checklist do primeiro dia da loja online", "Salve"],
    ["S4 qui", "Reels", "Resposta a uma dúvida real recebida", "Direct"],
    ["S4 sex", "Imagem", "Post 6 do kit: venda direto, sem comissão", "Link na bio"],
], "c") + '</section>')

add('''<section class="pg"><h3 class="sec" style="margin-top:0">5 roteiros de Reels (15 a 30 segundos)</h3>''' + msg("Roteiro 1 · Quanto você paga ao app?", "0–3s (texto na tela): “Você sabe quanto o app leva de cada pedido?”\n3–10s: mostre um pedido de R$ 80 e a conta: até R$ 18,40 de comissão.\n10–20s: “Em 12 meses, quem vende R$ 10 mil por mês deixa até R$ 27.600.”\n20–28s: “Existe outro jeito. Link na bio.”") + msg("Roteiro 2 · O pedido chegando no painel", "0–3s: “Assim chega um pedido de verdade.”\n3–12s: tela dividida: o celular do cliente escolhendo e enviando, e o painel tocando o alerta de pedido novo.\n12–22s: mostre o cliente acompanhando pelo link de rastreio.\n22–28s: “Sem comissão. Link na bio.”") + msg("Roteiro 3 · Tour pelo painel", "0–3s: “O painel de uma loja de padaria, em 30 segundos.”\n3–25s: Início (link e plano do mês), Pedidos, Cardápio com fotos, Equipe.\n25–30s: “Crie o seu grátis. Link na bio.”") + msg("Roteiro 4 · Três lojas, três estilos", "0–3s: “A mesma plataforma, três jeitos de vender.”\n3–25s: mostre a vitrine de padaria (café e dourado), hamburgueria (preto e vermelho) e restaurante (carvão e âmbar), uma em cada 7 segundos.\n25–30s: “O visual combina com o seu negócio. Link na bio.”") + msg("Roteiro 5 · O cliente é seu", "0–4s: “No app, o cliente é deles. E na sua loja?”\n4–20s: explique: o contato do cliente fica com você, no seu WhatsApp, e ele pode voltar a comprar direto.\n20–28s: “Venda direto. Link na bio.”") + '''
  ''' + av("dica", "Como gravar sem estúdio", "<p>Grave a tela do celular com o gravador nativo, fale por cima (ou use legenda), e mostre o rosto no primeiro e no último segundo. Legenda sempre, porque muita gente assiste sem som. Fonte grande, 1 ideia por vídeo.</p>") + '''
  <h3 class="sec">Rotina diária de 20 minutos</h3>''' + check("Responder todos os comentários e directs.", "Comentar em 10 perfis de padarias, cafés e restaurantes da sua região (comentário de valor, sem propaganda).", "Postar 3 a 5 stories com enquete, bastidor ou um resultado.", "Anotar no <code>/crm/</code> quem demonstrou interesse.") + '</section>')

# ------------------------------------------------------------------ 06 Meta Ads
meta_textos = limite([
    "Você faz a comida, a entrega e o atendimento. O app de delivery fica com até 23% de cada pedido. Crie seu cardápio online e venda direto, sem comissão. Grátis até R$ 3 mil/mês.",
    "Áudio, “quanto fica?” e pedido anotado errado. Com o cardápio online, o cliente monta o pedido sozinho e ele chega organizado no painel e no WhatsApp. Crie sua loja em 5 minutos.",
    "Vende R$ 10 mil por mês pelo app? Até R$ 2.300 vão embora em comissão. Faça a conta do seu negócio e veja como vender direto.",
], 220, "Texto do anúncio Meta")
meta_tit = limite(["Venda direto. Sem comissão.", "Sua loja online em 5 minutos", "Cardápio digital grátis", "Pare de pagar comissão ao app"], 40, "Título do anúncio Meta")

add('<section class="pg">' + cap("06", "Meta Ads (Instagram e Facebook)", "Duas campanhas simples, três ângulos e muita paciência na fase de aprendizado.") + '''
  <h3 class="sec">Estrutura recomendada</h3>
  <table class="c"><tr><th></th><th>Campanha 1 · Cadastro no site</th><th>Campanha 2 · Conversa no WhatsApp</th></tr>
  <tr><td><b>Objetivo</b></td><td>Leads ou Vendas, com conversão no site</td><td>Mensagens, com destino WhatsApp</td></tr>
  <tr><td><b>Evento a otimizar</b></td><td>No começo: <b>Cadastro completo</b>. Quando tiver cerca de 50 eventos por semana: <b>Loja criada</b>.</td><td>Conversas iniciadas</td></tr>
  <tr><td><b>Para quem</b></td><td>Donos de comida que querem vender direto</td><td>Quem quer ajuda para montar</td></tr>
  <tr><td><b>Destino</b></td><td><code>bistroconnect.com.br/?para=padaria&amp;utm_source=meta&amp;utm_medium=pago&amp;utm_campaign=...</code></td><td>WhatsApp do suporte, com mensagem pronta</td></tr>
  <tr><td><b>Orçamento inicial</b></td><td>R$ 20 a R$ 30 por dia</td><td>R$ 15 a R$ 20 por dia</td></tr></table>
  <h3 class="sec">Público</h3>''' + check(
    "<b>Local:</b> comece por 2 a 3 cidades ou regiões onde você consiga atender bem. O serviço de ajuda é pelo WhatsApp e videochamada, mas comece concentrado para medir.",
    "<b>Idade:</b> 25 a 55 anos. <b>Idioma:</b> português.",
    "<b>Segmentação:</b> comece com público amplo (Advantage+) e deixe os criativos fortes fazerem a seleção, porque a Meta aprende com o seu Pixel. Teste um segundo conjunto com interesses (donos de restaurante, padaria, delivery, empreendedorismo gastronômico).",
    "<b>Remarketing</b> (depois de 2 semanas): quem visitou o site e não criou a loja, e quem interagiu com o Instagram. Orçamento de R$ 5 a R$ 10 por dia.",
    "<b>Não use</b> segmentação por dados sensíveis nem alegações pessoais (“você está endividado?”), porque a Meta reprova.") + '''
  </section>''')

add('<section class="fl"><h3 class="sec" style="margin-top:0">Textos dos anúncios (copiar e colar)</h3>' + "".join(msg(f"Texto principal {chr(65 + i)} · {len(t)} caracteres", t) for i, t in enumerate(meta_textos))
    + msg("Títulos (até 40 caracteres cada)", "\n".join(f"{t}  ({len(t)})" for t in meta_tit)) + msg("Botão", "Cadastre-se (Campanha 1) · Enviar mensagem (Campanha 2)")
    + '''<h3 class="sec">Criativos: o que testar</h3>
  <table class="c"><tr><th>Criativo</th><th>Formato</th><th>Ângulo</th></tr>
  <tr><td>Post 1 e Post 2 do kit</td><td>Imagem 4:5</td><td>A e B (comissão e conta do ano)</td></tr>
  <tr><td>Post 4 do kit</td><td>Imagem 4:5</td><td>C (caos do WhatsApp)</td></tr>
  <tr><td>Reels do pedido chegando no painel</td><td>Vídeo 9:16, 20 a 30 s</td><td>Produto e prova</td></tr>
  <tr><td>Reels com as três vitrines</td><td>Vídeo 9:16</td><td>Visual e identidade</td></tr></table>
  <h3 class="sec">Regras de operação (hipóteses de partida, ajuste com os seus dados)</h3>''' + check(
    "<b>Não mexa por 3 a 4 dias</b> depois de publicar. Mudar toda hora reinicia o aprendizado.",
    "<b>Só julgue um anúncio depois de gastar</b> pelo menos R$ 100 a R$ 150 nele, ou 1.000 impressões.",
    "<b>Desligue</b> o criativo cuja taxa de clique no link fique bem abaixo da dos outros e que não gere nenhum cadastro depois desse gasto.",
    "<b>Aumente o orçamento em no máximo 20%</b> a cada 3 dias, e só nos conjuntos que geram lojas criadas por um custo aceitável (capítulo 10).",
    "<b>Renove os criativos</b> a cada 3 a 4 semanas, para a audiência não cansar.",
    "<b>Confira as políticas</b> de anúncios da Meta no momento da publicação, porque elas mudam.") + '</section>')

# ------------------------------------------------------------------ 07 Google Ads
g_tit = limite([
    "Cardápio Digital Sem Comissão", "Loja Online Grátis p/ Comida", "Pedidos Direto no WhatsApp", "Crie Sua Loja em 5 Minutos",
    "Cardápio Online com Fotos", "Grátis até R$ 3 Mil em Vendas", "Pare de Pagar Comissão", "Rastreio do Pedido p/ Cliente",
    "Para Padaria, Café e Burger", "Sem Taxa por Pedido", "Painel de Pedidos ao Vivo", "Venda Direto, Sem Comissão",
    "Comece Grátis Hoje", "Sem Cartão de Crédito", "Cardápio no Link da Bio"], 30, "Título do Google Ads")
g_desc = limite([
    "Cardápio online com fotos e pedido organizado no painel e no WhatsApp. Sem comissão.",
    "Crie sua loja em minutos. Grátis até R$ 3 mil em vendas por mês. Sem cartão de crédito.",
    "Painel de pedidos, rastreio para o cliente e equipe com funções. Tudo em um só lugar.",
    "Para padarias, cafés, hamburguerias e restaurantes. Comece hoje e venda direto.",
], 90, "Descrição do Google Ads")

add('<section class="pg">' + cap("07", "Google Ads (Pesquisa)", "Pega quem já está procurando a solução. É o canal de maior intenção, e o mais fácil de jogar dinheiro fora sem negativas e sem medição.") + '''
  <h3 class="sec">Configuração da campanha</h3>
  <table class="c"><tr><th>Item</th><th>O que fazer</th></tr>
  <tr><td><b>Tipo</b></td><td>Pesquisa (Search). Desligue a Rede de Display e a “expansão de pesquisa” no começo.</td></tr>
  <tr><td><b>Conversão</b></td><td>Principal: <b>Loja criada</b>. Secundária: <b>Pedido de ajuda</b>. Já estão ligadas na página; falta criar no Google Ads e colocar os rótulos no <code>config.js</code>.</td></tr>
  <tr><td><b>Lances</b></td><td>Comece em <b>Maximizar cliques</b> com teto de CPC. Quando tiver de 15 a 30 conversões, mude para <b>Maximizar conversões</b>.</td></tr>
  <tr><td><b>Orçamento</b></td><td>R$ 20 a R$ 30 por dia</td></tr>
  <tr><td><b>Local</b></td><td>As mesmas regiões da Meta. Opção: “presença” (pessoas na região), não “interesse”.</td></tr>
  <tr><td><b>Horário</b></td><td>Das 7h às 22h no começo; ajuste pelos relatórios.</td></tr>
  <tr><td><b>Página de destino</b></td><td><code>/?para=padaria&amp;utm_source=google&amp;utm_medium=cpc&amp;utm_campaign=...</code>, uma por grupo de anúncios. O título muda para falar da mesma coisa que a pessoa pesquisou, o que melhora a nota do anúncio.</td></tr></table>
  <h3 class="sec">Grupos de anúncios e palavras-chave</h3>
  <p>Comece com correspondência <b>de frase</b> e <b>exata</b>. Use a lista como ponto de partida e confirme volumes no Planejador de Palavras-chave.</p>
  <table class="c"><tr><th>Grupo</th><th>Palavras-chave (frase ou exata)</th><th>Destino</th></tr>
  <tr><td><b>1. Cardápio digital</b></td><td class="mono">"cardápio digital", "cardápio digital grátis", "cardápio online para restaurante", "cardápio digital para padaria", "cardápio digital para hamburgueria"</td><td><code>?para=restaurante</code> e as páginas do nicho</td></tr>
  <tr><td><b>2. Pedidos no WhatsApp</b></td><td class="mono">"sistema de pedidos pelo whatsapp", "cardápio com pedido no whatsapp", "receber pedidos pelo whatsapp", "loja online para delivery próprio"</td><td><code>?para=padaria</code></td></tr>
  <tr><td><b>3. Sem comissão</b></td><td class="mono">"delivery sem comissão", "como vender sem pagar comissão de app", "alternativa ao app de delivery", "delivery próprio"</td><td>Página principal</td></tr>
  <tr><td><b>4. Cardápio QR code</b></td><td class="mono">"cardápio qr code", "cardápio digital qr code grátis"</td><td>Página principal</td></tr></table>
  ''' + av("cuidado", "Palavras-chave com marca de concorrente", "<p>Anunciar quando alguém pesquisa o nome de outra marca é permitido pelo Google em geral, mas <b>escrever essa marca no texto do anúncio</b> não é, e a resposta do cliente costuma ser ruim. Comece sem isso e só teste depois, com orçamento separado.</p>") + '</section>')

negativas = "emprego, vaga, vagas, curso, aula, pdf, template, modelo, canva, word, excel, download, gratuito para baixar, wordpress, plugin, programação, código, apk, concurso, receita, cardápio de festa, cardápio semanal, cardápio da semana, cardápio do dia, atendente, motoboy, entregador, trabalhar, salário"
add('<section class="fl"><h3 class="sec" style="margin-top:0">Palavras negativas (comece com estas)</h3>' + msg("Cole na lista de palavras-chave negativas da campanha", negativas) + '''
  <p>Toda semana, abra <b>Palavras-chave › Termos de pesquisa</b> e adicione como negativa tudo que não tenha a ver. É o hábito que mais economiza dinheiro.</p>
  <h3 class="sec">Anúncio responsivo de pesquisa (copiar e colar)</h3>
  <p>O Google combina os títulos e as descrições. Cadastre os 15 títulos (até 30 caracteres) e as 4 descrições (até 90).</p>''' + msg("Títulos (15)", "\n".join(f"{t}  ({len(t)})" for t in g_tit)) + msg("Descrições (4)", "\n".join(f"{d}  ({len(d)})" for d in g_desc)) + '''
  <h3 class="sec">Extensões (grátis, mais cliques)</h3>
  <table class="c"><tr><th>Extensão</th><th>Texto sugerido</th></tr>
  <tr><td><b>Sitelinks</b></td><td>Como funciona · Planos · Calculadora de comissão · Fale conosco</td></tr>
  <tr><td><b>Frases de destaque</b></td><td>Sem comissão · Grátis até R$ 3 mil · Sem cartão de crédito · Pedido no WhatsApp</td></tr>
  <tr><td><b>Snippets estruturados</b></td><td>Tipos: Padaria, Cafeteria, Hamburgueria, Restaurante, Pizzaria, Doceria</td></tr>
  <tr><td><b>Mensagem / ligação</b></td><td>WhatsApp do suporte</td></tr></table>
  <h3 class="sec">Regras de operação</h3>''' + check(
    "<b>Primeiras 2 semanas:</b> só observe e corte termos ruins. Não otimize com poucas conversões.",
    "<b>Palavra-chave com gasto igual ao dobro do valor que você aceita pagar por loja criada e nenhuma conversão:</b> pause.",
    "<b>Nota de qualidade baixa (menos de 5)</b> numa palavra: melhore o anúncio e a página, ou pause.",
    "<b>Confira as políticas</b> do Google Ads (marcas, comparações e promessas) na hora de publicar.") + '</section>')

# ------------------------------------------------------------------ 08 sem gastar
add('<section class="pg">' + cap("08", "Divulgação sem gastar", "No começo, estes canais trazem as primeiras lojas e os primeiros depoimentos, enquanto os anúncios aprendem.") + tabela(["Canal", "O que fazer", "Meta"], [
    ["<b>Perfil da Empresa no Google</b>", "Cadastre a Bistrô Connect como serviço online. Fotos, descrição, link com UTM e pedido de avaliação.", "Aparecer em buscas de marca"],
    ["<b>Seu WhatsApp (status e contatos)</b>", "Poste o post 1 e o 3 no status. Avise contatos que têm negócio de comida.", "5 conversas por semana"],
    ["<b>Prospecção ativa no Instagram</b>", "Siga e interaja com 10 a 15 negócios de comida da região por dia e envie 5 a 10 directs manuais personalizados (script no capítulo 09).", "3 conversas por semana"],
    ["<b>Lojas de demonstração</b>", "Monte uma prévia com o nome e o tipo do negócio do lead, e mande o link. Sem usar fotos dele sem autorização.", "Converter conversa em loja criada"],
    ["<b>Contadores e consultores</b>", "Ofereça comissão ou reciprocidade a contadores, designers e fornecedores que atendem donos de comida.", "2 parceiros no mês"],
    ["<b>Associações e grupos</b>", "Associação comercial, sindicato de bares e restaurantes, grupos de donos de comida no WhatsApp e Facebook. Participe e ajude antes de oferecer.", "1 palestra ou live curta"],
    ["<b>As 3 primeiras lojas “fundadoras”</b>", "Ofereça ajuda grátis na montagem em troca de uma foto da loja e um depoimento autorizado.", "3 depoimentos reais"],
    ["<b>Indicação</b>", "Quem indicar uma loja que ficar ativa ganha, por exemplo, um mês da sua ajuda. Defina a regra por escrito.", "20% das lojas por indicação"],
], "c") + av("cuidado", "Cuidado com mensagem em massa", "<p>Não use programas que disparam mensagens em massa no WhatsApp ou no Instagram: o número é banido e a LGPD exige que o contato tenha como pedir para parar. Envie poucas mensagens, <b>manualmente e personalizadas</b>, e se a pessoa disser “não quero”, anote e não procure mais.</p>") + av("dica", "Depoimentos", "<p>Só publique depoimento real, com nome e autorização por escrito (uma mensagem de WhatsApp serve). Nunca invente prova social: além de antiético, pode violar o Código de Defesa do Consumidor.</p>") + '</section>')

# ------------------------------------------------------------------ 09 scripts
add('<section class="pg">' + cap("09", "Scripts de venda e respostas", "O anúncio traz o contato. Quem converte é a sua conversa.") + msg("Primeira resposta a quem pediu ajuda (em até 5 minutos)", "Oi, {nome}! Aqui é o Adilson, da Bistrô Connect. Recebi o seu pedido para montar a loja da {estabelecimento}. 🙂\nPosso te ajudar agora? Em cerca de 20 minutos deixamos o cardápio no ar, com pedido pelo celular.\nMe conta: hoje você vende mais por Instagram, WhatsApp ou app?") + msg("Primeira mensagem de prospecção (Instagram, manual)", "Oi, {nome}! Vi a {loja} no Instagram, os {produto} estão lindos. 😍\nPergunta rápida: hoje os pedidos chegam todos por aqui, no WhatsApp? Trabalho com cardápio online que organiza o pedido e sem comissão. Se fizer sentido, te mostro em 2 minutos. Se não, sem problema, e sigo torcendo pela {loja}!") + msg("Follow-up (2 dias depois, 1 vez só)", "Oi, {nome}! Só passando para ver se você viu a minha mensagem. Montei uma prévia de como ficaria o cardápio da {loja}: {link}. Dá uma olhada quando puder. 🙂") + '''
  <h3 class="sec">Respostas às objeções mais comuns</h3>''' + tabela(["Objeção", "Resposta"], [
    ["“Já uso o app de delivery”", "Continue no app: ele traz cliente novo. A loja é para o cliente que já conhece você pedir direto, sem comissão. Cada pedido que migra é margem de volta."],
    ["“Meu cliente não vai saber usar”", "Ele já chama você no WhatsApp. A diferença é que vê o cardápio com fotos e manda o pedido pronto em poucos toques. Posso te mostrar numa loja de exemplo agora."],
    ["“Não tenho tempo de montar”", "A gente monta junto em 20 minutos pelo WhatsApp, com o cardápio de exemplo que já vem com fotos."],
    ["“É caro?”", "Começa grátis, sem cartão. Você só paga quando a loja vende mais de R$ 3 mil por mês, e a mensalidade tem teto de R$ 199. Sem comissão por pedido."],
    ["“E se eu não gostar?”", "Sem fidelidade, sem multa. Você cancela quando quiser."],
    ["“Quem recebe o dinheiro?”", "Você, direto do seu cliente (Pix, cartão na entrega ou dinheiro). A Bistrô Connect não fica com nada das suas vendas."],
], "c") + msg("Mensagem de boas-vindas depois que a loja for criada", "Parabéns, {nome}! A {loja} está no ar: {link}. 🎉\nPróximos passos para vender já hoje: 1) Coloque o logo. 2) Ajuste os 3 produtos mais vendidos. 3) Coloque o link na bio do Instagram e no status do WhatsApp. Qualquer dúvida, me chama aqui!") + '</section>')

# ------------------------------------------------------------------ 10 orçamento
add('<section class="pg">' + cap("10", "Orçamento, metas e regras de decisão", "A conta que decide se vale gastar mais ou parar. Os percentuais são hipóteses a validar nos seus primeiros 30 dias.") + '''
  <h3 class="sec">A conta de equilíbrio</h3>
  <p>Gastar em anúncio compensa quando:</p>
  <p style="text-align:center;font:600 12pt 'Poppins';color:var(--navy);margin:10px 0">custo por loja criada ÷ percentual de lojas que compram serviço &le; ticket do serviço</p>
  <p><b>Exemplo ilustrativo (os números são hipóteses suas para testar):</b> se cada loja criada custa R$ 40 em anúncio e 15% das lojas compram uma implantação de R$ 300, cada loja gera, em média, R$ 45 de receita de serviço. Resultado: R$ 5 de margem por loja, ou seja, o anúncio quase se paga, e o ganho real vem das mensalidades futuras, das indicações e dos sites completos. Se o custo por loja criada for R$ 120, o anúncio perde dinheiro nesse formato.</p>
  <h3 class="sec">Três cenários de orçamento por mês</h3>''' + tabela(["Cenário", "Gasto em anúncio", "O que fazer", "O que esperar"], [
    ["<b>Zero</b>", "R$ 0", "Só o capítulo 08, Instagram e Google Business", "As primeiras 3 a 10 lojas e os depoimentos. Mais lento, e quase sem risco."],
    ["<b>Teste</b>", "R$ 600 (R$ 20/dia)", "Metade em Meta (cadastro) e metade em Google (Pesquisa), mais Instagram orgânico", "Dados reais para decidir. Não espere lucro nos primeiros 30 dias."],
    ["<b>Aceleração</b>", "R$ 1.500 (R$ 50/dia)", "Só depois de saber o custo por loja criada e a taxa de compra de serviço", "Volume maior, se os números do teste fecharem a conta."],
], "c") + '''
  <h3 class="sec">Metas dos primeiros 30 dias</h3>''' + tabela(["Métrica", "Meta de partida", "Como medir"], [
    ["Lojas criadas (orgânico + pago)", "10 a 20", "<code>/admin/</code>, coluna Origem"],
    ["Pedidos de ajuda", "5 a 10", "<code>/crm/</code> e WhatsApp"],
    ["Implantações vendidas", "2 a 3", "Seu controle financeiro"],
    ["Depoimentos reais autorizados", "3", "WhatsApp"],
    ["Custo por loja criada (pago)", "Descobrir o número real", "Gasto ÷ lojas da origem paga"],
], "c") + '''
  <h3 class="sec">Painel semanal (preencha toda segunda-feira)</h3>''' + tabela(["Semana", "Gasto", "Cliques", "Cadastros", "Lojas criadas", "Custo por loja", "Ajudas pedidas", "Vendas"], [["1", "", "", "", "", "", "", ""], ["2", "", "", "", "", "", "", ""], ["3", "", "", "", "", "", "", ""], ["4", "", "", "", "", "", "", ""]], "c") + '''
  <h3 class="sec">Regras de decisão</h3>''' + check(
    "<b>Depois de 14 dias e R$ 300 de gasto sem nenhuma loja criada:</b> pare, revise a página, a mensagem e o público antes de gastar mais.",
    "<b>Custo por loja criada acima do limite que você definiu:</b> não aumente o orçamento. Troque o criativo, a página ou o público.",
    "<b>Custo dentro do limite por 2 semanas seguidas:</b> aumente o orçamento em 20%, e repita a cada 3 dias.",
    "<b>Lojas criadas, mas poucas ativas:</b> o problema é a ativação (primeiros passos), não o anúncio. Melhore o acompanhamento no WhatsApp.",
    "<b>Muitos pedidos de ajuda e pouca venda:</b> ajuste o preço, o script ou a oferta do serviço.") + '</section>')

# ------------------------------------------------------------------ 11 roteiro 90 dias
add('<section class="pg">' + cap("11", "Roteiro de 90 dias e rotina semanal", "O que fazer em cada fase, sem pular etapas.") + tabela(["Fase", "Semanas", "O que fazer", "Saída da fase"], [
    ["<b>0 · Preparar</b>", "Semana 0", "Capítulo 01 inteiro: contas, medição, config.js, SMTP e teste completo", "Tudo medindo e funcionando"],
    ["<b>1 · Base orgânica</b>", "1 a 2", "Perfil do Instagram, 6 posts do kit, destaques, Google Business, WhatsApp. 10 conversas de prospecção por semana.", "Perfil com 9 posts e 5 conversas"],
    ["<b>2 · Primeiros clientes</b>", "3 a 4", "Convidar 3 lojas fundadoras, atender os leads, coletar depoimentos e fazer 2 Reels de produto", "3 lojas ativas e 3 depoimentos"],
    ["<b>3 · Teste pago</b>", "5 a 6", "Ligar Meta (cadastro) e Google (Pesquisa) com R$ 20 por dia cada, sem mexer por 4 dias", "Custo por cadastro e por loja criada conhecido"],
    ["<b>4 · Otimizar</b>", "7 a 8", "Cortar o que não converte, acrescentar negativas, trocar criativos, ligar o remarketing", "Custo por loja criada em queda"],
    ["<b>5 · Decidir</b>", "9 a 10", "Aplicar a conta de equilíbrio. Se fechar, aumentar 20% por vez. Se não, voltar à base orgânica e ao serviço.", "Decisão de investir ou não"],
    ["<b>6 · Escalar com controle</b>", "11 a 13", "Novos nichos e cidades, nova rodada de criativos, programa de indicação, Supabase Pro e cobrança organizada", "Rotina estável e previsível"],
], "c") + '''
  <h3 class="sec">Sua semana de trabalho</h3>''' + tabela(["Dia", "O que fazer", "Tempo"], [
    ["<b>Segunda</b>", "Preencher o painel semanal, rever anúncios, responder o que sobrou do fim de semana", "45 min"],
    ["<b>Terça a quinta</b>", "Postar, responder comentários e directs, prospectar 5 a 10 negócios, atender leads", "40 min por dia"],
    ["<b>Sexta</b>", "Termos de pesquisa do Google (negativas), enviar cobranças do mês, planejar a semana seguinte", "45 min"],
    ["<b>Todo dia</b>", "Responder lead em até 5 minutos, em horário comercial", "—"],
], "c") + av("ok", "O que decide o resultado", "<p>Três coisas: <b>a oferta</b> (sem comissão, grátis até R$ 3 mil), <b>a velocidade de resposta</b> ao lead e <b>a prova</b> (lojas reais e depoimentos). O anúncio só amplifica o que já funciona.</p>") + '</section>')

# ------------------------------------------------------------------ 12 lista
add('<section class="pg">' + cap("12", "Lista de lançamento", "Marque tudo antes de ligar o primeiro anúncio.") + check(
    "Pacote de atualização no ar, com a imagem de prévia do link funcionando (teste colando o link no WhatsApp).",
    "SQL <code>02-admin-por-mes</code> rodado e SMTP funcionando.",
    "<code>config.js</code> com WhatsApp, empresa, Pixel, Google Ads (ID e 2 rótulos), Analytics e CRM.",
    "Instagram profissional criado: nome, foto, bio, link com UTM e destaques.",
    "6 posts do kit publicados e 2 Reels no ar.",
    "Pixel da Meta e domínio verificados, e eventos conferidos no Pixel Helper.",
    "Conversões “Loja criada” e “Pedido de ajuda” criadas no Google Ads e conferidas no Tag Assistant.",
    "Campanha Meta de cadastro e campanha de Mensagens criadas, com 3 textos e 4 criativos.",
    "Campanha de Pesquisa no Google com 4 grupos, negativas e anúncio responsivo.",
    "Percentual do app de delivery conferido, com fonte e data anotadas.",
    "Roteiro de teste do guia feito até o fim.",
    "Perfil da Empresa no Google criado.",
    "Planilha ou painel semanal pronto, com o limite de custo por loja criada definido.",
    "WhatsApp Business com saudação, ausência e etiquetas.",
    "Scripts de atendimento do capítulo 09 salvos como respostas rápidas.") + av("ok", "Pronto para ligar", "<p>Com a lista toda marcada, ligue as campanhas com o orçamento do cenário <b>Teste</b>, não mexa por 4 dias e siga a rotina semanal. Me mande os números da primeira semana que eu te ajudo a ler.</p>") + '</section>')

P = [x if ('class="cap"' in x or "capa" in x[:40]) else x.replace('<section class="pg">', '<section class="fl">', 1) for x in P]
html = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Plano de divulgação · Bistrô Connect</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&family=DM+Mono:wght@400;500&display=swap">
<style>{css}</style>
</head>
<body>
{chr(10).join(P)}
</body>
</html>'''
open(os.path.join(RAIZ, "manual/plano-de-divulgacao.html"), "w", encoding="utf-8").write(html)
print("manual/plano-de-divulgacao.html gerado:", len(html) // 1024, "KB")
