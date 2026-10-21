-- Bistrô Connect · migração 05: limite de tamanho do conteúdo das páginas da loja (lojas.extra).
-- Rode uma vez no SQL Editor do Supabase (projeto plataforma). Pode rodar de novo sem problema.
alter table public.lojas drop constraint if exists lojas_extra_tam;
alter table public.lojas add constraint lojas_extra_tam
  check (jsonb_typeof(extra) = 'object' and pg_column_size(extra) < 30000);
