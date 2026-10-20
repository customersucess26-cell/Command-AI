/* Bistrô Connect · vitrine pública de cada loja (/l/<endereço> ou loja.html?l=<endereço>).
   Lê o cardápio com a chave pública (anon) e cria o pedido pela função create_order do banco,
   que recalcula preço, taxa e total. Tudo que vem do banco é escrito com textContent. */
(function () {
  "use strict";
  var BC = window.BC || {};
  var API = String(BC.supabaseUrl || "").replace(/\/+$/, "");
  var CHAVE = BC.supabaseKey || "";
  var $ = function (id) { return document.getElementById(id); };
  var COLUNAS_LOJA = "id,slug,store_name,modelo,descricao,whatsapp,address,hours,instagram,cor,logo_url,capa_url," +
    "delivery_fee,min_order,accept_orders,faz_entrega,faz_retirada,pagamentos,extra,status";

  var slug = (new URLSearchParams(location.search).get("l") || (location.pathname.match(/^\/l\/([a-z0-9-]{3,40})\/?$/) || [])[1] || "").toLowerCase();
  var loja = null, cats = [], prods = [], porId = {}, carrinho = {}, passo = "carrinho";
  var idem = { sig: "", chave: "" }, enviando = false, ultimoPedido = null;

  /* ---------- utilidades ---------- */
  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function brl(v) { return (Number(v) || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" }); }
  function r2(v) { return Math.round((Number(v) || 0) * 100) / 100; }
  function digitos(s) { return String(s || "").replace(/\D/g, ""); }
  function urlSegura(u) { u = String(u || "").trim(); return /^https:\/\/[^\s"'<>]+$/i.test(u) || /^\/[^\/\s"'<>][^\s"'<>]*$/.test(u) ? u : ""; }
  function chaveNova() { try { return crypto.randomUUID(); } catch (e) { return "k" + Date.now().toString(36) + Math.random().toString(36).slice(2, 12); } }
  function lsGet(k) { try { return JSON.parse(localStorage.getItem(k) || "null"); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  function zapNumero(f) { var d = digitos(f); if (d.length === 10 || d.length === 11) d = "55" + d; return d.length >= 12 && d.length <= 13 ? d : ""; }
  function siteBase() { return String(BC.site || location.origin).replace(/\/+$/, ""); }
  var avisoT = null;
  function aviso(t) { var a = $("aviso"); a.textContent = t; a.classList.add("mostra"); clearTimeout(avisoT); avisoT = setTimeout(function () { a.classList.remove("mostra"); }, 2600); }

  function api(caminho, opcoes) {
    opcoes = opcoes || {};
    var h = { apikey: CHAVE, Authorization: "Bearer " + CHAVE, Accept: "application/json" };
    if (opcoes.body) h["Content-Type"] = "application/json";
    return fetch(API + "/rest/v1/" + caminho, { method: opcoes.method || "GET", headers: h, body: opcoes.body, cache: "no-store" })
      .then(function (r) {
        return r.text().then(function (t) {
          var j = null; try { j = t ? JSON.parse(t) : null; } catch (e) {}
          if (!r.ok) { var err = new Error((j && j.code === "P0001" && j.message) || ""); err.hint = j && j.hint; err.amigavel = !!(j && j.code === "P0001"); throw err; }
          return j;
        });
      });
  }

  function estado(txt, comBotao) {
    $("app").hidden = true; $("barra").hidden = true;
    $("estado").hidden = false; $("estadoTxt").textContent = txt;
    $("estado").querySelector(".giro").hidden = !!comBotao; $("estadoBtn").hidden = !comBotao;
  }

  /* ---------- carregar ---------- */
  function carregaCardapio() {
    return Promise.all([
      api("categories?select=id,name,position&loja_id=eq." + loja.id + "&active=eq.true&order=position.asc,name.asc"),
      api("products?select=id,category_id,name,description,price,unit,image_url,featured,badge,position&loja_id=eq." + loja.id + "&active=eq.true&order=position.asc,name.asc")
    ]).then(function (r) {
      cats = r[0] || []; prods = r[1] || []; porId = {};
      prods.forEach(function (p) { p.price = Number(p.price) || 0; porId[p.id] = p; });
      var mudou = false;
      Object.keys(carrinho).forEach(function (id) { if (!porId[id]) { delete carrinho[id]; mudou = true; } });
      if (mudou) salvaCarrinho();
      return mudou;
    });
  }

  function inicia() {
    if (!slug) { estado("Endereço de loja inválido.", true); return; }
    if (!API || !CHAVE) { estado("A plataforma ainda não está configurada.", true); return; }
    api("lojas?select=" + COLUNAS_LOJA + "&slug=eq." + encodeURIComponent(slug) + "&limit=1")
      .then(function (r) {
        loja = r && r[0];
        if (!loja) { estado("Não encontramos esta loja. Confira o endereço.", true); document.title = "Loja não encontrada"; return null; }
        loja.delivery_fee = Number(loja.delivery_fee) || 0; loja.min_order = Number(loja.min_order) || 0;
        loja.pagamentos = Array.isArray(loja.pagamentos) && loja.pagamentos.length ? loja.pagamentos : ["Pix", "Cartão", "Dinheiro"];
        carrinho = lsGet("bc-carrinho-" + slug) || {};
        if (typeof carrinho !== "object" || Array.isArray(carrinho)) carrinho = {};
        return carregaCardapio().then(function () { montaLoja(); desenhaMenu(); atualizaBarra(); });
      })
      .catch(function () { estado("Não conseguimos abrir o cardápio agora. Confira a internet e tente de novo.", false); $("estadoBtn").hidden = true; setTimeout(inicia, 6000); });
  }

  /* ---------- tema e cabeçalho ---------- */
  function corTexto(hex) {
    var m = /^#?([0-9a-f]{6})$/i.exec(hex || ""); if (!m) return "#fff";
    var n = parseInt(m[1], 16), r = n >> 16 & 255, g = n >> 8 & 255, b = n & 255;
    return (0.299 * r + 0.587 * g + 0.114 * b) > 170 ? "#1b1410" : "#fff";
  }
  /* cada tipo de loja usa um tema, inspirado nos sites de referência: artesanal (padaria, café, doceria),
     brasa (hamburgueria, pizzaria) e autoral (restaurante e outros) */
  var TEMAS = { padaria: "artesanal", cafeteria: "artesanal", doceria: "artesanal", hamburgueria: "brasa", pizzaria: "brasa", restaurante: "autoral", outro: "autoral" };
  var ETIQUETAS = { padaria: "padaria e confeitaria artesanal", cafeteria: "café especial e confeitaria", doceria: "doces feitos com carinho",
    hamburgueria: "Hamburgueria artesanal · feita na hora", pizzaria: "Pizzaria · forno quente", restaurante: "Cozinha autoral", outro: "Cardápio" };
  /* cor da marca sempre legível no fundo escuro dos temas: se a cor for muito escura, clareia misturando com branco */
  function luz(hex) { var n = parseInt(hex.slice(1), 16); return (0.299 * (n >> 16 & 255) + 0.587 * (n >> 8 & 255) + 0.114 * (n & 255)) / 255; }
  function clareia(hex) {
    var n = parseInt(hex.slice(1), 16), m = [n >> 16 & 255, n >> 8 & 255, n & 255], t = luz(hex) < 0.38 ? Math.min(0.75, (0.38 - luz(hex)) * 2.2 + 0.25) : 0;
    return t ? "#" + m.map(function (v) { return ("0" + Math.round(v + (255 - v) * t).toString(16)).slice(-2); }).join("") : hex;
  }
  function montaLoja() {
    var modelo = TEMAS[loja.modelo] ? loja.modelo : "outro";
    document.body.className = "m-" + modelo + " t-" + TEMAS[modelo];
    var raiz = document.documentElement.style;
    /* loja que ainda usa a cor padrão da plataforma ganha o destaque do tema (dourado, vermelho ou âmbar) */
    var COR_TEMA = { artesanal: "#D4A65A", brasa: "#E0301E", autoral: "#C98A3E" };
    var corLoja = /^#b0703f$/i.test(loja.cor || "") ? COR_TEMA[TEMAS[modelo]] : loja.cor;
    if (/^#[0-9a-f]{6}$/i.test(corLoja || "")) { var viva = clareia(corLoja); raiz.setProperty("--cor", viva); raiz.setProperty("--cor-txt", corTexto(viva)); }
    var eb = $("eyebrow"); eb.textContent = ETIQUETAS[modelo]; eb.hidden = false;
    var tr = $("faixaTrilho"); tr.textContent = "";
    for (var k = 0; k < 8; k++) { tr.appendChild(el("span", "", loja.store_name)); tr.appendChild(el("i", "", "★")); }
    var meta = document.querySelector('meta[name="theme-color"]'); if (meta && loja.cor) meta.setAttribute("content", loja.cor);
    document.title = loja.store_name + " · Cardápio";

    $("nome").textContent = loja.store_name;
    $("descricao").textContent = loja.descricao || "";
    $("descricao").hidden = !loja.descricao;
    var aberta = loja.accept_orders !== false;
    $("selo").textContent = aberta ? "Recebendo pedidos" : "Pedidos pausados";
    $("selo").classList.toggle("fechada", !aberta);
    $("pausa").hidden = aberta;

    var fundo = $("capaFundo"); fundo.textContent = "";
    var capa = urlSegura(loja.capa_url);
    /* sem capa própria: foto padrão pelo tipo do negócio, até a loja enviar a dela */
    var padrao = !capa && ((window.BC_CAPAS || {})[loja.modelo] || "");
    if (capa || padrao) {
      var ic = el("img", padrao ? "padrao" : ""); ic.alt = ""; ic.src = capa || padrao;
      ic.addEventListener("load", function () { fundo.classList.add("carregou"); });
      ic.addEventListener("error", function () {
        /* capa da loja não abriu: usa a capa padrão do tipo, se houver */
        var reserva = (window.BC_CAPAS || {})[loja.modelo];
        if (!padrao && reserva && ic.getAttribute("src") !== reserva) { ic.className = "padrao"; ic.src = reserva; } else ic.remove();
      }); fundo.appendChild(ic);
    }
    var logo = $("logo"); logo.textContent = "";
    var lu = urlSegura(loja.logo_url);
    /* iniciais sem "da", "de", "do"…: "Doceria da Marina" vira DM */
    var palavras = String(loja.store_name || "?").split(/\s+/).filter(Boolean);
    var fortes = palavras.filter(function (p) { return !/^(d[aeo]s?|e|&|a|o|na|no)$/i.test(p); });
    var iniciais = (fortes.length ? fortes : palavras).slice(0, 2).map(function (p) { return p[0]; }).join("").toUpperCase();
    if (lu) { var il = el("img"); il.alt = ""; il.src = lu; il.addEventListener("error", function () { logo.textContent = iniciais; }); logo.appendChild(il); }
    else logo.textContent = iniciais;

    var inf = $("infos"); inf.textContent = "";
    function chip(icone, txt, href) {
      var c = el(href ? "a" : "span", "chip"); c.appendChild(el("i", "", icone)); c.appendChild(document.createTextNode(txt));
      if (href) { c.href = href; c.target = "_blank"; c.rel = "noopener noreferrer"; }
      inf.appendChild(c);
    }
    if (loja.hours) chip("◷", loja.hours);
    if (loja.faz_entrega) chip("➜", loja.delivery_fee > 0 ? "Entrega " + brl(loja.delivery_fee) : "Entrega grátis");
    if (loja.faz_retirada) chip("⌂", "Retirada na loja");
    if (loja.min_order > 0) chip("◎", "Pedido mínimo " + brl(loja.min_order));
    if (loja.address) chip("⚲", loja.address, "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(loja.address));
    var zap = zapNumero(loja.whatsapp);
    if (zap) chip("✆", "WhatsApp", "https://wa.me/" + zap);
    if (loja.instagram) {
      var ig = String(loja.instagram).replace(/^@/, "").replace(/^https?:\/\/(www\.)?instagram\.com\//i, "").replace(/[^A-Za-z0-9._]/g, "");
      if (ig) chip("◉", "@" + ig, "https://instagram.com/" + ig);
    }
    $("rodapeLoja").textContent = loja.store_name + (loja.address ? " · " + loja.address : "");

    $("estado").hidden = true; $("app").hidden = false;
  }

  /* ---------- cardápio ---------- */
  function qtd(id) { return carrinho[id] || 0; }
  function controle(p) {
    var box = el("div", "ctrl"); box.dataset.id = p.id;
    pintaControle(box, p);
    return box;
  }
  function pintaControle(box, p) {
    box.textContent = "";
    var q = qtd(p.id), aberta = loja.accept_orders !== false;
    if (!q) {
      var b = el("button", "add", "Adicionar"); b.type = "button"; b.dataset.mais = p.id;
      b.setAttribute("aria-label", "Adicionar " + p.name); b.disabled = !aberta;
      box.appendChild(b);
    } else {
      var s = el("div", "passo" + (q === 1 ? " novo" : ""));
      var m = el("button", "", "−"); m.type = "button"; m.dataset.menos = p.id; m.setAttribute("aria-label", "Tirar um " + p.name);
      var n = el("span", "", String(q)); n.setAttribute("aria-live", "polite");
      var mais = el("button", "", "+"); mais.type = "button"; mais.dataset.mais = p.id; mais.setAttribute("aria-label", "Mais um " + p.name);
      s.appendChild(m); s.appendChild(n); s.appendChild(mais); box.appendChild(s);
    }
  }
  function foto(p, cls) {
    var f = el("div", cls || "foto"), u = urlSegura(p.image_url);
    if (u) {
      f.classList.add("brilhando"); if (p.extra && p.extra.ajuste === "contain") f.classList.add("contem");
      var i = el("img"); i.alt = p.name; i.loading = "lazy"; i.decoding = "async"; i.src = u;
      i.addEventListener("load", function () { f.classList.remove("brilhando"); f.classList.add("carregou"); });
      i.addEventListener("error", function () { f.classList.remove("brilhando"); i.remove(); f.textContent = (p.name || "?")[0].toUpperCase(); });
      f.appendChild(i);
    } else f.textContent = (p.name || "?")[0].toUpperCase();
    return f;
  }
  function precoEl(p) {
    var d = el("span", "preco", brl(p.price));
    if (p.unit) d.appendChild(el("small", "", p.unit));
    return d;
  }
  function cartao(p) {
    var c = el("article", "prod revela" + (urlSegura(p.image_url) ? "" : " sem-foto"));
    var t = el("div");
    if (p.badge) t.appendChild(el("span", "badge", p.badge));
    t.appendChild(el("h3", "", p.name));
    if (p.description) t.appendChild(el("p", "", p.description));
    var meta = el("div", "meta"); meta.appendChild(precoEl(p)); meta.appendChild(controle(p));
    t.appendChild(meta); c.appendChild(t);
    if (urlSegura(p.image_url)) c.appendChild(foto(p));
    return c;
  }
  function desenhaMenu() {
    var menu = $("menu"), trilho = $("abasTrilho");
    menu.textContent = ""; trilho.textContent = "";
    var secoes = [];
    var destaques = prods.filter(function (p) { return p.featured; });
    if (destaques.length) {
      var sd = el("section", "secao"); sd.id = "s-destaques";
      sd.appendChild(el("h2", "", "Destaques"));
      var tr = el("div", "destaques");
      destaques.forEach(function (p) {
        var d = el("article", "dest revela dir"); d.appendChild(foto(p));
        var tx = el("div", "dest-txt"); if (p.badge) tx.appendChild(el("span", "badge", p.badge));
        tx.appendChild(el("h3", "", p.name));
        var meta = el("div", "meta"); meta.appendChild(precoEl(p)); meta.appendChild(controle(p));
        tx.appendChild(meta); d.appendChild(tx); tr.appendChild(d);
      });
      sd.appendChild(tr); menu.appendChild(sd); secoes.push(["s-destaques", "Destaques"]);
    }
    var usadas = {};
    cats.forEach(function (c) {
      var itens = prods.filter(function (p) { return p.category_id === c.id; });
      if (!itens.length) return;
      usadas[c.id] = 1;
      var s = el("section", "secao"); s.id = "s-" + c.id;
      s.appendChild(el("h2", "", c.name));
      var l = el("div", "lista"); itens.forEach(function (p) { l.appendChild(cartao(p)); });
      s.appendChild(l); menu.appendChild(s); secoes.push([s.id, c.name]);
    });
    var soltos = prods.filter(function (p) { return !p.category_id || !usadas[p.category_id] && !cats.some(function (c) { return c.id === p.category_id; }); });
    if (soltos.length) {
      var so = el("section", "secao"); so.id = "s-outros"; so.appendChild(el("h2", "", "Mais opções"));
      var lo = el("div", "lista"); soltos.forEach(function (p) { lo.appendChild(cartao(p)); });
      so.appendChild(lo); menu.appendChild(so); secoes.push(["s-outros", "Mais opções"]);
    }
    if (!prods.length) menu.appendChild(el("p", "vazio", "O cardápio desta loja está sendo preparado. Volte em breve!"));
    secoes.forEach(function (s, i) {
      var b = el("button", "aba" + (i === 0 ? " ativa" : ""), s[1]); b.type = "button"; b.dataset.alvo = s[0];
      trilho.appendChild(b);
    });
    $("abas").hidden = secoes.length < 2;
    observaSecoes();
    if (window.BCEfeitos) window.BCEfeitos.revelar(menu);
  }
  var observador = null;
  function marcaAba(id) {
    var ativa = null;
    Array.prototype.forEach.call($("abasTrilho").children, function (b) { var on = b.dataset.alvo === id; b.classList.toggle("ativa", on); if (on) ativa = b; });
    if (ativa) { var t = $("abasTrilho"); t.scrollTo({ left: ativa.offsetLeft - 16, behavior: "smooth" }); }
  }
  function observaSecoes() {
    if (observador) observador.disconnect();
    if (!("IntersectionObserver" in window)) return;
    observador = new IntersectionObserver(function (ents) {
      ents.forEach(function (e) { if (e.isIntersecting) marcaAba(e.target.id); });
    }, { rootMargin: "-80px 0px -65% 0px" });
    Array.prototype.forEach.call(document.querySelectorAll(".secao"), function (s) { observador.observe(s); });
  }
  $("abasTrilho").addEventListener("click", function (e) {
    var b = e.target.closest("[data-alvo]"); if (!b) return;
    var s = document.getElementById(b.dataset.alvo); if (s) s.scrollIntoView({ behavior: "smooth", block: "start" });
    marcaAba(b.dataset.alvo);
  });

  /* ---------- carrinho ---------- */
  function salvaCarrinho() { lsSet("bc-carrinho-" + slug, carrinho); }
  function muda(id, d) {
    var p = porId[id]; if (!p) return;
    if (d > 0 && loja.accept_orders === false) { aviso("A loja pausou os pedidos agora."); return; }
    var n = Math.max(0, Math.min(99, qtd(id) + d));
    if (n) carrinho[id] = n; else delete carrinho[id];
    salvaCarrinho();
    Array.prototype.forEach.call(document.querySelectorAll('.ctrl[data-id="' + (window.CSS && CSS.escape ? CSS.escape(id) : id) + '"]'), function (b) { pintaControle(b, p); });
    atualizaBarra();
    if (!$("folha").hidden && passo === "carrinho") desenhaCarrinho();
    if (d > 0 && n === 1) aviso(p.name + " no pedido");
  }
  /* o item "voa" do botão até a barra do pedido, e a barra dá um pulinho */
  function voaParaSacola(origem, id) {
    var barra = $("barra"), parado = window.BCEfeitos && window.BCEfeitos.parado;
    if (barra.hidden) return;
    var pula = function () { barra.classList.remove("pula"); void barra.offsetWidth; barra.classList.add("pula"); };
    if (parado || !document.body.animate || !origem) return pula();
    var a = origem.getBoundingClientRect(), qtdEl = $("barraQtd").getBoundingClientRect();
    var p = porId[id], u = p && urlSegura(p.image_url);
    var bola = el("div", "voando");
    if (u) { var im = el("img"); im.alt = ""; im.src = u; bola.appendChild(im); } else bola.textContent = "+1";
    document.body.appendChild(bola);
    var x0 = a.left + a.width / 2 - 24, y0 = a.top + a.height / 2 - 24, x1 = qtdEl.left + qtdEl.width / 2 - 24, y1 = qtdEl.top + qtdEl.height / 2 - 24;
    var meio = Math.min(y0, y1) - 120;
    var anim = bola.animate([
      { transform: "translate(" + x0 + "px," + y0 + "px) scale(1)", opacity: 1 },
      { transform: "translate(" + (x0 + (x1 - x0) * 0.5) + "px," + meio + "px) scale(1.1)", opacity: 1, offset: 0.45 },
      { transform: "translate(" + x1 + "px," + y1 + "px) scale(.35)", opacity: 0.6 }
    ], { duration: 720, easing: "cubic-bezier(.45,.05,.55,.95)" });
    anim.onfinish = function () { bola.remove(); pula(); };
  }
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-mais],[data-menos]"); if (!b) return;
    if (b.dataset.mais) {
      var r = b.getBoundingClientRect(), fake = { getBoundingClientRect: function () { return r; } };
      var antes = qtd(b.dataset.mais); muda(b.dataset.mais, 1);
      if (qtd(b.dataset.mais) > antes && b.closest(".ctrl")) voaParaSacola(fake, b.dataset.mais);
    } else muda(b.dataset.menos, -1);
  });
  function itensCarrinho() {
    return Object.keys(carrinho).filter(function (id) { return porId[id] && carrinho[id] > 0; })
      .map(function (id) { return { p: porId[id], q: carrinho[id] }; });
  }
  function tipoEscolhido() {
    var r = document.querySelector('input[name="tipo"]:checked');
    if (r) return r.value;
    return loja.faz_entrega ? "entrega" : "retirada";
  }
  function contas() {
    var sub = 0, n = 0;
    itensCarrinho().forEach(function (i) { sub += i.p.price * i.q; n += i.q; });
    sub = r2(sub);
    var taxa = tipoEscolhido() === "entrega" ? r2(loja.delivery_fee) : 0;
    return { sub: sub, taxa: taxa, total: r2(sub + taxa), n: n };
  }
  function atualizaBarra() {
    var c = contas();
    var mostra = c.n > 0 && ($("folha").hidden);
    $("barra").hidden = !mostra;
    document.body.classList.toggle("com-barra", c.n > 0);
    $("barraQtd").textContent = String(c.n);
    $("barraTotal").textContent = brl(c.sub);
  }
  function resumo(alvo, comTaxa) {
    var c = contas(), box = $(alvo); box.textContent = "";
    function linha(a, b, cls) { var d = el("div", cls || ""); d.appendChild(el("span", "", a)); d.appendChild(el("span", "", b)); box.appendChild(d); }
    linha("Subtotal", brl(c.sub));
    if (comTaxa && tipoEscolhido() === "entrega") linha("Entrega", c.taxa > 0 ? brl(c.taxa) : "Grátis");
    linha("Total", brl(comTaxa ? c.total : c.sub), "total");
  }
  function desenhaCarrinho() {
    var box = $("linhas"); box.textContent = "";
    var itens = itensCarrinho();
    if (!itens.length) {
      box.appendChild(el("p", "vazio", "Seu pedido está vazio. Escolha algo no cardápio."));
    }
    itens.forEach(function (i) {
      var l = el("div", "linha");
      var t = el("div"); t.appendChild(el("b", "", i.p.name)); t.appendChild(el("small", "", brl(i.p.price) + (i.p.unit ? " · " + i.p.unit : "")));
      l.appendChild(t); l.appendChild(el("span", "valor", brl(i.p.price * i.q)));
      var c = el("div", "ctrl"); c.dataset.id = i.p.id; pintaControle(c, i.p); l.appendChild(c);
      box.appendChild(l);
    });
    resumo("resumoCarrinho", false);
    var c = contas(), nota = $("notaCarrinho"), btn = $("btnAvancar");
    nota.classList.remove("alerta");
    if (loja.accept_orders === false) { nota.textContent = "A loja pausou os pedidos pelo site agora. Chame no WhatsApp."; nota.classList.add("alerta"); btn.disabled = true; }
    else if (!c.n) { nota.textContent = ""; btn.disabled = true; }
    else if (loja.min_order > 0 && c.sub < loja.min_order) { nota.textContent = "Pedido mínimo: " + brl(loja.min_order) + ". Faltam " + brl(loja.min_order - c.sub) + "."; nota.classList.add("alerta"); btn.disabled = true; }
    else { nota.textContent = loja.faz_entrega && loja.delivery_fee > 0 ? "A taxa de entrega (" + brl(loja.delivery_fee) + ") entra no próximo passo, se escolher entrega." : ""; btn.disabled = false; }
  }

  /* ---------- folha do pedido ---------- */
  var focoAntes = null;
  function abreFolha(qual) {
    focoAntes = document.activeElement;
    document.documentElement.classList.add("trava");
    $("veu").hidden = false; $("folha").hidden = false; $("barra").hidden = true;
    $("aviso").classList.remove("mostra");
    vaiPara(qual || "carrinho");
  }
  function fechaFolha() {
    document.documentElement.classList.remove("trava");
    $("veu").hidden = true; $("folha").hidden = true;
    if (passo === "pronto") vaiPara("carrinho");
    atualizaBarra();
    if (focoAntes && focoAntes.focus) try { focoAntes.focus(); } catch (e) {}
  }
  function vaiPara(qual) {
    passo = qual;
    $("passoCarrinho").hidden = qual !== "carrinho";
    $("passoDados").hidden = qual !== "dados";
    $("passoPronto").hidden = qual !== "pronto";
    $("folhaVoltar").hidden = qual !== "dados";
    $("folhaPe").hidden = qual === "pronto";
    $("folhaTitulo").textContent = qual === "dados" ? "Seus dados" : qual === "pronto" ? "Tudo certo" : "Seu pedido";
    var btn = $("btnAvancar");
    if (qual === "carrinho") { btn.textContent = "Continuar"; desenhaCarrinho(); }
    if (qual === "dados") { preparaDados(); btn.disabled = false; btn.textContent = "Enviar pedido"; }
    $("folhaTitulo").focus({ preventScroll: true });
  }
  $("barra").addEventListener("click", function () { abreFolha("carrinho"); });
  $("veu").addEventListener("click", fechaFolha);
  $("folhaFechar").addEventListener("click", fechaFolha);
  $("folhaVoltar").addEventListener("click", function () { vaiPara("carrinho"); });
  $("okFechar").addEventListener("click", fechaFolha);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !$("folha").hidden) fechaFolha(); });
  $("btnAvancar").addEventListener("click", function () {
    if (passo === "carrinho") vaiPara("dados"); else if (passo === "dados") envia();
  });

  /* ---------- dados do cliente ---------- */
  function mascaraFone(v) {
    var d = digitos(v).slice(0, 11);
    if (d.length <= 2) return d ? "(" + d : "";
    if (d.length <= 6) return "(" + d.slice(0, 2) + ") " + d.slice(2);
    if (d.length <= 10) return "(" + d.slice(0, 2) + ") " + d.slice(2, 6) + "-" + d.slice(6);
    return "(" + d.slice(0, 2) + ") " + d.slice(2, 7) + "-" + d.slice(7);
  }
  $("fFone").addEventListener("input", function () { var f = $("fFone"); f.value = mascaraFone(f.value); });
  function preparaDados() {
    var salvo = lsGet("bc-cliente") || {};
    if (!$("fNome").value && salvo.nome) $("fNome").value = String(salvo.nome).slice(0, 80);
    if (!$("fFone").value && salvo.fone) $("fFone").value = mascaraFone(salvo.fone);
    if (!$("fEnd").value && salvo.end) $("fEnd").value = String(salvo.end).slice(0, 200);
    $("optEntrega").hidden = !loja.faz_entrega; $("optRetirada").hidden = !loja.faz_retirada;
    $("taxaTxt").textContent = loja.delivery_fee > 0 ? "+ " + brl(loja.delivery_fee) : "grátis";
    if (!document.querySelector('input[name="tipo"]:checked')) {
      var padrao = document.querySelector('input[name="tipo"][value="' + (loja.faz_entrega ? "entrega" : "retirada") + '"]');
      if (padrao) padrao.checked = true;
    }
    $("tipoBox").hidden = !(loja.faz_entrega && loja.faz_retirada);
    var box = $("pagOpcoes");
    if (!box.children.length) {
      loja.pagamentos.forEach(function (f, i) {
        var l = el("label", "opcao"), r = el("input"); r.type = "radio"; r.name = "pag"; r.value = f; if (i === 0) r.checked = true;
        l.appendChild(r); l.appendChild(el("span", "", f)); box.appendChild(l);
      });
    }
    trocaTipo();
    $("erroDados").textContent = "";
  }
  function trocaTipo() { $("campoEnd").hidden = tipoEscolhido() !== "entrega"; resumo("resumoDados", true); }
  $("passoDados").addEventListener("change", function (e) { if (e.target.name === "tipo") trocaTipo(); });
  $("passoDados").addEventListener("submit", function (e) { e.preventDefault(); envia(); });

  function marcaErro(campo, msg) {
    $("erroDados").textContent = msg;
    if (campo) { campo.classList.add("invalido"); campo.focus(); setTimeout(function () { campo.classList.remove("invalido"); }, 2500); }
  }

  /* ---------- envio ---------- */
  function mensagemZap(o, d) {
    var m = ["Olá, " + loja.store_name + "! Fiz o pedido *" + o.code + "* pelo site.", ""];
    (o.items || []).forEach(function (i) { m.push("• " + i.qty + "× " + i.name + " — " + brl(i.price * i.qty)); });
    m.push("");
    if (Number(o.delivery_fee) > 0) m.push("Entrega: " + brl(o.delivery_fee));
    m.push("Total: *" + brl(o.total) + "*");
    m.push(d.tipo === "entrega" ? "Entregar em: " + d.end : "Vou retirar na loja");
    if (d.quando) m.push("Para: " + d.quando);
    m.push("Pagamento: " + d.pag);
    m.push("Nome: " + d.nome + " · " + d.fone);
    if (d.obs) m.push("Obs.: " + d.obs);
    m.push("", "Acompanhe: " + siteBase() + "/pedido.html#" + o.track_token);
    return m.join("\n");
  }
  function abreJanela(w, url) {
    if (w && !w.closed) { try { w.opener = null; } catch (e) {} w.location.href = url; }
    else location.href = url;
  }
  function envia() {
    if (enviando) return;
    var nome = $("fNome").value.trim(), fone = $("fFone").value.trim(), tipo = tipoEscolhido();
    var end = $("fEnd").value.trim(), quando = $("fQuando").value.trim(), obs = $("fObs").value.trim();
    var pagEl = document.querySelector('input[name="pag"]:checked'), pag = pagEl ? pagEl.value : "";
    var itens = itensCarrinho(), c = contas();
    if (!itens.length) { vaiPara("carrinho"); return; }
    if (nome.length < 2) return marcaErro($("fNome"), "Informe seu nome.");
    if (digitos(fone).length < 10 || digitos(fone).length > 13) return marcaErro($("fFone"), "Informe seu WhatsApp com DDD.");
    if (tipo === "entrega" && end.length < 8) return marcaErro($("fEnd"), "Informe o endereço completo para entrega.");
    if (!pag) return marcaErro(null, "Escolha a forma de pagamento.");
    if (loja.min_order > 0 && c.sub < loja.min_order) return marcaErro(null, "Pedido mínimo: " + brl(loja.min_order) + ".");

    var pedido = {
      customer_name: nome, customer_phone: fone, delivery_type: tipo, address: tipo === "entrega" ? end : "",
      scheduled_for: quando, notes: obs, payment_method: pag, expected_total: c.total,
      items: itens.map(function (i) { return { product_id: i.p.id, qty: i.q }; })
    };
    var sig = JSON.stringify(pedido);
    if (idem.sig !== sig) idem = { sig: sig, chave: chaveNova() };
    lsSet("bc-cliente", { nome: nome, fone: digitos(fone), end: end });

    var zap = zapNumero(loja.whatsapp);
    var w = null;
    if (zap) { try { w = window.open("about:blank", "_blank"); } catch (e) { w = null; } }
    enviando = true;
    var btn = $("btnAvancar"); btn.disabled = true; btn.textContent = "Enviando…";
    $("erroDados").textContent = "";
    api("rpc/create_order", { method: "POST", body: JSON.stringify({ p_slug: slug, p_idem: idem.chave, p_order: pedido }) })
      .then(function (o) {
        var d = { tipo: tipo, end: end, quando: quando, pag: pag, nome: nome, fone: fone, obs: obs };
        ultimoPedido = o;
        idem = { sig: "", chave: "" };
        carrinho = {}; salvaCarrinho();
        Array.prototype.forEach.call(document.querySelectorAll(".ctrl"), function (b) { var p = porId[b.dataset.id]; if (p) pintaControle(b, p); });
        $("fObs").value = ""; $("fQuando").value = "";
        var rastreio = siteBase() + "/pedido.html#" + o.track_token;
        $("okCodigo").textContent = "Pedido " + o.code;
        $("okTxt").textContent = "Total " + brl(o.total) + ". " + (zap ? "Envie o resumo no WhatsApp para a loja confirmar mais rápido." : "A loja já recebeu o seu pedido.");
        $("okRastreio").href = rastreio;
        var link = zap ? "https://wa.me/" + zap + "?text=" + encodeURIComponent(mensagemZap(o, d)) : "";
        $("okZap").hidden = !zap; if (zap) $("okZap").href = link;
        vaiPara("pronto");
        atualizaBarra();
        if (w) abreJanela(w, link);
      })
      .catch(function (err) {
        if (w) try { w.close(); } catch (e) {}
        var msg = err && err.amigavel && err.message ? err.message : "Não conseguimos enviar o pedido agora. Ele NÃO foi enviado. Confira a internet e tente de novo.";
        if (err && (err.hint === "PRICE_CHANGED")) {
          carregaCardapio().then(function () { desenhaMenu(); atualizaBarra(); vaiPara("carrinho"); $("notaCarrinho").textContent = msg; $("notaCarrinho").classList.add("alerta"); }).catch(function () {});
          return;
        }
        if (/pausad|não está recebendo/i.test(msg)) { loja.accept_orders = false; montaLoja(); desenhaMenu(); }
        $("erroDados").textContent = msg;
      })
      .then(function () {
        enviando = false;
        if (passo === "dados") { btn.disabled = false; btn.textContent = "Enviar pedido"; }
      });
  }

  inicia();
})();
