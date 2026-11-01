# Manual de Operação BistrôConnect

## 1. Visão geral

A BistrôConnect vende presença digital para restaurantes: site com a marca da casa, cardápio digital, pedido direto no WhatsApp sem comissão, rastreio do pedido e painel de gestão. Este manual é o roteiro de quem vende, implanta e atende, do primeiro contato ao cliente rodando. Quem chega na equipe lê as seções 1 a 3 e depois a seção da sua função.

### O que vendemos

| Plano | Implantação | Mensalidade | Para quem | O que entra |
| --- | --- | --- | --- | --- |
| Cardápio Digital | R$ 997 | a partir de R$ 149 | Quem só precisa do cardápio, sem site | Cardápio interativo e pedido enviado ao WhatsApp |
| Site Gastronômico | R$ 1.497 | R$ 149 | Restaurante que quer site próprio | Modelo gastronômico com a identidade da casa, cardápio com pedido, domínio próprio com HTTPS, QR Code e link para as redes |
| Digital Experience | R$ 2.997 | R$ 199 | Quem quer canal próprio completo | Tudo do Site Gastronômico + painel de pedidos e rastreio, perfil no Google otimizado, 500 cartões de volta e display de balcão, campanha de lançamento, 30 dias de acompanhamento |
| Signature | sob orçamento | sob orçamento | Marcas que exigem exclusividade | Projeto criado do zero: direção criativa, design, navegação e integrações próprias |

Valores de referência da página de vendas (bistroconnect.com.br/sites-personalizados). A mensalidade cobre hospedagem, uso do sistema e do painel, suporte no WhatsApp e ajustes de conteúdo e banners de datas comemorativas.

**Foco agora:** Site Gastronômico e Digital Experience, que têm o maior valor e geram caixa mais rápido. O Cardápio Digital avulso fica em segundo plano.

### Como a tecnologia funciona, em uma frase

Cada cliente tem o próprio site no domínio dele, mas cardápio, pedidos, rastreio e painel rodam num **motor único**: um só banco de dados (Supabase) para todos os clientes, cada loja vendo apenas os próprios dados. O dono muda o cardápio no painel e o site mostra na hora; o pedido feito no site entra no painel e o cliente acompanha pelo link de rastreio.

## 2. Papéis da equipe

Hoje o Adilson faz tudo. A ordem de contratação sugerida é: primeiro **Implantação** (libera o Adilson para vender), depois **Comercial**, depois **Suporte** quando houver mais de 20 clientes ativos.

| Função | Faz | Não faz | Perfil | Seções deste manual |
| --- | --- | --- | --- | --- |
| Gestão (Adilson) | Define preço e oferta, aprova propostas e contratos, cuida do dinheiro, das senhas mestras e do motor | Produção do dia a dia, depois que houver equipe | Dono | Todas |
| Comercial | Prospecta, atende leads no CRM, faz o diagnóstico, apresenta demonstrações, envia proposta e fecha | Promete prazo ou recurso que não está neste manual; dá desconto sem aprovação | Comunicação boa, conhece restaurante | 1, 5, 6 |
| Implantação | Recebe o briefing, monta o cardápio no painel, gera o site, publica, testa e treina o cliente | Mexe no código dos modelos ou no banco | Organizado, detalhista, básico de Hostinger | 3, 6, 7, 8, 9, 10 |
| Suporte | Atende os clientes no WhatsApp, faz ajustes de conteúdo e banners, resolve os problemas comuns | Alterações de código; fica com a senha de um cliente | Paciente, responde rápido | 10, 11 |
| Desenvolvimento (sob demanda) | Novos modelos, mudanças no motor e no painel, projetos Signature | Atendimento ao cliente | Freelancer ou parceiro técnico | 4, 7 e o repositório |

**Regra de ouro para todos:** só prometa o que está construído. Se o cliente pedir algo que não está neste manual, anote e leve para a Gestão antes de responder.

## 3. Ferramentas, acessos e segurança

Cada pessoa tem o próprio login em cada ferramenta. Nunca compartilhe senha nem use a conta de outra pessoa.

