#!/usr/bin/env python3
"""Monta o painel da plataforma Bistrô Connect (plataforma/painel/) a partir do painel das lojas (paineis/loja/).

O painel é o mesmo dos sites de nicho, com as mudanças para várias lojas:
  * configuração em window.BC (plataforma/assets/config.js);
  * depois do login em 2 etapas, escolhe a loja (minhas_lojas) e filtra tudo por loja_id;
  * dados da loja vêm da tabela lojas (com descrição, cor, logo, capa, entrega/retirada e pagamentos);
  * aba Equipe (convites com link, funções) e caixas "Seu link" e "Plano do mês" no Início;
  * o que cada função vê: cozinha só pedidos; atendente pedidos e clientes; dono e gerente tudo.

Rode da raiz do repositório depois de mudar paineis/loja:  python3 ferramentas/montar-painel-plataforma.py
"""
import os
import re
import shutil
import subprocess

ORIG, DEST = "paineis/loja", "plataforma/painel"
os.makedirs(DEST, exist_ok=True)
shutil.copy(f"{ORIG}/painel.css", f"{DEST}/painel.css")
html = open(f"{ORIG}/index.html", encoding="utf-8").read()
js = open(f"{ORIG}/painel.js", encoding="utf-8").read()


def troca(txt, velho, novo, vezes=1):
    n = txt.count(velho)
    assert n == vezes, (n, velho[:90])
    return txt.replace(velho, novo)


# ------------------------------------------------------------------ HTML
h = html
h = troca(h, '<title>Painel da loja</title>', '<title>Painel · Bistrô Connect</title>')
h = troca(h, '<script src="vendor/supabase-2.45.4.js"></script>', '<script src="../assets/vendor/supabase-2.45.4.js"></script>')
h = troca(h, '<small>Painel da loja</small>', '<small>Bistrô Connect</small>')
h = troca(h, '''      <button class="btn primary big" type="submit">Entrar</button>
    </form>''', '''      <button class="btn primary big" type="submit">Entrar</button>
      <p class="muted fino centro">Ainda não tem loja? <a href="../entrar.html">Crie grátis</a></p>
    </form>''')
h = troca(h, '''    <div id="semConfig" hidden>''', '''    <div id="semLoja" hidden>
      <h1>Você ainda não tem loja</h1>
      <p class="muted">Sua conta entrou, mas não faz parte da equipe de nenhuma loja. Crie a sua ou peça um convite para o dono da loja.</p>
      <a class="btn primary big" href="../entrar.html">Criar minha loja</a>
      <a class="btn link" href="../admin/">Sou administrador da plataforma</a>
      <button class="btn link" type="button" data-sair>Sair</button>
    </div>
    <div id="escolheLoja" hidden>
      <h1>Escolha a loja</h1>
      <div class="list" id="listaLojas"></div>
      <button class="btn link" type="button" data-sair>Sair</button>
    </div>
    <div id="semConfig" hidden>''')
h = troca(h, 'Preencha <code>supabaseUrl</code> e <code>supabaseKey</code> em <code>assets/config.js</code> do site e rode os arquivos SQL da loja.',
          'Preencha <code>supabaseUrl</code> e <code>supabaseKey</code> em <code>assets/config.js</code> da plataforma e rode o <code>01-plataforma.sql</code>.')
h = troca(h, '''      <button type="button" data-aba="pedidos" data-recurso="pedidos">''',
          '''      <button type="button" data-aba="pedidos" data-recurso="pedidos" data-papel="dono gerente atendente cozinha">''')
h = troca(h, '''      <button type="button" data-aba="financeiro" data-recurso="pedidos">''',
          '''      <button type="button" data-aba="financeiro" data-recurso="pedidos" data-papel="dono gerente">''')
h = troca(h, '''      <button type="button" data-aba="clientes" data-recurso="pedidos">''',
          '''      <button type="button" data-aba="clientes" data-recurso="pedidos" data-papel="dono gerente atendente">''')
h = troca(h, '''      <span class="side-grupo">Cardápio</span>
      <button type="button" data-aba="cardapio">''', '''      <span class="side-grupo" data-papel="dono gerente">Cardápio</span>
      <button type="button" data-aba="cardapio" data-papel="dono gerente">''')
