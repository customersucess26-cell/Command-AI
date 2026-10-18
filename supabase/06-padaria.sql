-- eBistrô · 06: banco do site Padaria & Café (sites/padaria-cafe)
-- Rode no Supabase DA PADARIA, nesta ordem: 01-admins.sql, 06-padaria.sql e seed-padaria.sql.
-- Pode rodar de novo sem perder dados.
--
-- O que este arquivo garante:
--   * visitante lê só o que o site mostra (textos, cardápio ativo, fotos, vídeos);
--   * visitante NÃO lê pedidos nem clientes. Ele só cria o pedido pela função create_order
--     e acompanha o próprio pedido pelo link de rastreio (código secreto de 64 caracteres);
--   * o banco recalcula preço, taxa e total com os preços cadastrados. Mexer no navegador não adianta;
--   * status, pagamento, estorno e desconto só mudam pelo painel e seguem as regras
--     (não pula etapa, não recebe mais que o total, não estorna mais que o recebido);
--   * cada mudança fica no histórico do pedido (order_events), com quem fez e quando;
--   * só administradores (tabela admins, ver 01-admins.sql) alteram cardápio, textos e pedidos.

-- ============ tabelas ============
create table if not exists public.stores (
  id         uuid primary key default gen_random_uuid(),
  slug       text not null unique check (slug ~ '^[a-z0-9-]{2,40}$'),
  name       text not null default '',
  created_at timestamptz not null default now()
);

-- textos e configurações do site: um documento por loja
create table if not exists public.settings (
  store_id   uuid primary key references public.stores (id) on delete cascade,
  data       jsonb not null default '{}'::jsonb check (jsonb_typeof(data) = 'object'),
  updated_at timestamptz not null default now()
);

create table if not exists public.features (
  id       text primary key default gen_random_uuid()::text,
  store_id uuid not null references public.stores (id) on delete cascade,
  title    text not null default '' check (length(title) <= 120),
  text     text not null default '' check (length(text) <= 600),
  icon     text not null default '' check (length(icon) <= 30),
  position int  not null default 0
);

create table if not exists public.categories (
  id       text primary key default gen_random_uuid()::text,
  store_id uuid not null references public.stores (id) on delete cascade,
  name     text not null check (length(name) between 1 and 60),
  position int  not null default 0,
  menu     text not null default 'padaria' check (menu in ('padaria', 'cafe'))
);

create table if not exists public.products (
  id          text primary key default gen_random_uuid()::text,
  store_id    uuid not null references public.stores (id) on delete cascade,
  category_id text references public.categories (id) on delete set null,
  name        text not null check (length(name) between 1 and 100),
  description text not null default '' check (length(description) <= 600),
  price       numeric(10,2) not null default 0 check (price >= 0 and price <= 99999),
  unit        text not null default '' check (length(unit) <= 40),
  image_url   text not null default '' check (length(image_url) <= 1000),
  badge       text not null default '' check (length(badge) <= 40),
  featured    boolean not null default false,
  bake        boolean not null default false,
  bake_note   text not null default '' check (length(bake_note) <= 120),
  active      boolean not null default true,
  available   boolean not null default true,
  position    int not null default 0,
  created_at  timestamptz not null default now()
);
create index if not exists products_store_idx on public.products (store_id, position);

create table if not exists public.gallery (
  id        text primary key default gen_random_uuid()::text,
  store_id  uuid not null references public.stores (id) on delete cascade,
  image_url text not null default '' check (length(image_url) <= 1000),
  alt       text not null default '' check (length(alt) <= 160),
  position  int  not null default 0
);

create table if not exists public.videos (
  id       text primary key default gen_random_uuid()::text,
  store_id uuid not null references public.stores (id) on delete cascade,
  url      text not null check (url ~ '^https://' and length(url) <= 500),
  title    text not null default '' check (length(title) <= 160),
  poster   text not null default '' check (length(poster) <= 1000),
  position int  not null default 0
);

