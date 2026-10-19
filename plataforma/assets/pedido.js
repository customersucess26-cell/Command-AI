/* Bistrô Connect · rastreio do pedido: o cliente abre o link que chega no WhatsApp (pedido.html#codigo-secreto).
   Só lê pela função rastrear_pedido do banco, que devolve status, itens e valores do pedido
   daquele código. Nada de telefone ou endereço. Use pedido.html#demo para ver um exemplo. */
(function () {
  "use strict";
  var BC = window.BC || {};
  var $ = function (id) { return document.getElementById(id); };
  var token = (location.hash || "").replace(/^#(t=)?/, "").trim();
  var demo = token === "demo";
  var timer = null, ultimo = null, demoInicio = Date.now();

  function aplicaCor(c) { if (c && /^#[0-9a-fA-F]{6}$/.test(c)) document.documentElement.style.setProperty("--cor", c); }
  $("loja").textContent = "";

  var brl = function (v) { return (Number(v) || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" }); };
  var hora = function (iso) { var d = new Date(iso); return isNaN(d) ? "" : d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }); };
  var dia = function (iso) { var d = new Date(iso); return isNaN(d) ? "" : d.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" }); };
  var FORMAS = { pix: "Pix", dinheiro: "Dinheiro", cartao: "Cartão", a_combinar: "A combinar" };
  var PGTO = { pendente: "A pagar", parcial: "Pago em parte", pago: "Pago", estornado: "Estornado" };

  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function linha(a, b, cls) { var d = el("div", "linha" + (cls ? " " + cls : "")); d.appendChild(el("span", "", a)); d.appendChild(el("span", "", b)); return d; }
  function info(a, b) { var d = el("div"); d.appendChild(el("span", "", a)); d.appendChild(el("span", "", b)); return d; }

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

  function mostra(p) {
    ultimo = p;
    $("carregando").hidden = true;
    if (!p) { $("erro").hidden = false; $("pedido").hidden = true; return; }
    $("erro").hidden = true; $("pedido").hidden = false;
    if (p.store_name) { $("loja").textContent = p.store_name; document.title = "Pedido " + p.code + " · " + p.store_name; }
    aplicaCor(p.cor);
    if (p.slug && /^[a-z0-9-]{3,40}$/.test(p.slug)) $("voltar").href = "/l/" + p.slug;

    var lista = passos(p), ordem = lista.map(function (s) { return s[0]; });
    var idx = ordem.indexOf(p.status), cancel = p.status === "cancelado";
    var quando = {};
    (p.history || []).forEach(function (h) { if (h && h.status) quando[h.status] = h.at; });
    if (!quando.novo) quando.novo = p.created_at;

    $("ola").textContent = p.first_name ? "Olá, " + p.first_name + "!" : "Olá!";
    $("titulo").textContent = cancel ? "Pedido cancelado" : idx >= 0 ? lista[idx][1] : "Pedido recebido";
    $("codigo").textContent = "Pedido " + p.code;
    $("cancelado").hidden = !cancel;

    var ol = $("passos"); ol.textContent = "";
    lista.forEach(function (s, i) {
      var li = el("li", cancel ? (i === 0 ? "feito" : "pendente") : i < idx ? "feito" : i === idx ? (i === lista.length - 1 ? "feito" : "atual") : "pendente");
      li.appendChild(el("span", "bola", i < idx || (i === idx && i === lista.length - 1) ? "✓" : String(i + 1)));
      var t = el("div"); t.appendChild(el("b", "", s[1]));
      var sub = quando[s[0]] ? hora(quando[s[0]]) + (i === idx && !cancel ? " · " + s[2] : "") : (i === idx && !cancel ? s[2] : "");
      if (sub) t.appendChild(el("small", "", sub));
      li.appendChild(t); ol.appendChild(li);
    });

    var it = $("itens"); it.textContent = "";
    (p.items || []).forEach(function (i) {
      var preco = Number(i.price) > 0 ? brl(i.price * i.qty) : "sob consulta";
      it.appendChild(linha(i.qty + "× " + i.name + (i.unit ? " (" + i.unit + ")" : ""), preco));
    });
    if (Number(p.delivery_fee) > 0) it.appendChild(linha("Entrega", brl(p.delivery_fee)));
    if (Number(p.quoted_amount) > 0) it.appendChild(linha("Itens sob consulta", brl(p.quoted_amount)));
    if (Number(p.discount) > 0) it.appendChild(linha("Desconto", "− " + brl(p.discount)));
    var semValor = p.has_quote_items && !(Number(p.quoted_amount) > 0);
    it.appendChild(linha("Total", brl(p.total) + (semValor ? " + itens sob consulta" : ""), "total"));

    var inf = $("info"); inf.textContent = "";
    inf.appendChild(info("Como recebe", p.delivery_type === "entrega" ? "Entrega" : "Retirada na loja"));
    if (p.scheduled_for) inf.appendChild(info("Para", p.scheduled_for));
    inf.appendChild(info("Feito em", dia(p.created_at) + " às " + hora(p.created_at)));
    inf.appendChild(info("Pagamento", (FORMAS[p.payment_method] || p.payment_method || "A combinar") + " · " + (PGTO[p.payment_status] || "A pagar")));

    var fone = String(p.whatsapp || "").replace(/\D/g, "");
    if (fone.length === 10 || fone.length === 11) fone = "55" + fone;
    var zap = $("zap");
    if (fone.length >= 12 && fone.length <= 13 && !/^550+$/.test(fone)) {
      zap.href = "https://wa.me/" + fone + "?text=" + encodeURIComponent("Olá! Quero falar sobre o meu pedido " + p.code + ".");
      zap.hidden = false;
    } else zap.hidden = true;

    var final = cancel || p.status === "entregue";
    $("vivo").hidden = final;
    $("atualizado").textContent = final ? "" : "Esta página se atualiza sozinha. Última atualização às " + hora(new Date().toISOString()) + ".";
    if (final && timer) { clearInterval(timer); timer = null; }
  }

  function exemplo() {
    var passo = Math.min(4, Math.floor((Date.now() - demoInicio) / 8000));
    var st = ["novo", "confirmado", "em_preparo", "pronto", "entregue"][passo], agora = Date.now(), h = [];
    for (var i = 0; i <= passo; i++) h.push({ status: ["novo", "confirmado", "em_preparo", "pronto", "entregue"][i], at: new Date(agora - (passo - i) * 6 * 60000).toISOString() });
    return {
      code: "LO00042", status: st, delivery_type: "entrega", scheduled_for: "Hoje, o quanto antes", created_at: h[0].at,
      first_name: "Maria", store_name: "Padaria Exemplo", whatsapp: "", cor: "#B0703F",
      items: [{ name: "Croissant de manteiga", unit: "Unidade", qty: 2, price: 12.9 }, { name: "Cappuccino", unit: "300 ml", qty: 2, price: 14.5 }],
      subtotal: 54.8, delivery_fee: 6, total: 60.8, payment_method: "pix", payment_status: passo >= 1 ? "pago" : "pendente", history: h
    };
  }

  function busca() {
    if (demo) { mostra(exemplo()); return; }
    if (!/^[a-f0-9]{32,64}$/.test(token)) { mostra(null); return; }
    if (!BC.supabaseUrl || !BC.supabaseKey) {
      $("erroTxt").textContent = "O acompanhamento ainda não está ligado nesta loja. Fale com a loja pelo WhatsApp.";
      mostra(null); return;
    }
    fetch(BC.supabaseUrl.replace(/\/+$/, "") + "/rest/v1/rpc/rastrear_pedido", {
      method: "POST",
      headers: { "Content-Type": "application/json", apikey: BC.supabaseKey, Authorization: "Bearer " + BC.supabaseKey },
      body: JSON.stringify({ p_token: token }),
      cache: "no-store", referrerPolicy: "no-referrer"
    }).then(function (r) {
      if (!r.ok) throw new Error("http " + r.status);
      return r.json();
    }).then(function (p) { mostra(p && p.code ? p : null); })
      .catch(function () {
        if (ultimo) { $("atualizado").textContent = "Sem conexão agora. Tentando de novo…"; return; }
        $("erroTxt").textContent = "Não conseguimos buscar o pedido agora. Confira a internet e toque para tentar de novo.";
        mostra(null);
      });
  }

  busca();
  timer = setInterval(function () { if (!document.hidden) busca(); }, demo ? 4000 : 20000);
  document.addEventListener("visibilitychange", function () { if (!document.hidden && timer) busca(); });
  $("erro").addEventListener("click", function () { if (!ultimo && !demo) { $("carregando").hidden = false; $("erro").hidden = true; busca(); } });
  window.addEventListener("hashchange", function () { location.reload(); });
})();
