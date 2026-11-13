# Los 5 Pilares · página de vendas v17 (espanhol)

Modelo: **sequência cinematográfica controlada pela rolagem** (no estilo das vitrines "scroll cinematic"). A página abre com a foto da torre em tela cheia, e a câmera sobe andar por andar (Espiritualidad, Finanzas, Carrera, Relaciones e Salud) com uma frase grande para cada pilar. No fim, a câmera recua, o andar de Finanzas apaga e racha (o Pilar Ancla) e os botões levam ao teste ou ao checkout. Depois vem a página de vendas, escura e dourada. A câmera fica em `assets/app.js` (função `cinema`, pontos `FL`). Para trocar a foto por um vídeo de IA, gere-o a partir de `assets/img/torre.webp`.

## Arquivos

```
index.html            a página (texto, estrutura e configuração)
assets/site.css       visual
assets/app.js         preço, checkout com UTM, píxel, teste, contagem, animações
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

## Fotos dos 5 pilares

Os andares da biblioteca usam `assets/img/piso-salud.webp`, `piso-relaciones.webp`, `piso-carrera.webp`, `piso-finanzas.webp` e `piso-espiritualidad.webp`, recortados dos cômodos da foto da torre (cerca de 850 × 130 px cada). Para mais nitidez, gere cada cômodo separadamente em formato panorâmico (cerca de 2400 × 500 px) e salve com os mesmos nomes.

## Prompts das imagens (para quando houver créditos de geração)

Na produção desta versão, os geradores conectados (Higgsfield, OpenArt, Morphix e Kairogen) estavam no plano grátis ou sem saldo. Por isso a torre foi feita em código (SVG). Prompts para versões fotográficas:

1. **Topo, 9:16 e 4:5:** A cylindrical tower of five stacked glass rooms separated by glossy colored rings (emerald green at the base, then cyan blue, amber, violet, indigo at the top), each room softly lit from inside with warm light and plants on the edges, a lush green tree growing on the top floor, standing on a hilltop at golden hour, low sun on the right, volumetric light, cinematic, photorealistic architectural visualization, Kodak Vision3 grade, no text, no labels.
2. **Versão Pilar Ancla:** the same tower at dusk, the cyan blue ring (second from the bottom) dull and cracked with golden light leaking through the crack, the rooms above it slightly tilted and dim, the base room lit, dramatic chiaroscuro, photorealistic, no text.
3. **Fechamento, 16:9:** the same tower fully restored at sunrise, all five rings glowing, every room lit with warm interior light, golden god rays, misty valley behind, hopeful and majestic, cinematic wide shot, photorealistic, no text.
4. **Cômodos (um por pilar, 3:4):** interior of a round glass room at golden hour seen from outside: [Salud: a person stretching beside fresh fruit] [Finanzas: a tidy desk with a notebook and coins] [Carrera: a person working at a laptop by the window] [Relaciones: a family sharing a meal] [Fe: a person reading a Bible in quiet light], warm practical lights, plants, cinematic, photorealistic, no text.

## Acessibilidade e movimento

- Quem tem "reduzir movimento" ativado no aparelho, ou abre com `?fx=0`, vê a página estática e completa. Para forçar os efeitos: `?fx=1`.
- O teste funciona por teclado, anuncia cada pergunta e o resultado (`aria-live`) e não envia nada para fora do navegador.
- A rolagem suave (Lenis) e as seções fixas só funcionam no desktop com mouse. No celular, a rolagem é nativa e o sistema vira um carrossel de toque.

## O que mudou em relação à v16

- A primeira dobra agora é a torre dos 5 pilares, com o Pilar Ancla rachado, e não a captura do painel.
- O teste grátis virou o botão principal do topo e o centro da página. O resultado desenha os cinco pilares e abre o livro do pilar âncora.
- A faixa de compra que se repetia cerca de 8 vezes foi substituída por CTAs nos pontos de decisão e uma barra fixa no celular depois do teste.
- As telas reais do sistema passam em rolagem horizontal fixa no desktop.
- Cerca de 300 KB na primeira tela e uns 700 KB com todas as imagens, contra 2 MB da v16. As imagens ficam fora do HTML e carregam sob demanda.
- Sem A/B de headline (`?v=c`): a v16 trazia um título alternativo que não estava no arquivo. Ainda dá para reativar.

## Proteção contra clonagem em moldura

A página não se esconde mais quando aberta dentro de outra página, porque isso deixava a prévia em branco. Para impedir que outro site a exiba em moldura, configure na hospedagem (Apache, no `.htaccess`):

```
Header always set Content-Security-Policy "frame-ancestors 'self'"
Header always set X-Frame-Options "SAMEORIGIN"
```