h = troca(h, '''      <span class="side-grupo">Loja</span>
      <button type="button" data-aba="loja">''', '''      <span class="side-grupo">Loja</span>
      <button type="button" data-aba="loja" data-papel="dono gerente">''')
h = troca(h, '''<span>Dados da loja</span></button>''', '''<span>Dados da loja</span></button>
      <button type="button" data-aba="equipe" data-papel="dono gerente"><svg viewBox="0 0 24 24"><circle cx="8" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M2 20c0-3.3 2.7-6 6-6s6 2.7 6 6M14 15.5c.9-.6 2-1 3-1 2.8 0 5 2.2 5 5"/></svg><span>Equipe</span></button>''')
h = troca(h, '''        <a class="btn ghost-escuro small" href="../" target="_blank" rel="noopener">Ver site ↗</a>''',
          '''        <a class="btn ghost-escuro small" id="verSite" href="../" target="_blank" rel="noopener">Ver loja ↗</a>
        <button class="btn ghost-escuro small" type="button" id="btnTrocaLoja" hidden>Trocar loja</button>
        <a class="btn ghost-escuro small" id="btnPlataforma" href="../admin/" hidden>Plataforma</a>''')
h = troca(h, '''        <button class="btn primary" type="button" id="btnNovoProduto">+ Produto</button>''',
          '''        <button class="btn primary" type="button" id="btnNovoProduto" data-papel="dono gerente">+ Produto</button>''')
h = troca(h, '''    <section class="panel" data-panel="inicio">
      <div class="kpis" id="kpisInicio"></div>''', '''    <section class="panel" data-panel="inicio">
      <div class="grid2">
        <div class="box"><div class="box-head"><h2>Link da sua loja</h2><span class="muted fino">mande para os clientes</span></div>
          <p class="link-loja"><a id="linkLoja" href="#" target="_blank" rel="noopener"></a></p>
          <div class="acoes-linha"><button class="btn small" type="button" id="btnCopiaLink">Copiar link</button><a class="btn zap small" id="btnZapLink" href="#" target="_blank" rel="noopener noreferrer">Divulgar no WhatsApp</a></div></div>
        <div class="box" data-papel="dono gerente"><div class="box-head"><h2>Plano do mês</h2><span class="muted fino" id="planoFaixa"></span></div>
          <div class="kpis" id="kpisPlano"></div>
          <p class="muted fino">Você paga pelo que vende na plataforma, com teto. Sem comissão por pedido.</p></div>
      </div>
      <div class="kpis" id="kpisInicio"></div>''')
# loja: campos novos
h = troca(h, '''          <label class="full">Nome da loja<input id="sNome" maxlength="80" required></label>''',
          '''          <label class="full">Nome da loja<input id="sNome" maxlength="80" required></label>
          <label class="full">Frase da loja<input id="sDesc" maxlength="300" placeholder="Pães e doces feitos todo dia, com carinho."></label>''')
h = troca(h, '''          <label class="full inline" data-recurso="pedidos"><input type="checkbox" id="sAceita"> Receber pedidos pelo site agora</label>''',
          '''          <label class="full inline" data-recurso="pedidos"><input type="checkbox" id="sAceita"> Receber pedidos pelo site agora</label>
          <label class="inline"><input type="checkbox" id="sEntrega"> Faz entrega</label>
          <label class="inline"><input type="checkbox" id="sRetirada"> Cliente pode retirar</label>
          <fieldset class="full pagamentos"><legend>Formas de pagamento aceitas</legend>
            <label class="inline"><input type="checkbox" data-pag="Pix"> Pix</label>
            <label class="inline"><input type="checkbox" data-pag="Cartão"> Cartão</label>
            <label class="inline"><input type="checkbox" data-pag="Dinheiro"> Dinheiro</label></fieldset>
          <label>Cor da marca<input id="sCor" type="color" value="#B0703F"></label>
          <div class="full fotos-loja">
            <div class="foto-campo"><div class="foto-prev" id="sLogoPrev"><span>Logo</span></div><div class="foto-acoes"><label class="btn small">Enviar logo<input type="file" id="sLogo" accept="image/jpeg,image/png,image/webp" hidden></label><button type="button" class="btn small" data-tira="logo_url">Tirar</button></div></div>
            <div class="foto-campo"><div class="foto-prev larga" id="sCapaPrev"><span>Capa</span></div><div class="foto-acoes"><label class="btn small">Enviar capa<input type="file" id="sCapa" accept="image/jpeg,image/png,image/webp" hidden></label><button type="button" class="btn small" data-tira="capa_url">Tirar</button><p class="muted fino">Foto larga do ambiente ou dos produtos (fica no topo da loja).</p></div></div>
          </div>''')
