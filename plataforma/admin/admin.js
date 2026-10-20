/* Painel do dono da plataforma: todas as lojas, vendas do mês, plano e situação.
   Usa a sessão do painel (mesma aba) e só abre para quem está em plataforma_admins com login em 2 etapas. */
(function () {
'use strict';
const CFG=window.BC||{};
const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const brl=n=>'R$ '+Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
const dataBR=s=>{const d=new Date(s);return isNaN(d)?'—':d.toLocaleDateString('pt-BR')};
const SITE=String(CFG.site||location.origin).replace(/\/+$/,'');
let db=null,lojas=[],mesSel='';
function toast(t){const el=$('#toast');el.textContent=t;el.hidden=false;clearTimeout(toast.t);toast.t=setTimeout(()=>el.hidden=true,2600)}
function bloqueia(msg){$('#bloqueioMsg').textContent=msg;$('#bloqueio').hidden=false;$('#app').hidden=true}
/* de onde veio a loja: "google / cpc / padaria-sp" (vazio = direto) */
const origemTxt=o=>{o=o||{};return o.fonte?[o.fonte,o.meio,o.campanha].filter(Boolean).join(' / '):'direto'};
function kpi(l,v,s){return `<div class="kpi"><span class="lbl">${esc(l)}</span><span class="val">${esc(v)}</span>${s?`<span class="sub">${esc(s)}</span>`:''}</div>`}
async function carrega(){const r=await db.rpc('admin_lojas',mesSel?{p_mes:mesSel+'-01'}:{});if(r.error){bloqueia(/42501|permiss/i.test(r.error.message+r.error.code)?'Esta conta não é administradora da plataforma (ou entrou sem o login em 2 etapas).':'Não foi possível carregar: '+r.error.message);return false}
  lojas=r.data||[];desenha();return true}
function desenha(){const at=lojas.filter(l=>l.status==='ativa'),mes=mesSel?new Date(mesSel+'-01T00:00:00'):new Date();mes.setDate(1);mes.setHours(0,0,0,0);
  $('#kpis').innerHTML=kpi('Lojas ativas',at.length,lojas.length+' cadastradas')+kpi('Vendido nas lojas (mês)',brl(at.reduce((s,l)=>s+Number(l.vendido_mes||0),0)),at.reduce((s,l)=>s+Number(l.pedidos_mes||0),0)+' pedidos')+kpi('Mensalidades do mês',brl(at.reduce((s,l)=>s+Number(l.mensalidade||0),0)),'pelo plano de cada loja')+kpi('Lojas novas no mês',lojas.filter(l=>new Date(l.criada)>=mes).length,(()=>{const c={};lojas.filter(l=>new Date(l.criada)>=mes).forEach(l=>{const k=(l.origem&&l.origem.fonte)||'direto';c[k]=(c[k]||0)+1});return Object.entries(c).sort((a,b)=>b[1]-a[1]).slice(0,3).map(([k,n])=>k+': '+n).join(' · ')})());
  $('#subtitulo').textContent=(mesSel?new Date(mesSel+'-15T12:00:00'):new Date()).toLocaleDateString('pt-BR',{month:'long',year:'numeric'})+(mesSel&&mesSel!==new Date().toISOString().slice(0,7)?' · mês fechado':'');
  const q=($('#busca').value||'').trim().toLowerCase(),f=$('#filtro').value;
  const L=lojas.filter(l=>(!f||l.status===f)&&(!q||[l.store_name,l.slug,l.dono].some(x=>String(x||'').toLowerCase().includes(q))));
  $('#tb').innerHTML=L.map(l=>`<tr><td><b>${esc(l.store_name)}</b><br><a class="muted" href="${esc(SITE+'/l/'+l.slug)}" target="_blank" rel="noopener">/l/${esc(l.slug)}</a> · <span class="muted">${esc(l.modelo)}</span></td><td>${esc(l.dono||'—')}</td><td>${dataBR(l.criada)}</td><td>${esc(origemTxt(l.origem))}${l.origem&&l.origem.termo?`<br><span class="muted">${esc(l.origem.termo)}</span>`:''}</td><td>${Number(l.pedidos_mes||0)}</td><td>${brl(l.vendido_mes)}</td><td>${esc(l.plano||'')}<br><span class="muted">${Number(l.mensalidade)?brl(l.mensalidade)+'/mês':'grátis'}</span></td><td><select data-status="${esc(l.id)}" aria-label="Situação de ${esc(l.store_name)}">${['ativa','suspensa','cancelada'].map(s=>`<option value="${s}"${s===l.status?' selected':''}>${s[0].toUpperCase()+s.slice(1)}</option>`).join('')}</select></td></tr>`).join('')||'<tr><td colspan="8"><div class="empty">Nenhuma loja encontrada.</div></td></tr>'}
$('#mesAdmin').addEventListener('change',function(){mesSel=this.value;carrega()});
$('#busca').addEventListener('input',desenha);$('#filtro').addEventListener('change',desenha);
document.addEventListener('change',async e=>{const s=e.target.closest('[data-status]');if(!s)return;const l=lojas.find(x=>x.id===s.dataset.status);
  if(s.value!=='ativa'&&!confirm((s.value==='suspensa'?'Suspender':'Cancelar')+' a loja "'+l.store_name+'"? O site dela sai do ar e o cardápio fica oculto.')){s.value=l.status;return}
  const r=await db.rpc('admin_status_loja',{p_loja:l.id,p_status:s.value});if(r.error){toast('Não foi possível: '+r.error.message);s.value=l.status;return}toast('Situação atualizada');carrega()});
$('#btnCsv').addEventListener('click',()=>{const lin=[['Loja','Endereço','Modelo','Dono','Criada','Origem','Termo/anúncio','Pedidos no mês','Vendido no mês','Plano','Mensalidade','Situação']].concat(lojas.map(l=>[l.store_name,'/l/'+l.slug,l.modelo,l.dono,dataBR(l.criada),origemTxt(l.origem),(l.origem&&(l.origem.termo||l.origem.conteudo))||'',l.pedidos_mes,String(Number(l.vendido_mes||0).toFixed(2)).replace('.',','),l.plano,String(Number(l.mensalidade||0).toFixed(2)).replace('.',','),l.status]));
  const cel=v=>{let c=String(v??'');if(/^[=+\-@\t\r]/.test(c))c="'"+c;return '"'+c.replace(/"/g,'""')+'"'};
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob(['﻿'+lin.map(r=>r.map(cel).join(';')).join('\r\n')],{type:'text/csv;charset=utf-8'}));a.download='lojas-'+(mesSel||new Date().toISOString().slice(0,7))+'.csv';a.click()});
(async()=>{
  const url=String(CFG.supabaseUrl||''),chave=String(CFG.supabaseKey||'');
  if(!window.supabase||!/^https:\/\/[a-z0-9-]+\.supabase\.co\/?$/.test(url)||!chave)return bloqueia('Plataforma ainda não conectada (assets/config.js).');
  db=window.supabase.createClient(url.replace(/\/$/,''),chave,{auth:{storage:window.sessionStorage,persistSession:true,autoRefreshToken:true,detectSessionInUrl:false}});
  const {data}=await db.auth.getSession();if(!data||!data.session)return bloqueia('Entre pelo painel com a sua conta de administrador (login em 2 etapas) e volte aqui.');
  if(await carrega()){$('#bloqueio').hidden=true;$('#app').hidden=false;setInterval(()=>{if(!document.hidden)carrega()},120000)}
})();
})();
