# Auditoria da página "Sites personalizados" — BistrôConnect

**Fase:** Parte 1 (entendimento) e Parte 2 (auditoria). **Nenhum código foi alterado.**
**Arquivo auditado:** `sites-personalizados/index.html` do repositório. É o mesmo arquivo que vai para `public_html/sites-personalizados/` e equivale ao `index(1).html` citado no briefing.
**Data:** 01/11/2026

> **Limitação:** a página publicada (bistroconnect.com.br/sites-personalizados/) não pôde ser aberta, porque a rede do ambiente de trabalho bloqueia o domínio. A auditoria foi feita sobre o arquivo-fonte, rodando-o num servidor local com navegador automatizado (Chromium). O que depende do servidor real (configuração em `/assets/config.js`, Supabase, Pixel, páginas dos modelos) está classificado como **C** ou **D**.

---

## 1. Leitura estratégica (antes do código)

### 1.1 O que a página vende hoje
A página inteira vende **uma única linha**: modelos de site para gastronomia, com cardápio, pedido no WhatsApp e painel. Na nomenclatura nova, isso é a **BistrôConnect Gastronomia**.

- **Promessa atual do topo:** "O site da sua casa no ar em 7 dias, pronto para vender." É uma promessa de velocidade, não de exclusividade.
- **Ofertas:** dois planos, **Standard** (R$ 1.497 + R$ 149/mês) e **Plus** (R$ 2.997 + R$ 199/mês). Há também uma linha solta "só cardápio digital" (a partir de R$ 149/mês + R$ 997).
- **Argumento central:** economia com a comissão do app (a calculadora) e a demonstração do sistema funcionando.

### 1.2 Lacunas em relação ao posicionamento pedido

| Pedido no briefing | Situação atual | Lacuna |
|---|---|---|
| Promessa "Sua marca merece um site do seu tamanho." | Não aparece em nenhum lugar | Falta a promessa central |
| Linha **Signature** (projeto exclusivo, orçamento individual) | **Não existe** na página | Falta a linha premium inteira |
| Linha **Gastronomia** apresentada como estrutura própria personalizável | Existe, mas o texto fala em "modelos" e "7 dias" sem deixar claro o limite da personalização | Falta transparência sobre o que é modelo e o que é exclusivo |
| Percepção premium, longe de "fábrica de sites" | Selos de urgência, vagas, contador, preços riscados e "Grátis" repetido puxam para uma linguagem de oferta de varejo | Conflito de tom |
| Foco em gastronomia | O 5º modelo, "Consultora", é marca pessoal e não gastronomia | Conflito de especialização |

**Conclusão estratégica:** a base técnica é forte e quase toda pertence à linha **Gastronomia**. A linha **Signature** terá de ser criada, com conteúdo, prova e chamada próprios, sem reaproveitar a vitrine de modelos como se fosse trabalho exclusivo.

---

## 2. Inventário técnico

### 2.1 Números gerais
| Item | Valor |
|---|---|
| Tamanho do HTML | **3,47 MB** (3,21 MB são imagens embutidas em base64) |
| Blocos `<style>` | 1, com cerca de 134 KB de CSS |
| `<script>` | 7: 2 externos (config) e 5 internos, todos com hash na CSP |
| IDs | 76, sem IDs duplicados |
| Animações `@keyframes` | 46 |
| Laços contínuos | 7 com `requestAnimationFrame`, 6 com `setInterval` e 7 com `IntersectionObserver` |
| `addEventListener` | 42 |
| Fontes Google | 6 famílias: Poppins, Orbitron, Fraunces, Oswald, Yellowtail e DM Sans |

### 2.2 Seções (na ordem)

