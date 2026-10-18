/* Painel eBistrô: CRM dos leads gravados pelo site (tabela "leads" do Supabase).
   Segurança: login com 2 etapas obrigatório, sessão só nesta aba, saída automática
   após 30 min parado, dados sempre escritos com textContent (nunca innerHTML). */
(function () {
  'use strict';

  var CFG = window.BISTRO || {};
  var ETAPAS = [
    ['lead', 'Novo lead'], ['contato', 'Em contato'], ['amostra', 'Amostra enviada'],
    ['proposta', 'Proposta'], ['cliente', 'Cliente'], ['perdido', 'Perdido']
  ];
  var NOME_ETAPA = Object.fromEntries(ETAPAS);
  var CHECK = [
    ['cardapio', 'Cardápio recebido'], ['fotos', 'Fotos recebidas'], ['logo', 'Logo recebido'],
    ['amostra', 'Amostra enviada'], ['contrato', 'Contrato aceito'], ['pagamento', 'Implantação paga'],
    ['noar', 'Cardápio no ar'], ['treino', 'Treinamento feito']
  ];
  var INATIVO_MS = 30 * 60 * 1000;

  var db = null, demo = false, leads = [], vista = 'inicio', atual = null, salvando = false;

  /* ---------- utilidades ---------- */
  var $ = function (id) { return document.getElementById(id); };
  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function limpa(n) { while (n.firstChild) n.removeChild(n.firstChild); }
  function hoje() { var d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }
  function dataBR(iso) { if (!iso) return '—'; var p = String(iso).slice(0, 10).split('-'); return p.length === 3 ? p[2] + '/' + p[1] + '/' + p[0] : '—'; }
  function brl(n) { return (Number(n) || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }); }
  function num(txt) { var t = String(txt || '').replace(/[^\d,.-]/g, ''); if (t.indexOf(',') >= 0) t = t.replace(/\./g, '').replace(',', '.'); var v = parseFloat(t); return isFinite(v) && v >= 0 ? Math.round(v * 100) / 100 : 0; }
  function digitos(t) { return String(t || '').replace(/\D/g, ''); }
  function zap(t) { var d = digitos(t); if (d.length >= 10 && d.length <= 11) d = '55' + d; return d.length >= 12 ? 'https://wa.me/' + d : ''; }
  function D(l) { return l.doc || {}; }
  var tAviso;
  function aviso(txt, ruim) { var a = $('aviso'); a.textContent = txt; a.className = 'aviso on' + (ruim ? ' ruim' : ''); clearTimeout(tAviso); tAviso = setTimeout(function () { a.className = 'aviso'; }, ruim ? 5000 : 2400); }
  function msgAuth(txt, ok) { var m = $('authMsg'); m.textContent = txt || ''; m.className = 'msg' + (ok ? ' ok' : ''); }
  function erroAmigavel(e) {
    var m = (e && (e.message || e.error_description)) || '';
    if (/Invalid login credentials/i.test(m)) return 'E-mail ou senha incorretos.';
    if (/Invalid TOTP|invalid code|expired/i.test(m)) return 'Código inválido ou vencido. Confira o app e tente de novo.';
    if (/rate limit|too many/i.test(m)) return 'Muitas tentativas. Espere alguns minutos.';
    if (/permission denied|row-level security|JWT/i.test(m)) return 'Sua conta não tem acesso a estes dados.';
    if (/Failed to fetch|NetworkError/i.test(m)) return 'Sem conexão com o servidor. Verifique a internet.';
    return 'Não foi possível concluir. Tente de novo.';
  }

  /* ---------- entrada e login em 2 etapas ---------- */
  function mostraForm(id) { ['fLogin', 'fCodigo', 'fCadastro2fa', 'semConfig'].forEach(function (f) { $(f).hidden = f !== id; }); $('telaAuth').hidden = false; $('telaApp').hidden = true; var i = $(id).querySelector('input'); if (i) i.focus(); }

  var tentativas = 0, bloqueadoAte = 0;
  $('fLogin').addEventListener('submit', async function (ev) {
    ev.preventDefault(); msgAuth('');
    if (Date.now() < bloqueadoAte) return msgAuth('Muitas tentativas. Aguarde ' + Math.ceil((bloqueadoAte - Date.now()) / 1000) + ' s.');
    var email = $('lgEmail').value.trim().toLowerCase(), senha = $('lgSenha').value;
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) || !senha) return msgAuth('Informe e-mail e senha.');
    var b = this.querySelector('button'); b.disabled = true;
    try {
      var r = await db.auth.signInWithPassword({ email: email, password: senha });
      if (r.error) throw r.error;
      tentativas = 0; $('lgSenha').value = '';
      await segundaEtapa();
    } catch (e) {
      tentativas++; if (tentativas >= 5) { bloqueadoAte = Date.now() + 60000 * Math.min(tentativas - 4, 10); }
      msgAuth(erroAmigavel(e));
    } finally { b.disabled = false; }
  });

  var fatorNovo = null;
  async function segundaEtapa() {
    var nivel = await db.auth.mfa.getAuthenticatorAssuranceLevel();
    if (nivel.error) throw nivel.error;
    if (nivel.data.currentLevel === 'aal2') return entrar();
    var f = await db.auth.mfa.listFactors();
    if (f.error) throw f.error;
    if (f.data.totp && f.data.totp.length) { $('cdCodigo').value = ''; return mostraForm('fCodigo'); }
    // primeira vez: cadastra o autenticador
    var pendentes = (f.data.all || []).filter(function (x) { return x.status === 'unverified'; });
    for (var i = 0; i < pendentes.length; i++) await db.auth.mfa.unenroll({ factorId: pendentes[i].id });
    var n = await db.auth.mfa.enroll({ factorType: 'totp', friendlyName: 'Painel eBistrô ' + Date.now() });
    if (n.error) throw n.error;
    fatorNovo = n.data.id;
    $('qr2fa').src = n.data.totp.qr_code;
    $('seg2fa').textContent = n.data.totp.secret;
    $('cdNovo').value = '';
    mostraForm('fCadastro2fa');
  }

  async function verifica(fatorId, codigo, botao) {
    if (!/^\d{6}$/.test(codigo)) return msgAuth('Digite os 6 números do app.');
    botao.disabled = true; msgAuth('');
    try {
      var r = await db.auth.mfa.challengeAndVerify({ factorId: fatorId, code: codigo });
      if (r.error) throw r.error;
      await entrar();
    } catch (e) { msgAuth(erroAmigavel(e)); } finally { botao.disabled = false; }
  }
  $('fCodigo').addEventListener('submit', async function (ev) {
    ev.preventDefault();
    var f = await db.auth.mfa.listFactors();
    var fator = f.data && f.data.totp && f.data.totp[0];
    if (!fator) return segundaEtapa();
    verifica(fator.id, $('cdCodigo').value.trim(), this.querySelector('button[type=submit]'));
  });
  $('fCadastro2fa').addEventListener('submit', function (ev) {
    ev.preventDefault();
    verifica(fatorNovo, $('cdNovo').value.trim(), this.querySelector('button[type=submit]'));
  });

  var saindo = false;
  async function sair(motivo) {
    if (saindo) return; saindo = true;
    clearInterval(tRecarga);
    if (db && !demo) { try { await db.auth.signOut(); } catch (e) { } }
    saindo = false;
    leads = []; demo = false; fechaFicha();
    if (!db) return mostraForm('semConfig');
    mostraForm('fLogin'); msgAuth(motivo || '', !motivo);
  }
  document.addEventListener('click', function (e) { if (e.target.closest('[data-sair]')) sair(''); });

  // saída automática por inatividade
  var ultimoUso = Date.now();
  ['pointerdown', 'keydown', 'scroll', 'touchstart'].forEach(function (t) { addEventListener(t, function () { ultimoUso = Date.now(); }, { passive: true }); });
  setInterval(function () { if (!$('telaApp').hidden && !demo && Date.now() - ultimoUso > INATIVO_MS) sair('Você saiu por inatividade. Entre de novo.'); }, 30000);

  /* ---------- dados ---------- */
  var tRecarga;
  async function entrar() {
    try { await carrega(); } catch (e) { await sair(erroAmigavel(e)); return; }
    if (!demo) {
      var u = await db.auth.getUser();
      $('quem').textContent = (u.data && u.data.user && u.data.user.email) || '';
    }
    $('telaAuth').hidden = true; $('telaApp').hidden = false; $('faixaDemo').hidden = !demo;
    msgAuth(''); trocaVista(vista);
    clearInterval(tRecarga);
    if (!demo) tRecarga = setInterval(function () { if (!document.hidden && $('ficha').hidden) carrega().then(desenha).catch(function () { }); }, 60000);
  }

  async function carrega() {
    if (demo) return;
    var r = await db.from('leads').select('id, doc, created_at').order('created_at', { ascending: false }).limit(2000);
    if (r.error) throw r.error;
    leads = (r.data || []).filter(function (l) { return l.doc && typeof l.doc === 'object'; });
  }

  async function grava(l, doc) {
    if (demo) { if (l) { l.doc = doc; return l; } var n = { id: 'd' + Date.now(), doc: doc, created_at: new Date().toISOString() }; leads.unshift(n); return n; }
    var r = l
      ? await db.from('leads').update({ doc: doc }).eq('id', l.id).select('id, doc, created_at').single()
      : await db.from('leads').insert({ doc: doc }).select('id, doc, created_at').single();
    if (r.error) throw r.error;
    var i = leads.findIndex(function (x) { return x.id === r.data.id; });
    if (i >= 0) leads[i] = r.data; else leads.unshift(r.data);
    return r.data;
  }

  async function apaga(l) {
    if (!demo) { var r = await db.from('leads').delete().eq('id', l.id); if (r.error) throw r.error; }
    leads = leads.filter(function (x) { return x.id !== l.id; });
  }

  /* ---------- telas ---------- */
  var TITULOS = { inicio: 'Início', funil: 'Funil de vendas', lista: 'Todos os leads', clientes: 'Clientes' };
  function trocaVista(v) {
    vista = v;
    document.querySelectorAll('[data-vista]').forEach(function (b) { if (b.dataset.vista === v) b.setAttribute('aria-current', 'page'); else b.removeAttribute('aria-current'); });
    ['inicio', 'funil', 'lista', 'clientes'].forEach(function (x) { $('v' + x.charAt(0).toUpperCase() + x.slice(1)).hidden = x !== v; });
    $('titulo').textContent = TITULOS[v];
    desenha();
  }
  document.querySelectorAll('[data-vista]').forEach(function (b) { b.addEventListener('click', function () { trocaVista(b.dataset.vista); }); });

  function filtrados() {
    var q = $('busca').value.trim().toLowerCase(), qd = digitos(q);
    if (!q) return leads;
    return leads.filter(function (l) {
      var d = D(l);
      return [d.nome, d.responsavel, d.cidade, d.tipo].some(function (v) { return String(v || '').toLowerCase().indexOf(q) >= 0; })
        || (qd.length >= 3 && digitos(d.whatsapp).indexOf(qd) >= 0);
    });
  }
  $('busca').addEventListener('input', function () { desenha(); });

  function etiqueta(st) { return el('span', 'etiqueta e-' + (NOME_ETAPA[st] ? st : 'lead'), NOME_ETAPA[st] || 'Novo lead'); }
  function etapaDe(l) { return NOME_ETAPA[D(l).stage] ? D(l).stage : 'lead'; }
  function emAberto(l) { var s = etapaDe(l); return s !== 'cliente' && s !== 'perdido'; }
  function atrasado(l) { var p = D(l).proximoContato; return emAberto(l) && p && p <= hoje(); }

  function kpi(alvo, rotulo, valor, nota, quente) {
    var k = el('div', 'kpi' + (quente ? ' quente' : '')); k.append(el('span', null, rotulo), el('b', null, valor)); if (nota) k.append(el('small', null, nota)); alvo.appendChild(k);
  }
  function mini(alvo, l, linha2) {
    var b = el('button', 'mini'); b.type = 'button';
    var t = el('div', 't'); t.append(el('b', null, D(l).nome || 'Sem nome'), el('small', null, linha2));
    b.append(t, etiqueta(etapaDe(l))); b.addEventListener('click', function () { abreFicha(l); }); alvo.appendChild(b);
  }

  function desenha() {
    if ($('telaApp').hidden) return;
    var L = filtrados();
    if (vista === 'inicio') desenhaInicio(L);
    if (vista === 'funil') desenhaFunil(L);
    if (vista === 'lista') desenhaLista(L);
    if (vista === 'clientes') desenhaClientes(L);
  }

  function desenhaInicio(L) {
    var k = $('kpis'); limpa(k);
    var seteDias = Date.now() - 7 * 864e5;
    var novos = L.filter(function (l) { return new Date(l.created_at).getTime() >= seteDias; }).length;
    var abertos = L.filter(emAberto).length;
    var clientes = L.filter(function (l) { return etapaDe(l) === 'cliente'; });
    var mrr = clientes.reduce(function (s, l) { return s + num(D(l).mensalidade); }, 0);
    var fechados = L.filter(function (l) { var s = etapaDe(l); return s === 'cliente' || s === 'perdido'; }).length;
    var atras = L.filter(atrasado);
    kpi(k, 'Leads em 7 dias', String(novos));
    kpi(k, 'Em negociação', String(abertos));
    kpi(k, 'Retornos pendentes', String(atras.length), atras.length ? 'Para hoje ou atrasados' : 'Tudo em dia', atras.length > 0);
    kpi(k, 'Receita mensal (clientes)', brl(mrr), clientes.length + (clientes.length === 1 ? ' cliente' : ' clientes'));
    kpi(k, 'Conversão', fechados ? Math.round(clientes.length / fechados * 100) + '%' : '—', 'Clientes ÷ negócios encerrados');

    var ag = $('agenda'); limpa(ag);
    atras.sort(function (a, b) { return String(D(a).proximoContato).localeCompare(String(D(b).proximoContato)); }).slice(0, 8)
      .forEach(function (l) { mini(ag, l, (D(l).proximoContato < hoje() ? 'Atrasado desde ' : 'Hoje · ') + dataBR(D(l).proximoContato)); });
    if (!ag.firstChild) ag.appendChild(el('p', 'vazio', 'Nenhum retorno para hoje.'));

    var rc = $('recentes'); limpa(rc);
    L.slice(0, 6).forEach(function (l) { mini(rc, l, dataBR(l.created_at) + ' · ' + (D(l).origem || 'site')); });
    if (!rc.firstChild) rc.appendChild(el('p', 'vazio', 'Nenhum lead ainda. Eles aparecem aqui assim que alguém preencher o site.'));

    var bf = $('barrasFunil'); limpa(bf);
    var cont = ETAPAS.map(function (e) { return L.filter(function (l) { return etapaDe(l) === e[0]; }).length; });
    var mx = Math.max.apply(null, cont.concat(1));
    ETAPAS.forEach(function (e, i) {
      var r = el('div', 'barra'), trilho = el('div'), b = el('i');
      b.style.width = (cont[i] / mx * 100) + '%'; trilho.appendChild(b);
      r.append(el('span', null, e[1]), trilho, el('b', null, String(cont[i]))); bf.appendChild(r);
    });
  }

  function desenhaFunil(L) {
    var k = $('kanban'); limpa(k);
    ETAPAS.forEach(function (e, idx) {
      var col = el('div', 'coluna'); col.dataset.etapa = e[0];
      var da = L.filter(function (l) { return etapaDe(l) === e[0]; });
      var h = el('h2', null, e[1]); h.appendChild(el('span', null, String(da.length))); col.appendChild(h);
      da.forEach(function (l) {
        var c = el('div', 'cartao'); c.draggable = true; c.tabIndex = 0; c.setAttribute('role', 'button');
        c.setAttribute('aria-label', 'Abrir ' + (D(l).nome || 'lead'));
        c.append(el('b', null, D(l).nome || 'Sem nome'), el('small', null, [D(l).tipo, D(l).cidade].filter(Boolean).join(' · ') || '—'));
        if (D(l).proximoContato && emAberto(l)) { var p = el('small', atrasado(l) ? 'atrasado' : null, 'Retorno: ' + dataBR(D(l).proximoContato)); c.appendChild(p); }
        var mv = el('div', 'mover');
        if (idx > 0) { var a = el('button', null, '‹ ' + ETAPAS[idx - 1][1]); a.type = 'button'; a.addEventListener('click', function (ev) { ev.stopPropagation(); mudaEtapa(l, ETAPAS[idx - 1][0]); }); mv.appendChild(a); }
        if (idx < ETAPAS.length - 1) { var p2 = el('button', null, ETAPAS[idx + 1][1] + ' ›'); p2.type = 'button'; p2.addEventListener('click', function (ev) { ev.stopPropagation(); mudaEtapa(l, ETAPAS[idx + 1][0]); }); mv.appendChild(p2); }
        c.appendChild(mv);
        c.addEventListener('click', function () { abreFicha(l); });
        c.addEventListener('keydown', function (ev) { if (ev.target === c && (ev.key === 'Enter' || ev.key === ' ')) { ev.preventDefault(); abreFicha(l); } });
        c.addEventListener('dragstart', function (ev) { ev.dataTransfer.setData('text/plain', String(l.id)); });
        col.appendChild(c);
      });
      col.addEventListener('dragover', function (ev) { ev.preventDefault(); col.classList.add('alvo'); });
      col.addEventListener('dragleave', function () { col.classList.remove('alvo'); });
      col.addEventListener('drop', function (ev) {
        ev.preventDefault(); col.classList.remove('alvo');
        var id = ev.dataTransfer.getData('text/plain'), l = leads.find(function (x) { return String(x.id) === id; });
        if (l && etapaDe(l) !== e[0]) mudaEtapa(l, e[0]);
      });
      k.appendChild(col);
    });
  }

  async function mudaEtapa(l, etapa) {
    var doc = Object.assign({}, D(l), { stage: etapa });
    try { await grava(l, doc); aviso((doc.nome || 'Lead') + ': ' + NOME_ETAPA[etapa]); desenha(); }
    catch (e) { aviso(erroAmigavel(e), true); }
  }

  function preencheFiltros() {
    var fe = $('fEtapa'); if (fe.options.length === 1) ETAPAS.forEach(function (e) { fe.appendChild(new Option(e[1], e[0])); });
    var fo = $('fOrigem'), atualO = fo.value, origens = {};
    leads.forEach(function (l) { var o = String(D(l).origem || 'site').split(' / ')[0]; origens[o] = 1; });
    while (fo.options.length > 1) fo.remove(1);
    Object.keys(origens).sort().forEach(function (o) { fo.appendChild(new Option(o, o)); });
    fo.value = origens[atualO] ? atualO : '';
  }
  function listaFiltrada(L) {
    var fe = $('fEtapa').value, fo = $('fOrigem').value;
    return L.filter(function (l) { return (!fe || etapaDe(l) === fe) && (!fo || String(D(l).origem || 'site').split(' / ')[0] === fo); });
  }
  $('fEtapa').addEventListener('change', desenha); $('fOrigem').addEventListener('change', desenha);

  function linha(tb, l, cols) {
    var tr = el('tr'); tr.tabIndex = 0;
    cols.forEach(function (c) { var td = el('td'); if (c instanceof Node) td.appendChild(c); else td.textContent = c; tr.appendChild(td); });
    tr.addEventListener('click', function () { abreFicha(l); });
    tr.addEventListener('keydown', function (ev) { if (ev.key === 'Enter') abreFicha(l); });
    tb.appendChild(tr);
  }
  function desenhaLista(L) {
    preencheFiltros();
    var tb = $('tbLeads'); limpa(tb);
    listaFiltrada(L).forEach(function (l) {
      var d = D(l), prox = el('span', atrasado(l) ? 'atrasado' : null, dataBR(d.proximoContato));
      linha(tb, l, [d.nome || 'Sem nome', d.responsavel || '—', etiqueta(etapaDe(l)), prox, d.origem || 'site', dataBR(l.created_at)]);
    });
    if (!tb.firstChild) { var tr = el('tr'), td = el('td', 'vazio', 'Nenhum lead com esses filtros.'); td.colSpan = 6; tr.appendChild(td); tb.appendChild(tr); }
  }

  function desenhaClientes(L) {
    var C = L.filter(function (l) { return etapaDe(l) === 'cliente'; });
    var k = $('kpisClientes'); limpa(k);
    var mrr = C.reduce(function (s, l) { return s + num(D(l).mensalidade); }, 0);
    var impl = C.reduce(function (s, l) { return s + num(D(l).implantacao); }, 0);
    var pend = C.filter(function (l) { var ck = D(l).checklist || {}; return CHECK.some(function (c) { return !ck[c[0]]; }); }).length;
    kpi(k, 'Clientes', String(C.length));
    kpi(k, 'Receita mensal', brl(mrr), 'Soma das mensalidades');
    kpi(k, 'Receita anual prevista', brl(mrr * 12));
    kpi(k, 'Implantações', brl(impl), 'Valor combinado');
    kpi(k, 'Implantação incompleta', String(pend), pend ? 'Com itens do checklist em aberto' : 'Tudo concluído', pend > 0);
    var tb = $('tbClientes'); limpa(tb);
    C.forEach(function (l) {
      var d = D(l), ck = d.checklist || {}, feitos = CHECK.filter(function (c) { return ck[c[0]]; }).length;
      linha(tb, l, [d.nome || 'Sem nome', d.plano || '—', d.mensalidade ? brl(num(d.mensalidade)) : '—', d.implantacao ? brl(num(d.implantacao)) : '—', feitos + ' de ' + CHECK.length]);
    });
    if (!tb.firstChild) { var tr = el('tr'), td = el('td', 'vazio', 'Quando um lead virar cliente, ele aparece aqui.'); td.colSpan = 5; tr.appendChild(td); tb.appendChild(tr); }
  }

  /* ---------- ficha do lead ---------- */
  var F = $('fFicha');
  ETAPAS.forEach(function (e) { $('selEtapa').appendChild(new Option(e[1], e[0])); });
  CHECK.forEach(function (c) { var lb = el('label'), cb = el('input'); cb.type = 'checkbox'; cb.name = 'ck_' + c[0]; lb.append(cb, document.createTextNode(c[1])); $('checklist').appendChild(lb); });

  var focoAntes = null;
  function abreFicha(l) {
    atual = l || null; focoAntes = document.activeElement;
    var d = l ? D(l) : { stage: 'lead', tipo: 'Padaria', origem: 'manual' };
    F.reset();
    ['nome', 'responsavel', 'whatsapp', 'cidade', 'plano', 'proximoContato', 'notas'].forEach(function (k) { F.elements[k].value = d[k] || ''; });
    F.elements.tipo.value = d.tipo || 'Outro'; if (!F.elements.tipo.value) F.elements.tipo.value = 'Outro';
    F.elements.stage.value = NOME_ETAPA[d.stage] ? d.stage : 'lead';
    F.elements.mensalidade.value = d.mensalidade ? num(d.mensalidade).toFixed(2).replace('.', ',') : '';
    F.elements.implantacao.value = d.implantacao ? num(d.implantacao).toFixed(2).replace('.', ',') : '';
    var ck = d.checklist || {}; CHECK.forEach(function (c) { F.elements['ck_' + c[0]].checked = !!ck[c[0]]; });
    $('fichaTitulo').textContent = l ? (d.nome || 'Lead') : 'Novo lead';
    $('fichaInfo').textContent = l ? 'Entrou em ' + dataBR(l.created_at) + ' · origem: ' + (d.origem || 'site') : '';
    $('fichaMsg').textContent = '';
    var w = zap(d.whatsapp); $('fichaZap').hidden = !w; if (w) $('fichaZap').href = w + '?text=' + encodeURIComponent('Olá' + (d.responsavel ? ', ' + String(d.responsavel).split(' ')[0] : '') + '! Aqui é o Adilson, do eBistrô.');
    $('btnExcluir').hidden = !l;
    $('veu').hidden = false; $('ficha').hidden = false; F.elements.nome.focus();
  }
  function fechaFicha() { $('veu').hidden = true; $('ficha').hidden = true; atual = null; if (focoAntes && focoAntes.focus) focoAntes.focus(); }
  document.addEventListener('click', function (e) { if (e.target.closest('[data-fechar]') || e.target === $('veu')) fechaFicha(); });
  addEventListener('keydown', function (e) {
    if ($('ficha').hidden) return;
    if (e.key === 'Escape') fechaFicha();
    if (e.key === 'Tab') { // mantém o foco dentro da ficha
      var f = $('ficha').querySelectorAll('button:not([hidden]),a[href]:not([hidden]),input,select,textarea'), a = f[0], z = f[f.length - 1];
      if (e.shiftKey && document.activeElement === a) { e.preventDefault(); z.focus(); } else if (!e.shiftKey && document.activeElement === z) { e.preventDefault(); a.focus(); }
    }
  });
  F.elements.whatsapp.addEventListener('input', function () { var w = zap(this.value); $('fichaZap').hidden = !w; if (w) $('fichaZap').href = w; });

  F.addEventListener('submit', async function (ev) {
    ev.preventDefault(); if (salvando) return;
    var g = function (k) { return String(F.elements[k].value || '').trim(); };
    var m = $('fichaMsg'); m.textContent = '';
    if (!g('nome')) return (m.textContent = 'Informe o nome do estabelecimento.');
    var dw = digitos(g('whatsapp')); if (dw.length < 10 || dw.length > 13) return (m.textContent = 'Informe um WhatsApp com DDD.');
    var base = atual ? D(atual) : { stage: 'lead', origem: 'manual', criadoEm: hoje() };
    var ck = {}; CHECK.forEach(function (c) { if (F.elements['ck_' + c[0]].checked) ck[c[0]] = true; });
    var doc = Object.assign({}, base, {
      nome: g('nome').slice(0, 100), responsavel: g('responsavel').slice(0, 80), whatsapp: g('whatsapp').slice(0, 20),
      cidade: g('cidade').slice(0, 60), tipo: g('tipo'), stage: g('stage'), plano: g('plano'),
      proximoContato: /^\d{4}-\d{2}-\d{2}$/.test(g('proximoContato')) ? g('proximoContato') : '',
      mensalidade: num(g('mensalidade')), implantacao: num(g('implantacao')), checklist: ck, notas: g('notas').slice(0, 4000)
    });
    salvando = true; $('btnSalvar').disabled = true;
    try { await grava(atual, doc); aviso('Salvo'); fechaFicha(); desenha(); }
    catch (e) { m.textContent = erroAmigavel(e); }
    finally { salvando = false; $('btnSalvar').disabled = false; }
  });

  $('btnExcluir').addEventListener('click', async function () {
    if (!atual) return;
    if (!confirm('Excluir "' + (D(atual).nome || 'este lead') + '" para sempre? Para guardar o histórico, prefira a etapa "Perdido".')) return;
    try { await apaga(atual); aviso('Lead excluído'); fechaFicha(); desenha(); } catch (e) { $('fichaMsg').textContent = erroAmigavel(e); }
  });
  $('btnNovo').addEventListener('click', function () { abreFicha(null); });
  $('btnAtualizar').addEventListener('click', async function () { try { await carrega(); desenha(); aviso('Atualizado'); } catch (e) { aviso(erroAmigavel(e), true); } });

  /* ---------- planilha ---------- */
  $('btnCsv').addEventListener('click', function () {
    var cel = function (v) { var s = String(v == null ? '' : v); if (/^[=+\-@\t\r]/.test(s)) s = "'" + s; return '"' + s.replace(/"/g, '""') + '"'; };
    var linhas = [['Estabelecimento', 'Responsável', 'WhatsApp', 'Cidade', 'Tipo', 'Etapa', 'Plano', 'Mensalidade', 'Implantação', 'Próximo contato', 'Origem', 'Entrou em', 'Notas']]
      .concat(listaFiltrada(filtrados()).map(function (l) { var d = D(l); return [d.nome, d.responsavel, d.whatsapp, d.cidade, d.tipo, NOME_ETAPA[etapaDe(l)], d.plano, num(d.mensalidade).toFixed(2).replace('.', ','), num(d.implantacao).toFixed(2).replace('.', ','), dataBR(d.proximoContato), d.origem, dataBR(l.created_at), d.notas]; }));
    var blob = new Blob(['﻿' + linhas.map(function (r) { return r.map(cel).join(';'); }).join('\n')], { type: 'text/csv;charset=utf-8' });
    var a = el('a'); a.href = URL.createObjectURL(blob); a.download = 'leads-ebistro-' + hoje() + '.csv'; a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 2000);
  });

  /* ---------- demonstração (sem Supabase) ---------- */
  function dadosDemo() {
    var dia = function (n) { var d = new Date(Date.now() + n * 864e5); return d.toISOString(); };
    var dt = function (n) { return dia(n).slice(0, 10); };
    var L = [
      ['Padaria Trigo de Ouro', 'Marta', 'Padaria', 'Ponta Grossa', 'cliente', 'Profissional', 199, 1497, dt(30), { cardapio: 1, fotos: 1, logo: 1, amostra: 1, contrato: 1, pagamento: 1, noar: 1, treino: 1 }, 'site / instagram', -40],
      ['Café Grão Nobre', 'Rafael', 'Cafeteria', 'Ponta Grossa', 'cliente', 'Essencial', 149, 997, '', { cardapio: 1, fotos: 1, logo: 1, amostra: 1, contrato: 1, pagamento: 1 }, 'chat', -21],
      ['Brasa Burger', 'Diego', 'Hamburgueria', 'Castro', 'proposta', 'Premium', 299, 2497, dt(0), { cardapio: 1, amostra: 1 }, 'site / facebook', -9],
      ['Confeitaria Doce Lar', 'Ana', 'Confeitaria', 'Ponta Grossa', 'amostra', '', 0, 0, dt(-2), { amostra: 1 }, 'site', -6],
      ['Restaurante Alecrim', 'Paulo', 'Restaurante', 'Carambeí', 'contato', '', 0, 0, dt(1), {}, 'chat / google', -3],
      ['Pizzaria Forno a Lenha', 'Júlia', 'Pizzaria', 'Ponta Grossa', 'lead', '', 0, 0, '', {}, 'site / instagram', -1],
      ['Padaria Bom Dia', 'Carlos', 'Padaria', 'Telêmaco Borba', 'lead', '', 0, 0, '', {}, 'site', 0],
      ['Lanchonete do Zé', 'José', 'Outro', 'Ponta Grossa', 'perdido', '', 0, 0, '', {}, 'chat', -15]
    ];
    return L.map(function (r, i) { return { id: 'd' + i, created_at: dia(r[11]), doc: { nome: r[0], responsavel: r[1], tipo: r[2], cidade: r[3], stage: r[4], plano: r[5], mensalidade: r[6], implantacao: r[7], proximoContato: r[8], checklist: r[9], origem: r[10], whatsapp: '(42) 9 99' + (10 + i) + '-00' + (10 + i), notas: '' } }; });
  }
  $('btnDemo').addEventListener('click', function () { demo = true; leads = dadosDemo(); $('quem').textContent = 'demonstração'; entrar(); });

  /* ---------- início ---------- */
  async function inicia() {
    var url = String(CFG.supabaseUrl || ''), chave = String(CFG.supabaseKey || '');
    if (!/^https:\/\/[a-z0-9-]+\.supabase\.co\/?$/.test(url) || !chave || !window.supabase) return mostraForm('semConfig');
    db = window.supabase.createClient(url.replace(/\/$/, ''), chave, {
      auth: { storage: window.sessionStorage, persistSession: true, autoRefreshToken: true, detectSessionInUrl: false }
    });
    db.auth.onAuthStateChange(function (ev) { if (ev === 'SIGNED_OUT' && !$('telaApp').hidden && !demo) sair('Sua sessão terminou. Entre de novo.'); });
    var s = await db.auth.getSession();
    if (s.data && s.data.session) { try { await segundaEtapa(); return; } catch (e) { } }
    mostraForm('fLogin');
  }
  inicia();
})();
