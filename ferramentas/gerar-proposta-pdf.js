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
  // versão para celular: layout fluido de tela, numa página contínua de 430 px
  const cel = sai.replace(/\.pdf$/, '-celular.pdf');
  const m = await b.newPage({ viewport: { width: 430, height: 900 }, deviceScaleFactor: 2 });
  await m.goto('file://' + ent, { waitUntil: 'networkidle' });
  await m.evaluate(() => document.fonts.ready);
  await m.emulateMedia({ media: 'screen' });
  await m.addStyleTag({ content: '@page{size:auto;margin:0}.web-cta,.web-pdf{display:none!important}body{padding-bottom:0!important}.pg:first-child{min-height:0!important}.pg{page-break-after:auto!important;break-after:auto!important;break-inside:auto!important}' });
  const h = await m.evaluate(() => document.documentElement.scrollHeight);
  await m.pdf({ path: cel, width: '430px', height: (h + 2) + 'px', printBackground: true, pageRanges: '1' });
  console.log('celular →', cel, h + 'px');
  await b.close();
  console.log(n + ' páginas →', sai);
})();
