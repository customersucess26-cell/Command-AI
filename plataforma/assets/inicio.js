/* Página inicial da Bistrô Connect: planos lidos do banco (tabela planos) e link do suporte.
   Sem banco configurado, ficam os planos escritos no HTML. */
(function () {
  "use strict";
  var BC = window.BC || {};
  var $ = function (id) { return document.getElementById(id); };
  var brl = function (v) { return (Number(v) || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL", minimumFractionDigits: 0, maximumFractionDigits: 2 }); };
  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }

  $("ano").textContent = String(new Date().getFullYear());

  var fone = String(BC.suporteWhatsapp || "").replace(/\D/g, "");
  if (fone.length >= 12 && fone.length <= 13) {
    var s = $("suporte");
    s.href = "https://wa.me/" + fone + "?text=" + encodeURIComponent("Olá! Quero saber mais sobre a Bistrô Connect.");
    s.hidden = false;
  }

  var EXTRAS = [
    ["Loja e cardápio completos", "Pedidos e rastreio", "Painel e financeiro"],
    ["Tudo do Começo", "Equipe com funções", "Suporte pelo WhatsApp"],
    ["Tudo do Crescendo", "Relatórios por período", "Até 30 pessoas na equipe"],
    ["Tudo do Forte", "Valor fixo, venda o quanto quiser", "Atendimento prioritário"]
  ];

  function desenha(planos) {
    var box = $("planos"), anterior = 0;
    box.textContent = "";
    planos.forEach(function (p, i) {
      var art = el("article", "plano" + (i === 1 ? " destaque" : ""));
      if (i === 1) art.appendChild(el("span", "tag", "Mais comum"));
      art.appendChild(el("h3", "", p.nome));
      var faixa = p.ate_valor == null ? "Acima de " + brl(anterior) + "/mês" : "Vendas de até " + brl(p.ate_valor) + "/mês";
      art.appendChild(el("span", "faixa", faixa));
      var preco = el("div", "preco");
      if (Number(p.mensalidade) > 0) { preco.textContent = brl(p.mensalidade); preco.appendChild(el("small", "", "/mês")); }
      else preco.textContent = "Grátis";
      art.appendChild(preco);
      var ul = el("ul");
      (EXTRAS[Math.min(i, EXTRAS.length - 1)] || []).forEach(function (t) { ul.appendChild(el("li", "", t)); });
      art.appendChild(ul);
      box.appendChild(art);
      if (p.ate_valor != null) anterior = Number(p.ate_valor);
    });
  }

  if (BC.supabaseUrl && BC.supabaseKey) {
    fetch(BC.supabaseUrl.replace(/\/+$/, "") + "/rest/v1/planos?select=id,nome,ate_valor,mensalidade,ordem&order=ordem", {
      headers: { apikey: BC.supabaseKey, Authorization: "Bearer " + BC.supabaseKey }
    }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (lista) { if (Array.isArray(lista) && lista.length) desenha(lista); })
      .catch(function () { /* fica a tabela do HTML */ });
  }
})();
