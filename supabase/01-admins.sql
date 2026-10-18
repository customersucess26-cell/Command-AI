-- eBistrô · 01: quem é administrador
-- Rode no Supabase: SQL Editor > New query > cole > Run. Pode rodar mais de uma vez.
--
-- Só quem estiver na tabela "admins" lê leads e pedidos ou altera o cardápio.
-- Estar logado não basta: se alguém criar uma conta no seu Supabase, continua sem acesso.

create table if not exists public.admins (
  user_id   uuid primary key references auth.users (id) on delete cascade,
  criado_em timestamptz not null default now()
);
alter table public.admins enable row level security;
revoke all on public.admins from anon, authenticated;

-- true quando o usuário logado é administrador.
-- Para exigir login em 2 etapas (recomendado), troque a linha do "select" por:
--   select exists (select 1 from public.admins a where a.user_id = auth.uid())
--          and coalesce(auth.jwt() ->> 'aal', '') = 'aal2'
create or replace function public.eh_admin()
returns boolean
language sql stable security definer
set search_path = ''
as $$
  select exists (select 1 from public.admins a where a.user_id = auth.uid())
$$;
revoke all on function public.eh_admin() from public;
grant execute on function public.eh_admin() to anon, authenticated;

-- Depois de criar o seu usuário em Authentication > Users, rode (troque o e-mail):
-- insert into public.admins (user_id)
--   select id from auth.users where email = 'seu-email@exemplo.com'
-- on conflict do nothing;
