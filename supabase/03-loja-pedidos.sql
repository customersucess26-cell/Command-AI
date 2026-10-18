-- eBistrô · 03: loja com cardápio e pedidos (modelo padaria/café e sites de nicho)
-- Rode depois do 01-admins.sql, no Supabase de CADA loja.
--
-- O que este arquivo garante:
--   * cliente vê só o cardápio público (produtos ativos, textos, fotos);
--   * cliente só CRIA pedido e assina a newsletter; não lê pedidos de ninguém;
--   * o banco recalcula preço, subtotal, taxa e total de cada pedido com os
--     preços cadastrados. Mexer no preço pelo navegador não adianta;
--   * pedido com produto pausado, quantidade absurda ou loja fechada é recusado;
--   * só administradores (tabela admins) alteram cardápio, pedidos e fotos.
--
-- ATENÇÃO: substitui as políticas atuais destas tabelas. Os usuários do painel
-- precisam estar na tabela admins (ver 01-admins.sql).

-- remove políticas antigas e liga a RLS nas tabelas que existirem
do $$
declare t text; p record;
begin
  foreach t in array array['settings','features','categories','products','gallery','videos','orders','subscribers'] loop
    if to_regclass('public.' || t) is null then continue; end if;
    execute format('alter table public.%I enable row level security', t);
    execute format('alter table public.%I force row level security', t);
    for p in select policyname from pg_policies where schemaname = 'public' and tablename = t loop
      execute format('drop policy %I on public.%I', p.policyname, t);
    end loop;
    execute format('revoke all on public.%I from anon, authenticated', t);
    execute format('grant select, insert, update, delete on public.%I to authenticated', t);
    execute format('create policy "admin gerencia" on public.%I for all to authenticated using (public.eh_admin()) with check (public.eh_admin())', t);
  end loop;
end $$;

-- leitura pública do cardápio e do site
do $$
declare t text;
begin
  foreach t in array array['settings','features','categories','gallery','videos'] loop
    if to_regclass('public.' || t) is null then continue; end if;
    execute format('grant select on public.%I to anon', t);
    execute format('create policy "publico le" on public.%I for select to anon using (true)', t);
  end loop;
  if to_regclass('public.products') is not null then
    grant select on public.products to anon;
    create policy "publico le ativos" on public.products for select to anon using (active);
  end if;
  if to_regclass('public.subscribers') is not null then
    grant insert (email) on public.subscribers to anon;
    create policy "visitante assina" on public.subscribers for insert to anon
      with check (email ~* '^[^@\s]{1,64}@[^@\s]{1,190}\.[^@\s]{2,24}$');
  end if;
  if to_regclass('public.orders') is not null then
    grant insert on public.orders to anon;
    create policy "cliente cria pedido" on public.orders for insert to anon
      with check (status = 'novo');
  end if;
end $$;

-- sequências de id (se houver) para o visitante conseguir inserir
do $$
declare s text;
begin
  foreach s in array array[pg_get_serial_sequence('public.orders', 'id'), pg_get_serial_sequence('public.subscribers', 'id')] loop
    if s is not null then execute format('grant usage on sequence %s to anon', s); end if;
  end loop;
exception when others then null;
end $$;

-- preço e total sempre calculados pelo banco
create or replace function public.pedido_confere()
returns trigger
language plpgsql security definer
set search_path = ''
as $$
declare
  it      jsonb;
  prod    record;
  qtd     int;
  itens   jsonb := '[]'::jsonb;
  soma    numeric := 0;
  taxa    numeric := 0;
  cfg     jsonb;
