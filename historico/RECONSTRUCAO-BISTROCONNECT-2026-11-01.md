# Reconstrução estratégica, comercial e visual da BistrôConnect

**Arquivo:** `sites-personalizados/index.html` (publicado em `/sites-personalizados/`)
**Cópia do original preservada em:** `historico/sites-personalizados-index-ANTES-DA-RECONSTRUCAO-2026-11-01.html` (3,47 MB, idêntica ao arquivo de antes da reconstrução) e no histórico do git.
**Auditoria (Etapa 1):** `historico/AUDITORIA-BISTROCONNECT-2026-11-01.md`

---

## 1. Resumo

A página deixou de vender "site em 7 dias" e passou a vender a marca. A narrativa agora é: **promessa → manifesto → dois caminhos → Signature → demonstrações gastronômicas → cardápio → painel → pedidos diretos → processo → investimento → perguntas → conversa.**

Nada do que existia foi removido sem investigação. As 26 verificações da matriz de preservação passam (seção 6). O tamanho do HTML caiu de **3,47 MB para 244 KB**, e o carregamento inicial de **3,5 MB para 1,1 MB**.

---

## 2. Etapa 2 — Arquitetura

| # | Seção | id | Fundo | Função |
|---|---|---|---|---|
| 1 | Hero | (topo) | grafite | Promessa + demonstração real (computador e celular) |
| 2 | Manifesto | `manifesto` | off-white | A experiência começa antes da primeira mesa |
| 3 | Duas linhas | `solucoes` | grafite | Signature × Soluções gastronômicas, lado a lado |
| 4 | Projetos Signature | `signature` | off-white | 8 pilares + processo Signature |
| 5 | Demonstrações | `templates` | grafite | Os cinco modelos (carrossel 3D) |
| 6 | Cardápio digital | `modelos` | off-white | Os cinco cardápios interativos |
| 7 | Painel administrativo | `sites` | grafite | 9 telas reais, navegação e rastreio |
| 8 | Pedidos diretos | `calculadora` | off-white | Canal próprio + calculadora com premissas |
| 9 | Soluções gastronômicas | `gastronomia` | grafite | O que inclui + processo + prazo |
| 10 | Investimento | `planos` | off-white | 4 caminhos + mensalidade + condição especial (oculta) |
| 11 | Perguntas frequentes | `faq` | grafite | 14 perguntas em 7 grupos |
| 12 | Contato | `contato` | off-white | CTA final + formulário |

Fundos alternam claro e escuro, sem repetir cores em seções vizinhas. Hierarquia de valor seguida: marca → qualidade → experiência → soluções → tecnologia → benefícios → investimento.

**Dois caminhos separados:** Signature (orçamento personalizado, processo próprio, CTA "Quero um projeto exclusivo") e Gastronomia (valores de referência, implantação rápida, CTA "Conhecer as soluções"). O texto afirma a diferença: *"um projeto Signature não é um modelo com novas cores, e uma solução gastronômica não é desenvolvimento exclusivo."*

## 3. Etapa 3 — Copy

Reescrita completa. Pontos principais:
- **Headline:** "Sua marca merece um site do seu tamanho." **Subtítulo:** "Experiências digitais criadas para restaurantes que não abrem mão da excelência."
- **Manifesto:** identidade, ambiente, atendimento, gastronomia e presença digital como uma experiência só.
- **CTAs (Parte 6):** Signature "Quero um projeto exclusivo" · Gastronomia "Conhecer as soluções" · Cardápio "Ver demonstração" · Geral "Vamos conversar sobre meu projeto".
- **Sem prova social inventada:** removidos o selo "4,9 de 5" e qualquer depoimento.
- **Palavra "grátis":** eliminada da página (0 ocorrências), inclusive no assistente Bia.

**Oferta Casa Cheia reavaliada.** Removidos: valor somado artificial (R$ 6.847 e preços riscados), "vagas 2 de 5", contagem regressiva, "bônus fundador" e a "Garantia Pedido Direto" (promessa de pedidos que depende de fatores externos). **Preservado:** tudo o que o plano entregava (painel e rastreio, perfil no Google, 500 cartões de volta + display, campanha de lançamento, 30 dias de acompanhamento) e o mecanismo `OFERTA` do código, agora **oculto por padrão**. Para publicar uma condição especial: `ativa:true`, `texto`, prazo `ate` e, se houver limite real, `vagas`/`restantes`.

## 4. Etapa 4 — Direção de arte

- **Paleta:** grafite profundo (`#0F1011`), off-white (`#F4F1EA`), champagne (`#C8B48E`, substituiu o dourado forte) e verde profundo (`#1D3A30`) como cor complementar (linha Gastronomia, calculadora, plano mais completo).
- **Tipografia:** Fraunces (títulos editoriais, itálico para a palavra de destaque), DM Sans (leitura), microtextos em caixa alta com espaçamento.
- **Composição:** espaçamento generoso, linhas finas em vez de cartões, botões retangulares, fotografia gastronômica em alta resolução (forno a lenha, restaurante à luz de velas, hambúrguer), mockups de computador e celular.
- **Removidos:** partículas, texto digitando, selos flutuantes, brilhos, gradientes decorativos, poeira dourada, reflexo nos botões.

