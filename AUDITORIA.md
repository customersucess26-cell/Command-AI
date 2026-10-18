# eBistrô: auditoria e correções (18/10/2026)

> Atualização: a hamburgueria e o Âmbar mudaram de `modelos/` para `sites/hamburgueria-bruto/` e `sites/ambar/`, cada um com painel próprio (ver SEGURANCA.md). O painel do eBistrô foi refeito a partir do painel original, que está guardado em `historico/painel-original.html`.
> O modelo padaria foi trocado pela versão 17 do projeto (enviada depois): ela já valida pedidos com o fuso de São Paulo, impede pedido duplicado, confere mudança de preço, controla status, pagamentos parciais e estornos, e protege o CSV. Nela foram feitas só duas correções: a tela final no modo demonstração e o login de demonstração sem e-mail pessoal. A versão 16 corrigida e as originais estão em `historico/`.

## O que foi auditado

Os 4 arquivos enviados nesta sessão, salvos sem alteração no primeiro commit (`393cc87`), para que dê para comparar e recuperar o original:

| Arquivo no repositório | Arquivo enviado | O que é |
|---|---|---|
| `index.html` | `index_4.html` | Landing de vendas do eBistrô (planos, calculadora, chat Bia, formulário de lead) |
| `modelos/padaria-cafe.html` | `template-padaria-cafe.html` | Modelo de site com cardápio, encomendas e painel admin (React compilado) |
| `modelos/hamburgueria-bruto.html` | `hamburgueria-bruto_1.html` | Modelo de site com cardápio e pedido pelo WhatsApp |
| `modelos/ambar.html` | `ambar-index.html` | Modelo de site vitrine de restaurante (sem pedido) |

### Limitações importantes

1. **O histórico anterior do projeto não está nesta conversa.** A sessão começou com o repositório vazio. A auditoria se baseou só nos arquivos acima.
2. **O código-fonte do painel não veio.** `padaria-cafe.html` é um build de demonstração de um projeto Next.js + Supabase (há chamadas a `/api/admin/users`, `/api/admin/bootstrap` e `process.env.NEXT_PUBLIC_*`). Nesse build o Supabase está desligado e **tudo fica no `localStorage` do navegador de quem abre**. As correções foram feitas direto no JavaScript compilado, em trechos pequenos e verificados. A correção definitiva precisa ser repetida no código-fonte (`src/`), que não está aqui.
3. **`assets/config.js` e a pasta `admin/` não vieram.** O `config.js` foi criado como modelo com os campos vazios. O link "Acesso restrito" (`admin/`) continua apontando para uma pasta que não existe neste repositório.

## Diagnóstico

Prioridades: **P0** = crítico, perda de dados ou segurança; **P1** = função essencial quebrada; **P2** = incompleto ou inconsistente; **P3** = usabilidade e acabamento.

### Modelo padaria/café (`modelos/padaria-cafe.html`)

