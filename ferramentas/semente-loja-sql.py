"""Gera o SQL que cria (ou atualiza) uma loja de demonstração na plataforma a partir de uma semente JSON.
Uso: python3 ferramentas/semente-loja-sql.py plataforma/supabase/sementes/hamburgueria.json plataforma/supabase/15-hamburgueria.sql
A loja nova recebe os mesmos donos da loja "padaria" (para aparecer no mesmo login do painel).
Rodar o SQL apaga os produtos e as categorias atuais dessa loja e cria de novo. Pode rodar mais de uma vez."""
import json, sys
src, dst = sys.argv[1:3]
S = json.load(open(src, encoding='utf-8'))
L = S['loja']
def q(v): return "'" + str(v).replace("'", "''") + "'"
cardapio = json.dumps(S['categorias'], ensure_ascii=False)
extra = json.dumps(L.get('extra', {}), ensure_ascii=False)
pag = "array[" + ",".join(q(x) for x in L.get('pagamentos', ['Pix', 'Cartão', 'Dinheiro'])) + "]"
sql = f"""-- Bistrô Connect · loja de demonstração "{L['store_name']}" (endereço /l/{L['slug']}).
-- Gerado por ferramentas/semente-loja-sql.py a partir de {src}. Edite a semente e gere de novo.
-- Rode no SQL Editor do Supabase (projeto plataforma), DEPOIS dos arquivos 01 a 14.
-- Cria a loja se ela não existir (com os mesmos donos da loja "padaria") e troca o cardápio inteiro.
do $$
declare
  v_loja uuid; v_pad uuid;
  cardapio jsonb := {q(cardapio)}::jsonb;
  c jsonb; p jsonb; cid text; pos int := 0; k int;
begin
  select id into v_loja from public.lojas where slug = {q(L['slug'])};
  if v_loja is null then
    select id into v_pad from public.lojas where slug = 'padaria';
    insert into public.lojas (slug, store_name, modelo, criado_por)
    values ({q(L['slug'])}, {q(L['store_name'])}, {q(L['modelo'])}, (select criado_por from public.lojas where id = v_pad))
    returning id into v_loja;
    if v_pad is not null then
      insert into public.membros (loja_id, user_id, papel, email)
      select v_loja, m.user_id, m.papel, m.email from public.membros m where m.loja_id = v_pad
      on conflict (loja_id, user_id) do nothing;
    end if;
  end if;

  update public.lojas set
    store_name = {q(L['store_name'])}, modelo = {q(L['modelo'])}, descricao = {q(L.get('descricao', ''))},
    whatsapp = {q(L.get('whatsapp', ''))}, address = {q(L.get('address', ''))}, hours = {q(L.get('hours', ''))},
    instagram = {q(L.get('instagram', ''))}, cor = {q(L.get('cor') or '#B0703F')},
    logo_url = {q(L.get('logo_url', ''))}, capa_url = {q(L.get('capa_url', ''))},
    delivery_fee = {float(L.get('delivery_fee', 0))}, min_order = {float(L.get('min_order', 0))},
    accept_orders = true, faz_entrega = true, faz_retirada = true, pagamentos = {pag}, status = 'ativa',
    extra = coalesce(extra, '{{}}'::jsonb) || {q(extra)}::jsonb
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
  raise notice 'Pronto: % com % categorias e % produtos.', {q(L['store_name'])}, pos, (select count(*) from public.products where loja_id = v_loja);
end $$;
"""
open(dst, 'w', encoding='utf-8').write(sql)
print(dst, len(sql) // 1024, 'KB')
