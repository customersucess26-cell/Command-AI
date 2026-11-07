// Gera o PDF da proposta a partir do HTML (Chromium/Playwright).
// Uso: node ferramentas/gerar-proposta-pdf.js [entrada.html] [saida.pdf]
const { chromium } = require('playwright');
const path = require('path');
const ent = path.resolve(process.argv[2] || 'propostas/digital-experience/proposta.html');
const sai = path.resolve(process.argv[3] || 'manual/materiais-vendas/proposta-digital-experience-v14.pdf');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + ent, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const n = await p.$$eval('section.pg', s => s.length);
  await p.pdf({ path: sai, preferCSSPageSize: true, printBackground: true });
  await b.close();
  console.log(n + ' páginas →', sai);
})();
