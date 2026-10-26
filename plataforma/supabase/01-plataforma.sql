-- Bistrô Connect · banco da plataforma (várias lojas num Supabase só)
-- Rode no SQL Editor do Supabase da plataforma. Pode rodar de novo sem perder dados.
--
-- Regras de segurança (valem no banco, não dependem da tela):
--   * cada linha de cardápio, pedido e equipe tem a loja dona (loja_id);
--   * quem é da equipe de uma loja só enxerga e altera aquela loja;
--   * dono e gerente precisam do login em 2 etapas (aal2) para mudar cardápio, loja e equipe;
--     atendente e cozinha mexem só nos pedidos;
--   * visitante lê só o cardápio ativo de lojas ativas e cria pedido pela função create_order,
--     que recalcula preço, taxa e total com os valores do banco;
--   * o cliente acompanha o pedido pelo link secreto (rastrear_pedido), sem ver dados pessoais;
--   * cada mudança de pedido fica registrada (order_events).

-- ================= administradores da plataforma (você) =================
create table if not exists public.plataforma_admins (
  user_id   uuid primary key references auth.users (id) on delete cascade,
  criado_em timestamptz not null default now()
);
alter table public.plataforma_admins enable row level security;
revoke all on public.plataforma_admins from anon, authenticated;

create or replace function public.eh_admin_plataforma()
returns boolean language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.plataforma_admins a where a.user_id = auth.uid())
         and coalesce(auth.jwt() ->> 'aal', '') = 'aal2'
$$;

-- ================= planos (preço pelo faturamento da loja na plataforma) =================
create table if not exists public.planos (
  id          text primary key,
  nome        text not null,
  ate_valor   numeric(12,2),            -- faturamento mensal máximo da faixa (null = sem limite)
  mensalidade numeric(10,2) not null,
  ordem       int not null default 0
);
insert into public.planos (id, nome, ate_valor, mensalidade, ordem) values
  ('inicio',   'Começo',      3000,  0,   1),
  ('cresce',   'Crescendo',   10000, 49,  2),
  ('forte',    'Forte',       30000, 99,  3),
  ('completo', 'Sem limites', null,  199, 4)
on conflict (id) do nothing;

