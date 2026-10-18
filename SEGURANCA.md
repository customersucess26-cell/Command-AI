# eBistrô: segurança do site e do painel

Guia para colocar o site oficial na Hostinger com as proteções ligadas e repetir o mesmo nos sites de nicho.

## O que já está pronto neste repositório

| Camada | Arquivo | O que protege |
|---|---|---|
| Política de conteúdo (CSP) dentro de cada página | `index.html`, `modelos/*.html` (gerada por `ferramentas/csp.py`) | Bloqueia script injetado por invasor (XSS). Testado: script e `onerror` injetados não rodam |
| Cabeçalhos do servidor | `.htaccess` (raiz) | HTTPS obrigatório (HSTS), anti-clickjacking, `nosniff`, `Referrer-Policy`, `Permissions-Policy` (câmera, microfone e localização desligados), só GET/HEAD/POST/OPTIONS |
| Arquivos internos fora do ar | `.htaccess` (raiz) | `.git`, `.md`, `.py`, `.sql`, backups, `ferramentas/` e `supabase/` devolvem 403 |
| Painel (Acesso restrito) | `admin/` | Login com 2 etapas obrigatório (app autenticador). Sessão só na aba aberta, saída automática após 30 min parado, bloqueio após 5 senhas erradas. Dados exibidos sem risco de XSS. Biblioteca do Supabase servida do próprio site (sem CDN de terceiros) |
| Servidor do painel | `admin/.htaccess` | Fora do Google (`noindex`), sem cache, sem `Referer`, espaço para senha do servidor e trava por IP |
| Formulário de lead | `index.html` | Campo-armadilha e tempo mínimo contra robôs, limite de tamanho, 1 envio a cada 30 s, aviso de uso dos dados |
| Meta Pixel (LGPD) | `index.html` | Só carrega depois de o visitante tocar em "Aceitar". Sem Pixel configurado, o aviso não aparece |
| Banco de dados | `supabase/01-admins.sql`, `02-leads-ebistro.sql`, `03-loja-pedidos.sql` | Visitante só cria lead ou pedido e não lê nada. Só administradores veem os dados. Os leads exigem login com 2 etapas também no banco. Preço e total recalculados no banco. Limite de envios contra robôs |

Todos esses itens foram testados aqui: o `.htaccess` num Apache 2.4 real, as páginas no Chromium e o SQL num PostgreSQL 16 com as funções do Supabase simuladas. Veja "Testes executados" no fim.

## Passo a passo na Hostinger

1. **Ative o SSL** do domínio: hPanel > Segurança > SSL. Isso tem que vir antes do passo 2, porque o `.htaccess` obriga HTTPS.
2. **Envie os arquivos** para `public_html`: `index.html`, `.htaccess` e a pasta `assets/`. Não envie `ferramentas/`, `supabase/` nem os `.md` (mesmo se enviar por engano, o `.htaccess` bloqueia).
3. **Painel (Acesso restrito):** envie a pasta `admin/` inteira, com `index.html`, `painel.css`, `painel.js`, `img/`, `vendor/` e `.htaccess`. Ela abre em `seudominio.com.br/admin/`.
4. **Segunda senha no painel:** hPanel > Avançado > Proteger diretórios com senha > escolha `public_html/admin`. Quem tentar abrir o painel precisa passar por essa senha antes da tela de login.
5. **Preencha `assets/config.js`** com o WhatsApp (só dígitos, com 55) e, se usar, o Pixel e o Supabase. Use só a chave **anon** do Supabase, **nunca** a `service_role`.
6. **Confira:** abra https://securityheaders.com e teste o seu domínio. O resultado esperado é nota A.

## Passo a passo no Supabase

1. Authentication > Sign In / Providers: **desligue "Allow new users to sign up"**. Só você cria usuários.
2. Authentication > Users: crie o seu usuário. Em Authentication > Multi-Factor, confira se **TOTP** está ativo. No primeiro login, o painel mostra um QR Code para você ler com o Google Authenticator (ou similar). Depois disso, todo login pede o código de 6 números.
3. Authentication > Attack Protection (ou Policies): ligue a **proteção contra senhas vazadas** e use senha com 12 caracteres ou mais.
4. SQL Editor: rode, nesta ordem, `01-admins.sql`, `02-leads-ebistro.sql` e, na loja de cada cliente, `03-loja-pedidos.sql`.
5. Rode o `insert into public.admins ...` do fim do `01-admins.sql` com o seu e-mail. **Sem isso o painel não enxerga os leads.**
6. Os leads já exigem as 2 etapas no banco. Para exigir o mesmo nas lojas (`03-loja-pedidos.sql`), troque a função `eh_admin()` pela versão com `aal2`, comentada no `01-admins.sql`, mas só depois que o painel da loja também pedir o código.
7. Database > Backups: confira se o backup diário está ligado.