# aba equipe
h = troca(h, '''    <!-- AJUSTES -->''', '''    <!-- EQUIPE -->
    <section class="panel" data-panel="equipe" hidden>
      <div class="grid2">
        <form class="box" id="conviteForm" novalidate>
          <div class="box-head"><h2>Convidar pessoa</h2></div>
          <label>E-mail da pessoa<input id="cvEmail" type="email" maxlength="190" autocomplete="off" required></label>
          <label>Função<select id="cvPapel">
            <option value="atendente">Atendente: pedidos e clientes</option>
            <option value="cozinha">Cozinha: só os pedidos</option>
            <option value="gerente">Gerente: tudo, menos a equipe e a conta</option></select></label>
          <div class="acoes-linha"><button class="btn primary" type="submit">Gerar convite</button></div>
          <div id="cvLinkBox" hidden><p class="muted fino">Mande este link para a pessoa. Ela cria a conta com o mesmo e-mail e já entra na equipe. Vale 7 dias.</p>
            <p class="link-loja"><code id="cvLink"></code></p>
            <div class="acoes-linha"><button class="btn small" type="button" id="btnCopiaConvite">Copiar</button><a class="btn zap small" id="btnZapConvite" href="#" target="_blank" rel="noopener noreferrer">Mandar no WhatsApp</a></div></div>
        </form>
        <div class="box">
          <div class="box-head"><h2>O que cada função pode fazer</h2></div>
          <ul class="muted fino lista-funcoes">
            <li><b>Dono:</b> tudo, inclusive equipe e dados da loja.</li>
            <li><b>Gerente:</b> pedidos, financeiro, cardápio e dados da loja. Convida atendentes e cozinha.</li>
            <li><b>Atendente:</b> pedidos, pagamentos e clientes. Pode pausar os pedidos.</li>
            <li><b>Cozinha:</b> só vê e avança os pedidos.</li>
          </ul>
          <p class="muted fino">Todos entram com senha e login em 2 etapas. Cada pessoa tem o próprio acesso: nunca compartilhe senha.</p>
        </div>
      </div>
      <div class="box"><div class="box-head"><h2>Equipe</h2></div><div class="list" id="listaEquipe"></div></div>
      <div class="box"><div class="box-head"><h2>Convites pendentes</h2></div><div class="list" id="listaConvites"></div></div>
    </section>
    <!-- AJUSTES -->''')
assert "data-tira" in h
open(f"{DEST}/index.html", "w", encoding="utf-8").write(h)

# ------------------------------------------------------------------ JS
j = js
j = troca(j, """/* Painel da loja (sites de nicho). Lê a configuração de ../assets/config.js (window.LOJA).
   Tabelas: settings, categories, products, orders (supabase/05-loja-tabelas.sql + 03-loja-pedidos.sql).""",
          """/* Painel da loja na plataforma Bistrô Connect (gerado por ferramentas/montar-painel-plataforma.py a partir de paineis/loja).
   Configuração: ../assets/config.js (window.BC). Tabelas: lojas, membros, convites, categories, products, orders
   (plataforma/supabase/01-plataforma.sql), sempre filtradas pela loja escolhida (loja_id).""")
j = troca(j, "const CFG=window.LOJA||{};", "const CFG=window.BC||{};")
j = troca(j, "let db=null,demo=false,settings={store_name:CFG.nome||'Minha loja',",
          "let db=null,demo=false,lojaId=null,lojaSlug='',papel='dono',minhas=[],settings={store_name:'Minha loja',")
j = troca(j, "  if(CFG.cor&&/^#[0-9a-f]{3,8}$/i.test(CFG.cor))document.documentElement.style.setProperty('--marca',CFG.cor)}",
          "  const cor=settings.cor||CFG.cor;if(cor&&/^#[0-9a-f]{3,8}$/i.test(cor))document.documentElement.style.setProperty('--marca',cor)}")
j = troca(j, "  if(/permission denied|row-level security|JWT|42501/i.test(m))return 'Sua conta não tem acesso (confira a tabela admins no Supabase).';",
          "  if(/permission denied|row-level security|JWT|42501/i.test(m))return 'Sua função na equipe não permite isso.';\n  if(e&&e.code==='P0001'&&m)return m;")