| # | Linha | Seção / ID | Fundo | Título |
|---|---|---|---|---|
| 1 | 1520 | `.hero.cream` (sem id; âncora `#topo`) | claro | O site da sua casa no ar em 7 dias, pronto para vender. |
| 2 | 1570 | `#templates` | escuro | Cinco estilos criados para gastronomia e marcas pessoais… |
| 3 | 1656 | `#modelos` | claro | Um cardápio que o cliente usa sozinho. Toque e teste. |
| 4 | 1679 | `#sites` | escuro | Todo site já vem com o sistema da sua casa |
| 5 | 1699 | `#calculadora` | claro | O app fica com até 23% de cada pedido… |
| 6 | 1736 | `#como-funciona` | escuro | Do sim ao site no ar em 7 dias. Você só aprova. |
| 7 | 1751 | (sem id) "O que está incluso" e "Lado a lado" | claro | Tudo o que vem em cada site… |
| 8 | 1788 | `#oferta` | escuro | Plus: site de marca e delivery próprio em 7 dias |
| 9 | 1820 | `#planos` | claro | Escolha o tamanho do seu site |
| 10 | 1847 | `#faq` | escuro | Antes de você perguntar |
| 11 | 1863 | `#contato` | claro | Mande o nome da sua casa… |

Fora das seções ficam o cabeçalho fixo (`header.nav`), o rodapé, o botão flutuante do WhatsApp (`#waFloat`), a assistente virtual "Bia" (`.ai-fab` e `.ai-panel`) e o aviso de cookies (`.consent`, criado por script só quando há Pixel configurado).

### 2.3 IDs críticos (dependências de script)

| Grupo | IDs |
|---|---|
| Topo | `topo`, `net` (canvas), `typed`, `vitrine`, `vt-rest`, `vt-burger`, `vt-cafe`, `vt-pizza`, `heroPhone` |
| Carrossel de modelos | `cfTpls`, `cfPrev`, `cfNext`, `cfThumb`, `cfName`, `cfTag`, `cfDots` |
| Carrossel de celulares | `pfStage`, `pfModels`, `pfPrev`, `pfNext`, `pfName`, `pfDesc`, `pfDots` |
| Sistema (painel) | `pcStage`, `pcFlow`, `pcHand`, `pcTag`, `pcPrev`, `pcNext`, `pcName`, `pcDesc`, `pcDots` |
| Calculadora | `fat`, `fatOut`, `dir`, `dirOut`, `taxaLbl`, `rCom`, `rSave`, `rMens`, `rEco`, `rAno`, `rNote` + atributos `data-taxa` |
| Oferta | `ofMes`, `ofRest`, `ofTot`, `ofBar`, `ofTimerBox`, `ofTimer` |
| Formulário | `leadForm`, `lNome`, `lEst`, `lTipo`, `lPlano`, `lModelo`, `lWhats`, `lSite` (armadilha antispam), `formMsg` + atributos `data-plano` e `data-modelo` |
| Outros | `waFloat`, `aiInput`, `ano` |

### 2.4 Scripts

| # | Tipo | O que faz |
|---|---|---|
| 1 | `src="assets/config.js"` | **Retorna 404.** Esse arquivo não existe dentro de `/sites-personalizados/` |
| 2 | `src="/assets/config.js"` | Configuração da plataforma: `window.BC` (Supabase, WhatsApp de suporte, Pixel) |
| 3 | interno (389 bytes) | Monta `window.BISTRO` a partir de `window.BC` (whatsapp, pixelId, supabaseUrl, supabaseKey, aiUrl) |
| 4 | interno (98 bytes) | `window.MRTECH` (whatsapp e pixel): **nome herdado de outro projeto** |
| 5 | interno (588 bytes) | Meta Pixel. Só carrega com `pixelId` e consentimento (`localStorage eb-consent`) |
| 6 | interno (955 KB) | Aplicação principal (módulos na tabela abaixo) |
| 7 | interno (13 KB) | Oferta (vagas e prazo), carrosséis 3D, entrada ao rolar, carrossel do painel, celular pedido → rastreio, selos e cartão ao vivo |

