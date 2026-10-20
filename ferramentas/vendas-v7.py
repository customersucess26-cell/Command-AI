"""Página de vendas v7: modo convite. Sem "grátis" em destaque e sem cadastro aberto na vitrine de vendas.
Todos os botões "Criar minha loja" passam a levar ao formulário "Quero ajuda para montar" (#contato), que cai no CRM.
A página entrar.html continua existindo (noindex, fora do sitemap), mas só quem recebe o link usa.
Uso: python3 ferramentas/vendas-v7.py && python3 ferramentas/csp.py plataforma/index.html
Pode rodar de novo: não duplica nada."""
ARQ = "plataforma/index.html"
MARCA = "<!-- v7: modo convite -->"
s = open(ARQ, encoding="utf-8").read()
if MARCA in s:
    raise SystemExit("plataforma/index.html já está na v7")


def troca(velho, novo, vezes=1):
    global s
    n = s.count(velho)
    assert n == vezes, "esperava %d de %r, achei %d" % (vezes, velho[:70], n)
    s = s.replace(velho, novo)


# metas
troca('content="Crie grátis a loja online da sua padaria, café, hamburgueria ou restaurante: cardápio com fotos, pedido pronto no WhatsApp, rastreio para o cliente e painel completo. Sem comissão por pedido."',
      'content="Loja online para a sua padaria, café, hamburgueria ou restaurante: cardápio com fotos, pedido pronto no WhatsApp, rastreio para o cliente e painel completo. Sem comissão por pedido."')
troca('content="Cardápio digital, pedido no WhatsApp e painel. Grátis até R$ 3 mil em vendas por mês, sem comissão por pedido."',
      'content="Cardápio digital, pedido no WhatsApp e painel completo. Sem comissão por pedido."')

# topo, hero, dor, comece, fixo
troca('<a class="btn btn-mint" href="/entrar.html" data-track="cta-topo">Criar minha loja grátis</a>',
      '<a class="btn btn-mint" href="#contato" data-track="cta-topo">Quero uma demonstração</a>')
troca('<a class="btn btn-mint" href="/entrar.html" data-track="cta-hero">Quero vender sem comissão</a>',
      '<a class="btn btn-mint" href="#contato" data-track="cta-hero">Quero vender sem comissão</a>')
troca('<span>✓ Grátis até R$ 3 mil por mês</span><span>✓ Sem cartão de crédito</span><span>✓ Sem fidelidade</span>',
      '<span>✓ Montamos com você</span><span>✓ Sem comissão por pedido</span><span>✓ Sem fidelidade</span>')
troca('<a class="btn btn-mint brilho-v6" href="/entrar.html" data-track="cta-dor">',
      '<a class="btn btn-mint brilho-v6" href="#contato" data-track="cta-dor">')
troca('<td class="us">Grátis até R$ 3 mil, com teto</td>', '<td class="us">Mensalidade fixa, com teto</td>')
troca('<h2 style="margin-top:12px">Se a sua loja não vender, você não paga.</h2>',
      '<h2 style="margin-top:12px">Sem comissão, sem fidelidade, sem multa.</h2>')
troca('<p class="eyebrow">Risco zero</p>', '<p class="eyebrow">Sem amarras</p>')
troca('O plano Começo é grátis até R$ 3 mil em vendas por mês. Sem cartão de crédito, sem taxa de implantação e sem fidelidade. Você testa com os seus clientes de verdade e decide depois.',
      'Você começa com a ajuda da nossa equipe, sem fidelidade e sem multa. Testa com os seus clientes de verdade e decide depois.')
troca('<span class="tag">Sem cartão de crédito</span>', '<span class="tag">Vagas limitadas</span>')
troca('<h3 style="font-size:24px;position:relative">Sua loja no ar em minutos</h3>',
      '<h3 style="font-size:24px;position:relative">Sua loja no ar, montada com você</h3>')
troca('<li>Cadastro sozinho, sem esperar ninguém</li>', '<li>Cadastro feito com a ajuda da nossa equipe</li>')
troca('<a class="btn btn-mint" href="/entrar.html" style="position:relative;align-self:flex-start" data-track="cta-comece">Criar minha loja grátis</a>',
      '<a class="btn btn-mint" href="#contato" style="position:relative;align-self:flex-start" data-track="cta-comece">Pedir minha vaga</a>')

# planos
troca('<p class="price" style="color:var(--mint)">Grátis</p>', '<p class="price" style="color:var(--mint)">Convite</p>')
troca('<p class="faixa">Vendas de até R$ 3 mil por mês</p>', '<p class="faixa">Vendas de até R$ 3 mil por mês · vagas limitadas</p>')
troca('<a class="btn btn-mint" href="/entrar.html">Criar minha loja</a>', '<a class="btn btn-mint" href="#contato">Pedir minha vaga</a>')
troca('<a class="btn btn-ghost" href="/entrar.html">Criar minha loja</a>', '<a class="btn btn-ghost" href="#contato">Quero este plano</a>', 3)

# perguntas, contato, rodapé, botão fixo
troca(' E enquanto vender até R$ 3 mil por mês, não paga nada.', '')
troca('<a class="btn btn-ghost-claro" href="/entrar.html">Ou criar a loja agora</a>',
      '<a class="btn btn-ghost-claro" href="#contato">Ou pedir uma demonstração</a>')
troca('Ou você pode começar hoje a trazer os seus clientes para o seu próprio cardápio. Leva 5 minutos e é grátis. Prefere ajuda? Mande seus dados ao lado que a gente monta com você pelo WhatsApp.',
      'Ou você pode começar a trazer os seus clientes para o seu próprio cardápio. Mande seus dados ao lado e a gente monta a sua loja com você pelo WhatsApp.')
troca('<a class="btn btn-mint" href="/entrar.html" data-track="cta-final">Criar minha loja grátis agora</a>',
      '<a class="btn btn-mint" href="#leadForm" data-track="cta-final">Quero minha demonstração</a>')
troca('Grátis e sem compromisso. A conversa continua no WhatsApp.', 'Sem compromisso. A conversa continua no WhatsApp.')
troca('<a href="/entrar.html">Criar loja grátis</a>', '<a href="#contato">Pedir demonstração</a>')
troca('<a class="btn btn-mint" href="/entrar.html" data-track="cta-fixo">Criar minha loja grátis</a>',
      '<a class="btn btn-mint" href="#contato" data-track="cta-fixo">Quero uma demonstração</a>')

# assistente Bia e calculadora
troca("Quer criar a sua loja agora? É grátis para começar.',[{t:'Criar minha loja',fn:function(){location.href='/entrar.html'}}",
      "Quer ver uma demonstração e montar a sua?',[{t:'Quero uma demonstração',fn:function(){startLead()}}")
troca("if(/criar|cadastr/.test(norm(history.length?history[history.length-1].content:''))){location.href='/entrar.html';return}", "")
troca("• Até R$ 3 mil/mês: grátis\\n", "• Até R$ 3 mil/mês: faixa de entrada (fale com a gente sobre as condições de lançamento)\\n")
troca("A mensalidade vai de grátis a no máximo R$ 199", "A mensalidade tem teto de R$ 199")
troca("'Nessa faixa de vendas diretas a Bistrô Connect é grátis.'", "'Nessa faixa de vendas diretas a mensalidade da Bistrô Connect é a da faixa de entrada.'")

s = s.replace("</body>", MARCA + "\n</body>", 1)
open(ARQ, "w", encoding="utf-8").write(s)
print("v7 aplicada em", ARQ)
