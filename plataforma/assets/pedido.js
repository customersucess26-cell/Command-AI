/* Bistrô Connect · rastreio do pedido: o cliente abre o link que chega no WhatsApp (/p/<código>).
   Lê pela função cartao_pedido do banco (itens, valores, endereço, andamento e dados da loja) com o código de 16
   letras e números do pedido; links antigos (código longo) continuam abrindo pelo rastrear_pedido.
   Use ?c=demo para ver um exemplo. */
(function () {
  "use strict";
  var BC = window.BC || {};
  var $ = function (id) { return document.getElementById(id); };
  /* link curto /p/<código> (reescrito pelo .htaccess), ?c=<código> ou, nos links antigos, #<código longo> */
  var token = ((location.pathname.match(/^\/p\/([a-f0-9]{16})\/?$/) || [])[1] || new URLSearchParams(location.search).get("c") || (location.hash || "").replace(/^#(t=)?/, "")).trim();
  var demo = token === "demo";
  var timer = null, ultimo = null, demoInicio = Date.now(), demoPasso = null;

  var TEMAS = { padaria: "grid", doceria: "grid", cafeteria: "cafe", hamburgueria: "burger", pizzaria: "burger", restaurante: "plates", outro: "plates" };
  var brl = function (v) { return (Number(v) || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" }); };
  var hora = function (iso) { var d = new Date(iso); return isNaN(d) ? "" : d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }); };
  var dia = function (iso) { var d = new Date(iso); return isNaN(d) ? "" : d.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" }); };
  var FORMAS = { pix: "Pix", dinheiro: "Dinheiro", cartao: "Cartão", a_combinar: "A combinar" };
  var PGTO = { pendente: "A pagar", parcial: "Pago em parte", pago: "Pago", estornado: "Estornado" };

  var I = {
    check: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
    relogio: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    vazio: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8"/></svg>',
    pino: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s7-6 7-11a7 7 0 0 0-14 0c0 5 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>',
    cartao: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="6" width="18" height="12" rx="2"/><path d="M3 10h18M7 15h3"/></svg>',
    recibo: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3h12v18l-3-2-3 2-3-2-3 2zM9 8h6M9 12h6"/></svg>',
    panela: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 11h14v6a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3zM3 11h18M9 7c0-1.5 1-1.5 1-3M14 7c0-1.5 1-1.5 1-3"/></svg>',
    moto: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="6" cy="17" r="3"/><circle cx="18" cy="17" r="3"/><path d="M9 17h6l-3-7h-3M12 10h4l2 7"/></svg>',
    sacola: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 8h14l-1 12H6zM9 8V6a3 3 0 0 1 6 0v2"/></svg>',
    casa: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 11l9-7 9 7v9H5zM10 20v-6h4v6"/></svg>'
  };
  var IC5 = [I.recibo, I.check, I.panela, I.moto, I.casa];
  var ICONES = { novo: I.recibo, confirmado: I.check, em_preparo: I.panela, pronto: I.moto, entregue: I.casa };

  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function foneBR(f) {
    var d = String(f || "").replace(/\D/g, ""); if (d.length > 11 && d.slice(0, 2) === "55") d = d.slice(2);
    return d.length === 11 ? "(" + d.slice(0, 2) + ") " + d.slice(2, 7) + "-" + d.slice(7) : d.length === 10 ? "(" + d.slice(0, 2) + ") " + d.slice(2, 6) + "-" + d.slice(6) : "";
  }
  function foto(u) { return /^(\/assets\/|https:\/\/)/.test(u || "") ? u : ""; }
  function css(u) { return "url('" + String(u).replace(/['"\\()\s]/g, encodeURIComponent) + "')"; }

  function passos(p) {
    var entrega = p.delivery_type === "entrega";
    return [
      ["novo", "Pedido recebido", "A loja já recebeu o seu pedido."],
      ["confirmado", "Confirmado", "A loja confirmou e vai começar."],
      ["em_preparo", "Em preparo", "Estamos preparando com carinho."],
      ["pronto", entrega ? "Saiu para entrega" : "Pronto para retirar", entrega ? "Está a caminho." : "Pode vir buscar."],
      ["entregue", entrega ? "Entregue" : "Retirado", "Bom apetite!"]
    ];
  }
  var SUBTITULO = {
    novo: "Seu pedido foi realizado com sucesso pelo nosso site!",
    confirmado: "A loja confirmou o seu pedido.",
    em_preparo: "Estamos preparando o seu pedido agora.",
    pronto_entrega: "Seu pedido saiu para entrega!",
    pronto_retirada: "Seu pedido está pronto para retirar.",
    entregue: "Pedido finalizado. Bom apetite!",
    cancelado: "Este pedido foi cancelado."
  };

  function mostra(p) {
    ultimo = p;
    $("carregando").hidden = true;
    if (!p) { $("erro").hidden = false; $("pedido").hidden = true; return; }
    $("erro").hidden = true; $("pedido").hidden = false;

    var tema = TEMAS[p.modelo] || "plates";
    document.body.className = "lm-" + tema;
    if (p.store_name) document.title = "Pedido " + p.code + " · " + p.store_name;
    if (p.slug && /^[a-z0-9-]{3,40}$/.test(p.slug)) $("voltar").href = "/l/" + p.slug;

    var lista = passos(p), ordem = lista.map(function (s) { return s[0]; });
    var idx = ordem.indexOf(p.status), cancel = p.status === "cancelado", entrega = p.delivery_type === "entrega";
    var quando = {};
    (p.history || []).forEach(function (h) { if (h && h.status) quando[h.status] = h.at; });
    if (!quando.novo) quando.novo = p.created_at;
    var final = cancel || p.status === "entregue";

    var nome = p.first_name || String(p.customer_name || "").split(" ")[0];
    $("titulo").textContent = nome ? "Olá, " + nome + "!" : "Olá!";
    $("subtitulo").textContent = SUBTITULO[p.status === "pronto" ? (entrega ? "pronto_entrega" : "pronto_retirada") : p.status] || SUBTITULO.novo;
    $("codigo").textContent = "Pedido " + p.code;
    $("dataPed").textContent = "Data: " + dia(p.created_at) + " - " + hora(p.created_at);
    $("estSub").textContent = final ? (cancel ? "Pedido cancelado" : "Pedido finalizado") : "Em breve, ele estará com você!";
    $("cancelado").hidden = !cancel;

    var primeira = (p.items || []).map(function (i) { return foto(i.image_url); }).filter(Boolean)[0];
    var capa = foto(p.capa_url) || primeira || "";
    var f = $("foto"), card = $("olaCard");
    card.classList.toggle("sem-foto", !capa); f.hidden = !capa;
    if (capa) f.style.backgroundImage = css(capa);

    var hs = $("hst"); hs.textContent = ""; hs.hidden = cancel;
    lista.forEach(function (st, i) {
      var est = i < idx ? "feito" : i === idx ? (i === lista.length - 1 ? "feito" : "atual") : "pendente";
      var d = el("div", "hs " + est), ic = el("i"); ic.innerHTML = est === "feito" && i < lista.length - 1 ? I.check : (i === 3 && !entrega ? I.sacola : IC5[i]);
      d.appendChild(ic); d.appendChild(el("b", "", i === 3 && !entrega ? "Pronto" : i === 3 ? "A caminho" : i === 4 ? (entrega ? "Entregue" : "Retirado") : i === 0 ? "Recebido" : st[1])); hs.appendChild(d);
    });
    var ol = $("passos"); ol.textContent = "";
    lista.forEach(function (s, i) {
      var estado = cancel ? (i === 0 ? "feito" : "pendente") : i < idx ? "feito" : i === idx ? (i === lista.length - 1 ? "feito" : "atual") : "pendente";
      var li = el("li", estado);
      var bola = el("span", "bola"); bola.innerHTML = estado === "feito" ? I.check : ICONES[s[0]];
      var t = el("div"); t.appendChild(el("b", "", s[1]));
      var sub = quando[s[0]] && estado !== "pendente" ? hora(quando[s[0]]) + (estado === "feito" && i === lista.length - 1 ? " · " + s[2] : estado === "atual" ? " · " + s[2] : "") : (estado === "atual" ? s[2] : "");
      if (sub) t.appendChild(el("small", "", sub));
      var tag = el("span", "tag");
      tag.innerHTML = estado === "feito" ? I.check + "Concluído" : estado === "atual" ? I.relogio + "Em andamento" : I.vazio + "Pendente";
      li.appendChild(bola); li.appendChild(t); li.appendChild(tag); ol.appendChild(li);
    });

    var it = $("itens"); it.textContent = "";
    (p.items || []).forEach(function (i) {
      var u = foto(i.image_url), ops = Array.isArray(i.options) && i.options.length ? i.options.join(", ") : "";
      var row = el("div", "it" + (u ? "" : " sem-foto"));
      if (u) { var fo = el("span", "fto"); fo.style.backgroundImage = css(u); row.appendChild(fo); }
      row.appendChild(el("span", "q", i.qty + "x"));
      var nm = el("span", "", i.name + (i.unit ? " (" + i.unit + ")" : "")); if (ops) nm.appendChild(el("small", "", ops)); row.appendChild(nm);
      row.appendChild(el("em", "", Number(i.price) > 0 ? brl(i.price * i.qty) : "sob consulta"));
      it.appendChild(row);
    });
    if (Number(p.delivery_fee) > 0 || entrega) {
      var e = el("div", "it sem-foto"); e.appendChild(el("span", "q", "")); e.appendChild(el("span", "", "Entrega")); e.appendChild(el("em", "", Number(p.delivery_fee) > 0 ? brl(p.delivery_fee) : "Grátis"));
      it.appendChild(e);
    }
    $("total").textContent = brl(p.total);

    var inf = $("info"); inf.textContent = "";
    function bloco(ic, a, b) { var d = el("div"); var c = el("span", "ic"); c.innerHTML = ic; var t = el("div"); t.appendChild(el("small", "", a)); t.appendChild(el("b", "", b)); d.appendChild(c); d.appendChild(t); inf.appendChild(d); }
    bloco(I.pino, entrega ? "Entrega em" : "Retirada", entrega ? (p.address || "Endereço informado no pedido") : "Na loja");
    bloco(I.relogio, "Horário", p.scheduled_for || "O quanto antes");
    bloco(I.cartao, "Pagamento", (FORMAS[p.payment_method] || p.payment_method || "A combinar") + (p.payment_status ? " · " + (PGTO[p.payment_status] || "A pagar") : ""));

    var fone = String(p.whatsapp || "").replace(/\D/g, "");
    if (fone.length === 10 || fone.length === 11) fone = "55" + fone;
    var zap = $("zap");
    if (fone.length >= 12 && fone.length <= 13 && !/^550+$/.test(fone)) {
      zap.href = "https://wa.me/" + fone + "?text=" + encodeURIComponent("Olá! Quero falar sobre o meu pedido " + p.code + ".");
      $("zapNome").textContent = p.store_name || "Loja"; $("zapFone").textContent = foneBR(fone);
      zap.hidden = false;
    } else zap.hidden = true;

    $("atualizado").textContent = final ? "" : "Esta página se atualiza sozinha. Última atualização às " + hora(new Date().toISOString()) + ".";
    if (final && timer) { clearInterval(timer); timer = null; }
  }

  function exemplo() {
    var vel = +(String(new URLSearchParams(location.search).get("d") || "").match(/"v":(\d+)/) || [])[1] || 8000;
    var passo = demoPasso != null ? demoPasso : Math.min(4, Math.floor((Date.now() - demoInicio) / Math.max(1500, vel)));
    var st = ["novo", "confirmado", "em_preparo", "pronto", "entregue"][passo], agora = Date.now(), h = [];
    for (var i = 0; i <= passo; i++) h.push({ status: ["novo", "confirmado", "em_preparo", "pronto", "entregue"][i], at: new Date(agora - (passo - i) * 6 * 60000).toISOString() });
    var dd = null; try { dd = JSON.parse(new URLSearchParams(location.search).get("d") || "null"); } catch (e) { dd = null; }
    if (dd && typeof dd === "object") {      /* demonstração da página de vendas: loja, itens e tema do telefone */
      var its = (Array.isArray(dd.i) ? dd.i : []).slice(0, 8).map(function (x) { return { name: String(x[0] || "").slice(0, 60), unit: "", qty: +x[1] || 1, price: +x[2] || 0, image_url: /^\/assets\/img\/[a-z0-9_\/.-]+$/i.test(x[3] || "") ? x[3] : "" }; });
      var sub = its.reduce(function (a, x) { return a + x.qty * x.price; }, 0), fee = +dd.f || 0, ent = dd.t !== "r";
      return { code: "#" + (+dd.n || 42), status: st, delivery_type: ent ? "entrega" : "retirada", scheduled_for: "O quanto antes", created_at: h[0].at,
        modelo: String(dd.m || "padaria"), first_name: String(dd.c || "Maria").slice(0, 30), store_name: String(dd.l || "Sua loja").slice(0, 40), whatsapp: "5542999990000",
        address: String(dd.a || "Rua das Flores, 120 · Centro").slice(0, 80), items: its, subtotal: sub, delivery_fee: ent ? fee : 0, total: sub + (ent ? fee : 0),
        payment_method: "pix", payment_status: passo >= 1 ? "pago" : "pendente", history: h };
    }
    return {
      code: "#42", status: st, delivery_type: "entrega", scheduled_for: "Hoje, o quanto antes", created_at: h[0].at, modelo: "padaria",
      first_name: "Juliana", store_name: "Padaria da Ana", whatsapp: "5542999990000", address: "Rua das Flores, 120 · Centro",
      items: [{ name: "Pão doce com creme", unit: "Unidade", qty: 2, price: 8, image_url: "/assets/img/exemplo/pao-doce-com-creme.jpg" }, { name: "Cappuccino cremoso", unit: "Xícara", qty: 1, price: 12, image_url: "/assets/img/exemplo/cafe-menu-cappuccino-cacau.jpg" }],
      subtotal: 28, delivery_fee: 5, total: 33, payment_method: "pix", payment_status: passo >= 1 ? "pago" : "pendente", history: h
    };
  }

  function chama(rpc, corpo) {
    return fetch(BC.supabaseUrl.replace(/\/+$/, "") + "/rest/v1/rpc/" + rpc, {
      method: "POST",
      headers: { "Content-Type": "application/json", apikey: BC.supabaseKey, Authorization: "Bearer " + BC.supabaseKey },
      body: JSON.stringify(corpo), cache: "no-store", referrerPolicy: "no-referrer"
    }).then(function (r) { if (!r.ok) throw new Error("http " + r.status); return r.json(); });
  }

  function busca() {
    if (demo) { mostra(exemplo()); return; }
    if (!/^([a-f0-9]{16}|[a-f0-9]{32,64})$/.test(token)) { mostra(null); return; }
    if (!BC.supabaseUrl || !BC.supabaseKey) {
      $("erroTxt").textContent = "O acompanhamento ainda não está ligado nesta loja. Fale com a loja pelo WhatsApp.";
      mostra(null); return;
    }
    chama("cartao_pedido", { p_code: token })
      .then(function (p) { return p && p.code ? p : chama("rastrear_pedido", { p_token: token }); })
      .catch(function () { return chama("rastrear_pedido", { p_token: token }); })
      .then(function (p) { mostra(p && p.code ? p : null); })
      .catch(function () {
        if (ultimo) { $("atualizado").textContent = "Sem conexão agora. Tentando de novo…"; return; }
        $("erroTxt").textContent = "Não conseguimos buscar o pedido agora. Confira a internet e toque para tentar de novo.";
        mostra(null);
      });
  }

  if (demo) window.addEventListener("message", function (e) { if (e.origin === location.origin && e.data && typeof e.data.bcDemo === "number") { demoPasso = Math.max(0, Math.min(4, e.data.bcDemo)); busca(); } });
  busca();
  timer = setInterval(function () { if (!document.hidden) busca(); }, demo ? 1000 : 6000);
  document.addEventListener("visibilitychange", function () { if (!document.hidden && timer) busca(); });
  $("erro").addEventListener("click", function () { if (!ultimo && !demo) { $("carregando").hidden = false; $("erro").hidden = true; busca(); } });
  window.addEventListener("hashchange", function () { location.reload(); });
})();