create table if not exists public.orders (
  id              uuid primary key default gen_random_uuid(),
  store_id        uuid not null references public.stores (id) on delete cascade,
  seq             int  not null,
  code            text not null,
  idem_key        text not null,
  track_token     text not null unique,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now(),
  status          text not null default 'novo'
                  check (status in ('novo','confirmado','em_preparo','pronto','entregue','cancelado')),
  customer_name   text not null,
  customer_phone  text not null,
  delivery_type   text not null check (delivery_type in ('retirada','entrega')),
  address         text not null default '',
  scheduled_for   text not null default '',
  scheduled_date  date,
  notes           text not null default '',
  items           jsonb not null default '[]'::jsonb,
  has_quote_items boolean not null default false,
  subtotal        numeric(10,2) not null default 0,
  delivery_fee    numeric(10,2) not null default 0,
  quoted_amount   numeric(10,2) not null default 0,
  discount        numeric(10,2) not null default 0,
  total           numeric(10,2) not null default 0,
  payment_method  text not null default 'a_combinar'
                  check (payment_method in ('pix','dinheiro','cartao','a_combinar')),
  payment_status  text not null default 'pendente' check (payment_status in ('pendente','parcial','pago')),
  paid_amount     numeric(10,2) not null default 0,
  paid_at         timestamptz,
  refunded_amount numeric(10,2) not null default 0,
  refunded_at     timestamptz,
  admin_notes     text not null default '',
  unique (store_id, seq),
  unique (store_id, idem_key)
);
create index if not exists orders_store_created_idx on public.orders (store_id, created_at desc);

create table if not exists public.order_events (
  id         bigint generated always as identity primary key,
  order_id   uuid not null references public.orders (id) on delete cascade,
  at         timestamptz not null default now(),
  actor      text not null default '',
  type       text not null,
  from_value text,
  to_value   text,
  note       text
);
create index if not exists order_events_order_idx on public.order_events (order_id, id);

create table if not exists public.subscribers (
  id         text primary key default gen_random_uuid()::text,
  store_id   uuid not null references public.stores (id) on delete cascade,
  email      text not null check (email ~* '^[^@\s]{1,64}@[^@\s]{1,190}\.[^@\s]{2,24}$'),
  created_at timestamptz not null default now(),
  unique (store_id, email)
);

