# Entrega de site premium (Site Gastronômico e Digital Experience)

Cada cliente recebe um **site exclusivo no domínio dele**, feito a partir de um dos modelos, com o **painel completo**
(pedidos ao vivo, cardápio, clientes, financeiro, WhatsApp, cupons, mesas com QR, taxa por bairro) e o
**rastreio do pedido** no próprio domínio. Tudo isso roda no **motor Bistrô Connect**: um banco só (o Supabase da
plataforma) para todos os clientes. Cada loja só enxerga os próprios dados.

O HTML do modelo **não é editado**. Tudo que muda de um cliente para outro fica em `assets/config.js`, que o
gerador escreve a partir do briefing.

## Modelos

| Modelo | Pasta | Ligado ao motor |
|---|---|---|
| `hamburgueria` | `sites/hamburgueria-bruto` | sim (piloto) |
| `pizzaria` | `sites/pizzaria-fornalha` | próxima etapa |
| `restaurante` | `sites/ambar` | próxima etapa |
| `padaria` | `sites/padaria-cafe` | próxima etapa |

## Passo a passo

1. **Motor (uma vez só).** A plataforma precisa estar no ar (veja `plataforma/LEIA-ME.md`, item 1). Copie
   `clientes/motor.exemplo.json` para `clientes/motor.json` e preencha a URL e a chave **anon** do Supabase da
   plataforma. Esse arquivo não vai para o Git.
2. **Loja no banco.** Em `app.bistroconnect.com.br/entrar.html`, crie a loja do cliente com o **mesmo endereço (slug)**
   que vai no briefing (ex.: `forno-do-ze`). No painel, em **Equipe › Convidar pessoa**, convide o dono da casa
   pelo e-mail dele. Ele cria a senha e passa a entrar em `dominiodocliente.com.br/admin/`.
3. **Cardápio, bairros e pagamentos** ficam no painel (aba Cardápio e Dados da loja). O site lê de lá: o que o
   cliente mudar no painel aparece no site na hora. Categorias com "Acompanhamentos", "Bebidas", "Porções" ou
   "Extras" no nome vão para a lista lateral; "Combos" vai para o bloco de combos; produtos com destaque vão para
   "Os mais pedidos". Blocos sem produtos somem sozinhos.
4. **Briefing → JSON.** Copie `clientes/exemplo-briefing.json` para `clientes/<slug>.json` e preencha com o que o
   cliente mandou (nome, WhatsApp, domínio, cores, logo, textos, fotos, contato). Campo vazio = texto ou foto do modelo.
5. **Gerar.**
   ```
   python3 ferramentas/novo-cliente.py --dados clientes/forno-do-ze.json --fotos caminho/das/fotos
   ```
   As fotos vão para `img/cliente/` (o nome do arquivo vira minúsculo e sem acento). No JSON, use
   `"img/cliente/hero.jpg"` etc. Sai `entregas/<slug>/site/` e `entregas/<slug>.zip`. No fim, o gerador lista o que
   ainda falta (WhatsApp, domínio, depoimentos de exemplo).
6. **Revisar** abrindo `entregas/<slug>/site/index.html` e mandar o link de prévia ao cliente.
7. **Publicar.** Na Hostinger do cliente, envie o conteúdo do zip para a `public_html` (o site fica na **raiz** do
   domínio; para outra pasta, gere com `--caminho /pasta/`). Ative o SSL. Teste um pedido de ponta a ponta:
   site → WhatsApp → painel → rastreio.

## Textos que podem ser trocados (modelo hamburgueria)

`carregando`, `logo`, `logoSub`, `hero.selo`, `hero.l1`, `hero.l2`, `hero.l3a`, `hero.l3b`, `hero.l4`, `hero.texto`,
`hero.n1` / `hero.n1txt`, `hero.n2` / `hero.n2txt`, `hero.n3` / `hero.n3txt` (números do topo), `faixa` (lista de
palavras que passam na faixa), `camadas.selo`, `camadas.t1`, `camadas.t2`, `camadas.t3`, `camadas.texto`,
`cardapio.selo`, `cardapio.t1`, `cardapio.t2`, `cardapio.texto`, `favoritos.selo`, `favoritos.t1`, `favoritos.t2`,
`combos.selo`, `combos.t1`, `combos.t2`, `combos.texto`, `depoimentos.selo`, `depoimentos.t1`, `depoimentos.t2`,
`depoimento1.texto` / `depoimento1.nome` (até 3), `visite.t1`, `visite.t2`, `visite.texto`, `rodape.copy`, `rodape.frase`.

Opcionais (tamanho, tipo de leite, adicionais) cadastrados no painel abrem uma janela de escolha no próprio site.

Fotos (`imagens`): `hero`, `fogo` (foto do bloco "Visite"), `batata` (foto ao lado dos acompanhamentos).
Cores (`marca.cores`): `ember` (destaque), `red`, `mustard`, `bg`, `bg2`, `cream` (texto), `muted`, `line`.

**Depoimentos:** os do modelo são exemplos. Use só depoimentos reais (com autorização) ou coloque
`"depoimentos"` em `ocultar`.

## Peças (para manutenção)

| Peça | Fonte | Vai para |
|---|---|---|
| Motor (cardápio, pedido, rastreio) | `paineis/motor/motor.js` | `assets/motor.js` |
| Marca (textos, fotos, cores, fontes) | `paineis/motor/marca.js` | `assets/marca.js` |
| Rastreio | `plataforma/pedido.html`, `assets/pedido.js`, `pedido.php`, `pedido-lib.php` | raiz do site |
| Painel | `plataforma/painel/` | `admin/` |

Melhorou o painel ou o rastreio na plataforma? Gere de novo os clientes para levar a melhoria a eles.