| Área | Estado | Problema | Correção | Prioridade |
|---|---|---|---|---|
| Pedidos em modo demonstração | Funcionando parcialmente | O pedido fica gravado só no navegador do cliente. A loja não recebe nada se o cliente não tocar em "Enviar no WhatsApp", mas a tela dizia "Recebemos seu pedido" | No modo demonstração, a tela agora diz "Falta só enviar" e pede o envio pelo WhatsApp. Com o Supabase ligado, o texto original continua | P0 ✅ |
| Credenciais do painel | Com defeito | O e-mail pessoal `adilsonrutes@gmail.com` e a senha padrão `admin@2026` estão no arquivo público | O login de demonstração passou a ser `admin@demo.ebistro` (a senha continua `admin@2026` e o painel já avisa para trocar). No código-fonte, a mesma dupla aciona `/api/admin/bootstrap`: **isso precisa ser corrigido lá** | P0 ⚠️ parcial |
| Data da encomenda | Com defeito | O formulário usa `noValidate`, então o `min` do campo de data era ignorado e dava para pedir para uma data passada. O `min` também era calculado em UTC: depois das 21h no Brasil, liberava o dia anterior | A data mínima agora é calculada no fuso local e validada no envio, com mensagem clara | P1 ✅ |
| Pedido duplicado | Funcionando parcialmente | Um duplo clique ou Enter rápido podia enviar duas vezes antes de o botão ser desabilitado | Trava síncrona no envio (testado: duplo clique gera 1 pedido) | P1 ✅ |
| Totais | Funcionando parcialmente | A soma em ponto flutuante podia gravar e exportar valores como `37,800000000000004` | Subtotal, taxa e total gravados arredondados em centavos. A planilha exporta com 2 casas | P2 ✅ |
| Exportar planilha (CSV) | Com defeito (segurança) | Um nome de cliente começando com `=`, `+`, `-` ou `@` vira fórmula no Excel (injeção de CSV) | Esses valores agora saem com `'` na frente | P2 ✅ |
| Indicadores do painel | Funcionando parcialmente | "Vendas no mês" somava pedidos não cancelados, inclusive os "novos", que ainda não foram pagos nem confirmados. "Pedidos hoje" contava cancelados | Rótulo trocado para "Pedidos no mês (R$)", que é o que o número mede. "Pedidos hoje" agora ignora cancelados | P2 ✅ |
| Excluir pedido | Funcionando | Apaga o pedido do histórico e dos indicadores, sem volta | O botão agora diz "Excluir pedido (apaga do histórico)". O recomendado é usar o status "Cancelado" | P2 ✅ |
| Financeiro | Não implementado | Não há forma de pagamento, status de pagamento (pendente/pago/estornado), descontos nem relatório por período | Precisa do código-fonte e de colunas novas no banco (ver Pendências) | P2 ⏳ |
| Preço validado no servidor | Não verificável | Com o Supabase ligado, o navegador grava `orders` com o total que ele mesmo calculou | Precisa de trigger/função no banco ou rota de API que recalcule pelo preço do produto (ver Pendências) | P0 ⏳ |
| Cardápio, categorias, carrinho, quantidade, taxa de entrega, observações, status, busca, CSV, usuários, mídia | Funcionando | Testados sem erros de console | Preservados | — |

### Modelo hamburgueria (`modelos/hamburgueria-bruto.html`)

| Área | Estado | Problema | Correção | Prioridade |
|---|---|---|---|---|
| Número do WhatsApp | Não configurado | `WHATS = "5500000000000"` | Trocar pelo número real no início do `<script>` | P1 ⏳ configuração |
| Pedido | Funcionando parcialmente | A mensagem só tinha itens e total, sem entrega/retirada nem observações | Adicionados "Entrega / Retirada" e um campo de observações, que entram na mensagem do WhatsApp | P2 ✅ |
| Carrinho | Funcionando parcialmente | Recarregar a página perdia o pedido | O carrinho fica salvo no navegador | P3 ✅ |
| Preços | Funcionando parcialmente | Um preço quebrado aparecia como "R$ 7.5" | Formata com vírgula quando há centavos (os inteiros continuam como "R$ 46", no estilo do site) | P3 ✅ |
| Acessibilidade | Com defeito | "Os mais pedidos" só funcionava com mouse. A gaveta fechada continuava recebendo foco pelo Tab | Enter/Espaço adicionam o item. A gaveta fechada fica `inert` e, ao abrir, o foco vai para "Fechar" | P3 ✅ |
| Conteúdo | Atenção | Os depoimentos dizem "Exemplo de depoimento", e a nota 4,9, o endereço e o telefone são fictícios | Trocar por dados reais antes de publicar para um cliente | P2 ⏳ conteúdo |

### Landing do eBistrô (`index.html`)

| Área | Estado | Problema | Correção | Prioridade |
|---|---|---|---|---|
| Formulário de lead | Com defeito | `window.open(..., 'noopener')` sempre devolve `null`, então o código também levava a aba atual para o WhatsApp. O visitante saía do site (confirmado em teste no original) | Abre só uma aba nova; a página continua aberta | P1 ✅ |
| `assets/config.js` | Ausente | Sem ele, o WhatsApp fica vazio e todos os botões abrem `wa.me/` sem destinatário | Criado `assets/config.js` com os campos explicados, mais um aviso no console se o WhatsApp estiver vazio | P1 ✅ (falta preencher o número) |
| LGPD | Funcionando parcialmente | O formulário coleta nome e WhatsApp sem dizer para quê | Adicionada uma linha explicando o uso dos dados e como pedir exclusão | P2 ✅ |
| Gravação de leads (Supabase) | Não verificável | Usa a chave anon no navegador | A tabela `leads` precisa de RLS que permita só INSERT para `anon` | P1 ⏳ |
| Demonstrações (celulares, painel ao vivo, chat) | Funcionando | Simulações rotuladas como "Demonstração" | Preservadas | — |

