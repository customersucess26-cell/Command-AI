-- Bistrô Connect · 03: CRM dentro do banco da plataforma (leads, orçamentos e metas)
-- Rode no SQL Editor do projeto "plataforma", depois do 01 (e do 02). Pode rodar mais de uma vez.
--
-- O que garante:
--   * visitante (chave anon) só CRIA lead, pelo formulário "Quero ajuda para montar" e pela Bia;
--     não lê, não altera, não apaga;
--   * cada lead tem tamanho e formato conferidos no banco;
--   * limite contra robôs: 30 leads a cada 10 minutos no total e 3 por WhatsApp por dia;
--   * só quem está em plataforma_admins, logado com 2 etapas (aal2), vê e mexe em leads, orçamentos e metas.
-- Este é o mesmo painel /crm/ que antes ficava ligado ao projeto do site oficial.

create table if not exists public.leads (
  id         bigint generated always as identity primary key,
  doc        jsonb not null,
  created_at timestamptz not null default now()
);
create table if not exists public.orcamentos (
  id         bigint generated always as identity primary key,
  doc        jsonb not null,
  created_at timestamptz not null default now()
);
create table if not exists public.config (
  id         text primary key,
  doc        jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
create index if not exists leads_created_at_idx on public.leads (created_at);

do $$
declare t text; p record;
begin
  foreach t in array array['leads', 'orcamentos', 'config'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('alter table public.%I force row level security', t);
    for p in select policyname from pg_policies where schemaname = 'public' and tablename = t loop
      execute format('drop policy %I on public.%I', p.policyname, t);
    end loop;
    execute format('revoke all on public.%I from anon, authenticated', t);
    execute format('grant select, insert, update, delete on public.%I to authenticated', t);
    execute format($f$create policy "admin da plataforma" on public.%I for all to authenticated
      using (public.eh_admin_plataforma())
      with check (public.eh_admin_plataforma() and pg_column_size(doc) < 200000)$f$, t);
  end loop;
end $$;

-- visitante só cria lead
grant insert (doc) on public.leads to anon;
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

-- limite de envios (roda no banco, o navegador não consegue pular).
-- Admin logado e o SQL Editor (para importar leads antigos) não sofrem o limite.
create or replace function public.leads_limite()
returns trigger language plpgsql security definer set search_path = '' as $$
declare
  fone text := regexp_replace(coalesce(new.doc ->> 'whatsapp', ''), '\D', '', 'g');
begin
  if auth.uid() is null or public.eh_admin_plataforma() then
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

-- atualização ao vivo no painel
do $$
declare t text;
begin
  if exists (select 1 from pg_publication where pubname = 'supabase_realtime') then
    foreach t in array array['leads', 'orcamentos', 'config'] loop
      if not exists (select 1 from pg_publication_tables where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = t) then
        execute format('alter publication supabase_realtime add table public.%I', t);
      end if;
    end loop;
  end if;
end $$;