**Módulos do script principal (#6):** WhatsApp flutuante; cardápios de demonstração ("4 modelos" no comentário; hoje são 5 no carrossel); "dedo" automático da demonstração; rede de partículas do topo; palavra digitando; luz que segue o mouse; inclinação do celular do topo; números que contam; assistente Bia; **painel falso antigo (código morto: sai logo no início porque `#dash` não existe mais)**; troca de modelos do topo; revelar ao rolar; calculadora; planos → formulário; `salvarLead` (Supabase); formulário de lead.

### 2.5 Carrosséis e componentes interativos
1. **Topo:** abas Restaurante, Hamburgueria, Padaria e café e Pizzaria, com troca automática a cada 44 s, site rolando e celular com cardápio clicável (`#heroPhone`).
2. **Modelos de site (`#cfTpls`):** 5 cartões em 3D, troca a cada 10 s, setas, bolinhas, toque, "Ver ao vivo" e "Quero este modelo".
3. **Cardápios (`#pfModels`):** 5 celulares em 3D, troca a cada 15 s, cada um com cardápio clicável e carrinho.
4. **Sistema (`#pcFlow`):** 9 telas reais do painel em imagem, com rolagem e a mãozinha clicando no menu; celular alternando pedido no WhatsApp e rastreio.
5. **Calculadora:** 2 controles deslizantes, 2 botões e extrato.
6. **Oferta:** barra de vagas e contador regressivo.
7. **FAQ:** `<details>` nativo.
8. **Assistente Bia:** respostas prontas; usa IA se `aiUrl` estiver configurado.
9. **Aviso de cookies:** cria o consentimento e então carrega o Pixel.

### 2.6 Formulários
| Formulário | Validação | Destino |
|---|---|---|
| `#leadForm` | nome, estabelecimento e WhatsApp (10–13 dígitos); campo-armadilha `lSite`; bloqueio de envio em menos de 2,5 s; reenvio só após 30 s | 1) `fbq('track','Lead')` 2) `POST {supabaseUrl}/rest/v1/leads` com a chave anon 3) abre `wa.me` com a mensagem pronta |
| `.ai-foot` (chat) | texto livre | respostas locais, ou `POST` para `aiUrl` com a chave anon |

### 2.7 Links
- **Âncoras internas:** `#contato` (11×), `#templates` (3×), `#calculadora` (2×), `#topo`, `#como-funciona`, `#oferta`, `#sites`, `#planos` e um `#` solto.
- **"Ver ao vivo":**
  - `restaurante/`, `hamburgueria/` e `cafeteria/` são **relativos a `/sites-personalizados/`**;
  - `/pizzaria/` é absoluto, na raiz;
  - `consultoria/` é relativo.

  Os três primeiros precisam existir no servidor dentro de `sites-personalizados/`.
- **Rodapé:** "Acesso restrito" → `/crm/`.
- **WhatsApp:** `wa.me/{número de config}`. **Sem a configuração, sai `wa.me/?text=` sem número** (comprovado no teste local).

### 2.8 Mídia e iframes
- 13 imagens embutidas em base64 (3,2 MB): capturas dos modelos, fotos dos cardápios e logo.
- 11 arquivos em `img/painel/`: 9 telas do painel, `pedido-whats.jpg` e `rastreio.jpg`.
- **2 imagens em servidor externo** (`d8j0ntlcm91z4.cloudfront.net`, do Higgsfield): fotos da Consultora no cartão. Dependem de um terceiro.
- 1 iframe: `consultoria/index.html`, o site da Consultora rolando dentro do cartão. Só funciona publicado, mesma origem.

### 2.9 Dependências externas
`fonts.googleapis.com` e `fonts.gstatic.com` (fontes), `connect.facebook.net` e `www.facebook.com` (Pixel), `*.supabase.co` (leads e IA), `wa.me` (WhatsApp) e `d8j0ntlcm91z4.cloudfront.net` (fotos da Consultora).

---

## 3. Inventário funcional e classificação

**A** = implementada e identificada · **B** = demonstração/simulação · **C** = depende de ambiente externo · **D** = precisa de validação