### Modelo Âmbar (`modelos/ambar.html`)

| Área | Estado | Observação |
|---|---|---|
| Cardápio, carta de vinhos, coverflow, navegação | Funcionando | Sem erros. Os números (28 pratos, 14 rótulos, 6 países) batem com o conteúdo. Nenhuma alteração |
| Reserva | Funcionando parcialmente | "Fazer reserva" só leva ao rodapé, que tem um telefone fictício. Para um cliente real, ligar a um link de WhatsApp. O aviso de "modelo de demonstração" já está no rodapé |

## Testes executados (Chromium/Playwright)

| Teste | Resultado |
|---|---|
| Carregar as 4 páginas em 1280px e 375px: erros de JS, console e rolagem horizontal | ✅ Sem erros e sem rolagem horizontal (a landing só mostra o aviso de WhatsApp não configurado) |
| Padaria: adicionar 2 itens, abrir o carrinho, conferir o subtotal | ✅ R$ 179,80 |
| Padaria: data passada | ✅ Bloqueada com mensagem |
| Padaria: duplo clique em "Enviar pedido" | ✅ 1 pedido gravado |
| Padaria: total gravado | ✅ 179.8 (em centavos) |
| Padaria: tela final em modo demonstração | ✅ "Falta só enviar" com o botão do WhatsApp |
| Padaria: login no painel `#admin` com o novo login de demonstração e indicadores | ✅ Pedidos novos 1, Pedidos hoje 1, Pedidos no mês R$ 179,80 |
| Hamburgueria: adicionar pelo cardápio, pelos acompanhamentos e pelo teclado no ranking | ✅ 3 itens |
| Hamburgueria: mensagem do WhatsApp com retirada e observação | ✅ "... Total: R$ 82 / Retirada no balcão / Obs.: Sem cebola" |
| Hamburgueria: recarregar a página mantém o carrinho; gaveta fechada `inert` | ✅ |
| Landing: enviar o formulário de lead | ✅ 1 aba do WhatsApp, a página atual continua (no original, a página saía) |

Não testado: Supabase real, Meta Pixel, `aiUrl` do chat e a pasta `admin/`. Esses dependem de configuração e código que não estão aqui.

## Pendências e próximos passos

1. **Enviar o código-fonte do projeto Next.js** (pasta com `package.json`, `src/` ou `app/`, e as migrações do Supabase). Com ele dá para:
   - remover a dupla e-mail/senha fixa e a rota `/api/admin/bootstrap` (P0);
   - recalcular preços e total no servidor, por trigger ou rota de API, em vez de confiar no navegador (P0);
   - conferir as políticas RLS de `orders`, `products`, `settings`, `subscribers` e `leads` (P0);
   - criar o financeiro: forma de pagamento, status de pagamento (pendente/pago/estornado), desconto e relatório por período, separando "pedido feito" de "pagamento recebido" (P2);
   - preparar várias lojas: coluna `store_id` em todas as tabelas, com RLS por loja (hoje `settings` usa `id = 1`, ou seja, uma loja por banco) (P2).
2. **Preencher `assets/config.js`**: WhatsApp e, se for usar, Pixel, Supabase e `aiUrl`.
3. **Trocar `WHATS`** na hamburgueria e os dados fictícios (endereço, telefone, depoimentos, nota) de cada modelo antes de entregar a um cliente.
4. Repetir no código-fonte as correções feitas no build da padaria (lista na tabela acima), senão o próximo build desfaz tudo.

## Como abrir e validar

- Abra `index.html`, `modelos/padaria-cafe.html`, `modelos/hamburgueria-bruto.html` ou `modelos/ambar.html` direto no navegador, ou sirva a pasta com `npx http-server .`.
- Painel de demonstração da padaria: `modelos/padaria-cafe.html#admin`. Login `admin@demo.ebistro`, senha `admin@2026`. Troque a senha no primeiro acesso. Os dados ficam só no seu navegador.
- Para comparar com o original: `git diff 393cc87 -- <arquivo>`.
