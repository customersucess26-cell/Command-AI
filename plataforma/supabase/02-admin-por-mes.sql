-- Bistrô Connect · painel do dono da plataforma com escolha do mês (para cobrar o mês que passou).
-- Rode UMA vez no SQL Editor do projeto "plataforma". É seguro rodar de novo.
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
revoke all on function public.admin_lojas(date) from public;
grant execute on function public.admin_lojas(date) to authenticated;
