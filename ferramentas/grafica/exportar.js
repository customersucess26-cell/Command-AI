// Exporta as peças de gráfica geradas por gerar.py: PDF para a gráfica (com sangria, sem guias),
// PNG de cada face (área final, sem sangria) e uma foto-montagem "como fica impresso".
// Uso: node ferramentas/grafica/exportar.js <pasta>
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = path.resolve(process.argv[2]);
  const b = await chromium.launch();
  const faces = {};
  for (const [arq, nome] of [['cartao-de-volta.html', 'cartao'], ['display-balcao.html', 'display']]) {
    const p = await b.newPage({ viewport: { width: 1000, height: 1400 }, deviceScaleFactor: 4 });
    await p.goto('file://' + path.join(dir, arq)); await p.evaluate(() => document.fonts.ready);
    await p.evaluate(() => document.body.classList.add('final'));
    await p.pdf({ path: path.join(dir, nome + '-para-grafica.pdf'), preferCSSPageSize: true, printBackground: true });
    await p.evaluate(() => { document.body.style.background = '#777'; document.querySelectorAll('.pg').forEach(s => { s.style.margin = '0'; }); });
    const secs = await p.$$('section.pg'); faces[nome] = [];
    for (let i = 0; i < secs.length; i++) {
      const bb = await secs[i].boundingBox(), sang = bb.width * 3 / (nome === 'cartao' ? 96 : 154);
      const f = path.join(dir, `${nome}-${i === 0 ? (nome === 'cartao' ? 'frente' : 'frente') : 'verso'}.png`);
      await p.screenshot({ path: f, fullPage: true, clip: { x: bb.x + sang, y: bb.y + sang, width: bb.width - 2 * sang, height: bb.height - 2 * sang } });
      faces[nome].push(f);
    }
    await p.close();
  }
  // foto-montagem
  const u = f => 'data:image/png;base64,' + fs.readFileSync(f).toString('base64');
  const m = await b.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1.5 });
  await m.setContent(`<html><body style="margin:0;width:1600px;height:1000px;overflow:hidden;background:radial-gradient(80% 70% at 40% 40%,#3b2b1f,#120d0a 75%);font-family:Arial">
  <div style="position:absolute;inset:0;background:repeating-linear-gradient(90deg,rgba(255,255,255,.015) 0 2px,transparent 2px 9px)"></div>
  <img src="${u(faces.display[0])}" style="position:absolute;left:960px;top:96px;width:520px;border-radius:4px;box-shadow:30px 40px 60px rgba(0,0,0,.6);outline:10px solid rgba(255,255,255,.12)">
  <div style="position:absolute;left:910px;top:872px;width:580px;height:40px;background:linear-gradient(180deg,rgba(255,255,255,.35),rgba(255,255,255,.08));border-radius:6px;box-shadow:0 18px 30px rgba(0,0,0,.6)"></div>
  <img src="${u(faces.cartao[1])}" style="position:absolute;left:140px;top:520px;width:600px;border-radius:14px;transform:rotate(-8deg);box-shadow:24px 30px 50px rgba(0,0,0,.55)">
  <img src="${u(faces.cartao[0])}" style="position:absolute;left:190px;top:170px;width:600px;border-radius:14px;transform:rotate(5deg);box-shadow:24px 30px 50px rgba(0,0,0,.6)">
  </body></html>`);
  await m.waitForTimeout(300);
  await m.screenshot({ path: path.join(dir, 'previa-impressos.png') });
  await b.close();
  console.log(fs.readdirSync(dir).join('\n'));
})();
