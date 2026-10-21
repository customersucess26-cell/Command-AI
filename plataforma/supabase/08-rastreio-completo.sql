-- Bistrô Connect · rastreio do pedido completo (rode uma vez no SQL Editor do Supabase).
-- A página de acompanhamento passa a mostrar fotos dos itens, endereço, horário, o WhatsApp da loja e as cores da loja.
-- Só quem tem o código do pedido (16 letras e números) consegue ler.
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
    'subtotal', o.subtotal, 'delivery_fee', o.delivery_fee, 'total', o.total,
    'store_name', l.store_name, 'whatsapp', l.whatsapp, 'slug', l.slug, 'logo_url', l.logo_url, 'capa_url', l.capa_url, 'modelo', l.modelo, 'cor', l.cor);
end $$;

grant execute on function public.cartao_pedido(text) to anon, authenticated;
notify pgrst, 'reload schema';
