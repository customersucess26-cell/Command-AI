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

  /* se o loja.html no ar for de uma versão antiga, monta aqui o cabeçalho novo e troca o estilo, em vez de travar */
  (function garanteCasca() {
    var app = document.getElementById("app"); if (!app || document.getElementById("topo")) return;
    var topo = document.createElement("header"); topo.id = "topo"; topo.className = "topo";
    var faixa = document.createElement("div"); faixa.id = "capaFaixa"; faixa.className = "capa-faixa"; faixa.hidden = true;
    var capa = app.querySelector(".capa");
    if (capa) capa.parentNode.insertBefore(topo, capa); else app.insertBefore(topo, app.firstChild);
    topo.parentNode.insertBefore(faixa, topo.nextSibling);
    if (capa) capa.parentNode.removeChild(capa);
    var fm = app.querySelector(".faixa-marca"); if (fm) fm.parentNode.removeChild(fm);
    Array.prototype.forEach.call(document.querySelectorAll('link[href*="vitrine-temas.css"]'), function (l) { l.parentNode.removeChild(l); });
    function css(href) { var l = document.createElement("link"); l.rel = "stylesheet"; l.href = href; document.head.appendChild(l); }
    if (!document.querySelector('link[href*="loja-modelos.css"]')) css("/assets/loja-modelos.css");
    css("https://fonts.googleapis.com/css2?family=Oswald:wght@500;600&family=Yellowtail&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&display=swap");
    var bt = document.querySelector(".barra-txt"); if (bt) bt.textContent = "Finalizar pedido";
  })();

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
      api("products?select=id,category_id,name,description,price,unit,image_url,featured,badge,position,opcoes&loja_id=eq." + loja.id + "&active=eq.true&order=position.asc,name.asc")
    ]).then(function (r) {
      cats = r[0] || []; prods = r[1] || []; porId = {};
      prods.forEach(function (p) { p.price = Number(p.price) || 0; p.opcoes = Array.isArray(p.opcoes) ? p.opcoes : []; porId[p.id] = p; });
      var mudou = false;
      Object.keys(carrinho).forEach(function (k) { if (!linhaCarrinho(k, 1)) { delete carrinho[k]; mudou = true; } });
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
  /* cada tipo de loja usa um dos 4 modelos da página de vendas: grade (padaria), café, hambúrguer e pratos (restaurante) */
  var LAYOUTS = { padaria: "grid", doceria: "grid", cafeteria: "cafe", hamburgueria: "burger", pizzaria: "burger", restaurante: "plates", outro: "plates" };
  var FUNDO_TEMA = { grid: "#231710", cafe: "#2A1A12", burger: "#121212", plates: "#FBF8F3" };
  var layout = "plates", catAtual = "";
  var SVG_MENU = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>';
  var SVG_SACOLA = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 8h12l-1 12H7z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg>';
  function iniciaisDe(nome) {
    /* iniciais sem "da", "de", "do"…: "Doceria da Marina" vira DM */
    var palavras = String(nome || "?").split(/\s+/).filter(Boolean);
    var fortes = palavras.filter(function (x) { return !/^(d[aeo]s?|e|&|a|o|na|no)$/i.test(x); });
    return (fortes.length ? fortes : palavras).slice(0, 2).map(function (x) { return x[0]; }).join("").toUpperCase();
  }
  function logoEl(cls) {
    var l = el("div", cls); l.setAttribute("aria-hidden", "true");
    var lu = urlSegura(loja.logo_url), ini = iniciaisDe(loja.store_name);
    if (lu) { var il = el("img"); il.alt = ""; il.src = lu; il.addEventListener("error", function () { l.textContent = ini; }); l.appendChild(il); }
    else l.textContent = ini;
    return l;
  }
  function montaLoja() {
    var modelo = LAYOUTS[loja.modelo] ? loja.modelo : "outro";
    layout = LAYOUTS[modelo];
    document.body.className = "lm-" + layout;
    /* cor da marca própria da loja: troca o destaque do modelo (a cor padrão da plataforma mantém o do modelo) */
    var raiz = document.documentElement.style;
    ["--cor", "--cor-txt", "--on", "--on-ink", "--bar", "--bar-ink"].forEach(function (v) { raiz.removeProperty(v); });
    if (/^#[0-9a-f]{6}$/i.test(loja.cor || "") && !/^#b0703f$/i.test(loja.cor)) {
      var viva = (layout === "grid" || layout === "plates") ? loja.cor : clareia(loja.cor), tx = corTexto(viva);
      raiz.setProperty("--cor", viva); raiz.setProperty("--cor-txt", tx); raiz.setProperty("--on", viva); raiz.setProperty("--on-ink", tx);
      raiz.setProperty("--bar", viva); raiz.setProperty("--bar-ink", tx);
    }
    var meta = document.querySelector('meta[name="theme-color"]'); if (meta) meta.setAttribute("content", FUNDO_TEMA[layout]);
    document.title = loja.store_name + " · Cardápio";

    var aberta = loja.accept_orders !== false;
    var topo = $("topo"); topo.textContent = ""; topo.className = "topo topo-" + layout;
    if (layout === "grid") {
      var bar = el("div", "t-bar");
      var bi = el("button", "t-ico"); bi.type = "button"; bi.id = "btnInfo"; bi.setAttribute("aria-label", "Horário, endereço e contato"); bi.innerHTML = SVG_MENU;
      bi.addEventListener("click", function () { var t = $("s-visite"); if (t) t.scrollIntoView({ behavior: "smooth", block: "start" }); });
      var bs = el("button", "t-ico round"); bs.type = "button"; bs.id = "btnSacola"; bs.setAttribute("aria-label", "Ver pedido"); bs.innerHTML = SVG_SACOLA;
      var bd = el("span", "t-badge", "0"); bd.id = "sacolaBadge"; bd.hidden = true; bs.appendChild(bd);
      bs.addEventListener("click", function () { abreFolha("carrinho"); });
      bar.appendChild(bi); bar.appendChild(logoEl("t-logo")); bar.appendChild(bs);
      topo.appendChild(bar);
    }
    var cab = el("div", "t-head");
    if (layout !== "grid") cab.appendChild(logoEl("t-logo"));
    cab.appendChild(el("p", "t-etiqueta", ETIQUETAS[modelo]));
    var h1 = el("h1", "t-nome", loja.store_name); h1.id = "nome"; cab.appendChild(h1);
    if (loja.descricao) cab.appendChild(el("p", "t-desc", loja.descricao));
    var selo = el("span", "selo" + (aberta ? "" : " fechada"), aberta ? "Recebendo pedidos" : "Pedidos pausados"); cab.appendChild(selo);
    topo.appendChild(cab);
    $("pausa").hidden = aberta;

    /* capa enviada pela loja: faixa de foto logo abaixo do topo */
    var fx = $("capaFaixa"); fx.textContent = ""; var capa = urlSegura(loja.capa_url); fx.hidden = !capa;
    if (capa) { var ic = el("img"); ic.alt = ""; ic.src = capa; ic.decoding = "async"; ic.addEventListener("error", function () { fx.hidden = true; }); fx.appendChild(ic); }

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
  function baseId(k) { return String(k).split("|")[0]; }
  function temOpc(p) { return !!(p && p.opcoes && p.opcoes.length); }
  /* quantas unidades do produto estão no pedido, somando todas as combinações de opções */
  function qtdProduto(pid) {
    var n = 0; Object.keys(carrinho).forEach(function (k) { if (baseId(k) === pid) n += carrinho[k]; });
    return n;
  }
  /* resolve uma chave do carrinho: produto, opções escolhidas e preço unitário. null se algo saiu do cardápio */
  function linhaCarrinho(k, q) {
    var p = porId[baseId(k)]; if (!p) return null;
    var sel = String(k).split("|")[1], ops = [], unit = p.price;
    if (sel) {
      var ok = sel.split(",").every(function (par) {
        var gi = par.split(":"), g = null, it = null;
        p.opcoes.forEach(function (x) { if (x.id === gi[0]) g = x; });
        if (g) (g.itens || []).forEach(function (y) { if (y.id === gi[1]) it = y; });
        if (!g || !it) return false;
        ops.push({ g: g.id, o: it.id, grupo: g.nome, nome: it.nome, preco: Number(it.preco) || 0 });
        unit += Number(it.preco) || 0; return true;
      });
      if (!ok) return null;
      var ordem = function (o) { var i = 0; p.opcoes.forEach(function (g, n) { if (g.id === o.g) i = n; }); return i; };
      ops.sort(function (x, y) { return ordem(x) - ordem(y); });
    }
    return { key: k, p: p, q: q, ops: ops, unit: r2(unit) };
  }
  function controle(p, comTexto) {
    var box = el("div", "ctrl" + (!comTexto && (layout === "cafe" || layout === "burger") ? " round" : "")); box.dataset.id = p.id;
    pintaControle(box, p, p.id, false);
    return box;
  }
  /* linha = true dentro do pedido (sempre com − e +); no cardápio, produto com opções abre a escolha */
  function pintaControle(box, p, key, linha) {
    key = key || p.id; box.textContent = ""; if (linha) box.dataset.linha = "1";
    var aberta = loja.accept_orders !== false;
    var redondo = !linha && box.classList.contains("round");
    if (!linha && temOpc(p)) {
      var n0 = qtdProduto(p.id);
      var bo = el("button", "add", redondo ? "+" : n0 ? "Adicionar (" + n0 + ")" : "Escolher"); bo.type = "button"; bo.dataset.opc = p.id;
      if (redondo && n0) bo.dataset.n = String(n0);
      bo.setAttribute("aria-label", "Escolher opções de " + p.name); bo.disabled = !aberta;
      box.appendChild(bo); return;
    }
    var q = qtd(key);
    if (!q) {
      var b = el("button", "add", redondo ? "+" : "Adicionar"); b.type = "button"; b.dataset.mais = key;
      b.setAttribute("aria-label", "Adicionar " + p.name); b.disabled = !aberta;
      box.appendChild(b);
    } else {
      var s = el("div", "passo" + (q === 1 ? " novo" : ""));
      var m = el("button", "", "−"); m.type = "button"; m.dataset.menos = key; m.setAttribute("aria-label", "Tirar um " + p.name);
      var n = el("span", "", String(q)); n.setAttribute("aria-live", "polite");
      var mais = el("button", "", "+"); mais.type = "button"; mais.dataset.mais = key; mais.setAttribute("aria-label", "Mais um " + p.name);
      s.appendChild(m); s.appendChild(n); s.appendChild(mais); box.appendChild(s);
    }
  }
  function repintaControles() {
    Array.prototype.forEach.call(document.querySelectorAll(".ctrl"), function (b) {
      var p = porId[baseId(b.dataset.id)]; if (p) pintaControle(b, p, b.dataset.id, !!b.dataset.linha);
    });
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
  function etiquetaFoto(p) { return p.badge ? el("span", "m-tag", p.badge) : null; }
  function fotoCartao(p, extra) {
    var f = foto(p, "foto pic" + (extra ? " " + extra : "")), t = etiquetaFoto(p); if (t) f.appendChild(t); return f;
  }
  function cartaoGrade(p) {
    var c = el("article", "m-card revela");
    c.appendChild(fotoCartao(p));
    c.appendChild(el("h3", "m-name", p.name));
    c.appendChild(el("p", "m-desc", p.description || ""));
    c.appendChild(el("hr"));
    c.appendChild(el("p", "m-unit", p.unit || "Unidade"));
    c.appendChild(el("p", "m-price", brl(p.price)));
    c.appendChild(controle(p));
    return c;
  }
  function cartaoPrato(p) {
    var c = el("article", "m-plate revela");
    c.appendChild(fotoCartao(p, "redonda"));
    c.appendChild(el("h3", "m-name", p.name));
    c.appendChild(el("p", "m-desc", p.description || ""));
    c.appendChild(el("p", "m-price", brl(p.price) + (p.unit ? " · " + p.unit : "")));
    c.appendChild(controle(p));
    return c;
  }
  function cartaoLinha(p) {
    var c = el("article", "m-row revela");
    c.appendChild(fotoCartao(p));
    var t = el("div", "t");
    t.appendChild(el("h3", "m-name", p.name));
    if (p.description) t.appendChild(el("p", "m-desc", p.description));
    var meta = el("div", "meta"), pr = el("span", "m-preco");
    pr.appendChild(el("b", "m-price", brl(p.price))); if (p.unit) pr.appendChild(el("small", "m-w", p.unit));
    meta.appendChild(pr); meta.appendChild(controle(p)); t.appendChild(meta); c.appendChild(t);
    return c;
  }
  function cartao(p) { return layout === "grid" ? cartaoGrade(p) : layout === "plates" ? cartaoPrato(p) : cartaoLinha(p); }

  /* categorias com produto; produto sem categoria vai para "Mais opções" */
  function listaCategorias() {
    var out = [], usadas = {};
    cats.forEach(function (c) {
      var it = prods.filter(function (p) { return p.category_id === c.id; });
      if (it.length) { out.push({ id: c.id, nome: c.name, itens: it }); usadas[c.id] = 1; }
    });
    var soltos = prods.filter(function (p) { return !p.category_id || !usadas[p.category_id] && !cats.some(function (c) { return c.id === p.category_id; }); });
    if (soltos.length) out.push({ id: "outros", nome: "Mais opções", itens: soltos });
    return out;
  }
  function blocoCategoria(c, primeira) {
    var box = el("section", "secao-cat"); box.id = "s-" + c.id;
    var itens = c.itens.slice();
    if (layout === "cafe") {
      /* prateleira: até 3 itens em destaque com foto, como no modelo café */
      var dest = itens.filter(function (p) { return p.featured && urlSegura(p.image_url); }).slice(0, 3);
      /* sem destaques marcados, a primeira aba mostra os 3 primeiros itens com foto */
      if (dest.length < 2 && primeira) dest = itens.filter(function (p) { return urlSegura(p.image_url); }).slice(0, 3);
      if (dest.length >= 2 && itens.length > dest.length) {
        var sh = el("div", "m-shelf");
        dest.forEach(function (p) {
          var it = el("article", "it revela"); it.appendChild(fotoCartao(p));
          it.appendChild(el("h3", "m-name", p.name)); it.appendChild(el("p", "m-price", brl(p.price))); it.appendChild(controle(p, true)); sh.appendChild(it);
        });
        box.appendChild(sh);
        itens = itens.filter(function (p) { return dest.indexOf(p) < 0; });
        if (itens.length) box.appendChild(el("h2", "m-section", "Especiais da casa"));
      }
    }
    var cls = layout === "grid" ? "m-grid" : layout === "plates" ? "m-plates" : "m-rows";
    var l = el("div", cls); itens.forEach(function (p) { l.appendChild(cartao(p)); });
    box.appendChild(l);
    return box;
  }
  function desenhaMenu() {
    var menu = $("menu"), trilho = $("abasTrilho");
    menu.textContent = ""; trilho.textContent = "";
    var lista = listaCategorias();
    if (!lista.length) {
      menu.appendChild(el("p", "vazio", "O cardápio desta loja está sendo preparado. Volte em breve!"));
      $("abas").hidden = true; desenhaSecoes(); return;
    }
    if (!lista.some(function (c) { return c.id === catAtual; })) catAtual = lista[0].id;
    var atual = null;
    lista.forEach(function (c) {
      var on = c.id === catAtual; if (on) atual = c;
      var b = el("button", "aba" + (on ? " ativa" : ""), c.nome); b.type = "button"; b.dataset.cat = c.id; b.setAttribute("aria-pressed", on ? "true" : "false");
      trilho.appendChild(b);
    });
    $("abas").hidden = lista.length < 2;
    menu.appendChild(blocoCategoria(atual, lista[0].id === atual.id));
    desenhaSecoes();
    if (window.BCEfeitos) { window.BCEfeitos.revelar(menu); window.BCEfeitos.revelar($("secoes")); }
  }
  /* ---------- seções da página: como pedir, sobre, galeria, depoimentos, visite e chamada final ----------
     O texto e as fotos vêm do painel (Dados da loja > Páginas do site), guardados em loja.extra.secoes.
     O que o dono não preencher usa um texto padrão neutro, ou a seção simplesmente não aparece. */
  function secaoEl(id, titulo, classe) {
    var s = el("section", "secao bloco " + (classe || "")); s.id = id;
    s.appendChild(el("h2", "", titulo)); return s;
  }
  function desenhaSecoes() {
    var box = $("secoes"); box.textContent = "";
    var conf = (loja.extra && loja.extra.secoes) || {}, nome = loja.store_name;

    /* como pedir */
    var c = secaoEl("s-como", "Como pedir", "como"), g = el("ol", "como-lista");
    [["Escolha", "Monte o pedido no cardápio, direto pelo celular."], ["Informe", "Diga como quer receber e como vai pagar."], ["Acompanhe", "O pedido chega pronto na loja e você acompanha o status."]]
      .forEach(function (x, i) { var li = el("li"); li.appendChild(el("span", "num", String(i + 1))); li.appendChild(el("b", "", x[0])); li.appendChild(el("p", "", x[1])); g.appendChild(li); });
    c.appendChild(g); box.appendChild(c);

    /* sobre */
    var so = conf.sobre || {};
    var texto = String(so.texto || "").trim() || (loja.descricao ? loja.descricao : "Conheça a " + nome + ". Montamos o cardápio com carinho para você pedir pelo celular e receber em casa ou retirar na loja.");
    var sb = secaoEl("s-sobre", String(so.titulo || "").trim() || "Sobre a " + nome, "sobre" + (urlSegura(so.foto) ? " com-foto" : ""));
    var corpo = el("div", "sobre-corpo");
    if (urlSegura(so.foto)) { var f = el("div", "sobre-foto"), im = el("img"); im.alt = nome; im.loading = "lazy"; im.decoding = "async"; im.src = urlSegura(so.foto); f.appendChild(im); corpo.appendChild(f); }
    var tx = el("div", "sobre-txt"); texto.split(/\n+/).slice(0, 6).forEach(function (par) { if (par.trim()) tx.appendChild(el("p", "", par.trim())); });
    corpo.appendChild(tx); sb.appendChild(corpo); box.appendChild(sb);

    /* galeria: fotos do dono; sem fotos, as dos produtos */
    var fotos = ((conf.galeria && conf.galeria.fotos) || []).map(urlSegura).filter(Boolean).slice(0, 8), auto = false;
    if (!fotos.length) {
      var vistos = {}; prods.forEach(function (p) { var u = urlSegura(p.image_url); if (u && !vistos[u] && fotos.length < 6) { vistos[u] = 1; fotos.push(u); } });
      auto = true; if (fotos.length < 3) fotos = [];
    }
    if (fotos.length) {
      var ga = secaoEl("s-galeria", auto ? "Uma volta pelo cardápio" : "Galeria", "galeria"), gr = el("div", "galeria-grade n" + Math.min(fotos.length, 6));
      fotos.forEach(function (u, i) { var d = el("div", "gfoto"), im2 = el("img"); im2.alt = nome + " · foto " + (i + 1); im2.loading = "lazy"; im2.decoding = "async"; im2.src = u; d.appendChild(im2); gr.appendChild(d); });
      ga.appendChild(gr); box.appendChild(ga);
    }

    /* depoimentos: só os que o dono cadastrou */
    var deps = ((conf.depoimentos && conf.depoimentos.itens) || []).filter(function (d) { return d && String(d.texto || "").trim(); }).slice(0, 6);
    if (deps.length) {
      var de = secaoEl("s-depoimentos", "Quem pede, volta", "depoimentos"), lista = el("div", "depo-lista");
      deps.forEach(function (d) { var q = el("blockquote", "depo"); q.appendChild(el("p", "", String(d.texto).trim().slice(0, 240))); if (String(d.nome || "").trim()) q.appendChild(el("footer", "", "— " + String(d.nome).trim().slice(0, 60))); lista.appendChild(q); });
      de.appendChild(lista); box.appendChild(de);
    }

    /* visite ou peça */
    var linhas = [], zap = zapNumero(loja.whatsapp), insta = String(loja.instagram || "").replace(/^@/, "").replace(/[^A-Za-z0-9._]/g, "").slice(0, 40);
    if (loja.address) linhas.push(["Endereço", loja.address]);
    if (loja.hours) linhas.push(["Horário", loja.hours]);
    var como = [loja.faz_entrega ? "Entrega" + (loja.delivery_fee > 0 ? " (" + brl(loja.delivery_fee) + ")" : " grátis") : "", loja.faz_retirada ? "Retirada na loja" : ""].filter(Boolean).join(" · ");
    if (como) linhas.push(["Como receber", como]);
    linhas.push(["Pagamento", loja.pagamentos.join(" · ")]);
    var vi = secaoEl("s-visite", "Visite ou peça", "visite"), lv = el("dl", "visite-lista");
    linhas.forEach(function (l) { var d1 = el("div"); d1.appendChild(el("dt", "", l[0])); d1.appendChild(el("dd", "", l[1])); lv.appendChild(d1); });
    vi.appendChild(lv);
    var bt = el("div", "visite-botoes");
    if (loja.address) { var m = el("a", "btn-sec", "Ver no mapa"); m.href = "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(loja.address); m.target = "_blank"; m.rel = "noopener noreferrer"; bt.appendChild(m); }
    if (zap) { var w = el("a", "btn-sec zap", "Chamar no WhatsApp"); w.href = "https://wa.me/" + zap; w.target = "_blank"; w.rel = "noopener noreferrer"; bt.appendChild(w); }
    if (insta) { var ig = el("a", "btn-sec", "@" + insta); ig.href = "https://www.instagram.com/" + insta; ig.target = "_blank"; ig.rel = "noopener noreferrer"; bt.appendChild(ig); }
    if (bt.children.length) vi.appendChild(bt);
    box.appendChild(vi);

    /* chamada final */
    if (prods.length) {
      var fim = el("section", "secao bloco final"); fim.id = "s-final";
      fim.appendChild(el("h2", "", "Bateu a fome?")); fim.appendChild(el("p", "", "Escolha no cardápio e peça em poucos toques."));
      var bb = el("button", "add grande", "Ver o cardápio"); bb.type = "button";
      bb.addEventListener("click", function () { var t = $("abas").hidden ? $("menu") : $("abas"); t.scrollIntoView({ behavior: "smooth", block: "start" }); });
      fim.appendChild(bb); box.appendChild(fim);
    }
  }
  $("abasTrilho").addEventListener("click", function (e) {
    var b = e.target.closest("[data-cat]"); if (!b || b.dataset.cat === catAtual) return;
    catAtual = b.dataset.cat; desenhaMenu();
    var y = $("abas").getBoundingClientRect().top + window.scrollY;
    if (window.scrollY > y) window.scrollTo({ top: y, behavior: "smooth" });
    var ativa = $("abasTrilho").querySelector(".ativa"); if (ativa) $("abasTrilho").scrollTo({ left: ativa.offsetLeft - 16, behavior: "smooth" });
  });

  /* ---------- carrinho ---------- */
  function salvaCarrinho() { lsSet("bc-carrinho-" + slug, carrinho); }
  function muda(id, d) {
    var p = porId[baseId(id)]; if (!p) return;
    if (d > 0 && loja.accept_orders === false) { aviso("A loja pausou os pedidos agora."); return; }
    var n = Math.max(0, Math.min(99, qtd(id) + d));
    if (n) carrinho[id] = n; else delete carrinho[id];
    salvaCarrinho();
    repintaControles();
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
    var p = porId[baseId(id)], u = p && urlSegura(p.image_url);
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
    var b = e.target.closest("[data-mais],[data-menos],[data-opc]"); if (!b) return;
    if (b.dataset.opc) { abreOpc(b.dataset.opc, b); return; }
    if (b.dataset.mais) {
      var r = b.getBoundingClientRect(), fake = { getBoundingClientRect: function () { return r; } };
      var antes = qtd(b.dataset.mais); muda(b.dataset.mais, 1);
      if (qtd(b.dataset.mais) > antes && b.closest(".ctrl")) voaParaSacola(fake, b.dataset.mais);
    } else muda(b.dataset.menos, -1);
  });
  function itensCarrinho() {
    return Object.keys(carrinho).filter(function (k) { return carrinho[k] > 0; })
      .map(function (k) { return linhaCarrinho(k, carrinho[k]); }).filter(Boolean);
  }
  function tipoEscolhido() {
    var r = document.querySelector('input[name="tipo"]:checked');
    if (r) return r.value;
    return loja.faz_entrega ? "entrega" : "retirada";
  }
  function contas() {
    var sub = 0, n = 0;
    itensCarrinho().forEach(function (i) { sub += i.unit * i.q; n += i.q; });
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
    var sb = $("sacolaBadge"); if (sb) { sb.textContent = String(c.n); sb.hidden = !c.n; }
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
      var t = el("div"); t.appendChild(el("b", "", i.p.name));
      if (i.ops.length) t.appendChild(el("small", "opc-resumo", i.ops.map(function (o) { return o.nome; }).join(", ")));
      t.appendChild(el("small", "", brl(i.unit) + (i.p.unit ? " · " + i.p.unit : "")));
      l.appendChild(t); l.appendChild(el("span", "valor", brl(i.unit * i.q)));
      var c = el("div", "ctrl"); c.dataset.id = i.key; pintaControle(c, i.p, i.key, true); l.appendChild(c);
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
  /* mensagem do pedido para o WhatsApp da loja. Só texto e símbolos comuns (sem emoji): alguns celulares trocam emoji por "�".
     O link de acompanhamento não vai aqui: o cliente vê na tela "Pedido recebido" e a loja manda pelo painel. */
  function mensagemZap(o, d) {
    var m = ["Olá, " + loja.store_name + "!", "Fiz o pedido *" + o.code + "* pelo site.", "", "*ITENS DO PEDIDO*"];
    (o.items || []).forEach(function (i) {
      m.push("• " + i.qty + "× " + i.name + " — " + brl(i.price * i.qty));
      var ops = (i.options || []).map(function (x) { return x.name; });
      if (ops.length) m.push("   ↳ " + ops.join(", "));
    });
    m.push("");
    if (Number(o.delivery_fee) > 0) m.push("Entrega: " + brl(o.delivery_fee));
    m.push("*TOTAL: " + brl(o.total) + "*", "");
    m.push(d.tipo === "entrega" ? "*Entregar em:* " + d.end : "*Retirada* na loja");
    if (d.quando) m.push("*Para:* " + d.quando);
    m.push("*Pagamento:* " + d.pag);
    m.push("*Cliente:* " + d.nome + " · " + d.fone);
    if (d.obs) m.push("*Obs.:* " + d.obs);
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
      items: itens.map(function (i) { var x = { product_id: i.p.id, qty: i.q }; if (i.ops.length) x.options = i.ops.map(function (o) { return { g: o.g, o: o.o }; }); return x; })
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
        repintaControles();
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

  /* ---------- opções do produto (ponto da carne, adicionais, tamanho) ---------- */
  var opc = null, opcFoco = null;
  function opcDom() {
    if ($("opcFolha")) return;
    var veu = el("div", "opc-veu"); veu.id = "opcVeu"; veu.hidden = true;
    var f = el("div", "opc-folha"); f.id = "opcFolha"; f.hidden = true;
    f.setAttribute("role", "dialog"); f.setAttribute("aria-modal", "true"); f.setAttribute("aria-labelledby", "opcTitulo");
    var topo = el("div", "opc-topo"), h = el("h2"); h.id = "opcTitulo"; h.tabIndex = -1;
    var x = el("button", "opc-x", "×"); x.type = "button"; x.id = "opcFecha"; x.setAttribute("aria-label", "Fechar");
    topo.appendChild(h); topo.appendChild(x);
    var corpo = el("div", "opc-corpo"); corpo.id = "opcCorpo";
    var pe = el("div", "opc-pe"), passo = el("div", "passo"); passo.id = "opcPasso";
    var menos = el("button", "", "−"); menos.type = "button"; menos.id = "opcMenos"; menos.setAttribute("aria-label", "Menos um");
    var n = el("span", "", "1"); n.id = "opcQtd"; n.setAttribute("aria-live", "polite");
    var mais = el("button", "", "+"); mais.type = "button"; mais.id = "opcMais"; mais.setAttribute("aria-label", "Mais um");
    passo.appendChild(menos); passo.appendChild(n); passo.appendChild(mais);
    var add = el("button", "opc-add", "Adicionar"); add.type = "button"; add.id = "opcAdd";
    pe.appendChild(passo); pe.appendChild(add);
    f.appendChild(topo); f.appendChild(corpo); f.appendChild(pe);
    document.body.appendChild(veu); document.body.appendChild(f);
    veu.addEventListener("click", fechaOpc); x.addEventListener("click", fechaOpc);
    menos.addEventListener("click", function () { if (opc && opc.q > 1) { opc.q--; opcAtualiza(); } });
    mais.addEventListener("click", function () { if (opc && opc.q < 99) { opc.q++; opcAtualiza(); } });
    add.addEventListener("click", opcAdiciona);
    corpo.addEventListener("click", function (e) {
      var b = e.target.closest("[data-og]"); if (!b || !opc) return;
      var g = grupoPorId(b.dataset.og), oid = b.dataset.oo, sel = opc.sel[g.id] || (opc.sel[g.id] = []);
      var i = sel.indexOf(oid), max = Number(g.max) || 1;
      if (max === 1) { opc.sel[g.id] = i >= 0 ? (Number(g.min) >= 1 ? sel : []) : [oid]; }
      else if (i >= 0) sel.splice(i, 1);
      else if (sel.length >= max) { aviso("Escolha até " + max + " em " + g.nome + "."); return; }
      else sel.push(oid);
      opcDesenha(false);
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !f.hidden) fechaOpc(); });
  }
  function grupoPorId(id) { var r = null; opc.p.opcoes.forEach(function (g) { if (g.id === id) r = g; }); return r; }
  function opcSoma() {
    var s = opc.p.price;
    opc.p.opcoes.forEach(function (g) { (opc.sel[g.id] || []).forEach(function (oid) { (g.itens || []).forEach(function (it) { if (it.id === oid) s += Number(it.preco) || 0; }); }); });
    return r2(s);
  }
  function opcAtualiza() { $("opcQtd").textContent = String(opc.q); $("opcAdd").textContent = "Adicionar · " + brl(opcSoma() * opc.q); }
  function opcDesenha(zeraRolagem) {
    var corpo = $("opcCorpo"), rolou = corpo.scrollTop; corpo.textContent = "";
    var p = opc.p;
    if (p.description) corpo.appendChild(el("p", "opc-desc", p.description));
    p.opcoes.forEach(function (g) {
      var sec = el("section", "opc-grupo"); sec.dataset.g = g.id;
      var cab = el("div", "opc-gcab"), t = el("b", "", g.nome), max = Number(g.max) || 1, min = Number(g.min) || 0;
      var sub = min >= 1 ? (max === 1 ? "Escolha 1 · obrigatório" : "Escolha de " + min + " a " + max + " · obrigatório") : (max === 1 ? "Opcional · escolha 1" : "Opcional · até " + max);
      cab.appendChild(t); cab.appendChild(el("span", "opc-gsub" + (min >= 1 ? " obrig" : ""), sub)); sec.appendChild(cab);
      (g.itens || []).forEach(function (it) {
        var on = (opc.sel[g.id] || []).indexOf(it.id) >= 0;
        var b = el("button", "opc-item" + (on ? " on" : "")); b.type = "button"; b.dataset.og = g.id; b.dataset.oo = it.id;
        b.setAttribute("role", max === 1 ? "radio" : "checkbox"); b.setAttribute("aria-checked", on ? "true" : "false");
        b.appendChild(el("span", "opc-marca" + (max === 1 ? " redondo" : ""))); b.appendChild(el("span", "opc-nome", it.nome));
        if (Number(it.preco) > 0) b.appendChild(el("span", "opc-preco", "+ " + brl(it.preco)));
        sec.appendChild(b);
      });
      corpo.appendChild(sec);
    });
    corpo.scrollTop = zeraRolagem ? 0 : rolou;
    opcAtualiza();
  }
  function abreOpc(pid, origem) {
    var p = porId[pid]; if (!p) return;
    if (loja.accept_orders === false) { aviso("A loja pausou os pedidos agora."); return; }
    opcDom(); opcFoco = origem || document.activeElement;
    opc = { p: p, sel: {}, q: 1, origem: origem };
    $("opcTitulo").textContent = p.name;
    opcDesenha(true);
    $("opcVeu").hidden = false; $("opcFolha").hidden = false;
    document.documentElement.classList.add("trava");
    $("opcTitulo").focus({ preventScroll: true });
  }
  function fechaOpc() {
    if (!$("opcFolha")) return;
    $("opcVeu").hidden = true; $("opcFolha").hidden = true; opc = null;
    if (!$("folha") || $("folha").hidden) document.documentElement.classList.remove("trava");
    if (opcFoco && opcFoco.focus) try { opcFoco.focus(); } catch (e) {}
  }
  function opcAdiciona() {
    if (!opc) return;
    var p = opc.p, falta = null;
    p.opcoes.forEach(function (g) { if (!falta && (opc.sel[g.id] || []).length < (Number(g.min) || 0)) falta = g; });
    if (falta) {
      var sec = $("opcCorpo").querySelector('[data-g="' + falta.id + '"]');
      if (sec) { sec.classList.add("falta"); sec.scrollIntoView({ block: "center", behavior: "smooth" }); setTimeout(function () { sec.classList.remove("falta"); }, 1800); }
      aviso("Escolha " + falta.nome.toLowerCase() + " para continuar.");
      return;
    }
    var pares = [];
    p.opcoes.forEach(function (g) { (opc.sel[g.id] || []).forEach(function (oid) { pares.push(g.id + ":" + oid); }); });
    var chave = pares.length ? p.id + "|" + pares.sort().join(",") : p.id;
    var q = Math.min(99, qtd(chave) + opc.q), origem = opc.origem, id = p.id;
    carrinho[chave] = q; salvaCarrinho();
    fechaOpc(); repintaControles(); atualizaBarra();
    if (!$("folha").hidden && passo === "carrinho") desenhaCarrinho();
    aviso(p.name + " no pedido");
    if (origem && origem.getBoundingClientRect) { var r = origem.getBoundingClientRect(); voaParaSacola({ getBoundingClientRect: function () { return r; } }, id); }
  }

  inicia();
})();
