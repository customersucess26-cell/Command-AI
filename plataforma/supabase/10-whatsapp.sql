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