j = troca(j, "function mostraForm(id){['fLogin','fCodigo','fCadastro2fa','semConfig'].forEach(",
          "function mostraForm(id){['fLogin','fCodigo','fCadastro2fa','semConfig','semLoja','escolheLoja'].forEach(")
j = troca(j, "  if(n.data.currentLevel==='aal2')return start();", "  if(n.data.currentLevel==='aal2')return escolheLoja();")
j = troca(j, "const r=await db.auth.mfa.challengeAndVerify({factorId:fatorId,code:codigo});if(r.error)throw r.error;await start()}",
          "const r=await db.auth.mfa.challengeAndVerify({factorId:fatorId,code:codigo});if(r.error)throw r.error;await escolheLoja()}")
j = troca(j, "const e=await db.auth.mfa.enroll({factorType:'totp',friendlyName:'Painel da loja '+Date.now()});",
          "const e=await db.auth.mfa.enroll({factorType:'totp',friendlyName:'Bistrô Connect '+Date.now()});")

# dados por loja
j = troca(j, "if(!qual||qual==='settings')tarefas.push(db.from('settings').select('*').eq('id',1).maybeSingle().then(r=>{if(r.error)throw r.error;if(r.data)settings=r.data}));",
          "if(!qual||qual==='settings')tarefas.push(db.from('lojas').select('*').eq('id',lojaId).maybeSingle().then(r=>{if(r.error)throw r.error;if(r.data){settings=r.data;lojaSlug=r.data.slug}}));")
j = troca(j, "db.from('categories').select('*').order('position')", "db.from('categories').select('*').eq('loja_id',lojaId).order('position')")
j = troca(j, "db.from('products').select('*').order('position')", "db.from('products').select('*').eq('loja_id',lojaId).order('position')")
j = troca(j, "db.from('orders').select('*').gte('created_at',desde)", "db.from('orders').select('*').eq('loja_id',lojaId).gte('created_at',desde)")
j = troca(j, "  const q=tabela==='settings'?db.from('settings').update(linha).eq('id',1):id!=null?db.from(tabela).update(linha).eq('id',id):db.from(tabela).insert(linha);",
          "  const q=tabela==='settings'?db.from('lojas').update(linha).eq('id',lojaId):id!=null?db.from(tabela).update(linha).eq('id',id):db.from(tabela).insert(Object.assign({loja_id:lojaId},linha));")
# categoria nova: id gerado pelo banco (ids são únicos na plataforma toda)
j = troca(j, "  if(id==='novo'){let novo=slug(nome);while(C(novo))novo+='-2';tenta(()=>grava('categories',{id:novo,name:nome,position:cats.length+1,active:true}),'Categoria criada').then(()=>{catSel=novo;desenhaCardapio()})}",
          "  if(id==='novo'){let nova=null;tenta(async()=>{nova=await grava('categories',{name:nome,position:cats.length+1,active:true})},'Categoria criada').then(()=>{if(nova)catSel=nova.id;desenhaCardapio()})}")
# fotos: bucket "lojas", pasta da loja
j = troca(j, "const nome='produtos/'+(crypto.randomUUID?crypto.randomUUID():Date.now()+'-'+Math.random().toString(36).slice(2))+'.jpg';\n  const {error}=await db.storage.from('site').upload(nome,blob,{contentType:'image/jpeg',cacheControl:'31536000',upsert:false});if(error)throw error;return db.storage.from('site').getPublicUrl(nome).data.publicUrl}",
          "const nome=lojaId+'/produtos/'+(crypto.randomUUID?crypto.randomUUID():Date.now()+'-'+Math.random().toString(36).slice(2))+'.jpg';\n  const {error}=await db.storage.from('lojas').upload(nome,blob,{contentType:'image/jpeg',cacheControl:'31536000',upsert:false});if(error)throw error;return db.storage.from('lojas').getPublicUrl(nome).data.publicUrl}")
