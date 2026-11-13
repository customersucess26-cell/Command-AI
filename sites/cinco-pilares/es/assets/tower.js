/* Los 5 Pilares · "La torre de los 5 pilares"
   Cinco anéis empilhados (de baixo para cima: Espiritualidad, Finanzas, Carrera, Relaciones, Salud),
   um cômodo de vidro iluminado entre eles e um jardim no topo.
   Tower(opts) devolve o SVG como texto. Cada anel nasce dentro do anel de baixo,
   então inclinar um anel inclina tudo o que está acima dele. */
(function () {
  'use strict';
  /* índices do teste: 0 Salud, 1 Relaciones, 2 Carrera, 3 Finanzas, 4 Espiritualidad */
  var ORDER = [4, 3, 2, 1, 0];
  var COL = ['#57c79a', '#b48cf0', '#f0a54a', '#4fc2dd', '#8b90f5'];
  var NAME = ['Salud', 'Relaciones', 'Carrera', 'Finanzas', 'Espiritualidad'];
  var BAND = ['SALUD', 'RELACIONES', 'CARRERA', 'FINANZAS', 'ESPIRITUALIDAD'];
  var DESC = ['Energía, sueño y cuerpo', 'Familia y vínculos', 'Rumbo y trabajo', 'Dinero en orden', 'Propósito y fe'];
  var ICON = [
    'M12 20s-7-4.4-7-9.6A3.9 3.9 0 0 1 12 8a3.9 3.9 0 0 1 7 2.4C19 15.6 12 20 12 20zM6.5 12.5h3l1.5-2.5 2.5 5 1.5-2.5h3',
    'M9 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM16.5 11.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM3.5 19.5c0-3 2.5-5.5 5.5-5.5s5.5 2.5 5.5 5.5M14.5 14.3c2.9-.4 6 1.5 6 4.7',
    'M4 8.5h16V19H4zM9 8.5V6h6v2.5M4 13h16M11 13v2h2v-2',
    'M6 7.5c0 1.4 2.7 2.5 6 2.5s6-1.1 6-2.5S15.3 5 12 5 6 6.1 6 7.5zM6 7.5V12c0 1.4 2.7 2.5 6 2.5s6-1.1 6-2.5V7.5M6 12v4.5C6 17.9 8.7 19 12 19s6-1.1 6-2.5V12',
    'M12 3.5c2.8 3.6 5 6 5 9.5a5 5 0 0 1-10 0c0-1.8.8-3.2 1.8-4.3.2 1.8 1 2.8 2 2.8-.3-2.8-.6-4.8 1.2-8z'
  ];

  function Tower(o) {
    o = o || {};
    var id = o.id || ('t' + Math.random().toString(36).slice(2, 7));
    var compact = !!o.compact;
    var W = compact ? 340 : 540, cx = W / 2;
    var bandH = 30, wallH = 64, rx0 = compact ? 152 : 156, step = 7;
    var floorBase = 566, H = floorBase + 40;
    var lit = o.lit || [0.5, 0.5, 0.5, 0.5, 0.5];
    var anchor = o.anchor == null ? -1 : o.anchor;
    var scores = o.scores || null;
    var callouts = o.callouts || (compact ? 'none' : 'name');

    var defs = '<defs>' +
      '<radialGradient id="' + id + 'sky" cx="50%" cy="45%" r="50%"><stop offset="0" stop-color="#e8b878" stop-opacity=".22"/><stop offset="1" stop-color="#e8b878" stop-opacity="0"/></radialGradient>' +
      '<linearGradient id="' + id + 'glass" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity=".02"/><stop offset=".3" stop-color="#fff" stop-opacity=".16"/><stop offset=".55" stop-color="#fff" stop-opacity=".05"/><stop offset="1" stop-color="#fff" stop-opacity=".02"/></linearGradient>' +
      '<radialGradient id="' + id + 'leaf" cx="40%" cy="30%" r="70%"><stop offset="0" stop-color="#b9e38a"/><stop offset=".55" stop-color="#5e9e4a"/><stop offset="1" stop-color="#2c5a2c"/></radialGradient>' +
      '<filter id="' + id + 'blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>';
    ORDER.forEach(function (q) {
      var c = COL[q];
      defs += '<linearGradient id="' + id + 'b' + q + '" x1="0" x2="1">' +
        '<stop offset="0" stop-color="#050404"/><stop offset=".14" stop-color="#1c1813"/><stop offset=".34" stop-color="#5a4a34"/>' +
        '<stop offset=".42" stop-color="#2a231a"/><stop offset=".75" stop-color="#14110d"/><stop offset="1" stop-color="#030303"/></linearGradient>' +
        '<radialGradient id="' + id + 'g' + q + '" cx="50%" cy="85%" r="65%"><stop offset="0" stop-color="#ffd9a0" stop-opacity=".95"/><stop offset=".5" stop-color="#e8a24e" stop-opacity=".5"/><stop offset="1" stop-color="' + c + '" stop-opacity="0"/></radialGradient>';
    });
    defs += '</defs>';

    function ring(x, y, rx, ry, hh, q) {
      var L = x - rx, R = x + rx, b = y + hh;
      var front = 'M' + L + ' ' + y + 'A' + rx + ' ' + ry + ' 0 0 0 ' + R + ' ' + y + 'L' + R + ' ' + b + 'A' + rx + ' ' + ry + ' 0 0 1 ' + L + ' ' + b + 'Z';
      return '<path class="band" d="' + front + '" fill="url(#' + id + 'b' + q + ')"/>' +
        '<path class="rim" d="M' + L + ' ' + (y + 1.2) + 'A' + rx + ' ' + ry + ' 0 0 0 ' + R + ' ' + (y + 1.2) + '" fill="none" stroke="#f2c57c" stroke-width="2.2"/>' +
        '<path class="rim" d="M' + L + ' ' + (b - 1.2) + 'A' + rx + ' ' + ry + ' 0 0 0 ' + R + ' ' + (b - 1.2) + '" fill="none" stroke="#c9923f" stroke-width="2"/>';
    }

    var out = '';
    var close = '';
    ORDER.forEach(function (q, k) {
      var rx = rx0 - k * step, ry = rx * 0.16;
      var floorY = floorBase - k * (bandH + wallH);       /* base do anel */
      var top = floorY - bandH;                            /* topo do anel (piso do cômodo) */
      var isA = q === anchor;
      var l = Math.max(0, Math.min(1, lit[q] == null ? 0.5 : lit[q]));
      var lean = isA && o.lean !== false ? (k % 2 ? 4 : -4) : 0;
      out += '<g class="tier' + (isA ? ' is-anchor' : '') + '" data-q="' + q + '" style="--c:' + COL[q] + ';--l:' + l.toFixed(2) + ';--lean:' + lean + 'deg;transform-origin:' + cx + 'px ' + (floorY + ry) + 'px">';
      /* sombra no chão (só na base) */
      if (k === 0) out += '<ellipse cx="' + cx + '" cy="' + (floorY + ry + 6) + '" rx="' + (rx * 1.1) + '" ry="' + (ry * 0.9) + '" fill="#000" opacity=".45" filter="url(#' + id + 'blur)"/>';
      out += ring(cx, top, rx, ry, bandH, q);
      /* piso do cômodo (elipse de cima do anel) */
      out += '<ellipse cx="' + cx + '" cy="' + top + '" rx="' + rx + '" ry="' + ry + '" fill="#120f0b"/>' +
        '<ellipse cx="' + cx + '" cy="' + top + '" rx="' + rx * 0.97 + '" ry="' + ry * 0.92 + '" fill="' + COL[q] + '" opacity=".1"/>';
      /* rachadura no anel do ancla */
      if (isA) {
        var x0 = cx - rx * 0.22;
        out += '<path class="crk" d="M' + x0 + ' ' + (top + ry * 0.95) + 'l7 8-5 6 9 7-4 6 6 ' + (bandH - 25 + ry * 0.2) + '" fill="none" stroke-width="2" stroke-linejoin="round"/>';
      }
      /* ícone e nome no anel */
      var ly = top + ry + bandH / 2 + 5;
      var label = BAND[q], fs = compact ? 13.5 : 14;
      var tw = label.length * fs * 0.78;
      var ix = cx - (tw + 26) / 2;
      out += '<g class="lbl" transform="translate(' + ix + ' ' + (ly - 15) + ') scale(.8)"><path d="' + ICON[q] + '" fill="none" stroke="#f2d08e" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></g>' +
        '<text x="' + (ix + 26) + '" y="' + ly + '" class="lbl" font-size="' + fs + '" letter-spacing="1.5" fill="#f2d08e">' + label + '</text>';

      if (k < 4) {
        /* cômodo de vidro iluminado até o anel de cima */
        var rw = (rx - step) * 0.93, ryw = rw * 0.16, wt = top - wallH;
        out += '<g class="room">' +
          '<ellipse class="glow" cx="' + cx + '" cy="' + (top - wallH * 0.35) + '" rx="' + rw * 0.95 + '" ry="' + wallH * 0.7 + '" fill="url(#' + id + 'g' + q + ')"/>' +
          '<path d="M' + (cx - rw) + ' ' + wt + 'V' + top + 'A' + rw + ' ' + ryw + ' 0 0 0 ' + (cx + rw) + ' ' + top + 'V' + wt + 'Z" fill="url(#' + id + 'glass)" stroke="#fff" stroke-opacity=".14"/>';
        for (var m = 1; m < 6; m++) {
          var mx = cx - rw + (2 * rw) * m / 6, my = top + ryw * Math.sqrt(Math.max(0, 1 - Math.pow((mx - cx) / rw, 2)));
          out += '<path d="M' + mx.toFixed(1) + ' ' + wt + 'V' + my.toFixed(1) + '" stroke="#fff" stroke-opacity=".1"/>';
        }
        /* plantas nas bordas */
        out += '<circle cx="' + (cx - rw + 8) + '" cy="' + (top - 4) + '" r="9" fill="#3f7a3a" opacity=".85"/><circle cx="' + (cx - rw + 18) + '" cy="' + (top - 2) + '" r="6" fill="#5e9e4a" opacity=".85"/>' +
          '<circle cx="' + (cx + rw - 10) + '" cy="' + (top - 3) + '" r="8" fill="#3f7a3a" opacity=".85"/>' +
          '<g class="ico" transform="translate(' + (cx - 19) + ' ' + (top - wallH * 0.5 - 17) + ') scale(1.6)"><path d="' + ICON[q] + '" fill="none" stroke="' + COL[q] + '" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></g>' +
          '</g>';
      } else {
        /* jardim no topo */
        var ty = top - 2, g = '';
        for (var pl = 0; pl < 15; pl++) {
          var a = (pl / 14) * Math.PI, px = cx - Math.cos(a) * rx * 0.86, py = ty - Math.sin(a) * ry * 0.5;
          var r = 9 + ((pl * 7) % 5) * 2.2;
          g += '<circle cx="' + px.toFixed(1) + '" cy="' + (py - r * 0.6).toFixed(1) + '" r="' + r + '" fill="#244a25"/>' +
            '<circle cx="' + (px - 2).toFixed(1) + '" cy="' + (py - r * 0.8).toFixed(1) + '" r="' + (r * 0.78).toFixed(1) + '" fill="url(#' + id + 'leaf)"/>';
        }
        out += '<g class="tree">' + g + '</g>';
      }

      /* chamadas laterais */
      if (callouts !== 'none') {
        var right = k % 2 === 0, ex = right ? cx + rx + 4 : cx - rx - 4, ey = top + ry + bandH / 2;
        var tx = right ? W - 6 : 6, anchorTxt = right ? 'end' : 'start';
        var lx = right ? tx - 96 : tx + 96;
        var sub = callouts === 'score' && scores ? (scores[q] + ' de 3') : DESC[q];
        out += '<g class="co">' +
          '<path d="M' + ex + ' ' + ey + 'H' + lx + '" stroke="' + COL[q] + '" stroke-opacity=".7"/><circle cx="' + ex + '" cy="' + ey + '" r="2.5" fill="' + COL[q] + '"/>' +
          '<text x="' + tx + '" y="' + (ey - 8) + '" text-anchor="' + anchorTxt + '" class="co-n">' + NAME[q] + (isA ? ' · Ancla' : '') + '</text>' +
          '<text x="' + tx + '" y="' + (ey + 12) + '" text-anchor="' + anchorTxt + '" class="co-s">' + sub + '</text></g>';
      }
      close += '</g>';
    });
    out += close;

    var skyEl = '<ellipse cx="' + cx + '" cy="' + (H * 0.4) + '" rx="' + W * 0.5 + '" ry="' + H * 0.45 + '" fill="url(#' + id + 'sky)"/>';
    return '<svg class="tower' + (compact ? ' compact' : '') + '" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="' + (o.label || 'Torre de los 5 pilares') + '">' + defs + skyEl + out + '</svg>';
  }
  Tower.ORDER = ORDER; Tower.NAME = NAME;
  window.Tower = Tower;
})();
