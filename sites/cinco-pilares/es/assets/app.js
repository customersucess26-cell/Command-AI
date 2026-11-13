/* Los 5 Pilares · v17 · lógica da página
   preço e checkout (com UTM), píxel, teste de 5 perguntas, contagem regressiva,
   prova social (só com dados reais), cenas e animações. */
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

  /* ---------- configuração ---------- */
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

  /* preço "de" só quando é real e maior */
  if (C.precoDe) {
    var De = parse(C.precoDe);
    if (De.num > P.num) {
      $('[data-price-from]').forEach(function (e) { e.textContent = cur + ' ' + De.txt; });
      var sv = De.num - P.num, pct = Math.round((1 - P.num / De.num) * 100);
      $('[data-save]').forEach(function (e) { e.textContent = cur + ' ' + sv.toFixed(2).replace('.', ',') + ' (' + pct + '%)'; });
      $1('#from').hidden = false; $1('#save').hidden = false;
    }
  }

  /* lançamento: só com data futura real e preço posterior maior */
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
  track('ViewContent', { content_name: PROD, content_type: 'product', value: P.num, currency: CUR, variant: 'v17' });

  var ok = !!https(C.checkout);
  function ckUrl(extra) {
    if (!ok) return '#oferta';
    try {
      var u = new URL(C.checkout), q = new URLSearchParams(location.search);
      ['fbclid', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'src', 'sck'].forEach(function (k) { if (q.get(k)) u.searchParams.set(k, q.get(k)); });
      if (!u.searchParams.get('src') && q.get('utm_source')) u.searchParams.set('src', q.get('utm_source').slice(0, 60));
      var sck = [q.get('utm_campaign'), q.get('utm_content'), 'v17', extra].filter(Boolean).join('|');
      if (!u.searchParams.get('sck') && sck) u.searchParams.set('sck', sck.slice(0, 120));
      return u.toString();
    } catch (e) { return C.checkout; }
  }
  var CK = ckUrl();
  function wire(a) { if (ok) { a.href = CK; a.rel = 'noopener'; } }
  $('[data-co]').forEach(wire);
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
  function swap(html, after) {
    if (RM || !window.gsap) { box.innerHTML = html; if (after) after(); return; }
    gsap.to(box.children, { opacity: 0, y: -10, duration: 0.22, ease: 'power2.in', onComplete: function () {
      box.innerHTML = html; if (after) after();
      gsap.from(box.children, { opacity: 0, y: 14, duration: 0.5, ease: 'power3.out', stagger: 0.05 });
    } });
  }
  function ask(first) {
    var q = Q[qi]; box.style.setProperty('--c', COL[qi]);
    var html = prog(qi) + '<p class="q-n">Pregunta ' + (qi + 1) + ' de 5 · ' + q[0] + '</p><p class="q-t" id="q-t" tabindex="-1">' + esc(q[1]) + '</p><div class="q-o" role="group" aria-labelledby="q-t">' +
      q[2].map(function (o, k) { return '<button type="button" data-k="' + (k + 1) + '"><b>' + 'ABC'.charAt(k) + '</b><span>' + esc(o) + '</span></button>'; }).join('') +
      '</div><p class="q-priv">Tus respuestas no salen de tu pantalla.</p>';
    var bind = function () {
      $('button', box).forEach(function (b) {
        b.onclick = function () {
          if (!sc.length) track('QuizStart', {}, true);
          sc.push(+b.dataset.k); qi++;
          if (qi < 5) ask(); else res();
        };
      });
      if (!first) { var t = $1('#q-t'); if (t) t.focus({ preventScroll: true }); }
    };
    if (first) { box.innerHTML = html; bind(); } else swap(html, bind);
  }
  function res() {
    var m = 0; sc.forEach(function (s, i) { if (s < sc[m]) m = i; });
    var name = Q[m][0], firm = sc[m] === 3;
    var link = ok ? esc(ckUrl('quiz-' + name.toLowerCase())) : '#oferta';
    box.style.setProperty('--c', firm ? 'var(--gold)' : COL[m]);
    var html = '<div class="res">' + prog(5) +
      '<p class="q-n">Tu resultado</p><h3 id="res-h" tabindex="-1">' + (firm ? 'Tus pilares están firmes.' : 'Tu Pilar Ancla hoy: ' + name) + '</h3>' +
      '<p>' + (firm ? 'Buen punto de partida. El sistema te ayuda a sostenerlos y a subir cada uno.' : REC[name]) + '</p>' +
      (function () {
        var cmp = box.clientWidth < 460;
        return '<div class="res-tower' + (cmp ? ' compact-w' : '') + '">' + window.Tower({ id: 'r', compact: cmp, anchor: firm ? -1 : m, scores: sc, callouts: cmp ? 'none' : 'score',
          lit: sc.map(function (v) { return 0.12 + v / 3 * 0.8; }), label: 'Tus cinco pilares: ' + Q.map(function (q, i) { return q[0] + ' ' + sc[i] + ' de 3'; }).join(', ') }) + '</div>';
      })() +
      (box.clientWidth < 460 ? '<div class="rcols-l" aria-hidden="true">' + Q.map(function (q, i) { return '<span><b>' + q[0] + '</b>' + sc[i] + '/3</span>'; }).join('') + '</div>' : '') +
      '<a class="btn btn-gold wide" data-co href="' + link + '"' + (ok ? ' rel="noopener"' : '') + '>' + (firm ? 'Comprar acceso completo' : 'Empezar por ' + name + ' · ' + esc(cur + ' ' + P.txt)) + '</a>' +
      '<p class="micro">Pago único. <a href="#oferta">Ver qué incluye</a></p>' +
      '<button type="button" class="redo">Repetir la prueba</button></div>';
    swap(html, function () {
      box.querySelector('.redo').onclick = function () { qi = 0; sc = []; ask(); };
      var h = $1('#res-h'); if (h) h.focus({ preventScroll: true });
    });
    track('Lead', { content_name: 'Diagnostico 5 Pilares', value: 0, currency: CUR, variant: 'v17' });
    /* destaca o livro do pilar âncora */
    $('.pillar').forEach(function (e) { e.classList.toggle('hl', !firm && +e.dataset.m === m); });
    if (!firm) openPillar(m, false);
  }
  if (box) ask(true);

  /* ---------- prova social: só com dados reais no config ---------- */
  (function () {
    var deps = Array.isArray(C.depoimentos) ? C.depoimentos : [], prints = Array.isArray(C.prints) ? C.prints : [];
    var g = $1('#ps-grid'), n = 0;
    deps.forEach(function (d) {
      if (!d || !d.texto) return;
      var b = document.createElement('blockquote');
      b.innerHTML = '<p></p><footer></footer>';
      b.firstChild.textContent = '«' + d.texto + '»';
      b.lastChild.textContent = [d.nome, d.local].filter(Boolean).join(' · ');
      g.appendChild(b); n++;
    });
    prints.forEach(function (u) {
      if (!(https(u) || /^assets\//.test(u || ''))) return;
      var i = document.createElement('img'); i.src = u; i.alt = 'Mensaje de un cliente'; i.loading = 'lazy'; g.appendChild(i); n++;
    });
    if (n) $1('#prueba-social').hidden = false;
  })();

  /* ---------- livros: abrir um painel ---------- */
  var pillars = $('.pillar');
  function openPillar(i, focus) {
    pillars.forEach(function (p, k) {
      var on = k === i; p.classList.toggle('on', on);
      var b = $1('.pillar-h', p); b.setAttribute('aria-expanded', on);
    });
    if (focus) { var b = $1('.pillar-b', pillars[i]); if (b) b.setAttribute('tabindex', '-1'); }
  }
  pillars.forEach(function (p, i) {
    $1('.pillar-h', p).addEventListener('click', function () { openPillar(p.classList.contains('on') && innerWidth < 900 ? -1 : i); });
    if (FINE) p.addEventListener('mouseenter', function () { if (innerWidth >= 900) openPillar(i); });
  });
  if (pillars.length && innerWidth >= 900) openPillar(0);

  /* ---------- perguntas frequentes: uma aberta por vez ---------- */
  $('.faq details').forEach(function (d) {
    d.addEventListener('toggle', function () { if (d.open) $('.faq details').forEach(function (o) { if (o !== d) o.open = false; }); });
  });

  /* ---------- topo, indicador e barra fixa ---------- */
  var top = $1('#top'), dock = $1('#dock'), meter = $('#meter i');
  var quizSec = $1('#prueba-rapida'), offer = $1('#oferta'), fin = $1('#final');
  var ticking = false;
  function onScroll() {
    ticking = false;
    var y = scrollY, H = document.documentElement.scrollHeight - innerHeight, f = H > 0 ? Math.min(1, Math.max(0, y / H)) : 0;
    top.classList.toggle('solid', y > 40);
    meter.forEach(function (s, i) { s.style.setProperty('--f', Math.min(1, Math.max(0, f * 5 - i)).toFixed(3)); });
    if (dock) {
      var qb = quizSec.getBoundingClientRect().bottom, ob = offer.getBoundingClientRect(), fb = fin.getBoundingClientRect();
      var inPrice = $1('#price-card').getBoundingClientRect();
      var show = qb < 0 && !(inPrice.top < innerHeight && inPrice.bottom > 0) && fb.top > innerHeight * 0.6;
      dock.classList.toggle('on', show);
      dock.setAttribute('aria-hidden', !show);
      $1('a', dock).tabIndex = show ? 0 : -1;
    }
  }
  addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  addEventListener('resize', onScroll); onScroll();

  /* cor ambiente por seção */
  if ('IntersectionObserver' in window) {
    var ao = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) root.style.setProperty('--amb', e.target.dataset.amb); }); }, { rootMargin: '-45% 0px -50% 0px' });
    $('[data-amb]').forEach(function (s) { ao.observe(s); });
  }

  /* entrada simples dos blocos marcados */
  var io = ('IntersectionObserver' in window) ? new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -10% 0px', threshold: 0.1 }) : null;
  $('[data-rv]').forEach(function (e, i) { e.style.setProperty('--d', ((i % 4) * 0.08) + 's'); if (io && !RM) io.observe(e); else e.classList.add('in'); });

  /* pilares que caem e se levantam */
  (function () {
    var fall = $1('#fall'), btn = $1('#fall-btn'), cap = $1('#fall-cap');
    if (!fall || !btn) return;
    btn.addEventListener('click', function () {
      var up = !fall.classList.contains('up'); fall.classList.toggle('up', up);
      btn.textContent = up ? btn.dataset.b : btn.dataset.a; cap.textContent = up ? cap.dataset.b : cap.dataset.a;
    });
  })();

  /* ---------- torres dos 5 pilares ---------- */
  var T = window.Tower, htw = $1('#hero-tower'), gtw = $1('#giro-tower'), ftw = $1('#fall-tower'), fin = $1('#final-tower');
  if (T) {
    if (htw) htw.innerHTML = T({ id: 'h', compact: true, anchor: 3, lit: RM ? [0.7, 0.7, 0.7, 0.15, 0.7] : [0, 0, 0, 0, 0] });
    if (gtw) gtw.innerHTML = T({ id: 'g', anchor: -1, lit: [0.06, 0.06, 0.06, 0.06, 0.06], callouts: innerWidth < 600 ? 'none' : 'name', compact: innerWidth < 600 });
    if (ftw) ftw.innerHTML = T({ id: 'a', anchor: 3, lit: [0.25, 0.25, 0.25, 0.12, 0.25], callouts: innerWidth < 600 ? 'none' : 'name', compact: innerWidth < 600 });
    if (fin) fin.innerHTML = T({ id: 'f', compact: true, anchor: -1, lit: [0.85, 0.85, 0.85, 0.85, 0.85] });
  }
  function setL(el, q, v) { var t = el && el.querySelector('.tier[data-q="' + q + '"]'); if (t) t.style.setProperty('--l', v); }

  /* ---------- animações (GSAP) ---------- */
  function splitWords(h) {
    var t = h.textContent.trim(); h.setAttribute('aria-label', t); h.textContent = '';
    t.split(/\s+/).forEach(function (w, i, a) {
      var o = document.createElement('span'); o.className = 'w'; o.setAttribute('aria-hidden', 'true');
      var s = document.createElement('span'); s.textContent = w; o.appendChild(s); h.appendChild(o);
      if (i < a.length - 1) h.appendChild(document.createTextNode(' '));
    });
    return $('.w>span', h);
  }

  function motion() {
    if (RM || !window.gsap || !window.ScrollTrigger) { if (htw) [0, 1, 2, 4].forEach(function (q) { setL(htw, q, 0.75); }); return; }
    gsap.registerPlugin(ScrollTrigger);

    /* rolagem suave só no desktop com mouse */
    if (FINE && window.Lenis && innerWidth >= 900) {
      var lenis = new Lenis({ lerp: 0.11, smoothWheel: true });
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

    /* abertura: o título surge palavra por palavra e a luz entra no templo */
    var words = splitWords($1('#h1'));
    var tl = gsap.timeline({ defaults: { ease: 'expo.out' } });
    tl.from(words, { yPercent: 115, duration: 1.3, stagger: 0.045 }, 0.25)
      .from('[data-in]', { opacity: 0, y: 24, duration: 1.1, stagger: 0.1 }, 0.7);
    if (htw) {
      /* os anéis acendem de baixo para cima; o ancla (Finanzas) fica apagado e rachado */
      var seq = [0, 3, 2, 1, 4];
      seq.forEach(function (q, k) {
        var o = { v: 0 };
        tl.to(o, { v: q === 3 ? 0.15 : 0.75, duration: 1.1, ease: 'power2.out', onUpdate: function () { setL(htw, q, o.v.toFixed(3)); } }, 0.9 + k * 0.28);
      });
      tl.from('#hero-tower', { opacity: 0, y: 40, duration: 1.6, ease: 'expo.out' }, 0.2);
      gsap.to('.hero-in', { yPercent: -12, opacity: 0, ease: 'none', scrollTrigger: { trigger: '#hero', start: '35% top', end: 'bottom top', scrub: true } });
      if (innerWidth > 760) gsap.to('#hero-tower', { yPercent: -60, ease: 'none', scrollTrigger: { trigger: '#hero', start: 'top top', end: 'bottom top', scrub: true } });
    }

    /* a dor: a lista aparece e o carimbo bate */
    gsap.from('.note li', { opacity: 0, x: -16, duration: 0.6, stagger: 0.12, ease: 'power3.out', scrollTrigger: { trigger: '.note', start: 'top 75%' } });
    gsap.from('.stamp', { scale: 2.4, opacity: 0, rotate: -30, duration: 0.5, ease: 'back.out(2)', scrollTrigger: { trigger: '.note', start: 'top 45%' } });
    gsap.from('.note', { rotate: 4, y: 60, opacity: 0, duration: 1.2, ease: 'expo.out', scrollTrigger: { trigger: '.note', start: 'top 85%' } });
    gsap.from('.symptoms li', { opacity: 0, y: 16, duration: 0.7, stagger: 0.07, ease: 'power3.out', scrollTrigger: { trigger: '.symptoms', start: 'top 80%' } });
    $('.display:not(#h1)').forEach(function (h) {
      gsap.from(h, { opacity: 0, y: 40, duration: 1.2, ease: 'expo.out', scrollTrigger: { trigger: h, start: 'top 85%' } });
    });

    /* a virada: seção fixa no desktop, cada especialista acende um pilar */
    var steps = $('.giro-steps li');
    function giroSet(k) {
      steps.forEach(function (s, i) { s.classList.toggle('on', i === k); });
      var st = k >= 0 ? +steps[k].dataset.step : -2;
      for (var q = 0; q < 5; q++) setL(gtw, q, st === -1 ? 0.35 : (st === q ? 0.85 : 0.05));
    }
    giroSet(-1);
    var mm = gsap.matchMedia();
    mm.add('(min-width:900px)', function () {
      ScrollTrigger.create({
        trigger: '#giro', start: 'top top', end: '+=180%', pin: '.giro-pin', scrub: true,
        onUpdate: function (s) { giroSet(Math.min(steps.length - 1, Math.floor(s.progress * steps.length * 0.999))); }
      });

      /* o sistema: rolagem horizontal pelas telas reais */
      var track = $1('#sis-track');
      var dist = function () { return Math.max(0, track.scrollWidth - innerWidth); };
      gsap.to(track, { x: function () { return -dist(); }, ease: 'none',
        scrollTrigger: { trigger: '.sis-pin', start: 'top top', end: function () { return '+=' + dist(); }, pin: true, scrub: 0.6, invalidateOnRefresh: true } });
    });
    mm.add('(max-width:899px)', function () {
      steps.forEach(function (s, i) {
        ScrollTrigger.create({ trigger: s, start: 'top 70%', end: 'bottom 30%', onToggle: function (st) { if (st.isActive) giroSet(i); } });
      });
    });

    /* o mecanismo: o ancla se levanta sozinha uma vez ao entrar */
    ScrollTrigger.create({ trigger: '#fall', start: 'top 35%', once: true, onEnter: function () {
      setTimeout(function () { var b = $1('#fall-btn'); if (b && !$1('#fall').classList.contains('up')) b.click(); }, 900);
    } });

    /* números e passos */
    gsap.from('.ruta-steps li', { opacity: 0, y: 20, duration: 0.8, stagger: 0.1, ease: 'power3.out', scrollTrigger: { trigger: '.ruta-steps', start: 'top 80%' } });
    gsap.from('.inv li', { opacity: 0, x: -20, duration: 0.7, stagger: 0.06, ease: 'power3.out', scrollTrigger: { trigger: '.inv', start: 'top 80%' } });
    gsap.from('.pillar', { opacity: 0, y: 60, duration: 1.1, stagger: 0.08, ease: 'expo.out', scrollTrigger: { trigger: '#pillars', start: 'top 80%' } });

    /* fechamento: a torre sobe na luz do amanhecer */
    gsap.from('#final-tower', { y: 80, opacity: 0, duration: 1.6, ease: 'expo.out', scrollTrigger: { trigger: '#final', start: 'top 70%' } });
    gsap.from('.final-sky', { opacity: 0, ease: 'none', scrollTrigger: { trigger: '#final', start: 'top bottom', end: 'top 30%', scrub: true } });

    /* botões magnéticos */
    if (FINE) $('.magnetic').forEach(function (b) {
      b.addEventListener('pointermove', function (e) {
        var r = b.getBoundingClientRect();
        b.style.setProperty('--mx', ((e.clientX - r.left - r.width / 2) * 0.18).toFixed(1) + 'px');
        b.style.setProperty('--my', ((e.clientY - r.top - r.height / 2) * 0.28).toFixed(1) + 'px');
      });
      b.addEventListener('pointerleave', function () { b.style.setProperty('--mx', '0px'); b.style.setProperty('--my', '0px'); });
    });

    addEventListener('load', function () { ScrollTrigger.refresh(); });
  }
  motion();

})();
