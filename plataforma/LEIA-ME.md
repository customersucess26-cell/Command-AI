# Bistrô Connect: plataforma de lojas online (Fase 1)

Uma plataforma só, com várias lojas. O empreendedor se cadastra, cria a loja em minutos, monta o cardápio e recebe pedidos. Você administra todas as lojas de um lugar.

## O que tem nesta pasta

| Arquivo ou pasta | O que é |
|---|---|
| `index.html` | Página de apresentação da Bistrô Connect, com os planos |
| `entrar.html` | Criar conta, criar a loja e aceitar convite de equipe |
| `loja.html` | Vitrine de cada loja: `seudominio/l/nome-da-loja` |
| `pedido.html` | Rastreio do pedido para o cliente (link secreto) |
| `painel/` | Painel da loja: pedidos ao vivo, financeiro, clientes, cardápio, dados da loja, equipe, link e plano do mês |
| `admin/` | Seu painel de dono da plataforma: todas as lojas, vendas do mês, plano e situação (ativa, suspensa, cancelada) |
| `assets/config.js` | Endereço e chave pública do Supabase da plataforma |
| `assets/efeitos.js` e `assets/efeitos.css` | Efeitos visuais (blocos que surgem, contadores, confete, cabeçalho de vidro, máscara de WhatsApp). Quem pede "reduzir movimento" no celular vê tudo parado |
| `crm/` | Seu painel de leads, orçamentos e plano de negócio (o mesmo do site oficial). Usa o mesmo Supabase da plataforma (tabelas em `supabase/03-crm.sql`); o `window.BISTRO` do `assets/config.js` já aponta para ele. Gerado por `ferramentas/montar-crm-plataforma.py` |
| `assets/vitrine-temas.css` | Os 3 temas da vitrine, inspirados nos sites de referência: **artesanal** (padaria, cafeteria, doceria), **brasa** (hamburgueria, pizzaria) e **autoral** (restaurante e outros). O tema vem do tipo escolhido ao criar a loja |
| `assets/exemplo.js` e `assets/img/exemplo/` | Cardápio de exemplo com fotos para cada tipo de loja (botão "Usar exemplo com fotos" no painel). Gerado por `ferramentas/montar-exemplos.py` |
| `termos.html` e `privacidade.html` | Termos de uso e Política de privacidade. Os dados da empresa vêm de `empresa` no `assets/config.js` |
| `assets/medicao.js` | Meta Pixel, Google Ads e Google Analytics, com aviso de cookies (LGPD) |
| `robots.txt` e `sitemap.xml` | Orientam o Google. A imagem de prévia do link (WhatsApp, Instagram) é `assets/img/og-bistro-connect.jpg`, gerada por `ferramentas/montar-kit-divulgacao.py` |
| `assets/nicho.js` | Página de vendas por nicho: `/?para=padaria`, `cafeteria`, `hamburgueria`, `restaurante`, `pizzaria`, `confeitaria`, `marmitaria` |
| `.htaccess` | Segurança e o endereço curto `/l/nome-da-loja` |
| `supabase/01-plataforma.sql` | Banco: tabelas, regras de acesso e funções |

O painel é gerado a partir de `paineis/loja/` pelo `ferramentas/montar-painel-plataforma.py`. Melhorias no painel das lojas entram na plataforma rodando esse script de novo.

## Como colocar no ar

### 1. Supabase (um projeto só para a plataforma)
1. Crie o projeto em supabase.com. No SQL Editor, cole e rode `supabase/01-plataforma.sql`.
2. **Authentication > Sign In / Providers > Email:** deixe o cadastro ligado (os empreendedores se cadastram sozinhos) e a confirmação de e-mail ligada.
3. **Authentication > URL Configuration:** em *Site URL*, coloque o endereço da plataforma (ex.: `https://app.bistroconnect.com.br`). Em *Redirect URLs*, adicione `https://app.bistroconnect.com.br/entrar.html*` (com o asterisco, para os links de confirmação, de nova senha e de convite).
4. **Authentication > Multi-Factor:** confira se o TOTP (aplicativo autenticador) está ligado. Ele já vem ligado.
5. Se o plano tiver a opção, ligue a proteção contra senhas vazadas.
6. Crie a **sua** conta pelo `entrar.html` e torne-se administrador da plataforma. Rode no SQL Editor, trocando o e-mail:
   `insert into public.plataforma_admins (user_id) select id from auth.users where email = 'seu-email@exemplo.com';`

### 2. Configuração
Em `assets/config.js`, preencha `supabaseUrl` e `supabaseKey` (Project Settings > API, chave **anon public**). Preencha também `suporteWhatsapp` e `site`, que é o endereço da plataforma sem barra no fim.