## 5. Etapas 5 e 6 — Implementação e otimização

| Medida (servidor local, sem limitação de rede) | Antes | Depois |
|---|---|---|
| Tamanho do HTML | 3.388 KB | **244 KB** |
| Carregamento inicial (total) | 3.581 KB | **1.128 KB (−68%)** |
| DOMContentLoaded (desktop) | 736 ms | **363 ms** |
| LCP (desktop) | 560 ms | **432 ms** |
| Imagens embutidas em base64 | 3.133 KB | **12 KB** (só o ícone da aba (9 KB); o resto virou arquivos WebP) |
| Código JavaScript morto | ~25 KB | removido |
| CSS de componentes antigos | ~23 KB | removido |

- 13 capturas de modelos e 38 miniaturas de cardápios foram para arquivos WebP, com `width`/`height`, `loading="lazy"` e `decoding="async"` (imagens do topo ficam imediatas, a primeira com `fetchpriority="high"`). Duplicatas removidas por conteúdo. Telas do painel convertidas de JPG para WebP (1,1 MB → 0,6 MB).
- **Poda de CSS verificada:** comparação pixel a pixel da página inteira antes e depois — celular 0 pixels diferentes; computador 123 de 23,7 milhões (ruído).
- `prefers-reduced-motion` respeitado (animações decorativas desligam, o conteúdo continua visível e navegável).
- Link "Ir para o conteúdo" (acessibilidade), `alt` nas imagens, foco visível nos botões.
- CSP: scripts internos mudaram, hashes regenerados com `ferramentas/csp.py` (5 scripts liberados). `frame-src 'self'` mantido para o cartão ao vivo.
- Removida a requisição duplicada `assets/config.js` (retornava 404 em toda visita); a configuração vem de `/assets/config.js`.

## 6. Etapa 7 — Validação

**Ambiente:** servidor local, Chromium (Playwright), desktop 1440×900 e celular 390×844 emulado. **Supabase, WhatsApp e Pixel foram simulados por interceptação de rede** (veja pendências). Resultado: **26/26 verificações aprovadas, sem erros de JavaScript e sem bloqueio de CSP.**

| ID | Verificação | Resultado |
|---|---|---|
| P01 | Carrossel de modelos: 5 cartões, setas, bolinhas | OK |
| P02 | "Ver ao vivo": `/restaurante/`, `/hamburgueria/`, `/cafeteria/`, `/pizzaria/`, `consultoria/` | OK |
| P03 | "Quero este modelo" preenche o formulário (modelo e tipo) | OK |
| P04 | Cinco cardápios: adicionar item e ver "Finalizar pedido" | OK (5/5) |
| P05 | Finalizar pedido abre o resumo (simulação) | OK |
| P06 | Abas do topo trocam o modelo | OK |
| P07 | Painel: 9 telas, 9 abas, setas | OK |
| P08 | Celular alterna "pedido no WhatsApp" e "rastreio" | OK |
| P09 | Calculadora: R$ 10 mil, 12%, 3 em 10, R$ 199 → R$ 1.200 / +R$ 360 / −R$ 199 / **R$ 161**; com R$ 149 → R$ 211 | OK |
| P10 | Formulário: validação de campos | OK |
| P11 | Antispam (campo-armadilha) bloqueia envio | OK |
| P12 | Lead: `POST /rest/v1/leads`, chave anon, documento completo, solução procurada | OK (interceptado) |
| P13 | WhatsApp do formulário: número, mensagem e link da demonstração escolhida | OK (interceptado) |
| P14 | WhatsApp flutuante com número | OK |
| P15 | Meta Pixel: carrega com ID e consentimento | OK (script simulado) |
| P16 | Botões de plano preenchem "Solução procurada" | OK |
| P17 | Condição especial oculta por padrão | OK |
| P18 | Assistente Bia: preços atualizados, sem "Standard/Plus/grátis" | OK |
| P19 | Rodapé "Acesso restrito" → `/crm/` | OK |
| P20 | Celular: sem rolagem lateral (390 px) | OK |
| P21 | CSP: nenhum recurso bloqueado | OK |
| P22 | CTAs da Parte 6 e do hero presentes | OK |
| P23 | Formulário: 5 opções de solução | OK |
| P24 | Todas as âncoras internas apontam para um id existente | OK |
| P25 | Nenhuma imagem local quebrada | OK |

