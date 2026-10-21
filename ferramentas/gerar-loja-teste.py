"""Gera plataforma/supabase/06-padaria-teste.sql: deixa a loja de endereço "padaria" pronta para teste real,
com cardápio completo (fotos, preços, destaques e opcionais), dados da loja e seção Sobre.
Os produtos vêm de plataforma/assets/exemplo.js (modelo padaria). Roda de novo para atualizar o SQL.
Uso: python3 ferramentas/gerar-loja-teste.py [slug] [whatsapp]"""
import json
import sys

SLUG = sys.argv[1] if len(sys.argv) > 1 else "padaria"
ZAP = sys.argv[2] if len(sys.argv) > 2 else "5542999006578"

s = open("plataforma/assets/exemplo.js", encoding="utf-8").read()
a = s.index("window.BC_EXEMPLO = ") + len("window.BC_EXEMPLO = ")
d = json.loads(s[a:s.index(";\nwindow.BC_CAPAS")])["padaria"]


def grupo(i, nome, mn, mx, itens):
    return {"id": i, "nome": nome, "min": mn, "max": mx,
            "itens": [{"id": "%s%d" % (i, k + 1), "nome": n, "preco": p} for k, (n, p) in enumerate(itens)]}


LEITE = grupo("leite", "Tipo de leite", 1, 1, [("Integral", 0), ("Sem lactose", 0), ("Vegetal (aveia)", 3)])
EXTRA = grupo("extra", "Extras", 0, 2, [("Chantilly", 3), ("Calda de caramelo", 2.5)])
AQUECE = grupo("quente", "Como prefere?", 1, 1, [("Aquecido", 0), ("Do jeito que está", 0)])
FATIA = grupo("cober", "Cobertura extra", 0, 1, [("Sorvete de creme", 6), ("Calda de chocolate", 3)])
OPCOES = {"Cappuccino cremoso": [LEITE, EXTRA], "Latte": [LEITE, EXTRA],
          "Croissant de presunto e queijo": [AQUECE], "Bolo de cenoura": [FATIA], "Bolo red velvet": [FATIA]}

cats, ordem = {}, []
for i in d:
    if i["cat"] not in cats:
        cats[i["cat"]] = []; ordem.append(i["cat"])
    item = {"nome": i["nome"], "desc": i["desc"], "preco": i["preco"], "unid": i.get("unid", ""), "foto": i.get("foto", ""),
            "destaque": bool(i.get("destaque")), "selo": i.get("selo", "")}
    if i["nome"] in OPCOES:
        item["opcoes"] = OPCOES[i["nome"]]
    cats[i["cat"]].append(item)
menu = [{"nome": c, "itens": cats[c]} for c in ordem]
sobre = {"titulo": "Nossa história",
         "texto": "Pães de fermentação natural, bolos caseiros e café passado na hora.\nTudo feito com ingredientes selecionados e muito carinho, todos os dias.",
         "foto": ""}

q = lambda t: "'" + t.replace("'", "''") + "'"
sql = f"""-- Bistrô Connect · loja de teste: deixa a loja de endereço "{SLUG}" com cardápio completo, fotos e opcionais.
-- Rode DEPOIS do 04-opcionais.sql e do 05-paginas.sql, no SQL Editor do Supabase (projeto plataforma).
-- ATENÇÃO: apaga os produtos e as categorias atuais dessa loja e cria de novo. Pode rodar mais de uma vez.
-- Para testar com outro celular, troque o número do WhatsApp logo abaixo (55 + DDD + número, só dígitos).
do $$
declare
  v_loja uuid;
  cardapio jsonb := {q(json.dumps(menu, ensure_ascii=False))}::jsonb;
  c jsonb; p jsonb; cid text; pos int := 0; k int;
begin
  select id into v_loja from public.lojas where slug = {q(SLUG)};
  if v_loja is null then
    raise exception 'Não achei a loja com o endereço "{SLUG}". Confira o endereço em Dados da loja.';
  end if;

  update public.lojas set
    modelo = 'padaria',
    descricao = 'Pães de fermentação natural, bolos caseiros e café passado na hora.',
    whatsapp = {q(ZAP)},
    address = 'Rua das Flores, 120 · Centro',
    hours = 'Seg a sáb · 7h às 19h',
    delivery_fee = 5, min_order = 0,
    accept_orders = true, faz_entrega = true, faz_retirada = true,
    pagamentos = array['Pix','Cartão','Dinheiro'],
    capa_url = '/assets/img/exemplo/cafe-hero.jpg',
    extra = coalesce(extra, '{{}}'::jsonb) || jsonb_build_object('secoes', jsonb_build_object('sobre', {q(json.dumps(sobre, ensure_ascii=False))}::jsonb))
  where id = v_loja;

  delete from public.products where loja_id = v_loja;
  delete from public.categories where loja_id = v_loja;

  for c in select * from jsonb_array_elements(cardapio) loop
    pos := pos + 1;
    insert into public.categories (loja_id, name, position) values (v_loja, c ->> 'nome', pos) returning id into cid;
    k := 0;
    for p in select * from jsonb_array_elements(c -> 'itens') loop
      k := k + 1;
      insert into public.products (loja_id, category_id, name, description, price, unit, image_url, active, featured, badge, position, opcoes)
      values (v_loja, cid, p ->> 'nome', coalesce(p ->> 'desc', ''), (p ->> 'preco')::numeric, coalesce(p ->> 'unid', ''),
              coalesce(p ->> 'foto', ''), true, coalesce((p ->> 'destaque')::boolean, false), coalesce(p ->> 'selo', ''), k,
              coalesce(p -> 'opcoes', '[]'::jsonb));
    end loop;
  end loop;
  raise notice 'Pronto: loja {SLUG} com % categorias e % produtos.', pos, (select count(*) from public.products where loja_id = v_loja);
end $$;
"""
open("plataforma/supabase/06-padaria-teste.sql", "w", encoding="utf-8").write(sql)
print("gerado plataforma/supabase/06-padaria-teste.sql para", SLUG, "com", sum(len(c["itens"]) for c in menu), "produtos")