# tempo real só da loja
j = troca(j, "canal=db.channel('loja').on('postgres_changes',{event:'*',schema:'public',table:'orders'},()=>carregar('orders')).on('postgres_changes',{event:'*',schema:'public',table:'products'},()=>carregar('products')).on('postgres_changes',{event:'*',schema:'public',table:'categories'},()=>carregar('categories')).on('postgres_changes',{event:'*',schema:'public',table:'settings'},()=>carregar('settings'))",
          "const fl='loja_id=eq.'+lojaId;canal=db.channel('loja-'+lojaId).on('postgres_changes',{event:'*',schema:'public',table:'orders',filter:fl},()=>carregar('orders')).on('postgres_changes',{event:'*',schema:'public',table:'products',filter:fl},()=>carregar('products')).on('postgres_changes',{event:'*',schema:'public',table:'categories',filter:fl},()=>carregar('categories')).on('postgres_changes',{event:'*',schema:'public',table:'lojas',filter:'id=eq.'+lojaId},()=>carregar('settings'))")
# demo
j = troca(j, "const r=await fetch('../assets/cardapio.json',{cache:'no-store'})", "const r=await fetch('../assets/cardapio-demo.json',{cache:'no-store'})")
j = troca(j, "$('#btnDemo').addEventListener('click',async()=>{demo=true;await dadosDemo();start()});",
          "$('#btnDemo').addEventListener('click',async()=>{demo=true;papel='dono';lojaSlug='padaria-da-ana';settings=Object.assign(settings,{store_name:'Loja de demonstração',slug:'padaria-da-ana',descricao:'',cor:'#B0703F',faz_entrega:true,faz_retirada:true,pagamentos:['Pix','Cartão','Dinheiro'],logo_url:'',capa_url:''});await dadosDemo();start()});")

# dados da loja: campos novos
j = troca(j, "$('#sAceita').checked=settings.accept_orders!==false}",
          "$('#sAceita').checked=settings.accept_orders!==false;\n  $('#sDesc').value=settings.descricao||'';$('#sEntrega').checked=settings.faz_entrega!==false;$('#sRetirada').checked=settings.faz_retirada!==false;$('#sCor').value=/^#[0-9a-f]{6}$/i.test(settings.cor||'')?settings.cor:'#B0703F';\n  document.querySelectorAll('[data-pag]').forEach(c=>c.checked=(settings.pagamentos||['Pix','Cartão','Dinheiro']).includes(c.dataset.pag));mostraFotoLoja()}")
j = troca(j, "  const w=digitos($('#sWhats').value);if(w&&(w.length<10||w.length>13))return toast('Confira o WhatsApp: DDD + número');\n  tenta(()=>grava('settings',{store_name:nome.slice(0,80),whatsapp:$('#sWhats').value.trim().slice(0,20),",
          "  let w=digitos($('#sWhats').value);if(w.length===10||w.length===11)w='55'+w;if(w&&(w.length<12||w.length>13))return toast('Confira o WhatsApp: DDD + número');\n  const pags=[...document.querySelectorAll('[data-pag]')].filter(c=>c.checked).map(c=>c.dataset.pag);if(!pags.length)return toast('Marque pelo menos uma forma de pagamento');\n  if(!$('#sEntrega').checked&&!$('#sRetirada').checked)return toast('Marque entrega, retirada ou os dois');\n  tenta(()=>grava('settings',{store_name:nome.slice(0,80),descricao:$('#sDesc').value.trim().slice(0,300),faz_entrega:$('#sEntrega').checked,faz_retirada:$('#sRetirada').checked,pagamentos:pags,cor:$('#sCor').value,whatsapp:w,")
j = troca(j, "instagram:$('#sInsta').value.trim().slice(0,60),address:$('#sEnd').value.trim().slice(0,160),hours:$('#sHoras').value.trim().slice(0,160),",
          "instagram:$('#sInsta').value.trim().slice(0,60),address:$('#sEnd').value.trim().slice(0,160),hours:$('#sHoras').value.trim().slice(0,160),")

# render: link, plano, equipe e permissões por função
j = troca(j, "if(aba==='cardapio')desenhaCardapio();if(aba==='loja')preencheLoja()}",
          "if(aba==='cardapio')desenhaCardapio();if(aba==='loja')preencheLoja();if(aba==='equipe')desenhaEquipe();if(aba==='inicio')desenhaLink()}")