| Ferramenta | Para quê | Quem acessa |
| --- | --- | --- |
| CRM de sites (`/sites-personalizados/crm/`) | Leads, propostas, funil, scripts, objeções e materiais | Gestão, Comercial |
| Plataforma (`entrar.html`, `admin/`) | Criar a loja de cada cliente, convidar o dono, ver todas as lojas | Gestão, Implantação |
| Painel da loja (`/admin/` no site do cliente) | Cardápio, pedidos, bairros, pagamentos, cupons, mesas, equipe | Cliente; Implantação e Suporte quando convidados |
| Hostinger | Hospedagem e domínio dos sites | Gestão; Implantação com acesso de colaborador |
| Supabase | Banco do motor (todas as lojas) | Só Gestão e Desenvolvimento |
| GitHub (repositório Command-AI) | Código dos modelos, do motor e do gerador | Gestão, Desenvolvimento, Implantação (só para gerar) |
| WhatsApp Business da BistrôConnect | Comercial e suporte | Comercial, Suporte |

### Regras de segurança

1. A **chave service_role** do Supabase nunca sai do painel do Supabase: não vai em site, arquivo, e-mail nem conversa. Nos sites só vai a chave **anon** (pública).
2. Nunca sobrescreva o `assets/config.js` de um site que já está no ar sem antes baixar uma cópia dele.
3. Senhas e tokens não são enviados por WhatsApp nem e-mail. O cliente cria a própria senha pelo convite do painel.
4. Ative a verificação em duas etapas no Supabase, na Hostinger, no GitHub e no painel.
5. Fotos de terceiros só aparecem em demonstração. No site do cliente, só fotos dele ou com licença.
6. Depoimentos e números ("4,9 de nota", "35 min") só se forem reais e comprováveis. Senão, esconda o bloco.
7. Quem sai da equipe perde todos os acessos no mesmo dia.

## 4. Montar a base (uma vez só)

Antes do primeiro cliente, o motor precisa estar no ar. Responsável: Gestão, com apoio do Desenvolvimento. O detalhe técnico de cada passo está em `plataforma/LEIA-ME.md` no repositório.

1. **Supabase da plataforma.** Crie o projeto em supabase.com e rode, no SQL Editor, os arquivos de `plataforma/supabase/` em ordem numérica (01 a 14). Em Authentication, deixe a confirmação de e-mail ligada e configure a Site URL e as Redirect URLs com o endereço da plataforma.
2. **Hospedagem da plataforma.** Na Hostinger, crie o subdomínio `app.bistroconnect.com.br`, envie o conteúdo da pasta `plataforma/` (sem a pasta `supabase/`) e ative o SSL. Preencha `assets/config.js` com a URL e a chave anon.
3. **Sua conta de administrador.** Crie sua conta pelo `entrar.html` e torne-se administrador da plataforma com o comando SQL do LEIA-ME.
4. **Motor para o gerador.** No repositório, copie `clientes/motor.exemplo.json` para `clientes/motor.json` e preencha `supabaseUrl`, `supabaseKey` (anon) e `plataforma` (o endereço do app). Esse arquivo não vai para o Git.
5. **Teste do motor.** Gere e publique o pacote de teste ligado à loja "padaria" (`public_html/teste-motor/`) e faça um pedido de ponta a ponta: site, WhatsApp, painel, rastreio. Depois apague a pasta.
6. **CRM.** Rode `plataforma/supabase/03-crm.sql` (se ainda não rodou) e entre no CRM.
7. **WhatsApp integrado ao painel (quando houver CNPJ).** Siga `plataforma/supabase/functions/LEIA-ME-WHATSAPP.md`: app na Meta, as duas funções no Supabase e o webhook. Sem isso, o pedido continua chegando pelo WhatsApp comum, o que já funciona.

**Custo fixo:** um projeto Supabase para todos os clientes (gratuito no começo; plano pago quando crescer) + a hospedagem da Hostinger. Não há custo por cliente no banco.

## 5. Venda: do contato ao contrato

Toda venda passa pelo CRM: lead sem registro é lead perdido. Responsável: Comercial. Os textos prontos estão na aba Scripts e as respostas às objeções na aba Objeções.

