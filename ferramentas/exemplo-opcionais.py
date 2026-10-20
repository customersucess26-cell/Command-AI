"""Põe opcionais de exemplo no cardápio de exemplo (plataforma/assets/exemplo.js): ponto da carne e adicionais nos burgers,
tamanho e borda nas pizzas, leite e açúcar nos cafés com leite. Roda depois do montar-exemplos.py. Pode rodar de novo."""
import json

ARQ = "plataforma/assets/exemplo.js"
s = open(ARQ, encoding="utf-8").read()
a = s.index("window.BC_EXEMPLO = ") + len("window.BC_EXEMPLO = ")
b = s.index(";\nwindow.BC_CAPAS")
d = json.loads(s[a:b])


def grupo(i, nome, mn, mx, itens):
    return {"id": i, "nome": nome, "min": mn, "max": mx,
            "itens": [{"id": "%s%d" % (i, k + 1), "nome": n, "preco": p} for k, (n, p) in enumerate(itens)]}


PONTO = grupo("ponto", "Ponto da carne", 1, 1, [("Mal passado", 0), ("Ao ponto", 0), ("Bem passado", 0)])
ADICIONAIS = grupo("add", "Adicionais", 0, 3, [("Queijo extra", 4.5), ("Bacon", 6), ("Ovo", 3), ("Cebola caramelizada", 3.5)])
TAMANHO = grupo("tam", "Tamanho", 1, 1, [("Média (6 fatias)", 0), ("Grande (8 fatias)", 14), ("Família (12 fatias)", 28)])
BORDA = grupo("borda", "Borda", 0, 1, [("Catupiry", 8), ("Cheddar", 8), ("Chocolate", 9)])
LEITE = grupo("leite", "Tipo de leite", 1, 1, [("Integral", 0), ("Sem lactose", 0), ("Vegetal (aveia)", 3)])
EXTRA = grupo("extra", "Extras", 0, 2, [("Chantilly", 3), ("Calda de caramelo", 2.5)])

for item in d.get("hamburgueria", []):
    item.pop("opcoes", None)
    if item["cat"] == "Burgers":
        item["opcoes"] = [PONTO, ADICIONAIS]
for item in d.get("pizzaria", []):
    item.pop("opcoes", None)
    if item["cat"].startswith("Pizzas"):
        item["opcoes"] = [TAMANHO, BORDA]
for item in d.get("cafeteria", []):
    item.pop("opcoes", None)
    if item["cat"] == "Com leite":
        item["opcoes"] = [LEITE, EXTRA]

s = s[:a] + json.dumps(d, ensure_ascii=False, indent=1) + s[b:]
open(ARQ, "w", encoding="utf-8").write(s)
print("opcionais de exemplo gravados em", ARQ)