-- ================= lojas =================
create table if not exists public.lojas (
  id            uuid primary key default gen_random_uuid(),
  slug          text not null unique check (slug ~ '^[a-z0-9](?:[a-z0-9-]{1,38}[a-z0-9])$'),
  store_name    text not null check (length(store_name) between 2 and 80),
  modelo        text not null default 'outro'
                check (modelo in ('padaria','cafeteria','hamburgueria','pizzaria','restaurante','doceria','outro')),
  descricao     text not null default '' check (length(descricao) <= 300),
  whatsapp      text not null default '' check (whatsapp ~ '^[0-9]{0,13}$'),
  address       text not null default '' check (length(address) <= 200),
  hours         text not null default '' check (length(hours) <= 200),
  instagram     text not null default '' check (length(instagram) <= 120),
  cor           text not null default '#B0703F' check (cor ~ '^#[0-9A-Fa-f]{6}$'),
  logo_url      text not null default '' check (length(logo_url) <= 600),
  capa_url      text not null default '' check (length(capa_url) <= 600),
  delivery_fee  numeric(10,2) not null default 0 check (delivery_fee between 0 and 999),
  min_order     numeric(10,2) not null default 0 check (min_order between 0 and 9999),
  accept_orders boolean not null default true,
  faz_entrega   boolean not null default true,
  faz_retirada  boolean not null default true,
  pagamentos    text[] not null default array['Pix','Cartão','Dinheiro'],
  extra         jsonb not null default '{}'::jsonb,
  status        text not null default 'ativa' check (status in ('ativa','suspensa','cancelada')),
  plano         text not null default 'inicio' references public.planos (id),
  criado_por    uuid references auth.users (id) on delete set null,
  -- de onde veio quem criou a loja (anúncio, Google, Instagram...): só a plataforma lê
  origem        jsonb not null default '{}'::jsonb check (jsonb_typeof(origem) = 'object' and pg_column_size(origem) < 4000),
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
-- quem já rodou uma versão anterior deste arquivo ganha a coluna nova
alter table public.lojas add column if not exists origem jsonb not null default '{}'::jsonb;
-- conteúdo das páginas da loja (Sobre, Galeria, Depoimentos) fica em extra; limita o tamanho
alter table public.lojas drop constraint if exists lojas_extra_tam;
alter table public.lojas add constraint lojas_extra_tam
  check (jsonb_typeof(extra) = 'object' and pg_column_size(extra) < 30000);
-- cartão de volta: cupom da loja para o cliente que veio de outro canal pedir direto (ex.: {"ativo":true,"codigo":"VOLTEI15","pct":15,"minimo":30,"uma_vez":true})
alter table public.lojas add column if not exists cupom jsonb not null default '{}'::jsonb;
create or replace function public.cupom_ok(j jsonb)
returns boolean language sql immutable set search_path = '' as $$
  select jsonb_typeof(j) = 'object' and (j = '{}'::jsonb or (
    coalesce(j ->> 'codigo', '') ~ '^[A-Z0-9]{3,20}$'
    and jsonb_typeof(j -> 'pct') = 'number' and (j ->> 'pct')::numeric between 5 and 30
    and coalesce(jsonb_typeof(j -> 'minimo'), 'number') = 'number' and coalesce((j ->> 'minimo')::numeric, 0) between 0 and 10000
    and coalesce(jsonb_typeof(j -> 'ativo'), 'boolean') = 'boolean'
    and coalesce(jsonb_typeof(j -> 'uma_vez'), 'boolean') = 'boolean'))
$$;
alter table public.lojas drop constraint if exists lojas_cupom_ok;
alter table public.lojas add constraint lojas_cupom_ok check (public.cupom_ok(cupom));

create table if not exists public.membros (
  loja_id   uuid not null references public.lojas (id) on delete cascade,
  user_id   uuid not null references auth.users (id) on delete cascade,
  papel     text not null check (papel in ('dono','gerente','atendente','cozinha')),
  nome      text not null default '',
  email     text not null default '',
  criado_em timestamptz not null default now(),
  primary key (loja_id, user_id)
);
create index if not exists membros_user_idx on public.membros (user_id);

create table if not exists public.convites (
  id        uuid primary key default gen_random_uuid(),
  loja_id   uuid not null references public.lojas (id) on delete cascade,
  email     text not null check (email ~* '^[^@\s]{1,64}@[^@\s]{1,190}\.[^@\s]{2,24}$'),
  papel     text not null check (papel in ('gerente','atendente','cozinha')),
  token     text not null unique,
  criado_por uuid references auth.users (id) on delete set null,
  criado_em timestamptz not null default now(),
  expira_em timestamptz not null default now() + interval '7 days',
  aceito_em timestamptz
);

-- ================= cardápio e pedidos =================
create table if not exists public.categories (
  id       text primary key default gen_random_uuid()::text,
  loja_id  uuid not null references public.lojas (id) on delete cascade,
  name     text not null check (length(name) between 1 and 60),
  position int not null default 0,
  active   boolean not null default true,
  extra    jsonb not null default '{}'::jsonb
);
create index if not exists categories_loja_idx on public.categories (loja_id, position);

create table if not exists public.products (
  id          text primary key default gen_random_uuid()::text,
  loja_id     uuid not null references public.lojas (id) on delete cascade,
  category_id text references public.categories (id) on delete set null,
  name        text not null check (length(name) between 1 and 100),
  description text not null default '' check (length(description) <= 400),
  price       numeric(10,2) not null default 0 check (price between 0 and 99999),
  unit        text not null default '' check (length(unit) <= 40),
  image_url   text not null default '' check (length(image_url) <= 600),
  active      boolean not null default true,
  featured    boolean not null default false,
  badge       text not null default '' check (length(badge) <= 30),
  position    int not null default 0,
  extra       jsonb not null default '{}'::jsonb,
  created_at  timestamptz not null default now()
);
create index if not exists products_loja_idx on public.products (loja_id, position);

-- ================= opcionais dos produtos (ponto da carne, adicionais, tamanho) =================
-- products.opcoes: [{"id","nome","min","max","itens":[{"id","nome","preco"}]}]
create or replace function public.opcoes_ok(j jsonb)
returns boolean language plpgsql immutable set search_path = '' as $$
declare g jsonb; o jsonb; usados text[] := '{}';
begin
  if j is null or jsonb_typeof(j) <> 'array' or jsonb_array_length(j) > 8 then return false; end if;
  for g in select * from jsonb_array_elements(j) loop
    if coalesce(jsonb_typeof(g) <> 'object'
       or jsonb_typeof(g -> 'id') <> 'string' or (g ->> 'id') !~ '^[A-Za-z0-9_-]{1,30}$'
       or jsonb_typeof(g -> 'nome') <> 'string' or length(btrim(g ->> 'nome')) not between 1 and 60
       or jsonb_typeof(g -> 'min') <> 'number' or (g ->> 'min') !~ '^[0-9]{1,2}$'
       or jsonb_typeof(g -> 'max') <> 'number' or (g ->> 'max') !~ '^[0-9]{1,2}$'
       or (g ->> 'min')::int > (g ->> 'max')::int or (g ->> 'max')::int < 1
       or jsonb_typeof(g -> 'itens') <> 'array' or jsonb_array_length(g -> 'itens') not between 1 and 30
       or (g ->> 'id') = any (usados), true) then
      return false;
    end if;
    usados := usados || (g ->> 'id');
    if (g ->> 'min')::int > jsonb_array_length(g -> 'itens') then return false; end if;
    for o in select * from jsonb_array_elements(g -> 'itens') loop
      if coalesce(jsonb_typeof(o) <> 'object'
         or jsonb_typeof(o -> 'id') <> 'string' or (o ->> 'id') !~ '^[A-Za-z0-9_-]{1,30}$'
         or jsonb_typeof(o -> 'nome') <> 'string' or length(btrim(o ->> 'nome')) not between 1 and 60
         or jsonb_typeof(o -> 'preco') <> 'number' or (o ->> 'preco')::numeric not between 0 and 9999, true) then
        return false;
      end if;
    end loop;
  end loop;
  return true;
end $$;

alter table public.products add column if not exists opcoes jsonb not null default '[]'::jsonb;
alter table public.products drop constraint if exists products_opcoes_ok;
alter table public.products add constraint products_opcoes_ok check (public.opcoes_ok(opcoes));

create table if not exists public.orders (
  id             uuid primary key default gen_random_uuid(),
  loja_id        uuid not null references public.lojas (id) on delete cascade,
  seq            int not null,
  code           text not null,
  idem_key       text not null,
  track_token    text not null unique,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now(),
  status         text not null default 'novo'
                 check (status in ('novo','confirmado','em_preparo','pronto','entregue','cancelado')),
  customer_name  text not null,
  customer_phone text not null,
  delivery_type  text not null check (delivery_type in ('retirada','entrega')),
  address        text not null default '',
  scheduled_for  text not null default '',
  notes          text not null default '',
  items          jsonb not null default '[]'::jsonb,
  subtotal       numeric(10,2) not null default 0,
  delivery_fee   numeric(10,2) not null default 0,
  total          numeric(10,2) not null default 0,
  payment_method text not null default '',
  payment_status text not null default 'pendente' check (payment_status in ('pendente','pago','estornado')),
  admin_notes    text not null default '' check (length(admin_notes) <= 2000),
  unique (loja_id, seq),
  unique (loja_id, idem_key)
);
create index if not exists orders_loja_created_idx on public.orders (loja_id, created_at desc);
-- código curto do link de acompanhamento (bistroconnect.com.br/p/<código>): 16 letras e números, sem dados pessoais
alter table public.orders add column if not exists track_code text;
update public.orders set track_code = substr(track_token, 1, 16) where track_code is null or length(track_code) <> 16;
create unique index if not exists orders_track_code_idx on public.orders (track_code);
-- desconto do cartão de volta (cupom) no pedido
alter table public.orders add column if not exists discount numeric(10,2) not null default 0;
alter table public.orders add column if not exists coupon text not null default '';

create table if not exists public.order_events (
  id         bigint generated always as identity primary key,
  order_id   uuid not null references public.orders (id) on delete cascade,
  loja_id    uuid not null references public.lojas (id) on delete cascade,
  at         timestamptz not null default now(),
  actor      text not null default '',
  campo      text not null,
  de         text,
  para       text
);
create index if not exists order_events_order_idx on public.order_events (order_id, id);

-- ================= quem pode o quê =================
-- papel do usuário logado na loja (null = não é da equipe)
create or replace function public.papel_na_loja(p_loja uuid)
returns text language sql stable security definer set search_path = '' as $$
  select m.papel from public.membros m where m.loja_id = p_loja and m.user_id = auth.uid()
$$;

-- atendente e cozinha: basta estar logado. dono e gerente: login em 2 etapas.
create or replace function public.pode(p_loja uuid, p_papeis text[] default array['dono','gerente','atendente','cozinha'])
returns boolean language sql stable security definer set search_path = '' as $$
  select coalesce((
    select m.papel = any (p_papeis)
           and (m.papel not in ('dono','gerente') or coalesce(auth.jwt() ->> 'aal', '') = 'aal2')
      from public.membros m
     where m.loja_id = p_loja and m.user_id = auth.uid()
  ), false) or public.eh_admin_plataforma()
$$;

do $$
declare f text;
begin
  foreach f in array array['eh_admin_plataforma()', 'papel_na_loja(uuid)', 'pode(uuid, text[])'] loop
    execute 'revoke all on function public.' || f || ' from public';
    execute 'grant execute on function public.' || f || ' to anon, authenticated';
  end loop;
end $$;

-- ================= permissões (RLS) =================
do $$
declare t text; p record;
begin
  foreach t in array array['planos','lojas','membros','convites','categories','products','orders','order_events'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('alter table public.%I force row level security', t);
    for p in select policyname from pg_policies where schemaname = 'public' and tablename = t loop
      execute format('drop policy %I on public.%I', p.policyname, t);
    end loop;
    execute format('revoke all on public.%I from anon, authenticated', t);
  end loop;
end $$;

-- planos: todos leem (página de preços)
grant select on public.planos to anon, authenticated;
create policy "publico le" on public.planos for select using (true);

-- lojas: visitante lê só os campos do site, de loja ativa; equipe lê tudo da própria loja
grant select (id, slug, store_name, modelo, descricao, whatsapp, address, hours, instagram, cor, logo_url, capa_url,
              delivery_fee, min_order, accept_orders, faz_entrega, faz_retirada, pagamentos, extra, status)
  on public.lojas to anon;
grant select on public.lojas to authenticated;
grant update (store_name, descricao, whatsapp, address, hours, instagram, cor, logo_url, capa_url,
              delivery_fee, min_order, accept_orders, faz_entrega, faz_retirada, pagamentos, extra, cupom)
  on public.lojas to authenticated;
create policy "publico le ativas" on public.lojas for select to anon using (status = 'ativa');
create policy "equipe le" on public.lojas for select to authenticated
  using (public.papel_na_loja(id) is not null or public.eh_admin_plataforma());
-- pausar pedidos também vale para atendente (balcão lotado); o resto só dono/gerente (ver gatilho lojas_quem_altera)
create policy "equipe altera" on public.lojas for update to authenticated
  using (public.pode(id)) with check (public.pode(id));

-- equipe: cada um vê a equipe das lojas onde está; mudanças só pelas funções
grant select on public.membros to authenticated;
create policy "equipe le" on public.membros for select to authenticated
  using (public.papel_na_loja(loja_id) is not null or public.eh_admin_plataforma());

grant select, delete on public.convites to authenticated;
create policy "dono e gerente leem" on public.convites for select to authenticated
  using (public.pode(loja_id, array['dono','gerente']));
create policy "dono e gerente cancelam" on public.convites for delete to authenticated
  using (public.pode(loja_id, array['dono','gerente']));

-- cardápio: visitante lê o ativo de lojas ativas; dono e gerente alteram
do $$
declare t text;
begin
  foreach t in array array['categories','products'] loop
    execute format('grant select on public.%I to anon, authenticated', t);
    execute format('grant insert, update, delete on public.%I to authenticated', t);
    execute format($p$create policy "publico le" on public.%I for select
      using ((active and exists (select 1 from public.lojas l where l.id = loja_id and l.status = 'ativa'))
             or public.papel_na_loja(loja_id) is not null or public.eh_admin_plataforma())$p$, t);
    execute format($p$create policy "gestao insere" on public.%I for insert to authenticated
      with check (public.pode(loja_id, array['dono','gerente']))$p$, t);
    execute format($p$create policy "gestao altera" on public.%I for update to authenticated
      using (public.pode(loja_id, array['dono','gerente'])) with check (public.pode(loja_id, array['dono','gerente']))$p$, t);
    execute format($p$create policy "gestao apaga" on public.%I for delete to authenticated
      using (public.pode(loja_id, array['dono','gerente']))$p$, t);
  end loop;
end $$;

-- pedidos: a equipe lê e muda só status, pagamento e anotações. Itens e valores ninguém altera.
grant select on public.orders, public.order_events to authenticated;
grant update (status, payment_method, payment_status, admin_notes) on public.orders to authenticated;
create policy "equipe le" on public.orders for select to authenticated using (public.pode(loja_id));
create policy "equipe altera" on public.orders for update to authenticated
  using (public.pode(loja_id)) with check (public.pode(loja_id));
create policy "equipe le" on public.order_events for select to authenticated using (public.pode(loja_id));

-- ================= gatilhos =================
create or replace function public.toca_updated_at()
returns trigger language plpgsql set search_path = '' as $$
begin new.updated_at := now(); return new; end $$;
drop trigger if exists lojas_updated_at on public.lojas;
create trigger lojas_updated_at before update on public.lojas for each row execute function public.toca_updated_at();

-- atendente/cozinha só podem pausar ou reabrir pedidos; o resto da loja é com dono/gerente
create or replace function public.lojas_quem_altera()
returns trigger language plpgsql security definer set search_path = '' as $$
begin
  -- auth.uid() vazio = SQL Editor ou chave service_role (o visitante não tem permissão de UPDATE em lojas)
  if auth.uid() is null or public.eh_admin_plataforma() or public.pode(new.id, array['dono','gerente']) then
    return new;
  end if;
  if (to_jsonb(new) - 'accept_orders' - 'updated_at') is distinct from (to_jsonb(old) - 'accept_orders' - 'updated_at') then
    raise exception 'Só o dono ou o gerente podem mudar os dados da loja.' using errcode = '42501';
  end if;
  return new;
end $$;
drop trigger if exists lojas_quem_altera on public.lojas;
create trigger lojas_quem_altera before update on public.lojas for each row execute function public.lojas_quem_altera();

-- histórico de cada mudança de pedido; cozinha não mexe em pagamento
create or replace function public.pedido_alterado()
returns trigger language plpgsql security definer set search_path = '' as $$
declare quem text := coalesce((select u.email from auth.users u where u.id = auth.uid()), 'sistema');
begin
  if new.payment_status is distinct from old.payment_status or new.payment_method is distinct from old.payment_method then
    if public.papel_na_loja(new.loja_id) = 'cozinha' and not public.eh_admin_plataforma() then
      raise exception 'A cozinha não altera pagamento.' using errcode = '42501';
    end if;
  end if;
  if new.payment_status = 'pago' and old.payment_status <> 'pago' and new.status = 'cancelado' then
    raise exception 'Pedido cancelado não recebe pagamento.' using errcode = 'P0001';
  end if;
  new.updated_at := now();
  if new.status is distinct from old.status then
    insert into public.order_events (order_id, loja_id, actor, campo, de, para) values (new.id, new.loja_id, quem, 'status', old.status, new.status);
  end if;
  if new.payment_status is distinct from old.payment_status or new.payment_method is distinct from old.payment_method then
    insert into public.order_events (order_id, loja_id, actor, campo, de, para)
    values (new.id, new.loja_id, quem, 'pagamento', old.payment_status || ' ' || old.payment_method, new.payment_status || ' ' || new.payment_method);
  end if;
  if new.admin_notes is distinct from old.admin_notes then
    insert into public.order_events (order_id, loja_id, actor, campo) values (new.id, new.loja_id, quem, 'anotacao');
  end if;
  return new;
end $$;
drop trigger if exists pedido_alterado on public.orders;
create trigger pedido_alterado before update on public.orders for each row execute function public.pedido_alterado();

-- produto só pode usar categoria da mesma loja
create or replace function public.produto_confere()
returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if new.category_id is not null and not exists (
       select 1 from public.categories c where c.id = new.category_id and c.loja_id = new.loja_id) then
    raise exception 'Categoria de outra loja.' using errcode = '42501';
  end if;
  return new;
end $$;
drop trigger if exists produto_confere on public.products;
create trigger produto_confere before insert or update on public.products for each row execute function public.produto_confere();

-- ================= erro amigável para a tela =================
create or replace function public.recusa(msg text, dica text default '')
returns void language plpgsql set search_path = '' as $$
begin raise exception '%', msg using errcode = 'P0001', hint = dica; end $$;

-- ================= criar loja (cadastro do empreendedor) =================
drop function if exists public.criar_loja(text, text, text, text);
create or replace function public.criar_loja(p_nome text, p_slug text, p_modelo text, p_whatsapp text, p_origem jsonb default '{}'::jsonb)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare
  v_origem jsonb := '{}'::jsonb;
  eu    uuid := auth.uid();
  meu_email text := coalesce(auth.jwt() ->> 'email', '');
  nova  public.lojas;
  v_slug text := lower(btrim(coalesce(p_slug, '')));
  fone  text := regexp_replace(coalesce(p_whatsapp, ''), '\D', '', 'g');
  cats  text[];
  i     int := 0;
  c     text;
begin
  if eu is null then perform public.recusa('Entre na sua conta para criar a loja.'); end if;
  if length(btrim(coalesce(p_nome, ''))) not between 2 and 80 then perform public.recusa('Informe o nome da loja.'); end if;
  if v_slug !~ '^[a-z0-9](?:[a-z0-9-]{1,38}[a-z0-9])$' then
    perform public.recusa('O endereço da loja usa só letras minúsculas, números e hífen (3 a 40 caracteres).');
  end if;
  if v_slug = any (array['admin','painel','api','www','entrar','loja','lojas','pedido','planos','suporte','ajuda',
                       'bistro','bistroconnect','connect','login','cadastro','conta','app','static','assets']) then
    perform public.recusa('Esse endereço é reservado. Escolha outro.');
  end if;
  if exists (select 1 from public.lojas l where l.slug = v_slug) then
    perform public.recusa('Esse endereço já está em uso. Tente outro.', 'SLUG');
  end if;
  if p_modelo not in ('padaria','cafeteria','hamburgueria','pizzaria','restaurante','doceria','outro') then
    perform public.recusa('Escolha o tipo da loja.');
  end if;
  if length(fone) in (10, 11) then fone := '55' || fone; end if;
  if length(fone) not between 12 and 13 then perform public.recusa('Informe o WhatsApp da loja com DDD.'); end if;
  if (select count(*) from public.membros m where m.user_id = eu and m.papel = 'dono') >= 3 then
    perform public.recusa('Cada conta pode ter até 3 lojas. Fale com o suporte para mais.');
  end if;

  -- origem da campanha: só as chaves conhecidas, cada valor com no máximo 150 caracteres
  if jsonb_typeof(p_origem) = 'object' then
    select coalesce(jsonb_object_agg(e.k, left(e.v, 150)), '{}'::jsonb) into v_origem
      from jsonb_each_text(p_origem) as e(k, v)
     where e.k in ('fonte','meio','campanha','termo','conteudo','gclid','fbclid','referencia','pagina','nicho','quando');
  end if;

  insert into public.lojas (slug, store_name, modelo, whatsapp, criado_por, origem)
  values (v_slug, btrim(p_nome), p_modelo, fone, eu, v_origem) returning * into nova;
  insert into public.membros (loja_id, user_id, papel, email) values (nova.id, eu, 'dono', meu_email);

  cats := case p_modelo
    when 'padaria'      then array['Pães','Bolos','Doces','Salgados','Bebidas']
    when 'cafeteria'    then array['Cafés','Com leite','Gelados','Comidinhas','Doces']
    when 'hamburgueria' then array['Burgers','Combos','Acompanhamentos','Bebidas','Sobremesas']
    when 'pizzaria'     then array['Pizzas salgadas','Pizzas doces','Bebidas']
    when 'restaurante'  then array['Entradas','Pratos principais','Sobremesas','Bebidas']
    when 'doceria'      then array['Bolos','Doces','Tortas','Encomendas']
    else array['Destaques','Cardápio','Bebidas'] end;
  foreach c in array cats loop
    i := i + 1;
    insert into public.categories (loja_id, name, position) values (nova.id, c, i);
  end loop;
  return jsonb_build_object('id', nova.id, 'slug', nova.slug);
end $$;

-- lojas do usuário logado, com o papel dele
create or replace function public.minhas_lojas()
returns table (id uuid, slug text, store_name text, modelo text, papel text, status text)
language sql stable security definer set search_path = '' as $$
  select l.id, l.slug, l.store_name, l.modelo, m.papel, l.status
    from public.membros m join public.lojas l on l.id = m.loja_id
   where m.user_id = auth.uid()
   order by m.criado_em
$$;

-- ================= equipe =================
create or replace function public.convidar_membro(p_loja uuid, p_email text, p_papel text)
returns text language plpgsql security definer set search_path = '' as $$
declare tk text := replace(gen_random_uuid()::text, '-', '') || replace(gen_random_uuid()::text, '-', '');
        quem text := public.papel_na_loja(p_loja);
begin
  if not public.pode(p_loja, array['dono','gerente']) then
    raise exception 'Só o dono ou o gerente convidam pessoas (com login em 2 etapas).' using errcode = '42501';
  end if;
  if p_papel not in ('gerente','atendente','cozinha') then perform public.recusa('Escolha a função da pessoa.'); end if;
  if p_papel = 'gerente' and quem <> 'dono' and not public.eh_admin_plataforma() then
    perform public.recusa('Só o dono convida gerentes.');
  end if;
  if lower(btrim(p_email)) !~ '^[^@\s]{1,64}@[^@\s]{1,190}\.[^@\s]{2,24}$' then perform public.recusa('E-mail inválido.'); end if;
  if (select count(*) from public.membros m where m.loja_id = p_loja) >= 30 then
    perform public.recusa('A equipe chegou ao limite de 30 pessoas.');
  end if;
  delete from public.convites c where c.loja_id = p_loja and c.email = lower(btrim(p_email)) and c.aceito_em is null;
  insert into public.convites (loja_id, email, papel, token, criado_por)
  values (p_loja, lower(btrim(p_email)), p_papel, tk, auth.uid());
  return tk;
end $$;

create or replace function public.aceitar_convite(p_token text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare cv public.convites; meu_email text := lower(coalesce(auth.jwt() ->> 'email', ''));
begin
  if auth.uid() is null then perform public.recusa('Entre na sua conta para aceitar o convite.'); end if;
  select * into cv from public.convites c where c.token = p_token for update;
  if not found or cv.aceito_em is not null or cv.expira_em < now() then
    perform public.recusa('Convite inválido ou vencido. Peça um novo para a loja.');
  end if;
  if cv.email <> meu_email then
    perform public.recusa('Este convite foi enviado para outro e-mail. Entre com o e-mail convidado.');
  end if;
  insert into public.membros (loja_id, user_id, papel, email) values (cv.loja_id, auth.uid(), cv.papel, meu_email)
  on conflict (loja_id, user_id) do update set papel = excluded.papel;
  update public.convites set aceito_em = now() where id = cv.id;
  return jsonb_build_object('loja_id', cv.loja_id, 'papel', cv.papel);
end $$;

create or replace function public.mudar_membro(p_loja uuid, p_user uuid, p_papel text)
returns void language plpgsql security definer set search_path = '' as $$
begin
  if not public.pode(p_loja, array['dono']) then
    raise exception 'Só o dono muda a equipe (com login em 2 etapas).' using errcode = '42501';
  end if;
  if p_papel is not null and p_papel not in ('dono','gerente','atendente','cozinha') then
    perform public.recusa('Função inválida.');
  end if;
  if (select papel from public.membros where loja_id = p_loja and user_id = p_user) = 'dono'
     and (p_papel is null or p_papel <> 'dono')
     and (select count(*) from public.membros where loja_id = p_loja and papel = 'dono') <= 1 then
    perform public.recusa('A loja precisa de pelo menos um dono.');
  end if;
  if p_papel is null then
    delete from public.membros where loja_id = p_loja and user_id = p_user;
  else
    update public.membros set papel = p_papel where loja_id = p_loja and user_id = p_user;
  end if;
end $$;

-- ================= pedido feito pelo site =================
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
begin
  select * into loja from public.lojas l where l.slug = lower(coalesce(p_slug, ''));
  if not found or loja.status <> 'ativa' then perform public.recusa('Loja não encontrada.'); end if;
  if coalesce(p_idem, '') !~ '^[A-Za-z0-9_-]{8,80}$' then perform public.recusa('Pedido inválido. Atualize a página.'); end if;

  select * into ja from public.orders o where o.loja_id = loja.id and o.idem_key = p_idem;
  if found then
    return jsonb_build_object('code', ja.code, 'track_token', ja.track_token, 'track_code', ja.track_code, 'total', ja.total,
                              'subtotal', ja.subtotal, 'delivery_fee', ja.delivery_fee, 'discount', ja.discount, 'coupon', ja.coupon, 'items', ja.items);
  end if;

  if not loja.accept_orders then
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

  if (select count(*) from public.orders o where o.loja_id = loja.id and o.created_at > now() - interval '10 minutes'
        and regexp_replace(o.customer_phone, '\D', '', 'g') = digs) >= 5
     or (select count(*) from public.orders o where o.loja_id = loja.id and o.created_at > now() - interval '10 minutes') >= 120 then
    perform public.recusa('Muitos pedidos seguidos. Fale com a loja no WhatsApp.');
  end if;

  perform pg_advisory_xact_lock(hashtext('pedido:' || loja.id::text));
  select coalesce(max(o.seq), 0) + 1 into proximo from public.orders o where o.loja_id = loja.id;

  loop
    codigo := substr(replace(gen_random_uuid()::text, '-', ''), 1, 16);
    exit when not exists (select 1 from public.orders o where o.track_code = codigo);
  end loop;
  insert into public.orders (loja_id, seq, code, idem_key, track_token, track_code, customer_name, customer_phone, delivery_type,
                             address, scheduled_for, notes, items, subtotal, delivery_fee, total, payment_method, discount, coupon)
  values (loja.id, proximo, '#' || proximo::text, p_idem,
          replace(gen_random_uuid()::text, '-', '') || replace(gen_random_uuid()::text, '-', ''), codigo,
          nome, fone, tipo, ender, quando, obs, itens, soma, taxa, total, forma, descon, case when descon > 0 then cup else '' end)
  returning * into novo;
  insert into public.order_events (order_id, loja_id, actor, campo, para) values (novo.id, loja.id, 'cliente', 'status', 'novo');

  return jsonb_build_object('code', novo.code, 'track_token', novo.track_token, 'track_code', novo.track_code, 'total', novo.total,
                            'subtotal', novo.subtotal, 'delivery_fee', novo.delivery_fee, 'discount', novo.discount, 'coupon', novo.coupon, 'items', novo.items);
end $$;

-- ================= rastreio do pedido =================
create or replace function public.rastrear_pedido(p_token text)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare o public.orders; l public.lojas;
begin
  if coalesce(p_token, '') !~ '^([a-f0-9]{16}|[a-f0-9]{32,64})$' then return null; end if;
  select * into o from public.orders where track_token = p_token or track_code = p_token;
  if not found then return null; end if;
  select * into l from public.lojas where id = o.loja_id;
  return jsonb_build_object(
    'code', o.code, 'status', o.status, 'delivery_type', o.delivery_type, 'scheduled_for', o.scheduled_for,
    'created_at', o.created_at, 'updated_at', o.updated_at, 'first_name', split_part(o.customer_name, ' ', 1),
    'items', (select coalesce(jsonb_agg(jsonb_build_object('name', i ->> 'name', 'unit', coalesce(i ->> 'unit', ''),
                                         'qty', (i ->> 'qty')::int, 'price', (i ->> 'price')::numeric,
                                         'options', (select coalesce(jsonb_agg(x ->> 'name'), '[]'::jsonb)
                                                       from jsonb_array_elements(coalesce(i -> 'options', '[]'::jsonb)) x))), '[]'::jsonb)
                from jsonb_array_elements(o.items) i),
    'subtotal', o.subtotal, 'delivery_fee', o.delivery_fee, 'discount', o.discount, 'coupon', o.coupon, 'total', o.total,
    'payment_method', o.payment_method, 'payment_status', o.payment_status,
    'history', (select coalesce(jsonb_agg(jsonb_build_object('status', e.para, 'at', e.at) order by e.id), '[]'::jsonb)
                  from public.order_events e where e.order_id = o.id and e.campo = 'status'),
    'store_name', l.store_name, 'whatsapp', l.whatsapp, 'slug', l.slug, 'cor', l.cor);
end $$;

-- ================= cupom do cartão de volta: o cardápio confere antes de enviar (não revela o código) =================
create or replace function public.confere_cupom(p_slug text, p_code text)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare l public.lojas;
begin
  select * into l from public.lojas x where x.slug = lower(coalesce(p_slug, '')) and x.status = 'ativa';
  if not found or not coalesce((l.cupom ->> 'ativo')::boolean, false)
     or upper(btrim(coalesce(p_code, ''))) is distinct from (l.cupom ->> 'codigo') then
    return jsonb_build_object('ok', false);
  end if;
  return jsonb_build_object('ok', true, 'pct', (l.cupom ->> 'pct')::numeric, 'minimo', coalesce((l.cupom ->> 'minimo')::numeric, 0));
end $$;

-- ================= cartão do pedido (imagem que o cliente compartilha com a loja) =================
-- Devolve também nome, telefone e endereço do cliente: só com o código do pedido (16 letras e números ou o código longo).
create or replace function public.cartao_pedido(p_code text)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare o public.orders; l public.lojas;
begin
  if coalesce(p_code, '') !~ '^([a-f0-9]{16}|[a-f0-9]{32,64})$' then return null; end if;
  select * into o from public.orders where track_token = p_code or track_code = p_code;
  if not found then return null; end if;
  select * into l from public.lojas where id = o.loja_id;
  return jsonb_build_object(
    'code', o.code, 'status', o.status, 'delivery_type', o.delivery_type, 'scheduled_for', o.scheduled_for,
    'created_at', o.created_at, 'updated_at', o.updated_at, 'first_name', split_part(o.customer_name, ' ', 1), 'customer_name', o.customer_name, 'customer_phone', o.customer_phone,
    'address', o.address, 'payment_method', o.payment_method, 'payment_status', o.payment_status, 'notes', o.notes,
    'history', (select coalesce(jsonb_agg(jsonb_build_object('status', e.para, 'at', e.at) order by e.id), '[]'::jsonb)
                  from public.order_events e where e.order_id = o.id and e.campo = 'status'),
    'items', (select coalesce(jsonb_agg(jsonb_build_object('name', i ->> 'name', 'unit', coalesce(i ->> 'unit', ''),
                                         'qty', (i ->> 'qty')::int, 'price', (i ->> 'price')::numeric,
                                         'options', (select coalesce(jsonb_agg(x ->> 'name'), '[]'::jsonb)
                                                       from jsonb_array_elements(coalesce(i -> 'options', '[]'::jsonb)) x),
                                         'image_url', coalesce((select pr.image_url from public.products pr where pr.id = i ->> 'product_id'), ''))),
                                  '[]'::jsonb)
                from jsonb_array_elements(o.items) i),
    'subtotal', o.subtotal, 'delivery_fee', o.delivery_fee, 'discount', o.discount, 'coupon', o.coupon, 'total', o.total,
    'store_name', l.store_name, 'whatsapp', l.whatsapp, 'slug', l.slug, 'logo_url', l.logo_url, 'capa_url', l.capa_url, 'modelo', l.modelo, 'cor', l.cor);
end $$;

-- ================= faturamento e plano =================
-- vendido no mês (pedidos não cancelados) e o plano que essa faixa indica
create or replace function public.faturamento_loja(p_loja uuid, p_mes date default (now() at time zone 'America/Sao_Paulo')::date)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare ini timestamptz; fim timestamptz; vendido numeric; pl public.planos;
begin
  if not public.pode(p_loja) then raise exception 'Sem permissão.' using errcode = '42501'; end if;
  ini := (date_trunc('month', p_mes::timestamp) at time zone 'America/Sao_Paulo');
  fim := ((date_trunc('month', p_mes::timestamp) + interval '1 month') at time zone 'America/Sao_Paulo');
  select coalesce(sum(o.total), 0) into vendido from public.orders o
   where o.loja_id = p_loja and o.status <> 'cancelado' and o.created_at >= ini and o.created_at < fim;
  select * into pl from public.planos p where p.ate_valor is null or vendido <= p.ate_valor order by p.ordem limit 1;
  return jsonb_build_object('vendido', vendido, 'plano', pl.id, 'plano_nome', pl.nome, 'mensalidade', pl.mensalidade,
                            'ate_valor', pl.ate_valor);
end $$;

-- painel da plataforma (só você): lojas, vendas do mês e plano
drop function if exists public.admin_lojas();
drop function if exists public.admin_lojas(date);
create or replace function public.admin_lojas(p_mes date default (now() at time zone 'America/Sao_Paulo')::date)
returns table (id uuid, slug text, store_name text, modelo text, status text, criada timestamptz,
               dono text, pedidos_mes bigint, vendido_mes numeric, plano text, mensalidade numeric, origem jsonb)
language plpgsql stable security definer set search_path = '' as $$
begin
  if not public.eh_admin_plataforma() then raise exception 'Sem permissão.' using errcode = '42501'; end if;
  return query
  with mes as (
    select o.loja_id, count(*) n, sum(o.total) v from public.orders o
     where o.status <> 'cancelado'
       and o.created_at >= (date_trunc('month', p_mes::timestamp) at time zone 'America/Sao_Paulo')
       and o.created_at <  ((date_trunc('month', p_mes::timestamp) + interval '1 month') at time zone 'America/Sao_Paulo')
     group by o.loja_id)
  select l.id, l.slug, l.store_name, l.modelo, l.status, l.created_at,
         (select m.email from public.membros m where m.loja_id = l.id and m.papel = 'dono' order by m.criado_em limit 1),
         coalesce(mes.n, 0), coalesce(mes.v, 0),
         pl.nome, pl.mensalidade, l.origem
    from public.lojas l
    left join mes on mes.loja_id = l.id
    left join lateral (select * from public.planos p where p.ate_valor is null or coalesce(mes.v, 0) <= p.ate_valor
                        order by p.ordem limit 1) pl on true
   order by l.created_at desc;
end $$;

create or replace function public.admin_status_loja(p_loja uuid, p_status text)
returns void language plpgsql security definer set search_path = '' as $$
begin
  if not public.eh_admin_plataforma() then raise exception 'Sem permissão.' using errcode = '42501'; end if;
  if p_status not in ('ativa','suspensa','cancelada') then perform public.recusa('Status inválido.'); end if;
  update public.lojas set status = p_status where id = p_loja;
end $$;

do $$
declare f text;
begin
  foreach f in array array['criar_loja(text, text, text, text, jsonb)', 'minhas_lojas()', 'convidar_membro(uuid, text, text)',
                           'aceitar_convite(text)', 'mudar_membro(uuid, uuid, text)', 'faturamento_loja(uuid, date)',
                           'admin_lojas(date)', 'admin_status_loja(uuid, text)'] loop
    execute 'revoke all on function public.' || f || ' from public';
    execute 'grant execute on function public.' || f || ' to authenticated';
  end loop;
  foreach f in array array['create_order(text, text, jsonb)', 'rastrear_pedido(text)', 'cartao_pedido(text)', 'confere_cupom(text, text)'] loop
    execute 'revoke all on function public.' || f || ' from public';
    execute 'grant execute on function public.' || f || ' to anon, authenticated';
  end loop;
  foreach f in array array['recusa(text, text)', 'toca_updated_at()', 'lojas_quem_altera()', 'pedido_alterado()', 'produto_confere()'] loop
    execute 'revoke all on function public.' || f || ' from public';
  end loop;
end $$;

-- ================= fotos (bucket "lojas", uma pasta por loja) =================
do $$
declare p record;
begin
  if to_regclass('storage.buckets') is null then return; end if;
  insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
  values ('lojas', 'lojas', true, 5242880, array['image/jpeg','image/png','image/webp'])
  on conflict (id) do nothing;
  for p in select policyname from pg_policies where schemaname = 'storage' and tablename = 'objects'
           and policyname like 'lojas: %' loop
    execute format('drop policy %I on storage.objects', p.policyname);
  end loop;
  create policy "lojas: publico le" on storage.objects for select using (bucket_id = 'lojas');
  create policy "lojas: gestao envia" on storage.objects for insert to authenticated
    with check (bucket_id = 'lojas' and public.pode(((storage.foldername(name))[1])::uuid, array['dono','gerente']));
  create policy "lojas: gestao altera" on storage.objects for update to authenticated
    using (bucket_id = 'lojas' and public.pode(((storage.foldername(name))[1])::uuid, array['dono','gerente']));
  create policy "lojas: gestao apaga" on storage.objects for delete to authenticated
    using (bucket_id = 'lojas' and public.pode(((storage.foldername(name))[1])::uuid, array['dono','gerente']));
end $$;

-- ================= painel atualiza sozinho =================
do $$
declare t text;
begin
  if exists (select 1 from pg_publication where pubname = 'supabase_realtime') then
    foreach t in array array['orders', 'products', 'categories', 'lojas'] loop
      if not exists (select 1 from pg_publication_tables where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = t) then
        execute format('alter publication supabase_realtime add table public.%I', t);
      end if;
    end loop;
  end if;
end $$;

-- ================= WhatsApp oficial no painel (Cloud API da Meta) =================
-- As mensagens que chegam no número da loja entram no painel (aba Atendimento) e a equipe responde por lá.
-- Quem recebe da Meta é a função whats-webhook; quem envia é a whats-enviar (pasta functions/).
-- O token da Meta fica em whats_segredos, que ninguém lê pelo navegador (só as funções, com a chave de serviço).

create table if not exists public.whats_contas (
  loja_id         uuid primary key references public.lojas (id) on delete cascade,
  phone_number_id text not null unique check (phone_number_id ~ '^[0-9]{5,30}$'),
  numero          text not null default '' check (numero ~ '^[0-9]{0,15}$'),
  ativo           boolean not null default true,
  robo            boolean not null default true,
  criado_em       timestamptz not null default now()
);

create table if not exists public.whats_segredos (
  loja_id uuid primary key references public.lojas (id) on delete cascade,
  token   text not null default ''
);

create table if not exists public.whats_conversas (
  id         bigint generated always as identity primary key,
  loja_id    uuid not null references public.lojas (id) on delete cascade,
  wa_id      text not null check (wa_id ~ '^[0-9]{6,20}$'),
  nome       text not null default '',
  ultima_msg text not null default '',
  ultima_em  timestamptz not null default now(),
  nao_lidas  int not null default 0,
  janela_ate timestamptz,
  modo       text not null default 'robo' check (modo in ('robo','humano')),
  unique (loja_id, wa_id)
);
create index if not exists whats_conversas_loja_idx on public.whats_conversas (loja_id, ultima_em desc);

create table if not exists public.whats_mensagens (
  id          bigint generated always as identity primary key,
  conversa_id bigint not null references public.whats_conversas (id) on delete cascade,
  loja_id     uuid not null references public.lojas (id) on delete cascade,
  direcao     text not null check (direcao in ('in','out')),
  tipo        text not null default 'text',
  texto       text not null default '' check (length(texto) <= 4096),
  midia_id    text not null default '',
  wamid       text unique,
  status      text not null default '',
  autor       text not null default '',
  criado_em   timestamptz not null default now()
);
create index if not exists whats_mensagens_conversa_idx on public.whats_mensagens (conversa_id, id);

do $$
declare t text; p record;
begin
  foreach t in array array['whats_contas','whats_segredos','whats_conversas','whats_mensagens'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('alter table public.%I force row level security', t);
    for p in select policyname from pg_policies where schemaname = 'public' and tablename = t loop
      execute format('drop policy %I on public.%I', p.policyname, t);
    end loop;
    execute format('revoke all on public.%I from anon, authenticated', t);
  end loop;
end $$;

-- dono, gerente e atendente leem as conversas da própria loja; mudanças só pelas funções abaixo
grant select on public.whats_contas, public.whats_conversas, public.whats_mensagens to authenticated;
create policy "atendimento le" on public.whats_contas for select to authenticated
  using (public.pode(loja_id, array['dono','gerente','atendente']));
create policy "atendimento le" on public.whats_conversas for select to authenticated
  using (public.pode(loja_id, array['dono','gerente','atendente']));
create policy "atendimento le" on public.whats_mensagens for select to authenticated
  using (public.pode(loja_id, array['dono','gerente','atendente']));
-- whats_segredos: nenhuma permissão para anon/authenticated (só a chave de serviço das funções)

-- ---------- usadas pelo painel ----------
create or replace function public.whats_lida(p_conversa bigint)
returns void language plpgsql security definer set search_path = '' as $$
begin
  update public.whats_conversas c set nao_lidas = 0
   where c.id = p_conversa and public.pode(c.loja_id, array['dono','gerente','atendente']);
end $$;

create or replace function public.whats_modo(p_conversa bigint, p_modo text)
returns void language plpgsql security definer set search_path = '' as $$
begin
  if p_modo not in ('robo','humano') then raise exception 'Modo inválido.' using errcode = 'P0001'; end if;
  update public.whats_conversas c set modo = p_modo
   where c.id = p_conversa and public.pode(c.loja_id, array['dono','gerente','atendente']);
  if not found then raise exception 'Sem permissão.' using errcode = '42501'; end if;
end $$;

-- robô da loja ligado/desligado (vale para todas as conversas)
create or replace function public.whats_robo(p_loja uuid, p_ligado boolean)
returns void language plpgsql security definer set search_path = '' as $$
begin
  if not public.pode(p_loja, array['dono','gerente']) then raise exception 'Sem permissão.' using errcode = '42501'; end if;
  update public.whats_contas set robo = coalesce(p_ligado, true) where loja_id = p_loja;
end $$;

-- a equipe responde: grava a mensagem como "enviando" e devolve o que a função whats-enviar precisa para mandar
create or replace function public.whats_responder(p_conversa bigint, p_texto text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare c public.whats_conversas; ct public.whats_contas; txt text := btrim(coalesce(p_texto, '')); quem text; mid bigint;
begin
  select * into c from public.whats_conversas where id = p_conversa;
  if c.id is null or not public.pode(c.loja_id, array['dono','gerente','atendente']) then
    raise exception 'Sem permissão.' using errcode = '42501';
  end if;
  if txt = '' or length(txt) > 4096 then raise exception 'Escreva a mensagem (até 4096 letras).' using errcode = 'P0001'; end if;
  select * into ct from public.whats_contas where loja_id = c.loja_id and ativo;
  if ct.loja_id is null then raise exception 'O WhatsApp desta loja não está conectado.' using errcode = 'P0001'; end if;
  if c.janela_ate is null or c.janela_ate < now() then
    raise exception 'Passaram 24 horas desde a última mensagem do cliente. O WhatsApp só libera a resposta depois que ele escrever de novo.'
      using errcode = 'P0001', hint = 'JANELA';
  end if;
  select coalesce(nullif(split_part(u.raw_user_meta_data ->> 'nome', ' ', 1), ''), split_part(u.email, '@', 1), 'equipe')
    into quem from auth.users u where u.id = auth.uid();
  insert into public.whats_mensagens (conversa_id, loja_id, direcao, tipo, texto, status, autor)
       values (c.id, c.loja_id, 'out', 'text', txt, 'enviando', coalesce(quem, 'equipe')) returning id into mid;
  update public.whats_conversas set ultima_msg = txt, ultima_em = now(), nao_lidas = 0, modo = 'humano' where id = c.id;
  return jsonb_build_object('id', mid, 'loja_id', c.loja_id, 'wa_id', c.wa_id, 'phone_number_id', ct.phone_number_id);
end $$;

-- a equipe pede para ver uma foto/áudio: confere a permissão e devolve o id da mídia na Meta
create or replace function public.whats_midia(p_mensagem bigint)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare m public.whats_mensagens;
begin
  select * into m from public.whats_mensagens where id = p_mensagem;
  if m.id is null or m.midia_id = '' or not public.pode(m.loja_id, array['dono','gerente','atendente']) then
    raise exception 'Sem permissão.' using errcode = '42501';
  end if;
  return jsonb_build_object('loja_id', m.loja_id, 'midia_id', m.midia_id, 'tipo', m.tipo);
end $$;

-- administrador da plataforma liga o número oficial de uma loja (dados do app da Meta)
create or replace function public.liga_whats(p_loja uuid, p_phone_number_id text, p_numero text, p_token text default null)
returns void language plpgsql security definer set search_path = '' as $$
begin
  if not public.eh_admin_plataforma() then raise exception 'Sem permissão.' using errcode = '42501'; end if;
  insert into public.whats_contas (loja_id, phone_number_id, numero)
       values (p_loja, btrim(p_phone_number_id), regexp_replace(coalesce(p_numero, ''), '\D', '', 'g'))
  on conflict (loja_id) do update set phone_number_id = excluded.phone_number_id, numero = excluded.numero, ativo = true;
  if nullif(btrim(coalesce(p_token, '')), '') is not null then
    insert into public.whats_segredos (loja_id, token) values (p_loja, btrim(p_token))
    on conflict (loja_id) do update set token = excluded.token;
  end if;
end $$;

-- ---------- usadas só pelas funções (chave de serviço) ----------
-- mesma pessoa: DDD + 8 últimos dígitos (o WhatsApp às vezes manda o celular sem o 9)
create or replace function public.whats_chave_fone(p text)
returns text language sql immutable set search_path = '' as $$
  select case when length(d) >= 10 then left(d, 2) || right(d, 8) else d end
    from (select regexp_replace(regexp_replace(coalesce(p, ''), '\D', '', 'g'), '^55(?=\d{10,11}$)', '') d) x
$$;

-- chegou mensagem: guarda, abre a janela de 24h e devolve o que o robô precisa para responder
create or replace function public.whats_recebe(p_phone_number_id text, p_wa_id text, p_nome text, p_wamid text,
                                               p_tipo text, p_texto text, p_midia text default '', p_quando timestamptz default now())
returns jsonb language plpgsql security definer set search_path = '' as $$
declare ct public.whats_contas; c public.whats_conversas; l public.lojas; o public.orders; nova boolean := false; volta boolean := false;
        resumo text; tok text;
begin
  select * into ct from public.whats_contas where phone_number_id = p_phone_number_id and ativo;
  if ct.loja_id is null then return jsonb_build_object('ok', false, 'motivo', 'numero_desconhecido'); end if;
  if p_wamid is not null and exists (select 1 from public.whats_mensagens where wamid = p_wamid) then
    return jsonb_build_object('ok', false, 'motivo', 'repetida');
  end if;
  resumo := left(coalesce(nullif(btrim(p_texto), ''), case p_tipo when 'image' then '📷 Foto' when 'audio' then '🎤 Áudio'
              when 'video' then '🎬 Vídeo' when 'document' then '📄 Documento' when 'sticker' then 'Figurinha'
              when 'location' then '📍 Localização' else 'Mensagem' end), 300);
  select * into c from public.whats_conversas where loja_id = ct.loja_id and wa_id = p_wa_id;
  if c.id is null then
    nova := true;
    insert into public.whats_conversas (loja_id, wa_id, nome, ultima_msg, ultima_em, nao_lidas, janela_ate)
         values (ct.loja_id, p_wa_id, left(coalesce(p_nome, ''), 80), resumo, now(), 1, p_quando + interval '24 hours')
    returning * into c;
  else
    volta := c.ultima_em < now() - interval '12 hours';
    update public.whats_conversas set nome = coalesce(nullif(left(btrim(coalesce(p_nome, '')), 80), ''), nome), ultima_msg = resumo,
           ultima_em = now(), nao_lidas = nao_lidas + 1, janela_ate = greatest(coalesce(janela_ate, p_quando), p_quando + interval '24 hours'),
           -- depois de um dia parado, o robô volta a responder a conversa
           modo = case when volta then 'robo' else modo end
     where id = c.id returning * into c;
  end if;
  insert into public.whats_mensagens (conversa_id, loja_id, direcao, tipo, texto, midia_id, wamid, criado_em)
       values (c.id, ct.loja_id, 'in', left(coalesce(p_tipo, 'text'), 20), left(coalesce(p_texto, ''), 4096), coalesce(p_midia, ''), p_wamid, now());
  select * into l from public.lojas where id = ct.loja_id;
  select * into o from public.orders
   where loja_id = ct.loja_id and created_at > now() - interval '3 days'
     and public.whats_chave_fone(customer_phone) = public.whats_chave_fone(p_wa_id)
   order by created_at desc limit 1;
  select token into tok from public.whats_segredos where loja_id = ct.loja_id;
  return jsonb_build_object('ok', true, 'nova', nova or volta, 'conversa_id', c.id, 'loja_id', ct.loja_id, 'wa_id', c.wa_id,
    'phone_number_id', ct.phone_number_id, 'token', coalesce(tok, ''), 'responde', ct.robo and c.modo = 'robo',
    'loja', jsonb_build_object('nome', l.store_name, 'slug', l.slug, 'horario', l.hours, 'endereco', l.address,
      'taxa', l.delivery_fee, 'minimo', l.min_order, 'aberta', l.accept_orders and l.status = 'ativa',
      'entrega', l.faz_entrega, 'retirada', l.faz_retirada, 'pagamentos', to_jsonb(l.pagamentos)),
    'pedido', case when o.id is null then null else jsonb_build_object('code', o.code, 'status', o.status,
      'tipo', o.delivery_type, 'track_code', o.track_code, 'total', o.total, 'pago', o.payment_status = 'pago') end);
end $$;

-- o robô (ou a função de envio) registra o que foi mandado
create or replace function public.whats_saida(p_conversa bigint, p_texto text, p_wamid text, p_autor text, p_status text default 'sent', p_modo text default null)
returns void language plpgsql security definer set search_path = '' as $$
declare c public.whats_conversas;
begin
  select * into c from public.whats_conversas where id = p_conversa;
  if c.id is null then return; end if;
  insert into public.whats_mensagens (conversa_id, loja_id, direcao, tipo, texto, wamid, status, autor)
       values (c.id, c.loja_id, 'out', 'text', left(coalesce(p_texto, ''), 4096), nullif(p_wamid, ''), coalesce(p_status, ''), coalesce(p_autor, ''));
  update public.whats_conversas set ultima_msg = left(coalesce(p_texto, ''), 300), ultima_em = now(),
         modo = coalesce(p_modo, modo) where id = c.id;
end $$;

-- resultado do envio da equipe (whats-enviar)
create or replace function public.whats_enviada(p_mensagem bigint, p_wamid text, p_status text)
returns void language sql security definer set search_path = '' as $$
  update public.whats_mensagens set wamid = coalesce(nullif(p_wamid, ''), wamid), status = p_status where id = p_mensagem
$$;

-- a Meta avisa: enviada, entregue, lida, falhou
create or replace function public.whats_status(p_wamid text, p_status text)
returns void language sql security definer set search_path = '' as $$
  update public.whats_mensagens set status = p_status
   where wamid = p_wamid and direcao = 'out'
     and coalesce(array_position(array['enviando','sent','delivered','read'], status), 0)
         < coalesce(array_position(array['enviando','sent','delivered','read'], p_status), 99)
$$;

-- token da Meta da loja (vazio = usa o token geral da plataforma)
create or replace function public.whats_token(p_loja uuid)
returns text language sql stable security definer set search_path = '' as $$
  select coalesce((select token from public.whats_segredos where loja_id = p_loja), '')
$$;

do $$
declare f text;
begin
  foreach f in array array['whats_lida(bigint)', 'whats_modo(bigint, text)', 'whats_robo(uuid, boolean)',
                           'whats_responder(bigint, text)', 'whats_midia(bigint)', 'liga_whats(uuid, text, text, text)'] loop
    execute format('revoke all on function public.%s from public, anon', f);
    execute format('grant execute on function public.%s to authenticated', f);
  end loop;
  foreach f in array array['whats_chave_fone(text)', 'whats_recebe(text, text, text, text, text, text, text, timestamptz)',
                           'whats_saida(bigint, text, text, text, text, text)', 'whats_enviada(bigint, text, text)',
                           'whats_status(text, text)', 'whats_token(uuid)'] loop
    execute format('revoke all on function public.%s from public, anon, authenticated', f);
    execute format('grant execute on function public.%s to service_role', f);
  end loop;
end $$;

-- painel atualiza sozinho quando chega mensagem
do $$
declare t text;
begin
  if exists (select 1 from pg_publication where pubname = 'supabase_realtime') then
    foreach t in array array['whats_conversas', 'whats_mensagens'] loop
      if not exists (select 1 from pg_publication_tables where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = t) then
        execute format('alter publication supabase_realtime add table public.%I', t);
      end if;
    end loop;
  end if;
end $$;

-- Depois de criar a SUA conta (Authentication > Users), torne-se administrador da plataforma:
-- insert into public.plataforma_admins (user_id) select id from auth.users where email = 'seu-email@exemplo.com';
