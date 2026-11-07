---
name: site-premium-gastronomia
description: Como construir e publicar os sites premium da Bistrô Connect e da Mr. Connect (página de vendas, sites de nicho, cardápios e briefing) com os efeitos de movimento, o padrão visual grafite e champagne e a checagem de mobile (iOS e Android). Use quando for criar, alterar ou revisar uma página ou um site de restaurante, hamburgueria, pizzaria, padaria ou cafeteria.
---

# Site premium de gastronomia (Bistrô Connect)

Este guia reúne o que foi aprendido ao montar a página `sites-personalizados/index.html` (publicada em `/gastronomia/`), os modelos de nicho e o motor. Siga na ordem. Cada etapa aponta o arquivo onde a coisa acontece.

## 1. Princípios

- **Uma página, um arquivo.** O HTML é único (CSS e JS inline). As imagens ficam em `img/` como WebP e são carregadas sob demanda.
- **Premium é contenção.** Grafite `#120d0a`/`#111`, champagne `#D9AE5C`/`#E3C68E`, off-white `#F3EFE6`/`#F5F2EC`. Pouco brilho, muito espaço, tipografia firme (Poppins para títulos, DM Sans para textos, Fraunces para detalhes em itálico).
- **Só prometer o que está construído.** Nada de "grátis", resultados garantidos ou depoimentos inventados (ver `manual/manual-de-operacao.md`, seção 3).
- **Nunca chamar o cliente de "casa".** Em toda copy (site, proposta, CRM, scripts, PDFs), o negócio do cliente é "sua marca", "seu negócio" ou "seu empreendimento" ("WhatsApp do seu negócio", "identidade da sua marca", "tipo de negócio"). Ficam como estão só os nomes de pratos ("molho da casa", "Suprema da Casa") e o nome da oferta antiga "Casa Cheia".
- **Respeitar `prefers-reduced-motion`.** Todo efeito tem uma versão parada. Quem desligou animações no sistema deve ver a página completa, sem movimento.

## 2. Estrutura da página (ordem das seções e IDs)

Mantenha os IDs: são usados por links, por menu e pelo rastreio de cliques.

| Seção | ID | Efeito principal |
|---|---|---|
| Hero | `.hero` | Vitrine 3D (notebook + celular) com troca de modelos a cada 6 s |
| Manifesto | `#manifesto` | Palavras que acendem com a rolagem, jornada com ponto de luz |
| Duas soluções | `#solucoes` | Cartões com demonstrações que alternam (`.dx-rot`) |
| Signature | `#signature` | Processo em cartões, etapa ativa que percorre, briefing (`#briefing-signature`) |
| Gastronomia | `#gastronomia` | Demonstrações e troca por rolagem |
| Cardápios | `#pfStage` | Carrossel 3D (`#pfModels`) com palco vivo e cápsula com contador |
| Planos | `#planos` | Cartões com destaque no plano mais procurado |
| Contato | `#contato` | Formulário de lead (grava no CRM) |

O rodapé tem o "Acesso restrito" (link para `crm/`) e o Instagram. O WhatsApp fica só no botão flutuante.

## 3. Efeitos e onde mexer

| Efeito | Como funciona | Onde no código |
|---|---|---|
| Carrossel 3D dos cardápios | `data-pos` (-2 a 2) define transform e brilho; troca a cada 6 s (`vai()` + `setInterval`) | bloco "carrossel 3D dos celulares" + CSS `.models.pf .model[data-pos]` |
| Telas flutuando | `@keyframes pfFlutua` com `animation-delay` por posição | CSS "v12" (só em telas acima de 900 px) |
| Palco vivo | aura que muda de cor por cardápio (`AURA`), raios girando, ondas, traços, ingredientes e notificações | CSS "v13" (`.pf-fx`, `.pf-aura`, `.pf-palco`, `.pf-notif`) |
| Palco segue o mouse | `--mx`/`--my` no `#pfStage` | JS "palco dos cardápios acompanha o mouse" |
| Manifesto | palavras acendem pelo progresso `p` da rolagem | IIFE `#manifesto` |
| Processo Signature | `act`/`past` a cada 3,8 s, ponto `.rl-dot` percorre a linha | IIFE "processo Signature" + CSS "v8" |
| Vitrine do hero | `.v-stage` com perspectiva, `--rx`/`--ry` pelo mouse | CSS `.v-3d`, `.mbp` |
| Revelação ao rolar | classe `dx-on` com IntersectionObserver (**nunca** `in`, que colide com `.in`) | IIFE final de seções 3, 4 e 9 |
| Cartão Gastronomia | `.dx-rot` mostra só a demonstração da vez (`.on`) | IIFE "cartão Gastronomia" |

**Regra de ouro do movimento:** pausar quando a seção não está na tela (`data-live` e `IntersectionObserver`), para não gastar bateria no celular.

