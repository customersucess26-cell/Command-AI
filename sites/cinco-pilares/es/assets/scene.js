/* Los 5 Pilares · cena "Amanecer en cinco columnas"
   Templo de cinco colunas desenhado em canvas 2D, em tempo real.
   Estado controlado de fora: amb (luz ambiente), lit[5] (luz de cada pilar),
   crack (brilho da rachadura do Pilar Ancla), dawn (amanhecer final). */
(function () {
  'use strict';

  var PILAR = [[87, 199, 154], [180, 140, 240], [240, 165, 74], [79, 194, 221], [139, 144, 245]];
  var GOLD = [232, 184, 120];
  var STONE = [201, 187, 164];
  var STONE_D = [22, 19, 16];

  function mix(a, b, t) { return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]; }
  function rgb(c, a) { return 'rgba(' + (c[0] | 0) + ',' + (c[1] | 0) + ',' + (c[2] | 0) + ',' + (a == null ? 1 : a) + ')'; }
  function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }

  /* rachadura: caminho irregular fixo, em coordenadas da coluna (x -0.5..0.5, y 0..1) */
  var CRACK = [[0.08, 0], [0.02, 0.06], [0.12, 0.13], [-0.04, 0.22], [0.06, 0.29], [-0.1, 0.38], [0.03, 0.45],
    [-0.06, 0.53], [0.1, 0.6], [-0.02, 0.68], [0.07, 0.76], [-0.08, 0.84], [0.02, 0.92], [-0.03, 1]];
  var BRANCH = [[-0.1, 0.38], [-0.28, 0.43], [-0.36, 0.5]];
  var BRANCH2 = [[0.1, 0.6], [0.26, 0.63], [0.34, 0.7]];

  function Temple(canvas, opt) {
    opt = opt || {};
    this.c = canvas;
    this.x = canvas.getContext('2d');
    this.anchor = opt.anchor == null ? 3 : opt.anchor;
    this.s = { amb: opt.amb || 0, lit: [0, 0, 0, 0, 0], crack: opt.crack || 0, dawn: opt.dawn || 0, mx: 0, my: 0 };
    this.t = 0;
    this.run = false;
    this.static = !!opt.static;
    var small = Math.min(innerWidth, innerHeight) < 700;
    this.dust = [];
    var n = small ? 46 : 110;
    for (var i = 0; i < n; i++) this.dust.push({ x: Math.random(), y: Math.random(), z: 0.3 + Math.random() * 0.7, v: 0.2 + Math.random() * 0.8, p: Math.random() * 6.28 });
    this.resize();
    var self = this;
    addEventListener('resize', function () { self.resize(); if (!self.run) self.draw(); });
    if ('IntersectionObserver' in window && !this.static) {
      new IntersectionObserver(function (es) {
        es.forEach(function (e) { e.isIntersecting ? self.start() : self.stop(); });
      }).observe(canvas);
    }
    this.draw();
  }

  Temple.prototype.resize = function () {
    var r = this.c.getBoundingClientRect();
    var dpr = Math.min(window.devicePixelRatio || 1, r.width < 700 ? 1.5 : 1.75);
    this.w = Math.max(1, r.width); this.h = Math.max(1, r.height);
    this.c.width = Math.round(this.w * dpr); this.c.height = Math.round(this.h * dpr);
    this.x.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.layout();
  };

  Temple.prototype.layout = function () {
    var w = this.w, h = this.h, tall = w / h < 1.05;
    var x0, x1, top, floor;
    if (tall) { x0 = 0.06; x1 = 0.94; top = 0.44; floor = 0.9; }
    else if (this.wide === false) { x0 = 0.1; x1 = 0.9; top = 0.16; floor = 0.86; }
    else { x0 = 0.44; x1 = 0.97; top = 0.13; floor = 0.85; }
    if (this.centered) { x0 = tall ? 0.06 : 0.12; x1 = tall ? 0.94 : 0.88; }
    var span = (x1 - x0) * w, step = span / 5;
    this.L = { tall: tall, step: step, cw: Math.min(step * 0.44, h * 0.11), top: top * h, floor: floor * h, x0: x0 * w };
    this.cols = [];
    for (var i = 0; i < 5; i++) this.cols.push(this.L.x0 + step * (i + 0.5));
  };

  Temple.prototype.start = function () {
    if (this.run || this.static) return;
    this.run = true;
    var self = this, last = performance.now();
    function f(t) {
      if (!self.run) return;
      self.t += Math.min(50, t - last) / 1000; last = t;
      self.draw();
      self.raf = requestAnimationFrame(f);
    }
    this.raf = requestAnimationFrame(f);
  };
  Temple.prototype.stop = function () { this.run = false; cancelAnimationFrame(this.raf); };

  Temple.prototype.draw = function () {
    var g = this.x, w = this.w, h = this.h, s = this.s, L = this.L, t = this.t;
    var amb = clamp(s.amb), dawn = clamp(s.dawn);
    var px = s.mx * 10, py = s.my * 6;

    /* fundo: noite fria que esquenta no amanhecer */
    var bg = g.createLinearGradient(0, 0, 0, h);
    bg.addColorStop(0, rgb(mix([7, 6, 9], [58, 34, 18], dawn)));
    bg.addColorStop(0.55, rgb(mix([12, 10, 10], [120, 74, 36], dawn)));
    bg.addColorStop(0.85, rgb(mix([16, 13, 11], [176, 116, 58], dawn)));
    bg.addColorStop(1, rgb(mix([8, 7, 7], [70, 44, 22], dawn)));
    g.globalCompositeOperation = 'source-over';
    g.fillStyle = bg; g.fillRect(0, 0, w, h);

    /* parede do fundo com vãos (arcos sugeridos) */
    var wallA = 0.05 + amb * 0.05 + dawn * 0.05;
    g.fillStyle = rgb(mix([30, 26, 22], [210, 160, 100], dawn), wallA);
    for (var i = 0; i < 6; i++) {
      var ax = L.x0 - L.step * 0.5 + L.step * i + px * 0.3;
      g.fillRect(ax - L.step * 0.18, L.top + (L.floor - L.top) * 0.08, L.step * 0.36, (L.floor - L.top) * 0.92);
    }

    /* feixe principal vindo do alto à esquerda */
    g.globalCompositeOperation = 'lighter';
    var beamA = 0.17 * amb + 0.18 * dawn;
    if (beamA > 0.002) {
      var bx = L.tall ? w * 0.1 : w * 0.3;
      var bgd = g.createLinearGradient(bx, 0, bx + w * 0.5, h);
      var bc = mix([220, 170, 110], GOLD, dawn);
      bgd.addColorStop(0, rgb(bc, beamA * 1.1));
      bgd.addColorStop(0.6, rgb(bc, beamA * 0.45));
      bgd.addColorStop(1, rgb(bc, 0));
      g.fillStyle = bgd;
      g.beginPath();
      g.moveTo(bx - w * 0.03 + px, -10); g.lineTo(bx + w * 0.08 + px, -10);
      g.lineTo(bx + w * 0.62 + px * 1.6, h); g.lineTo(bx + w * 0.3 + px * 1.6, h);
      g.closePath(); g.fill();
    }

    /* raios de amanhecer entre as colunas */
    if (dawn > 0.01) {
      for (var r = 0; r < 6; r++) {
        var rx = L.x0 + L.step * r + px * 0.6;
        var rg = g.createLinearGradient(0, L.top - h * 0.1, 0, L.floor);
        var flick = 0.85 + 0.15 * Math.sin(t * 0.6 + r);
        rg.addColorStop(0, rgb(GOLD, 0));
        rg.addColorStop(0.35, rgb(GOLD, 0.16 * dawn * flick));
        rg.addColorStop(1, rgb([255, 200, 140], 0.05 * dawn));
        g.fillStyle = rg;
        g.beginPath();
        g.moveTo(rx - L.step * 0.08, L.top - h * 0.12); g.lineTo(rx + L.step * 0.08, L.top - h * 0.12);
        g.lineTo(rx + L.step * 0.3, L.floor); g.lineTo(rx - L.step * 0.3, L.floor);
        g.closePath(); g.fill();
      }
    }

    /* feixes coloridos de cada pilar */
    for (var k = 0; k < 5; k++) {
      var l = clamp(s.lit[k]);
      if (l < 0.01) continue;
      var cx = this.cols[k] + px, c = PILAR[k];
      var lg = g.createLinearGradient(0, -20, 0, L.floor + 20);
      var fl = 0.9 + 0.1 * Math.sin(t * 1.3 + k * 2);
      lg.addColorStop(0, rgb(c, 0));
      lg.addColorStop(0.25, rgb(c, 0.22 * l * fl));
      lg.addColorStop(0.95, rgb(c, 0.1 * l));
      lg.addColorStop(1, rgb(c, 0));
      g.fillStyle = lg;
      g.beginPath();
      g.moveTo(cx - L.cw * 0.5 - L.step * 0.15, -20); g.lineTo(cx + L.cw * 0.2 - L.step * 0.15, -20);
      g.lineTo(cx + L.cw * 1.25, L.floor); g.lineTo(cx - L.cw * 1.25, L.floor);
      g.closePath(); g.fill();
      /* poça de luz no piso */
      var pg = g.createRadialGradient(cx, L.floor, 0, cx, L.floor, L.cw * 2.6);
      pg.addColorStop(0, rgb(c, 0.32 * l)); pg.addColorStop(1, rgb(c, 0));
      g.fillStyle = pg;
      g.save(); g.translate(cx, L.floor); g.scale(1, 0.22); g.translate(-cx, -L.floor);
      g.beginPath(); g.arc(cx, L.floor, L.cw * 2.6, 0, 6.283); g.fill(); g.restore();
    }

    /* piso */
    g.globalCompositeOperation = 'source-over';
    var fg = g.createLinearGradient(0, L.floor, 0, h);
    fg.addColorStop(0, rgb(mix([24, 20, 17], [150, 98, 50], dawn), 0.92));
    fg.addColorStop(1, rgb(mix([6, 5, 5], [52, 32, 16], dawn), 1));
    g.fillStyle = fg; g.fillRect(0, L.floor, w, h - L.floor);
    g.fillStyle = rgb(mix([80, 70, 60], [255, 210, 150], dawn), 0.12 + 0.2 * amb + 0.2 * dawn);
    g.fillRect(0, L.floor, w, 1);

    /* colunas */
    for (var j = 0; j < 5; j++) this.column(j, this.cols[j] + px, py);

    /* poeira suspensa */
    g.globalCompositeOperation = 'lighter';
    for (var d = 0; d < this.dust.length; d++) {
      var p = this.dust[d];
      var yy = ((p.y - t * 0.012 * p.v) % 1 + 1) % 1;
      var xx = p.x + Math.sin(t * 0.3 * p.v + p.p) * 0.01;
      var X = xx * w + px * p.z * 2, Y = yy * h;
      var near = 0;
      for (var q = 0; q < 5; q++) {
        var dx = (X - this.cols[q]) / (L.step * 0.6);
        near += clamp(s.lit[q]) * Math.exp(-dx * dx);
      }
      var a = (0.05 + amb * 0.18 + dawn * 0.35 + near * 0.5) * p.z * (0.6 + 0.4 * Math.sin(t * 2 * p.v + p.p));
      if (a < 0.02) continue;
      g.fillStyle = rgb(mix([255, 226, 180], GOLD, dawn), Math.min(0.9, a));
      g.beginPath(); g.arc(X, Y, 0.6 + p.z * 1.3, 0, 6.283); g.fill();
    }

    /* vinheta */
    g.globalCompositeOperation = 'source-over';
    var vg = g.createRadialGradient(w * 0.6, h * 0.5, Math.min(w, h) * 0.2, w * 0.6, h * 0.5, Math.max(w, h) * 0.8);
    vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,' + (0.62 - dawn * 0.3) + ')');
    g.fillStyle = vg; g.fillRect(0, 0, w, h);
  };

  Temple.prototype.column = function (i, cx, py) {
    var g = this.x, s = this.s, L = this.L, cw = L.cw, t = this.t;
    var l = clamp(s.lit[i]), amb = clamp(s.amb), dawn = clamp(s.dawn);
    var c = PILAR[i];
    var light = clamp(0.12 + amb * 0.52 + l * 0.6 + dawn * 0.75);
    var base = mix(STONE_D, STONE, light * 0.85);
    base = mix(base, c, l * 0.32 * (1 - dawn * 0.6));
    base = mix(base, [236, 190, 130], dawn * 0.3);

    var top = L.top + py * 0.2, floor = L.floor;
    var abH = cw * 0.2, echH = cw * 0.26, plH = cw * 0.22, tbH = cw * 0.14;
    var sTop = top + abH + echH, sBot = floor - plH - tbH;

    /* sombra no piso */
    g.fillStyle = 'rgba(0,0,0,' + (0.35 + dawn * 0.1) + ')';
    g.beginPath(); g.ellipse(cx + cw * 0.5, floor + 3, cw * 1.1, cw * 0.12, 0, 0, 6.283); g.fill();

    /* fuste com sombreamento cilíndrico (luz vinda da esquerda) */
    var sg = g.createLinearGradient(cx - cw / 2, 0, cx + cw / 2, 0);
    sg.addColorStop(0, rgb(mix(base, [0, 0, 0], 0.55)));
    sg.addColorStop(0.22, rgb(mix(base, [255, 245, 225], 0.12 + l * 0.12)));
    sg.addColorStop(0.5, rgb(base));
    sg.addColorStop(0.82, rgb(mix(base, [0, 0, 0], 0.6)));
    sg.addColorStop(1, rgb(mix(base, [0, 0, 0], 0.8)));
    g.fillStyle = sg;
    g.fillRect(cx - cw / 2, sTop, cw, sBot - sTop);

    /* caneluras */
    g.globalAlpha = 0.28;
    for (var f = 1; f < 8; f++) {
      var fx = cx - cw / 2 + cw * f / 8;
      var edge = Math.abs(f / 8 - 0.4);
      g.fillStyle = rgb([0, 0, 0], 0.5 + edge);
      g.fillRect(fx - 0.6, sTop, 1.2, sBot - sTop);
    }
    g.globalAlpha = 1;

    /* luz de topo sobre o fuste (tom do pilar) */
    if (l > 0.01) {
      var tg = g.createLinearGradient(0, sTop, 0, sBot);
      tg.addColorStop(0, rgb(c, 0.28 * l)); tg.addColorStop(0.6, rgb(c, 0.06 * l)); tg.addColorStop(1, rgb(c, 0));
      g.globalCompositeOperation = 'lighter';
      g.fillStyle = tg; g.fillRect(cx - cw / 2, sTop, cw, sBot - sTop);
      g.globalCompositeOperation = 'source-over';
    }

    /* capitel e base */
    function slab(y, hh, ww, k) {
      var bgd = g.createLinearGradient(cx - ww / 2, 0, cx + ww / 2, 0);
      bgd.addColorStop(0, rgb(mix(base, [0, 0, 0], 0.5)));
      bgd.addColorStop(0.25, rgb(mix(base, [255, 245, 225], 0.1 * k)));
      bgd.addColorStop(0.75, rgb(mix(base, [0, 0, 0], 0.55)));
      bgd.addColorStop(1, rgb(mix(base, [0, 0, 0], 0.75)));
      g.fillStyle = bgd; g.fillRect(cx - ww / 2, y, ww, hh);
      g.fillStyle = rgb(mix(base, [255, 245, 230], 0.25), 0.5);
      g.fillRect(cx - ww / 2, y, ww, 1);
    }
    slab(top, abH, cw * 1.42, 1);
    slab(top + abH, echH, cw * 1.16, 1);
    slab(sBot, tbH, cw * 1.16, 1);
    slab(sBot + tbH, plH, cw * 1.42, 1);

    /* rachadura do Pilar Ancla */
    if (i === this.anchor) {
      var cr = clamp(s.crack), H = sBot - sTop;
      var pts = function (arr) {
        g.beginPath();
        arr.forEach(function (p, n) { var X = cx + p[0] * cw, Y = sTop + p[1] * H; n ? g.lineTo(X, Y) : g.moveTo(X, Y); });
      };
      var heal = dawn; /* no amanhecer a coluna está restaurada */
      g.lineJoin = 'round';
      g.strokeStyle = 'rgba(0,0,0,' + (0.85 * (1 - heal)) + ')';
      g.lineWidth = Math.max(1.6, cw * 0.035);
      pts(CRACK); g.stroke(); pts(BRANCH); g.stroke(); pts(BRANCH2); g.stroke();
      if (cr > 0.01) {
        var pulse = 0.75 + 0.25 * Math.sin(t * 1.6);
        g.globalCompositeOperation = 'lighter';
        g.shadowColor = rgb(GOLD, 0.9); g.shadowBlur = cw * 0.5;
        g.strokeStyle = rgb([255, 200, 120], 0.8 * cr * pulse * (1 - heal * 0.7));
        g.lineWidth = Math.max(1, cw * 0.018);
        pts(CRACK); g.stroke(); pts(BRANCH); g.stroke(); pts(BRANCH2); g.stroke();
        g.shadowBlur = 0;
        var mg = g.createRadialGradient(cx, sTop + H * 0.5, 0, cx, sTop + H * 0.5, cw * 1.8);
        mg.addColorStop(0, rgb(GOLD, 0.16 * cr * pulse * (1 - heal))); mg.addColorStop(1, rgb(GOLD, 0));
        g.fillStyle = mg; g.fillRect(cx - cw * 2, sTop, cw * 4, H);
        g.globalCompositeOperation = 'source-over';
      }
    }

    /* reflexo no piso polido */
    var rg = g.createLinearGradient(0, floor, 0, floor + (this.h - floor));
    rg.addColorStop(0, rgb(mix(base, c, l * 0.4), 0.16 + l * 0.12 + dawn * 0.1));
    rg.addColorStop(1, rgb(base, 0));
    g.fillStyle = rg; g.fillRect(cx - cw * 0.7, floor + 1, cw * 1.4, this.h - floor);
  };

  window.Temple = Temple;
})();
