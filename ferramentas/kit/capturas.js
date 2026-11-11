// Telas de celular de um nicho para a proposta do kit (1170 × 2532, como as demais).
// Uso: node ferramentas/kit/capturas.js <nicho> <pasta-site> <pasta-saida> "<item com opções>" "<opção 1>" "<opção 2>"
// Gera: cel-site.png, cel-menu.png, cel-item.png e cel-sacola.png.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path'), os = require('os');
const RAIZ = path.resolve(__dirname, '..', '..');
const [NICHO, SITE, SAIDA, ITEM, ...OPS] = process.argv.slice(2);
(async () => {
  fs.mkdirSync(SAIDA, { recursive: true });
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'kit-'));
  for (const n of fs.readdirSync(path.join(RAIZ, 'plataforma'))) fs.symlinkSync(path.join(RAIZ, 'plataforma', n), path.join(tmp, n));
  fs.symlinkSync(path.resolve(RAIZ, SITE), path.join(tmp, '_site'));
  const srv = spawn('python3', ['-m', 'http.server', '8793', '-d', tmp], { stdio: 'ignore' });
  await new Promise(r => setTimeout(r, 900));
  const S = JSON.parse(fs.readFileSync(path.join(RAIZ, 'plataforma/supabase/sementes', NICHO + '.json'), 'utf8'));
  const loja = Object.assign({ id: 'loja-1', status: 'ativa', accept_orders: true, faz_entrega: true, faz_retirada: true }, S.loja);
  const cats = [], prods = [];
  S.categorias.forEach((c, i) => { const cid = 'c' + (i + 1); cats.push({ id: cid, name: c.nome, position: i + 1 });
    c.itens.forEach((p, k) => prods.push({ id: cid + 'p' + (k + 1), category_id: cid, name: p.nome, description: p.desc || '', price: p.preco, unit: p.unid || '',
      image_url: p.foto || '', featured: !!p.destaque, badge: p.selo || '', position: k + 1, opcoes: p.opcoes || [], extra: {} })); });
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
  await ctx.route('**/assets/config.js*', r => r.fulfill({ contentType: 'application/javascript', body: 'window.BC={supabaseUrl:"https://teste.supabase.co",supabaseKey:"anon-teste-000000000000000",site:""};' }));
  await ctx.route('https://teste.supabase.co/**', r => { const u = r.request().url(), j = d => r.fulfill({ contentType: 'application/json', body: JSON.stringify(d) });
    if (u.includes('/lojas?')) return j([loja]); if (u.includes('/categories?')) return j(cats); if (u.includes('/products?')) return j(prods); return j([]); });
  const p = await ctx.newPage();
  await p.goto('http://localhost:8793/_site/index.html', { waitUntil: 'networkidle' }); await p.waitForTimeout(2200);
  await p.screenshot({ path: path.join(SAIDA, 'cel-site.png') });
  await p.goto('http://localhost:8793/loja.html?l=' + loja.slug, { waitUntil: 'networkidle' }); await p.waitForTimeout(1500);
  await p.evaluate(() => { const t = document.querySelector('.m-dest-tit'); if (t) scrollTo(0, t.getBoundingClientRect().top + scrollY - 260); }); await p.waitForTimeout(900);
  await p.screenshot({ path: path.join(SAIDA, 'cel-menu.png') });
  const alvo = await p.evaluateHandle(n => { const c = [...document.querySelectorAll('.m-dest-it,.m-row,.m-card,.m-plate')].find(e => e.textContent.includes(n)); return c && c.querySelector('.ctrl button'); }, ITEM);
  await alvo.asElement().click(); await p.waitForTimeout(800);
  for (const o of OPS) {
    await p.evaluate(t => { const b = [...document.querySelectorAll('.opc-item')].find(e => e.textContent.toLowerCase().includes(t.toLowerCase())); if (b) { b.scrollIntoView({ block: 'center' }); b.click(); } }, o);
    await p.waitForTimeout(350);
  }
  await p.evaluate(() => { const c = document.getElementById('opcCorpo'); if (c) c.scrollTop = 0; }); await p.waitForTimeout(400);
  await p.screenshot({ path: path.join(SAIDA, 'cel-item.png') });
  await p.click('#opcAdd'); await p.waitForTimeout(700); await p.click('#barra'); await p.waitForTimeout(900);
  await p.screenshot({ path: path.join(SAIDA, 'cel-sacola.png') });
  await b.close(); srv.kill(); fs.rmSync(tmp, { recursive: true, force: true });
  console.log(fs.readdirSync(SAIDA).join(' '));
})();