j = troca(j, "const TITULOS={inicio:'Início',pedidos:'Pedidos',financeiro:'Financeiro',clientes:'Clientes',cardapio:'Cardápio',loja:'Dados da loja',ajustes:'Conta e ajustes'};",
          "const TITULOS={inicio:'Início',pedidos:'Pedidos',financeiro:'Financeiro',clientes:'Clientes',cardapio:'Cardápio',loja:'Dados da loja',equipe:'Equipe',ajustes:'Conta e ajustes'};\n"
          "const ABAS_PAPEL={dono:Object.keys(TITULOS),gerente:Object.keys(TITULOS),atendente:['inicio','pedidos','clientes','ajustes'],cozinha:['pedidos','ajustes']};\n"
          "function aplicaPapel(){document.querySelectorAll('[data-papel]').forEach(el=>{el.hidden=!el.dataset.papel.split(' ').includes(papel)})}")
j = troca(j, "function abrirAba(t){if(!TITULOS[t]||(!RECURSOS.pedidos&&['pedidos','financeiro','clientes'].includes(t)))t='inicio';",
          "function abrirAba(t){if(!TITULOS[t]||(!RECURSOS.pedidos&&['pedidos','financeiro','clientes'].includes(t)))t='inicio';if(!(ABAS_PAPEL[papel]||[]).includes(t))t=(ABAS_PAPEL[papel]||['pedidos'])[0];")