1. **Lead chega** pelo formulário da página de vendas, pelo WhatsApp ou por indicação. Registre no CRM no mesmo dia, com a origem.
2. **Primeiro contato em até 2 horas úteis.** Pergunte o tipo de casa, se já vende por aplicativo, quanto paga de comissão e o que mais incomoda hoje.
3. **Diagnóstico (15 a 20 minutos, vídeo ou presencial).** Entenda: cardápio, delivery ou retirada, bairros atendidos, volume de pedidos, identidade visual, domínio, redes. Use a calculadora da página para mostrar a comissão que ele paga hoje.
4. **Demonstração.** Abra a demonstração do tipo da casa (restaurante, hamburgueria, cafeteria ou pizzaria) e faça um pedido de teste junto com ele. Mostre o rastreio e o painel.
5. **Indique o plano.** Só cardápio → Cardápio Digital. Quer site → Site Gastronômico. Quer tirar pedidos do aplicativo e crescer o canal próprio → Digital Experience. Marca que exige exclusividade → Signature (passa para a Gestão orçar).
6. **Proposta por escrito** (gerada no CRM, aba Orçamentos), com plano, valores, prazo e condições. Validade de 7 dias.
7. **Aceite e pagamento da 1ª parte.** Só depois do aceite e do pagamento a implantação começa. Mova o lead para "Fechado" e passe para a Implantação com o briefing (seção 6).

### Condições comerciais

- Implantação: 50% no Pix no aceite e 50% na entrega, ou parcelada no cartão.
- Mensalidade: começa só depois que o site vai ao ar.
- Contrato mínimo de 6 meses de mensalidade; depois, cancelamento quando quiser.
- Prazo: até 7 dias úteis, contados a partir do recebimento de todos os materiais (logo, fotos, cardápio) e das aprovações.
- Os valores são de referência e podem ser atualizados. Desconto só com aprovação da Gestão.

### O que não dizer

- "Grátis" (não há nada grátis na oferta).
- Promessa de resultado de vendas ou de posição no Google.
- WhatsApp com robô e caixa de entrada no painel, enquanto essa parte não estiver ligada (depende do CNPJ e da aprovação da Meta).
- Prazo menor que 7 dias úteis ou recurso que não está neste manual.

## 6. Briefing e materiais do cliente

O prazo de 7 dias úteis só começa quando tudo abaixo chegou. Envie esta lista ao cliente no dia do aceite (script "Pedido de materiais") e cobre o que faltar no 2º dia. Responsável: Implantação.

### O que pedir

- [ ] Nome da casa como deve aparecer, e o endereço curto desejado (vira o slug, ex.: `forno-do-ze`)
- [ ] Logo em PNG com fundo transparente ou SVG
- [ ] Cores da marca (se não tiver, usamos as do modelo)
- [ ] Fotos: fachada ou salão, 3 a 5 pratos de destaque e foto de cada produto do cardápio
- [ ] Cardápio em planilha: categoria, nome, descrição, preço, unidade, opcionais com preço de cada um
- [ ] WhatsApp que recebe os pedidos
- [ ] Endereço, horário de funcionamento e Instagram
- [ ] Entrega: bairros atendidos e taxa de cada um (ou taxa única) e pedido mínimo
- [ ] Retirada no balcão: sim ou não
- [ ] Formas de pagamento aceitas
- [ ] Domínio: se já tem, acesso ao painel do domínio; se não, o nome desejado
- [ ] Textos: uma frase sobre a casa e o diferencial
- [ ] Depoimentos reais com autorização (opcional)
- [ ] E-mail do dono para o convite do painel

### Como transformar em configuração

Copie `clientes/exemplo-briefing.json` para `clientes/<slug>.json` e preencha: nome, modelo, slug, WhatsApp, domínio, cores, logo, textos, fotos e contato. Campo vazio = texto ou foto do modelo. A lista de textos de cada modelo está em `clientes/LEIA-ME.md`. O cardápio, os bairros e os pagamentos vão no painel (seção 7).

## 7. Produção do Site Gastronômico

Com os materiais em mãos, um site sai em 1 a 3 dias de trabalho, sem editar código. Responsável: Implantação.

| Dia útil | Etapa |
| --- | --- |
| 1 | Loja criada no motor, cardápio cadastrado, site gerado |
| 2 | Prévia enviada ao cliente, ajustes |
| 3 a 5 | Domínio, publicação e teste de aceite |
| até 7 | Treinamento e entrega formal |

### Passo a passo

