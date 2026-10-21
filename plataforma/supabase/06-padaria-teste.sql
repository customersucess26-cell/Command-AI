-- Bistrô Connect · loja de teste: deixa a loja de endereço "padaria" com cardápio completo, fotos e opcionais.
-- Rode DEPOIS do 04-opcionais.sql e do 05-paginas.sql, no SQL Editor do Supabase (projeto plataforma).
-- ATENÇÃO: apaga os produtos e as categorias atuais dessa loja e cria de novo. Pode rodar mais de uma vez.
-- Para testar com outro celular, troque o número do WhatsApp logo abaixo (55 + DDD + número, só dígitos).
do $$
declare
  v_loja uuid;
  cardapio jsonb := '[{"nome": "Pães", "itens": [{"nome": "Croissant tradicional", "desc": "Folhado, amanteigado, assado a cada hora.", "preco": 9.5, "unid": "Unidade", "foto": "/assets/img/exemplo/croissant-tradicional.jpg", "destaque": true, "selo": "Mais pedido"}, {"nome": "Pão trançado", "desc": "Massa macia e brilhante, ótimo para o café da manhã.", "preco": 18, "unid": "Unidade", "foto": "/assets/img/exemplo/pao-trancado-grego.jpg", "destaque": false, "selo": ""}, {"nome": "Pão doce com creme", "desc": "Recheado com creme de baunilha.", "preco": 8, "unid": "Unidade", "foto": "/assets/img/exemplo/pao-doce-com-creme.jpg", "destaque": false, "selo": ""}, {"nome": "Folhado dinamarquês", "desc": "Massa folhada com geleia da casa.", "preco": 12, "unid": "Unidade", "foto": "/assets/img/exemplo/folhado-dinamarques.jpg", "destaque": false, "selo": ""}]}, {"nome": "Bolos", "itens": [{"nome": "Bolo de cenoura", "desc": "Com cobertura de chocolate, fatia generosa.", "preco": 14, "unid": "Fatia", "foto": "/assets/img/exemplo/bolo-de-cenoura.jpg", "destaque": true, "selo": "", "opcoes": [{"id": "cober", "nome": "Cobertura extra", "min": 0, "max": 1, "itens": [{"id": "cober1", "nome": "Sorvete de creme", "preco": 6}, {"id": "cober2", "nome": "Calda de chocolate", "preco": 3}]}]}, {"nome": "Bolo red velvet", "desc": "Massa aveludada e cream cheese.", "preco": 18, "unid": "Fatia", "foto": "/assets/img/exemplo/bolo-red-velvet.jpg", "destaque": false, "selo": "Novo", "opcoes": [{"id": "cober", "nome": "Cobertura extra", "min": 0, "max": 1, "itens": [{"id": "cober1", "nome": "Sorvete de creme", "preco": 6}, {"id": "cober2", "nome": "Calda de chocolate", "preco": 3}]}]}, {"nome": "Bolo de limão", "desc": "Leve, cítrico e muito úmido.", "preco": 14, "unid": "Fatia", "foto": "/assets/img/exemplo/bolo-de-limao.jpg", "destaque": false, "selo": ""}, {"nome": "Cuca de frutas vermelhas", "desc": "Com farofa crocante por cima.", "preco": 15, "unid": "Fatia", "foto": "/assets/img/exemplo/cuca-de-frutas-vermelhas.jpg", "destaque": false, "selo": ""}]}, {"nome": "Doces", "itens": [{"nome": "Pastel de nata", "desc": "Casquinha crocante e creme na medida.", "preco": 9, "unid": "Unidade", "foto": "/assets/img/exemplo/pastel-de-nata.jpg", "destaque": true, "selo": ""}, {"nome": "Rolinho de canela", "desc": "Glaçado, macio e perfumado.", "preco": 10, "unid": "Unidade", "foto": "/assets/img/exemplo/rolinho-de-canela.jpg", "destaque": false, "selo": ""}, {"nome": "Scones com geleia", "desc": "Servidos com geleia de frutas vermelhas.", "preco": 12, "unid": "2 unidades", "foto": "/assets/img/exemplo/scones-com-geleia.jpg", "destaque": false, "selo": ""}, {"nome": "Torta de limão", "desc": "Base crocante e merengue maçaricado.", "preco": 16, "unid": "Fatia", "foto": "/assets/img/exemplo/torta-de-limao.jpg", "destaque": false, "selo": ""}]}, {"nome": "Salgados", "itens": [{"nome": "Croissant de presunto e queijo", "desc": "Quentinho, com queijo derretido.", "preco": 14, "unid": "Unidade", "foto": "/assets/img/exemplo/croissant-de-presunto-e-queijo.jpg", "destaque": false, "selo": "", "opcoes": [{"id": "quente", "nome": "Como prefere?", "min": 1, "max": 1, "itens": [{"id": "quente1", "nome": "Aquecido", "preco": 0}, {"id": "quente2", "nome": "Do jeito que está", "preco": 0}]}]}, {"nome": "Croissant de salmão", "desc": "Com cream cheese e ervas.", "preco": 22, "unid": "Unidade", "foto": "/assets/img/exemplo/croissant-de-salmao.jpg", "destaque": false, "selo": ""}]}, {"nome": "Bebidas", "itens": [{"nome": "Café espresso", "desc": "Grãos selecionados, tirado na hora.", "preco": 7, "unid": "Xícara", "foto": "/assets/img/exemplo/cafe-menu-espresso2.jpg", "destaque": false, "selo": ""}, {"nome": "Cappuccino cremoso", "desc": "Com cacau em pó por cima.", "preco": 12, "unid": "Xícara", "foto": "/assets/img/exemplo/cafe-menu-cappuccino-cacau.jpg", "destaque": false, "selo": "", "opcoes": [{"id": "leite", "nome": "Tipo de leite", "min": 1, "max": 1, "itens": [{"id": "leite1", "nome": "Integral", "preco": 0}, {"id": "leite2", "nome": "Sem lactose", "preco": 0}, {"id": "leite3", "nome": "Vegetal (aveia)", "preco": 3}]}, {"id": "extra", "nome": "Extras", "min": 0, "max": 2, "itens": [{"id": "extra1", "nome": "Chantilly", "preco": 3}, {"id": "extra2", "nome": "Calda de caramelo", "preco": 2.5}]}]}, {"nome": "Latte", "desc": "Espresso com leite vaporizado.", "preco": 13, "unid": "Xícara", "foto": "/assets/img/exemplo/cafe-menu-latte.jpg", "destaque": false, "selo": "", "opcoes": [{"id": "leite", "nome": "Tipo de leite", "min": 1, "max": 1, "itens": [{"id": "leite1", "nome": "Integral", "preco": 0}, {"id": "leite2", "nome": "Sem lactose", "preco": 0}, {"id": "leite3", "nome": "Vegetal (aveia)", "preco": 3}]}, {"id": "extra", "nome": "Extras", "min": 0, "max": 2, "itens": [{"id": "extra1", "nome": "Chantilly", "preco": 3}, {"id": "extra2", "nome": "Calda de caramelo", "preco": 2.5}]}]}]}]'::jsonb;
  c jsonb; p jsonb; cid text; pos int := 0; k int;
begin
  select id into v_loja from public.lojas where slug = 'padaria';
  if v_loja is null then
    raise exception 'Não achei a loja com o endereço "padaria". Confira o endereço em Dados da loja.';
  end if;

  update public.lojas set
    modelo = 'padaria',
    descricao = 'Pães de fermentação natural, bolos caseiros e café passado na hora.',
    whatsapp = '5542999006578',
    address = 'Rua das Flores, 120 · Centro',
    hours = 'Seg a sáb · 7h às 19h',
    delivery_fee = 5, min_order = 0,
    accept_orders = true, faz_entrega = true, faz_retirada = true,
    pagamentos = array['Pix','Cartão','Dinheiro'],
    capa_url = '/assets/img/exemplo/cafe-hero.jpg',
    extra = coalesce(extra, '{}'::jsonb) || jsonb_build_object('secoes', jsonb_build_object('sobre', '{"titulo": "Nossa história", "texto": "Pães de fermentação natural, bolos caseiros e café passado na hora.\nTudo feito com ingredientes selecionados e muito carinho, todos os dias.", "foto": ""}'::jsonb))
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
  raise notice 'Pronto: loja padaria com % categorias e % produtos.', pos, (select count(*) from public.products where loja_id = v_loja);
end $$;