-- ============ permissões (RLS) ============
do $$
declare t text; p record;
begin
  foreach t in array array['stores','settings','features','categories','products','gallery','videos',
                           'orders','order_events','subscribers'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('alter table public.%I force row level security', t);
    for p in select policyname from pg_policies where schemaname = 'public' and tablename = t loop
      execute format('drop policy %I on public.%I', p.policyname, t);
    end loop;
    execute format('revoke all on public.%I from anon, authenticated', t);
  end loop;

  -- conteúdo do site: todos leem, só admin altera
  foreach t in array array['stores','settings','features','categories','gallery','videos'] loop
    execute format('grant select on public.%I to anon, authenticated', t);
    execute format('grant insert, update, delete on public.%I to authenticated', t);
    execute format('create policy "publico le" on public.%I for select using (true)', t);
    execute format('create policy "admin insere" on public.%I for insert to authenticated with check (public.eh_admin())', t);
    execute format('create policy "admin altera" on public.%I for update to authenticated using (public.eh_admin()) with check (public.eh_admin())', t);
    execute format('create policy "admin apaga" on public.%I for delete to authenticated using (public.eh_admin())', t);
  end loop;
end $$;

grant select on public.products to anon, authenticated;
grant insert, update, delete on public.products to authenticated;
create policy "publico le ativos" on public.products for select using (active or public.eh_admin());
create policy "admin insere" on public.products for insert to authenticated with check (public.eh_admin());
create policy "admin altera" on public.products for update to authenticated using (public.eh_admin()) with check (public.eh_admin());
create policy "admin apaga" on public.products for delete to authenticated using (public.eh_admin());

-- pedidos: só admin lê; criar e alterar só pelas funções abaixo
grant select on public.orders, public.order_events to authenticated;
create policy "admin le" on public.orders for select to authenticated using (public.eh_admin());
create policy "admin le" on public.order_events for select to authenticated using (public.eh_admin());

-- newsletter: visitante só cadastra o e-mail; admin lê e apaga
grant insert (store_id, email) on public.subscribers to anon, authenticated;
grant select, delete on public.subscribers to authenticated;
create policy "visitante assina" on public.subscribers for insert with check (true);
create policy "admin le" on public.subscribers for select to authenticated using (public.eh_admin());
create policy "admin apaga" on public.subscribers for delete to authenticated using (public.eh_admin());

-- ============ funções auxiliares ============
create or replace function public.toca_updated_at()
returns trigger language plpgsql set search_path = '' as $$
begin new.updated_at := now(); return new; end $$;
drop trigger if exists settings_updated_at on public.settings;
create trigger settings_updated_at before insert or update on public.settings
  for each row execute function public.toca_updated_at();

-- quem está mexendo (para o histórico)
create or replace function public.quem()
returns text language sql stable security definer set search_path = '' as $$
  select coalesce((select u.email from auth.users u where u.id = auth.uid()), 'admin')
$$;
revoke all on function public.quem() from public;

-- erro amigável que o site mostra para o cliente (código P0001 + dica)
create or replace function public.recusa(msg text, dica text default '')
returns void language plpgsql set search_path = '' as $$
begin
  raise exception '%', msg using errcode = 'P0001', hint = dica;
end $$;

-- ============ criar pedido (site) ============
create or replace function public.create_order(p_store uuid, p_idem text, p_order jsonb)
returns jsonb
language plpgsql security definer
set search_path = ''
as $$
declare
  cfg     jsonb;
  ja      public.orders;
  novo    public.orders;
  nome    text := btrim(coalesce(p_order ->> 'customer_name', ''));
  fone    text := btrim(coalesce(p_order ->> 'customer_phone', ''));
  digs    text := regexp_replace(coalesce(p_order ->> 'customer_phone', ''), '\D', '', 'g');
  tipo    text := coalesce(p_order ->> 'delivery_type', '');
  ender   text := btrim(coalesce(p_order ->> 'address', ''));
  obs     text := btrim(coalesce(p_order ->> 'notes', ''));
  forma   text := coalesce(nullif(p_order ->> 'payment_method', ''), 'a_combinar');
  hora    text := coalesce(p_order ->> 'time', '');
  dia_txt text := coalesce(p_order ->> 'date', '');
  dia     date;
  fuso    text;
  minimo  date;
  hoje    date;
  it      jsonb;
  qtds    jsonb := '{}'::jsonb;
  pid     text;
  qtd     int;
  prod    public.products;
  itens   jsonb := '[]'::jsonb;
  soma    numeric := 0;
  consulta boolean := false;
  taxa    numeric := 0;
  total   numeric;
  proximo int;
begin
  if p_store is null or not exists (select 1 from public.stores s where s.id = p_store) then
    perform public.recusa('Loja não encontrada.');
  end if;
  if coalesce(p_idem, '') !~ '^[A-Za-z0-9_-]{8,80}$' then
    perform public.recusa('Pedido inválido. Atualize a página e tente de novo.');
  end if;

  -- mesmo pedido enviado duas vezes (clique duplo, internet caindo): devolve o primeiro
  select * into ja from public.orders o where o.store_id = p_store and o.idem_key = p_idem;
  if found then
    return to_jsonb(ja) - 'idem_key' - 'admin_notes';
  end if;

  select s.data into cfg from public.settings s where s.store_id = p_store;
  cfg := coalesce(cfg, '{}'::jsonb);
  if coalesce((cfg ->> 'accept_orders')::boolean, true) = false then
    perform public.recusa('A loja não está recebendo encomendas pelo site agora. Fale com a gente no WhatsApp.');
  end if;

  if length(nome) < 2 or length(nome) > 120 then perform public.recusa('Informe seu nome.'); end if;
  if length(digs) < 10 or length(digs) > 13 or length(fone) > 30 then
    perform public.recusa('Informe um WhatsApp com DDD, como (42) 99999-9999.');
  end if;
  if tipo not in ('retirada', 'entrega') then perform public.recusa('Escolha retirada ou entrega.'); end if;
  if tipo = 'entrega' then
    if length(ender) < 8 or length(ender) > 300 then
      perform public.recusa('Informe o endereço completo para entrega.');
    end if;
  else
    ender := '';
  end if;
  if length(obs) > 500 then perform public.recusa('As observações passam de 500 caracteres.'); end if;
  if forma not in ('pix', 'dinheiro', 'cartao', 'a_combinar') then
    perform public.recusa('Forma de pagamento inválida.');
  end if;
  if forma <> 'a_combinar' and not coalesce(cfg -> 'payment_methods', '[]'::jsonb) ? forma then
    perform public.recusa('Essa forma de pagamento não está disponível nesta loja.');
  end if;
  if hora <> '' and hora !~ '^([01][0-9]|2[0-3]):[0-5][0-9]$' then
    perform public.recusa('Horário inválido.');
  end if;

  if dia_txt !~ '^\d{4}-\d{2}-\d{2}$' then
    perform public.recusa('Escolha o dia da retirada ou entrega.');
  end if;
  begin
    dia := dia_txt::date;
  exception when others then
    perform public.recusa('Escolha o dia da retirada ou entrega.');
  end;
  fuso := coalesce(nullif(cfg ->> 'timezone', ''), 'America/Sao_Paulo');
  if not exists (select 1 from pg_catalog.pg_timezone_names z where z.name = fuso) then
    fuso := 'America/Sao_Paulo';
  end if;
  hoje   := (now() at time zone fuso)::date;
  minimo := ((now() + coalesce((cfg ->> 'min_notice_hours')::numeric, 0) * interval '1 hour') at time zone fuso)::date;
  if dia < hoje then
    perform public.recusa('Escolha uma data a partir de hoje.');
  end if;
  if dia < minimo then
    perform public.recusa(format('Encomendas precisam de pelo menos %s horas de antecedência.',
                                 coalesce(cfg ->> 'min_notice_hours', '0')));
  end if;
  if dia > hoje + 365 then perform public.recusa('Data muito distante.'); end if;

  if jsonb_typeof(p_order -> 'items') is distinct from 'array'
     or jsonb_array_length(p_order -> 'items') < 1
     or jsonb_array_length(p_order -> 'items') > 40 then
    perform public.recusa('Sua encomenda está vazia.');
  end if;
  for it in select * from jsonb_array_elements(p_order -> 'items') loop
    if jsonb_typeof(it) <> 'object' or jsonb_typeof(it -> 'qty') <> 'number'
       or jsonb_typeof(it -> 'product_id') <> 'string' then
      perform public.recusa('Item inválido na encomenda.');
    end if;
    if (it ->> 'qty')::numeric <> trunc((it ->> 'qty')::numeric)
       or (it ->> 'qty')::numeric < 1 or (it ->> 'qty')::numeric > 99 then
      perform public.recusa('Quantidade inválida: use de 1 a 99 por produto.');
    end if;
    pid := it ->> 'product_id';
    qtds := jsonb_set(qtds, array[pid], to_jsonb(coalesce((qtds ->> pid)::int, 0) + (it ->> 'qty')::int));
  end loop;

  for pid, qtd in select key, value::int from jsonb_each_text(qtds) loop
    select * into prod from public.products p where p.id = pid and p.store_id = p_store;
    if not found or not prod.active then
      perform public.recusa('Um dos produtos não está mais no cardápio. Atualize a página.', 'PRICE_CHANGED');
    end if;
    if not prod.available then
      perform public.recusa(format('"%s" está indisponível no momento. Remova da encomenda.', prod.name), 'UNAVAILABLE');
    end if;
    if qtd > 99 then perform public.recusa('Quantidade inválida: use de 1 a 99 por produto.'); end if;
    if prod.price > 0 then soma := soma + prod.price * qtd; else consulta := true; end if;
    itens := itens || jsonb_build_object('product_id', prod.id, 'name', prod.name, 'unit', prod.unit,
                                         'price', prod.price, 'qty', qtd);
  end loop;

  soma  := round(soma, 2);
  taxa  := case when tipo = 'entrega' then round(coalesce((cfg ->> 'delivery_fee')::numeric, 0), 2) else 0 end;
  total := round(soma + taxa, 2);
  if jsonb_typeof(p_order -> 'expected_total') = 'number'
     and round((p_order ->> 'expected_total')::numeric, 2) <> total then
    perform public.recusa('Os preços mudaram desde que você montou a encomenda. Confira o novo total e envie de novo.',
                          'PRICE_CHANGED');
  end if;

  -- freio contra robôs: até 5 pedidos do mesmo WhatsApp em 10 minutos e 60 por loja em 10 minutos
  if (select count(*) from public.orders o
       where o.store_id = p_store and o.created_at > now() - interval '10 minutes'
         and regexp_replace(o.customer_phone, '\D', '', 'g') = digs) >= 5
     or (select count(*) from public.orders o
       where o.store_id = p_store and o.created_at > now() - interval '10 minutes') >= 60 then
    perform public.recusa('Muitos pedidos seguidos. Fale com a loja no WhatsApp.');
  end if;

  perform pg_advisory_xact_lock(hashtext('pedido:' || p_store::text));
  select coalesce(max(o.seq), 0) + 1 into proximo from public.orders o where o.store_id = p_store;

  insert into public.orders (store_id, seq, code, idem_key, track_token, status,
                             customer_name, customer_phone, delivery_type, address,
                             scheduled_for, scheduled_date, notes, items, has_quote_items,
                             subtotal, delivery_fee, total, payment_method)
  values (p_store, proximo, 'LO' || lpad(proximo::text, 5, '0'), p_idem,
          replace(gen_random_uuid()::text, '-', '') || replace(gen_random_uuid()::text, '-', ''),
          'novo', nome, fone, tipo, ender,
          to_char(dia, 'DD/MM/YYYY') || case when hora <> '' then ' às ' || hora else '' end,
          dia, obs, itens, consulta, soma, taxa, total, forma)
  returning * into novo;

  insert into public.order_events (order_id, actor, type, to_value)
  values (novo.id, 'cliente', 'criado', 'novo');

  return to_jsonb(novo) - 'idem_key' - 'admin_notes';
end $$;
revoke all on function public.create_order(uuid, text, jsonb) from public;
grant execute on function public.create_order(uuid, text, jsonb) to anon, authenticated;

-- ============ painel: mudar pedido ============
create or replace function public.pedido_do_admin(p_order uuid)
returns public.orders
language plpgsql security definer set search_path = '' as $$
declare o public.orders;
begin
  if not public.eh_admin() then
    raise exception 'Sem permissão.' using errcode = '42501';
  end if;
  select * into o from public.orders where id = p_order for update;
  if not found then perform public.recusa('Pedido não encontrado.'); end if;
  return o;
end $$;
revoke all on function public.pedido_do_admin(uuid) from public;

create or replace function public.admin_set_status(p_order uuid, p_to text, p_note text default '')
returns void language plpgsql security definer set search_path = '' as $$
declare o public.orders; pode text[];
begin
  o := public.pedido_do_admin(p_order);
  pode := case o.status
            when 'novo'       then array['confirmado','cancelado']
            when 'confirmado' then array['em_preparo','cancelado']
            when 'em_preparo' then array['pronto','cancelado']
            when 'pronto'     then array['entregue','cancelado']
            else array[]::text[] end;
  if not (p_to = any (pode)) then
    perform public.recusa(format('Não é possível mudar de "%s" para "%s".', o.status, p_to));
  end if;
  if p_to = 'confirmado' and o.has_quote_items and o.quoted_amount = 0 then
    perform public.recusa('Defina o valor dos itens "sob consulta" antes de confirmar o pedido.');
  end if;
  update public.orders set status = p_to, updated_at = now() where id = o.id;
  insert into public.order_events (order_id, actor, type, from_value, to_value, note)
  values (o.id, public.quem(), 'status', o.status, p_to, nullif(left(coalesce(p_note, ''), 500), ''));
end $$;

create or replace function public.admin_adjust_order(p_order uuid, p_quoted numeric, p_discount numeric, p_note text default '')
returns void language plpgsql security definer set search_path = '' as $$
declare o public.orders; q numeric; d numeric;
begin
  o := public.pedido_do_admin(p_order);
  if o.status not in ('novo','confirmado','em_preparo') then
    perform public.recusa('Este pedido não pode mais ser ajustado.');
  end if;
  if o.paid_amount > 0 then
    perform public.recusa('Já há pagamento registrado. Registre um estorno se precisar corrigir o valor.');
  end if;
  if p_quoted is null or p_discount is null or p_quoted < 0 or p_discount < 0 or p_quoted > 99999 or p_discount > 99999 then
    perform public.recusa('Valores inválidos.');
  end if;
  if p_quoted > 0 and not o.has_quote_items then
    perform public.recusa('Este pedido não tem itens "sob consulta".');
  end if;
  q := round(p_quoted, 2); d := round(p_discount, 2);
  if d > round(o.subtotal + q + o.delivery_fee, 2) then
    perform public.recusa('O desconto não pode passar do valor do pedido.');
  end if;
  update public.orders
     set quoted_amount = q, discount = d, total = round(o.subtotal + q + o.delivery_fee - d, 2), updated_at = now()
   where id = o.id;
  insert into public.order_events (order_id, actor, type, note)
  values (o.id, public.quem(), 'ajuste', nullif(left(coalesce(p_note, ''), 500), ''));
end $$;

create or replace function public.admin_register_payment(p_order uuid, p_method text, p_amount numeric)
returns void language plpgsql security definer set search_path = '' as $$
declare o public.orders; v numeric; pago numeric;
begin
  o := public.pedido_do_admin(p_order);
  if o.status = 'cancelado' then perform public.recusa('Pedido cancelado não recebe pagamento.'); end if;
  if o.has_quote_items and o.quoted_amount = 0 then
    perform public.recusa('Defina o valor dos itens "sob consulta" antes de registrar pagamento.');
  end if;
  if p_method not in ('pix','dinheiro','cartao') then perform public.recusa('Escolha a forma de pagamento.'); end if;
  if p_amount is null or p_amount <= 0 then perform public.recusa('Informe um valor maior que zero.'); end if;
  v := round(p_amount, 2);
  pago := round(o.paid_amount + v, 2);
  if pago > o.total then perform public.recusa('O valor passa do que falta receber neste pedido.'); end if;
  update public.orders
     set paid_amount = pago, payment_method = p_method,
         payment_status = case when pago = o.total then 'pago' else 'parcial' end,
         paid_at = now(), updated_at = now()
   where id = o.id;
  insert into public.order_events (order_id, actor, type, to_value, note)
  values (o.id, public.quem(), 'pagamento', v::text, p_method);
end $$;

create or replace function public.admin_register_refund(p_order uuid, p_amount numeric, p_note text default '')
returns void language plpgsql security definer set search_path = '' as $$
declare o public.orders; v numeric;
begin
  o := public.pedido_do_admin(p_order);
  if p_amount is null or p_amount <= 0 then perform public.recusa('Informe um valor maior que zero.'); end if;
  v := round(p_amount, 2);
  if round(o.refunded_amount + v, 2) > o.paid_amount then
    perform public.recusa('O estorno passa do valor recebido.');
  end if;
  update public.orders set refunded_amount = round(o.refunded_amount + v, 2), refunded_at = now(), updated_at = now()
   where id = o.id;
  insert into public.order_events (order_id, actor, type, to_value, note)
  values (o.id, public.quem(), 'estorno', v::text, nullif(left(coalesce(p_note, ''), 500), ''));
end $$;

create or replace function public.admin_set_notes(p_order uuid, p_notes text)
returns void language plpgsql security definer set search_path = '' as $$
declare o public.orders;
begin
  o := public.pedido_do_admin(p_order);
  update public.orders set admin_notes = left(coalesce(p_notes, ''), 2000), updated_at = now() where id = o.id;
  insert into public.order_events (order_id, actor, type) values (o.id, public.quem(), 'anotacao');
end $$;

-- usuários do painel (lista); criar e apagar usuário é feito no Supabase (ver SEGURANCA.md)
create or replace function public.admin_list_users()
returns table (email text, name text, created_at timestamptz)
language plpgsql stable security definer set search_path = '' as $$
begin
  if not public.eh_admin() then
    raise exception 'Sem permissão.' using errcode = '42501';
  end if;
  return query
    select u.email::text, coalesce(u.raw_user_meta_data ->> 'name', '')::text, a.criado_em
      from public.admins a join auth.users u on u.id = a.user_id
     order by a.criado_em;
end $$;

do $$
declare f text;
begin
  foreach f in array array['admin_set_status(uuid, text, text)', 'admin_adjust_order(uuid, numeric, numeric, text)',
                           'admin_register_payment(uuid, text, numeric)', 'admin_register_refund(uuid, numeric, text)',
                           'admin_set_notes(uuid, text)', 'admin_list_users()'] loop
    execute 'revoke all on function public.' || f || ' from public';
    execute 'grant execute on function public.' || f || ' to authenticated';
  end loop;
end $$;

-- ============ rastreio do pedido (link enviado ao cliente) ============
-- Devolve só o necessário para acompanhar: nada de telefone, endereço ou anotações internas.
create or replace function public.rastrear_pedido(p_token text)
returns jsonb
language plpgsql stable security definer
set search_path = ''
as $$
declare o public.orders; cfg jsonb;
begin
  if coalesce(p_token, '') !~ '^[a-f0-9]{32,64}$' then
    return null;
  end if;
  select * into o from public.orders where track_token = p_token;
  if not found then
    return null;
  end if;
  select s.data into cfg from public.settings s where s.store_id = o.store_id;
  return jsonb_build_object(
    'code', o.code,
    'status', o.status,
    'delivery_type', o.delivery_type,
    'scheduled_for', o.scheduled_for,
    'created_at', o.created_at,
    'updated_at', o.updated_at,
    'first_name', split_part(o.customer_name, ' ', 1),
    'items', (select coalesce(jsonb_agg(jsonb_build_object('name', i ->> 'name', 'unit', i ->> 'unit',
                                                           'qty', (i ->> 'qty')::int, 'price', (i ->> 'price')::numeric)), '[]'::jsonb)
                from jsonb_array_elements(o.items) i),
    'has_quote_items', o.has_quote_items,
    'subtotal', o.subtotal,
    'delivery_fee', o.delivery_fee,
    'quoted_amount', o.quoted_amount,
    'discount', o.discount,
    'total', o.total,
    'payment_method', o.payment_method,
    'payment_status', o.payment_status,
    'history', (select coalesce(jsonb_agg(jsonb_build_object('status', e.to_value, 'at', e.at) order by e.id), '[]'::jsonb)
                  from public.order_events e where e.order_id = o.id and e.type in ('criado', 'status')),
    'store_name', coalesce(cfg ->> 'store_name', ''),
    'whatsapp', coalesce(cfg ->> 'whatsapp', '')
  );
end $$;
revoke all on function public.rastrear_pedido(text) from public;
grant execute on function public.rastrear_pedido(text) to anon, authenticated;

-- ============ fotos (bucket "site") ============
do $$
declare p record;
begin
  if to_regclass('storage.buckets') is null then return; end if;
  insert into storage.buckets (id, name, public) values ('site', 'site', true) on conflict (id) do nothing;
  for p in select policyname from pg_policies where schemaname = 'storage' and tablename = 'objects'
           and policyname in ('site: publico le', 'site: admin envia', 'site: admin altera', 'site: admin apaga') loop
    execute format('drop policy %I on storage.objects', p.policyname);
  end loop;
  create policy "site: publico le"   on storage.objects for select using (bucket_id = 'site');
  create policy "site: admin envia"  on storage.objects for insert to authenticated with check (bucket_id = 'site' and public.eh_admin());
  create policy "site: admin altera" on storage.objects for update to authenticated using (bucket_id = 'site' and public.eh_admin());
  create policy "site: admin apaga"  on storage.objects for delete to authenticated using (bucket_id = 'site' and public.eh_admin());
end $$;

-- ============ painel atualiza sozinho quando chega pedido ============
do $$
begin
  if exists (select 1 from pg_publication where pubname = 'supabase_realtime')
     and not exists (select 1 from pg_publication_tables
                      where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = 'orders') then
    alter publication supabase_realtime add table public.orders;
  end if;
end $$;
