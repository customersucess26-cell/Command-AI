// Grava o vídeo de vendas de 30 s (1080 × 1920) a partir de ferramentas/video/palco.html.
// Uso: node ferramentas/video/gravar.js [saida.mp4]
// Monta uma pasta temporária com a plataforma (raiz), o site do Âmbar (/restaurante/) e o palco (/_video/),
// simula o Supabase com a semente da hamburgueria, captura a tela quadro a quadro e codifica com o ffmpeg.
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs'), path = require('path'), os = require('os');
const RAIZ = path.resolve(__dirname, '..', '..');
const SAIDA = path.resolve(process.argv[2] || path.join(RAIZ, 'manual/materiais-vendas/video-vendas-30s.mp4'));
const PORTA = 8790;

(async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'palco-'));
  for (const n of fs.readdirSync(path.join(RAIZ, 'plataforma'))) fs.symlinkSync(path.join(RAIZ, 'plataforma', n), path.join(tmp, n));
  fs.symlinkSync(path.join(RAIZ, 'sites/ambar'), path.join(tmp, 'restaurante'));
  fs.symlinkSync(__dirname, path.join(tmp, '_video'));
  const srv = spawn('python3', ['-m', 'http.server', String(PORTA), '-d', tmp], { stdio: 'ignore' });
  await new Promise(r => setTimeout(r, 900));

  const S = JSON.parse(fs.readFileSync(path.join(RAIZ, 'plataforma/supabase/sementes/hamburgueria.json'), 'utf8'));
  const loja = Object.assign({ id: 'loja-1', status: 'ativa', accept_orders: true, faz_entrega: true, faz_retirada: true }, S.loja);
  const cats = [], prods = [];
  S.categorias.forEach((c, i) => { const cid = 'c' + (i + 1); cats.push({ id: cid, name: c.nome, position: i + 1 });
    c.itens.forEach((p, k) => prods.push({ id: cid + 'p' + (k + 1), category_id: cid, name: p.nome, description: p.desc || '', price: p.preco, unit: p.unid || '',
      image_url: p.foto || '', featured: !!p.destaque, badge: p.selo || '', position: k + 1, opcoes: p.opcoes || [], extra: {} })); });

  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await ctx.route('**/assets/config.js*', r => r.fulfill({ contentType: 'application/javascript',
    body: 'window.BC={nome:"Bistrô Connect",supabaseUrl:"https://teste.supabase.co",supabaseKey:"anon-teste-0000000000000000",suporteWhatsapp:"5542999006578",site:""};' }));
  await ctx.route('https://wa.me/**', r => r.fulfill({ contentType: 'text/html', body: '<html></html>' }));
  await ctx.route('https://teste.supabase.co/**', r => {
    const u = r.request().url(), j = d => r.fulfill({ contentType: 'application/json', body: JSON.stringify(d) });
    if (u.includes('/lojas?')) return j([loja]);
    if (u.includes('/categories?')) return j(cats);
    if (u.includes('/products?')) return j(prods);
    if (u.includes('rpc/create_order')) return j({ code: '#24', subtotal: 64, delivery_fee: 0, discount: 0, total: 64, delivery_type: 'retirada',
      track_code: 'a1b2c3d4e5f60718', track_token: 'a1b2c3d4e5f60718a1b2c3d4e5f60718',
      items: [{ qty: 1, name: 'Barbecue Onion', unit: '', price: 64, options: [{ name: 'Ao ponto para mais', group: 'Ponto da carne', price: 0 }, { name: 'Bacon crocante', group: 'Turbine o seu burger', price: 6 }, { name: 'Batata frita + refrigerante lata', group: 'Vire combo', price: 19 }] }] });
    return j([]);
  });
  ctx.on('page', p => { if (p.url().includes('wa.me')) p.close().catch(() => {}); });
  const p = await ctx.newPage();
  p.on('console', m => { if (/sem alvo|Error/.test(m.text())) console.log('palco:', m.text()); });
  await p.goto(`http://localhost:${PORTA}/_video/palco.html`, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.evaluate(() => window.__prepara()); await p.waitForTimeout(800);

  const quadros = fs.mkdtempSync(path.join(os.tmpdir(), 'quadros-')); let n = 0; const tempos = [];
  const cdp = await ctx.newCDPSession(p);
  cdp.on('Page.screencastFrame', async f => {
    const nome = path.join(quadros, String(n).padStart(5, '0') + '.jpg');
    fs.writeFileSync(nome, Buffer.from(f.data, 'base64')); tempos.push([nome, f.metadata.timestamp]); n++;
    cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }).catch(() => {});
  });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: 1080, maxHeight: 1920, everyNthFrame: 1 });
  await p.evaluate(() => window.__comeca());
  await p.waitForFunction(() => window.__fim === true, null, { timeout: 90000, polling: 200 });
  const fimTs = Date.now() / 1000;
  await cdp.send('Page.stopScreencast');
  await b.close(); srv.kill();

  // lista do ffmpeg com a duração real de cada quadro
  let lista = '';
  for (let i = 0; i < tempos.length; i++) {
    const d = i + 1 < tempos.length ? Math.max(0.001, tempos[i + 1][1] - tempos[i][1]) : Math.max(0.5, fimTs - tempos[i][1]);
    lista += `file '${tempos[i][0]}'\nduration ${d.toFixed(4)}\n`;
  }
  lista += `file '${tempos[tempos.length - 1][0]}'\n`;
  fs.writeFileSync(path.join(quadros, 'lista.txt'), lista);
  const total = fimTs - tempos[0][1];
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(quadros, 'lista.txt'),
    '-vf', `setpts=PTS*${(30 / Math.max(30, total)).toFixed(4)},fps=30,scale=1080:1920:flags=lanczos,format=yuv420p`, '-t', '30', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-movflags', '+faststart', SAIDA]);
  console.log(`${n} quadros, ${total.toFixed(1)} s → ${SAIDA}`);
  fs.rmSync(tmp, { recursive: true, force: true });
})();
