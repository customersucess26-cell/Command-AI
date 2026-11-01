/* Marca do cliente · aplica no modelo o que está em window.LOJA (assets/config.js), sem editar o HTML:
   textos   → elementos com data-tx="chave" (texto puro; "\n" vira quebra de linha)
   imagens  → elementos <img data-img="chave"> (e o mapa IMG do cardápio, lido pelo próprio modelo)
   contato  → elementos com data-c="whatsapp|endereco|horario|instagram"
   marca    → cores (variáveis CSS do modelo), fontes do Google, título, descrição e cor do navegador
   ocultar  → blocos com data-bloco="nome" que não se aplicam a este cliente (ex.: "depoimentos")
   Fonte: paineis/motor/marca.js. Roda antes dos scripts do modelo. */
(function () {
  "use strict";
  var L = window.LOJA || {}, M = L.marca || {}, T = L.textos || {}, I = L.imagens || {}, C = L.contato || {};
  function linhas(el, v) {
    el.textContent = "";
    String(v).split("\n").forEach(function (t, i) { if (i) el.appendChild(document.createElement("br")); el.appendChild(document.createTextNode(t)); });
  }
  function urlOk(u) { return typeof u === "string" && /^(img\/[\w.\/-]+|assets\/[\w.\/-]+|https:\/\/[^"'\s<>()]+)$/.test(u); }
  function cor(v) { return typeof v === "string" && /^(#[0-9a-f]{3,8}|rgba?\([\d\s.,%]+\)|hsla?\([\d\s.,%deg]+\))$/i.test(v.trim()); }
  window.MARCA_IMG = function (k, padrao) { return urlOk(I[k]) ? I[k] : padrao; };

  /* cores e fontes antes do primeiro desenho */
  var raiz = document.documentElement.style;
  Object.keys(M.cores || {}).forEach(function (k) { if (/^[a-z][a-z0-9-]{0,30}$/i.test(k) && cor(M.cores[k])) raiz.setProperty("--" + k, M.cores[k].trim()); });
  var F = M.fontes || {};
  if (typeof F.url === "string" && /^https:\/\/fonts\.googleapis\.com\/css2\?[^"'<>\s]+$/.test(F.url)) {
    var lk = document.createElement("link"); lk.rel = "stylesheet"; lk.href = F.url; document.head.appendChild(lk);
  }
  ["display", "script", "body"].forEach(function (k) { if (typeof F[k] === "string" && /^[\w\s"',.-]{2,120}$/.test(F[k])) raiz.setProperty("--f-" + k, F[k]); });
  if (typeof M.titulo === "string" && M.titulo) document.title = M.titulo.slice(0, 90);
  if (typeof M.descricao === "string" && M.descricao) { var d = document.querySelector('meta[name="description"]'); if (d) d.setAttribute("content", M.descricao.slice(0, 200)); }
  if (cor(M.corNavegador)) { var tc = document.querySelector('meta[name="theme-color"]'); if (tc) tc.setAttribute("content", M.corNavegador); }

  function aplica() {
    [].forEach.call(document.querySelectorAll("[data-tx]"), function (el) {
      var v = T[el.getAttribute("data-tx")];
      if (el.hasAttribute("data-count")) { var n = Number(String(v).replace(",", ".")); if (v !== undefined && isFinite(n)) { el.setAttribute("data-count", n); el.setAttribute("data-dec", String(n).indexOf(".") >= 0 ? 1 : 0); } return; }
      if (typeof v === "string" || typeof v === "number") linhas(el, v);
    });
    [].forEach.call(document.querySelectorAll("img[data-img]"), function (el) {
      var u = I[el.getAttribute("data-img")]; if (urlOk(u)) el.src = u;
    });
    var fone = String(C.whatsappTexto || L.whatsapp || "");
    var mapa = { whatsapp: fone, endereco: C.endereco, horario: C.horario, instagram: C.instagram };
    [].forEach.call(document.querySelectorAll("[data-c]"), function (el) {
      var v = mapa[el.getAttribute("data-c")]; if (typeof v === "string" && v) linhas(el, v);
    });
    (Array.isArray(L.ocultar) ? L.ocultar : []).forEach(function (b) {
      [].forEach.call(document.querySelectorAll('[data-bloco="' + String(b).replace(/[^\w-]/g, "") + '"]'), function (el) { el.hidden = true; el.style.display = "none"; });
    });
    /* logo em imagem, quando houver: troca o logotipo em texto */
    if (urlOk(M.logo)) [].forEach.call(document.querySelectorAll("[data-logo]"), function (el) {
      var im = document.createElement("img"); im.src = M.logo; im.alt = L.nome || ""; im.className = "logo-img";
      el.textContent = ""; el.appendChild(im);
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", aplica); else aplica();
  window.MARCA_APLICA = aplica;
})();
