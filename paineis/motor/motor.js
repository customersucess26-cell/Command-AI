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
      /* fotos cadastradas com caminho da plataforma (ex.: /assets/img/exemplo/...) passam a apontar para o endereço dela */
      var PLAT = String(BC.plataforma || "").replace(/\/+$/, "");
      var prods = (r[1] || []).map(function (p) {
        p.price = Number(p.price) || 0; p.opcoes = Array.isArray(p.opcoes) ? p.opcoes : [];
        if (typeof p.image_url === "string" && /^\/[^\/]/.test(p.image_url)) p.image_url = /^https:\/\//.test(PLAT) ? PLAT + p.image_url : "";
        return p;
      });
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


  /* opcoes(prod): janela para escolher os opcionais do produto (tamanho, tipo de leite, adicionais...).
     Devolve uma Promise com { ops: [{ g, o }], extra, rotulo, qtd } ou null se a pessoa fechar.
     Cores pelas variáveis --mot-bg, --mot-txt e --mot-cor (cada modelo define as suas). */
  function brl(v) { return "R$ " + (Math.round(v * 100) / 100).toFixed(2).replace(".", ","); }
  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  var cssOk = false;
  function css() {
    if (cssOk) return; cssOk = true;
    var st = document.createElement("style");
    st.textContent = ".mot-veu{position:fixed;inset:0;z-index:2147483000;background:rgba(0,0,0,.6);backdrop-filter:blur(3px)}" +
      ".mot-folha{position:fixed;z-index:2147483001;left:50%;bottom:0;transform:translateX(-50%);width:min(520px,100%);max-height:88vh;display:flex;flex-direction:column;background:var(--mot-bg,#151311);color:var(--mot-txt,#f3e9d8);border-radius:20px 20px 0 0;box-shadow:0 -20px 60px rgba(0,0,0,.5);font-family:inherit}" +
      "@media(min-width:700px){.mot-folha{bottom:auto;top:50%;transform:translate(-50%,-50%);border-radius:20px}}" +
      ".mot-topo{display:flex;align-items:center;gap:12px;padding:18px 20px 12px}.mot-topo h3{flex:1;margin:0;font-size:1.25rem;line-height:1.2}" +
      ".mot-x{width:38px;height:38px;border-radius:50%;border:1px solid rgba(255,255,255,.2);background:transparent;color:inherit;font-size:18px;cursor:pointer}" +
      ".mot-corpo{overflow:auto;padding:0 20px 10px}.mot-desc{opacity:.75;margin:0 0 12px;font-size:.95rem}" +
      ".mot-g{margin:0 0 14px;padding:12px;border-radius:14px;border:1px solid rgba(255,255,255,.12);transition:border-color .3s}.mot-g.falta{border-color:#ff4d3d}" +
      ".mot-gc{display:flex;justify-content:space-between;align-items:baseline;gap:10px;margin-bottom:8px}.mot-gc span{font-size:.8rem;opacity:.7}.mot-gc span.ob{color:var(--mot-cor,#ff6a1a);opacity:1}" +
      ".mot-i{display:flex;align-items:center;gap:10px;width:100%;padding:10px 8px;border:0;border-radius:10px;background:transparent;color:inherit;font:inherit;text-align:left;cursor:pointer}.mot-i:hover{background:rgba(255,255,255,.06)}" +
      ".mot-m{flex:none;width:20px;height:20px;border-radius:6px;border:2px solid rgba(255,255,255,.35)}.mot-m.r{border-radius:50%}.mot-i.on .mot-m{border-color:var(--mot-cor,#ff6a1a);background:radial-gradient(circle,var(--mot-cor,#ff6a1a) 0 45%,transparent 50%)}" +
      ".mot-i .n{flex:1}.mot-i .p{opacity:.8;font-size:.9rem}" +
      ".mot-pe{display:flex;gap:10px;padding:14px 20px 18px;border-top:1px solid rgba(255,255,255,.1)}.mot-q{display:flex;align-items:center;gap:6px}.mot-q button{width:38px;height:44px;border-radius:10px;border:1px solid rgba(255,255,255,.2);background:transparent;color:inherit;font-size:20px;cursor:pointer}.mot-q b{min-width:22px;text-align:center}" +
      ".mot-add{flex:1;border:0;border-radius:12px;background:var(--mot-cor,#ff6a1a);color:var(--mot-cor-txt,#111);font:inherit;font-weight:700;cursor:pointer}";
    document.head.appendChild(st);
  }
  function opcoes(p) {
    return new Promise(function (ok) {
      css();
      var sel = {}, q = 1, foco = document.activeElement;
      var veu = el("div", "mot-veu"), f = el("div", "mot-folha"), topo = el("div", "mot-topo"), h = el("h3", "", p.name), x = el("button", "mot-x", "✕");
      f.setAttribute("role", "dialog"); f.setAttribute("aria-modal", "true"); f.setAttribute("aria-label", p.name); x.type = "button"; x.setAttribute("aria-label", "Fechar");
      topo.appendChild(h); topo.appendChild(x);
      var corpo = el("div", "mot-corpo"), pe = el("div", "mot-pe"), qq = el("div", "mot-q"), menos = el("button", "", "−"), qn = el("b", "", "1"), mais = el("button", "", "+"), add = el("button", "mot-add");
      menos.type = mais.type = add.type = "button"; menos.setAttribute("aria-label", "Menos"); mais.setAttribute("aria-label", "Mais");
      qq.appendChild(menos); qq.appendChild(qn); qq.appendChild(mais); pe.appendChild(qq); pe.appendChild(add);
      f.appendChild(topo); f.appendChild(corpo); f.appendChild(pe);
      function soma() { var s = p.price; p.opcoes.forEach(function (g) { (sel[g.id] || []).forEach(function (oid) { (g.itens || []).forEach(function (it) { if (it.id === oid) s += Number(it.preco) || 0; }); }); }); return s; }
      function desenha() {
        corpo.textContent = "";
        if (p.description) corpo.appendChild(el("p", "mot-desc", p.description));
        p.opcoes.forEach(function (g) {
          var max = Number(g.max) || 1, min = Number(g.min) || 0, sec = el("section", "mot-g"), cab = el("div", "mot-gc");
          sec.dataset.g = g.id; cab.appendChild(el("b", "", g.nome));
          cab.appendChild(el("span", min >= 1 ? "ob" : "", min >= 1 ? (max === 1 ? "Escolha 1 · obrigatório" : "Escolha de " + min + " a " + max) : (max === 1 ? "Opcional" : "Opcional · até " + max)));
          sec.appendChild(cab);
          (g.itens || []).forEach(function (it) {
            var on = (sel[g.id] || []).indexOf(it.id) >= 0, b = el("button", "mot-i" + (on ? " on" : ""));
            b.type = "button"; b.setAttribute("role", max === 1 ? "radio" : "checkbox"); b.setAttribute("aria-checked", on ? "true" : "false");
            b.appendChild(el("span", "mot-m" + (max === 1 ? " r" : ""))); b.appendChild(el("span", "n", it.nome));
            if (Number(it.preco) > 0) b.appendChild(el("span", "p", "+ " + brl(Number(it.preco))));
            b.addEventListener("click", function () {
              var s = sel[g.id] || (sel[g.id] = []), i = s.indexOf(it.id);
              if (max === 1) sel[g.id] = i >= 0 ? (min >= 1 ? s : []) : [it.id];
              else if (i >= 0) s.splice(i, 1); else if (s.length < max) s.push(it.id);
              desenha();
            });
            sec.appendChild(b);
          });
          corpo.appendChild(sec);
        });
        qn.textContent = q; add.textContent = "Adicionar · " + brl(soma() * q);
      }
      function fecha(r) { veu.remove(); f.remove(); document.removeEventListener("keydown", tecla); try { foco && foco.focus(); } catch (e) {} ok(r); }
      function tecla(e) { if (e.key === "Escape") fecha(null); }
      veu.addEventListener("click", function () { fecha(null); }); x.addEventListener("click", function () { fecha(null); });
      menos.addEventListener("click", function () { if (q > 1) { q--; desenha(); } });
      mais.addEventListener("click", function () { if (q < 99) { q++; desenha(); } });
      add.addEventListener("click", function () {
        var falta = null;
        p.opcoes.forEach(function (g) { if (!falta && (sel[g.id] || []).length < (Number(g.min) || 0)) falta = g; });
        if (falta) { var sec = corpo.querySelector('[data-g="' + falta.id + '"]'); if (sec) { sec.classList.add("falta"); sec.scrollIntoView({ block: "center" }); setTimeout(function () { sec.classList.remove("falta"); }, 1800); } return; }
        var ops = [], nomes = [];
        p.opcoes.forEach(function (g) { (sel[g.id] || []).forEach(function (oid) { ops.push({ g: g.id, o: oid }); (g.itens || []).forEach(function (it) { if (it.id === oid) nomes.push(it.nome); }); }); });
        fecha({ ops: ops, extra: Math.round((soma() - p.price) * 100) / 100, rotulo: nomes.join(", "), qtd: q });
      });
      document.addEventListener("keydown", tecla);
      desenha(); document.body.appendChild(veu); document.body.appendChild(f); x.focus();
    });
  }

  window.MOTOR = { ok: ok, slug: SLUG, carrega: carrega, pedido: pedido, rastreio: rastreio, opcoes: opcoes, api: api };
})();
