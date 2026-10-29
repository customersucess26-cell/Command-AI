-- ================= 13: taxa de entrega por bairro =================
-- A loja cadastra os bairros em lojas.extra.bairros (painel > Dados da loja). Rode DEPOIS do 09 e do 11. Pode rodar de novo.

alter table public.orders add column if not exists bairro text not null default '';
create or replace function public.bairros_ok(j jsonb)
returns boolean language sql immutable set search_path = '' as $$
  select j is null or j = 'null'::jsonb or (jsonb_typeof(j) = 'array' and jsonb_array_length(j) <= 80 and not exists (
    select 1 from jsonb_array_elements(j) x
     where jsonb_typeof(x) <> 'object' or jsonb_typeof(x -> 'n') <> 'string' or length(btrim(x ->> 'n')) not between 2 and 40
        or jsonb_typeof(x -> 't') <> 'number' or (x ->> 't')::numeric not between 0 and 999))
$$;
alter table public.lojas drop constraint if exists lojas_bairros_ok;
alter table public.lojas add constraint lojas_bairros_ok check (public.bairros_ok(extra -> 'bairros'));

-- create_order: igual ao anterior (cupom, pedido da equipe), mais o bairro e a taxa por bairro conferidos aqui
create or replace function public.create_order(p_slug text, p_idem text, p_order jsonb)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare
  loja    public.lojas;
  ja      public.orders;
  novo    public.orders;
  nome    text := btrim(coalesce(p_order ->> 'customer_name', ''));
  fone    text := btrim(coalesce(p_order ->> 'customer_phone', ''));
  digs    text := regexp_replace(coalesce(p_order ->> 'customer_phone', ''), '\D', '', 'g');
  tipo    text := coalesce(p_order ->> 'delivery_type', '');
  ender   text := btrim(coalesce(p_order ->> 'address', ''));
  obs     text := btrim(coalesce(p_order ->> 'notes', ''));
  quando  text := btrim(coalesce(p_order ->> 'scheduled_for', ''));
  forma   text := coalesce(p_order ->> 'payment_method', '');
  it      jsonb;
  pid     text;
  qtd     int;
  sel     jsonb;
  op      jsonb;
  grp     jsonb;
  itm     jsonb;
  cont    jsonb;
  ops     jsonb;
  vistos  text[];
  gid     text;
  oid     text;
  c       int;
  unit    numeric;
  prod    public.products;
  itens   jsonb := '[]'::jsonb;
  soma    numeric := 0;
  taxa    numeric := 0;
  total   numeric;
  proximo int;
  codigo  text;
  cup     text := upper(btrim(coalesce(p_order ->> 'coupon', '')));
  descon  numeric := 0;
  bairro  text := btrim(coalesce(p_order ->> 'neighborhood', ''));
  bx      jsonb;