## 4. Imagens

- Converta com `ferramentas/extrair-imagens-webp.py` (tira o base64 do HTML e grava WebP em `img/`, máximo de 1400 px).
- Primeira imagem da vitrine: `fetchpriority="high"`, sem `loading="lazy"`. As demais: `loading="lazy"` e `decoding="async"`.
- Ícones: `img/favicon-32.png`, `favicon-512.png` e `apple-touch-icon.png` (180 px, sem arredondar: o iOS arredonda sozinho). Gere a partir do "B" da logo atual.
- Depois de mexer em imagem: rode `python3 ferramentas/csp.py sites-personalizados/index.html` (recalcula os hashes de script da CSP; sem isso os efeitos param).

## 5. Mobile (iOS e Android)

Blocos usados no `@media (max-width:640px)` da v11:
- Topo de vidro com `backdrop-filter` e `env(safe-area-inset-top)` para o recorte da câmera.
- `theme-color` `#120d0a` e `apple-mobile-web-app-*` para a barra do navegador e a tela inicial.
- Botões com altura mínima de 52 px (toque), cantos de 16 px.
- Campos de formulário com `font-size:16px` (o iPhone dá zoom abaixo disso) e `inputmode` correto.
- Botões flutuantes pequenos (WhatsApp 52 px; Bia sem texto), com `env(safe-area-inset-bottom)`.
- Rodapé com `padding-bottom` extra para não ficar atrás dos flutuantes.
- Vitrine do hero com moldura e abas num só trilho deslizante.

Teste em 390 × 844 com `deviceScaleFactor:2` e `isMobile:true`. Confira também 360 px (Android comum) e 768 px (tablet).

## 6. Formulários e CRM

- Formulário de contato (`#leadForm`) e briefing Signature (`#sigForm`) **gravam no CRM** (POST em `/rest/v1/leads`, chave anon) e **não abrem o WhatsApp sozinhos**. A confirmação aparece no lugar do formulário.
- Se o banco recusar, mostrar a mensagem com código e um link "Falar pelo WhatsApp".
- A função `leads_limite` do banco aceita no máximo 3 envios por WhatsApp por dia e exige `stage:'lead'`, nome e WhatsApp com 10 a 13 dígitos.
- Leads de site entram com `linha:'sites'`. O CRM de Mr. Connect (`sites-personalizados/crm/`) mostra só esses.

## 7. Checagem antes de entregar

1. `node` com Playwright: abrir a página, rolar até o fim e contar imagens quebradas (devem ser zero, exceto as externas da consultoria).
2. Bateria de testes `/tmp/ot/t_matriz.js` ou equivalente: 26 checagens (imagens, botões, formulário, CSP, âncoras, Pixel, Bia, rodapé). Uma falha só é aceitável se for mudança proposital, e precisa ser dita.
3. Desktop 1440 × 900: confirmar a troca dos cardápios e a inclinação pelo mouse.
4. Mobile 390 × 844: rolar a página inteira em telas de 760 px e olhar cada uma.
5. Rodapé com a versão nova (`Versão DD/MM/AAAA-x`). Assim o usuário confirma qual arquivo está no ar.
6. `reduced-motion` ligado: a página precisa aparecer completa e sem movimento.

## 8. Entrega ao cliente

- Gere o pacote com `git commit` + `zip` só dos arquivos que mudaram (ex.: `index.html`, `img/`), e diga o caminho exato na Hostinger (`public_html/gastronomia/`).
- Diga que a pasta `crm/` não é alterada quando for só a página.
- Não envie tokens nem chaves `service_role` por chat. Só a chave anon aparece no `assets/config.js`.

## 9. Modelos de nicho e motor

Para clientes de restaurante, hamburgueria, pizzaria ou padaria, o fluxo é outro: modelo + `config.js` + motor. Veja `clientes/LEIA-ME.md` e `ferramentas/novo-cliente.py`. O site lê cardápio, pedidos e rastreio do banco da plataforma; o HTML do modelo não é editado por cliente.

## 10. Armadilhas já vividas

- Classe `.in` é do container da página. Revelação com `in` estreita os cartões. Use `dx-on`.
- Um `replace` de regex em bloco de script pode corromper o JS ("Invalid or unexpected token"). Edite só o HTML e o `<style>`.
- Cartão Gastronomia com 8 imagens animando ao mesmo tempo travou em computadores fracos: só a demonstração da vez fica visível.
- Reflexo com `-webkit-box-reflect` ficou feio e pesado: não usar.
- Sem `reduced-motion`, o movimento pode incomodar quem tem sensibilidade; sempre oferecer a versão parada.
- O navegador guarda o ícone e o CSS antigos. Peça Ctrl + F5 ou janela anônima ao testar.
