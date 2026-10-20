"""Monta o cardápio de exemplo da plataforma: fotos reduzidas dos sites (Padaria & Café, Bruto, Âmbar)
em plataforma/assets/img/exemplo/ e o arquivo plataforma/assets/exemplo.js com um cardápio por tipo de loja.
O painel usa isso no botão "Usar cardápio de exemplo"; a capa padrão da vitrine usa as imagens em CAPAS.
Rode da raiz do repositório:  python3 ferramentas/montar-exemplos.py"""
import json, os, shutil
from PIL import Image

PAD = "sites/padaria-cafe/images/"
BRU = "sites/hamburgueria-bruto/img/"
AMB = "sites/ambar/img/"
SAIDA = "plataforma/assets/img/exemplo/"

# (categoria, nome, descrição, preço, unidade, foto, destaque, selo)
PADARIA = [
    ("Pães", "Croissant tradicional", "Folhado, amanteigado, assado a cada hora.", 9.5, "Unidade", PAD + "banco-croissant-tradicional.jpg", True, "Mais pedido"),
    ("Pães", "Pão trançado", "Massa macia e brilhante, ótimo para o café da manhã.", 18, "Unidade", PAD + "banco-pao-trancado-grego.jpg", False, ""),
    ("Pães", "Pão doce com creme", "Recheado com creme de baunilha.", 8, "Unidade", PAD + "banco-pao-doce-com-creme.jpg", False, ""),
    ("Pães", "Folhado dinamarquês", "Massa folhada com geleia da casa.", 12, "Unidade", PAD + "banco-folhado-dinamarques.jpg", False, ""),
    ("Bolos", "Bolo de cenoura", "Com cobertura de chocolate, fatia generosa.", 14, "Fatia", PAD + "banco-bolo-de-cenoura.jpg", True, ""),
    ("Bolos", "Bolo red velvet", "Massa aveludada e cream cheese.", 18, "Fatia", PAD + "banco-bolo-red-velvet.jpg", False, "Novo"),
    ("Bolos", "Bolo de limão", "Leve, cítrico e muito úmido.", 14, "Fatia", PAD + "banco-bolo-de-limao.jpg", False, ""),
    ("Bolos", "Cuca de frutas vermelhas", "Com farofa crocante por cima.", 15, "Fatia", PAD + "banco-cuca-de-frutas-vermelhas.jpg", False, ""),
    ("Doces", "Pastel de nata", "Casquinha crocante e creme na medida.", 9, "Unidade", PAD + "banco-pastel-de-nata.jpg", True, ""),
    ("Doces", "Rolinho de canela", "Glaçado, macio e perfumado.", 10, "Unidade", PAD + "banco-rolinho-de-canela.jpg", False, ""),
    ("Doces", "Scones com geleia", "Servidos com geleia de frutas vermelhas.", 12, "2 unidades", PAD + "banco-scones-com-geleia.jpg", False, ""),
    ("Doces", "Torta de limão", "Base crocante e merengue maçaricado.", 16, "Fatia", PAD + "banco-torta-de-limao.jpg", False, ""),
    ("Salgados", "Croissant de presunto e queijo", "Quentinho, com queijo derretido.", 14, "Unidade", PAD + "banco-croissant-de-presunto-e-queijo.jpg", False, ""),
    ("Salgados", "Croissant de salmão", "Com cream cheese e ervas.", 22, "Unidade", PAD + "banco-croissant-de-salmao.jpg", False, ""),
    ("Bebidas", "Café espresso", "Grãos selecionados, tirado na hora.", 7, "Xícara", PAD + "cafe-menu-espresso2.jpg", False, ""),
    ("Bebidas", "Cappuccino cremoso", "Com cacau em pó por cima.", 12, "Xícara", PAD + "cafe-menu-cappuccino-cacau.jpg", False, ""),
    ("Bebidas", "Latte", "Espresso com leite vaporizado.", 13, "Xícara", PAD + "cafe-menu-latte.jpg", False, ""),
]
CAFETERIA = [
    ("Cafés", "Espresso", "Intenso e encorpado, tirado na hora.", 7, "Xícara", PAD + "cafe-item-espresso.jpg", True, "Clássico"),
    ("Cafés", "Americano", "Espresso alongado com água quente.", 8, "Xícara", PAD + "cafe-menu-americano.jpg", False, ""),
    ("Cafés", "Espresso duplo", "Duas doses para quem precisa de energia.", 11, "Xícara", PAD + "cafe-menu-espresso2.jpg", False, ""),
    ("Cafés", "Flat white", "Espresso duplo com leite sedoso.", 14, "Xícara", PAD + "cafe-menu-flat-white.jpg", False, ""),
    ("Com leite", "Cappuccino", "Espuma cremosa e toque de cacau.", 12, "Xícara", PAD + "cafe-item-cappuccino.jpg", True, "Mais pedido"),
    ("Com leite", "Latte", "Suave, com leite vaporizado.", 13, "Xícara", PAD + "cafe-menu-latte.jpg", False, ""),
    ("Com leite", "Latte macchiato", "Camadas de leite, espuma e espresso.", 14, "Copo", PAD + "cafe-menu-latte-macchiato.jpg", False, ""),
    ("Com leite", "Mocha com canela", "Chocolate, espresso e canela.", 16, "Xícara", PAD + "cafe-menu-mocha-canela.jpg", False, ""),
    ("Com leite", "Latte com especiarias", "Canela, cravo e noz-moscada.", 15, "Xícara", PAD + "cafe-menu-latte-especiarias.jpg", False, "Da estação"),
    ("Gelados", "Iced latte", "Café com leite e muito gelo.", 14, "Copo", PAD + "cafe-menu-iced-latte.jpg", False, ""),
    ("Gelados", "Iced caramel latte", "Calda de caramelo e chantilly.", 17, "Copo", PAD + "cafe-menu-iced-caramel-latte.jpg", True, ""),
    ("Gelados", "Frappé de chocolate", "Cremoso, com raspas de chocolate.", 18, "Copo", PAD + "cafe-menu-frappe-chocolate.jpg", False, ""),
    ("Gelados", "Dalgona", "Café batido sobre leite gelado.", 16, "Copo", PAD + "cafe-menu-dalgona.jpg", False, ""),
    ("Comidinhas", "Croissant tradicional", "Folhado e amanteigado.", 9.5, "Unidade", PAD + "banco-croissant-tradicional.jpg", False, ""),
    ("Comidinhas", "Croissant de presunto e queijo", "Quentinho, com queijo derretido.", 14, "Unidade", PAD + "banco-croissant-de-presunto-e-queijo.jpg", False, ""),
    ("Comidinhas", "Waffle belga", "Com frutas e calda.", 22, "Unidade", PAD + "banco-waffle-belga.jpg", False, ""),
    ("Doces", "Cheesecake basco", "Cremoso e levemente queimado.", 19, "Fatia", PAD + "banco-cheesecake-basco.jpg", False, ""),
    ("Doces", "Pastel de nata", "Casquinha crocante e creme na medida.", 9, "Unidade", PAD + "banco-pastel-de-nata.jpg", False, ""),
    ("Doces", "Madeleines", "Macias e douradas, feitas na hora.", 12, "4 unidades", PAD + "banco-madeleines.jpg", False, ""),
]
DOCERIA = [
    ("Bolos", "Bolo de chocolate com chantilly", "Massa úmida e cobertura generosa.", 16, "Fatia", PAD + "banco-bolo-de-chocolate-com-chantilly.jpg", True, "Mais pedido"),
    ("Bolos", "Bolo de morango com chantilly", "Recheio de morangos frescos.", 17, "Fatia", PAD + "banco-bolo-de-morango-com-chantilly.jpg", False, ""),
    ("Bolos", "Bolo red velvet", "Massa aveludada e cream cheese.", 18, "Fatia", PAD + "banco-bolo-red-velvet.jpg", False, ""),
    ("Bolos", "Bolo ganache", "Camadas de chocolate meio amargo.", 18, "Fatia", PAD + "banco-bolo-ganache.jpg", False, ""),
    ("Bolos", "Bolo três chocolates", "Branco, ao leite e meio amargo.", 19, "Fatia", PAD + "banco-bolo-tres-chocolates.jpg", True, ""),
    ("Bolos", "Bolo de coco", "Úmido, com coco fresco.", 14, "Fatia", PAD + "banco-bolo-de-coco.jpg", False, ""),
    ("Doces", "Profiteroles", "Bomboniere de creme com calda de chocolate.", 18, "4 unidades", PAD + "banco-profiteroles.jpg", False, ""),
    ("Doces", "Petit gâteau", "Casquinha firme e coração derretendo.", 22, "Unidade", PAD + "banco-petit-gateau.jpg", True, ""),
    ("Doces", "Cannoli sicilianos", "Recheio de ricota e gotas de chocolate.", 15, "Unidade", PAD + "banco-cannoli-sicilianos.jpg", False, ""),
    ("Doces", "Baba ao rum", "Molhadinho e perfumado.", 14, "Unidade", PAD + "banco-baba-ao-rum.jpg", False, ""),
    ("Tortas", "Torta de limão", "Base crocante e merengue maçaricado.", 16, "Fatia", PAD + "banco-torta-de-limao.jpg", False, ""),
    ("Tortas", "Torta mousse de chocolate", "Mousse aerado sobre base de biscoito.", 18, "Fatia", PAD + "banco-torta-mousse-de-chocolate.jpg", False, ""),
    ("Tortas", "Torta della nonna", "Creme de baunilha e pinhões.", 18, "Fatia", PAD + "banco-torta-della-nonna.jpg", False, ""),
    ("Tortas", "Cheesecake de frutas vermelhas", "Cremoso, com calda artesanal.", 19, "Fatia", PAD + "banco-cheesecake-de-frutas-vermelhas.jpg", False, ""),
    ("Tortas", "Tiramisu", "Clássico italiano, com café de verdade.", 18, "Porção", PAD + "banco-tiramisu.jpg", False, ""),
    ("Encomendas", "Bolo de festa", "Escolha o sabor e o tamanho. Consulte prazos.", 120, "A partir de", PAD + "banco-bolo-floresta-negra.jpg", False, "Sob encomenda"),
]
HAMBURGUERIA = [
    ("Burgers", "Clássico", "Blend 160g, queijo, bacon, cebola e molho da casa.", 32.9, "", BRU + "classico.jpg", True, "Mais pedido"),
    ("Burgers", "Barbecue", "Blend 160g, onion rings, cheddar e barbecue defumado.", 36.9, "", BRU + "barbecue.jpg", True, ""),
    ("Burgers", "Mexicano", "Blend 160g, guacamole, jalapeño e cheddar.", 38.9, "", BRU + "mexicano.jpg", False, "Picante"),
    ("Burgers", "Trufado", "Pão preto, cogumelos, queijo e maionese trufada.", 42.9, "", BRU + "trufado.jpg", False, "Novo"),
    ("Burgers", "Crispy", "Frango empanado, picles, tomate e maionese.", 34.9, "", BRU + "crispy.jpg", False, ""),
    ("Burgers", "Salmão", "Salmão grelhado, guacamole e pão de milho.", 44.9, "", BRU + "salmao.jpg", False, ""),
    ("Burgers", "Halloumi", "Queijo halloumi grelhado e legumes. Vegetariano.", 36.9, "", BRU + "halloumi.jpg", False, "Veggie"),
    ("Combos", "Combo Clássico", "Clássico, batata e refrigerante.", 49.9, "", BRU + "combo.jpg", True, ""),
    ("Acompanhamentos", "Batata frita", "Porção individual, crocante e sequinha.", 16, "", BRU + "fritas.jpg", False, ""),
    ("Acompanhamentos", "Batata com cheddar", "Porção grande coberta de cheddar cremoso.", 29, "", BRU + "batata.jpg", False, ""),
    ("Bebidas", "Milkshake de chocolate", "Cremoso, 400 ml.", 24, "", PAD + "cafe-menu-frappe-chocolate.jpg", False, ""),
    ("Sobremesas", "Petit gâteau", "Com sorvete de creme.", 24, "", PAD + "banco-petit-gateau.jpg", False, ""),
]
PIZZARIA = [
    ("Pizzas salgadas", "Margherita", "Molho de tomate, muçarela, manjericão e azeite.", 49, "Grande", "", True, "Clássica"),
    ("Pizzas salgadas", "Calabresa", "Calabresa fatiada, cebola e azeitonas.", 52, "Grande", "", False, ""),
    ("Pizzas salgadas", "Quatro queijos", "Muçarela, provolone, gorgonzola e parmesão.", 58, "Grande", "", False, ""),
    ("Pizzas salgadas", "Portuguesa", "Presunto, ovos, cebola, ervilha e azeitonas.", 55, "Grande", "", False, ""),
    ("Pizzas doces", "Chocolate com morango", "Chocolate ao leite e morangos frescos.", 54, "Grande", "", False, ""),
    ("Bebidas", "Refrigerante 2 L", "Gelado, na hora da entrega.", 14, "", "", False, ""),
]
RESTAURANTE = [
    ("Entradas", "Vieira selada", "Com creme de ervas e azeite cítrico.", 58, "", AMB + "vieira.jpg", True, "Da casa"),
    ("Entradas", "Carpaccio", "Lâminas de carne, rúcula, parmesão e alcaparras.", 46, "", AMB + "carpaccio.jpg", False, ""),
    ("Entradas", "Salada de burrata", "Burrata, tomates, folhas e vinagrete de ervas.", 42, "", AMB + "salada-burrata.jpg", False, ""),
    ("Entradas", "Tábua de frios", "Embutidos, queijos, geleia e castanhas.", 78, "Para dividir", AMB + "tabua.jpg", False, ""),
    ("Entradas", "Tartare", "Carne bovina, gema e picles.", 52, "", AMB + "tartare.jpg", False, ""),
    ("Pratos principais", "Chateaubriand", "Filé alto, purê de batata e legumes assados.", 169, "Para 2", AMB + "chateaubriand.jpg", True, "Para dividir"),
    ("Pratos principais", "Risoto de trufas", "Parmesão e trufa negra.", 118, "", AMB + "risoto-trufas.jpg", True, ""),
    ("Pratos principais", "Confit de pato", "Pato confitado com redução de vinho.", 98, "", AMB + "confit-pato.jpg", False, ""),
    ("Pratos principais", "Coq au vin", "Frango no vinho tinto, cogumelos e bacon.", 88, "", AMB + "coq-au-vin.jpg", False, ""),
    ("Pratos principais", "Salmão en papillote", "Salmão assado no papel com ervas e limão.", 92, "", AMB + "papillote.jpg", False, ""),
    ("Pratos principais", "Ratatouille", "Legumes assados em molho de tomate. Vegano.", 68, "", AMB + "ratatouille.jpg", False, "Vegano"),
    ("Sobremesas", "Crème brûlée", "Creme de baunilha com crosta de caramelo.", 36, "", AMB + "creme-brulee.jpg", True, ""),
    ("Sobremesas", "Pavlova", "Merengue crocante com frutas vermelhas.", 38, "", AMB + "pavlova.jpg", False, ""),
    ("Sobremesas", "Tiramisu", "Mascarpone, café e cacau.", 34, "", AMB + "tiramisu.jpg", False, ""),
    ("Sobremesas", "Torta de limão", "Merengue maçaricado.", 32, "", AMB + "torta-limao.jpg", False, ""),
    ("Bebidas", "Espumante Chandon", "Garrafa 750 ml.", 190, "Garrafa", AMB + "chandon.png", False, ""),
    ("Bebidas", "Malbec Catena", "Garrafa 750 ml.", 210, "Garrafa", AMB + "catena.png", False, ""),
    ("Bebidas", "Chablis", "Garrafa 750 ml.", 240, "Garrafa", AMB + "chablis.png", False, ""),
]
OUTRO = [
    ("Destaques", "Risoto de trufas", "Parmesão e trufa negra.", 118, "", AMB + "risoto-trufas.jpg", True, "Da casa"),
    ("Destaques", "Salada de burrata", "Burrata, tomates, folhas e vinagrete de ervas.", 42, "", AMB + "salada-burrata.jpg", False, ""),
    ("Cardápio", "Carpaccio", "Lâminas de carne, rúcula e parmesão.", 46, "", AMB + "carpaccio.jpg", False, ""),
    ("Cardápio", "Ratatouille", "Legumes assados em molho de tomate. Vegano.", 68, "", AMB + "ratatouille.jpg", False, "Vegano"),
    ("Cardápio", "Crème brûlée", "Creme de baunilha com crosta de caramelo.", 36, "", AMB + "creme-brulee.jpg", False, ""),
    ("Bebidas", "Espumante Chandon", "Garrafa 750 ml.", 190, "Garrafa", AMB + "chandon.png", False, ""),
]
MENUS = {"padaria": PADARIA, "cafeteria": CAFETERIA, "doceria": DOCERIA, "hamburgueria": HAMBURGUERIA,
         "pizzaria": PIZZARIA, "restaurante": RESTAURANTE, "outro": OUTRO}