extra = r"""
/* ================= plataforma: lojas, link, plano e equipe ================= */
const SITE=String(CFG.site||location.origin).replace(/\/+$/,'');
const linkDaLoja=()=>SITE+'/l/'+(lojaSlug||settings.slug||'');
const NOMES_PAPEL={dono:'Dono',gerente:'Gerente',atendente:'Atendente',cozinha:'Cozinha'};
async function escolheLoja(){
  const r=await db.rpc('minhas_lojas');if(r.error)throw r.error;minhas=(r.data||[]).filter(l=>l.status!=='cancelada');
  if(!minhas.length)return mostraForm('semLoja');
  let guardada='';try{guardada=sessionStorage.getItem('bc-loja')||''}catch(e){}
  const l=minhas.find(x=>x.id===guardada)||(minhas.length===1?minhas[0]:null);
  if(l)return usaLoja(l);
  $('#listaLojas').innerHTML=minhas.map(x=>`<button type="button" class="item" data-usa-loja="${esc(x.id)}"><div class="who"><b>${esc(x.store_name)}</b><span class="muted">${esc(NOMES_PAPEL[x.papel]||x.papel)} · /l/${esc(x.slug)}</span></div><span class="chip">${x.status==='ativa'?'Ativa':'Suspensa'}</span></button>`).join('');
  mostraForm('escolheLoja')}
function usaLoja(l){lojaId=l.id;lojaSlug=l.slug;papel=l.papel;settings.store_name=l.store_name;try{sessionStorage.setItem('bc-loja',l.id)}catch(e){}return start()}
document.addEventListener('click',e=>{const b=e.target.closest('[data-usa-loja]');if(!b)return;const l=minhas.find(x=>x.id===b.dataset.usaLoja);if(l)usaLoja(l)});
$('#btnTrocaLoja').addEventListener('click',()=>{try{sessionStorage.removeItem('bc-loja')}catch(e){}location.reload()});
function desenhaLink(){const u=linkDaLoja();$('#linkLoja').textContent=u.replace(/^https?:\/\//,'');$('#linkLoja').href=u;$('#verSite').href=u;
  $('#btnZapLink').href='https://wa.me/?text='+encodeURIComponent('Agora você pode fazer seu pedido na '+(settings.store_name||'nossa loja')+' pelo site: '+u);
  if(['dono','gerente'].includes(papel))desenhaPlano()}
$('#btnCopiaLink').addEventListener('click',()=>copia(linkDaLoja(),'Link copiado'));
async function copia(t,ok){try{await navigator.clipboard.writeText(t);toast(ok)}catch(e){prompt('Copie:',t)}}
let planoEm=0;
async function desenhaPlano(){if(demo){$('#kpisPlano').className='kpis';$('#kpisPlano').innerHTML=kpi('Vendido no mês','R$ 2.480,00','pedidos não cancelados')+kpi('Plano','Começo','grátis até R$ 3 mil');$('#planoFaixa').textContent='demonstração';return}
  if(Date.now()-planoEm<60000)return;planoEm=Date.now();
  const r=await db.rpc('faturamento_loja',{p_loja:lojaId});if(r.error)return;const f=r.data||{};
  $('#kpisPlano').className='kpis';$('#kpisPlano').innerHTML=kpi('Vendido no mês',brl(f.vendido),'pedidos não cancelados')+kpi('Plano '+(f.plano_nome||''),num(f.mensalidade)?brl(f.mensalidade)+'/mês':'Grátis',f.ate_valor?'faixa até '+brl0(f.ate_valor):'faixa sem limite');
  $('#planoFaixa').textContent=new Date().toLocaleDateString('pt-BR',{month:'long',year:'numeric'})}
let equipe=[],convites=[];
async function desenhaEquipe(){if(!demo){const [m,c]=await Promise.all([db.from('membros').select('*').eq('loja_id',lojaId).order('criado_em'),db.from('convites').select('id,email,papel,criado_em,expira_em').eq('loja_id',lojaId).is('aceito_em',null).order('criado_em',{ascending:false})]);
    if(m.error||c.error)return notice('Erro ao carregar a equipe: '+erroAmigavel(m.error||c.error));equipe=m.data||[];convites=c.data||[]}
  else if(!equipe.length){equipe=[{user_id:'u1',email:'voce@exemplo.com',papel:'dono',criado_em:new Date().toISOString()},{user_id:'u2',email:'caixa@exemplo.com',papel:'atendente',criado_em:new Date().toISOString()}]}
  const souDono=papel==='dono';
  $('#listaEquipe').innerHTML=equipe.map(p=>`<div class="item"><div class="who"><b>${esc(p.email||'(sem e-mail)')}</b><span class="muted">desde ${dataBR(p.criado_em)}</span></div><div class="acts">${souDono?`<select data-muda-papel="${esc(p.user_id)}" aria-label="Função de ${esc(p.email)}">${Object.keys(NOMES_PAPEL).map(k=>`<option value="${k}"${k===p.papel?' selected':''}>${NOMES_PAPEL[k]}</option>`).join('')}</select><button class="btn small perigo" type="button" data-remove="${esc(p.user_id)}">Remover</button>`:`<span class="chip">${esc(NOMES_PAPEL[p.papel]||p.papel)}</span>`}</div></div>`).join('')||'<div class="empty">Só você por enquanto.</div>';
  $('#listaConvites').innerHTML=convites.map(c=>`<div class="item"><div class="who"><b>${esc(c.email)}</b><span class="muted">${esc(NOMES_PAPEL[c.papel]||c.papel)} · vence ${dataBR(c.expira_em)}</span></div><div class="acts"><button class="btn small" type="button" data-cancela-convite="${esc(c.id)}">Cancelar</button></div></div>`).join('')||'<div class="empty">Nenhum convite esperando.</div>';
  $('#cvPapel').querySelector('option[value="gerente"]').disabled=!souDono}
$('#conviteForm').addEventListener('submit',async e=>{e.preventDefault();const email=$('#cvEmail').value.trim().toLowerCase(),pp=$('#cvPapel').value;
  if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email))return toast('Digite um e-mail válido');
  if(demo)return toast('Na demonstração o convite não é criado');
  const r=await db.rpc('convidar_membro',{p_loja:lojaId,p_email:email,p_papel:pp});if(r.error)return toast(erroAmigavel(r.error));
  const u=SITE+'/entrar.html#convite='+r.data;$('#cvLink').textContent=u;$('#cvLinkBox').hidden=false;
  $('#btnZapConvite').href='https://wa.me/?text='+encodeURIComponent('Você foi convidado para a equipe da '+(settings.store_name||'loja')+' no Bistrô Connect. Crie seu acesso com o e-mail '+email+': '+u);
  $('#cvEmail').value='';toast('Convite criado');desenhaEquipe()});
$('#btnCopiaConvite').addEventListener('click',()=>copia($('#cvLink').textContent,'Convite copiado'));
document.addEventListener('change',async e=>{const s=e.target.closest('[data-muda-papel]');if(!s)return;if(demo)return toast('Na demonstração nada muda');
  const r=await db.rpc('mudar_membro',{p_loja:lojaId,p_user:s.dataset.mudaPapel,p_papel:s.value});if(r.error)toast(erroAmigavel(r.error));else toast('Função alterada');desenhaEquipe()});
document.addEventListener('click',async e=>{const b=e.target.closest('[data-remove],[data-cancela-convite]');if(!b)return;if(demo)return toast('Na demonstração nada muda');
  if(b.dataset.remove){const p=equipe.find(x=>x.user_id===b.dataset.remove);if(!confirm('Remover '+(p&&p.email||'esta pessoa')+' da equipe? O acesso termina na hora.'))return;
    const r=await db.rpc('mudar_membro',{p_loja:lojaId,p_user:b.dataset.remove,p_papel:null});if(r.error)return toast(erroAmigavel(r.error));toast('Removido da equipe')}
  else{const r=await db.from('convites').delete().eq('id',b.dataset.cancelaConvite);if(r.error)return toast(erroAmigavel(r.error));toast('Convite cancelado')}
  desenhaEquipe()});
/* logo e capa da loja */
function mostraFotoLoja(){[['#sLogoPrev',settings.logo_url],['#sCapaPrev',settings.capa_url]].forEach(([s,u])=>{const el=$(s),v=imgUrl(u);el.style.backgroundImage=v?`url('${v.replace(/'/g,'%27')}')`:'';el.classList.toggle('tem',!!v)})}
async function sobeFotoLoja(input,campo,max){const f=input.files[0];input.value='';if(!f)return;
  if(!/^image\/(jpeg|png|webp)$/.test(f.type))return toast('Envie JPG, PNG ou WebP');if(f.size>5*1024*1024)return toast('Foto maior que 5 MB');
  await tenta(async()=>{const b=await reduz(f,max);let u;if(demo)u=URL.createObjectURL(b);else{const nome=lojaId+'/loja/'+campo+'-'+Date.now()+'.jpg';const up=await db.storage.from('lojas').upload(nome,b,{contentType:'image/jpeg',cacheControl:'31536000'});if(up.error)throw up.error;u=db.storage.from('lojas').getPublicUrl(nome).data.publicUrl}
    await grava('settings',{[campo]:u});mostraFotoLoja()},'Foto salva')}
$('#sLogo').addEventListener('change',function(){sobeFotoLoja(this,'logo_url',600)});
$('#sCapa').addEventListener('change',function(){sobeFotoLoja(this,'capa_url',1800)});
document.addEventListener('click',e=>{const b=e.target.closest('[data-tira]');if(!b)return;tenta(async()=>{await grava('settings',{[b.dataset.tira]:''});mostraFotoLoja()},'Foto retirada')});
"""
j = troca(j, "/* ================= início ================= */", extra + "\n/* ================= início ================= */")
j = troca(j, "  $('#auth').hidden=true;$('#app').hidden=false;$('#faixaDemo').hidden=!demo;",
          "  $('#auth').hidden=true;$('#app').hidden=false;$('#faixaDemo').hidden=!demo;aplicaPapel();$('#btnTrocaLoja').hidden=minhas.length<2;")
