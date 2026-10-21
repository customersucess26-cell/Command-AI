/* Abre manual/manual-venda-e-entrega.html no Chrome e grava manual/Manual-de-Venda-e-Entrega-Bistro-Connect.pdf (A4, com fundo).
   Uso:  node ferramentas/pdf-manual-entrega.js */
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage();
  await pg.goto('file://' + path.resolve('manual/manual-venda-e-entrega.html'), { waitUntil: 'networkidle' });
  await pg.waitForTimeout(1500);
  await pg.pdf({ path: 'manual/Manual-de-Venda-e-Entrega-Bistro-Connect.pdf', format: 'A4', printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
