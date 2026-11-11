"""Padroniza fotos de bebidas (latas, garrafas, vinhos): o produto inteiro, de pé, centralizado, no mesmo fundo
de ardósia das pizzas, já no formato 4:3 dos cartões do cardápio (nada é cortado no cartão, na faixa nem na janela do item).
Uso: python3 ferramentas/padronizar-bebidas.py <pasta-saida> origem1=nome1 origem2=nome2 ...
Origem com transparência (PNG/WebP recortado) fica perfeita. JPG com fundo escuro é mesclado com borda suave."""
import sys, os
import numpy as np, cv2
from PIL import Image, ImageFilter

W, H = 960, 720
ALTURA = 0.74          # altura do produto em relação ao quadro (cabe também na janela do item, que é mais larga)
saida = sys.argv[1]
os.makedirs(saida, exist_ok=True)


def ardosia():
    rng = np.random.default_rng(7)
    base = np.full((H, W, 3), (30, 29, 28), np.float32)
    ruido = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 2.2) * 9
    veios = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 18) * 14
    base += (ruido + veios)[..., None]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    luz = np.exp(-(((xx - W * .32) ** 2 + (yy - H * .2) ** 2) / (2 * (W * .5) ** 2)))
    base += luz[..., None] * np.array([26, 18, 10], np.float32)
    vin = 1 - .36 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2).clip(0, 1.6) / 1.6
    base *= vin[..., None]
    return Image.fromarray(base.clip(0, 255).astype(np.uint8))


FUNDO = ardosia()


def peca(caminho):
    im = Image.open(caminho)
    if im.mode == 'RGBA' and np.array(im)[..., 3].min() < 20:
        a = np.array(im)[..., 3]
        ys, xs = np.where(a > 30)
        return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)), True
    im = im.convert('RGB')
    # JPG de fundo escuro: borda suave para fundir com a ardósia
    m = Image.new('L', im.size, 255)
    borda = int(min(im.size) * .12)
    m = Image.fromarray(cv2.GaussianBlur(np.pad(np.full((im.height - 2 * borda, im.width - 2 * borda), 255, np.uint8), borda), (0, 0), borda / 2))
    im.putalpha(m)
    return im, False


def compoe(p, recortado):
    alvo = int(H * ALTURA) if recortado else int(H * .92)
    k = alvo / p.height
    p = p.resize((max(1, int(p.width * k)), alvo), Image.LANCZOS)
    tela = FUNDO.copy().convert('RGBA')
    x = (W - p.width) // 2
    y = (H - alvo) // 2 + (int(H * .03) if recortado else 0)
    if recortado:
        # sombra de contato no chão e sombra projetada suave
        chao = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        e = Image.new('L', (int(p.width * 1.5), 34), 0)
        cv2_e = np.zeros((34, int(p.width * 1.5)), np.uint8); cv2.ellipse(cv2_e, (cv2_e.shape[1] // 2, 17), (cv2_e.shape[1] // 2 - 2, 12), 0, 0, 360, 200, -1)
        e = Image.fromarray(cv2_e)
        sombra = Image.new('RGBA', e.size, (0, 0, 0, 255)); sombra.putalpha(e)
        chao.paste(sombra, (W // 2 - e.width // 2, y + alvo - 20), sombra)
        tela = Image.alpha_composite(tela, chao.filter(ImageFilter.GaussianBlur(10)))
        proj = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        s2 = Image.new('RGBA', p.size, (0, 0, 0, 120)); s2.putalpha(p.split()[3].point(lambda v: int(v * .45)))
        proj.paste(s2, (x + 16, y + 8), s2)
        tela = Image.alpha_composite(tela, proj.filter(ImageFilter.GaussianBlur(14)))
    tela.alpha_composite(p, (x, y))
    return tela.convert('RGB')


for par in sys.argv[2:]:
    orig, nome = par.rsplit('=', 1)
    p, rec = peca(orig)
    compoe(p, rec).save(os.path.join(saida, nome + '.jpg'), quality=88)
    print('ok', nome)