begin
  select * into loja from public.lojas l where l.slug = lower(coalesce(p_slug, ''));
  if not found or loja.status <> 'ativa' then perform public.recusa('Loja não encontrada.'); end if;
  if coalesce(p_idem, '') !~ '^[A-Za-z0-9_-]{8,80}$' then perform public.recusa('Pedido inválido. Atualize a página.'); end if;

  select * into ja from public.orders o where o.loja_id = loja.id and o.idem_key = p_idem;
  if found then
    return jsonb_build_object('code', ja.code, 'track_token', ja.track_token, 'track_code', ja.track_code, 'total', ja.total,
                              'subtotal', ja.subtotal, 'delivery_fee', ja.delivery_fee, 'discount', ja.discount, 'coupon', ja.coupon, 'items', ja.items);
  end if;

  if not loja.accept_orders and coalesce(current_setting('bc.interno', true), '') <> '1' then
    perform public.recusa('A loja não está recebendo pedidos pelo site agora. Chame no WhatsApp.');
  end if;
  if length(nome) not between 2 and 80 then perform public.recusa('Informe seu nome.'); end if;
  if length(digs) not between 10 and 13 or length(fone) > 30 then
    perform public.recusa('Informe seu WhatsApp com DDD.');
  end if;
  if tipo = 'entrega' then
    if not loja.faz_entrega then perform public.recusa('Esta loja não faz entrega. Escolha retirada.'); end if;
    if length(ender) not between 8 and 200 then perform public.recusa('Informe o endereço completo para entrega.'); end if;
  elsif tipo = 'retirada' then
    if not loja.faz_retirada then perform public.recusa('Esta loja só faz entrega.'); end if;
    ender := '';
  else
    perform public.recusa('Escolha entrega ou retirada.');
  end if;
  if length(obs) > 300 then perform public.recusa('As observações passam de 300 caracteres.'); end if;
  if length(quando) > 60 then perform public.recusa('Horário inválido.'); end if;
  if forma = '' or not (forma = any (loja.pagamentos)) then perform public.recusa('Escolha a forma de pagamento.'); end if;

  if jsonb_typeof(p_order -> 'items') is distinct from 'array'
     or jsonb_array_length(p_order -> 'items') < 1 or jsonb_array_length(p_order -> 'items') > 50 then
    perform public.recusa('Seu pedido está vazio.');
  end if;
  for it in select * from jsonb_array_elements(p_order -> 'items') loop
    if jsonb_typeof(it) <> 'object' or jsonb_typeof(it -> 'qty') <> 'number' or jsonb_typeof(it -> 'product_id') <> 'string'
       or (it ->> 'qty')::numeric <> trunc((it ->> 'qty')::numeric)
       or (it ->> 'qty')::numeric < 1 or (it ->> 'qty')::numeric > 99 then
      perform public.recusa('Quantidade inválida: de 1 a 99 por item.');
    end if;
    pid := it ->> 'product_id';
    qtd := (it ->> 'qty')::int;
    select * into prod from public.products p where p.id = pid and p.loja_id = loja.id;
    if not found or not prod.active then
      perform public.recusa('Um dos produtos saiu do cardápio. Atualize a página.', 'PRICE_CHANGED');
    end if;
    sel := case when jsonb_typeof(it -> 'options') = 'array' then it -> 'options' else '[]'::jsonb end;
    if jsonb_array_length(sel) > 30 then perform public.recusa('Opções demais em um item.'); end if;
    unit := prod.price; ops := '[]'::jsonb; cont := '{}'::jsonb; vistos := '{}';
    for op in select * from jsonb_array_elements(sel) loop
      if jsonb_typeof(op) <> 'object' or jsonb_typeof(op -> 'g') <> 'string' or jsonb_typeof(op -> 'o') <> 'string' then
        perform public.recusa('Opção inválida. Atualize a página.', 'PRICE_CHANGED');
      end if;
      gid := op ->> 'g'; oid := op ->> 'o'; grp := null; itm := null;
      select x into grp from jsonb_array_elements(prod.opcoes) x where x ->> 'id' = gid limit 1;
      if grp is not null then
        select y into itm from jsonb_array_elements(grp -> 'itens') y where y ->> 'id' = oid limit 1;
      end if;
      if itm is null or (gid || ':' || oid) = any (vistos) then
        perform public.recusa('Uma opção do cardápio mudou. Atualize a página.', 'PRICE_CHANGED');
      end if;
      vistos := vistos || (gid || ':' || oid);
      cont := jsonb_set(cont, array[gid], to_jsonb(coalesce((cont ->> gid)::int, 0) + 1));
      unit := unit + (itm ->> 'preco')::numeric;
      ops := ops || jsonb_build_object('group', grp ->> 'nome', 'name', itm ->> 'nome', 'price', (itm ->> 'preco')::numeric);
    end loop;
    for grp in select * from jsonb_array_elements(prod.opcoes) loop
      c := coalesce((cont ->> (grp ->> 'id'))::int, 0);
      if c < (grp ->> 'min')::int then
        perform public.recusa(format('Escolha %s em "%s" (%s).', case when (grp ->> 'min')::int = 1 then 'uma opção' else (grp ->> 'min') || ' opções' end,
                                     grp ->> 'nome', prod.name));
      end if;
      if c > (grp ->> 'max')::int then
        perform public.recusa(format('Você escolheu opções demais em "%s" (%s).', grp ->> 'nome', prod.name));
      end if;
    end loop;
    soma := soma + unit * qtd;
    itens := itens || jsonb_build_object('product_id', prod.id, 'name', prod.name, 'unit', prod.unit,
                                         'price', unit, 'qty', qtd, 'options', ops);
  end loop;

  soma  := round(soma, 2);
  if soma < loja.min_order then
    perform public.recusa(format('Pedido mínimo: R$ %s.', replace(to_char(loja.min_order, 'FM999990.00'), '.', ',')));
  end if;
  taxa  := case when tipo = 'entrega' then loja.delivery_fee else 0 end;
  -- loja com taxa por bairro: o bairro precisa ser um dos cadastrados e a taxa vem do servidor
  if tipo = 'entrega' and jsonb_typeof(loja.extra -> 'bairros') = 'array' and jsonb_array_length(loja.extra -> 'bairros') > 0 then
    select x into bx from jsonb_array_elements(loja.extra -> 'bairros') x where lower(btrim(x ->> 'n')) = lower(bairro) limit 1;
    if bx is null then perform public.recusa('Escolha o bairro da entrega.'); end if;
    bairro := btrim(bx ->> 'n'); taxa := (bx ->> 't')::numeric;
    if position(lower(bairro) in lower(ender)) = 0 then ender := ender || ' - ' || bairro; end if;
  else
    bairro := '';
  end if;
  -- cupom do cartão de volta: conferido aqui, nunca no navegador
  if cup <> '' then
    if not coalesce((loja.cupom ->> 'ativo')::boolean, false) or cup is distinct from (loja.cupom ->> 'codigo') then
      perform public.recusa('Este cupom não vale nesta loja. Confira o código.', 'CUPOM');
    end if;
    if soma < coalesce((loja.cupom ->> 'minimo')::numeric, 0) then
      perform public.recusa(format('O cupom vale para pedidos a partir de R$ %s.', replace(to_char((loja.cupom ->> 'minimo')::numeric, 'FM999990.00'), '.', ',')), 'CUPOM');
    end if;
    if coalesce((loja.cupom ->> 'uma_vez')::boolean, true) and exists (
         select 1 from public.orders o where o.loja_id = loja.id and o.coupon = cup and o.status <> 'cancelado'
           and regexp_replace(o.customer_phone, '\D', '', 'g') = digs) then
      perform public.recusa('Este cupom já foi usado neste WhatsApp.', 'CUPOM');
    end if;
    descon := round(soma * (loja.cupom ->> 'pct')::numeric / 100, 2);
  end if;
  total := round(soma - descon + taxa, 2);
  if jsonb_typeof(p_order -> 'expected_total') = 'number' and round((p_order ->> 'expected_total')::numeric, 2) <> total then
    perform public.recusa('Os preços mudaram desde que você montou o pedido. Confira o novo total e envie de novo.', 'PRICE_CHANGED');
  end if;

  if coalesce(current_setting('bc.interno', true), '') <> '1' and ((select count(*) from public.orders o where o.loja_id = loja.id and o.created_at > now() - interval '10 minutes'
        and regexp_replace(o.customer_phone, '\D', '', 'g') = digs) >= 5
     or (select count(*) from public.orders o where o.loja_id = loja.id and o.created_at > now() - interval '10 minutes') >= 120) then
    perform public.recusa('Muitos pedidos seguidos. Fale com a loja no WhatsApp.');
  end if;

  perform pg_advisory_xact_lock(hashtext('pedido:' || loja.id::text));
  select coalesce(max(o.seq), 0) + 1 into proximo from public.orders o where o.loja_id = loja.id;

  loop
    codigo := substr(replace(gen_random_uuid()::text, '-', ''), 1, 16);
    exit when not exists (select 1 from public.orders o where o.track_code = codigo);
  end loop;
  insert into public.orders (loja_id, seq, code, idem_key, track_token, track_code, customer_name, customer_phone, delivery_type,
                             address, scheduled_for, notes, items, subtotal, delivery_fee, total, payment_method, discount, coupon, bairro)
  values (loja.id, proximo, '#' || proximo::text, p_idem,
          replace(gen_random_uuid()::text, '-', '') || replace(gen_random_uuid()::text, '-', ''), codigo,
          nome, fone, tipo, ender, quando, obs, itens, soma, taxa, total, forma, descon, case when descon > 0 then cup else '' end, bairro)
  returning * into novo;
  insert into public.order_events (order_id, loja_id, actor, campo, para) values (novo.id, loja.id, 'cliente', 'status', 'novo');

  return jsonb_build_object('code', novo.code, 'track_token', novo.track_token, 'track_code', novo.track_code, 'total', novo.total,
                            'subtotal', novo.subtotal, 'delivery_fee', novo.delivery_fee, 'discount', novo.discount, 'coupon', novo.coupon, 'items', novo.items);
end $$;
