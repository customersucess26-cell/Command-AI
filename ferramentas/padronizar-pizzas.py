"""Padroniza fotos de pizza: recorta a pizza (pela transparência ou pelo contorno redondo) e coloca todas
no mesmo fundo de ardósia, centralizadas, do mesmo tamanho, com a mesma sombra e a mesma luz.
Uso: python3 ferramentas/padronizar-pizzas.py <pasta-saida> origem1=nome1 origem2=nome2 ...
Saída: <pasta-saida>/<nome>.jpg, 720 × 720."""
import sys, os
import numpy as np, cv2
from PIL import Image, ImageFilter, ImageDraw

S = 720
OCUPA = 0.84          # diâmetro da pizza em relação ao quadro
saida = sys.argv[1]
os.makedirs(saida, exist_ok=True)


def ardosia():
    rng = np.random.default_rng(7)
    base = np.full((S, S, 3), (30, 29, 28), np.float32)
    ruido = cv2.GaussianBlur(rng.normal(0, 1, (S, S)).astype(np.float32), (0, 0), 2.2) * 9
    veios = cv2.GaussianBlur(rng.normal(0, 1, (S, S)).astype(np.float32), (0, 0), 18) * 14
    base += (ruido + veios)[..., None]
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    luz = np.exp(-(((xx - S * .28) ** 2 + (yy - S * .22) ** 2) / (2 * (S * .55) ** 2)))   # luz quente do alto à esquerda
    base += luz[..., None] * np.array([26, 18, 10], np.float32)
    vinheta = 1 - .38 * (((xx - S / 2) ** 2 + (yy - S / 2) ** 2) / (S / 2) ** 2).clip(0, 1.6) / 1.6
    base *= vinheta[..., None]
    return Image.fromarray(base.clip(0, 255).astype(np.uint8))


FUNDO = ardosia()


def prepara(espec):
    """espec: arquivo[@x0,y0,x1,y1][:modo]. modos: v (separa pela luz, ignora prato), oval (pizza em perspectiva vira vista de cima),
    espelho (completa a parte de baixo cortada espelhando a de cima)."""
    modo = ''
    if ':' in espec: espec, modo = espec.split(':', 1)
    caixa = None
    if '@' in espec:
        espec, cx = espec.split('@'); caixa = tuple(int(v) for v in cx.split(','))
    im = Image.open(espec)
    if caixa: im = im.crop(caixa)
    if modo == 'espelho':
        a = np.array(im.convert('RGB')); h = a.shape[0]; cy = h // 2; corte = int(h * .82)
        for y in range(corte, h): a[y] = a[max(0, 2 * cy - y)]
        im = Image.fromarray(a)
    if modo == 'oval':
        rgb = np.array(im.convert('RGB')); v = cv2.GaussianBlur(cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)[..., 2], (7, 7), 0)
        _, m = cv2.threshold(v, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); c = max(cs, key=cv2.contourArea)
        (ex, ey), (ew, eh), ang = cv2.fitEllipse(c)
        eixoX, eixoY = (ew, eh) if abs(((ang + 45) % 180) - 45) < 45 else (eh, ew)
        k = max(eixoX, eixoY) / min(eixoX, eixoY)
        im = im.convert('RGB').resize((im.width, int(im.height * k)), Image.LANCZOS)
    if modo == 'v' and im.mode == 'RGBA':
        a = np.array(im); fundo = (a[..., 3] < 40) | (cv2.cvtColor(a[..., :3], cv2.COLOR_RGB2HSV)[..., 2] < 70)
        a[fundo] = (12, 12, 12, 255)
        im = Image.fromarray(a[..., :3])
    return im


def recorta(caminho):
    im = prepara(caminho)
    if im.mode == 'RGBA' and np.array(im)[..., 3].min() < 20:
        rgba = np.array(im)
        a = rgba[..., 3]
        _, m = cv2.threshold(a, 40, 255, cv2.THRESH_BINARY)
    else:
        rgb = np.array(im.convert('RGB'))
        g = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)[..., 2]
        g = cv2.GaussianBlur(g, (9, 9), 0)
        _, m = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        a = None
        rgba = np.dstack([rgb, np.full(rgb.shape[:2], 255, np.uint8)])
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cs, key=cv2.contourArea)
    (cx, cy), r = cv2.minEnclosingCircle(c)
    if a is None:
        # fundo escuro: a pizza é redonda, usa o círculo como máscara (um pouco para dentro)
        r = r * .985
        mask = np.zeros(m.shape, np.uint8)
        cv2.circle(mask, (int(cx), int(cy)), int(r), 255, -1)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        rgba[..., 3] = mask
    else:
        mask = np.zeros(m.shape, np.uint8); cv2.drawContours(mask, [c], -1, 255, -1)
        rgba[..., 3] = np.minimum(rgba[..., 3], cv2.GaussianBlur(mask, (3, 3), 0))
    peca = Image.fromarray(rgba, 'RGBA')
    x0, y0 = int(max(0, cx - r)), int(max(0, cy - r))
    x1, y1 = int(min(peca.width, cx + r)), int(min(peca.height, cy + r))
    return peca.crop((x0, y0, x1, y1)), 2 * r


def compoe(peca, diam):
    alvo = int(S * OCUPA)
    k = alvo / diam
    peca = peca.resize((max(1, int(peca.width * k)), max(1, int(peca.height * k))), Image.LANCZOS)
    tela = FUNDO.copy().convert('RGBA')
    x, y = (S - peca.width) // 2, (S - peca.height) // 2
    sombra = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    alfa = peca.split()[3]
    som = Image.new('RGBA', peca.size, (0, 0, 0, 170)); som.putalpha(alfa.point(lambda v: int(v * .7)))
    sombra.paste(som, (x + 10, y + 18), som)
    tela = Image.alpha_composite(tela, sombra.filter(ImageFilter.GaussianBlur(16)))
    tela.alpha_composite(peca, (x, y))
    return tela.convert('RGB')


for par in sys.argv[2:]:
    orig, nome = par.rsplit('=', 1)
    peca, diam = recorta(orig)
    compoe(peca, diam).save(os.path.join(saida, nome + '.jpg'), quality=88)
    print('ok', nome)
