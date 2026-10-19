/* Preenche os dados da empresa nos Termos e na Política de privacidade a partir de window.BC.empresa (assets/config.js).
   Campo vazio: some a linha marcada com data-se. */
(function () {
  "use strict";
  var BC = window.BC || {}, E = BC.empresa || {};
  var zap = String(BC.suporteWhatsapp || "").replace(/\D/g, "");
  var valores = {
    nome: E.razaoSocial || "Bistrô Connect",
    cnpj: E.cnpj || "",
    email: E.email || "",
    cidade: E.cidade || "",
    whatsapp: zap ? "+" + zap.replace(/^(\d{2})(\d{2})(\d{4,5})(\d{4})$/, "$1 ($2) $3-$4") : ""
  };
  document.querySelectorAll("[data-empresa]").forEach(function (el) {
    var v = valores[el.getAttribute("data-empresa")];
    if (v) el.textContent = v;
  });
  document.querySelectorAll("[data-se]").forEach(function (el) {
    if (!valores[el.getAttribute("data-se")]) el.hidden = true;
  });
  document.querySelectorAll("a[data-email]").forEach(function (a) { if (valores.email) a.href = "mailto:" + valores.email; });
  document.querySelectorAll("[data-rever-cookies]").forEach(function (b) {
    b.addEventListener("click", function () { try { localStorage.removeItem("eb-consent"); } catch (e) {} location.reload(); });
  });
  document.querySelectorAll("a[data-zap]").forEach(function (a) { if (zap) a.href = "https://wa.me/" + zap; });
})();
