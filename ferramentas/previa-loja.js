// Prévia da vitrine (plataforma/loja.html) sem banco: simula o Supabase com um cardápio de semente.
// Uso: node ferramentas/previa-loja.js <semente.json> <saida-sem-extensao> [largura=390] [porta=8771]
// A semente tem { loja: {...colunas de lojas}, categorias: [{nome, itens:[{nome, desc, preco, unid, foto, destaque, selo, opcoes}]}] }.
// Gera <saida>-topo.png (primeira tela), <saida>-pagina.png (página inteira) e <saida>-item.png (folha de um produto com opções).
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
(async () => {
  const [semente, saida, larg = '390', porta = '8771'] = process.argv.slice(2);
  const S = JSON.parse(fs.readFileSync(semente, 'utf8'));
  const raiz = path.resolve(__dirname, '..', 'plataforma');
  const srv = spawn('python3', ['-m', 'http.server', porta, '-d', raiz], { stdio: 'ignore' });
  await new Promise(r => setTimeout(r, 900));
  const loja = Object.assign({ id: 'loja-1', status: 'ativa', accept_orders: true, faz_entrega: true, faz_retirada: true, pagamentos: ['Pix', 'Cartão', 'Dinheiro'], extra: {} }, S.loja);
  const cats = [], prods = [];
  S.categorias.forEach((c, i) => {
    const cid = 'c' + (i + 1); cats.push({ id: cid, name: c.nome, position: i + 1 });
    c.itens.forEach((p, k) => prods.push({ id: cid + 'p' + (k + 1), category_id: cid, name: p.nome, description: p.desc || '', price: p.preco, unit: p.unid || '',
      image_url: p.foto || '', featured: !!p.destaque, badge: p.selo || '', position: k + 1, opcoes: p.opcoes || [], extra: {} }));
  });
  const b = await chromium.launch();
  const c = await b.newContext({ viewport: { width: +larg, height: 844 }, deviceScaleFactor: 2, isMobile: +larg < 700, hasTouch: +larg < 700 });
  await c.route('**/assets/config.js*', r => r.fulfill({ contentType: 'application/javascript', body: 'window.BC={nome:"Bistrô Connect",supabaseUrl:"https://teste.supabase.co",supabaseKey:"anon-teste",suporteWhatsapp:"",site:""};' }));
  await c.route('https://teste.supabase.co/**', r => {
    const u = r.request().url();
    const j = d => r.fulfill({ contentType: 'application/json', body: JSON.stringify(d) });
    if (u.includes('/lojas?')) return j([loja]);
    if (u.includes('/categories?')) return j(cats);
    if (u.includes('/products?')) return j(prods);
    return j([]);
  });
  const p = await c.newPage();
  const erros = []; p.on('pageerror', e => erros.push(e.message));
  await p.goto(`http://localhost:${porta}/loja.html?l=${loja.slug}`, { waitUntil: 'networkidle' });
  await p.waitForTimeout(1500);
  await p.screenshot({ path: saida + '-topo.png' });
  const H = await p.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < H; y += 400) { await p.evaluate(v => scrollTo(0, v), y); await p.waitForTimeout(90); }
  await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(400);
  await p.screenshot({ path: saida + '-pagina.png', fullPage: true });
  const comOp = prods.findIndex(x => x.opcoes.length);
  if (comOp >= 0) {
    const alvo = await p.$(`[data-id="${prods[comOp].id}"]`) || (await p.$$('.m-card,.m-row,.m-plate,.item'))[0];
    if (alvo) { await alvo.click().catch(() => {}); await p.waitForTimeout(800); await p.screenshot({ path: saida + '-item.png' }); }
  }
  const info = await p.evaluate(() => ({ sw: document.documentElement.scrollWidth, h: document.documentElement.scrollHeight, imgsQuebradas: [...document.images].filter(i => i.complete && !i.naturalWidth).map(i => i.src).slice(0, 8) }));
  console.log(JSON.stringify({ ...info, erros }));
  await b.close(); srv.kill();
})();
