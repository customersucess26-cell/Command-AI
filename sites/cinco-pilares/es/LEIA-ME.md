# Los 5 Pilares · página de vendas v17 (espanhol)

Conceito: **"Amanecer en cinco columnas"**. A página é uma caminhada da noite ao amanhecer dentro de um templo de cinco colunas. No topo, uma coluna está rachada (o Pilar Ancla). No fechamento, as cinco estão de pé, na luz da manhã.

## Arquivos

```
index.html            a página (texto, estrutura e configuração)
assets/site.css       visual
assets/app.js         preço, checkout com UTM, píxel, teste, contagem, animações
assets/scene.js       cena das colunas em canvas (topo e fechamento), desenhada ao vivo
assets/vendor/        GSAP 3.12.5, ScrollTrigger e Lenis 1.1.13 (locais, sem CDN)
assets/img/           logo, telas reais do sistema, fotos dos pilares, og.jpg, icon.png
```

Publicar: suba a pasta `es/` inteira. Não há etapa de build.

## Configuração (no `index.html`, bloco `<script id="cfg">`)

| Campo | Uso |
|---|---|
| `preco`, `moeda` | Preço exibido em toda a página |
| `precoDe` | Preço riscado. Só aparece se for maior que `preco` |
| `precoDepois` + `prazo` | Barra de lançamento e contagem regressiva. Só aparecem com data futura (`2026-12-01T23:59:00-03:00`) e preço posterior maior |
| `checkout` | Link do Hotmart. As UTMs da visita (`utm_*`, `fbclid`, `src`, `sck`) são repassadas, e o teste acrescenta `quiz-<pilar>` no `sck` |
| `pixel` | ID do píxel da Meta (PageView, ViewContent, QuizStart, Lead, InitiateCheckout) |
| `depoimentos` | `[{"nome":"...","local":"...","texto":"..."}]`. A seção de prova social só aparece com dados reais |
| `prints` | Lista de imagens (`assets/img/...` ou `https://...`) de mensagens reais |

## Trocar as fotos dos 5 pilares

Os painéis da biblioteca usam `assets/img/pilar-salud.webp`, `pilar-relaciones.webp`, `pilar-carrera.webp`, `pilar-finanzas.webp` e `pilar-espiritualidad.webp`. Hoje são as fotos pequenas da v16 (520 px), com tratamento escuro para disfarçar a resolução.

Para usar a colagem nova (mulher no amanhecer, família abraçada, executivo diante da cidade, moedas com a planta, alpinista no cume): salve cada foto separada em WebP, com pelo menos 900 px de largura e formato vertical (3:4 ou 2:3), usando os mesmos nomes. Os painéis cortam com `object-fit: cover`, então mantenha o rosto ou o assunto no centro.

## Prompts das imagens (para quando houver créditos de geração)

Na produção desta versão, os geradores conectados (Higgsfield, OpenArt, Morphix e Kairogen) estavam no plano grátis ou sem saldo. Por isso o templo foi feito em código. Se quiser fotos no lugar da cena, gere estas:

1. **Topo, 16:9 e 9:16:** Five monumental travertine stone columns in a row inside a vast dark ancient hall before dawn, one column with a deep visible crack, a single shaft of warm volumetric light from a high opening on the left, floating dust, columns in the right two thirds, empty dark negative space on the left, cinematic lighting, 35mm, low angle, Kodak Vision3 film grade, warm honey highlights, deep blacks, photorealistic stone, high-end editorial architectural photography, no people, no text.
2. **Rachadura, 4:5:** Extreme close-up of a cracked pale marble column, golden light leaking through the fissure from inside the stone, dust in the air, 85mm macro, shallow depth of field, chiaroscuro, photorealistic marble, luxury editorial still life.
3. **Fechamento, 16:9 e 9:16:** Five restored travertine columns in an ancient hall at sunrise, golden volumetric god rays between them, warm haze, hopeful and majestic, cinematic wide shot, 35mm, Kodak Vision3, photorealistic, no people, no text.
4. **Pilares, 3:4 (um por cor: verde-esmeralda, violeta, âmbar, azul-ciano, índigo):** A single monumental travertine column in a pitch dark hall lit by one beam of soft [cor] volumetric light from above, dust in the beam, chiaroscuro, 50mm, photorealistic stone, film grain, fine art photography.

## Acessibilidade e movimento

- Quem tem "reduzir movimento" ativado no aparelho, ou abre com `?fx=0`, vê a página estática e completa. Para forçar os efeitos: `?fx=1`.
- O teste funciona por teclado, anuncia cada pergunta e o resultado (`aria-live`) e não envia nada para fora do navegador.
- A rolagem suave (Lenis) e as seções fixas só funcionam no desktop com mouse. No celular, a rolagem é nativa e o sistema vira um carrossel de toque.

## O que mudou em relação à v16

- A primeira dobra agora é uma cena (o templo com o Pilar Ancla rachado), não a captura do painel.
- O teste grátis virou o botão principal do topo e o centro da página. O resultado desenha os cinco pilares e abre o livro do pilar âncora.
- A faixa de compra que se repetia cerca de 8 vezes foi substituída por CTAs nos pontos de decisão e uma barra fixa no celular depois do teste.
- As telas reais do sistema passam em rolagem horizontal fixa no desktop.
- Cerca de 300 KB na primeira tela e uns 700 KB com todas as imagens, contra 2 MB da v16. As imagens ficam fora do HTML e carregam sob demanda.
- Sem A/B de headline (`?v=c`): a v16 trazia um título alternativo que não estava no arquivo. Ainda dá para reativar.
