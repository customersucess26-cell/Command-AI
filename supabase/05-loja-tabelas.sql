-- eBistrô · 05: tabelas da loja (sites de nicho com painel: hamburgueria, Âmbar e próximos)
-- Rode no Supabase da loja, nesta ordem: 01-admins.sql, 05-loja-tabelas.sql, 03-loja-pedidos.sql
-- e depois o seed do site (seed-hamburgueria.sql ou seed-ambar.sql). Pode rodar de novo sem perder dados.

create table if not exists public.settings (
  id            int primary key default 1 check (id = 1),
  store_name    text not null default 'Minha loja',
  whatsapp      text not null default '',
  address       text not null default '',
  hours         text not null default '',
  instagram     text not null default '',
  delivery_fee  numeric(10,2) not null default 0 check (delivery_fee >= 0),
  min_order     numeric(10,2) not null default 0 check (min_order >= 0),
  accept_orders boolean not null default true,
  extra         jsonb not null default '{}'::jsonb,
  updated_at    timestamptz not null default now()
);
insert into public.settings (id) values (1) on conflict (id) do nothing;

create table if not exists public.categories (
  id       text primary key default gen_random_uuid()::text,
  name     text not null check (length(name) between 1 and 60),
  position int not null default 0,
  active   boolean not null default true,
  extra    jsonb not null default '{}'::jsonb
);

create table if not exists public.products (
  id          text primary key default gen_random_uuid()::text,
  category_id text references public.categories (id) on delete set null,
  name        text not null check (length(name) between 1 and 100),
  description text not null default '' check (length(description) <= 400),
  price       numeric(10,2) not null default 0 check (price >= 0),
  unit        text not null default '',
  image_url   text not null default '',
  active      boolean not null default true,
  featured    boolean not null default false,
  badge       text not null default '',
  position    int not null default 0,
  extra       jsonb not null default '{}'::jsonb,
  created_at  timestamptz not null default now()
);
create index if not exists products_category_idx on public.products (category_id, position);

create table if not exists public.orders (
  id             uuid primary key default gen_random_uuid(),
  code           text not null default '',
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now(),
  status         text not null default 'novo' check (status in ('novo','confirmado','em_preparo','pronto','entregue','cancelado')),
  admin_notes    text not null default '',
  customer_name  text not null default '',
  customer_phone text not null default '',
  delivery_type  text not null default 'retirada',
  address        text not null default '',
  scheduled_for  text not null default '',
  notes          text not null default '',
  items          jsonb not null default '[]'::jsonb,
  subtotal       numeric(10,2) not null default 0,
  delivery_fee   numeric(10,2) not null default 0,
  total          numeric(10,2) not null default 0,
  payment_method text not null default '',
  payment_status text not null default 'pendente' check (payment_status in ('pendente','pago','estornado'))
);
alter table public.orders add column if not exists payment_method text not null default '';
alter table public.orders add column if not exists payment_status text not null default 'pendente';
alter table public.orders add column if not exists updated_at timestamptz not null default now();
create index if not exists orders_created_idx on public.orders (created_at desc);

create table if not exists public.subscribers (
  id         bigint generated always as identity primary key,
  email      text not null unique,
  created_at timestamptz not null default now()
);

-- pedido feito pelo site: pagamento sempre começa "pendente"; forma só entre as aceitas
create or replace function public.pedido_pagamento()
returns trigger
language plpgsql security definer
set search_path = ''
as $$
begin
  if public.eh_admin() then
    return new;
  end if;
  new.payment_status := 'pendente';
  if new.payment_method not in ('Pix', 'Cartão', 'Dinheiro') then
    new.payment_method := '';
  end if;
  return new;
end $$;
revoke all on function public.pedido_pagamento() from public;
drop trigger if exists pedido_pagamento on public.orders;
create trigger pedido_pagamento before insert on public.orders
  for each row execute function public.pedido_pagamento();

create or replace function public.toca_updated_at()
returns trigger language plpgsql set search_path = '' as $$
begin new.updated_at := now(); return new; end $$;
drop trigger if exists orders_updated_at on public.orders;
create trigger orders_updated_at before update on public.orders
  for each row execute function public.toca_updated_at();
drop trigger if exists settings_updated_at on public.settings;
create trigger settings_updated_at before update on public.settings
  for each row execute function public.toca_updated_at();

-- bucket público de fotos do cardápio (as regras de envio estão no 03-loja-pedidos.sql)
do $$
begin
  if to_regclass('storage.buckets') is not null then
    insert into storage.buckets (id, name, public) values ('site', 'site', true) on conflict (id) do nothing;
  end if;
end $$;

-- painel atualiza sozinho quando chega pedido ou muda o cardápio
do $$
declare t text;
begin
  if exists (select 1 from pg_publication where pubname = 'supabase_realtime') then
    foreach t in array array['orders', 'products', 'categories', 'settings'] loop
      if not exists (select 1 from pg_publication_tables where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = t) then
        execute format('alter publication supabase_realtime add table public.%I', t);
      end if;
    end loop;
  end if;
end $$;