| # | Funcionalidade | Classe | Evidência |
|---|---|---|---|
| F01 | 5 demonstrações de modelos (carrossel) | **A** | 5 cartões em `#cfTpls`; setas, bolinhas e troca automática testadas |
| F02 | "Ver ao vivo" de cada modelo | **D** | Links relativos; só valida no servidor real (restaurante, hamburgueria e cafeteria dentro de `/sites-personalizados/`) |
| F03 | 5 experiências de cardápio | **B** | 5 celulares em `#pfModels` com cardápio clicável; marcas fictícias |
| F04 | Navegação entre demonstrações | **A** | Setas, bolinhas, toque e clique nas laterais |
| F05 | Carrinho de compras | **B** | Testado: "Adicionar" exibe "Finalizar pedido · 1 item" |
| F06 | Simulação de pedido (finalizar) | **B / D** | Existe a tela de finalização simulada dentro do celular; precisa de verificação manual do fluxo completo |
| F07 | Envio pelo WhatsApp (formulário e botão flutuante) | **C** | Abre `wa.me`; o número vem de `/assets/config.js` |
| F08 | Painel administrativo (9 telas) | **B** | Imagens reais do painel em demonstração; o painel de verdade está em `/painel/`, fora desta página |
| F09 | Gestão de pedidos | **B** | Tela "Pedidos", em quadro por etapa |
| F10 | Produtos e categorias | **B** | Tela "Cardápio" |
| F11 | Financeiro | **B** | Tela "Financeiro" (mês passado) |
| F12 | Clientes | **B** | Tela "Clientes" |
| F13 | Atendimento | **B** | Tela "Atendimento", com conversa aberta |
| F14 | Equipe | **B** | Tela "Equipe" |
| F15 | Configurações da loja | **B** | Telas "Dados da loja" e "Conta e ajustes" |
| F16 | Rastreamento | **B** | Imagem do rastreio real, alternando com o pedido no WhatsApp |
| F17 | Calculadora de economia | **A** | Testado: R$ 20.000 a 23% dá R$ 4.600 de comissão e R$ 1.181 de sobra no mês |
| F18 | Formulário de prévia | **A** | Validação testada ("Preencha nome, estabelecimento…"); antispam presente |
| F19 | Integração Supabase (gravar lead) | **C** | `POST /rest/v1/leads`; depende da URL e chave em `config.js` e da regra de acesso (RLS) que permite inserir |
| F20 | CRM | **C** | Recebe os leads da F19; acesso pelo link do rodapé `/crm/` |
| F21 | Meta Pixel | **C** | Só carrega com `pixelId` e consentimento; eventos `PageView` e `Lead` |
| F22 | Links de contratação | **A** | Botões dos planos com `data-plano` preenchem o select e levam a `#contato` |
| F23 | Planos e preços | **A** | Standard e Plus, mais a nota do cardápio avulso |
| F24 | Assistente Bia | **A / C** | Respostas locais funcionam; IA só com `aiUrl` |
| F25 | Oferta: vagas e contador | **A** (técnico) / **D** (veracidade) | Valores fixos no código em `OFERTA={mes, vagas:5, restantes:2, fimBonus}`; precisam ser atualizados à mão e ser verdadeiros |
| F26 | Aviso de cookies | **C** | Só aparece com Pixel configurado |
| F27 | Site da Consultora no cartão | **C** | iframe + imagens no cloudfront |

---

## 4. Matriz de preservação (para os testes depois da reconstrução)