## Sites de nicho (padaria, hamburgueria, restaurante...)

Para cada cliente:

1. Copie o `.htaccess` da raiz para a pasta do site do cliente. Se houver painel, copie também o `admin/.htaccess`.
2. Se editar algum `<script>` da página, rode `python3 ferramentas/csp.py caminho/da/pagina.html` antes de publicar. Sem isso, o script editado é bloqueado pela própria proteção.
3. Se o site tiver pedidos com Supabase, use **um projeto Supabase por cliente** (isolamento total) e rode `01-admins.sql` e `03-loja-pedidos.sql` nele.

## O que ainda depende de você

- **Painel `admin/`:** antes de conectar o Supabase, ele abre em modo demonstração, com dados fictícios e nada salvo. Para usar com dados reais, siga os passos do Supabase acima.
- **Modelo padaria:** no arquivo atual, o login do painel é só de demonstração e fica no navegador. Proteção real exige ligar o Supabase no código-fonte Next.js (que também não está aqui) e aplicar o `03-loja-pedidos.sql`. Os usuários criados pelo painel precisam entrar na tabela `admins`.
- **Chat da Bia com IA (`aiUrl`):** se usar, a chave da IA tem que ficar só na função do servidor, com limite de mensagens por visitante.

## Sobre "segurança da NASA"

Não existe site impossível de invadir. O que existe é fechar todas as portas conhecidas e ter um plano para quando algo der errado. Com o que está acima, o site segue as recomendações atuais da OWASP (CSP, cabeçalhos, RLS, 2 etapas, mínimo privilégio, limite de envios). O que mais pesa daqui em diante:

1. **Login em 2 etapas** em tudo: Hostinger, Supabase, GitHub, e-mail e Meta Business.
2. **Senhas únicas** num gerenciador de senhas (Bitwarden, 1Password).
3. **Nunca colocar a chave `service_role`** do Supabase em arquivo do site.
4. **Backup** ligado e testado de vez em quando.
5. Rever os acessos a cada 3 meses: tirar da tabela `admins` quem não trabalha mais com você.

## Testes executados

| Teste | Resultado |
|---|---|
| `.htaccess` no Apache 2.4.58: sintaxe | ✅ Syntax OK |
| HTTP → HTTPS | ✅ 301 |
| `index.html`, modelos, `assets/config.js` | ✅ 200 |
| `AUDITORIA.md`, `ferramentas/csp.py`, `.htaccess`, `.git/config`, listagem de `modelos/` | ✅ 403 |
| Método DELETE | ✅ 403 |
| Cabeçalhos HSTS, CSP, X-Frame-Options, nosniff, Referrer, Permissions, COOP, CORP | ✅ Presentes |
| `admin/`: `noindex` e `no-store` | ✅ Presentes |
| As 4 páginas no Chromium, com todos os cabeçalhos e a CSP | ✅ Carregam sem erro |
| XSS simulado (script e `<img onerror>` injetados) | ✅ Bloqueado pela CSP |
| Fluxos da padaria, da hamburgueria e do formulário de lead, refeitos com a CSP ligada | ✅ Passaram |
| Pixel antes e depois do "Aceitar"; aviso não volta depois da escolha | ✅ |
| Robô (campo-armadilha preenchido e envio instantâneo) | ✅ Ignorado |
| SQL: visitante lê leads ou pedidos, altera preço | ✅ Negado |
| SQL: lead fora do formato; 4º lead do mesmo WhatsApp no dia | ✅ Recusado |
| SQL: pedido com preço adulterado (R$ 0,01) | ✅ Gravado com o preço do banco: 2 × R$ 12,90 + R$ 8,00 de taxa = R$ 33,80 |
| SQL: produto pausado; quantidade 1000 | ✅ Recusado |
| SQL: usuário logado que não é admin | ✅ Vê 0 leads e não altera nada |
| SQL: rodar os 3 arquivos duas vezes | ✅ Sem erro |

| Painel: senha errada, cadastro da 2ª etapa, código errado, entrada, edição de lead e saída (Supabase simulado no navegador) | ✅ Nenhum dado aparece antes da 2ª etapa; sessão fica só na aba (`sessionStorage`) |
| Painel: nome de lead com código malicioso (`<img onerror>`) | ✅ Exibido como texto, não executa |
| Painel no celular (390 px) | ✅ Sem rolagem lateral |
| SQL: administrador logado só com senha (aal1) | ✅ Vê 0 leads; com 2 etapas (aal2) vê todos |

Não testado aqui: Supabase real (Auth, MFA e Storage) e o LiteSpeed da Hostinger. As diretivas usadas são compatíveis com ele, mas confira no securityheaders.com depois de publicar.