1. **Escolha o modelo** pelo tipo da casa: `hamburgueria` (Bruto, pronto), `pizzaria` (Fornalha), `restaurante` (Âmbar) e `padaria` (Padaria e Café), estes três em adaptação.
2. **Crie a loja no motor.** Em `app.bistroconnect.com.br/entrar.html`, entre com a conta da BistrôConnect e crie a loja com o mesmo slug do briefing.
3. **Cadastre no painel da loja:** cardápio (categorias, produtos, fotos, opcionais), dados da loja, entrega (taxa única ou por bairro, pedido mínimo), retirada e formas de pagamento. Categorias com "Acompanhamentos", "Bebidas", "Porções" ou "Extras" no nome vão para a lista lateral; "Combos" vai para o bloco de combos; produtos em destaque vão para "Os mais pedidos".
4. **Preencha o JSON do cliente** (seção 6) e coloque as fotos de marca (logo, capa, fachada) numa pasta.
5. **Gere o site** no repositório: `python3 ferramentas/novo-cliente.py --dados clientes/forno-do-ze.json --fotos pasta-das-fotos`. Sai `entregas/forno-do-ze/site/` e `entregas/forno-do-ze.zip`, com o site, o rastreio (`/p/código`) e o painel em `/admin/`.
6. **Revise** abrindo o `index.html` gerado: nome, logo, cores, textos, fotos, cardápio. Confira no celular.
7. **Prévia ao cliente.** Publique numa pasta de prévia (gere com `--caminho /previa-forno/`) e mande o link. Anote os ajustes, corrija no JSON ou no painel e gere de novo.

**Nunca** edite o `index.html` de um cliente à mão: a próxima geração apaga a edição. Se precisar de algo que o JSON não permite, peça ao Desenvolvimento para incluir no modelo.

## 8. Outros planos

### Digital Experience: o que entra além do site

1. **Painel e rastreio para o dono.** Convide o dono no painel (Equipe › Convidar pessoa) e, se ele quiser, os funcionários. Ative os avisos de pedido novo no computador do balcão e o som.
2. **Perfil da empresa no Google.** Categoria certa, horários, endereço, telefone, 10 fotos ou mais, link do site e de pedido, produtos de destaque e resposta às avaliações.
3. **500 cartões de volta e display de balcão.** No painel, crie o cupom de volta e gere os cartões com QR. Envie o arquivo à gráfica e imprima o display de balcão com o QR do cardápio.
4. **Campanha de lançamento.** Posts e stories avisando que a casa tem site e pedido direto, adaptados à casa. O dono publica; nós preparamos.
5. **30 dias de acompanhamento.** Contato nos dias 1, 7, 15 e 30 (seção 10).

### Cardápio Digital

Usa a plataforma, sem site próprio. Crie a loja em `entrar.html`, cadastre o cardápio no painel e entregue o link `app.bistroconnect.com.br/l/<slug>` e o QR para as mesas e o Instagram. Não usa o gerador.

### Signature

Projeto criado do zero, orçado pela Gestão depois do diagnóstico, com prazo e valor individuais: imersão e estratégia; direção criativa e arquitetura; design e desenvolvimento; refinamento e publicação. Se tiver pedido, também usa o motor.

## 9. Publicação, teste de aceite e entrega

O site só é entregue depois de passar em todos os itens abaixo, no celular e no computador. Responsável: Implantação.

### Publicar

1. Na Hostinger, aponte o domínio e ative o SSL.
2. Envie o conteúdo do zip para a `public_html`. Confira que o arquivo `.htaccess` subiu (ele é oculto).
3. Confirme que o PHP está ativo no domínio: o link curto do rastreio depende dele.

### Teste de aceite

- [ ] O site abre com `https://` e cadeado, no celular e no computador
- [ ] Nome, logo, cores e textos são os do cliente; nenhum texto do modelo sobrou
- [ ] Cardápio, preços e fotos batem com o painel
- [ ] Pedido de teste com entrega: bairro e taxa certos, opcionais pedidos, total certo
- [ ] O WhatsApp abre com o resumo, o número do pedido e o link de acompanhamento
- [ ] O pedido aparece no painel com aviso sonoro
- [ ] Mudar o status no painel muda a página de acompanhamento
- [ ] Pedido de teste com retirada e outra forma de pagamento
- [ ] Mudar um preço no painel e ver o novo preço no site
- [ ] Endereço, horário, Instagram e WhatsApp certos no rodapé
- [ ] Pedidos de teste excluídos ou cancelados no painel

### Entrega formal

Envie ao cliente o termo de entrega com: endereço do site, endereço do painel, o que foi entregue (conforme o plano), data de início da mensalidade e o canal de suporte. Com o aceite, cobre a 2ª parte da implantação e mova o cliente para "Cliente ativo" no CRM.

## 10. Treinamento e pós-venda