| ID | Item | Dependência no código | Como testar | Critério de aceite |
|---|---|---|---|---|
| P01 | Carrossel de modelos | `#cfTpls .tpl-card`, `#cfPrev/#cfNext/#cfDots`, `data-pos` | Clicar nas setas e bolinhas; esperar a troca | 5 cartões; o central rola; nenhum erro no console |
| P02 | Ver ao vivo | `href` de `.tc-cta a.btn-ghost` | Abrir cada link publicado | Os 5 abrem sem 404 |
| P03 | Quero este modelo | `data-modelo` → `#lModelo` | Clicar e conferir o select | O select muda e a página rola até o contato |
| P04 | Cardápios | `#pfModels .model`, `MODELS`, `IMG` | Adicionar item em cada um dos 5 | Aparece a barra "Finalizar pedido" |
| P05 | Finalizar pedido simulado | fluxo `ck-sheet` dentro do celular | Finalizar com 1 item | Mostra a etapa seguinte sem erro |
| P06 | Celular do topo | `#heroPhone`, abas `vt-*` | Trocar as abas | A imagem e o celular trocam juntos |
| P07 | Carrossel do painel | `#pcFlow .pc-card`, `data-y`, `#pcHand` | Esperar um ciclo; usar setas | 9 telas; a mãozinha clica no menu correto |
| P08 | Celular pedido → rastreio | `.pc-pscr img.pp`, `#pcTag` | Esperar 20 s | As duas telas se alternam e a etiqueta muda |
| P09 | Calculadora | `#fat`, `#dir`, `[data-taxa]`, `#rCom…#rAno` | 10 mil / 12% / 3 de 10 | R$ 1.200 / + R$ 360 / − R$ 199 / R$ 161 |
| P10 | Formulário: validação | `#leadForm` | Enviar vazio | Mensagem de erro em `#formMsg` |
| P11 | Formulário: antispam | `#lSite`, 2,5 s, 30 s | Preencher a armadilha | Não envia |
| P12 | Lead no Supabase | `salvarLead`, `window.BISTRO` | Enviar no site publicado | O lead aparece no `/crm/` |
| P13 | WhatsApp do formulário | `waLink()` | Enviar | Abre o WhatsApp com número e mensagem |
| P14 | WhatsApp flutuante | `#waFloat` | Clicar | Abre o WhatsApp **com número** |
| P15 | Pixel | `ebPixel`, `eb-consent` | Aceitar os cookies (site publicado) | `PageView` e `Lead` aparecem no Gerenciador de Eventos |
| P16 | Planos → formulário | `[data-plano]` | Clicar em "Escolher Plus" | `#lPlano` = Plus |
| P17 | Oferta | `OFERTA`, `#ofTimer`, `#ofRest` | Abrir a seção | Contador e vagas coerentes com a realidade |
| P18 | Bia | `.ai-fab`, `#aiInput` | Perguntar "quanto custa" | Responde com os preços certos |
| P19 | CRM no rodapé | `a[href="/crm/"]` | Clicar | Abre o login do CRM |
| P20 | Responsivo | toda a página | 390 px de largura | `scrollWidth` = 390 (hoje está ok) |
| P21 | CSP | meta CSP + `ferramentas/csp.py` | Rodar o csp.py depois de editar scripts | Nenhum "Refused to execute" no console |

---

## 5. Segurança técnica e riscos

### 5.1 CSP
- A política está em `<meta http-equiv>`: `script-src 'self'` + **5 hashes sha256** + `connect.facebook.net`. Também `frame-src 'self'`, `connect-src` para Supabase e Facebook, `img-src https:` e `object-src 'none'`.
- **Toda edição em script interno muda o hash.** Depois de qualquer alteração é obrigatório rodar `python3 ferramentas/csp.py sites-personalizados/index.html`. Sem isso, o script é bloqueado no navegador.
- **Risco já visto:** a Hostinger (LiteSpeed) pode reescrever scripts e quebrar os hashes. Isso já aconteceu antes; vale conferir o console depois de publicar.

### 5.2 Carregamento duplicado
- `assets/config.js` (relativo) dá **404** em toda visita; só o `/assets/config.js` é válido. É uma requisição inútil e um erro no console. **Correção segura:** remover a linha relativa.

### 5.3 Configuração e endpoints
- **Variáveis globais:** `window.BC`, que vem de `/assets/config.js`; `window.BISTRO`, montada a partir de BC; `window.MRTECH`, nome legado; `OFERTA`, fixa no código; `window.__BCIMG`.
- **Supabase:** a URL e a chave **anon** ficam expostas no navegador (correto, nunca a service_role). A gravação de lead depende da regra RLS da tabela `leads` permitir insert anônimo, mas **sem permitir leitura**. Isso precisa ser validado no Supabase.
- **IA (`aiUrl`):** vazio no padrão. Se for configurado, a chave anon vai no cabeçalho.