CAPAS = {"padaria": PAD + "cafe-hero.jpg", "cafeteria": PAD + "cafe-hero.jpg", "doceria": PAD + "banco-bolo-de-chocolate-com-chantilly.jpg",
         "hamburgueria": BRU + "w2.jpg", "restaurante": AMB + "hero-bg.jpg"}


def copia(origem, largura):
    """Reduz a foto, grava em SAIDA e devolve o caminho público (começa com /)."""
    nome = os.path.basename(origem).lower().replace("banco-", "")
    destino = SAIDA + nome
    if not os.path.isfile(destino):
        im = Image.open(origem)
        png = origem.endswith(".png")
        if png:
            im = im.convert("RGBA")
        else:
            im = im.convert("RGB")
        if im.width > largura:
            im = im.resize((largura, round(im.height * largura / im.width)), Image.LANCZOS)
        if png:
            im.save(destino, optimize=True)
        else:
            im.save(destino, quality=80, optimize=True, progressive=True)
    return "/" + destino.split("plataforma/")[1]


os.makedirs(SAIDA, exist_ok=True)
saida = {}
for modelo, itens in MENUS.items():
    lista = []
    for i, (cat, nome, desc, preco, unid, foto, dest, selo) in enumerate(itens):
        item = {"cat": cat, "nome": nome, "desc": desc, "preco": preco, "unid": unid, "destaque": dest, "selo": selo, "pos": i + 1}
        if foto:
            item["foto"] = copia(foto, 640)
            if foto.endswith(".png"):
                item["contem"] = True  # garrafas: a foto inteira, sem cortar
        lista.append(item)
    saida[modelo] = lista
capas = {m: copia(f, 1400) for m, f in CAPAS.items()}
js = ("/* Gerado por ferramentas/montar-exemplos.py. Cardápio de exemplo por tipo de loja (usado no botão \"Usar cardápio de exemplo\" do painel). */\n"
      "window.BC_EXEMPLO = " + json.dumps(saida, ensure_ascii=False, indent=1) + ";\n"
      "window.BC_CAPAS = " + json.dumps(capas, ensure_ascii=False, indent=1) + ";\n")
open("plataforma/assets/exemplo.js", "w", encoding="utf-8").write(js)
tot = sum(os.path.getsize(SAIDA + f) for f in os.listdir(SAIDA))
print(len(os.listdir(SAIDA)), "fotos,", round(tot / 1024), "KB; modelos:", {m: len(v) for m, v in saida.items()})