O cliente que aprende a usar o painel na primeira semana tende a ficar; por isso o treinamento e o dia 7 não são opcionais. Responsável: Implantação até o dia 7, depois Suporte.

### Treinamento (30 a 40 minutos, no dia da entrega)

1. Entrar no painel pelo convite e criar a senha.
2. Receber um pedido: aviso, aceitar, mudar status até entregue, imprimir a comanda.
3. Pausar e reabrir os pedidos.
4. Mudar preço, desativar um produto esgotado, incluir um produto com foto.
5. Ver o financeiro do dia e a lista de clientes.
6. Onde pedir ajuda: o WhatsApp de suporte da BistrôConnect.

### Contatos de acompanhamento

| Quando | O que fazer |
| --- | --- |
| Dia 1 | Confirmar que os primeiros pedidos chegaram e que a equipe sabe aceitar |
| Dia 7 | Ver no painel quantos pedidos entraram; ajustar cardápio e fotos; tirar dúvidas |
| Dia 15 (Digital Experience) | Conferir cartões de volta e perfil no Google; sugerir posts |
| Dia 30 | Conversa de resultado: pedidos pelo canal próprio e comissão evitada; pedir depoimento e indicação |
| Todo mês | Banner de data comemorativa e ajustes de conteúdo incluídos na mensalidade |

## 11. Suporte: problemas comuns

Responda no WhatsApp em até 1 hora útil; pedido parado é prioridade máxima. Responsável: Suporte.

| O cliente diz | Causa mais provável | O que fazer |
| --- | --- | --- |
| "O site mostra o cardápio de exemplo" | `assets/config.js` sem a URL, a chave ou o slug certo | Conferir os 3 valores; gerar de novo se preciso |
| "O pedido não chega no painel" | Pedidos pausados, loja suspensa ou internet | Ver em Dados da loja se aceita pedidos; ver a situação da loja no admin |
| "Não toca o aviso de pedido" | Som desligado ou aba fechada | Ligar o som e os avisos; manter o painel aberto no balcão |
| "O cliente diz que o preço mudou" | Preço alterado enquanto ele montava o pedido | Normal: o site avisa e mostra o total novo |
| "Pede para escolher o bairro" | Taxa por bairro ligada e bairro faltando | Incluir o bairro em Dados da loja |
| "O link de acompanhamento não abre" | PHP desligado ou `.htaccess` não subiu | Ativar o PHP e reenviar o `.htaccess` |
| "Esqueci a senha" | — | "Esqueci a senha" na tela de entrada; nunca envie senha |
| "Quero mudar texto, foto ou cor" | Ajuste de conteúdo (incluso) | Mudar no JSON do cliente, gerar e publicar de novo |
| "O site sumiu ou dá erro" | Hospedagem, domínio ou SSL vencidos | Ver na Hostinger; avisar a Gestão |
| Nenhum site carrega cardápio | Supabase pausado ou fora do ar | Avisar a Gestão na hora; reativar o projeto |

O que não for resolvido em 24 horas sobe para a Gestão, com print e o endereço do site.

## 12. Rotinas, indicadores e o que falta

### Rotinas

| Quando | O quê | Quem |
| --- | --- | --- |
| Todo dia | Responder leads novos e mensagens de suporte; conferir pedido parado | Comercial, Suporte |
| Toda segunda | Reunião de 30 min: funil do CRM, implantações e prazos, pendências | Todos |
| Todo mês | Cobrar mensalidades, banners de datas, indicadores, vencimentos de hospedagem e domínio | Gestão, Suporte |
| Antes de cada atualização do motor | Testar no pacote `teste-motor` antes de gerar os clientes de novo | Desenvolvimento |

### Indicadores

- Leads por semana e por origem
- Taxa de fechamento (propostas aceitas ÷ propostas enviadas)
- Tempo do aceite até o site no ar (meta: 7 dias úteis)
- Clientes ativos e receita mensal recorrente
- Cancelamentos no mês
- Pedidos por cliente no mês

### Decisões em aberto

- No Site Gastronômico, o dono recebe acesso ao painel ou a equipe mantém o cardápio por ele?
- O domínio e a hospedagem ficam no nome do cliente ou na conta da BistrôConnect?
- Modelo de contrato e de termo de aceite revisados por advogado.
- Qual oferta vale nos materiais antigos (Casa Cheia, Loja no Ar, garantia de 30 pedidos): manter ou aposentar?
