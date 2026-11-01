/* Motor Bistrô Connect · liga o site premium ao banco da plataforma: dados da casa, cardápio, pedido e rastreio.
   Usa só a chave pública (anon) de window.BC e o identificador da loja em window.LOJA.slug (assets/config.js).
   Sem BC ou sem slug, MOTOR.ok = false e o site segue em modo demonstração (cardápio do próprio arquivo e WhatsApp).
   Fonte: paineis/motor/motor.js (copiado para assets/motor.js de cada site pelo gerador de clientes). */
(function () {
  "use strict";
  var BC = window.BC || {}, L = window.LOJA || {};
  var URL_ = String(BC.supabaseUrl || "").replace(/\/+$/, ""), CHAVE = String(BC.supabaseKey || ""), SLUG = String(L.slug || "").trim().toLowerCase();
  var ok = /^https:\/\/[a-z0-9-]+\.supabase\.co$/.test(URL_) && CHAVE.length > 20 && /^[a-z0-9][a-z0-9-]{1,58}[a-z0-9]$/.test(SLUG);
  var COLS = "id,slug,store_name,whatsapp,address,hours,instagram,cor,logo_url,capa_url,delivery_fee,min_order,accept_orders,faz_entrega,faz_retirada,pagamentos,extra,status";

  function api(caminho, op) {
    op = op || {};
    var h = { apikey: CHAVE, Authorization: "Bearer " + CHAVE, Accept: "application/json" };
    if (op.body) h["Content-Type"] = "application/json";
    return fetch(URL_ + "/rest/v1/" + caminho, { method: op.method || "GET", headers: h, body: op.body, cache: "no-store" }).then(function (r) {
      return r.text().then(function (t) {
        var j = null; try { j = t ? JSON.parse(t) : null; } catch (e) {}
        if (!r.ok) { var err = new Error((j && j.code === "P0001" && j.message) || ""); err.amigavel = !!(j && j.code === "P0001"); err.hint = j && j.hint; throw err; }
        return j;
      });
    });
  }

  var loja = null;
  /* carrega(): { loja, cats, prods }. loja.bairros = [{n, t}] quando a taxa é por bairro. */
  function carrega() {
    if (!ok) return Promise.reject(new Error("motor desligado"));
    return api("lojas?select=" + COLS + "&slug=eq." + encodeURIComponent(SLUG) + "&limit=1").then(function (r) {
      loja = r && r[0];
      if (!loja) throw new Error("loja não encontrada");
      loja.delivery_fee = Number(loja.delivery_fee) || 0; loja.min_order = Number(loja.min_order) || 0;
      var ex = loja.extra || {};
      loja.bairros = (Array.isArray(ex.bairros) ? ex.bairros : []).filter(function (b) { return b && typeof b.n === "string" && b.n.trim().length >= 2 && isFinite(Number(b.t)); }).map(function (b) { return { n: b.n.trim(), t: Number(b.t) }; });
      loja.pagamentos = Array.isArray(loja.pagamentos) && loja.pagamentos.length ? loja.pagamentos : ["Pix", "Cartão", "Dinheiro"];
      loja.aberta = loja.accept_orders !== false && (!loja.status || loja.status === "ativa");
      return Promise.all([
        api("categories?select=id,name,position&loja_id=eq." + loja.id + "&active=eq.true&order=position.asc,name.asc"),
        api("products?select=id,category_id,name,description,price,unit,image_url,featured,badge,position,opcoes,extra&loja_id=eq." + loja.id + "&active=eq.true&order=position.asc,name.asc")
      ]);
    }).then(function (r) {
      var prods = (r[1] || []).map(function (p) { p.price = Number(p.price) || 0; p.opcoes = Array.isArray(p.opcoes) ? p.opcoes : []; return p; });
      return { loja: loja, cats: r[0] || [], prods: prods };
    });
  }

  /* pedido(p): registra no banco. p = { customer_name, customer_phone, delivery_type ("entrega"|"retirada"), address,
     neighborhood, notes, payment_method, scheduled_for, coupon, expected_total, items: [{ product_id, qty, options }] }.
     Repetir o mesmo pedido (duplo clique, internet caindo) não cria outro: a chave de idempotência acompanha o conteúdo. */
  var idem = { sig: "", chave: "" };
  function chaveNova() { try { return crypto.randomUUID(); } catch (e) { return "k" + Date.now().toString(36) + Math.random().toString(36).slice(2, 12); } }
  function pedido(p) {
    if (!ok) return Promise.reject(new Error("motor desligado"));
    var sig = JSON.stringify(p);
    if (idem.sig !== sig) idem = { sig: sig, chave: chaveNova() };
    return api("rpc/create_order", { method: "POST", body: JSON.stringify({ p_slug: SLUG, p_idem: idem.chave, p_order: p }) }).then(function (o) {
      idem = { sig: "", chave: "" };
      return o;
    });
  }

  /* link de acompanhamento no domínio do próprio site: /p/<código> (curto, com prévia no WhatsApp) ou pedido.html#token */
  function base() { return String(BC.site || "").replace(/\/+$/, "") || new URL(".", location.href).href.replace(/\/+$/, ""); }
  function rastreio(o) {
    if (!o) return "";
    if (/^[a-f0-9]{16}$/.test(o.track_code || "")) return base() + "/p/" + o.track_code;
    if (/^[a-f0-9]{32,64}$/.test(o.track_token || "")) return base() + "/pedido.html#" + o.track_token;
    return "";
  }

  window.MOTOR = { ok: ok, slug: SLUG, carrega: carrega, pedido: pedido, rastreio: rastreio, api: api };
})();