j = troca(j, "  abrirAba(lsGet('lj-aba',RECURSOS.pedidos?'pedidos':'cardapio'))}", "  if(!demo)db.rpc('eh_admin_plataforma').then(r=>{if(r.data===true)$('#btnPlataforma').hidden=false});\n  abrirAba(lsGet('lj-aba','inicio'))}")
open(f"{DEST}/painel.js", "w", encoding="utf-8").write(j)

# estilos extras
css = """
/* ===== plataforma ===== */
.centro{text-align:center}
.link-loja{margin:6px 0 12px;font-weight:700;word-break:break-all}
.link-loja a{color:var(--marca)}
.fotos-loja{display:grid;grid-template-columns:1fr 2fr;gap:14px}
.foto-prev.larga{aspect-ratio:16/7}
.pagamentos{border:0;padding:0;margin:0;display:flex;flex-wrap:wrap;gap:6px 18px}
.pagamentos legend{font-size:13px;font-weight:600;margin-bottom:6px;padding:0}
.lista-funcoes{margin:0;padding-left:18px;display:grid;gap:6px}
#listaLojas .item{width:100%;text-align:left;cursor:pointer;background:none;border:1px solid var(--linha,rgba(0,0,0,.12));border-radius:12px;margin-bottom:8px;padding:12px}
#listaEquipe select{min-height:36px}
@media (max-width:640px){.fotos-loja{grid-template-columns:1fr}}
"""
open(f"{DEST}/painel.css", "a", encoding="utf-8").write(css)
subprocess.run(["python3", "ferramentas/csp.py", f"{DEST}/index.html"], check=True)
print("painel da plataforma montado em", DEST)
