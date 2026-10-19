/* Bistrô Connect · medição de campanhas: Meta Pixel, Google Ads e Google Analytics 4.
   - Nada de terceiros carrega antes da pessoa aceitar os cookies de marketing (LGPD). A escolha fica em "eb-consent".
   - Os códigos ficam em assets/config.js (pixelId, googleAdsId, googleAdsRotuloLoja, googleAdsRotuloLead, googleAnalyticsId).
     Vazio = desligado, e o aviso de cookies nem aparece.
   - BCOrigem guarda de onde a pessoa veio (utm_*, gclid, fbclid ou o site que mandou para cá) por 90 dias,
     só neste navegador, para o cadastro da loja registrar qual campanha trouxe a loja.
   - BCMedir(evento, dados): "lead", "contato", "cadastro", "loja_criada", "clique". Também aceita "Lead" e "Contact". */
(function () {
  "use strict";
  var C = window.BC || {};
  var limpa = function (v, re) { v = String(v || "").trim(); return re.test(v) ? v : ""; };
  var PIXEL = limpa(C.pixelId, /^\d{6,20}$/);
  var ADS = limpa(C.googleAdsId, /^AW-\d{6,15}$/);
  var GA = limpa(C.googleAnalyticsId, /^G-[A-Z0-9]{4,15}$/);
  var ROT_LOJA = limpa(C.googleAdsRotuloLoja, /^[A-Za-z0-9_-]{4,40}$/);
  var ROT_LEAD = limpa(C.googleAdsRotuloLead, /^[A-Za-z0-9_-]{4,40}$/);
  var ligado = !!(PIXEL || ADS || GA), carregou = false;

  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  /* ---------- origem da visita ---------- */
  var CHAVES = { utm_source: "fonte", utm_medium: "meio", utm_campaign: "campanha", utm_term: "termo", utm_content: "conteudo", gclid: "gclid", fbclid: "fbclid" };
  (function guardaOrigem() {
    var q = new URLSearchParams(location.search), o = {}, tem = false;
    Object.keys(CHAVES).forEach(function (k) { var v = q.get(k); if (v) { o[CHAVES[k]] = v.slice(0, 150); tem = true; } });
    if (o.gclid && !o.fonte) { o.fonte = "google"; o.meio = o.meio || "cpc"; }
    if (o.fbclid && !o.fonte) { o.fonte = "facebook"; o.meio = o.meio || "social"; }
    var atual = null; try { atual = JSON.parse(lsGet("bc-origem") || "null"); } catch (e) {}
    if (atual && Date.now() - (atual.t || 0) > 90 * 864e5) atual = null;
    if (!tem && !atual && document.referrer) {
      try { var h = new URL(document.referrer).hostname; if (h && h !== location.hostname) { o.fonte = h.replace(/^www\./, ""); o.meio = "referencia"; o.referencia = h; tem = true; } } catch (e) {}
    }
    if (tem) {
      var nicho = q.get("para"); if (nicho) o.nicho = nicho.slice(0, 30);
      o.pagina = location.pathname.slice(0, 80); o.quando = new Date().toISOString().slice(0, 10); o.t = Date.now();
      lsSet("bc-origem", JSON.stringify(o));
    }
  })();
  window.BCOrigem = {
    dados: function () { var o = null; try { o = JSON.parse(lsGet("bc-origem") || "null"); } catch (e) {} if (!o) return {}; var c = {}; Object.keys(o).forEach(function (k) { if (k !== "t") c[k] = o[k]; }); return c; },
    texto: function () { var o = this.dados(); return o.fonte ? [o.fonte, o.meio, o.campanha].filter(Boolean).join(" / ") : "site"; }
  };

  /* ---------- carregar as ferramentas depois do aceite ---------- */
  function carrega() {
    if (carregou || !ligado) return; carregou = true;
    if (PIXEL && !window.fbq) {
      !function (f, b, e, v, n, t, s) { if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); }; if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = "2.0"; n.queue = []; t = b.createElement(e); t.async = !0; t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s); }(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
      window.fbq("init", PIXEL); window.fbq("track", "PageView");
    }
    if (ADS || GA) {
      window.dataLayer = window.dataLayer || [];
      window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
      var s = document.createElement("script"); s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + (GA || ADS);
      document.head.appendChild(s);
      window.gtag("consent", "default", { ad_storage: "granted", analytics_storage: "granted", ad_user_data: "granted", ad_personalization: "granted" });
      window.gtag("js", new Date());
      if (GA) window.gtag("config", GA);
      if (ADS) window.gtag("config", ADS);
    }
  }
  function aceitou() { return lsGet("eb-consent") === "sim"; }

  function aviso() {
    if (!ligado || lsGet("eb-consent") || document.querySelector(".consent,.bc-consent")) return;
    var st = document.createElement("style");
    st.textContent = ".bc-consent{position:fixed;left:16px;right:16px;bottom:16px;z-index:9000;max-width:560px;margin:0 auto;background:#0E1526;color:#EEF2F6;border:1px solid #24304B;border-radius:16px;padding:14px 16px;display:flex;gap:14px;align-items:center;flex-wrap:wrap;box-shadow:0 18px 40px -18px rgba(0,0,0,.7);font:15px/1.45 system-ui,-apple-system,'Segoe UI',sans-serif}" +
      ".bc-consent p{flex:1 1 240px;margin:0;color:#A9B4C6}.bc-consent a{color:#7AD3FF}.bc-consent div{display:flex;gap:8px}" +
      ".bc-consent button{font:inherit;font-weight:700;padding:10px 16px;border-radius:999px;border:1px solid #24304B;background:transparent;color:#EEF2F6;cursor:pointer;min-height:44px}" +
      ".bc-consent button.sim{background:#2BA8FF;border-color:#2BA8FF;color:#06101F}";
    document.head.appendChild(st);
    var b = document.createElement("div"); b.className = "bc-consent"; b.setAttribute("role", "region"); b.setAttribute("aria-label", "Aviso de cookies");
    var p = document.createElement("p");
    p.appendChild(document.createTextNode("Usamos cookies de marketing (Meta e Google) para medir nossos anúncios. Você escolhe. "));
    var a = document.createElement("a"); a.href = "/privacidade.html"; a.textContent = "Saiba mais"; p.appendChild(a);
    var d = document.createElement("div");
    [["nao", "Recusar", ""], ["sim", "Aceitar", "sim"]].forEach(function (x) { var bt = document.createElement("button"); bt.type = "button"; bt.dataset.c = x[0]; bt.textContent = x[1]; if (x[2]) bt.className = x[2]; d.appendChild(bt); });
    b.appendChild(p); b.appendChild(d);
    b.addEventListener("click", function (e) { var c = e.target.getAttribute("data-c"); if (!c) return; lsSet("eb-consent", c); if (c === "sim") carrega(); b.remove(); });
    document.body.appendChild(b);
  }

  /* ---------- eventos ---------- */
  var feitos = {};
  window.BCMedir = function (ev, dados) {
    ev = { Lead: "lead", Contact: "contato" }[ev] || ev; dados = dados || {};
    if (!ligado || !aceitou()) return;
    carrega();
    var fb = function (n, d, custom) { try { if (window.fbq) window.fbq(custom ? "trackCustom" : "track", n, d || {}); } catch (e) {} };
    var g = function (n, d) { try { if (window.gtag) window.gtag("event", n, d || {}); } catch (e) {} };
    if (ev === "lead") {
      fb("Lead", { content_name: dados.content_name || "ajuda" }); g("generate_lead", { method: dados.content_name || "formulario" });
      if (ADS && ROT_LEAD) g("conversion", { send_to: ADS + "/" + ROT_LEAD });
    } else if (ev === "contato") {
      fb("Contact"); g("contact", { method: "whatsapp" });
    } else if (ev === "cadastro") {
      if (feitos.cadastro) return; feitos.cadastro = 1;
      fb("CompleteRegistration"); g("sign_up", { method: "email" });
    } else if (ev === "loja_criada") {
      if (feitos.loja) return; feitos.loja = 1;
      fb("StartTrial", { value: 0, currency: "BRL", predicted_ltv: 0 }); fb("LojaCriada", { tipo: dados.tipo || "" }, true);
      g("loja_criada", { tipo: dados.tipo || "" });
      if (ADS && ROT_LOJA) g("conversion", { send_to: ADS + "/" + ROT_LOJA });
    } else if (ev === "clique") {
      g("clique_cta", { botao: dados.nome || "" });
    }
  };
  /* cliques nos botões marcados com data-track (ex.: data-track="cta-hero") */
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-track]"); if (!a) return;
    var n = a.getAttribute("data-track") || "";
    if (/whatsapp/.test(n)) window.BCMedir("contato"); else window.BCMedir("clique", { nome: n });
  });

  if (ligado && aceitou()) carrega();
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", aviso); else aviso();
})();