### 5.4 Conflitos e código legado
- **Nome `track`:** existe um `track` global (Pixel) e outro dentro do módulo do painel antigo. Não há conflito hoje, porque o segundo está isolado na função, mas é frágil.
- **Painel falso antigo:** o JS (cerca de 90 linhas) e o CSS (`.dash`, `.d-*`, `.track-phone`, `.os-toasts`…) ainda estão no arquivo, mas o código sai logo no início. É **código morto** e pode ser removido com segurança numa fase de limpeza.
- **CSS em camadas:** muitas regras foram sobrescritas várias vezes, inclusive com `!important` (topo, celulares, sistema). Funciona, mas qualquer mudança visual exige cuidado com a ordem. Recomenda-se consolidar.
- **Animações desativadas mas presentes:** `pfDust`, `pfRing`, `pfChip`, `pfSpot` e `cfLive`.

### 5.5 Desempenho
- **3,47 MB num único HTML** é o principal ponto. As imagens em base64 não ficam em cache separado, atrasam o primeiro carregamento e pesam no celular. **Recomendação:** extrair para arquivos `.webp` (estimativa de −2,5 MB).
- **6 famílias de fonte:** Orbitron e Yellowtail parecem servir só a detalhes dos modelos e são candidatas a remoção ou carregamento sob demanda.
- **7 laços de animação e 6 intervalos ao mesmo tempo:** os carrosséis já pausam fora da tela; o canvas de partículas do topo, não. Precisa ser verificado.
- **Imagens externas no cloudfront:** risco de sumirem (expiração ou conta do Higgsfield). Devem ser baixadas e hospedadas no próprio site.

---

## 6. Riscos de comunicação e veracidade

Para o posicionamento premium e a regra "só prometer o que existe", estes pontos precisam de decisão antes da reconstrução:

1. **Selo "4,9 de 5 — clientes que pediram pelo site":** nota **ilustrativa**, sem base real. Remover ou trocar.
2. **"Restam 2 de 5 vagas" + contador até 30/11:** valores fixos no código. Se não refletirem a capacidade real, é escassez falsa. Também conflita com o tom premium.
3. **Preços riscados** (R$ 3.500, R$ 6.847…): ancoragem de varejo. Exige que o preço "de" seja defensável.
4. **"Garantia Pedido Direto":** promessa contratual. Precisa de regras claras (o FAQ cita "se não chegar a 3…").
5. **Percentuais do iFood (12% / 23%):** citar a fonte ou suavizar ("em torno de").
6. **Assistente Bia desatualizada:** diz "três modelos" e "4 estilos"; hoje são 5.
7. **Cartão "Consultora" (marca pessoal):**
   - foge do foco gastronômico;
   - foi derivado do site de uma cliente real, com nome e fotos trocados, e as fotos estão em servidor de terceiros.
8. **Nome "MRTECH" no código:** legado de outro projeto. Não aparece para o visitante, mas convém renomear.
9. **Uso repetido de "grátis"** (topo, formulário, chat): a orientação anterior era evitar "grátis" em público.

---

## 7. Resumo

- **A página está tecnicamente saudável:**
  - nenhum erro de JavaScript no teste;
  - nenhum ID duplicado;
  - nenhum transbordo lateral no celular;
  - formulário com antispam;
  - integrações protegidas por configuração e consentimento.
- **Correções técnicas seguras:**
  - remover o `config.js` duplicado (404);
  - remover o código morto do painel antigo;
  - extrair as imagens base64;
  - hospedar as fotos da Consultora no próprio site.
- **O maior trabalho é estratégico:** a página só representa a linha **Gastronomia**. A linha **Signature** e a promessa "Sua marca merece um site do seu tamanho" ainda não existem, e alguns elementos (vagas, contador, nota 4,9, preços riscados, "grátis") puxam a percepção para longe do premium.

**Status:** auditoria concluída e nenhuma alteração feita no código. Aguardando as próximas partes do briefing para a reconstrução.