### 3. Hostinger
A plataforma precisa ficar **na raiz** de um domínio ou subdomínio, por causa do endereço `/l/nome-da-loja`. O mais simples é criar o subdomínio `app.bistroconnect.com.br` no hPanel e subir o conteúdo desta pasta (sem a pasta `supabase/`) para a pasta dele. Depois, ative o SSL.

**Capacidade:** a hospedagem compartilhada só entrega arquivos. Pedidos, login e regras rodam no Supabase. Por isso ela aguenta bem mais que 20 lojas. O limite real é o plano do Supabase (no plano gratuito, o projeto pausa se ficar uma semana sem uso).

## Campanhas (Meta Ads e Google Ads)
1. **Códigos no `assets/config.js`:** `pixelId` (Meta), `googleAdsId` (começa com `AW-`), `googleAdsRotuloLoja` e `googleAdsRotuloLead` (o texto depois da barra na tag da conversão) e `googleAnalyticsId` (começa com `G-`). Vazio = desligado.
2. **Nada carrega antes do "Aceitar"** no aviso de cookies (LGPD).
3. **Eventos enviados:**

   | Momento | Meta | Google |
   |---|---|---|
   | Conta criada | `CompleteRegistration` | `sign_up` |
   | **Loja criada (conversão principal)** | `StartTrial` + `LojaCriada` | `loja_criada` + conversão `googleAdsRotuloLoja` |
   | Formulário "Quero ajuda" ou chat | `Lead` | `generate_lead` + conversão `googleAdsRotuloLead` |
   | Clique no WhatsApp | `Contact` | `contact` |

4. **Link de cada anúncio:** use a página do nicho e as UTMs, por exemplo
   `https://seudominio.com.br/?para=hamburgueria&utm_source=meta&utm_medium=pago&utm_campaign=burger-pg`.
   No Google Ads, ligue a marcação automática (gclid) e use `?para=padaria` no URL final.
5. **De onde veio cada loja:** a origem (fonte, campanha, termo, gclid) é gravada na loja e aparece na coluna **Origem** do seu painel `/admin/` e no CSV. Os leads do formulário chegam no CRM com a origem.
6. **No texto do anúncio, não use a marca "iFood".** Use "app de delivery".

## Segurança (vale no banco, não depende da tela)
- **Separação entre lojas:** toda linha de cardápio, pedido e equipe é marcada com a loja dona. Os testes confirmam que uma loja não vê nem altera nada de outra, nem usa a categoria de outra.
- **Funções:**
  - **Dono:** tudo.
  - **Gerente:** tudo, menos a equipe e a conta.
  - **Atendente:** pedidos, pagamentos e clientes, e pode pausar os pedidos.
  - **Cozinha:** só pedidos, sem pagamento.
- **Login em 2 etapas:** o banco exige para dono e gerente mudarem cardápio, loja ou equipe. O painel exige de todos.
- **Pedido protegido:** o preço é recalculado no banco, com taxa, pedido mínimo, formas de pagamento da loja, entrega ou retirada, limite contra robôs e proteção contra clique duplo.
- **Itens e valores travados:** a equipe não altera itens nem valores de um pedido. Muda só status, pagamento e anotações, e cada mudança fica no histórico com quem fez.
- **Rastreio sem dados pessoais:** o link de rastreio não mostra telefone nem endereço.
- **Fotos separadas:** cada loja tem a própria pasta (até 5 MB, só JPG, PNG ou WebP).
- **Seu painel:** só abre para quem está em `plataforma_admins` e entrou com 2 etapas.

## Preço pelo faturamento
A tabela `planos` define as faixas (Começo grátis até R$ 3 mil; Crescendo R$ 49 até R$ 10 mil; Forte R$ 99 até R$ 30 mil; Sem limites R$ 199). Para mudar valores, edite a tabela no Supabase. O plano do mês é calculado pelo que a loja vendeu na plataforma (pedidos não cancelados).

## Próximas fases
1. **Cobrança automática (Asaas):** assinatura mensal pela faixa do mês, aviso de vencimento e suspensão automática por falta de pagamento (precisa de conta Asaas com CNPJ).
2. **Pix no pedido**, cupons, fidelidade, tela da cozinha, taxa de entrega por bairro e horário de funcionamento automático.
3. **App instalável (PWA)** e domínio próprio por loja.
4. **Revisão jurídica** dos Termos de uso e da Política de privacidade (as páginas já existem; peça a um advogado para revisar antes de escalar as campanhas).
