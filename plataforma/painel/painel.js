/* Painel da loja na plataforma Bistrô Connect (gerado por ferramentas/montar-painel-plataforma.py a partir de paineis/loja).
   Configuração: ../assets/config.js (window.BC). Tabelas: lojas, membros, convites, categories, products, orders
   (plataforma/supabase/01-plataforma.sql), sempre filtradas pela loja escolhida (loja_id).
   Segurança: login com 2 etapas obrigatório, sessão só na aba, saída por inatividade, dados escritos com esc(). */
(function () {
'use strict';

const CFG=window.BC||{};
const RECURSOS=Object.assign({pedidos:true},CFG.recursos||{});
const STATUS=[['novo','Novos'],['confirmado','Confirmados'],['em_preparo','Em preparo'],['pronto','Prontos / saiu'],['entregue','Entregue'],['cancelado','Cancelado']];
const PROXIMO={novo:['confirmado','Confirmar'],confirmado:['em_preparo','Preparar'],em_preparo:['pronto','Pronto'],pronto:['entregue','Entregue']};
const FORMAS=['Pix','Cartão','Dinheiro'];
const INATIVO_MS=30*60*1000;

let db=null,demo=false,lojaId=null,lojaSlug='',papel='dono',minhas=[],settings={store_name:'Minha loja',whatsapp:CFG.whatsapp||'',address:'',hours:'',instagram:'',delivery_fee:0,min_order:0,accept_orders:true};
let cats=[],prods=[],orders=[],catSel='',aba='inicio',periodo='hoje',somLigado=true,vistos=new Set(),primeiraCarga=true,canal=null;

/* ================= utilidades ================= */
const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const iso=d=>{d=new Date(d);d.setMinutes(d.getMinutes()-d.getTimezoneOffset());return d.toISOString().slice(0,10)};
const hoje=()=>iso(new Date());
const brl=n=>'R$ '+Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
const brl0=n=>'R$ '+Number(n||0).toLocaleString('pt-BR',{maximumFractionDigits:0});
const num=v=>{v=String(v??'').replace(/[^\d,.-]/g,'');if(v.includes(','))v=v.replace(/\./g,'').replace(',','.');const n=parseFloat(v);return isFinite(n)&&n>=0?Math.round(n*100)/100:0};
const digitos=t=>String(t||'').replace(/\D/g,'');
const dataBR=s=>{const d=new Date(s);return isNaN(d)?'—':d.toLocaleDateString('pt-BR')};
const horaBR=s=>{const d=new Date(s);return isNaN(d)?'':d.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'})};
const diaLocal=s=>iso(new Date(s));
const primeiroNome=s=>String(s||'').trim().split(/\s+/)[0]||'';
const stNome=k=>(STATUS.find(s=>s[0]===k)||[k,k])[1];
const P=id=>prods.find(p=>String(p.id)===String(id));
const C=id=>cats.find(c=>String(c.id)===String(id));
const OD=id=>orders.find(o=>String(o.id)===String(id));
function zapUrl(fone,txt){let d=digitos(fone);if(d.length>=10&&d.length<=11)d='55'+d;if(d.length<12||d.length>13)return '';return 'https://wa.me/'+d+(txt?'?text='+encodeURIComponent(txt):'')}
function imgUrl(u){u=String(u||'');if(!u)return '';if(/^(https:|data:image\/|blob:)/.test(u))return u;if(/^[a-z0-9/_.-]+$/i.test(u))return '../'+u.replace(/^\/+/,'');return ''}
function lsGet(k,d){try{const v=localStorage.getItem(k);return v==null?d:JSON.parse(v)}catch(e){return d}}
function lsSet(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function toast(t){const el=$('#toast');el.textContent=t;el.hidden=false;clearTimeout(toast.t);toast.t=setTimeout(()=>el.hidden=true,2600)}
function notice(t){$('#notice').textContent=t||'';$('#notice').hidden=!t}
function slug(s){return String(s||'').normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,40)||'cat'}
function erroAmigavel(e){const m=(e&&(e.message||e.error_description))||'';
  if(/Invalid login credentials/i.test(m))return 'E-mail ou senha incorretos.';
  if(/Invalid TOTP|invalid code|expired|mfa_verification/i.test(m))return 'Código inválido ou vencido. Confira o app e tente de novo.';
  if(/rate limit|too many/i.test(m))return 'Muitas tentativas. Espere alguns minutos.';
  if(/permission denied|row-level security|JWT|42501/i.test(m))return 'Sua função na equipe não permite isso.';
  if(e&&e.code==='P0001'&&m)return m;
  if(/Failed to fetch|NetworkError|Load failed/i.test(m))return 'Sem conexão com o servidor. Verifique a internet.';
  if(/weak|password should/i.test(m))return 'Senha fraca. Use pelo menos 12 caracteres.';
  return 'Não foi possível concluir. Tente de novo.'}
function marca(){const n=settings.store_name||CFG.nome||'Minha loja';document.querySelectorAll('.loja-nome').forEach(e=>e.textContent=n);document.querySelectorAll('.marca-ico').forEach(e=>e.dataset.letra=n.trim().charAt(0).toUpperCase());document.title=(pendentes()?'('+pendentes()+') ':'')+'Painel · '+n;
  const cor=settings.cor||CFG.cor;if(cor&&/^#[0-9a-f]{3,8}$/i.test(cor))document.documentElement.style.setProperty('--marca',cor)}
document.querySelectorAll('[data-recurso="pedidos"]').forEach(el=>{if(!RECURSOS.pedidos)el.hidden=true});
marca();

/* ================= tema ================= */
function aplicaTema(t){if(t==='light'||t==='dark')document.documentElement.dataset.theme=t;else delete document.documentElement.dataset.theme;document.querySelectorAll('[data-tema]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.tema===(t||'auto')))}
aplicaTema(lsGet('lj-tema','light'));
document.querySelectorAll('[data-tema]').forEach(b=>b.addEventListener('click',()=>{lsSet('lj-tema',b.dataset.tema);aplicaTema(b.dataset.tema)}));
$('#btnTema').addEventListener('click',()=>{const t=getComputedStyle(document.documentElement).colorScheme.includes('dark')?'light':'dark';lsSet('lj-tema',t);aplicaTema(t)});

/* ================= entrada: senha + 2 etapas ================= */
function mostraForm(id){if(demo)return;['fLogin','fCodigo','fCadastro2fa','semConfig','semLoja','escolheLoja'].forEach(f=>$('#'+f).hidden=f!==id);$('#auth').hidden=false;$('#app').hidden=true;const i=$('#'+id).querySelector('input');if(i)i.focus()}
function msgAuth(t,ok){const m=$('#authMsg');m.textContent=t||'';m.className='auth-msg'+(ok?' ok':'')}
let tentativas=0,bloqueadoAte=0,fatorNovo=null,saindo=false;
$('#fLogin').addEventListener('submit',async function(e){e.preventDefault();msgAuth('');
  if(Date.now()<bloqueadoAte)return msgAuth('Muitas tentativas. Aguarde '+Math.ceil((bloqueadoAte-Date.now())/1000)+' s.');
  const email=$('#lgEmail').value.trim().toLowerCase(),senha=$('#lgSenha').value;
  if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)||!senha)return msgAuth('Informe e-mail e senha.');
  const b=this.querySelector('button');b.disabled=true;
  try{const r=await db.auth.signInWithPassword({email,password:senha});if(r.error)throw r.error;tentativas=0;$('#lgSenha').value='';await segundaEtapa()}
  catch(err){tentativas++;if(tentativas>=5)bloqueadoAte=Date.now()+60000*Math.min(tentativas-4,10);msgAuth(erroAmigavel(err))}
  finally{b.disabled=false}});
async function segundaEtapa(){
  const n=await db.auth.mfa.getAuthenticatorAssuranceLevel();if(n.error)throw n.error;
  if(n.data.currentLevel==='aal2')return escolheLoja();
  const f=await db.auth.mfa.listFactors();if(f.error)throw f.error;
  if(f.data.totp&&f.data.totp.length){$('#cdCodigo').value='';return mostraForm('fCodigo')}
  for(const p of (f.data.all||[]).filter(x=>x.status==='unverified'))await db.auth.mfa.unenroll({factorId:p.id});
  const e=await db.auth.mfa.enroll({factorType:'totp',issuer:'Bistrô Connect',friendlyName:'Bistrô Connect '+Date.now()});if(e.error)throw e.error;
  fatorNovo=e.data.id;$('#qr2fa').src=e.data.totp.qr_code;$('#seg2fa').textContent=e.data.totp.secret;$('#cdNovo').value='';mostraForm('fCadastro2fa')}
async function verifica(fatorId,codigo,botao){if(!/^\d{6}$/.test(codigo))return msgAuth('Digite os 6 números do app.');botao.disabled=true;msgAuth('');
  try{const r=await db.auth.mfa.challengeAndVerify({factorId:fatorId,code:codigo});if(r.error)throw r.error;await escolheLoja()}catch(e){msgAuth(erroAmigavel(e))}finally{botao.disabled=false}}
$('#fCodigo').addEventListener('submit',async function(e){e.preventDefault();const f=await db.auth.mfa.listFactors(),fator=f.data&&f.data.totp&&f.data.totp[0];if(!fator)return segundaEtapa();verifica(fator.id,$('#cdCodigo').value.trim(),this.querySelector('button[type=submit]'))});
$('#fCadastro2fa').addEventListener('submit',function(e){e.preventDefault();verifica(fatorNovo,$('#cdNovo').value.trim(),this.querySelector('button[type=submit]'))});
['#cdCodigo','#cdNovo'].forEach(s=>$(s).addEventListener('input',function(){this.value=digitos(this.value).slice(0,6);if(this.value.length===6)this.form.requestSubmit()}));
async function sair(motivo){if(saindo)return;saindo=true;if(db&&!demo){try{await db.auth.signOut()}catch(e){}}try{sessionStorage.setItem('lj-msg',motivo||'')}catch(e){}location.reload()}
document.addEventListener('click',e=>{if(e.target.closest('[data-sair]'))sair('')});
let ultimoUso=Date.now();
['pointerdown','keydown','scroll','touchstart'].forEach(t=>addEventListener(t,()=>{ultimoUso=Date.now()},{passive:true}));
setInterval(()=>{if(!$('#app').hidden&&!demo&&Date.now()-ultimoUso>INATIVO_MS)sair('Você saiu por inatividade. Entre de novo.')},30000);

/* ================= dados ================= */
async function carregar(qual){
  if(demo){render();return}
  const tarefas=[];
  if(!qual||qual==='settings')tarefas.push(db.from('lojas').select('*').eq('id',lojaId).maybeSingle().then(r=>{if(r.error)throw r.error;if(r.data){settings=r.data;lojaSlug=r.data.slug}}));
  if(!qual||qual==='categories')tarefas.push(db.from('categories').select('*').eq('loja_id',lojaId).order('position').then(r=>{if(r.error)throw r.error;cats=r.data||[]}));
  if(!qual||qual==='products')tarefas.push(db.from('products').select('*').eq('loja_id',lojaId).order('position').then(r=>{if(r.error)throw r.error;prods=r.data||[]}));
  if(RECURSOS.pedidos&&(!qual||qual==='orders')){const desde=new Date(Date.now()-120*864e5).toISOString();
    tarefas.push(db.from('orders').select('*').eq('loja_id',lojaId).gte('created_at',desde).order('created_at',{ascending:false}).limit(3000).then(r=>{if(r.error)throw r.error;orders=r.data||[]}))}
  try{await Promise.all(tarefas);notice('')}catch(e){notice('Erro ao carregar: '+erroAmigavel(e))}
  verificaNovos();render()}
async function grava(tabela,linha,id){
  if(demo){const lista={categories:cats,products:prods,orders:orders}[tabela];
    if(tabela==='settings'){Object.assign(settings,linha);render();return settings}
    const cur=id!=null?lista.find(x=>String(x.id)===String(id)):null;if(cur){Object.assign(cur,linha);render();return cur}
    const n=Object.assign({id:linha.id||('d'+Date.now()+Math.random().toString(36).slice(2,6)),created_at:new Date().toISOString()},linha);lista.push(n);render();return n}
  const q=tabela==='settings'?db.from('lojas').update(linha).eq('id',lojaId):id!=null?db.from(tabela).update(linha).eq('id',id):db.from(tabela).insert(Object.assign({loja_id:lojaId},linha));
  const {data,error}=await q.select().maybeSingle();if(error)throw error;await carregar(tabela);return data}
async function apaga(tabela,id){if(demo){const k={categories:'cats',products:'prods'}[tabela];if(k==='cats')cats=cats.filter(x=>String(x.id)!==String(id));else prods=prods.filter(x=>String(x.id)!==String(id));render();return}
  const {error}=await db.from(tabela).delete().eq('id',id);if(error)throw error;await carregar(tabela)}
async function tenta(fn,ok){try{await fn();if(ok)toast(ok)}catch(e){console.error(e);toast(erroAmigavel(e))}}

/* ================= alerta de pedido novo ================= */
let audio=null;
function bip(){if(!somLigado)return;try{audio=audio||new (window.AudioContext||window.webkitAudioContext)();const t0=audio.currentTime;
  [[880,0],[1175,.18],[1568,.36]].forEach(([f,d])=>{const o=audio.createOscillator(),g=audio.createGain();o.type='sine';o.frequency.value=f;g.gain.setValueAtTime(.0001,t0+d);g.gain.exponentialRampToValueAtTime(.35,t0+d+.02);g.gain.exponentialRampToValueAtTime(.0001,t0+d+.32);o.connect(g).connect(audio.destination);o.start(t0+d);o.stop(t0+d+.34)})}catch(e){}}
function pendentes(){return orders.filter(o=>o.status==='novo').length}
function verificaNovos(){
  const novos=orders.filter(o=>!vistos.has(String(o.id)));orders.forEach(o=>vistos.add(String(o.id)));
  if(primeiraCarga){primeiraCarga=false;return}
  const chegaram=novos.filter(o=>o.status==='novo');if(!chegaram.length)return;
  bip();toast('Pedido novo: '+chegaram.map(o=>o.code).join(', '));
  chegaram.forEach(o=>chegou.add(String(o.id)));setTimeout(()=>chegaram.forEach(o=>chegou.delete(String(o.id))),6000);
  if(document.hidden&&'Notification' in window&&Notification.permission==='granted'){try{const o=chegaram[0];new Notification('Pedido novo · '+(settings.store_name||''),{body:o.code+' · '+(o.customer_name||'')+' · '+brl(o.total),tag:'pedido-'+o.id})}catch(e){}}}
const chegou=new Set();
$('#btnSom').addEventListener('click',function(){somLigado=!somLigado;lsSet('lj-som',somLigado);this.setAttribute('aria-pressed',somLigado);this.textContent=somLigado?'🔔 Som ligado':'🔕 Som desligado';if(somLigado)bip()});
$('#btnNotif').addEventListener('click',async()=>{if(!('Notification' in window))return toast('Este navegador não mostra avisos');const p=await Notification.requestPermission();toast(p==='granted'?'Avisos ligados':'Avisos não permitidos pelo navegador');$('#btnNotif').hidden=p==='granted'});
setInterval(()=>{if(aba==='pedidos')desenhaPedidos()},30000);

/* ================= navegação ================= */
const TITULOS={inicio:'Visão geral',pedidos:'Pedidos',financeiro:'Financeiro',clientes:'Clientes',cardapio:'Cardápio',loja:'Dados da loja',equipe:'Equipe',ajustes:'Conta e ajustes'};
const ABAS_PAPEL={dono:Object.keys(TITULOS),gerente:Object.keys(TITULOS),atendente:['inicio','pedidos','clientes','ajustes'],cozinha:['pedidos','ajustes']};
function aplicaPapel(){document.querySelectorAll('[data-papel]').forEach(el=>{el.hidden=!el.dataset.papel.split(' ').includes(papel)})}
function abrirAba(t){if(!TITULOS[t]||(!RECURSOS.pedidos&&['pedidos','financeiro','clientes'].includes(t)))t='inicio';if(!(ABAS_PAPEL[papel]||[]).includes(t))t=(ABAS_PAPEL[papel]||['pedidos'])[0];aba=t;
  document.querySelectorAll('[data-aba]').forEach(b=>{if(b.dataset.aba===t)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current')});
  document.querySelectorAll('section.panel').forEach(p=>p.hidden=p.dataset.panel!==t);$('#titulo').textContent=TITULOS[t];lsSet('lj-aba',t);render();scrollTo({top:0})}
document.querySelectorAll('[data-aba]').forEach(b=>b.addEventListener('click',()=>abrirAba(b.dataset.aba)));
document.addEventListener('click',e=>{const b=e.target.closest('[data-ir]');if(b)abrirAba(b.dataset.ir)});

/* ================= render ================= */
function render(){if($('#app').hidden)return;marca();
  const n=pendentes();$('#cNovos').textContent=n||'';
  const aberta=settings.accept_orders!==false;$('#btnPausa').textContent=aberta?'Recebendo pedidos':'Pedidos pausados';$('#btnPausa').classList.toggle('fechada',!aberta);
  $('#lojaStatus').textContent=RECURSOS.pedidos?(aberta?'Recebendo pedidos':'Pedidos pausados'):'Cardápio online';$('#lojaStatus').classList.toggle('fechada',RECURSOS.pedidos&&!aberta);
  const h=new Date().getHours();$('#subtitulo').textContent=aba==='inicio'?(h<12?'Bom dia':h<18?'Boa tarde':'Boa noite')+' · '+new Date().toLocaleDateString('pt-BR',{weekday:'long',day:'2-digit',month:'long'}):'';
  if(aba==='inicio')desenhaInicio();if(aba==='pedidos')desenhaPedidos();if(aba==='financeiro')desenhaFinanceiro();if(aba==='clientes')desenhaClientes();if(aba==='cardapio')desenhaCardapio();if(aba==='loja')preencheLoja();if(aba==='equipe')desenhaEquipe();if(aba==='inicio')desenhaLink()}
function kpi(l,v,s,cls,serie){return `<div class="kpi${cls?' '+cls:''}${serie?' com-spark':''}"><span class="lbl">${esc(l)}</span><span class="val">${esc(v)}</span>${s?`<span class="sub">${esc(s)}</span>`:''}${serie?spark(serie):''}</div>`}
/* mini gráfico dos últimos 7 dias dentro do cartão */
function spark(serie){const mx=Math.max(1,...serie),w=100,h=30,n=serie.length-1||1,pts=serie.map((v,i)=>[i/n*w,h-2-(v/mx)*(h-6)]);const linha=pts.map(p=>p[0].toFixed(1)+','+p[1].toFixed(1)).join(' ');
  return `<svg class="spark" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" aria-hidden="true"><polygon points="0,${h} ${linha} ${w},${h}"/><polyline points="${linha}"/><circle cx="${pts[pts.length-1][0]}" cy="${pts[pts.length-1][1]}" r="2.6"/></svg>`}
function ultimos7(fn){const r=[];for(let i=6;i>=0;i--){const d=new Date();d.setDate(d.getDate()-i);const dia=iso(d);r.push(fn(validos(orders).filter(o=>diaLocal(o.created_at)===dia)))}return r}
function barras(el,serie,rotulos,fmt,cls){const mx=Math.max(1,...serie);el.className='grafico'+(cls?' '+cls:'');el.style.gridTemplateColumns='repeat('+serie.length+',minmax(0,1fr))';el.innerHTML=serie.map((v,i)=>`<div class="gb"><b>${esc(fmt?fmt(v):v)}</b><i style="height:${Math.max(2,v/mx*100)}%"></i><span>${esc(rotulos[i])}</span></div>`).join('')}
const validos=lista=>lista.filter(o=>o.status!=='cancelado');

function desenhaInicio(){
  const k=$('#kpisInicio');
  if(RECURSOS.pedidos){const t=hoje(),hj=validos(orders.filter(o=>diaLocal(o.created_at)===t)),abertos=orders.filter(o=>['novo','confirmado','em_preparo','pronto'].includes(o.status)),d30=validos(orders.filter(o=>Date.now()-new Date(o.created_at)<30*864e5)),soma=d30.reduce((s,o)=>s+num(o.total),0);
    const novos=orders.filter(o=>o.status==='novo').length,agora=new Date(),mes=validos(orders.filter(o=>{const d=new Date(o.created_at);return d.getFullYear()===agora.getFullYear()&&d.getMonth()===agora.getMonth()})).reduce((s,o)=>s+num(o.total),0);
    k.className='kpis k4';k.innerHTML=kpi('Pedidos novos',novos,novos?'esperando você confirmar':'nenhum esperando',novos?'alert':'')+kpi('Pedidos hoje',hj.length,hj.length?'último às '+horaBR(hj[0].created_at):'nenhum ainda','',ultimos7(l=>l.length))+kpi('Vendas no mês',brl(mes),'pedidos não cancelados','',ultimos7(l=>l.reduce((s,o)=>s+num(o.total),0)))+kpi('Produtos no site',prods.filter(p=>p.active).length,prods.length+' cadastrados');
    const dias=[];for(let i=6;i>=0;i--){const d=new Date();d.setDate(d.getDate()-i);dias.push(iso(d))}
    const sem=dias.map(d=>validos(orders).filter(o=>diaLocal(o.created_at)===d).length);
    barras($('#grafDias'),sem,dias.map(d=>new Date(d+'T12:00:00').toLocaleDateString('pt-BR',{weekday:'short'}).replace('.','')),null,'dias7');
    $('#semTotal').textContent=sem.reduce((a,b)=>a+b,0)+' pedidos na semana';
    const ST_ROT={novo:'Novo',confirmado:'Confirmado',em_preparo:'Em preparo',pronto:'Pronto',entregue:'Entregue',cancelado:'Cancelado'};
    const ult=orders.slice().sort((a,b)=>new Date(b.created_at)-new Date(a.created_at)).slice(0,6);
    $('#ultimosPedidos').innerHTML=ult.length?ult.map(o=>{const n=(o.items||[]).reduce((s,i)=>s+(+i.qty||0),0);return `<button type="button" class="ult-l" data-ir="pedidos"><b>${esc(o.code)}</b><span>${esc(primeiroNome(o.customer_name))} · ${n} ${n===1?'item':'itens'}</span><em>${brl(o.total)}</em><i class="st st-${esc(o.status)}">${esc(ST_ROT[o.status]||o.status)}</i></button>`}).join(''):'<div class="empty">Os pedidos aparecem aqui assim que chegarem.</div>';
    const hs=Array(24).fill(0);d30.forEach(o=>hs[new Date(o.created_at).getHours()]++);barras($('#grafHoras'),hs,hs.map((_,i)=>i%3===0?i+'h':''),null,'horas');
    const qt={};d30.forEach(o=>(o.items||[]).forEach(i=>{qt[i.name]=(qt[i.name]||0)+(+i.qty||0)}));const top=Object.entries(qt).sort((a,b)=>b[1]-a[1]).slice(0,8),mx=top.length?top[0][1]:1;
    $('#maisVendidos').innerHTML=top.length?top.map(([n,q],i)=>`<div class="rk"><span>${i+1}</span><div><div>${esc(n)}</div><div class="barra"><i style="width:${q/mx*100}%"></i></div></div><b>${q}</b></div>`).join(''):'<div class="empty">Os mais vendidos aparecem aqui quando chegarem pedidos.</div>'}
  else{k.className='kpis k4';k.innerHTML=kpi('Itens no cardápio',prods.filter(p=>p.active).length,prods.length+' cadastrados')+kpi('Categorias',cats.length,'')+kpi('Destaques',prods.filter(p=>p.featured&&p.active).length,'aparecem nas vitrines')+kpi('Pausados',prods.filter(p=>!p.active).length,'fora do site agora',prods.some(p=>!p.active)?'alert':'')}
  $('#resumoCardapio').innerHTML=cats.length?cats.map(c=>{const t=prods.filter(p=>p.category_id===c.id),a=t.filter(p=>p.active).length;return `<div class="rk"><span>•</span><div>${esc(c.name)}</div><b>${a}/${t.length}</b></div>`}).join(''):'<div class="empty">Nenhuma categoria ainda.</div>'}

/* ================= pedidos ================= */
function optTxt(i){const a=(i.options||[]).map(x=>x.name);return a.length?' ('+a.join(', ')+')':''}
function optHtml(i){const a=(i.options||[]).map(x=>x.name);return a.length?`<br><small class="muted">${esc(a.join(', '))}</small>`:''}
function resumoItens(o){return (o.items||[]).map(i=>i.qty+'× '+i.name+optTxt(i)).join(', ')}
function tempo(o){const m=Math.max(0,Math.round((Date.now()-new Date(o.created_at))/60000));return m<60?'há '+m+' min':m<1440?'há '+Math.floor(m/60)+'h'+String(m%60).padStart(2,'0'):dataBR(o.created_at)}
const linkRastreio=o=>o&&/^[a-f0-9]{16}$/.test(o.track_code||'')?new URL('../p/'+o.track_code,location.href).href:(o&&/^[a-f0-9]{32,64}$/.test(o.track_token||'')?new URL('../pedido.html#'+o.track_token,location.href).href:'');
function msgStatus(o,st){const n=primeiroNome(o.customer_name),loja=settings.store_name||'',l=linkRastreio(o),txt=({confirmado:`Olá, ${n}! Seu pedido ${o.code} foi confirmado aqui na ${loja}. Já vamos começar a preparar.`,em_preparo:`${n}, seu pedido ${o.code} está sendo preparado agora!`,pronto:o.delivery_type==='entrega'?`${n}, seu pedido ${o.code} saiu para entrega!`:`${n}, seu pedido ${o.code} está pronto para retirar!`,entregue:`Obrigado pelo pedido, ${n}! Bom apetite. Se puder, conta pra gente o que achou.`,cancelado:`${n}, tivemos um problema com o pedido ${o.code}. Pode falar com a gente por aqui?`}[st])||`Olá, ${n}! Sobre o seu pedido ${o.code}: `;
  return l&&st!=='entregue'&&st!=='cancelado'?txt+'\n\nAcompanhe aqui: '+l:txt}
function cardPedido(o){const px=PROXIMO[o.status],min=(Date.now()-new Date(o.created_at))/60000,z=zapUrl(o.customer_phone,msgStatus(o,o.status));
  return `<div class="ped s-${esc(o.status)}${chegou.has(String(o.id))?' chegou':''}" data-pedido="${esc(o.id)}" tabindex="0" role="button" aria-label="Pedido ${esc(o.code)}"><div class="ped-top"><b>${esc(o.code)}</b><span class="tempo${o.status==='novo'&&min>10?' demora':''}">${esc(tempo(o))}</span></div>${esteira(o)}<span class="cli">${esc(o.customer_name||'Cliente')}</span><span class="itens">${esc(resumoItens(o))}</span><div class="ped-pe"><span class="tot">${brl(o.total)}</span><span class="chip ${o.delivery_type==='entrega'?'info':''}">${o.delivery_type==='entrega'?'Entrega':'Retirada'}</span><span class="chip ${o.payment_status==='pago'?'ok':'warn'}">${o.payment_status==='pago'?'Pago':esc(o.payment_method||'A pagar')}</span></div><div class="acts">${px?`<button class="btn small primary" type="button" data-avanca="${esc(o.id)}">${esc(proxRot(o,px))}</button>`:''}${z?`<a class="ic-zap" href="${esc(z)}" target="_blank" rel="noopener noreferrer" aria-label="Avisar ${esc(o.customer_name)} no WhatsApp">${ZAP}</a>`:''}<button class="btn small" type="button" data-imprime="${esc(o.id)}">Imprimir</button></div></div>`}
const ZAP='<svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm4.6 13.9c-.2.6-1.2 1.1-1.7 1.2-.4.1-1 .1-1.6-.1-.4-.1-.8-.3-1.4-.5-2.5-1.1-4.1-3.6-4.2-3.7-.1-.2-1-1.3-1-2.5s.6-1.8.9-2.1c.2-.2.5-.3.6-.3h.5c.1 0 .3 0 .5.4l.7 1.7c.1.1.1.3 0 .4l-.2.4-.4.4c-.1.1-.2.3-.1.5.1.2.6 1 1.3 1.6.9.8 1.7 1.1 1.9 1.2.2.1.4.1.5-.1l.7-.9c.2-.2.3-.2.5-.1l1.6.8c.2.1.4.2.4.3.1.1.1.6-.1 1.2z"/></svg>';

/* ===== jeitos de ver os pedidos ===== */
let vistaPed=lsGet('lj-vista','quadro');if(!['quadro','lista','grade'].includes(vistaPed))vistaPed='quadro';
const ORDEM_ST=['novo','confirmado','em_preparo','pronto','entregue'];
function proxRot(o,px){const e=o.delivery_type==='entrega';return ({novo:'Confirmar pedido',confirmado:'Iniciar preparo',em_preparo:e?'Saiu para entrega':'Pronto p/ retirar',pronto:e?'Marcar entregue':'Marcar retirado'})[o.status]||px[1]}
function esteira(o){const i=ORDEM_ST.indexOf(o.status);if(i<0)return '';const e=o.delivery_type==='entrega',nomes=['Recebido','Confirmado','Preparo',e?'A caminho':'Pronto','Entregue'];
  return `<ol class="esteira" aria-label="Etapa do pedido">${nomes.map((n,k)=>`<li class="${k<i?'ok':k===i?'at':''}"><i></i><span>${n}</span></li>`).join('')}</ol>`}
function htmlVista(lista){
  const abertos=lista.filter(o=>['novo','confirmado','em_preparo','pronto'].includes(o.status)).sort((a,b)=>new Date(a.created_at)-new Date(b.created_at));
  if(vistaPed==='lista')return abertos.length?`<div class="pl">${abertos.map(o=>{const px=PROXIMO[o.status];return `<div class="pl-row s-${esc(o.status)}" data-pedido="${esc(o.id)}" tabindex="0" role="button"><b>${esc(o.code)}</b><div class="pl-meio"><span class="cli">${esc(o.customer_name||'Cliente')}</span><span class="itens">${esc(resumoItens(o))}</span></div>${esteira(o)}<span class="tempo">${esc(tempo(o))}</span><b class="tot">${brl(o.total)}</b>${px?`<button class="btn small primary" type="button" data-avanca="${esc(o.id)}">${esc(proxRot(o,px))}</button>`:''}</div>`}).join('')}</div>`:'<div class="empty">Nenhum pedido em andamento.</div>';
  if(vistaPed==='grade')return abertos.length?`<div class="pgrid">${abertos.map(cardPedido).join('')}</div>`:'<div class="empty">Nenhum pedido em andamento.</div>';
  return STATUS.slice(0,4).map(([st,n])=>{const it=lista.filter(o=>o.status===st).sort((a,b)=>new Date(a.created_at)-new Date(b.created_at));
    return `<div class="kcol s-${st}"><header><b>${esc(n)}</b><span class="chip">${it.length}</span></header>${it.map(cardPedido).join('')||'<div class="empty">Nenhum</div>'}</div>`}).join('');
}
document.addEventListener('click',e=>{const b=e.target.closest('[data-vista]');if(!b)return;vistaPed=b.dataset.vista;lsSet('lj-vista',vistaPed);desenhaPedidos()});
function filtraPedido(o){const q=($('#buscaPedido').value||'').trim().toLowerCase(),qd=digitos(q);return !q||String(o.code).toLowerCase().includes(q)||String(o.customer_name).toLowerCase().includes(q)||(qd.length>=3&&digitos(o.customer_phone).includes(qd))}
function desenhaPedidos(){
  const lista=orders.filter(filtraPedido);
  $('#kanban').className='kanban v-'+vistaPed;$('#kanban').innerHTML=htmlVista(lista);
  document.querySelectorAll('[data-vista]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.vista===vistaPed));
  const t=hoje(),fech=lista.filter(o=>['entregue','cancelado'].includes(o.status)&&diaLocal(o.created_at)===t);
  $('#fechadosBox').hidden=!$('#mostrarFechados').checked;
  $('#listaFechados').innerHTML=fech.map(o=>`<div class="item s-${esc(o.status)}" data-pedido="${esc(o.id)}" role="button" tabindex="0"><div class="who"><b>${esc(o.code)} · ${esc(o.customer_name)}</b><span class="muted">${esc(resumoItens(o))}</span></div><div class="acts"><span class="chip st">${esc(stNome(o.status))}</span><b>${brl(o.total)}</b></div></div>`).join('')||'<div class="empty">Nada por aqui hoje.</div>'}
$('#buscaPedido').addEventListener('input',desenhaPedidos);$('#mostrarFechados').addEventListener('change',desenhaPedidos);
async function mudaStatus(id,st){const o=OD(id);if(!o||o.status===st)return;
  if(st==='cancelado'&&!confirm('Cancelar o pedido '+o.code+'? Ele sai do valor vendido.'))return;
  await tenta(()=>grava('orders',{status:st},o.id),o.code+': '+stNome(st));if(!$('#fichaPedido').hidden)abrePedido(o.id)}
document.addEventListener('click',async e=>{const b=e.target.closest('[data-rastreio]');if(!b)return;e.stopPropagation();const l=linkRastreio(OD(b.dataset.rastreio));if(!l)return;
  try{await navigator.clipboard.writeText(l);toast('Link de rastreio copiado')}catch(_){prompt('Copie o link de rastreio:',l)}},true);
document.addEventListener('click',e=>{const b=e.target.closest('[data-avanca],[data-imprime],[data-pedido],[data-st],[data-pg-status],[data-pg-forma]');if(!b||e.target.closest('a'))return;
  if(b.dataset.avanca){e.stopPropagation();const o=OD(b.dataset.avanca);if(o&&PROXIMO[o.status])mudaStatus(o.id,PROXIMO[o.status][0])}
  else if(b.dataset.imprime){e.stopPropagation();imprime(b.dataset.imprime)}
  else if(b.dataset.st)mudaStatus(b.closest('[data-ped-id]').dataset.pedId,b.dataset.st);
  else if(b.dataset.pgStatus){const id=b.closest('[data-ped-id]').dataset.pedId;tenta(()=>grava('orders',{payment_status:b.dataset.pgStatus},id),'Pagamento: '+b.dataset.pgStatus).then(()=>abrePedido(id))}
  else if(b.dataset.pgForma!==undefined){const id=b.closest('[data-ped-id]').dataset.pedId;tenta(()=>grava('orders',{payment_method:b.dataset.pgForma},id),'Forma de pagamento salva').then(()=>abrePedido(id))}
  else if(b.dataset.pedido)abrePedido(b.dataset.pedido)});
document.addEventListener('keydown',e=>{if((e.key==='Enter'||e.key===' ')&&e.target.matches('[data-pedido]')){e.preventDefault();abrePedido(e.target.dataset.pedido)}});

function abrePedido(id){const o=OD(id);if(!o)return;const f=$('#fichaPedido');f.dataset.pedId=o.id;
  $('#pdTitulo').textContent='Pedido '+o.code;$('#pdSub').textContent=dataBR(o.created_at)+' às '+horaBR(o.created_at)+' · '+tempo(o);
  const z=zapUrl(o.customer_phone,msgStatus(o,o.status));
  $('#pdAcoes').dataset.pedId=o.id;
  $('#pdAcoes').innerHTML=`<div class="linha-status">${STATUS.map(([st,n])=>`<button class="btn small s-${st}" type="button" data-st="${st}" aria-pressed="${o.status===st}">${esc(n.replace(' / saiu',''))}</button>`).join('')}</div>${z?`<a class="btn zap small" href="${esc(z)}" target="_blank" rel="noopener noreferrer">Avisar no WhatsApp</a>`:''}<button class="btn small" type="button" data-imprime="${esc(o.id)}">Imprimir comanda</button>${linkRastreio(o)?`<button class="btn small" type="button" data-rastreio="${esc(o.id)}">Copiar link de rastreio</button>`:''}`;
  $('#pdCorpo').dataset.pedId=o.id;
  $('#pdCorpo').innerHTML=`<div class="pd-bloco"><b>Cliente</b><span>${esc(o.customer_name)} · ${esc(o.customer_phone)}</span><span>${o.delivery_type==='entrega'?'Entrega: '+esc(o.address||'endereço não informado'):'Retirada no balcão'}</span>${o.scheduled_for?`<span>Para: ${esc(o.scheduled_for)}</span>`:''}</div>
  <table class="pd-itens"><tbody>${(o.items||[]).map(i=>`<tr><td>${esc(i.qty)}× ${esc(i.name)}${i.unit?` <span class="muted">(${esc(i.unit)})</span>`:''}${optHtml(i)}</td><td class="n">${brl((+i.price||0)*(+i.qty||0))}</td></tr>`).join('')}<tr><td class="muted">Subtotal</td><td class="n muted">${brl(o.subtotal)}</td></tr>${num(o.delivery_fee)?`<tr><td class="muted">Taxa de entrega</td><td class="n muted">${brl(o.delivery_fee)}</td></tr>`:''}<tr class="tot"><td>Total</td><td class="n">${brl(o.total)}</td></tr></tbody></table>
  <div class="pd-bloco"><b>Pagamento</b><div class="seg">${FORMAS.concat(['']).map(fm=>`<button type="button" data-pg-forma="${esc(fm)}" aria-pressed="${(o.payment_method||'')===fm}">${esc(fm||'Não informado')}</button>`).join('')}</div><div class="seg">${[['pendente','A receber'],['pago','Pago'],['estornado','Estornado']].map(([v,n])=>`<button type="button" data-pg-status="${v}" aria-pressed="${(o.payment_status||'pendente')===v}">${n}</button>`).join('')}</div></div>
  ${o.notes?`<div class="pd-bloco"><b>Observação do cliente</b><span>${esc(o.notes)}</span></div>`:''}
  <label class="lbl-form">Anotações internas<textarea id="pdNotas" maxlength="1000" placeholder="Só a equipe vê">${esc(o.admin_notes||'')}</textarea></label>`;
  $('#pdNotas').addEventListener('change',function(){tenta(()=>grava('orders',{admin_notes:this.value.trim()},o.id),'Anotação salva')});
  abreGaveta(f)}
function imprime(id){const o=OD(id);if(!o)return;
  $('#comanda').innerHTML=`<h3>${esc(settings.store_name||'')}</h3><div class="c">Pedido <b>${esc(o.code)}</b> · ${dataBR(o.created_at)} ${horaBR(o.created_at)}</div><hr><div>${esc(o.customer_name)} · ${esc(o.customer_phone)}</div><div>${o.delivery_type==='entrega'?'ENTREGA: '+esc(o.address):'RETIRADA NO BALCÃO'}</div>${o.scheduled_for?`<div>Para: ${esc(o.scheduled_for)}</div>`:''}<hr><table>${(o.items||[]).map(i=>`<tr><td>${esc(i.qty)}x ${esc(i.name)}${esc(optTxt(i))}</td><td class="n">${brl((+i.price||0)*(+i.qty||0))}</td></tr>`).join('')}</table><hr><table><tr><td>Subtotal</td><td class="n">${brl(o.subtotal)}</td></tr>${num(o.delivery_fee)?`<tr><td>Entrega</td><td class="n">${brl(o.delivery_fee)}</td></tr>`:''}<tr><td><b>TOTAL</b></td><td class="n"><b>${brl(o.total)}</b></td></tr></table><div>Pagamento: ${esc(o.payment_method||'a combinar')} · ${o.payment_status==='pago'?'PAGO':'a receber'}</div>${o.notes?`<hr><div>OBS: ${esc(o.notes)}</div>`:''}`;
  window.print()}

/* ================= financeiro ================= */
function intervalo(){const d=new Date(),t=hoje();
  if(periodo==='hoje')return [t,t];if(periodo==='7'){const i=new Date();i.setDate(i.getDate()-6);return [iso(i),t]}
  if(periodo==='mes')return [t.slice(0,8)+'01',t];
  if(periodo==='mesant'){const i=new Date(d.getFullYear(),d.getMonth()-1,1),f=new Date(d.getFullYear(),d.getMonth(),0);return [iso(i),iso(f)]}
  const a=$('#pIni').value||t,b=$('#pFim').value||t;return a<=b?[a,b]:[b,a]}
function noPeriodo(){const [a,b]=intervalo();return orders.filter(o=>{const d=diaLocal(o.created_at);return d>=a&&d<=b})}
document.querySelectorAll('#periodos button').forEach(b=>b.addEventListener('click',()=>{periodo=b.dataset.p;desenhaFinanceiro()}));
['#pIni','#pFim'].forEach(s=>$(s).addEventListener('change',desenhaFinanceiro));
function desenhaFinanceiro(){
  document.querySelectorAll('#periodos button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.p===periodo));$('#periodoCustom').hidden=periodo!=='custom';
  const L=noPeriodo(),V=validos(L),canc=L.filter(o=>o.status==='cancelado'),soma=a=>a.reduce((s,o)=>s+num(o.total),0);
  const bruto=soma(V),recebido=soma(V.filter(o=>o.payment_status==='pago')),areceber=soma(V.filter(o=>(o.payment_status||'pendente')==='pendente')),estorn=soma(L.filter(o=>o.payment_status==='estornado'));
  $('#kpisFin').className='kpis k3';
  $('#kpisFin').innerHTML=kpi('Pedidos',V.length,canc.length?canc.length+' cancelado(s) fora da conta':'nenhum cancelado')+kpi('Vendido',brl(bruto),'soma dos pedidos não cancelados')+kpi('Recebido',brl(recebido),bruto?Math.round(recebido/bruto*100)+'% do vendido':'')+kpi('A receber',brl(areceber),'pedidos marcados como “a receber”',areceber?'':'')+kpi('Ticket médio',brl(V.length?bruto/V.length:0),'')+kpi('Taxas de entrega',brl(V.reduce((s,o)=>s+num(o.delivery_fee),0)),estorn?'estornos: '+brl(estorn):'');
  const fm={};V.forEach(o=>{const k=o.payment_method||'Não informado';fm[k]=fm[k]||{n:0,v:0,r:0};fm[k].n++;fm[k].v+=num(o.total);if(o.payment_status==='pago')fm[k].r+=num(o.total)});
  $('#tbFormas').innerHTML=Object.entries(fm).sort((a,b)=>b[1].v-a[1].v).map(([k,x])=>`<tr><td>${esc(k)}</td><td>${x.n}</td><td>${brl(x.v)}</td><td>${brl(x.r)}</td></tr>`).join('')||'<tr><td colspan="4"><div class="empty">Sem pedidos no período.</div></td></tr>';
  const [a,b]=intervalo(),dias=[];for(let d=new Date(a+'T12:00:00');iso(d)<=b&&dias.length<62;d.setDate(d.getDate()+1))dias.push(iso(d));
  const ult=dias.slice(-31);barras($('#grafFin'),ult.map(d=>soma(V.filter(o=>diaLocal(o.created_at)===d))),ult.map(d=>ult.length>10?(+d.slice(8,10)%5===0||d===ult[0]?d.slice(8,10):''):d.slice(8,10)+'/'+d.slice(5,7)),brl0,ult.length>10?'dias14':'')}
function csv(nome,linhas){const cel=v=>{let s=String(v??'');if(/^[=+\-@\t\r]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"'};const blob=new Blob(['﻿'+linhas.map(r=>r.map(cel).join(';')).join('\n')],{type:'text/csv;charset=utf-8'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=nome;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),2000)}
const dec=v=>num(v).toFixed(2).replace('.',',');
$('#btnCsvFin').addEventListener('click',()=>{const [a,b]=intervalo();csv('pedidos-'+a+'-a-'+b+'.csv',[['Código','Data','Hora','Cliente','WhatsApp','Tipo','Endereço','Itens','Subtotal','Entrega','Total','Status','Forma de pagamento','Pagamento','Obs. cliente','Anotações']].concat(noPeriodo().map(o=>[o.code,dataBR(o.created_at),horaBR(o.created_at),o.customer_name,o.customer_phone,o.delivery_type,o.address,resumoItens(o),dec(o.subtotal),dec(o.delivery_fee),dec(o.total),stNome(o.status),o.payment_method,o.payment_status,o.notes,o.admin_notes])))});

/* ================= clientes ================= */
function agrupaClientes(){const m={};validos(orders).forEach(o=>{const k=digitos(o.customer_phone)||o.customer_name;if(!k)return;const c=m[k]=m[k]||{nome:o.customer_name,fone:o.customer_phone,n:0,v:0,ult:o.created_at};c.n++;c.v+=num(o.total);if(new Date(o.created_at)>new Date(c.ult)){c.ult=o.created_at;c.nome=o.customer_name}});return Object.values(m).sort((a,b)=>b.v-a.v)}
function desenhaClientes(){const q=($('#buscaCliente').value||'').trim().toLowerCase(),qd=digitos(q);
  const L=agrupaClientes().filter(c=>!q||String(c.nome).toLowerCase().includes(q)||(qd.length>=3&&digitos(c.fone).includes(qd)));
  $('#tbClientes').innerHTML=L.map(c=>{const z=zapUrl(c.fone,`Olá, ${primeiroNome(c.nome)}! Aqui é da ${settings.store_name||''}. `);return `<tr><td><b>${esc(c.nome)}</b><br><span class="muted">${esc(c.fone)}</span></td><td>${c.n}</td><td>${brl(c.v)}</td><td>${brl(c.v/c.n)}</td><td>${dataBR(c.ult)}</td><td><div class="acts-td">${z?`<a class="btn zap small" href="${esc(z)}" target="_blank" rel="noopener noreferrer">WhatsApp</a>`:''}</div></td></tr>`}).join('')||'<tr><td colspan="6"><div class="empty">Os clientes aparecem aqui a partir dos pedidos.</div></td></tr>'}
$('#buscaCliente').addEventListener('input',desenhaClientes);
$('#btnCsvCli').addEventListener('click',()=>csv('clientes-'+hoje()+'.csv',[['Cliente','WhatsApp','Pedidos','Total gasto','Último pedido']].concat(agrupaClientes().map(c=>[c.nome,c.fone,c.n,dec(c.v),dataBR(c.ult)]))));

/* ================= cardápio ================= */
let catEditando=null;
function desenhaCardapio(){
  const lc=$('#listaCats');
  lc.innerHTML=`<button class="cat" type="button" data-cat="" aria-pressed="${catSel===''}"><span class="n">Todos os produtos</span><span class="q">${prods.length}</span></button>`+cats.map((c,i)=>catEditando===c.id?`<form class="cat" data-cat-form="${esc(c.id)}"><input value="${esc(c.name)}" maxlength="60" aria-label="Nome da categoria" required><button class="btn small primary" type="submit">OK</button></form>`
    :`<div class="cat${c.active===false?' inativa':''}" data-cat="${esc(c.id)}" role="button" tabindex="0" aria-pressed="${catSel===c.id}"><span class="n">${esc(c.name)}</span><span class="q">${prods.filter(p=>p.category_id===c.id).length}</span><span class="mini-acts"><button type="button" data-cat-sobe="${esc(c.id)}" aria-label="Subir" ${i===0?'disabled':''}>↑</button><button type="button" data-cat-desce="${esc(c.id)}" aria-label="Descer" ${i===cats.length-1?'disabled':''}>↓</button><button type="button" data-cat-ren="${esc(c.id)}" aria-label="Renomear">✎</button><button type="button" data-cat-del="${esc(c.id)}" aria-label="Excluir">×</button></span></div>`).join('')+(catEditando==='novo'?`<form class="cat" data-cat-form="novo"><input maxlength="60" placeholder="Nome da categoria" aria-label="Nome da nova categoria" required><button class="btn small primary" type="submit">Criar</button></form>`:'');
  const f=lc.querySelector('form input');if(f)f.focus();
  const q=($('#buscaProd').value||'').trim().toLowerCase();
  const L=prods.filter(p=>(!catSel||p.category_id===catSel)&&(!q||String(p.name).toLowerCase().includes(q)||String(p.description).toLowerCase().includes(q))).sort((a,b)=>(cats.findIndex(c=>c.id===a.category_id)-cats.findIndex(c=>c.id===b.category_id))||(a.position-b.position));
  $('#resumoProds').textContent=L.length+' produto(s) · '+L.filter(p=>!p.active).length+' pausado(s)';$('#btnExemplo').hidden=!!prods.length;
  $('#gradeProds').innerHTML=L.map(p=>{const img=imgUrl(p.image_url),irmaos=prods.filter(x=>x.category_id===p.category_id).sort((a,b)=>a.position-b.position),i=irmaos.indexOf(p);
    return `<article class="prod${p.active?'':' off'}"><div class="ft" data-prod="${esc(p.id)}" style="${img?`background-image:url('${esc(img)}')`:''}">${img?'':'<span class="sem-ft"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/></svg>Adicionar foto</span>'}${p.badge?`<span class="selo">${esc(p.badge)}</span>`:''}<button class="estrela" type="button" data-destaque="${esc(p.id)}" aria-pressed="${!!p.featured}" aria-label="Destaque">★</button></div><div class="ct"><b data-prod="${esc(p.id)}">${esc(p.name)}</b><small>${esc(p.description||((p.extra||{}).origem)||C(p.category_id)?.name||'')}</small></div><div class="rod"><span class="preco">${num(p.price)>0?brl(p.price):'Sob consulta'}</span><span class="ord"><button type="button" data-prod-sobe="${esc(p.id)}" aria-label="Mover para cima" ${i<=0?'disabled':''}>↑</button><button type="button" data-prod-desce="${esc(p.id)}" aria-label="Mover para baixo" ${i>=irmaos.length-1?'disabled':''}>↓</button></span><label class="switch" title="${p.active?'Disponível':'Pausado'}"><input type="checkbox" data-ativo="${esc(p.id)}" ${p.active?'checked':''} aria-label="${esc(p.name)} disponível"><span></span></label></div></article>`}).join('')||'<div class="empty">Nenhum produto aqui. Use “+ Produto”.</div>'}
$('#buscaProd').addEventListener('input',desenhaCardapio);
async function troca(tabela,lista,id,dir){const L=lista.slice().sort((a,b)=>a.position-b.position),i=L.findIndex(x=>String(x.id)===String(id)),j=i+dir;if(i<0||j<0||j>=L.length)return;
  L.splice(j,0,L.splice(i,1)[0]);const mud=L.map((x,k)=>[x,k+1]).filter(([x,k])=>x.position!==k);
  await tenta(async()=>{if(demo){mud.forEach(([x,k])=>x.position=k);render();return}for(const [x,k] of mud){const {error}=await db.from(tabela).update({position:k}).eq('id',x.id);if(error)throw error}await carregar(tabela)})}
document.addEventListener('click',e=>{const b=e.target.closest('[data-cat],[data-cat-sobe],[data-cat-desce],[data-cat-ren],[data-cat-del],[data-prod],[data-destaque],[data-prod-sobe],[data-prod-desce]');if(!b||!b.closest('[data-panel="cardapio"]'))return;
  if(b.dataset.catSobe||b.dataset.catDesce){e.stopPropagation();troca('categories',cats,b.dataset.catSobe||b.dataset.catDesce,b.dataset.catSobe?-1:1)}
  else if(b.dataset.catRen){e.stopPropagation();catEditando=b.dataset.catRen;desenhaCardapio()}
  else if(b.dataset.catDel){e.stopPropagation();const c=C(b.dataset.catDel),n=prods.filter(p=>p.category_id===c.id).length;if(n)return toast('Mova ou exclua os '+n+' produtos desta categoria antes');if(confirm('Excluir a categoria "'+c.name+'"?'))tenta(()=>apaga('categories',c.id),'Categoria excluída')}
  else if(b.dataset.destaque){e.stopPropagation();const p=P(b.dataset.destaque);tenta(()=>grava('products',{featured:!p.featured},p.id),p.featured?'Tirado dos destaques':'Agora é destaque')}
  else if(b.dataset.prodSobe||b.dataset.prodDesce){const p=P(b.dataset.prodSobe||b.dataset.prodDesce);troca('products',prods.filter(x=>x.category_id===p.category_id),p.id,b.dataset.prodSobe?-1:1)}
  else if(b.dataset.prod)abreProduto(b.dataset.prod);
  else if(b.dataset.cat!==undefined){catSel=b.dataset.cat;catEditando=null;desenhaCardapio()}});
document.addEventListener('change',e=>{const el=e.target;if(el.dataset.ativo){const p=P(el.dataset.ativo);tenta(()=>grava('products',{active:el.checked},p.id),el.checked?p.name+' voltou ao site':p.name+' pausado')}});
document.addEventListener('submit',e=>{const f=e.target.closest('[data-cat-form]');if(!f)return;e.preventDefault();const nome=f.querySelector('input').value.trim().slice(0,60);if(!nome)return;const id=f.dataset.catForm;catEditando=null;
  if(id==='novo'){let nova=null;tenta(async()=>{nova=await grava('categories',{name:nome,position:cats.length+1,active:true})},'Categoria criada').then(()=>{if(nova)catSel=nova.id;desenhaCardapio()})}
  else tenta(()=>grava('categories',{name:nome},id),'Categoria renomeada')});
$('#btnNovaCat').addEventListener('click',()=>{catEditando='novo';desenhaCardapio()});

/* ---- produto ---- */
let prodAtual=null,fotoNova=null,fotoRemovida=false,opcAtual=[];
function abreProduto(id){const p=id?P(id):{name:'',description:'',price:0,unit:'',category_id:catSel||(cats[0]&&cats[0].id)||null,badge:'',active:true,featured:false,image_url:'',extra:{}};if(!p)return;
  prodAtual=id?p:null;fotoNova=null;fotoRemovida=false;
  $('#prTitulo').textContent=id?p.name:'Novo produto';$('#prExcluir').hidden=!id;$('#prMsg').textContent='';
  $('#prNome').value=p.name||'';$('#prDesc').value=p.description||'';$('#prPreco').value=num(p.price)?num(p.price).toFixed(2).replace('.',','):'';$('#prUnid').value=p.unit||'';$('#prSelo').value=p.badge||'';$('#prAtivo').checked=p.active!==false;$('#prDestaque').checked=!!p.featured;
  $('#prCat').innerHTML='<option value="">Sem categoria</option>'+cats.map(c=>`<option value="${esc(c.id)}">${esc(c.name)}</option>`).join('');$('#prCat').value=p.category_id||'';
  $('#prOrigem').value=(p.extra||{}).origem||'';mostraOrigem();opcAtual=JSON.parse(JSON.stringify(p.opcoes||[]));desenhaOpc();mostraFoto(imgUrl(p.image_url));abreGaveta($('#fichaProduto'));$('#prNome').focus()}
function mostraOrigem(){const c=C($('#prCat').value);$('#prOrigemLbl').hidden=!(c&&(c.extra||{}).tipo==='vinho')&&!$('#prOrigem').value}
$('#prCat').addEventListener('change',mostraOrigem);
function mostraFoto(u){const el=$('#prFotoPrev');el.style.backgroundImage=u?`url('${u.replace(/'/g,'%27')}')`:'';el.classList.toggle('tem',!!u)}
$('#prSemFoto').addEventListener('click',()=>{fotoNova=null;fotoRemovida=true;mostraFoto('')});
$('#prFoto').addEventListener('change',async function(){const f=this.files[0];this.value='';if(!f)return;
  if(!/^image\/(jpeg|png|webp)$/.test(f.type))return toast('Envie JPG, PNG ou WebP');if(f.size>5*1024*1024)return toast('Foto maior que 5 MB');
  try{fotoNova=await reduz(f,900);fotoRemovida=false;mostraFoto(URL.createObjectURL(fotoNova))}catch(e){toast('Não consegui ler essa foto')}});
function reduz(file,max){return new Promise((ok,erro)=>{const img=new Image(),u=URL.createObjectURL(file);img.onload=()=>{const k=Math.min(1,max/Math.max(img.width,img.height)),c=document.createElement('canvas');c.width=Math.round(img.width*k);c.height=Math.round(img.height*k);c.getContext('2d').drawImage(img,0,0,c.width,c.height);URL.revokeObjectURL(u);c.toBlob(b=>b?ok(b):erro(),'image/jpeg',.8)};img.onerror=erro;img.src=u})}
async function sobeFoto(blob){if(demo)return URL.createObjectURL(blob);const nome=lojaId+'/produtos/'+(crypto.randomUUID?crypto.randomUUID():Date.now()+'-'+Math.random().toString(36).slice(2))+'.jpg';
  const {error}=await db.storage.from('lojas').upload(nome,blob,{contentType:'image/jpeg',cacheControl:'31536000',upsert:false});if(error)throw error;return db.storage.from('lojas').getPublicUrl(nome).data.publicUrl}
$('#prForm').addEventListener('submit',async e=>{e.preventDefault();const nome=$('#prNome').value.trim();if(!nome){$('#prMsg').textContent='Informe o nome do produto.';return}
  const op=lerOpc();if(!op)return;
  const b=$('#prSalvar');b.disabled=true;$('#prMsg').textContent='';
  try{const linha={name:nome.slice(0,100),description:$('#prDesc').value.trim().slice(0,400),price:num($('#prPreco').value),unit:$('#prUnid').value.trim().slice(0,40),category_id:$('#prCat').value||null,badge:$('#prSelo').value.trim().slice(0,24),active:$('#prAtivo').checked,featured:$('#prDestaque').checked,opcoes:op,extra:Object.assign({},(prodAtual||{}).extra||{})};
    if($('#prOrigem').value.trim())linha.extra.origem=$('#prOrigem').value.trim().slice(0,60);else delete linha.extra.origem;
    if(fotoNova)linha.image_url=await sobeFoto(fotoNova);else if(fotoRemovida)linha.image_url='';
    if(!prodAtual)linha.position=prods.filter(p=>p.category_id===linha.category_id).length+1;
    await grava('products',linha,prodAtual?prodAtual.id:null);toast(prodAtual?'Produto atualizado':'Produto criado');fechaGavetas()}
  catch(err){console.error(err);$('#prMsg').textContent=erroAmigavel(err)}finally{b.disabled=false}});
$('#prExcluir').addEventListener('click',()=>{if(!prodAtual||!confirm('Excluir "'+prodAtual.name+'" do cardápio? Para tirar do site só por um tempo, use o botão de disponível.'))return;tenta(()=>apaga('products',prodAtual.id),'Produto excluído').then(fechaGavetas)});
$('#btnNovoProduto').addEventListener('click',()=>{if(aba!=='cardapio')abrirAba('cardapio');abreProduto(null)});

/* ---- gavetas ---- */
let focoAntes=null;
function abreGaveta(g){if(g.hidden)focoAntes=document.activeElement;document.querySelectorAll('.ficha').forEach(x=>x.hidden=x!==g);$('#veu').hidden=false;g.hidden=false}
function fechaGavetas(){document.querySelectorAll('.ficha').forEach(x=>x.hidden=true);$('#veu').hidden=true;if(focoAntes&&document.contains(focoAntes))focoAntes.focus()}
document.addEventListener('click',e=>{if(e.target.closest('[data-fechar]')||e.target===$('#veu'))fechaGavetas()});
addEventListener('keydown',e=>{if(e.key==='Escape')fechaGavetas()});

/* ================= loja ================= */
function preencheLoja(){if(document.activeElement&&document.activeElement.closest('#lojaForm'))return;
  $('#sNome').value=settings.store_name||'';$('#sWhats').value=settings.whatsapp||'';$('#sInsta').value=settings.instagram||'';$('#sEnd').value=settings.address||'';$('#sHoras').value=settings.hours||'';$('#sTaxa').value=num(settings.delivery_fee)?num(settings.delivery_fee).toFixed(2).replace('.',','):'';$('#sMin').value=num(settings.min_order)?num(settings.min_order).toFixed(2).replace('.',','):'';$('#sAceita').checked=settings.accept_orders!==false;
  $('#sDesc').value=settings.descricao||'';$('#sEntrega').checked=settings.faz_entrega!==false;$('#sRetirada').checked=settings.faz_retirada!==false;$('#sCor').value=/^#[0-9a-f]{6}$/i.test(settings.cor||'')?settings.cor:'#B0703F';
  document.querySelectorAll('[data-pag]').forEach(c=>c.checked=(settings.pagamentos||['Pix','Cartão','Dinheiro']).includes(c.dataset.pag));mostraFotoLoja();preencheSec()}
$('#lojaForm').addEventListener('submit',e=>{e.preventDefault();const nome=$('#sNome').value.trim();if(!nome)return toast('Informe o nome da loja');
  let w=digitos($('#sWhats').value);if(w.length===10||w.length===11)w='55'+w;if(w&&(w.length<12||w.length>13))return toast('Confira o WhatsApp: DDD + número');
  const pags=[...document.querySelectorAll('[data-pag]')].filter(c=>c.checked).map(c=>c.dataset.pag);if(!pags.length)return toast('Marque pelo menos uma forma de pagamento');
  if(!$('#sEntrega').checked&&!$('#sRetirada').checked)return toast('Marque entrega, retirada ou os dois');
  tenta(()=>grava('settings',{store_name:nome.slice(0,80),descricao:$('#sDesc').value.trim().slice(0,300),faz_entrega:$('#sEntrega').checked,faz_retirada:$('#sRetirada').checked,pagamentos:pags,cor:$('#sCor').value,whatsapp:w,instagram:$('#sInsta').value.trim().slice(0,60),address:$('#sEnd').value.trim().slice(0,160),hours:$('#sHoras').value.trim().slice(0,160),delivery_fee:num($('#sTaxa').value),min_order:num($('#sMin').value),accept_orders:$('#sAceita').checked}),'Dados da loja salvos')});
$('#btnPausa').addEventListener('click',()=>{const nova=settings.accept_orders===false;if(!nova&&!confirm('Pausar os pedidos pelo site agora? O cardápio continua visível.'))return;tenta(()=>grava('settings',{accept_orders:nova}),nova?'Pedidos liberados':'Pedidos pausados')});

/* ================= conta ================= */
$('#senhaForm').addEventListener('submit',async e=>{e.preventDefault();const a=$('#nsSenha').value,b=$('#nsSenha2').value;if(a.length<12)return toast('A senha precisa ter pelo menos 12 caracteres');if(a!==b)return toast('As duas senhas não são iguais');if(demo)return toast('Na demonstração a senha não muda');
  const {error}=await db.auth.updateUser({password:a});if(error)return toast(erroAmigavel(error));e.target.reset();toast('Senha trocada')});
$('#btnSairTudo').addEventListener('click',async()=>{if(!confirm('Encerrar a sessão em todos os aparelhos, inclusive este?'))return;if(db&&!demo){try{await db.auth.signOut({scope:'global'})}catch(e){}}sair('Sessões encerradas em todos os aparelhos.')});

/* ================= demonstração ================= */
async function dadosDemo(){
  try{const r=await fetch('../assets/cardapio-demo.json',{cache:'no-store'});const j=await r.json();cats=j.categories||[];prods=j.products||[];Object.assign(settings,j.settings||{})}catch(e){cats=[{id:'lanches',name:'Lanches',position:1,active:true}];prods=[{id:'x',category_id:'lanches',name:'Produto exemplo',description:'',price:25,active:true,position:1}]}
  if(!RECURSOS.pedidos)return;
  const ativos=prods.filter(p=>p.active&&num(p.price)>0),nomes=['Maria Souza','João Pereira','Ana Lima','Carlos Melo','Beatriz Rocha','Rafael Costa','Juliana Alves','Pedro Santos','Fernanda Dias','Lucas Ramos'],ruas=['Rua XV de Novembro, 120','Av. Vicente Machado, 455','Rua Balduíno Taques, 88','Rua Dr. Colares, 301'];
  let seed=7;const rnd=()=>(seed=(seed*9301+49297)%233280)/233280;let n=1000;
  const novo=(quando,status)=>{const it=[];const k=1+Math.floor(rnd()*3);for(let i=0;i<k;i++){const p=ativos[Math.floor(rnd()*ativos.length)];const ja=it.find(x=>x.product_id===p.id);if(ja)ja.qty++;else it.push({product_id:p.id,name:p.name,unit:p.unit||'',price:num(p.price),qty:1+(rnd()<.25?1:0)})}
    const sub=Math.round(it.reduce((s,i)=>s+i.price*i.qty,0)*100)/100,ent=rnd()<.6,taxa=ent?num(settings.delivery_fee)||7:0,cli=Math.floor(rnd()*nomes.length);
    return {id:'p'+(n),code:'PD'+(n++),created_at:new Date(quando).toISOString(),status,customer_name:nomes[cli],customer_phone:'(42) 9'+(9100+cli*37)+'-'+(1000+cli*211),delivery_type:ent?'entrega':'retirada',address:ent?ruas[cli%ruas.length]:'',notes:rnd()<.2?'Sem cebola, por favor':'',items:it,subtotal:sub,delivery_fee:taxa,total:Math.round((sub+taxa)*100)/100,payment_method:FORMAS[Math.floor(rnd()*3)],payment_status:status==='entregue'&&rnd()<.85?'pago':'pendente',admin_notes:''}};
  orders=[];for(let d=30;d>=1;d--){const q=2+Math.floor(rnd()*7);for(let i=0;i<q;i++){const t=new Date();t.setDate(t.getDate()-d);t.setHours(11+Math.floor(rnd()*11),Math.floor(rnd()*60));orders.push(novo(t,rnd()<.06?'cancelado':'entregue'))}}
  const agora=Date.now();[[95,'entregue'],[70,'pronto'],[40,'em_preparo'],[25,'confirmado'],[12,'novo'],[4,'novo']].forEach(([m,s])=>orders.push(novo(agora-m*60000,s)));
  orders.sort((a,b)=>new Date(b.created_at)-new Date(a.created_at));
  setInterval(()=>{if(!demo||$('#app').hidden)return;orders.unshift(novo(Date.now(),'novo'));verificaNovos();render()},40000)}
$('#btnDemo').addEventListener('click',async()=>{demo=true;papel='dono';lojaSlug='padaria-da-ana';settings=Object.assign(settings,{store_name:'Loja de demonstração',slug:'padaria-da-ana',descricao:'',cor:'#B0703F',faz_entrega:true,faz_retirada:true,pagamentos:['Pix','Cartão','Dinheiro'],logo_url:'',capa_url:''});await dadosDemo();{const nm=new URLSearchParams(location.search).get('nome');if(nm)settings.store_name=nm.slice(0,60)}start()});


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
  if(['dono','gerente'].includes(papel)){desenhaPlano();desenhaPassos()}}
$('#btnCopiaLink').addEventListener('click',()=>copia(linkDaLoja(),'Link copiado'));
async function copia(t,ok){try{await navigator.clipboard.writeText(t);toast(ok)}catch(e){prompt('Copie:',t)}}
/* cardápio de exemplo: cria as categorias que faltam e os produtos com fotos, para a loja já nascer bonita */
async function carregaExemplo(){
  const lista=(window.BC_EXEMPLO||{})[settings.modelo]||(window.BC_EXEMPLO||{}).outro||[];
  if(!lista.length)return toast('Cardápio de exemplo indisponível');
  if(demo)return toast('Na demonstração o exemplo não é criado');
  if(prods.length&&!confirm('A loja já tem produtos. Adicionar o cardápio de exemplo mesmo assim?'))return;
  await tenta(async()=>{
    const nomes=[...new Set(lista.map(i=>i.cat))],norm=t=>String(t||'').trim().toLowerCase(),ids={};
    let pos=cats.reduce((m,c)=>Math.max(m,c.position||0),0);
    const faltam=[];
    nomes.forEach(n=>{const c=cats.find(x=>norm(x.name)===norm(n));if(c)ids[n]=c.id;else faltam.push({loja_id:lojaId,name:n,position:++pos})});
    if(faltam.length){const r=await db.from('categories').insert(faltam).select();if(r.error)throw r.error;r.data.forEach(c=>{ids[c.name]=c.id})}
    let base=prods.reduce((m,p)=>Math.max(m,p.position||0),0);
    const linhas=lista.map((i,k)=>({loja_id:lojaId,category_id:ids[i.cat],name:i.nome,description:i.desc,price:i.preco,unit:i.unid||'',image_url:i.foto||'',active:true,featured:!!i.destaque,badge:i.selo||'',position:base+k+1,extra:i.contem?{ajuste:'contain'}:{},opcoes:i.opcoes||[]}));
    const r2=await db.from('products').insert(linhas);if(r2.error)throw r2.error;
    await Promise.all([carregar('categories'),carregar('products')]);render();
  },'Cardápio de exemplo carregado. Agora é só trocar pelos seus produtos.')}
document.addEventListener('click',e=>{if(e.target.closest('[data-exemplo]'))carregaExemplo()});
let planoEm=0;
/* plano do mês: quanto vendeu, em que faixa está e quanto falta para a próxima */
function planoHtml(f){const v=num(f.vendido),ate=num(f.ate_valor),pct=ate?Math.min(100,v/ate*100):100,mens=num(f.mensalidade);
  const txt=ate?(v<ate?'Faltam '+brl(ate-v)+' em vendas para mudar de faixa.':'Você passou desta faixa. Parabéns pelas vendas!'):'Faixa sem limite: pode vender à vontade.';
  return `<div class="pm-linha"><div><span class="lbl">Vendido no mês</span><b>${esc(brl(v))}</b><small>pedidos não cancelados</small></div>`+
    `<div class="pm-plano"><span class="lbl">Plano ${esc(f.plano_nome||'')}</span><b>${esc(mens?brl(mens):'Convite')}${mens?'<small>/mês</small>':''}</b><small>${esc(ate?'faixa até '+brl0(ate):'sem limite')}</small></div></div>`+
    `<div class="pm-barra" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${Math.round(pct)}"><i style="width:${pct.toFixed(1)}%"></i></div><p class="pm-nota">${esc(txt)}</p>`}
/* primeiros passos: guia para quem acabou de criar a loja */
const PASSOS_LOJA=[
  ['logo','Envie o logo da loja','Aparece no topo do seu cardápio.','loja',()=>!!settings.logo_url],
  ['produtos','Cadastre pelo menos 3 produtos','Com nome, preço e descrição.','cardapio',()=>prods.length>=3],
  ['foto','Coloque fotos nos produtos','Foto boa vende mais: use luz natural.','cardapio',()=>prods.some(p=>!!p.image_url)],
  ['entrega','Defina horário e entrega','Horário, taxa de entrega e pedido mínimo.','loja',()=>!!(settings.hours&&String(settings.hours).trim())],
  ['divulgar','Divulgue o seu link','No Instagram, no status e nos grupos do WhatsApp.','',()=>{try{return localStorage.getItem('bc-divulgou-'+lojaId)==='1'}catch(e){return false}}]];
function desenhaPassos(){const box=$('#primeirosPassos');if(!box||!['dono','gerente'].includes(papel))return;
  let fechado=false;try{fechado=localStorage.getItem('bc-passos-'+lojaId)==='fechado'}catch(e){}
  const feitos=PASSOS_LOJA.map(p=>{try{return !!p[4]()}catch(e){return false}}),n=feitos.filter(Boolean).length;
  box.hidden=fechado||n===PASSOS_LOJA.length;if(box.hidden)return;
  const pct=Math.round(n/PASSOS_LOJA.length*100);$('#ppAnel').style.setProperty('--p',pct);$('#ppPct').textContent=pct+'%';
  $('#ppLista').innerHTML=PASSOS_LOJA.map((p,i)=>`<li class="${feitos[i]?'feito':''}"><span class="pp-n" aria-hidden="true">${feitos[i]?'✓':i+1}</span><div><b>${esc(p[1])}</b><small>${esc(p[2])}</small></div>${feitos[i]?'<span class="pp-ok">Feito</span>':p[3]?`<span class="pp-acoes"><button class="btn small primary" type="button" data-ir="${p[3]}">Fazer agora</button>${p[0]==='produtos'&&!prods.length?'<button class="btn small" type="button" data-exemplo>Usar exemplo com fotos</button>':''}</span>`:'<button class="btn small primary" type="button" data-pp-divulga>Copiar link</button>'}</li>`).join('')}
function marcaDivulgou(){try{localStorage.setItem('bc-divulgou-'+lojaId,'1')}catch(e){}desenhaPassos()}
document.addEventListener('click',e=>{if(e.target.closest('[data-pp-divulga]')){copia(linkDaLoja(),'Link copiado. Agora é só colar no Instagram e no WhatsApp');marcaDivulgou()}
  if(e.target.closest('#btnCopiaLink,#btnZapLink'))marcaDivulgou();
  if(e.target.closest('#ppFecha')){try{localStorage.setItem('bc-passos-'+lojaId,'fechado')}catch(e){}desenhaPassos()}});
async function desenhaPlano(){if(demo){$('#kpisPlano').innerHTML=planoHtml({vendido:2480,plano_nome:'Começo',mensalidade:0,ate_valor:3000});$('#planoFaixa').textContent='demonstração';return}
  if(Date.now()-planoEm<60000)return;planoEm=Date.now();
  const r=await db.rpc('faturamento_loja',{p_loja:lojaId});if(r.error)return;const f=r.data||{};
  $('#kpisPlano').innerHTML=planoHtml(f);
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


/* ================= opcionais do produto ================= */
const novoId=p=>p+Math.random().toString(36).slice(2,8);
function tipoGrupo(g){return +g.max===1?(+g.min>=1?'unica':'unica_opc'):'varias'}
function desenhaOpc(){const box=$('#prOpc');if(!box)return;
  box.innerHTML=opcAtual.map((g,gi)=>`<div class="opc-g" data-gi="${gi}">
    <div class="opc-gl"><input class="opc-gn" data-f="nome" placeholder="Nome do grupo (ex.: Ponto da carne)" maxlength="60" value="${esc(g.nome||'')}">
      <select data-f="tipo"><option value="unica"${tipoGrupo(g)==='unica'?' selected':''}>Escolher 1 (obrigatório)</option><option value="unica_opc"${tipoGrupo(g)==='unica_opc'?' selected':''}>Escolher 1 (opcional)</option><option value="varias"${tipoGrupo(g)==='varias'?' selected':''}>Escolher vários (opcional)</option></select>
      ${tipoGrupo(g)==='varias'?`<label class="opc-ate">até <input type="number" min="2" max="30" data-f="max" value="${+g.max||2}"></label>`:''}
      <button type="button" class="btn small perigo" data-opc-rm-g="${gi}" aria-label="Remover grupo">Remover</button></div>
    ${(g.itens||[]).map((it,ii)=>`<div class="opc-i" data-ii="${ii}"><input data-f="inome" placeholder="Opção (ex.: Bacon)" maxlength="60" value="${esc(it.nome||'')}"><label class="opc-p">+ R$<input data-f="ipreco" inputmode="decimal" maxlength="7" placeholder="0" value="${+it.preco?String(it.preco).replace('.',','):''}"></label><button type="button" class="x" data-opc-rm-i="${gi}:${ii}" aria-label="Remover opção">×</button></div>`).join('')}
    <button type="button" class="btn small" data-opc-add-i="${gi}">+ Opção</button></div>`).join('');
  const add=$('#prOpcAdd');if(add)add.hidden=opcAtual.length>=8}
function sincOpc(){document.querySelectorAll('#prOpc .opc-g').forEach(el=>{const g=opcAtual[+el.dataset.gi];if(!g)return;
  g.nome=el.querySelector('[data-f=nome]').value;const t=el.querySelector('[data-f=tipo]').value;
  if(t==='unica'){g.min=1;g.max=1}else if(t==='unica_opc'){g.min=0;g.max=1}else{g.min=0;const m=el.querySelector('[data-f=max]');g.max=Math.max(2,Math.min(30,+(m&&m.value)||+g.max||2))}
  el.querySelectorAll('.opc-i').forEach(ie=>{const it=g.itens[+ie.dataset.ii];if(!it)return;it.nome=ie.querySelector('[data-f=inome]').value;it.preco=num(ie.querySelector('[data-f=ipreco]').value)})})}
function lerOpc(){sincOpc();const out=[];
  for(const g of opcAtual){const nome=(g.nome||'').trim();const itens=(g.itens||[]).map(i=>({id:i.id,nome:(i.nome||'').trim().slice(0,60),preco:Math.max(0,Math.min(9999,Math.round(num(i.preco)*100)/100))})).filter(i=>i.nome);
    if(!nome&&!itens.length)continue;
    if(!nome){$('#prMsg').textContent='Dê um nome a cada grupo de opções (ex.: Ponto da carne).';return null}
    if(!itens.length){$('#prMsg').textContent='O grupo "'+nome+'" precisa de pelo menos uma opção.';return null}
    const max=Math.min(+g.max||1,itens.length),min=Math.min(+g.min||0,max);out.push({id:g.id,nome:nome.slice(0,60),min,max:Math.max(1,max),itens})}
  return out}
document.addEventListener('click',e=>{const t=e.target;if(!t.closest||!t.closest('#prOpc,#prOpcAdd'))return;
  if(t.id==='prOpcAdd'){sincOpc();if(opcAtual.length<8)opcAtual.push({id:novoId('g'),nome:'',min:1,max:1,itens:[{id:novoId('o'),nome:'',preco:0},{id:novoId('o'),nome:'',preco:0}]});desenhaOpc();return}
  if(t.dataset.opcRmG!=null){sincOpc();opcAtual.splice(+t.dataset.opcRmG,1);desenhaOpc()}
  else if(t.dataset.opcAddI!=null){sincOpc();const g=opcAtual[+t.dataset.opcAddI];if(g&&g.itens.length<30)g.itens.push({id:novoId('o'),nome:'',preco:0});desenhaOpc()}
  else if(t.dataset.opcRmI!=null){sincOpc();const [gi,ii]=t.dataset.opcRmI.split(':').map(Number);const g=opcAtual[gi];if(g){g.itens.splice(ii,1);if(!g.itens.length)opcAtual.splice(gi,1)}desenhaOpc()}});
document.addEventListener('change',e=>{if(e.target.matches&&e.target.matches('#prOpc [data-f=tipo]')){sincOpc();desenhaOpc()}});


/* ================= páginas do site (Sobre, Galeria, Depoimentos) ================= */
let secFotos=[],secSobreFoto='';
const secConf=()=>((settings.extra||{}).secoes)||{};
function depLinha(d){const el=document.createElement('div');el.className='sec-dep';
  el.innerHTML=`<input data-d="nome" maxlength="60" placeholder="Nome (ex.: Ana, cliente)" value="${esc((d&&d.nome)||'')}"><textarea data-d="texto" maxlength="240" rows="2" placeholder="O que o cliente disse">${esc((d&&d.texto)||'')}</textarea><button type="button" class="x" data-sec-dep-rm aria-label="Remover depoimento">×</button>`;return el}
function desenhaSecGaleria(){const b=$('#secGaleria');if(!b)return;
  b.innerHTML=secFotos.map((u,i)=>`<div class="sec-foto" style="background-image:url('${esc(imgUrl(u)).replace(/'/g,'%27')}')"><button type="button" data-sec-foto-rm="${i}" aria-label="Tirar foto">×</button></div>`).join('');
  const add=$('#secGaleriaAdd');if(add)add.closest('label').hidden=secFotos.length>=8}
function mostraSecSobreFoto(){const el=$('#secSobreFotoPrev');if(!el)return;const v=imgUrl(secSobreFoto);el.style.backgroundImage=v?`url('${v.replace(/'/g,'%27')}')`:'';el.classList.toggle('tem',!!v)}
function preencheSec(){if(!$('#secForm')||(document.activeElement&&document.activeElement.closest('#secForm')))return;
  const c=secConf(),so=c.sobre||{};$('#secSobreTit').value=so.titulo||'';$('#secSobreTxt').value=so.texto||'';secSobreFoto=so.foto||'';
  secFotos=((c.galeria||{}).fotos||[]).slice(0,8);
  const d=$('#secDeps');d.textContent='';((c.depoimentos||{}).itens||[]).slice(0,6).forEach(x=>d.appendChild(depLinha(x)));
  $('#secDepAdd').hidden=d.children.length>=6;mostraSecSobreFoto();desenhaSecGaleria()}
function lerSec(){const deps=[...document.querySelectorAll('#secDeps .sec-dep')].map(el=>({nome:el.querySelector('[data-d=nome]').value.trim().slice(0,60),texto:el.querySelector('[data-d=texto]').value.trim().slice(0,240)})).filter(x=>x.texto);
  return {sobre:{titulo:$('#secSobreTit').value.trim().slice(0,60),texto:$('#secSobreTxt').value.trim().slice(0,700),foto:secSobreFoto},galeria:{fotos:secFotos.slice(0,8)},depoimentos:{itens:deps}}}
function salvaSec(msg){return tenta(()=>grava('settings',{extra:Object.assign({},settings.extra||{},{secoes:lerSec()})}),msg||'Páginas salvas')}
async function sobeFotoSec(file,max){if(!/^image\/(jpeg|png|webp)$/.test(file.type)){toast('Envie JPG, PNG ou WebP');return null}if(file.size>5*1024*1024){toast('Foto maior que 5 MB');return null}
  try{const b=await reduz(file,max);if(demo)return URL.createObjectURL(b);const nome=lojaId+'/loja/pagina-'+Date.now()+'.jpg';const up=await db.storage.from('lojas').upload(nome,b,{contentType:'image/jpeg',cacheControl:'31536000'});if(up.error)throw up.error;return db.storage.from('lojas').getPublicUrl(nome).data.publicUrl}
  catch(e){console.error(e);toast('Não consegui enviar essa foto');return null}}
$('#secForm').addEventListener('submit',e=>{e.preventDefault();salvaSec()});
$('#secSobreFoto').addEventListener('change',async function(){const f=this.files[0];this.value='';if(!f)return;const u=await sobeFotoSec(f,1400);if(u){secSobreFoto=u;mostraSecSobreFoto();salvaSec('Foto salva')}});
$('#secSobreTira').addEventListener('click',()=>{secSobreFoto='';mostraSecSobreFoto();salvaSec('Foto retirada')});
$('#secGaleriaAdd').addEventListener('change',async function(){const f=this.files[0];this.value='';if(!f||secFotos.length>=8)return;const u=await sobeFotoSec(f,1200);if(u){secFotos.push(u);desenhaSecGaleria();salvaSec('Foto adicionada')}});
$('#secDepAdd').addEventListener('click',()=>{const d=$('#secDeps');if(d.children.length<6)d.appendChild(depLinha());$('#secDepAdd').hidden=d.children.length>=6;const t=d.lastElementChild&&d.lastElementChild.querySelector('input');if(t)t.focus()});
document.addEventListener('click',e=>{const t=e.target;if(!t.closest)return;
  if(t.dataset.secFotoRm!=null){secFotos.splice(+t.dataset.secFotoRm,1);desenhaSecGaleria();salvaSec('Foto retirada')}
  else if(t.dataset.secDepRm!=null){t.closest('.sec-dep').remove();$('#secDepAdd').hidden=false}});

/* ================= início ================= */
let started=false;
async function start(){if(started)return;started=true;
  $('#auth').hidden=true;$('#app').hidden=false;$('#faixaDemo').hidden=!demo;aplicaPapel();$('#btnTrocaLoja').hidden=minhas.length<2;$('#faixaDemo').textContent=RECURSOS.pedidos?$('#faixaDemo').textContent:'Demonstração com dados fictícios: nada aqui é salvo.';
  somLigado=lsGet('lj-som',true);$('#btnSom').setAttribute('aria-pressed',somLigado);$('#btnSom').textContent=somLigado?'🔔 Som ligado':'🔕 Som desligado';
  if('Notification' in window&&Notification.permission==='granted')$('#btnNotif').hidden=true;
  if(!demo){const u=await db.auth.getUser();$('#contaEmail').textContent='Conectado como '+((u.data&&u.data.user&&u.data.user.email)||'');
    await carregar();
    const fl='loja_id=eq.'+lojaId;canal=db.channel('loja-'+lojaId).on('postgres_changes',{event:'*',schema:'public',table:'orders',filter:fl},()=>carregar('orders')).on('postgres_changes',{event:'*',schema:'public',table:'products',filter:fl},()=>carregar('products')).on('postgres_changes',{event:'*',schema:'public',table:'categories',filter:fl},()=>carregar('categories')).on('postgres_changes',{event:'*',schema:'public',table:'lojas',filter:'id=eq.'+lojaId},()=>carregar('settings'))
      .subscribe(st=>$('#aoVivo').classList.toggle('on',st==='SUBSCRIBED'));
    setInterval(()=>{if(!document.hidden)carregar('orders')},60000)}
  else{orders.forEach(o=>vistos.add(String(o.id)));primeiraCarga=false;$('#aoVivo').classList.add('on');$('#contaEmail').textContent='Demonstração'}
  if(!demo)db.rpc('eh_admin_plataforma').then(r=>{if(r.data===true)$('#btnPlataforma').hidden=false});
  abrirAba('inicio')}
(async()=>{
  let msg='';try{msg=sessionStorage.getItem('lj-msg')||'';sessionStorage.removeItem('lj-msg')}catch(e){}
  const url=String(CFG.supabaseUrl||''),chave=String(CFG.supabaseKey||'');
  if(!window.supabase||!/^https:\/\/[a-z0-9-]+\.supabase\.co\/?$/.test(url)||!chave){mostraForm('semConfig');return}
  db=window.supabase.createClient(url.replace(/\/$/,''),chave,{auth:{storage:window.sessionStorage,persistSession:true,autoRefreshToken:true,detectSessionInUrl:false}});
  db.auth.onAuthStateChange(ev=>{if(ev==='SIGNED_OUT'&&!$('#app').hidden&&!saindo)sair('Sua sessão terminou. Entre de novo.')});
  const {data}=await db.auth.getSession();
  if(data&&data.session){try{await segundaEtapa();return}catch(e){}}
  mostraForm('fLogin');if(msg)msgAuth(msg,/encerradas/.test(msg));
})();

/* ===== modo vitrine (página de vendas): ?demo=1&embed=1&aba=pedidos&nome=Padaria da Ana ===== */
(function(){const q=new URLSearchParams(location.search);if(!q.has('demo'))return;
  if(q.has('embed'))document.documentElement.classList.add('embed');
  setTimeout(()=>{$('#btnDemo').click();const a=q.get('aba');if(a)setTimeout(()=>abrirAba(a),500)},400);
  window.addEventListener('message',e=>{if(e.origin!==location.origin||!e.data)return;const d=e.data;
    if(d.bcVista&&['quadro','lista','grade'].includes(d.bcVista)){vistaPed=d.bcVista;if(aba==='pedidos')desenhaPedidos()}
    if(d.bcAba&&started)abrirAba(d.bcAba)})})();
})();
