-- eBistrô · 02: tabela de leads do site oficial (formulário e chat da Bia)
-- Rode depois do 01-admins.sql.
--
-- O que este arquivo garante:
--   * visitante (chave anon) só CRIA lead; não lê, não altera, não apaga;
--   * cada lead tem tamanho e formato conferidos no banco, não só no navegador;
--   * limite de envios contra robôs: 30 leads a cada 10 minutos no total
--     e 3 por WhatsApp por dia;
--   * só administradores (tabela admins) veem e mexem nos leads.
--
-- ATENÇÃO: o bloco "remove políticas antigas" apaga as políticas que existirem
-- hoje na tabela leads e põe estas no lugar. Se o painel parar de listar os
-- leads, confira se o seu usuário está na tabela admins (fim do 01-admins.sql).

create table if not exists public.leads (
  id         bigint generated always as identity primary key,
  doc        jsonb not null,
  created_at timestamptz not null default now()
);
alter table public.leads add column if not exists created_at timestamptz not null default now();
create index if not exists leads_created_at_idx on public.leads (created_at);

alter table public.leads enable row level security;
alter table public.leads force row level security;

-- remove políticas antigas
do $$
declare p record;
begin
  for p in select policyname from pg_policies where schemaname = 'public' and tablename = 'leads' loop
    execute format('drop policy %I on public.leads', p.policyname);
  end loop;
end $$;

revoke all on public.leads from anon, authenticated;
grant insert (doc) on public.leads to anon;
grant select, insert, update, delete on public.leads to authenticated;

-- se o id da tabela usar sequência (serial), o visitante precisa dela para inserir
do $$
declare s text := pg_get_serial_sequence('public.leads', 'id');
begin
  if s is not null then execute format('grant usage on sequence %s to anon', s); end if;
exception when others then null;
end $$;

create policy "visitante cria lead valido" on public.leads
  for insert to anon
  with check (
    jsonb_typeof(doc) = 'object'
    and pg_column_size(doc) < 4000
    and doc ->> 'stage' = 'lead'
    and length(coalesce(doc ->> 'nome', '')) between 1 and 100
    and length(coalesce(doc ->> 'responsavel', '')) <= 80
    and regexp_replace(coalesce(doc ->> 'whatsapp', ''), '\D', '', 'g') ~ '^\d{10,13}$'
  );

create policy "admin gerencia leads" on public.leads
  for all to authenticated
  using (public.eh_admin())
  with check (public.eh_admin());

-- limite de envios (roda no banco, o navegador não consegue pular)
create or replace function public.leads_limite()
returns trigger
language plpgsql security definer
set search_path = ''
as $$
declare
  fone text := regexp_replace(coalesce(new.doc ->> 'whatsapp', ''), '\D', '', 'g');
begin
  if public.eh_admin() then
    return new;
  end if;
  new.created_at := now();
  if (select count(*) from public.leads where created_at > now() - interval '10 minutes') >= 30 then
    raise exception 'Muitos envios agora. Tente de novo em alguns minutos.' using errcode = 'P0001';
  end if;
  if (select count(*) from public.leads
       where created_at > now() - interval '1 day'
         and regexp_replace(coalesce(doc ->> 'whatsapp', ''), '\D', '', 'g') = fone) >= 3 then
    raise exception 'Já recebemos seu contato. Vamos te chamar no WhatsApp.' using errcode = 'P0001';
  end if;
  return new;
end $$;
revoke all on function public.leads_limite() from public;

drop trigger if exists leads_limite on public.leads;
create trigger leads_limite before insert on public.leads
  for each row execute function public.leads_limite();
