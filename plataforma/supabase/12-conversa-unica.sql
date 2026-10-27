-- ================= 12: a mesma pessoa (com ou sem o 9) cai na mesma conversa =================
-- Rode depois do 10 e do 11. Pode rodar de novo sem problema.

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
  -- a Meta às vezes manda o celular com o 9 e às vezes sem: é a mesma pessoa e a mesma conversa
  select * into c from public.whats_conversas where loja_id = ct.loja_id and public.whats_chave_fone(wa_id) = public.whats_chave_fone(p_wa_id)
   order by ultima_em desc limit 1;
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