begin
  if public.eh_admin() then
    return new;
  end if;

  select to_jsonb(s) into cfg from public.settings s where s.id = 1;
  if cfg is not null and coalesce((cfg ->> 'accept_orders')::boolean, true) = false then
    raise exception 'A loja não está recebendo encomendas agora.' using errcode = 'P0001';
  end if;

  if jsonb_typeof(new.items) <> 'array' or jsonb_array_length(new.items) = 0 or jsonb_array_length(new.items) > 50 then
    raise exception 'Pedido sem itens válidos.' using errcode = 'P0001';
  end if;

  for it in select * from jsonb_array_elements(new.items) loop
    qtd := coalesce((it ->> 'qty')::int, 0);
    if qtd < 1 or qtd > 99 then
      raise exception 'Quantidade inválida.' using errcode = 'P0001';
    end if;
    select p.id, p.name, p.unit, coalesce(p.price, 0) as price into prod
      from public.products p
     where p.id::text = it ->> 'product_id' and p.active;
    if not found then
      raise exception 'Um dos produtos não está mais disponível. Atualize a página.' using errcode = 'P0001';
    end if;
    itens := itens || jsonb_build_object('product_id', prod.id, 'name', prod.name, 'unit', prod.unit,
                                         'price', prod.price, 'qty', qtd);
    soma := soma + prod.price * qtd;
  end loop;

  if new.delivery_type = 'entrega' then
    taxa := coalesce((cfg ->> 'delivery_fee')::numeric, 0);
  elsif new.delivery_type is distinct from 'retirada' then
    raise exception 'Escolha entrega ou retirada.' using errcode = 'P0001';
  end if;

  if length(coalesce(new.customer_name, '')) not between 2 and 120
     or regexp_replace(coalesce(new.customer_phone, ''), '\D', '', 'g') !~ '^\d{10,13}$'
     or length(coalesce(new.address, '')) > 300
     or length(coalesce(new.notes, '')) > 1000 then
    raise exception 'Confira nome, WhatsApp e endereço.' using errcode = 'P0001';
  end if;

  new.items        := itens;
  new.subtotal     := round(soma, 2);
  new.delivery_fee := round(taxa, 2);
  new.total        := round(soma + taxa, 2);
  new.status       := 'novo';
  new.admin_notes  := '';
  new.created_at   := now();
  new.code         := left(coalesce(new.code, ''), 16);
  if to_jsonb(new) ? 'track_token' and coalesce(to_jsonb(new) ->> 'track_token', '') !~ '^[a-f0-9]{32,64}$' then
    new := jsonb_populate_record(new, jsonb_build_object('track_token',
             replace(gen_random_uuid()::text, '-', '') || replace(gen_random_uuid()::text, '-', '')));
  end if;

  if (select count(*) from public.orders
       where created_at > now() - interval '10 minutes'
         and regexp_replace(customer_phone, '\D', '', 'g') = regexp_replace(new.customer_phone, '\D', '', 'g')) >= 5 then
    raise exception 'Muitos pedidos seguidos deste número. Fale com a loja no WhatsApp.' using errcode = 'P0001';
  end if;
  return new;
end $$;
revoke all on function public.pedido_confere() from public;

do $$
begin
  if to_regclass('public.orders') is not null then
    drop trigger if exists pedido_confere on public.orders;
    create trigger pedido_confere before insert on public.orders
      for each row execute function public.pedido_confere();
  end if;
end $$;

-- fotos (bucket "site"): todo mundo vê, só admin envia ou apaga
do $$
declare p record;
begin
  if to_regclass('storage.objects') is null then return; end if;
  for p in select policyname from pg_policies where schemaname = 'storage' and tablename = 'objects'
           and policyname in ('site: publico le', 'site: admin envia', 'site: admin altera', 'site: admin apaga') loop
    execute format('drop policy %I on storage.objects', p.policyname);
  end loop;
  create policy "site: publico le"   on storage.objects for select using (bucket_id = 'site');
  create policy "site: admin envia"  on storage.objects for insert to authenticated with check (bucket_id = 'site' and public.eh_admin());
  create policy "site: admin altera" on storage.objects for update to authenticated using (bucket_id = 'site' and public.eh_admin());
  create policy "site: admin apaga"  on storage.objects for delete to authenticated using (bucket_id = 'site' and public.eh_admin());
end $$;
