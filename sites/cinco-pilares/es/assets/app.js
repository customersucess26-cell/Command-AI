/* Los 5 Pilares · v18 · lógica da página
   Sequência da torre controlada pela rolagem, preço e checkout com UTM, píxel,
   teste de 5 perguntas, carrossel, contagem regressiva e prova social (só dados reais). */
(function () {
  'use strict';
  window.__app = true;
  var root = document.documentElement;
  var RM = root.classList.contains('rm');
  var FINE = false; try { FINE = matchMedia('(hover:hover) and (pointer:fine)').matches; } catch (e) {}
  var $ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };
  var $1 = function (s, r) { return (r || document).querySelector(s); };
  var https = function (u) { return /^https:\/\//i.test(u || '') ? u : ''; };
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

  /* ---------- configuração e preço ---------- */
  var C = { moeda: 'US$', preco: '19,90', garantiaDias: 7, checkout: '' };
  try { var cf = JSON.parse($1('#cfg').textContent); for (var k in cf) if (cf[k] !== '' && cf[k] !== null) C[k] = cf[k]; } catch (e) {}
  function parse(p) { var s = String(p || '').replace(/\s/g, '').replace('.', ','), a = s.split(','); var i = a[0] || '0', c = ((a[1] || '') + '00').slice(0, 2); return { txt: i + ',' + c, num: parseFloat(i + '.' + c) || 0 }; }
  var cur = C.moeda || 'US$', P = parse(C.preco), A = C.precoDepois ? parse(C.precoDepois) : null;
  $('[data-price]').forEach(function (e) { e.textContent = cur + ' ' + P.txt; });
  $('[data-cur]').forEach(function (e) { e.textContent = cur; });
  $('[data-num]').forEach(function (e) { e.textContent = P.txt; });
  $('[data-perday]').forEach(function (e) { var d = P.num / 90; e.textContent = d < 1 ? 'unos ' + Math.round(d * 100) + ' centavos de dólar' : cur + ' ' + d.toFixed(2).replace('.', ','); });
  var gd = +C.garantiaDias > 0 ? Math.round(+C.garantiaDias) : 7;
  $('[data-gd]').forEach(function (e) { e.textContent = gd; });
  if (C.precoDe) {
    var De = parse(C.precoDe);
    if (De.num > P.num) {
      $('[data-price-from]').forEach(function (e) { e.textContent = cur + ' ' + De.txt; });
      var sv = De.num - P.num, pct = Math.round((1 - P.num / De.num) * 100);
      $('[data-save]').forEach(function (e) { e.textContent = cur + ' ' + sv.toFixed(2).replace('.', ',') + ' (' + pct + '%)'; });
      $1('#from').hidden = false; $1('#save').hidden = false;
    }
  }
  var end = C.prazo ? new Date(C.prazo).getTime() : NaN;
  if (A && A.num > P.num && !isNaN(end) && end > Date.now()) {
    $('[data-price-after]').forEach(function (e) { e.textContent = cur + ' ' + A.txt; });
    var L = $1('#launch'); L.hidden = false; $1('#after').hidden = false; $1('#cdbox').hidden = false;
    try { $1('#launch-date').textContent = new Date(end).toLocaleDateString('es', { day: 'numeric', month: 'long' }); } catch (e) {}
    var f2 = function (n) { return String(n).padStart(2, '0'); };
    var tick = function () {
      var x = Math.max(0, end - Date.now()), d = Math.floor(x / 864e5); x -= d * 864e5; var h = Math.floor(x / 36e5); x -= h * 36e5; var m = Math.floor(x / 6e4), s = Math.floor((x - m * 6e4) / 1e3);
      $1('#cd').textContent = (d ? d + 'd ' : '') + f2(h) + 'h ' + f2(m) + 'm ' + f2(s) + 's';
      $1('#cd-d').textContent = f2(d); $1('#cd-h').textContent = f2(h); $1('#cd-m').textContent = f2(m); $1('#cd-s').textContent = f2(s);
      if (end <= Date.now()) { L.hidden = true; $1('#cdbox').hidden = true; }
    };
    tick(); setInterval(tick, 1000);
  }

  /* ---------- píxel e checkout com UTM ---------- */
  var CUR = /US/i.test(cur) ? 'USD' : cur;
  if (C.pixel && /^\d{8,20}$/.test(String(C.pixel))) {
    !function (f, b, e, v, n, t, s) { if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); }; if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = []; t = b.createElement(e); t.async = !0; t.src = 'https://connect.facebook.net/en_US/fbevents.js'; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s); }(window, document, 'script');
    fbq('init', String(C.pixel)); fbq('track', 'PageView');
  }
  var track = function (ev, data, custom) { try { if (window.fbq) fbq(custom ? 'trackCustom' : 'track', ev, data || {}); } catch (e) {} };
  var PROD = 'Los 5 Pilares de la Prosperidad';
  track('ViewContent', { content_name: PROD, content_type: 'product', value: P.num, currency: CUR, variant: 'v18' });
  var ok = !!https(C.checkout);
  function ckUrl(extra) {
    if (!ok) return '#oferta';
    try {
      var u = new URL(C.checkout), q = new URLSearchParams(location.search);
      ['fbclid', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'src', 'sck'].forEach(function (k) { if (q.get(k)) u.searchParams.set(k, q.get(k)); });
      if (!u.searchParams.get('src') && q.get('utm_source')) u.searchParams.set('src', q.get('utm_source').slice(0, 60));
      var sck = [q.get('utm_campaign'), q.get('utm_content'), 'v18', extra].filter(Boolean).join('|');
      if (!u.searchParams.get('sck') && sck) u.searchParams.set('sck', sck.slice(0, 120));
      return u.toString();
    } catch (e) { return C.checkout; }
  }
  var CK = ckUrl();
  $('[data-co]').forEach(function (a) { if (ok) { a.href = CK; a.rel = 'noopener'; } });
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('[data-co]');
    if (a && ok) track('InitiateCheckout', { content_name: PROD, value: P.num, currency: CUR });
  }, true);
  $('[data-quiz]').forEach(function (a) { a.addEventListener('click', function () { track('QuizClick', {}, true); }); });

  /* ---------- teste de 5 perguntas ---------- */
  var COL = ['var(--p1)', 'var(--p2)', 'var(--p3)', 'var(--p4)', 'var(--p5)'];
  var Q = [
    ['Salud', '¿Cómo está tu energía en el día a día?', ['Me despierto cansado y rindo poco', 'Varía: hay días buenos y días malos', 'Tengo energía y una rutina de cuidado']],
    ['Relaciones', '¿Cómo están las personas que amas?', ['Estoy distante y sin tiempo para ellas', 'Estoy presente, pero podría cuidarlas mejor', 'Cercano y con conversaciones de calidad']],
    ['Carrera', '¿Cómo está tu rumbo profesional?', ['Ocupado, pero sin avanzar', 'Tengo ideas, pero ningún plan', 'Tengo dirección y metas claras']],
    ['Finanzas', '¿Cómo está tu dinero?', ['Se me escapa y una emergencia me quebraría', 'Pago las cuentas, pero sin ahorro ni plan', 'Ordenado, con ahorro y metas']],
    ['Espiritualidad', '¿Sabes hacia dónde vas?', ['Corro mucho sin saber hacia dónde', 'Tengo pistas, pero no una dirección', 'Tengo sentido y dirección claros']]];
  var REC = {
    'Salud': 'Empieza por el pilar Salud. Con el cuerpo agotado, ningún otro cambio dura. Dentro del sistema, el libro de Salud y las primeras misiones te muestran qué hacer desde hoy.',
    'Relaciones': 'Empieza por el pilar Relaciones. Cuida a quienes amas antes de que la distancia crezca. Dentro del sistema, el libro de Relaciones y las primeras misiones te muestran qué hacer desde hoy.',
    'Carrera': 'Empieza por el pilar Carrera. Un plan de 90 días saca tu trabajo del piloto automático. Dentro del sistema, el libro de Carrera y las primeras misiones te muestran qué hacer desde hoy.',
    'Finanzas': 'Empieza por el pilar Finanzas. Ordenar deudas y crear un colchón trae calma a todo lo demás. Dentro del sistema, el libro de Finanzas y las primeras misiones te muestran qué hacer desde hoy.',
    'Espiritualidad': 'Empieza por el pilar Desarrollo personal y espiritualidad. La dirección le da sentido a todo tu esfuerzo. Dentro del sistema, el libro de este pilar y las primeras misiones te muestran qué hacer desde hoy.' };
  var box = $1('#quiz'), qi = 0, sc = [];
  function prog(n) { return '<div class="q-prog" aria-hidden="true">' + Q.map(function (_, i) { return '<i class="' + (i < n ? 'on' : '') + '" style="--c:' + COL[i] + '"></i>'; }).join('') + '</div>'; }
  function ask(first) {
    var q = Q[qi]; box.style.setProperty('--c', COL[qi]);
    box.innerHTML = prog(qi) + '<p class="q-n">Pregunta ' + (qi + 1) + ' de 5 · ' + q[0] + '</p><p class="q-t" id="q-t" tabindex="-1">' + esc(q[1]) + '</p><div class="q-o" role="group" aria-labelledby="q-t">' +
      q[2].map(function (o, k) { return '<button type="button" data-k="' + (k + 1) + '"><b>' + 'ABC'.charAt(k) + '</b><span>' + esc(o) + '</span></button>'; }).join('') +
      '</div><p class="q-priv">Tus respuestas no salen de tu pantalla.</p>';
    $('button', box).forEach(function (b) {
      b.onclick = function () {
        if (!sc.length) track('QuizStart', {}, true);
        sc.push(+b.dataset.k); qi++;
        if (qi < 5) ask(); else res();
      };
    });
    if (!first) { var t = $1('#q-t'); if (t) t.focus({ preventScroll: true }); }
  }
  function res() {
    var m = 0; sc.forEach(function (s, i) { if (s < sc[m]) m = i; });
    var name = Q[m][0], firm = sc[m] === 3;
    var link = ok ? esc(ckUrl('quiz-' + name.toLowerCase())) : '#oferta';
    box.style.setProperty('--c', firm ? 'var(--gold)' : COL[m]);
    box.innerHTML = '<div class="res">' + prog(5) +
      '<p class="q-n">Tu resultado</p><h3 id="res-h" tabindex="-1">' + (firm ? 'Tus pilares están firmes.' : 'Tu Pilar Ancla hoy: ' + name) + '</h3>' +
      '<p>' + (firm ? 'Buen punto de partida. El sistema te ayuda a sostenerlos y a subir cada uno.' : REC[name]) + '</p>' +
      '<div class="bars" role="img" aria-label="Tus cinco pilares: ' + Q.map(function (q, i) { return q[0] + ' ' + sc[i] + ' de 3'; }).join(', ') + '">' +
      Q.map(function (q, i) { return '<div class="bar' + (i === m && !firm ? ' low' : '') + '" style="--c:' + COL[i] + '"><span>' + q[0] + '</span><i><b style="--w:0%" data-w="' + Math.round(sc[i] / 3 * 100) + '%"></b></i><em>' + sc[i] + '/3</em></div>'; }).join('') + '</div>' +
      '<a class="cta wide" data-co href="' + link + '"' + (ok ? ' rel="noopener"' : '') + '>' + (firm ? 'Quiero mi acceso completo' : 'Empezar por ' + name + ' · ' + esc(cur + ' ' + P.txt)) + '</a>' +
      '<p class="small">Pago único. <a href="#oferta">Ver qué incluye</a></p>' +
      '<button type="button" class="redo">Repetir la prueba</button></div>';
    requestAnimationFrame(function () { requestAnimationFrame(function () { $('.bar b', box).forEach(function (b) { b.style.setProperty('--w', b.dataset.w); }); }); });
    box.querySelector('.redo').onclick = function () { qi = 0; sc = []; ask(); };
    var h = $1('#res-h'); if (h) h.focus({ preventScroll: true });
    track('Lead', { content_name: 'Diagnostico 5 Pilares', value: 0, currency: CUR, variant: 'v18' });
  }
  if (box) ask(true);

  /* ---------- prova social: só com dados reais no config ---------- */
  (function () {
    var deps = Array.isArray(C.depoimentos) ? C.depoimentos : [], prints = Array.isArray(C.prints) ? C.prints : [];
    var g = $1('#ps-grid'), n = 0;
    deps.forEach(function (d) {
      if (!d || !d.texto) return;
      var b = document.createElement('blockquote'); b.innerHTML = '<p></p><footer></footer>';
      b.firstChild.textContent = '«' + d.texto + '»'; b.lastChild.textContent = [d.nome, d.local].filter(Boolean).join(' · ');
      g.appendChild(b); n++;
    });
    prints.forEach(function (u) {
      if (!(https(u) || /^assets\//.test(u || ''))) return;
      var i = document.createElement('img'); i.src = u; i.alt = 'Mensaje de un cliente'; i.loading = 'lazy'; g.appendChild(i); n++;
    });
    if (n) $1('#prueba-social').hidden = false;
  })();

  /* ---------- carrossel das telas ---------- */
  (function () {
    var tr = $1('#track'); if (!tr) return;
    var slides = $('.slide', tr), dots = $1('#dots');
    slides.forEach(function () { dots.appendChild(document.createElement('i')); });
    function idx() { var c = tr.scrollLeft + tr.clientWidth / 2, best = 0, bd = 1e9; slides.forEach(function (s, i) { var d = Math.abs(s.offsetLeft + s.offsetWidth / 2 - c); if (d < bd) { bd = d; best = i; } }); return best; }
    function upd() { var i = idx(); $('i', dots).forEach(function (d, k) { d.classList.toggle('on', k === i); }); }
    function go(i) { i = Math.max(0, Math.min(slides.length - 1, i)); var s = slides[i]; tr.scrollTo({ left: s.offsetLeft - (tr.clientWidth - s.offsetWidth) / 2, behavior: RM ? 'auto' : 'smooth' }); }
    $1('#prev').onclick = function () { go(idx() - 1); };
    $1('#next').onclick = function () { go(idx() + 1); };
    tr.addEventListener('scroll', function () { requestAnimationFrame(upd); }, { passive: true });
    upd();
  })();

  /* ---------- perguntas: uma aberta por vez ---------- */
  $('.faq details').forEach(function (d) {
    d.addEventListener('toggle', function () { if (d.open) $('.faq details').forEach(function (o) { if (o !== d) o.open = false; }); });
  });

  /* ---------- topo e barra fixa ---------- */
  var top = $1('#top'), dock = $1('#dock'), cine = $1('#cine'), plan = $1('.plan'), fin = $1('.final');
  var ticking = false;
  function onScroll() {
    ticking = false;
    var cineEnd = cine ? cine.offsetTop + cine.offsetHeight - innerHeight : 0;
    top.classList.toggle('solid', scrollY > cineEnd - 10);
    if (dock) {
      var pr = plan.getBoundingClientRect(), fr = fin.getBoundingClientRect();
      var show = scrollY > cineEnd + innerHeight * 0.6 && !(pr.top < innerHeight && pr.bottom > 0) && fr.top > innerHeight * 0.5;
      dock.classList.toggle('on', show); dock.setAttribute('aria-hidden', !show); $1('a', dock).tabIndex = show ? 0 : -1;
    }
  }
  addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  addEventListener('resize', onScroll);

  /* entrada dos blocos */
  var io = ('IntersectionObserver' in window) ? new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 }) : null;
  $('[data-rv]').forEach(function (e, i) { e.style.setProperty('--d', ((i % 3) * 0.08) + 's'); if (io && !RM) io.observe(e); else e.classList.add('in'); });

  /* ---------- sequência da torre ---------- */
  function cinema() {
    if (RM || !window.gsap || !window.ScrollTrigger || !cine) { root.classList.add('no-cine'); return; }
    gsap.registerPlugin(ScrollTrigger);

    if (FINE && window.Lenis && innerWidth >= 900) {
      var lenis = new Lenis({ lerp: 0.1, smoothWheel: true });
      root.classList.add('lenis');
      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
      gsap.ticker.lagSmoothing(0);
      $('a[href^="#"]').forEach(function (a) {
        a.addEventListener('click', function (e) {
          var id = a.getAttribute('href'); if (id.length < 2) return;
          var el = $1(id); if (!el) return; e.preventDefault(); lenis.scrollTo(el, { offset: -70, duration: 1.4 });
        });
      });
    }

    var cam = $1('#cam'), shade = $1('.anchor-shade'), texts = $('.ct'), hudN = $1('#hud-n'), hudB = $1('#hud-bar');
    /* pontos da imagem (1199 × 1312): centro da torre e de cada andar */
    var FL = { full: [600, 660], esp: [600, 1100], fin: [600, 915], car: [600, 690], rel: [600, 455], sal: [600, 245] };
    var V = { s: 0, x: 0, y: 0, ax: 0, ay: 0 };
    function sizes() {
      var w = innerWidth, h = innerHeight, mob = w < 761;
      return {
        full: mob ? Math.min(h * 0.62 / 1312, w * 1.05 / 1199) : Math.min(h * 0.94 / 1312, w * 0.6 / 1199),
        floor: mob ? w * 1.3 / 820 : Math.max(w * 0.66 / 820, h * 0.36 / 165),
        axFull: mob ? 0.5 : 0.68, axFloor: mob ? 0.5 : 0.64,
        ay: mob ? 0.36 : 0.5,
        axLast: mob ? 0.5 : 0.74, ayLast: mob ? 0.3 : 0.5, lastK: mob ? 0.85 : 1
      };
    }
    function apply() {
      var w = innerWidth, h = innerHeight;
      cam.style.transform = 'translate3d(' + (w * V.ax - V.x * V.s).toFixed(1) + 'px,' + (h * V.ay - V.y * V.s).toFixed(1) + 'px,0) scale(' + V.s.toFixed(4) + ')';
    }
    function shot(p, zoom, S, last) { return { x: FL[p][0], y: FL[p][1], s: zoom ? S.floor : S.full * (last ? S.lastK : 1), ax: zoom ? S.axFloor : (last ? S.axLast : S.axFull), ay: last ? S.ayLast : S.ay }; }

    var tl;
    function build() {
      if (tl) { tl.scrollTrigger.kill(); tl.kill(); }
      var S = sizes();
      var start = shot('full', false, S);
      start.s *= 0.86;
      gsap.set(V, start); apply();
      gsap.set(texts, { autoAlpha: 0, y: 40, filter: 'blur(10px)' });
      gsap.set(texts[0], { autoAlpha: 1, y: 0, filter: 'blur(0px)' });
      gsap.set(shade, { opacity: 0 });
      tl = gsap.timeline({ defaults: { ease: 'none' }, onUpdate: apply,
        scrollTrigger: { trigger: cine, start: 'top top', end: 'bottom bottom', scrub: 0.9, invalidateOnRefresh: true,
          onUpdate: function (st) {
            var n = Math.max(0, Math.min(5, Math.floor(st.progress * 6.2)));
            hudN.textContent = '0' + n; hudB.style.transform = 'scaleX(' + st.progress.toFixed(3) + ')';
          } } });
      var seq = [['full', false], ['esp', true], ['fin', true], ['car', true], ['rel', true], ['sal', true], ['full', false]];
      seq.forEach(function (sh, k) {
        var at = k * 2;
        tl.to(V, Object.assign(shot(sh[0], sh[1], S, k === seq.length - 1), { duration: k === 0 ? 0.6 : 1.2, ease: 'power2.inOut' }), k === 0 ? 0 : at - 1.1);
        if (k > 0) tl.to(texts[k], { autoAlpha: 1, y: 0, filter: 'blur(0px)', duration: 0.45, ease: 'power2.out' }, at + 0.05);
        if (k < seq.length - 1) tl.to(texts[k], { autoAlpha: 0, y: -40, filter: 'blur(8px)', duration: 0.4, ease: 'power2.in' }, at + 1.25);
      });
      tl.to(shade, { opacity: 1, duration: 0.6 }, 12.3);
      tl.to('.cine-cue', { autoAlpha: 0, duration: 0.4 }, 0.5);
      tl.to({}, { duration: 1.2 });
    }
    build();
    var rt; addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(function () { build(); ScrollTrigger.refresh(); }, 200); });
    addEventListener('load', function () { ScrollTrigger.refresh(); });
  }
  cinema();
  onScroll();
})();
