/* Painel Bistrô Connect (Acesso restrito).
   Evolução do painel Bistrô Connection original (historico/painel-original.html): mesmas tabelas
   (leads, orcamentos, config), mesmos campos e regras, com login em 2 etapas, sessão só na aba,
   saída por inatividade, busca rápida, histórico dos leads e scripts que abrem o WhatsApp. */
(function () {
'use strict';

/* ================= regras do negócio (do painel original) ================= */
const STAGES=[['lead','Lead'],['contatado','Contatado'],['respondeu','Respondeu'],['demo','Demonstração'],['proposta','Proposta'],['fechado','Fechado · em entrega'],['ativo','Cliente ativo'],['perdido','Perdido']];
const FUNIL=['lead','contatado','respondeu','demo','proposta'];
const PLANOS={
  Essencial:{impl:997,mens:149,prazo:'5 dias úteis',itens:[['Cardápio digital com fotos, categorias e preços',1,697],['Pedido enviado pronto ao WhatsApp',1,0],['QR Code para mesas e balcão + link para a bio',1,150],['Arte de lançamento para o Instagram',1,150]],incl:['Hospedagem e certificado de segurança','Até 10 alterações de cardápio por mês','Suporte pelo WhatsApp em até 4h úteis','Treinamento de 30 minutos']},
  Profissional:{impl:1497,mens:199,prazo:'7 dias úteis',itens:[['Cardápio digital com fotos, categorias e preços',1,697],['Pedido enviado pronto ao WhatsApp',1,0],['Painel de pedidos e edição do cardápio pelo dono',1,400],['Horário de funcionamento e taxa de entrega por bairro',1,100],['QR Code para mesas e balcão + link para a bio',1,150],['Arte de lançamento para o Instagram',1,150]],incl:['Hospedagem e certificado de segurança','Até 10 alterações de cardápio por mês','Suporte pelo WhatsApp em até 4h úteis','Relatório mensal de pedidos','Treinamento de 30 minutos','Banners de datas comemorativas']},
  Premium:{impl:2497,mens:299,prazo:'10 dias úteis',itens:[['Cardápio digital com fotos, categorias e preços',1,697],['Pedido enviado pronto ao WhatsApp',1,0],['Painel de pedidos e edição do cardápio pelo dono',1,400],['Horário de funcionamento e taxa de entrega por bairro',1,100],['Domínio próprio configurado',1,300],['Google Meu Negócio otimizado',1,400],['Cupons de desconto e programa de fidelidade',1,300],['QR Code para mesas e balcão + arte de lançamento',1,300]],incl:['Hospedagem, domínio e certificado','Alterações de cardápio ilimitadas','Suporte prioritário pelo WhatsApp','Relatório mensal de pedidos','Treinamento de 30 minutos','Banners de datas comemorativas']}
};
const PASSOS=[['kickoff','Kickoff: materiais recebidos (logo, cardápio, fotos, horários, bairros)'],['montagem','Montagem: template, identidade, produtos'],['revisao','Revisão: link de teste enviado e ajustes feitos'],['publicacao','Publicação: no ar, QR Codes e arte do Instagram'],['treinamento','Treinamento de 30 min com o dono'],['acompanhamento','Dia 15: pedidos conferidos e depoimento pedido']];
const ROTINA=['10 mensagens de prospecção enviadas','Retornos do dia respondidos','1 demonstração personalizada montada','Orçamentos pendentes cobrados','Entregas em andamento avançadas','Painel atualizado'];
const SCRIPTS=[
 ['Primeira mensagem','Oi, [nome]! Sou o [eu], do [marca], aqui de Ponta Grossa. Vi as avaliações da [estabelecimento] no Google, parabéns! Montei uma amostra de como ficaria o cardápio de vocês com pedido direto no WhatsApp, sem comissão de app: [link]. Posso passar aí 10 minutinhos essa semana para mostrar?'],
 ['Retorno (sem resposta em 2 dias)','Oi, [nome]! Conseguiu ver a amostra do cardápio da [estabelecimento]? Ela já está com alguns produtos de vocês. Se preferir, passo aí rapidinho e te mostro no celular.'],
 ['Envio do orçamento','[nome], como combinamos, segue o orçamento do cardápio digital da [estabelecimento]. Fechando até [data], o cardápio fica no ar em 5 dias úteis. Qualquer dúvida, me chama aqui!'],
 ['Cobrança do orçamento','Oi, [nome]! Conseguiu dar uma olhada no orçamento? A validade vai até [data]. Se quiser, ajusto algum item para caber melhor no seu momento.'],
 ['Pedido de materiais (kickoff)','Bem-vindo ao [marca]! Para começar, me manda por aqui: 1) logo, 2) cardápio atual com preços, 3) fotos dos produtos, 4) horário de funcionamento, 5) bairros e taxas de entrega, 6) o número de WhatsApp que vai receber os pedidos.'],
 ['Pedido de indicação','[nome], que bom que o cardápio está trazendo pedidos! Você conhece outro dono de café, padaria ou restaurante que ia gostar? Se ele fechar, seu próximo mês de mensalidade fica por nossa conta.'],
 ['Cobrança gentil da mensalidade','Oi, [nome]! Passando para lembrar da mensalidade do [marca] com vencimento dia [dia]. Segue a chave Pix: [chave]. Qualquer coisa me chama!']];
const SCRIPT_DA_ETAPA={lead:0,contatado:1,respondeu:1,demo:1,proposta:3,fechado:4,ativo:5};
const FUNIL_META=[['contato','Contatos feitos',200],['respondeu','Responderam',60],['demo','Demonstrações',25],['proposta','Propostas',12],['fechado','Fechados',5]];
const INATIVO_MS=30*60*1000;

let db=null, demo=false, leads=[], orcs=[], editId=null, delArm=false, qEdit=null, qItems=[], modo='quadro', abaAtual='hoje';
let cfg={marca:'Bistrô Connect',nome:'Adilson',whats:'(42) 99900-6578',email:'',cidade:'Ponta Grossa · PR',site:'',pix:'',doc:'',metas:{clientes:15,mrr:3000,contatos:10,fechados:5}};

/* ================= utilidades ================= */
const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const iso=d=>{d=new Date(d);d.setMinutes(d.getMinutes()-d.getTimezoneOffset());return d.toISOString().slice(0,10)};
const hoje=()=>iso(new Date());
const addDias=n=>{const d=new Date();d.setDate(d.getDate()+n);return iso(d)};
const fmtData=s=>s?String(s).slice(8,10)+'/'+String(s).slice(5,7):'—';
const fmtDataLonga=s=>s?String(s).slice(8,10)+'/'+String(s).slice(5,7)+'/'+String(s).slice(0,4):'—';
const brl=n=>'R$ '+Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
const brl0=n=>'R$ '+Number(n||0).toLocaleString('pt-BR',{maximumFractionDigits:0});
const num=v=>{v=String(v??'').replace(/[^\d,.-]/g,'');if(v.includes(','))v=v.replace(/\./g,'').replace(',','.');const n=parseFloat(v);return isFinite(n)?Math.round(n*100)/100:0};
const stageName=k=>(STAGES.find(s=>s[0]===k)||[k,k||'Lead'])[1];
const mesmo=(a,b)=>String(a)===String(b);
const L=id=>leads.find(x=>mesmo(x.id,id));
const O=id=>orcs.find(x=>mesmo(x.id,id));
const digitos=t=>String(t||'').replace(/\D/g,'');
function zapUrl(fone,txt){let d=digitos(fone);if(d.length>=10&&d.length<=11)d='55'+d;if(d.length<12||d.length>13)return '';return 'https://wa.me/'+d+(txt?'?text='+encodeURIComponent(txt):'')}
const ZAP='<svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm4.6 13.9c-.2.6-1.2 1.1-1.7 1.2-.4.1-1 .1-1.6-.1-.4-.1-.8-.3-1.4-.5-2.5-1.1-4.1-3.6-4.2-3.7-.1-.2-1-1.3-1-2.5s.6-1.8.9-2.1c.2-.2.5-.3.6-.3h.5c.1 0 .3 0 .5.4l.7 1.7c.1.1.1.3 0 .4l-.2.4-.4.4c-.1.1-.2.3-.1.5.1.2.6 1 1.3 1.6.9.8 1.7 1.1 1.9 1.2.2.1.4.1.5-.1l.7-.9c.2-.2.3-.2.5-.1l1.6.8c.2.1.4.2.4.3.1.1.1.6-.1 1.2z"/></svg>';
function toast(t){const el=$('#toast');el.textContent=t;el.hidden=false;clearTimeout(toast.t);toast.t=setTimeout(()=>el.hidden=true,2600)}
function notice(t){const n=$('#notice');n.textContent=t||'';n.hidden=!t}
function primeiroNome(s){return String(s||'').trim().split(/\s+/)[0]||''}
function lsGet(k,def){try{const v=localStorage.getItem(k);return v==null?def:JSON.parse(v)}catch(e){return def}}
function lsSet(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}
function erroAmigavel(e){const m=(e&&(e.message||e.error_description))||'';
  if(/Invalid login credentials/i.test(m))return 'E-mail ou senha incorretos.';
  if(/Invalid TOTP|invalid code|expired|mfa_verification/i.test(m))return 'Código inválido ou vencido. Confira o app e tente de novo.';
  if(/rate limit|too many/i.test(m))return 'Muitas tentativas. Espere alguns minutos.';
  if(/permission denied|row-level security|JWT|42501/i.test(m))return 'Sua conta não tem acesso a estes dados (confira a tabela admins e o login em 2 etapas).';
  if(/Failed to fetch|NetworkError|Load failed/i.test(m))return 'Sem conexão com o servidor. Verifique a internet.';
  if(/weak|password should/i.test(m))return 'Senha fraca. Use pelo menos 12 caracteres.';
  return 'Não foi possível concluir. Tente de novo.'}

/* ================= tema ================= */
function aplicaTema(t){if(t==='light'||t==='dark')document.documentElement.dataset.theme=t;else delete document.documentElement.dataset.theme;
  document.querySelectorAll('[data-tema]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.tema===(t||'auto')))}
aplicaTema(lsGet('eb-tema','auto'));
document.querySelectorAll('[data-tema]').forEach(b=>b.addEventListener('click',()=>{lsSet('eb-tema',b.dataset.tema);aplicaTema(b.dataset.tema)}));
$('#btnTema').addEventListener('click',()=>{const escuro=getComputedStyle(document.documentElement).colorScheme.includes('dark');const t=escuro?'light':'dark';lsSet('eb-tema',t);aplicaTema(t)});

/* ================= entrada: senha + 2 etapas ================= */
function mostraForm(id){['fLogin','fCodigo','fCadastro2fa','semConfig'].forEach(f=>$('#'+f).hidden=f!==id);$('#auth').hidden=false;$('#app').hidden=true;const i=$('#'+id).querySelector('input');if(i)i.focus()}
function msgAuth(t,ok){const m=$('#authMsg');m.textContent=t||'';m.className='auth-msg'+(ok?' ok':'')}
let tentativas=0,bloqueadoAte=0,fatorNovo=null;
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
  if(n.data.currentLevel==='aal2')return start();
  const f=await db.auth.mfa.listFactors();if(f.error)throw f.error;
  if(f.data.totp&&f.data.totp.length){$('#cdCodigo').value='';return mostraForm('fCodigo')}
  for(const p of (f.data.all||[]).filter(x=>x.status==='unverified'))await db.auth.mfa.unenroll({factorId:p.id});
  const e=await db.auth.mfa.enroll({factorType:'totp',friendlyName:'Painel Bistrô Connect '+Date.now()});if(e.error)throw e.error;
  fatorNovo=e.data.id;$('#qr2fa').src=e.data.totp.qr_code;$('#seg2fa').textContent=e.data.totp.secret;$('#cdNovo').value='';mostraForm('fCadastro2fa')}
async function verifica(fatorId,codigo,botao){
  if(!/^\d{6}$/.test(codigo))return msgAuth('Digite os 6 números do app.');
  botao.disabled=true;msgAuth('');
  try{const r=await db.auth.mfa.challengeAndVerify({factorId:fatorId,code:codigo});if(r.error)throw r.error;await start()}
  catch(e){msgAuth(erroAmigavel(e))}finally{botao.disabled=false}}
$('#fCodigo').addEventListener('submit',async function(e){e.preventDefault();const f=await db.auth.mfa.listFactors();const fator=f.data&&f.data.totp&&f.data.totp[0];if(!fator)return segundaEtapa();verifica(fator.id,$('#cdCodigo').value.trim(),this.querySelector('button[type=submit]'))});
$('#fCadastro2fa').addEventListener('submit',function(e){e.preventDefault();verifica(fatorNovo,$('#cdNovo').value.trim(),this.querySelector('button[type=submit]'))});
['#cdCodigo','#cdNovo'].forEach(s=>$(s).addEventListener('input',function(){this.value=digitos(this.value).slice(0,6);if(this.value.length===6)this.form.requestSubmit()}));

let saindo=false;
async function sair(motivo){if(saindo)return;saindo=true;
  if(db&&!demo){try{await db.auth.signOut()}catch(e){}}
  try{sessionStorage.setItem('eb-msg',motivo||'')}catch(e){}
  location.reload()}
document.addEventListener('click',e=>{if(e.target.closest('[data-sair]'))sair('')});
let ultimoUso=Date.now();
['pointerdown','keydown','scroll','touchstart'].forEach(t=>addEventListener(t,()=>{ultimoUso=Date.now()},{passive:true}));
setInterval(()=>{if(!$('#app').hidden&&!demo&&Date.now()-ultimoUso>INATIVO_MS)sair('Você saiu por inatividade. Entre de novo.')},30000);

/* ================= dados ================= */
async function reload(col){
  if(demo){render();return}
  const {data,error}=await db.from(col).select('id,doc,created_at').order('created_at',{ascending:true});
  if(error){notice('Erro ao carregar dados: '+erroAmigavel(error));return}
  const arr=(data||[]).map(r=>Object.assign({},r.doc||{},{id:r.id,_criado:r.created_at}));
  if(col==='leads')leads=arr;else orcs=arr;
  render();if(col==='orcamentos'&&!qEdit)drawSheet()}
async function loadCfg(){
  if(!demo){const {data}=await db.from('config').select('doc').eq('id','empresa').maybeSingle();if(data&&data.doc)cfg=Object.assign({},cfg,data.doc,{metas:Object.assign({},cfg.metas,(data.doc||{}).metas)})}
  aplicaMarca();fillCfg();drawSheet();render()}
function limpaDoc(o){const d=Object.assign({},o);delete d.id;delete d._criado;return d}
function comHistorico(col,antes,doc,acao){
  if(col!=='leads')return doc;
  const h=Array.isArray(doc.historico)?doc.historico.slice(-99):[];
  if(acao)h.push(acao);
  else if(!antes)h.push({d:hoje(),t:'criado',v:doc.stage||'lead'});
  if(antes&&doc.stage&&antes.stage!==doc.stage)h.push({d:hoje(),t:'etapa',v:doc.stage});
  doc.historico=h;return doc}
async function salvar(col,id,patch,acao){
  const lista=col==='leads'?leads:orcs,cur=id?lista.find(x=>mesmo(x.id,id)):null;
  const doc=comHistorico(col,cur,Object.assign(limpaDoc(cur||{}),patch),acao);
  try{
    if(demo){if(cur){Object.keys(cur).forEach(k=>{if(k!=='id'&&k!=='_criado')delete cur[k]});Object.assign(cur,doc);render();return cur.id}
      const n=Object.assign({},doc,{id:'d'+Date.now()+Math.random().toString(36).slice(2,6),_criado:new Date().toISOString()});lista.push(n);render();return n.id}
    if(cur){const {error}=await db.from(col).update({doc}).eq('id',cur.id);if(error)throw error;await reload(col);return cur.id}
    const {data,error}=await db.from(col).insert({doc}).select('id').single();if(error)throw error;await reload(col);return data.id
  }catch(e){console.error(e);toast('Não foi possível salvar: '+erroAmigavel(e));return null}}
async function excluir(col,id){
  if(demo){if(col==='leads')leads=leads.filter(x=>!mesmo(x.id,id));else orcs=orcs.filter(x=>!mesmo(x.id,id));render();toast('Excluído');return}
  const {error}=await db.from(col).delete().eq('id',id);if(error){toast('Não foi possível excluir');return}toast('Excluído');reload(col)}
function registrarContato(id){const x=L(id);if(!x)return;salvar('leads',x.id,{ultimoContato:hoje(),proximoContato:addDias(2),stage:x.stage==='lead'?'contatado':x.stage},{d:hoje(),t:'contato'});toast('Contato registrado · retorno em 2 dias')}
function mudarEtapa(id,st){const patch={stage:st};const x=L(id);if(!x||x.stage===st)return;if(st==='fechado'&&!x.fechadoEm)patch.fechadoEm=hoje();if(st==='ativo'){patch.ativoEm=x.ativoEm||hoje();if(!x.pagamento)patch.pagamento='em dia'}
  salvar('leads',id,patch);toast(st==='fechado'?'Fechado! Ele está na aba Entregas':(x.nome||'Lead')+': '+stageName(st))}

/* ================= navegação ================= */
const TITULOS={hoje:'Hoje',leads:'Funil de leads',orcamentos:'Orçamentos',entregas:'Entregas em andamento',clientes:'Clientes e manutenção',resultados:'Plano de negócio e metas',scripts:'Scripts de venda',ajuda:'Ajuda · como tudo funciona',ajustes:'Ajustes'};
function abrirAba(t){if(!TITULOS[t])t='hoje';abaAtual=t;
  document.querySelectorAll('[data-aba]').forEach(b=>{if(b.dataset.aba===t)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current')});
  document.querySelectorAll('section.panel').forEach(p=>p.hidden=p.dataset.panel!==t);
  $('#titulo').textContent=TITULOS[t];subtitulo();lsSet('bt-aba',t);
  if(t==='orcamentos')requestAnimationFrame(fitSheet);scrollTo({top:0})}
document.querySelectorAll('[data-aba]').forEach(b=>b.addEventListener('click',()=>abrirAba(b.dataset.aba)));
document.addEventListener('click',e=>{const b=e.target.closest('[data-ir]');if(b)abrirAba(b.dataset.ir)});
function subtitulo(){const h=new Date().getHours(),s=h<12?'Bom dia':h<18?'Boa tarde':'Boa noite';
  $('#subtitulo').textContent=abaAtual==='hoje'?s+', '+primeiroNome(cfg.nome||'Adilson')+' · '+new Date().toLocaleDateString('pt-BR',{weekday:'long',day:'2-digit',month:'long'}):''}
function aplicaMarca(){document.querySelectorAll('.marca-nome').forEach(e=>e.textContent=cfg.marca||'Bistrô Connect');document.title='Painel · '+(cfg.marca||'Bistrô Connect')}

/* ================= render geral ================= */
function render(){
  const t=hoje(),mes=t.slice(0,7),M=cfg.metas||{};
  const ativos=leads.filter(l=>l.stage==='ativo'),entrega=leads.filter(l=>l.stage==='fechado'),funil=leads.filter(l=>FUNIL.includes(l.stage||'lead'));
  const mrr=ativos.reduce((s,l)=>s+num(l.mensalidade),0);
  const contHoje=leads.filter(l=>l.ultimoContato===t).length;
  const atrasados=funil.filter(l=>l.proximoContato&&l.proximoContato<t);
  const abertos=orcs.filter(o=>o.status==='enviado'||o.status==='rascunho');
  const metaCli=+M.clientes||15,metaMrr=+M.mrr||3000,metaCont=+M.contatos||10;
  $('#kAtivos').textContent=ativos.length;$('#kAtivosBar').style.width=Math.min(100,ativos.length/metaCli*100)+'%';
  $('#kAtivosSub').textContent=ativos.length>=metaCli?'meta de '+metaCli+' atingida':'faltam '+(metaCli-ativos.length)+' para a meta de '+metaCli;
  $('#kMrr').textContent=brl0(mrr);$('#kMrrBar').style.width=Math.min(100,mrr/metaMrr*100)+'%';$('#kMrrSub').textContent=Math.round(mrr/metaMrr*100)+'% da meta de '+brl0(metaMrr);
  $('#kHoje').textContent=contHoje;$('#kHojeBar').style.width=Math.min(100,contHoje/metaCont*100)+'%';$('#kHojeSub').textContent='meta: '+metaCont+' por dia útil';
  $('#kAtraso').textContent=atrasados.length;$('#kpiAtraso').classList.toggle('alert',atrasados.length>0);
  $('#kOrc').textContent=abertos.length;$('#kOrcSub').textContent=brl0(abertos.reduce((s,o)=>s+num(o.totalImpl),0))+' em implantações';
  const setC=(s,v)=>$(s).textContent=v||'';setC('#cLeads',funil.length);setC('#cEntregas',entrega.length);setC('#cClientes',ativos.length);setC('#cOrc',abertos.length);
  subtitulo();
  renderHoje(t,mes,funil,ativos);renderLeads(funil);renderEntregas(entrega);renderClientes(ativos,mrr,mes);renderOrcList();fillLeadSelects();renderResultados(ativos,mrr);renderScripts();
  if(!$('#paleta').hidden)renderPaleta()}

function itemLead(l,linha,chip){const z=zapUrl(l.whatsapp,scriptPara(l));
  return `<div class="item"><div class="who"><b>${esc(l.nome||'Sem nome')}</b><span class="muted">${esc(linha)}</span></div><div class="acts">${chip||''}${z?`<a class="ic-zap" href="${esc(z)}" target="_blank" rel="noopener noreferrer" aria-label="WhatsApp de ${esc(l.nome)}">${ZAP}</a>`:''}<button class="btn small" type="button" data-contato="${esc(l.id)}">Contato feito</button><button class="btn small" type="button" data-edit="${esc(l.id)}">Abrir</button></div></div>`}

function renderHoje(t,mes,funil,ativos){
  const due=funil.filter(l=>l.proximoContato&&l.proximoContato<=t).sort((a,b)=>a.proximoContato.localeCompare(b.proximoContato));
  $('#cRetornos').textContent=due.length;$('#cRetornos').className='chip '+(due.some(l=>l.proximoContato<t)?'bad':due.length?'warn':'ok');
  $('#listaRetornos').innerHTML=due.length?due.map(l=>itemLead(l,stageName(l.stage)+' · '+(l.bairro||'sem bairro')+(l.whatsapp?' · '+l.whatsapp:''),`<span class="chip ${l.proximoContato<t?'bad':'warn'}">${l.proximoContato<t?'atrasado '+fmtData(l.proximoContato):'hoje'}</span>`)).join(''):'<div class="empty">Nenhum retorno pendente. Marque o próximo retorno de cada lead na aba Leads.</div>';
  const al=[];
  ativos.forEach(l=>{if(l.pagamento==='atrasado')al.push([l.nome,'bad','Pagamento atrasado',l.plano||'',l.id]);if((l.relatorio||'').slice(0,7)!==mes)al.push([l.nome,'warn','Relatório do mês pendente',l.plano||'',l.id])});
  orcs.filter(o=>o.status==='enviado').forEach(o=>{const v=o.validoAte||'';al.push([o.est,v<t?'bad':'info',v<t?'Orçamento vencido em '+fmtData(v):'Orçamento aguardando · vence '+fmtData(v),o.numero,null,o.id])});
  $('#listaAlertas').innerHTML=al.length?al.map(([n,c,txt,sub,lid,oid])=>`<div class="item"><div class="who"><b>${esc(n)}</b><span class="muted">${esc(sub)}</span></div><div class="acts"><span class="chip ${c}">${esc(txt)}</span>${lid?`<button class="btn small" type="button" data-edit="${esc(lid)}">Abrir</button>`:`<button class="btn small" type="button" data-oopen="${esc(oid)}">Abrir</button>`}</div></div>`).join(''):'<div class="empty">Sem cobranças, orçamentos ou relatórios pendentes.</div>';
  const rot=lsGet('bt-rotina-'+t,{}),feitos=ROTINA.filter((r,i)=>rot[i]).length,pct=Math.round(feitos/ROTINA.length*100);
  $('#rotina').innerHTML=ROTINA.map((r,i)=>`<label class="check"><input type="checkbox" data-rot="${i}" ${rot[i]?'checked':''}><span>${esc(r)}</span></label>`).join('');
  $('#rotinaPct').textContent=pct+'%';$('#rotinaArco').setAttribute('stroke-dasharray',pct+' 100');
  const etapas=FUNIL.concat(['fechado','ativo']),cont=etapas.map(s=>leads.filter(l=>(l.stage||'lead')===s).length),mx=Math.max(1,...cont);
  $('#funilMini').innerHTML=etapas.map((s,i)=>`<div class="fm"><span>${esc(stageName(s).replace(' · em entrega',''))}</span><i style="width:${cont[i]/mx*100}%"></i><b>${cont[i]}</b></div>`).join('')}

function filtroLeads(l){const q=($('#busca').value||'').trim().toLowerCase(),qd=digitos(q),tp=$('#fTipoFiltro').value,og=$('#fOrigemFiltro').value;
  if(tp&&l.tipo!==tp)return false;if(og&&origemDe(l)!==og)return false;
  return !q||(l.nome||'').toLowerCase().includes(q)||(l.bairro||'').toLowerCase().includes(q)||(l.responsavel||'').toLowerCase().includes(q)||(qd.length>=3&&digitos(l.whatsapp).includes(qd))}
function origemDe(l){return String(l.origem||'manual').split(' / ')[0]||'manual'}
function preencheFiltros(){
  const ft=$('#fTipoFiltro'),fo=$('#fOrigemFiltro'),vt=ft.value,vo=fo.value;
  const tipos=[...new Set(leads.map(l=>l.tipo).filter(Boolean))].sort(),origens=[...new Set(leads.map(origemDe))].sort();
  ft.innerHTML='<option value="">Todos os tipos</option>'+tipos.map(x=>`<option>${esc(x)}</option>`).join('');ft.value=tipos.includes(vt)?vt:'';
  fo.innerHTML='<option value="">Todas as origens</option>'+origens.map(x=>`<option>${esc(x)}</option>`).join('');fo.value=origens.includes(vo)?vo:''}
function cardHTML(l){const t=hoje(),p=l.proximoContato,z=zapUrl(l.whatsapp,scriptPara(l));
  const chip=p?`<span class="chip ${p<t?'bad':p===t?'warn':''}">retorno ${p<t?'atrasado ':''}${fmtData(p)}</span>`:'';
  const og=l.origem&&l.origem!=='manual'?`<span class="chip info">${esc(origemDe(l))}</span>`:'';
  const opts=STAGES.filter(s=>s[0]!=='ativo').map(s=>`<option value="${s[0]}" ${s[0]===(l.stage||'lead')?'selected':''}>${esc(s[1])}</option>`).join('');
  return `<div class="card" draggable="true" data-card="${esc(l.id)}"><span class="t" data-edit="${esc(l.id)}" role="button" tabindex="0">${esc(l.nome||'Sem nome')}</span><span class="meta">${esc(l.tipo||'')}${l.bairro?' · '+esc(l.bairro):''}${l.nota?' · ★ '+esc(l.nota):''}${l.avaliacoes?' ('+esc(l.avaliacoes)+')':''}</span>${chip||og?`<div class="acts">${chip}${og}</div>`:''}<div class="acts">${z?`<a class="ic-zap" href="${esc(z)}" target="_blank" rel="noopener noreferrer" aria-label="WhatsApp">${ZAP}</a>`:''}<button class="btn small" type="button" data-contato="${esc(l.id)}">Contato feito</button><select data-stage="${esc(l.id)}" aria-label="Mudar etapa">${opts}</select><button class="btn small" type="button" data-orc-lead="${esc(l.id)}">Orçamento</button></div></div>`}
function renderLeads(funil){
  preencheFiltros();
  $('#board').innerHTML=FUNIL.map(st=>{const it=funil.filter(l=>(l.stage||'lead')===st&&filtroLeads(l)).sort((a,b)=>(a.proximoContato||'9').localeCompare(b.proximoContato||'9'));
    return `<div class="col" data-col="${st}"><header><b>${esc(stageName(st))}</b><span class="muted">${it.length}</span></header>${it.map(cardHTML).join('')||'<div class="empty">Vazio</div>'}</div>`}).join('');
  const todos=leads.filter(filtroLeads).slice().sort((a,b)=>String(b._criado||b.criadoEm||'').localeCompare(String(a._criado||a.criadoEm||'')));
  $('#tbLeads').innerHTML=todos.length?todos.map(l=>`<tr class="clicavel" data-edit="${esc(l.id)}" tabindex="0"><td><b>${esc(l.nome||'Sem nome')}</b><br><span class="muted">${esc(l.tipo||'')}</span></td><td><span class="chip ${l.stage==='ativo'?'ok':l.stage==='perdido'?'':'info'}">${esc(stageName(l.stage))}</span></td><td>${esc(l.bairro||'—')}</td><td>${l.proximoContato?`<span class="chip ${l.proximoContato<hoje()&&FUNIL.includes(l.stage)?'bad':''}">${fmtData(l.proximoContato)}</span>`:'—'}</td><td>${esc(l.origem||'manual')}</td><td>${fmtDataLonga(l.criadoEm||String(l._criado||'').slice(0,10))}</td></tr>`).join(''):'<tr><td colspan="6"><div class="empty">Nenhum lead com esses filtros.</div></td></tr>';
  $('#board').hidden=modo!=='quadro';$('#listaLeadsWrap').hidden=modo!=='lista';
  const perd=leads.filter(l=>l.stage==='perdido');$('#btnPerdidos').textContent=`Perdidos (${perd.length})`;
  $('#listaPerdidos').innerHTML=perd.map(l=>`<div class="item"><div class="who"><b>${esc(l.nome)}</b><span class="muted">${esc(l.notas||'')}</span></div><div class="acts"><button class="btn small" type="button" data-stage-set="${esc(l.id)}" data-v="lead">Reabrir</button><button class="btn small" type="button" data-edit="${esc(l.id)}">Abrir</button></div></div>`).join('')||'<div class="empty">Nenhum lead perdido.</div>'}

function renderEntregas(entrega){
  $('#entregas').innerHTML=entrega.length?entrega.map(l=>{const ck=l.checklist||{},n=PASSOS.filter(p=>ck[p[0]]).length,pronto=['kickoff','montagem','revisao','publicacao','treinamento'].every(k=>ck[k]);
    return `<div class="box"><div class="box-head"><div class="who"><b>${esc(l.nome)}</b><br><span class="muted fino">${esc(l.plano||'plano a definir')} · fechado em ${fmtData(l.fechadoEm)}</span></div><span class="prog">${n}/${PASSOS.length}</span></div><div class="meta-bar"><i style="width:${n/PASSOS.length*100}%"></i></div>${PASSOS.map(p=>`<label class="check"><input type="checkbox" data-ck="${esc(l.id)}" data-k="${p[0]}" ${ck[p[0]]?'checked':''}><span>${esc(p[1])}</span></label>`).join('')}<div class="acoes-linha"><button class="btn ${pronto?'primary':''} small" type="button" data-ativar="${esc(l.id)}" ${pronto?'':'disabled'}>Marcar como cliente ativo</button><button class="btn small" type="button" data-edit="${esc(l.id)}">Editar</button>${zapUrl(l.whatsapp)?`<a class="btn zap small" href="${esc(zapUrl(l.whatsapp,preencher(SCRIPTS[4][1],l)))}" target="_blank" rel="noopener noreferrer">Pedir materiais</a>`:''}</div></div>`}).join(''):'<div class="empty">Nenhuma entrega em andamento. Quando um orçamento for aceito ou um lead for para “Fechado”, ele aparece aqui.</div>'}

function renderClientes(ativos,mrr,mes){
  const atras=ativos.filter(l=>l.pagamento==='atrasado').length,semRel=ativos.filter(l=>(l.relatorio||'').slice(0,7)!==mes).length;
  $('#kpisClientes').innerHTML=[['Clientes ativos',ativos.length,''],['Receita mensal',brl0(mrr),'soma das mensalidades'],['Receita anual prevista',brl0(mrr*12),''],['Pagamentos atrasados',atras,atras?'cobre pelo botão abaixo':'tudo em dia',atras],['Relatórios do mês',ativos.length-semRel+' / '+ativos.length,semRel?semRel+' pendente(s)':'todos enviados']]
    .map(([l,v,s,a])=>`<div class="kpi${a?' alert':''}"><span class="lbl">${esc(l)}</span><span class="val">${esc(v)}</span><span class="sub">${esc(s)}</span></div>`).join('');
  $('#resumoClientes').textContent=`${ativos.length} ativos · ${brl0(mrr)}/mês`;
  $('#tbClientes').innerHTML=ativos.length?ativos.slice().sort((a,b)=>(+a.vencimento||99)-(+b.vencimento||99)).map(l=>{const z=zapUrl(l.whatsapp,preencher(SCRIPTS[6][1],l));
    return `<tr><td><b>${esc(l.nome)}</b><br><span class="muted">${esc(l.whatsapp||'')}</span></td><td>${esc(l.plano||'—')}</td><td>${brl0(l.mensalidade)}</td><td>${esc(l.vencimento||'—')}</td><td><button class="chip ${l.pagamento==='atrasado'?'bad':'ok'}" type="button" data-pag="${esc(l.id)}">${l.pagamento==='atrasado'?'Atrasado':'Em dia'}</button></td><td>${l.relatorio?fmtDataLonga(l.relatorio):'—'} ${(l.relatorio||'').slice(0,7)===mes?'<span class="chip ok">este mês</span>':''}</td><td><div class="acts-td">${z?`<a class="btn zap small" href="${esc(z)}" target="_blank" rel="noopener noreferrer">Cobrar</a>`:''}<button class="btn small" type="button" data-rel="${esc(l.id)}">Relatório enviado</button><button class="btn small" type="button" data-edit="${esc(l.id)}">Editar</button></div></td></tr>`}).join(''):'<tr><td colspan="7"><div class="empty">Clientes ativos aparecem aqui depois que a entrega é concluída.</div></td></tr>'}

/* ================= resultados ================= */
function renderResultados(ativos,mrr){
  const M=cfg.metas||{},mes=hoje().slice(0,7);
  const fech=leads.filter(l=>(l.fechadoEm||'').slice(0,7)===mes).length;
  const fechTot=leads.filter(l=>l.stage==='fechado'||l.stage==='ativo').length,encerrados=fechTot+leads.filter(l=>l.stage==='perdido').length;
  const ticket=ativos.length?mrr/ativos.length:0;
  $('#planMetrics').innerHTML=[['Clientes ativos',ativos.length+' / '+(+M.clientes||15),'meta de 90 dias'],['Receita recorrente',brl0(mrr),'meta: '+brl0(+M.mrr||3000)+'/mês'],['Fechados este mês',fech+' / '+(+M.fechados||5),'meta mensal do funil'],['Ticket médio',brl0(ticket),encerrados?'conversão '+Math.round(fechTot/encerrados*100)+'% dos negócios encerrados':'sem negócios encerrados']]
    .map(([l,v,s])=>`<div class="metric"><span class="lbl">${esc(l)}</span><span class="v">${esc(v)}</span><span class="muted fino">${esc(s)}</span></div>`).join('');
  const conta=(t,v)=>leads.reduce((s,l)=>s+(l.historico||[]).filter(h=>(h.d||'').slice(0,7)===mes&&h.t===t&&(v==null||h.v===v)).length,0);
  const real={contato:conta('contato'),respondeu:conta('etapa','respondeu'),demo:conta('etapa','demo'),proposta:conta('etapa','proposta'),fechado:fech};
  $('#funilReal').innerHTML=FUNIL_META.map(([k,n,meta])=>{if(k==='fechado')meta=+M.fechados||meta;const v=real[k],p=Math.min(100,v/meta*100);
    return `<div class="fr${v>=meta?' ok':''}"><div class="fr-top"><span>${esc(n)}</span><b>${v} / ${meta}</b></div><div class="fr-trilho"><i style="width:${p}%"></i></div></div>`}).join('');
  const meses=[];for(let i=5;i>=0;i--){const d=new Date();d.setDate(1);d.setMonth(d.getMonth()-i);meses.push(iso(d).slice(0,7))}
  const serie=meses.map(m=>ativos.filter(l=>String(l.ativoEm||l.fechadoEm||l.criadoEm||'0000').slice(0,7)<=m).reduce((s,l)=>s+num(l.mensalidade),0));
  const mx=Math.max(1,...serie);
  $('#graficoMrr').innerHTML=serie.map((v,i)=>{const d=new Date(meses[i]+'-15T12:00:00');return `<div class="gb"><b>${brl0(v)}</b><i style="height:${Math.max(2,v/mx*100)}%"></i><span>${esc(d.toLocaleDateString('pt-BR',{month:'short'}).replace('.',''))}</span></div>`}).join('');
  $('#planoResumo').innerHTML=`O ${esc(cfg.marca||'Bistrô Connect')} vende cardápio digital com pedido direto no WhatsApp para padarias, cafés e restaurantes de Ponta Grossa, cobrando implantação + mensalidade, sem comissão por pedido. Meta: <b>${esc(+M.clientes||15)} clientes ativos</b> e cerca de <b>${esc(brl0(+M.mrr||3000))}/mês recorrentes</b> em 90 dias.`;
  $('#tbPlanos').innerHTML=Object.entries(PLANOS).map(([k,p])=>`<tr><td><b>${k}</b></td><td>${brl0(p.impl)}</td><td>${brl0(p.mens)}/mês</td><td>${p.prazo}</td><td class="muted">${esc(p.itens.map(i=>i[0]).slice(0,4).join(' · '))}</td></tr>`).join('')}

/* ================= scripts ================= */
function preencher(txt,l){l=l||{};const o=l.id?orcs.filter(x=>mesmo(x.leadId,l.id)).sort((a,b)=>String(b.numero).localeCompare(String(a.numero)))[0]:null;
  const r={nome:primeiroNome(l.responsavel)||'[nome]',estabelecimento:l.nome||'[estabelecimento]',data:o?fmtDataLonga(o.validoAte):'[data]',dia:l.vencimento||'[dia]',chave:cfg.pix||'[chave]',marca:cfg.marca||'Bistrô Connect',eu:primeiroNome(cfg.nome)||'Adilson'};
  return txt.replace(/\[(nome|estabelecimento|data|dia|chave|marca|eu)\]/g,(m,k)=>r[k])}
function scriptPara(l){const i=SCRIPT_DA_ETAPA[l.stage||'lead'];return i==null?'':preencher(SCRIPTS[i][1],l)}
function renderScripts(){const sel=$('#scLead'),l=L(sel.value);
  $('#scripts').innerHTML=SCRIPTS.map((s,i)=>{const txt=preencher(s[1],l),z=l?zapUrl(l.whatsapp,txt):'';
    return `<div class="box script"><b>${esc(s[0])}</b><pre id="sc${i}">${esc(txt)}</pre><div class="acoes-linha"><button class="btn small" data-copy="${i}" type="button">Copiar</button>${z?`<a class="btn zap small" href="${esc(z)}" target="_blank" rel="noopener noreferrer">Enviar para ${esc(primeiroNome(l.responsavel)||l.nome)}</a>`:''}</div></div>`}).join('')}
$('#scLead').addEventListener('change',renderScripts);
$('#scripts').addEventListener('click',async e=>{const b=e.target.closest('[data-copy]');if(!b)return;const txt=$('#sc'+b.dataset.copy).textContent;
  try{await navigator.clipboard.writeText(txt);toast('Copiado')}catch(_){const r=document.createRange();r.selectNodeContents($('#sc'+b.dataset.copy));const s=getSelection();s.removeAllRanges();s.addRange(r);toast('Texto selecionado: copie com Ctrl+C')}});
function fillLeadSelects(){
  const ops=leads.filter(l=>l.stage!=='perdido').sort((a,b)=>(a.nome||'').localeCompare(b.nome||'')).map(l=>`<option value="${esc(l.id)}">${esc(l.nome)}</option>`).join('');
  [['#qLead','Digitar dados manualmente'],['#scLead','Nenhum lead (texto com campos)']].forEach(([s,t])=>{const sel=$(s),cur=sel.value;sel.innerHTML=`<option value="">${t}</option>`+ops;sel.value=cur;if(sel.value!==cur)sel.value=''})}

/* ================= orçamentos (folha A4 + PDF) ================= */
function setPlano(p){const P=PLANOS[p];qItems=P.itens.map(i=>({d:i[0],q:i[1],v:i[2]}));$('#qMens').value=P.mens;drawItems();drawSheet()}
function drawItems(){const w=$('#qItens');w.innerHTML='';qItems.forEach((it,i)=>{const r=document.createElement('div');r.className='it';
  r.innerHTML=`<input aria-label="Descrição do item ${i+1}" maxlength="140"><input aria-label="Quantidade" inputmode="numeric" maxlength="4"><input aria-label="Valor" inputmode="decimal" maxlength="10"><button type="button" aria-label="Remover item">×</button>`;
  const [d,q,v,b]=r.children;d.value=it.d;q.value=it.q;v.value=it.v;
  d.oninput=()=>{it.d=d.value;drawSheet()};q.oninput=()=>{it.q=num(q.value);drawSheet()};v.oninput=()=>{it.v=num(v.value);drawSheet()};b.onclick=()=>{qItems.splice(i,1);drawItems();drawSheet()};w.appendChild(r)})}
function qData(){const sub=qItems.reduce((s,i)=>s+(i.q||0)*(i.v||0),0),lanc=$('#qLanc').checked,pct=lanc?50:Math.min(100,Math.max(0,num($('#qDesc').value))),desc=Math.round(sub*pct)/100,val=Math.min(90,Math.max(1,num($('#qVal').value)||7));
  const base=qEdit?O(qEdit):null,data=base?base.data:hoje(),d=new Date(data+'T12:00:00');d.setDate(d.getDate()+val);
  return {numero:base?base.numero:nextNumero(),data,validoAte:iso(d),est:$('#qEst').value.trim(),resp:$('#qResp').value.trim(),whats:$('#qWhats').value.trim(),local:$('#qLocal').value.trim(),plano:$('#qPlano').value,itens:qItems.map(i=>({d:i.d,q:i.q,v:i.v})),subtotal:Math.round(sub*100)/100,descPct:pct,lanc,desconto:desc,totalImpl:Math.round((sub-desc)*100)/100,mens:num($('#qMens').value),validade:val,prazo:$('#qPrazo').value.trim(),pag:$('#qPag').value.trim(),obs:$('#qObs').value.trim(),leadId:$('#qLead').value||''}}
function nextNumero(){const y=hoje().slice(0,4),ns=orcs.filter(o=>String(o.numero||'').startsWith('BT-'+y)).map(o=>parseInt(String(o.numero).split('-')[2])||0);return 'BT-'+y+'-'+String((ns.length?Math.max(...ns):0)+1).padStart(3,'0')}
function drawSheet(){if(!$('#sheet'))return;const o=qData(),P=PLANOS[o.plano]||PLANOS.Profissional,mk=esc(cfg.marca||'Bistrô Connect');
  $('#sheet').innerHTML=`
  <div class="sh-head"><div class="sh-brand"><img class="sh-logo" src="img/logo-bistro-connect-clara.png" alt="${mk}"></div>
  <div class="sh-num"><div class="k">Orçamento</div><div class="n">${esc(o.numero)}</div><div class="d">Emitido em ${fmtDataLonga(o.data)}<br>Válido até ${fmtDataLonga(o.validoAte)}</div></div></div>
  <div class="sh-body">
    <div class="sh-cols">
      <div class="sh-box"><div class="sh-lbl">Para</div><b>${esc(o.est||'Nome do estabelecimento')}</b>${o.resp?esc(o.resp)+'<br>':''}${o.whats?'WhatsApp '+esc(o.whats)+'<br>':''}${esc(o.local)}</div>
      <div class="sh-box"><div class="sh-lbl">De</div><b>${esc(cfg.nome||'Adilson')} · ${mk}</b>WhatsApp ${esc(cfg.whats)}<br>${cfg.email?esc(cfg.email)+'<br>':''}${esc(cfg.cidade)}${cfg.doc?'<br>'+esc(cfg.doc):''}</div>
    </div>
    <div class="sh-intro"><h1>Cardápio digital com pedido direto no WhatsApp · Plano ${esc(o.plano)}</h1><p>Seus clientes escolhem pelo celular e o pedido chega pronto no seu WhatsApp, com itens, total e endereço. Sem comissão por pedido. Abaixo está tudo o que entregamos e quanto custa.</p></div>
    <table class="sh-t"><thead><tr><th>Item</th><th class="n">Qtd.</th><th class="n">Valor</th><th class="n">Total</th></tr></thead><tbody>
      ${o.itens.map(i=>`<tr><td>${esc(i.d)}</td><td class="n">${esc(i.q||0)}</td><td class="n">${i.v?brl(i.v):'incluso'}</td><td class="n">${i.v?brl((i.q||0)*i.v):'—'}</td></tr>`).join('')}
    </tbody></table>
    <div class="sh-sum">
      <div class="sh-incl"><div class="sh-lbl">Incluso na mensalidade</div><ul>${P.incl.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div>
      <div class="sh-tot"><div><span>Subtotal da implantação</span><span>${brl(o.subtotal)}</span></div>${o.desconto?`<div class="disc"><span>${o.lanc?'Oferta de lançamento (50%)':'Desconto ('+esc(o.descPct)+'%)'}</span><span>− ${brl(o.desconto)}</span></div>`:''}<div class="big"><span>Implantação</span><b>${brl(o.totalImpl)}</b></div><div class="mens"><span>Mensalidade</span><b>${brl(o.mens)}/mês</b></div></div>
    </div>
    <div><div class="sh-lbl">Como funciona a entrega · ${esc(o.prazo)}</div><div class="sh-steps"><div><b>1 · MATERIAL</b>Você envia logo, cardápio, fotos e horários</div><div><b>2 · MONTAGEM</b>O ${mk} monta o cardápio</div><div><b>3 · REVISÃO</b>Você testa e pede ajustes</div><div><b>4 · NO AR</b>QR Codes, arte e treinamento</div></div></div>
    <div class="sh-cond"><div class="sh-lbl">Condições</div><p><b>Pagamento:</b> ${esc(o.pag)}${cfg.pix?' · Chave Pix: '+esc(cfg.pix):''}</p><p><b>Mensalidade:</b> a partir do mês seguinte à publicação, com contrato mínimo de 6 meses.</p>${o.lanc?'<p><b>Oferta de lançamento:</b> desconto em troca de um depoimento em vídeo após 30 dias de uso.</p>':''}${o.obs?`<p><b>Observações:</b> ${esc(o.obs)}</p>`:''}</div>
    <div class="sh-sign"><div>${esc(cfg.nome||'Adilson')} · ${mk}</div><div>Aceite do cliente · data</div></div>
  </div>
  <div class="sh-foot"><span><b>${mk}</b> · A evolução digital da sua gastronomia</span><span>WhatsApp ${esc(cfg.whats)}${cfg.site?' · '+esc(cfg.site):''}${cfg.email?' · '+esc(cfg.email):''}</span></div>`;
  fitSheet()}
function fitSheet(){const w=$('#sheetWrap'),s=$('#sheetScale');if(!w||w.offsetParent===null)return;const k=Math.min(1,(w.clientWidth-32)/794);s.style.transform='scale('+k+')';s.style.width='794px';s.style.height=($('#sheet').offsetHeight*k)+'px'}
addEventListener('resize',fitSheet);
function loadLead(id){const l=L(id);if(!l)return;$('#qEst').value=l.nome||'';$('#qResp').value=l.responsavel||'';$('#qWhats').value=l.whatsapp||'';$('#qLocal').value=['Ponta Grossa',l.bairro].filter(Boolean).join(' · ');if(l.plano&&PLANOS[l.plano]){$('#qPlano').value=l.plano;setPlano(l.plano)}else drawSheet()}
function novoOrc(leadId){qEdit=null;$('#qForm').reset();$('#qTitulo').textContent='Novo orçamento';$('#qLead').value=leadId||'';$('#qPlano').value='Profissional';setPlano('Profissional');if(leadId)loadLead(leadId);abrirAba('orcamentos')}
function abrirOrc(id){const o=O(id);if(!o)return;qEdit=o.id;$('#qTitulo').textContent='Orçamento '+o.numero;$('#qLead').value=o.leadId||'';$('#qEst').value=o.est||'';$('#qResp').value=o.resp||'';$('#qWhats').value=o.whats||'';$('#qLocal').value=o.local||'';$('#qPlano').value=o.plano||'Profissional';qItems=(o.itens||[]).map(i=>Object.assign({},i));$('#qMens').value=o.mens;$('#qDesc').value=o.lanc?0:o.descPct;$('#qLanc').checked=!!o.lanc;$('#qVal').value=o.validade||7;$('#qPrazo').value=o.prazo||'';$('#qPag').value=o.pag||'';$('#qObs').value=o.obs||'';drawItems();drawSheet();abrirAba('orcamentos')}
async function salvarOrc(){const o=qData();if(!o.est){toast('Preencha o nome do estabelecimento');$('#qEst').focus();return null}
  if(qEdit){await salvar('orcamentos',qEdit,o);toast('Orçamento atualizado');return qEdit}
  o.status='enviado';o.criadoEm=hoje();const id=await salvar('orcamentos',null,o);
  if(id){qEdit=id;$('#qTitulo').textContent='Orçamento '+o.numero;toast('Orçamento '+o.numero+' salvo');
    if(o.leadId){const l=L(o.leadId);if(l&&FUNIL.includes(l.stage||'lead')&&l.stage!=='proposta')salvar('leads',l.id,{stage:'proposta',proximoContato:addDias(2),plano:o.plano,implantacao:o.totalImpl,mensalidade:o.mens})}}
  return id}
async function gerarPdf(){const st=$('#qStatus');
  if(!window.html2canvas||!window.jspdf){st.textContent='O gerador de PDF ainda está carregando. Tente de novo em instantes.';return}
  const id=await salvarOrc();if(!id)return;
  st.textContent='Gerando PDF...';const btn=$('#qPdf');btn.disabled=true;
  try{const s=$('#sheetScale'),prev=s.style.transform;s.style.transform='none';
    const canvas=await html2canvas($('#sheet'),{scale:2,backgroundColor:'#ffffff',useCORS:true,logging:false});s.style.transform=prev;
    const {jsPDF}=window.jspdf,pdf=new jsPDF({unit:'mm',format:'a4'}),W=210,H=canvas.height*W/canvas.width,img=canvas.toDataURL('image/jpeg',0.92);
    if(H<=297.5)pdf.addImage(img,'JPEG',0,0,W,H);else if(H<=345){const k=297/H;pdf.addImage(img,'JPEG',(W-W*k)/2,0,W*k,297)}else{let y=0;while(y<H){pdf.addImage(img,'JPEG',0,-y,W,H);y+=297;if(y<H)pdf.addPage()}}
    const o=qData(),nome=('Orcamento '+o.numero+' - '+(o.est||'cliente')).replace(/[\\/:*?"<>|]/g,'')+'.pdf';
    pdf.save(nome);st.textContent='PDF baixado: '+nome;fitSheet()}
  catch(e){console.error(e);st.textContent='Não foi possível gerar o PDF.';fitSheet()}
  btn.disabled=false}
function msgEnvio(){const o=qData();return `Olá${o.resp?', '+primeiroNome(o.resp):''}! Segue o orçamento ${o.numero} do cardápio digital da ${o.est||'sua casa'} (plano ${o.plano}).\n\nImplantação: ${brl(o.totalImpl)}\nMensalidade: ${brl(o.mens)}/mês\nPrazo: ${o.prazo}\nVálido até ${fmtDataLonga(o.validoAte)}.\n\nQualquer dúvida, me chama aqui! ${cfg.nome||'Adilson'} · ${cfg.marca||'Bistrô Connect'}`}
function renderOrcList(){const t=hoje(),ord=orcs.slice().sort((a,b)=>String(b.numero||'').localeCompare(String(a.numero||'')));
  const acc=orcs.filter(o=>o.status==='aceito').length;$('#qResumo').textContent=`${orcs.length} orçamentos · ${acc} aceitos`;
  $('#tbOrc').innerHTML=ord.length?ord.map(o=>{const venc=o.status==='enviado'&&o.validoAte<t,cls={enviado:venc?'bad':'info',aceito:'ok',recusado:''}[o.status]||'',lbl=o.status==='enviado'?(venc?'Vencido':'Enviado'):o.status==='aceito'?'Aceito':'Recusado';
    return `<tr><td><b>${esc(o.numero)}</b><br><span class="muted">${fmtData(o.data)}</span></td><td>${esc(o.est)}</td><td>${esc(o.plano)}</td><td>${brl0(o.totalImpl)}</td><td>${brl0(o.mens)}</td><td>${fmtData(o.validoAte)}</td><td><span class="chip ${cls}">${lbl}</span></td><td><div class="acts-td"><button class="btn small" type="button" data-oopen="${esc(o.id)}">Abrir</button>${o.status==='enviado'?`<button class="btn small primary" type="button" data-oacc="${esc(o.id)}">Aceito</button><button class="btn small" type="button" data-orec="${esc(o.id)}">Recusado</button>`:''}<button class="btn small" type="button" data-odup="${esc(o.id)}">Duplicar</button><button class="btn small perigo" type="button" data-odel="${esc(o.id)}" aria-label="Excluir">×</button></div></td></tr>`}).join(''):'<tr><td colspan="8"><div class="empty">Nenhum orçamento ainda. Preencha o formulário acima e salve.</div></td></tr>'}
async function aceitarOrc(id){const o=O(id);if(!o)return;await salvar('orcamentos',o.id,{status:'aceito',aceitoEm:hoje()});
  const patch={stage:'fechado',fechadoEm:hoje(),plano:o.plano,implantacao:o.totalImpl,mensalidade:o.mens,checklist:{}};
  const l=o.leadId?L(o.leadId):null;
  if(l){patch.checklist=l.checklist||{};await salvar('leads',l.id,patch)}
  else await salvar('leads',null,Object.assign({nome:o.est,responsavel:o.resp,whatsapp:o.whats,tipo:'Outro',criadoEm:hoje(),origem:'orçamento'},patch));
  toast('Aceito! O cliente foi para a aba Entregas')}
function duplicarOrc(id){const o=O(id);if(!o)return;abrirOrc(id);qEdit=null;$('#qTitulo').textContent='Novo orçamento (cópia de '+o.numero+')';drawSheet();toast('Cópia pronta: ajuste e salve')}

/* ================= eventos (delegados, como no original) ================= */
let delOrcArm=null;
document.addEventListener('click',e=>{const b=e.target.closest('[data-contato],[data-edit],[data-orc-lead],[data-stage-set],[data-ativar],[data-pag],[data-rel],[data-oopen],[data-oacc],[data-orec],[data-odel],[data-odup]');if(!b||b.closest('#paleta'))return;
  if(b.dataset.contato)registrarContato(b.dataset.contato);
  else if(b.dataset.edit)abrirFicha(b.dataset.edit);
  else if(b.dataset.orcLead)novoOrc(b.dataset.orcLead);
  else if(b.dataset.stageSet)mudarEtapa(b.dataset.stageSet,b.dataset.v);
  else if(b.dataset.ativar){mudarEtapa(b.dataset.ativar,'ativo');toast('Cliente ativo')}
  else if(b.dataset.pag){const x=L(b.dataset.pag);salvar('leads',x.id,{pagamento:x.pagamento==='atrasado'?'em dia':'atrasado'})}
  else if(b.dataset.rel){salvar('leads',b.dataset.rel,{relatorio:hoje()});toast('Relatório registrado')}
  else if(b.dataset.oopen)abrirOrc(b.dataset.oopen);
  else if(b.dataset.oacc)aceitarOrc(b.dataset.oacc);
  else if(b.dataset.orec){salvar('orcamentos',b.dataset.orec,{status:'recusado'});toast('Marcado como recusado')}
  else if(b.dataset.odup)duplicarOrc(b.dataset.odup);
  else if(b.dataset.odel){if(delOrcArm!==b.dataset.odel){delOrcArm=b.dataset.odel;b.textContent='Confirmar';return}excluir('orcamentos',b.dataset.odel);delOrcArm=null;if(mesmo(qEdit,b.dataset.odel))novoOrc()}});
document.addEventListener('keydown',e=>{if((e.key==='Enter'||e.key===' ')&&e.target.matches('[data-edit][tabindex]')){e.preventDefault();abrirFicha(e.target.dataset.edit)}});
document.addEventListener('change',e=>{const el=e.target;
  if(el.dataset.stage)mudarEtapa(el.dataset.stage,el.value);
  else if(el.dataset.ck){const x=L(el.dataset.ck);const ck=Object.assign({},x.checklist||{});ck[el.dataset.k]=el.checked;salvar('leads',x.id,{checklist:ck})}
  else if(el.dataset.rot!==undefined){const t=hoje(),r=lsGet('bt-rotina-'+t,{});r[el.dataset.rot]=el.checked;lsSet('bt-rotina-'+t,r);render()}});
/* arrastar e soltar no quadro */
document.addEventListener('dragstart',e=>{const c=e.target.closest&&e.target.closest('.card[data-card]');if(!c)return;e.dataTransfer.setData('text/plain',c.dataset.card);e.dataTransfer.effectAllowed='move';c.classList.add('arrastando')});
document.addEventListener('dragend',e=>{const c=e.target.closest&&e.target.closest('.card');if(c)c.classList.remove('arrastando');document.querySelectorAll('.col.alvo').forEach(x=>x.classList.remove('alvo'))});
$('#board').addEventListener('dragover',e=>{const col=e.target.closest('.col');if(!col)return;e.preventDefault();document.querySelectorAll('.col.alvo').forEach(x=>{if(x!==col)x.classList.remove('alvo')});col.classList.add('alvo')});
$('#board').addEventListener('drop',e=>{const col=e.target.closest('.col');if(!col)return;e.preventDefault();col.classList.remove('alvo');const id=e.dataTransfer.getData('text/plain');if(id)mudarEtapa(id,col.dataset.col)});

['#busca','#fTipoFiltro','#fOrigemFiltro'].forEach(s=>$(s).addEventListener(s==='#busca'?'input':'change',render));
document.querySelectorAll('[data-modo]').forEach(b=>b.addEventListener('click',()=>{modo=b.dataset.modo;lsSet('eb-modo',modo);document.querySelectorAll('[data-modo]').forEach(x=>x.setAttribute('aria-pressed',x===b));render()}));
$('#btnPerdidos').addEventListener('click',()=>{$('#perdidosBox').hidden=!$('#perdidosBox').hidden});
$('#btnOrcTop').addEventListener('click',()=>novoOrc());
['qEst','qResp','qWhats','qLocal','qMens','qDesc','qVal','qPrazo','qPag','qObs'].forEach(id=>$('#'+id).addEventListener('input',drawSheet));
$('#qLanc').addEventListener('change',drawSheet);
$('#qPlano').addEventListener('change',()=>setPlano($('#qPlano').value));
$('#qLead').addEventListener('change',()=>{if($('#qLead').value)loadLead($('#qLead').value)});
$('#qAddItem').addEventListener('click',()=>{qItems.push({d:'Novo item',q:1,v:0});drawItems();drawSheet()});
$('#qLimpar').addEventListener('click',()=>novoOrc());
$('#qForm').addEventListener('submit',e=>{e.preventDefault();salvarOrc()});
$('#qPdf').addEventListener('click',gerarPdf);
$('#qMsg').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(msgEnvio());toast('Mensagem copiada')}catch(_){toast('Não deu para copiar automaticamente')}});
$('#qZap').addEventListener('click',async()=>{const z=zapUrl($('#qWhats').value,msgEnvio());if(!z){toast('Informe o WhatsApp do cliente');$('#qWhats').focus();return}const id=await salvarOrc();if(id){const w=open(z,'_blank');if(w)w.opener=null}});
function csv(nome,linhas){const cel=v=>{let s=String(v??'');if(/^[=+\-@\t\r]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"'};
  const blob=new Blob(['﻿'+linhas.map(r=>r.map(cel).join(';')).join('\n')],{type:'text/csv;charset=utf-8'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=nome;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),2000)}
$('#btnCsvLeads').addEventListener('click',()=>csv('leads-'+hoje()+'.csv',[['Estabelecimento','Tipo','Bairro','Responsável','WhatsApp','Instagram','Etapa','Próximo retorno','Plano','Origem','Entrou em','Anotações']].concat(leads.filter(filtroLeads).map(l=>[l.nome,l.tipo,l.bairro,l.responsavel,l.whatsapp,l.instagram,stageName(l.stage),fmtDataLonga(l.proximoContato),l.plano,l.origem,fmtDataLonga(l.criadoEm),l.notas]))));
$('#btnCsvClientes').addEventListener('click',()=>csv('clientes-'+hoje()+'.csv',[['Cliente','WhatsApp','Plano','Mensalidade','Vence dia','Pagamento','Último relatório','Ativo desde']].concat(leads.filter(l=>l.stage==='ativo').map(l=>[l.nome,l.whatsapp,l.plano,num(l.mensalidade).toFixed(2).replace('.',','),l.vencimento,l.pagamento,fmtDataLonga(l.relatorio),fmtDataLonga(l.ativoEm)]))));

/* ajuda */
$('#hpBusca').addEventListener('input',e=>{const q=e.target.value.trim().toLowerCase();let n=0;document.querySelectorAll('#hpLista details.hp').forEach(d=>{const ok=!q||d.textContent.toLowerCase().includes(q);d.hidden=!ok;if(ok)n++;if(q&&ok)d.open=true});$('#hpVazio').hidden=n>0});
$('#hpAbrir').addEventListener('click',e=>{const ds=[...document.querySelectorAll('#hpLista details.hp')],abrir=ds.some(d=>!d.open);ds.forEach(d=>d.open=abrir);e.target.textContent=abrir?'Fechar tudo':'Abrir tudo'});

/* ================= ajustes ================= */
const CAMPOS={cMarca:'marca',cNome:'nome',cWhats:'whats',cEmail:'email',cCidade:'cidade',cSite:'site',cPix:'pix',cDoc:'doc'},METAS={mClientes:'clientes',mMrr:'mrr',mContatos:'contatos',mFechados:'fechados'};
function fillCfg(){Object.entries(CAMPOS).forEach(([i,k])=>{if(document.activeElement!==$('#'+i))$('#'+i).value=cfg[k]||''});Object.entries(METAS).forEach(([i,k])=>{if(document.activeElement!==$('#'+i))$('#'+i).value=(cfg.metas||{})[k]||''})}
$('#cfgForm').addEventListener('submit',async e=>{e.preventDefault();const d={};Object.entries(CAMPOS).forEach(([i,k])=>d[k]=$('#'+i).value.trim());d.marca=d.marca||'Bistrô Connect';
  d.metas={};Object.entries(METAS).forEach(([i,k])=>d.metas[k]=num($('#'+i).value)||cfg.metas[k]);
  if(!demo){const {error}=await db.from('config').upsert({id:'empresa',doc:d});if(error){toast('Não foi possível salvar: '+erroAmigavel(error));return}}
  cfg=Object.assign({},cfg,d);aplicaMarca();drawSheet();render();toast('Ajustes salvos')});
$('#senhaForm').addEventListener('submit',async e=>{e.preventDefault();const a=$('#nsSenha').value,b=$('#nsSenha2').value;
  if(a.length<12)return toast('A senha precisa ter pelo menos 12 caracteres');if(a!==b)return toast('As duas senhas não são iguais');
  if(demo)return toast('Na demonstração a senha não muda');
  const {error}=await db.auth.updateUser({password:a});if(error)return toast(erroAmigavel(error));e.target.reset();toast('Senha trocada')});
$('#btnSairTudo').addEventListener('click',async()=>{if(!confirm('Encerrar a sessão em todos os aparelhos, inclusive este?'))return;if(db&&!demo){try{await db.auth.signOut({scope:'global'})}catch(e){}}sair('Sessões encerradas em todos os aparelhos.')});

/* ================= ficha do lead ================= */
$('#fStage').innerHTML=STAGES.map(s=>`<option value="${s[0]}">${esc(s[1])}</option>`).join('');
$('#fPlano').addEventListener('change',()=>{const p=PLANOS[$('#fPlano').value];if(p){if(!$('#fImpl').value)$('#fImpl').value=p.impl;if(!$('#fMens').value)$('#fMens').value=p.mens}});
const HIST={criado:'Lead criado',contato:'Contato feito',etapa:'Etapa'};
let focoAntes=null;
function abrirFicha(id){editId=id||null;delArm=false;$('#mExcluir').textContent='Excluir lead';focoAntes=document.activeElement;
  const l=(id&&L(id))||{stage:'lead',tipo:'Padaria',proximoContato:hoje()};
  $('#mTitulo').textContent=id?(l.nome||'Lead'):'Novo lead';
  $('#mSub').textContent=id?[stageName(l.stage),l.origem?'origem: '+l.origem:'',l.criadoEm?'desde '+fmtDataLonga(l.criadoEm):''].filter(Boolean).join(' · '):'';
  $('#mExcluir').hidden=!id;$('#fichaAcoes').hidden=!id;
  const set=(s,v)=>$(s).value=v??'';set('#fNome',l.nome);set('#fTipo',l.tipo||'Padaria');set('#fBairro',l.bairro);set('#fResp',l.responsavel);set('#fWhats',l.whatsapp);set('#fInsta',l.instagram);set('#fNota',l.nota);set('#fAval',l.avaliacoes);set('#fStage',l.stage||'lead');set('#fProx',l.proximoContato);set('#fPlano',l.plano||'');set('#fImpl',l.implantacao||'');set('#fMens',l.mensalidade||'');set('#fVenc',l.vencimento);set('#fNotas',l.notas);
  if(!$('#fTipo').value)$('#fTipo').value='Outro';
  const z=id?zapUrl(l.whatsapp,scriptPara(l)):'';$('#mZap').hidden=!z;if(z)$('#mZap').href=z;
  const h=(l.historico||[]).slice().reverse();$('#mHistWrap').hidden=!h.length;
  $('#mHist').innerHTML=h.map(x=>`<li>${esc(HIST[x.t]||x.t)}${x.t==='etapa'?': '+esc(stageName(x.v)):''}<small>${fmtDataLonga(x.d)}</small></li>`).join('');
  $('#veu').hidden=false;$('#ficha').hidden=false;$('#fNome').focus()}
function fecharFicha(){$('#veu').hidden=true;$('#ficha').hidden=true;if(focoAntes&&focoAntes.focus&&document.contains(focoAntes))focoAntes.focus()}
$('#btnNovo').addEventListener('click',()=>abrirFicha(null));
['#mFechar','#mCancelar','#veu'].forEach(s=>$(s).addEventListener('click',fecharFicha));
$('#mContato').addEventListener('click',()=>{if(editId){registrarContato(editId);fecharFicha()}});
$('#mOrc').addEventListener('click',()=>{const id=editId;fecharFicha();novoOrc(id)});
$('#mExcluir').addEventListener('click',()=>{if(!delArm){delArm=true;$('#mExcluir').textContent='Clique de novo para excluir';return}excluir('leads',editId);fecharFicha()});
$('#form').addEventListener('submit',e=>{e.preventDefault();const v=s=>$(s).value.trim(),old=L(editId)||{};
  if(!v('#fNome')){toast('Informe o nome do estabelecimento');$('#fNome').focus();return}
  const d={nome:v('#fNome'),tipo:v('#fTipo'),bairro:v('#fBairro'),responsavel:v('#fResp'),whatsapp:v('#fWhats'),instagram:v('#fInsta'),nota:v('#fNota'),avaliacoes:v('#fAval'),stage:v('#fStage'),proximoContato:v('#fProx'),plano:v('#fPlano'),implantacao:num(v('#fImpl')),mensalidade:num(v('#fMens')),vencimento:v('#fVenc'),notas:v('#fNotas')};
  if(d.stage==='fechado'&&!old.fechadoEm)d.fechadoEm=hoje();if(d.stage==='ativo'){if(!old.pagamento)d.pagamento='em dia';if(!old.ativoEm)d.ativoEm=hoje()}
  if(!editId){d.criadoEm=hoje();d.checklist={};d.origem='manual'}
  salvar('leads',editId,d);fecharFicha();toast(editId?'Lead atualizado':'Lead adicionado')});

/* ================= busca rápida (Ctrl+K) ================= */
let palItens=[],palSel=0;
function abrirPaleta(){$('#paleta').hidden=false;$('#paletaInput').value='';renderPaleta();$('#paletaInput').focus()}
function fecharPaleta(){$('#paleta').hidden=true}
function renderPaleta(){const q=$('#paletaInput').value.trim().toLowerCase(),qd=digitos(q);
  const acoes=[['Novo lead','ação',()=>abrirFicha(null)],['Novo orçamento','ação',()=>novoOrc()]].concat(Object.entries(TITULOS).map(([k,t])=>['Ir para '+t,'tela',()=>abrirAba(k)]));
  const it=[];
  leads.forEach(l=>{const txt=[l.nome,l.bairro,l.responsavel,l.tipo].join(' ').toLowerCase();if(!q||txt.includes(q)||(qd.length>=3&&digitos(l.whatsapp).includes(qd)))it.push({t:l.nome||'Sem nome',s:stageName(l.stage)+(l.bairro?' · '+l.bairro:''),k:'lead',f:()=>abrirFicha(l.id)})});
  orcs.forEach(o=>{const txt=[o.numero,o.est].join(' ').toLowerCase();if(!q||txt.includes(q))it.push({t:o.numero+' · '+(o.est||''),s:o.plano+' · '+brl0(o.totalImpl),k:'orçamento',f:()=>abrirOrc(o.id)})});
  acoes.forEach(([t,k,f])=>{if(!q||t.toLowerCase().includes(q))it.push({t,s:'',k,f})});
  palItens=q?it.slice(0,30):acoes.map(([t,k,f])=>({t,s:'',k,f})).concat(it.filter(x=>x.k==='lead').slice(0,8));palSel=0;
  $('#paletaLista').innerHTML=palItens.length?palItens.map((x,i)=>`<li role="option" data-i="${i}" aria-selected="${i===palSel}"><div class="pt"><b>${esc(x.t)}</b>${x.s?`<small>${esc(x.s)}</small>`:''}</div><span class="tipo">${esc(x.k)}</span></li>`).join(''):'<li aria-disabled="true"><div class="pt"><small>Nada encontrado.</small></div></li>'}
function escolhe(i){const x=palItens[i];if(!x)return;fecharPaleta();x.f()}
$('#btnPaleta').addEventListener('click',abrirPaleta);
$('#paletaInput').addEventListener('input',renderPaleta);
$('#paleta').addEventListener('click',e=>{if(e.target.id==='paleta')return fecharPaleta();const li=e.target.closest('li[data-i]');if(li)escolhe(+li.dataset.i)});
$('#paletaInput').addEventListener('keydown',e=>{if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();palSel=(palSel+(e.key==='ArrowDown'?1:-1)+palItens.length)%Math.max(1,palItens.length);
  document.querySelectorAll('#paletaLista li[data-i]').forEach(li=>li.setAttribute('aria-selected',+li.dataset.i===palSel));const at=document.querySelector('#paletaLista li[aria-selected="true"]');if(at)at.scrollIntoView({block:'nearest'})}
  else if(e.key==='Enter'){e.preventDefault();escolhe(palSel)}});
addEventListener('keydown',e=>{
  if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'&&!$('#app').hidden){e.preventDefault();$('#paleta').hidden?abrirPaleta():fecharPaleta();return}
  if(e.key==='Escape'){if(!$('#paleta').hidden)fecharPaleta();else if(!$('#ficha').hidden)fecharFicha();return}
  if(e.key==='Tab'&&!$('#ficha').hidden){const f=[...$('#ficha').querySelectorAll('a[href]:not([hidden]),button:not([hidden]),input,select,textarea')].filter(x=>x.offsetParent!==null),a=f[0],z=f[f.length-1];
    if(e.shiftKey&&document.activeElement===a){e.preventDefault();z.focus()}else if(!e.shiftKey&&document.activeElement===z){e.preventDefault();a.focus()}}});

/* ================= demonstração ================= */
function dadosDemo(){const d=n=>addDias(n),c=n=>new Date(Date.now()+n*864e5).toISOString();
  const H=(...x)=>x.map(([n,t,v])=>({d:d(n),t,v}));
  leads=[
   {id:'d1',nome:'Padaria Trigo de Ouro',tipo:'Padaria',bairro:'Centro',responsavel:'Marta Ribeiro',whatsapp:'(42) 99911-2233',instagram:'@trigodeouro',nota:'4,8',avaliacoes:'312',stage:'ativo',plano:'Profissional',implantacao:1497,mensalidade:199,vencimento:'10',pagamento:'em dia',relatorio:d(-3),fechadoEm:d(-70),ativoEm:d(-60),criadoEm:d(-90),origem:'site / meta',checklist:{kickoff:1,montagem:1,revisao:1,publicacao:1,treinamento:1,acompanhamento:1},historico:H([-90,'criado','lead'],[-85,'contato'],[-80,'etapa','demo'],[-75,'etapa','proposta'],[-70,'etapa','fechado'],[-60,'etapa','ativo']),_criado:c(-90)},
   {id:'d2',nome:'Café Grão Nobre',tipo:'Cafeteria',bairro:'Uvaranas',responsavel:'Rafael Lima',whatsapp:'(42) 99922-3344',stage:'ativo',plano:'Essencial',implantacao:997,mensalidade:149,vencimento:'5',pagamento:'atrasado',relatorio:d(-40),fechadoEm:d(-40),ativoEm:d(-30),criadoEm:d(-50),origem:'chat',checklist:{kickoff:1,montagem:1,revisao:1,publicacao:1,treinamento:1},historico:H([-50,'criado','lead'],[-40,'etapa','fechado'],[-30,'etapa','ativo']),_criado:c(-50)},
   {id:'d3',nome:'Brasa Burger',tipo:'Hamburgueria',bairro:'Oficinas',responsavel:'Diego Souza',whatsapp:'(42) 99933-4455',stage:'fechado',plano:'Premium',implantacao:2497,mensalidade:299,fechadoEm:d(-4),criadoEm:d(-20),origem:'site / instagram',checklist:{kickoff:1,montagem:1},historico:H([-20,'criado','lead'],[-12,'contato'],[-10,'etapa','respondeu'],[-8,'etapa','demo'],[-6,'etapa','proposta'],[-4,'etapa','fechado']),_criado:c(-20)},
   {id:'d4',nome:'Confeitaria Doce Lar',tipo:'Confeitaria',bairro:'Jardim Carvalho',responsavel:'Ana Paula',whatsapp:'(42) 99944-5566',nota:'4,9',avaliacoes:'188',stage:'proposta',plano:'Profissional',implantacao:1497,mensalidade:199,proximoContato:d(-1),criadoEm:d(-12),origem:'site',historico:H([-12,'criado','lead'],[-9,'contato'],[-7,'etapa','respondeu'],[-5,'etapa','demo'],[-3,'etapa','proposta']),_criado:c(-12)},
   {id:'d5',nome:'Restaurante Alecrim',tipo:'Restaurante',bairro:'Órfãs',responsavel:'Paulo César',whatsapp:'(42) 99955-6677',stage:'demo',proximoContato:d(0),criadoEm:d(-9),origem:'chat / google',historico:H([-9,'criado','lead'],[-6,'contato'],[-4,'etapa','respondeu'],[-2,'etapa','demo']),_criado:c(-9)},
   {id:'d6',nome:'Pizzaria Forno a Lenha',tipo:'Pizzaria',bairro:'Nova Rússia',responsavel:'Júlia Martins',whatsapp:'(42) 99966-7788',stage:'respondeu',proximoContato:d(1),criadoEm:d(-6),origem:'site / meta',historico:H([-6,'criado','lead'],[-4,'contato'],[-3,'etapa','respondeu']),_criado:c(-6)},
   {id:'d7',nome:'Padaria Bom Dia',tipo:'Padaria',bairro:'Estrela',responsavel:'Carlos Alberto',whatsapp:'(42) 99977-8899',nota:'4,6',avaliacoes:'97',stage:'contatado',proximoContato:d(0),ultimoContato:d(-2),criadoEm:d(-3),origem:'manual',historico:H([-3,'criado','lead'],[-2,'contato']),_criado:c(-3)},
   {id:'d8',nome:'Marmitaria Sabor Caseiro',tipo:'Marmitaria',bairro:'Contorno',responsavel:'Dona Rosa',whatsapp:'(42) 99988-9900',stage:'lead',criadoEm:d(0),origem:'site / meta',historico:H([0,'criado','lead']),_criado:c(0)},
   {id:'d9',nome:'Café da Praça',tipo:'Cafeteria',bairro:'Centro',stage:'lead',criadoEm:d(-1),origem:'chat',whatsapp:'(42) 99900-1122',responsavel:'Lucas',historico:H([-1,'criado','lead']),_criado:c(-1)},
   {id:'d10',nome:'Lanchonete do Zé',tipo:'Outro',bairro:'Boa Vista',stage:'perdido',notas:'Achou caro agora, voltar em março.',criadoEm:d(-30),historico:H([-30,'criado','lead'],[-20,'etapa','perdido']),_criado:c(-30)}];
  orcs=[
   {id:'o1',numero:'BT-'+hoje().slice(0,4)+'-001',data:d(-75),validoAte:d(-68),est:'Padaria Trigo de Ouro',resp:'Marta Ribeiro',plano:'Profissional',itens:PLANOS.Profissional.itens.map(i=>({d:i[0],q:i[1],v:i[2]})),subtotal:1497,descPct:0,desconto:0,totalImpl:1497,mens:199,status:'aceito',leadId:'d1',prazo:'7 dias úteis',pag:'50% no aceite e 50% na entrega'},
   {id:'o2',numero:'BT-'+hoje().slice(0,4)+'-002',data:d(-6),validoAte:d(1),est:'Brasa Burger',resp:'Diego Souza',plano:'Premium',itens:PLANOS.Premium.itens.map(i=>({d:i[0],q:i[1],v:i[2]})),subtotal:2497,descPct:0,desconto:0,totalImpl:2497,mens:299,status:'aceito',leadId:'d3',prazo:'10 dias úteis',pag:'50% no aceite e 50% na entrega'},
   {id:'o3',numero:'BT-'+hoje().slice(0,4)+'-003',data:d(-3),validoAte:d(4),est:'Confeitaria Doce Lar',resp:'Ana Paula',whats:'(42) 99944-5566',plano:'Profissional',itens:PLANOS.Profissional.itens.map(i=>({d:i[0],q:i[1],v:i[2]})),subtotal:1497,lanc:true,descPct:50,desconto:748.5,totalImpl:748.5,mens:199,status:'enviado',leadId:'d4',prazo:'7 dias úteis',pag:'50% no aceite e 50% na entrega'}]}
$('#btnDemo').addEventListener('click',()=>{demo=true;dadosDemo();start()});

/* ================= início ================= */
let started=false;
async function start(){if(started)return;started=true;
  $('#auth').hidden=true;$('#app').hidden=false;$('#faixaDemo').hidden=!demo;
  if(!demo){const u=await db.auth.getUser(),email=(u.data&&u.data.user&&u.data.user.email)||'';$('#quemEmail').textContent=email;$('#avatar').textContent=(email[0]||'A').toUpperCase();
    await Promise.all([reload('leads'),reload('orcamentos'),loadCfg()]);
    db.channel('painel').on('postgres_changes',{event:'*',schema:'public',table:'leads'},()=>reload('leads'))
      .on('postgres_changes',{event:'*',schema:'public',table:'orcamentos'},()=>reload('orcamentos'))
      .on('postgres_changes',{event:'*',schema:'public',table:'config'},()=>loadCfg()).subscribe()}
  else{$('#quemEmail').textContent='demonstração';await loadCfg()}
  $('#quemNome').textContent=cfg.nome||'Administrador';
  abrirAba(lsGet('bt-aba','hoje'));const h0=(location.hash||'').slice(1);if(TITULOS[h0])abrirAba(h0)}

modo=lsGet('eb-modo','quadro')==='lista'?'lista':'quadro';document.querySelectorAll('[data-modo]').forEach(x=>x.setAttribute('aria-pressed',x.dataset.modo===modo));
setPlano('Profissional');fillCfg();

/* ================= conectar o painel pela própria tela ================= */
const RX_URL=/^https:\/\/[a-z0-9-]+\.supabase\.co\/?$/;
function conexaoLocal(){try{const v=JSON.parse(localStorage.getItem('bc-supa')||'null');return v&&RX_URL.test(v.url||'')&&/^eyJ/.test(v.key||'')?v:{}}catch(e){return {}}}
let cxDados=null;
$('#fConecta').addEventListener('submit',async function(e){e.preventDefault();msgAuth('');
  const url=$('#cxUrl').value.trim().replace(/\/+$/,''),key=$('#cxKey').value.replace(/\s+/g,''),zap=$('#cxZap').value.replace(/\D/g,'');
  if(!RX_URL.test(url))return msgAuth('A Project URL tem este formato: https://xxxxxxxx.supabase.co');
  if(!/^eyJ[\w-]+\.[\w-]+\.[\w-]+$/.test(key))return msgAuth('A chave anon começa com "eyJ" e tem dois pontos no meio. Copie de novo, inteira.');
  try{const p=JSON.parse(atob(key.split('.')[1].replace(/-/g,'+').replace(/_/g,'/')));if(p.role==='service_role')return msgAuth('Essa é a chave service_role (secreta). Use a chave anon public.')}catch(x){}
  if(zap&&(zap.length<10||zap.length>13))return msgAuth('Confira o WhatsApp: DDD + número.');
  const b=this.querySelector('button[type=submit]');b.disabled=true;b.textContent='Testando…';
  try{const r=await fetch(url+'/rest/v1/leads?select=id&limit=1',{headers:{apikey:key,Authorization:'Bearer '+key},cache:'no-store'});
    let j={};try{j=await r.json()}catch(x){}
    const txt=JSON.stringify(j);
    if(r.status===404||/PGRST205|42P01|does not exist|Could not find the table/i.test(txt))throw new Error('Conectou, mas as tabelas não existem. Rode o arquivo ebistro-banco-completo.sql no SQL Editor do Supabase e tente de novo.');
    if(/Invalid API key|No API key|JWSError|JWT/i.test(txt))throw new Error('A chave não confere com essa URL. Copie a chave anon public do mesmo projeto.');
    if(!r.ok&&!/42501|permission denied/i.test(txt))throw new Error('O Supabase respondeu com erro ('+r.status+'). Confira a URL e a chave.');
    cxDados={url,key,zap:zap.length===10||zap.length===11?'55'+zap:zap};
    try{localStorage.setItem('bc-supa',JSON.stringify({url,key}))}catch(x){}
    $('#fConecta').hidden=true;$('#cxOk').hidden=false}
  catch(err){msgAuth(/Failed to fetch|NetworkError|Load failed/i.test(err.message)?'Não encontrei esse endereço. Confira a Project URL.':err.message)}
  finally{b.disabled=false;b.textContent='Testar e conectar'}});
$('#btnBaixaCfg').addEventListener('click',()=>{const B=window.BISTRO||{},d=cxDados||{};const q=v=>JSON.stringify(String(v||''));
  const txt='/* Configuração do site Bistrô Connect (gerada pelo painel). Este arquivo é público: só a chave anon, nunca a service_role. */\nwindow.BISTRO = {\n  // WhatsApp que recebe os contatos: 55 + DDD + número, só dígitos\n  whatsapp: '+q(d.zap||B.whatsapp)+',\n  // ID do Meta Pixel (opcional)\n  pixelId: '+q(B.pixelId)+',\n  // Supabase: leads do formulário e do chat\n  supabaseUrl: '+q(d.url)+',\n  supabaseKey: '+q(d.key)+',\n  // Função de IA do chat (opcional)\n  aiUrl: '+q(B.aiUrl)+'\n};\nif (!window.BISTRO.whatsapp) console.warn("Bistrô Connect: preencha o WhatsApp em assets/config.js");\n';
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([txt],{type:'application/javascript'}));a.download='config.js';document.body.appendChild(a);a.click();a.remove()});
$('#btnEntrarAgora').addEventListener('click',()=>location.reload());
$('#btnTrocaBanco').addEventListener('click',()=>{if(!confirm('Desligar este navegador do banco atual e conectar outro?'))return;try{localStorage.removeItem('bc-supa')}catch(e){}location.reload()});

(async()=>{
  let msg='';try{msg=sessionStorage.getItem('eb-msg')||'';sessionStorage.removeItem('eb-msg')}catch(e){}
  const B=window.BISTRO||{},LOCAL=conexaoLocal(),url=String(B.supabaseUrl||LOCAL.url||''),chave=String(B.supabaseKey||LOCAL.key||'');
  if(!window.supabase||!/^https:\/\/[a-z0-9-]+\.supabase\.co\/?$/.test(url)||!chave){mostraForm('semConfig');return}
  if(!B.supabaseUrl&&LOCAL.url)$('#btnTrocaBanco').hidden=false;
  db=window.supabase.createClient(url.replace(/\/$/,''),chave,{auth:{storage:window.sessionStorage,persistSession:true,autoRefreshToken:true,detectSessionInUrl:false}});
  db.auth.onAuthStateChange(ev=>{if(ev==='SIGNED_OUT'&&!$('#app').hidden&&!saindo)sair('Sua sessão terminou. Entre de novo.')});
  const {data}=await db.auth.getSession();
  if(data&&data.session){try{await segundaEtapa();return}catch(e){}}
  mostraForm('fLogin');if(msg)msgAuth(msg,/encerradas/.test(msg));
})();
})();
