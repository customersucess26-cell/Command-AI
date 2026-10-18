-- eBistrô · 04: tabelas do painel (orçamentos e ajustes) e atualização ao vivo
-- Rode depois do 01-admins.sql e do 02-leads-ebistro.sql.
--
-- O painel admin/ guarda os orçamentos em "orcamentos" e os dados da empresa e
-- metas em "config" (linha id = 'empresa'). Só administradores logados com
-- 2 etapas (aal2) leem ou alteram. Visitante não tem acesso nenhum.

create table if not exists public.orcamentos (
  id         bigint generated always as identity primary key,
  doc        jsonb not null,
  created_at timestamptz not null default now()
);
alter table public.orcamentos add column if not exists created_at timestamptz not null default now();

create table if not exists public.config (
  id         text primary key,
  doc        jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

do $$
declare t text; p record;
begin
  foreach t in array array['orcamentos', 'config'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('alter table public.%I force row level security', t);
    for p in select policyname from pg_policies where schemaname = 'public' and tablename = t loop
      execute format('drop policy %I on public.%I', p.policyname, t);
    end loop;
    execute format('revoke all on public.%I from anon, authenticated', t);
    execute format('grant select, insert, update, delete on public.%I to authenticated', t);
    execute format($f$create policy "admin com 2 etapas" on public.%I for all to authenticated
      using (public.eh_admin() and coalesce(auth.jwt() ->> 'aal', '') = 'aal2')
      with check (public.eh_admin() and coalesce(auth.jwt() ->> 'aal', '') = 'aal2' and pg_column_size(doc) < 200000)$f$, t);
  end loop;
end $$;

-- atualização ao vivo no painel (se a publicação do Supabase existir)
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
