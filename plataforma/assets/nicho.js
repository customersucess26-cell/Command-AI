/* Página de vendas por nicho: ?para=padaria, cafeteria, hamburgueria, restaurante, pizzaria, confeitaria ou marmitaria.
   Use o link com ?para=... em cada anúncio. O título, a palavra do topo, o modelo do celular e o tipo do formulário
   passam a falar do mesmo negócio do anúncio. Sem ?para= a página fica como está. */
(function () {
  "use strict";
  var NICHOS = {
    padaria:      { palavra: "padarias",      modelo: "padaria", tipo: "Padaria",      titulo: "Sua padaria vende o dia inteiro. O app fica com <em class=\"risca\">até 23%</em> de cada pedido." },
    cafeteria:    { palavra: "cafeterias",    modelo: "cafe",    tipo: "Cafeteria",    titulo: "Seu café conquista pelo sabor. O app fica com <em class=\"risca\">até 23%</em> de cada pedido." },
    hamburgueria: { palavra: "hamburguerias", modelo: "burger",  tipo: "Hamburgueria", titulo: "Seu burger sai quente. O lucro sai pelo app: <em class=\"risca\">até 23%</em> de cada pedido." },
    restaurante:  { palavra: "restaurantes",  modelo: "rest",    tipo: "Restaurante",  titulo: "Seu restaurante lota no almoço. O app fica com <em class=\"risca\">até 23%</em> de cada prato." },
    pizzaria:     { palavra: "pizzarias",     modelo: "rest",    tipo: "Pizzaria",     titulo: "Sua pizza sai do forno. O app fica com <em class=\"risca\">até 23%</em> de cada pedido." },
    confeitaria:  { palavra: "confeitarias",  modelo: "padaria", tipo: "Confeitaria",  titulo: "Seus doces fazem sucesso. O app fica com <em class=\"risca\">até 23%</em> de cada encomenda." },
    marmitaria:   { palavra: "marmitarias",   modelo: "rest",    tipo: "Outro",        titulo: "Sua marmita sai no capricho. O app fica com <em class=\"risca\">até 23%</em> de cada pedido." }
  };
  var SIN = { doceria: "confeitaria", doces: "confeitaria", cafe: "cafeteria", cafes: "cafeteria", burger: "hamburgueria", lanchonete: "hamburgueria", pizza: "pizzaria", marmita: "marmitaria" };
  var q = "";
  try { q = (new URLSearchParams(location.search).get("para") || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z]/g, ""); } catch (e) {}
  q = NICHOS[q] ? q : (NICHOS[SIN[q]] ? SIN[q] : (NICHOS[q.replace(/s$/, "")] ? q.replace(/s$/, "") : ""));
  if (!q) return;
  var N = NICHOS[q]; N.chave = q;
  window.BC_NICHO = N;
  function aplica() {
    var h1 = document.querySelector(".hero h1");
    if (h1) h1.innerHTML = N.titulo; /* textos fixos deste arquivo, nada vem da URL */
    var t = document.getElementById("typed");
    if (t) { t.textContent = N.palavra; t.style.borderRight = "0"; }
    var sel = document.getElementById("lTipo");
    if (sel) Array.prototype.forEach.call(sel.options, function (o) { if (o.text === N.tipo) sel.value = o.value; });
    document.title = "Bistrô Connect para " + N.palavra + " | Cardápio digital e pedidos no WhatsApp, sem comissão";
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", aplica); else aplica();
})();