### Testes que NÃO foram executados
1. **Supabase real e CRM:** só confirmei que a página envia o `POST` correto; não gravei lead no banco real nem conferi no `/crm/`. Depende da regra de acesso (RLS) da tabela `leads` no servidor.
2. **WhatsApp real:** o endereço `wa.me` foi interceptado; não abri o aplicativo nem validei o número de produção.
3. **Meta Pixel real:** o carregamento do Pixel foi simulado; os eventos `PageView` e `Lead` não foram conferidos no Gerenciador de Eventos.
4. **Links de produção** (`/restaurante/`, `/hamburgueria/`, `/cafeteria/`, `/pizzaria/`): a rede deste ambiente bloqueia o domínio. Verifiquei que a página aponta para o endereço certo, não que ele responde.
5. **Hospedagem real (Hostinger/LiteSpeed):** a reescrita de scripts por esse servidor já quebrou hashes de CSP antes. Confira o console após publicar.
6. **Imagens da Consultora** (servidor do Higgsfield): dependem de rede externa, bloqueada aqui.
7. **Dispositivos físicos, Safari, Firefox, leitores de tela, Lighthouse e Core Web Vitals de campo.** Os números de desempenho são de laboratório local, sem simular rede lenta.

## 7. Preservado, corrigido e problemas encontrados

**Preservado (matriz P01–P21):** carrosséis (modelos, cardápios, painel), cinco cardápios com carrinho e resumo de pedido, abas do topo, painel de 9 telas e rastreio, calculadora, formulário com validação e antispam, integração Supabase, CRM, Pixel com consentimento, WhatsApp, assistente Bia, planos e botões de contratação, links e âncoras, CSP.

**Corrigido:**
- **Defeito real:** o "dedo" automático da demonstração disparava cliques nos celulares laterais e o carrossel de cardápios **saltava sozinho** de modelo (explica a sensação de movimento confuso). Agora só cliques do visitante trocam o modelo.
- Links "Ver ao vivo" eram relativos (`restaurante/`) e dariam 404 fora de `/`; agora apontam para os endereços de produção.
- `assets/config.js` duplicado (404 em toda visita).
- Texto da aba "Restaurante" ilegível no topo.
- Assistente Bia desatualizada ("três modelos", "4 estilos", planos antigos, "grátis").
- Calculadora: premissas explícitas, mensalidade escolhível, sem prometer resultado.

**Mudança de comportamento a conhecer:** com o sistema do visitante em "reduzir movimento", a página fica mais calma. Isso é o esperado, mas foi exatamente o que escondia os efeitos dos modelos no seu computador antes.

## 8. Decisões que dependem de você

1. **Cartão "Marca pessoal" (antiga Consultora):** o briefing pede não misturar consultoras; as demonstrações pedem preservar os cinco. Mantive o cartão, marcado como "Demonstração complementar". Recomendo trocá-lo por um quinto modelo gastronômico. Ele também deriva do site de uma cliente real (nome e fotos trocados) e usa fotos hospedadas fora.
2. **Correspondência de nomes:** Site Gastronômico = antigo Standard (R$ 1.497 + R$ 149/mês); Digital Experience = antigo Plus/Casa Cheia (R$ 2.997 + R$ 199/mês); Cardápio Digital = a partir de R$ 149/mês + R$ 997. **Nenhum preço foi alterado.** No formulário, Digital Experience aparece como "Sistema de pedidos". Confirme.
3. **Garantia Pedido Direto:** retirada da página. Só volte com critérios verificáveis e sem prometer pedidos.
4. **Atendimento no WhatsApp:** aparece no painel como central de conversas, com a nota "ativação combinada na implantação" (a ativação oficial do WhatsApp segue parada à espera do CNPJ).
5. **Resposta da Bia sobre IA no WhatsApp** e a frase do FAQ **"cada modelo é usado por uma só casa do mesmo ramo em cada cidade"** foram mantidas do original: confirme que são compromissos reais.
6. **"Quero este modelo":** abre o formulário com o modelo escolhido e o link da demonstração segue na mensagem do WhatsApp. O "Ver ao vivo" abre o site de demonstração. Se preferir que "Quero este modelo" abra o site, é uma linha.

## 9. Recomendações futuras

- Criar uma página de portfólio **Signature** com projetos reais (hoje a linha não tem vitrine e a página é honesta quanto a isso).
- Hospedar localmente as fontes e as fotos da Consultora; avaliar remover Orbitron/Yellowtail/Oswald se só servirem aos modelos.
- Rodar Lighthouse e medir Core Web Vitals em produção; considerar HTTP cache longo para `img/`.
- Dados estruturados (`Organization`, `LocalBusiness`) e nova imagem de compartilhamento (`og:image`) alinhada à nova identidade.
- Quando houver clientes autorizados, adicionar prova social real (depoimentos e números verificáveis).
- Painel: hoje são telas reais em imagem, com abas e rolagem; um painel realmente interativo exigiria embutir o sistema em modo demonstração (foi testado antes e ficou pesado e mal formatado).

## 10. Como publicar

1. Envie o zip para `public_html` e extraia (aceite substituir). Cria/atualiza `sites-personalizados/index.html` e as pastas `img/site`, `img/cardapio`, `img/gastro` e `img/painel`.
2. Pode apagar os `.jpg` antigos de `img/painel` (agora são `.webp`).
3. Atualize com **Ctrl + F5** e abra o console do navegador (F12): não deve haver erros vermelhos.

**Arquivos alterados:** `sites-personalizados/index.html` · `sites-personalizados/img/` (novas pastas) · `sites-personalizados/consultoria/index.html` (sem mudança nesta etapa) · `historico/` (cópia do original, auditoria e este relatório).
