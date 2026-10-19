/* Bistrô Connect · efeitos compartilhados, sem bibliotecas.
   - .revela: o bloco surge ao entrar na tela (com atraso em cascata entre irmãos)
   - [data-conta="500"]: o número sobe contando quando aparece (mantém o texto antes e depois do número)
   - .vidro-ao-rolar: ganha a classe .rolou depois de rolar a página
   - BCEfeitos.confete(): pequena comemoração
   Quem pede "reduzir movimento" no aparelho não vê animação. */
(function () {
  "use strict";
  var parado = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var doc = document.documentElement;
  if (!parado && "IntersectionObserver" in window) doc.classList.add("js-efeitos");

  function revelar(raiz) {
    var els = (raiz || document).querySelectorAll(".revela:not(.visto)");
    if (!doc.classList.contains("js-efeitos")) { els.forEach(function (e) { e.classList.add("visto"); }); return; }
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("visto"); io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: "0px 0px -30px 0px" });
    els.forEach(function (el) {
      if (!el.style.transitionDelay) {
        var irmaos = Array.prototype.filter.call(el.parentNode.children, function (c) { return c.classList.contains("revela"); });
        el.style.transitionDelay = Math.min(irmaos.indexOf(el), 5) * 80 + "ms";
      }
      io.observe(el);
    });
  }

  function formata(n, casas) {
    return n.toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });
  }
  function contar(raiz) {
    var els = (raiz || document).querySelectorAll("[data-conta]");
    els.forEach(function (el) {
      var alvo = parseFloat(el.getAttribute("data-conta")), casas = +(el.getAttribute("data-casas") || 0);
      if (!isFinite(alvo)) return;
      var antes = el.getAttribute("data-antes") || "", depois = el.getAttribute("data-depois") || "";
      var fim = function () { el.textContent = antes + formata(alvo, casas) + depois; };
      if (parado || !("IntersectionObserver" in window)) return fim();
      el.textContent = antes + formata(0, casas) + depois;
      var io = new IntersectionObserver(function (es) {
        if (!es[0].isIntersecting) return; io.disconnect();
        var t0 = performance.now(), dur = +(el.getAttribute("data-dur") || 1400);
        (function passo(t) {
          var p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 3);
          el.textContent = antes + formata(alvo * e, casas) + depois;
          if (p < 1) requestAnimationFrame(passo); else fim();
        })(t0);
      }, { threshold: 0.4 });
      io.observe(el);
    });
  }

  function vidro() {
    var els = document.querySelectorAll(".vidro-ao-rolar");
    if (!els.length) return;
    var f = function () { var r = window.scrollY > 12; els.forEach(function (e) { e.classList.toggle("rolou", r); }); };
    window.addEventListener("scroll", f, { passive: true }); f();
  }

  function confete(origem) {
    if (parado || !document.body.animate) return;
    var cores = ["#E2552B", "#F2B544", "#2F7A55", "#2BA8FF", "#FFF8EE", "#C9A24A"];
    var r = origem && origem.getBoundingClientRect ? origem.getBoundingClientRect() : { left: innerWidth / 2, top: innerHeight / 3, width: 0, height: 0 };
    var x0 = r.left + r.width / 2, y0 = r.top + r.height / 2;
    for (var i = 0; i < 90; i++) {
      var c = document.createElement("i");
      c.className = "confete";
      c.style.background = cores[i % cores.length];
      if (i % 3 === 0) c.style.borderRadius = "50%";
      document.body.appendChild(c);
      var ang = Math.random() * Math.PI * 2, vel = 120 + Math.random() * 260;
      var dx = Math.cos(ang) * vel, dy = Math.sin(ang) * vel - 220, giro = (Math.random() - 0.5) * 1080;
      var anim = c.animate([
        { transform: "translate(" + x0 + "px," + y0 + "px) rotate(0deg)", opacity: 1 },
        { transform: "translate(" + (x0 + dx) + "px," + (y0 + dy) + "px) rotate(" + giro / 2 + "deg)", opacity: 1, offset: 0.45 },
        { transform: "translate(" + (x0 + dx * 1.3) + "px," + (y0 + dy + 520) + "px) rotate(" + giro + "deg)", opacity: 0 }
      ], { duration: 1800 + Math.random() * 1200, easing: "cubic-bezier(.2,.6,.4,1)" });
      anim.onfinish = (function (el) { return function () { el.remove(); }; })(c);
    }
  }

  /* máscara de WhatsApp: (42) 99999-9999 */
  function mascaras() {
    document.querySelectorAll('[data-mascara="zap"]').forEach(function (inp) {
      inp.addEventListener("input", function () {
        var d = inp.value.replace(/\D/g, "");
        if (d.length > 11 && d.indexOf("55") === 0) d = d.slice(2);
        d = d.slice(0, 11);
        var f = d;
        if (d.length > 2) f = "(" + d.slice(0, 2) + ") " + d.slice(2);
        if (d.length > 6) f = "(" + d.slice(0, 2) + ") " + d.slice(2, d.length - 4) + "-" + d.slice(-4);
        inp.value = f;
      });
    });
  }

  /* [data-aparece-apos=".hero"]: ganha .mostra quando o elemento indicado sai da tela (botão fixo no celular) */
  function aparecer() {
    document.querySelectorAll("[data-aparece-apos]").forEach(function (el) {
      var alvo = document.querySelector(el.getAttribute("data-aparece-apos"));
      if (!alvo || !("IntersectionObserver" in window)) { el.classList.add("mostra"); return; }
      new IntersectionObserver(function (es) { el.classList.toggle("mostra", !es[0].isIntersecting && es[0].boundingClientRect.top < 0); }).observe(alvo);
    });
  }

  function iniciar() { revelar(); contar(); vidro(); mascaras(); aparecer(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar); else iniciar();
  window.BCEfeitos = { revelar: revelar, contar: contar, confete: confete, parado: parado };
})();
