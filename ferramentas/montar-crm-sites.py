#!/usr/bin/env python3
"""Monta o CRM da Mr. Connect (holding da Bistrô Connect) em sites-personalizados/crm/.

É o mesmo CRM do site oficial (admin/), com:
  - só os leads e orçamentos da linha de sites personalizados (campo linha = "sites"); os da plataforma ficam no /crm/ dela
  - os planos atuais (Cardápio Digital, Site Gastronômico, Digital Experience, Signature)
  - a Biblioteca: Materiais (PDFs + tabela de preços vigente), Scripts (Arsenal e Playbook), Objeções e o Manual de operação
  - nenhum acesso a painel de loja ou à plataforma: é o CRM de gestão da holding
Fontes: admin/, paineis/crm-sites/biblioteca.js, manual/manual-de-operacao.md, manual/playbook-resumo.md, manual/materiais-vendas/*.pdf
Uso:  python3 ferramentas/montar-crm-sites.py
"""
import html, os, re, shutil, subprocess

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(RAIZ, "sites-personalizados/crm")
os.chdir(RAIZ)


# ---------------------------------------------------------------- markdown simples → HTML (títulos, listas, tabelas, tarefas)
def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    return t


def md_html(md):
    """Devolve [(titulo_secao, html_corpo)] cortando em cada '## '."""
    secoes, atual, corpo = [], None, []
    linhas = md.split("\n")
    i = 0

    def fecha():
        if atual is not None:
            secoes.append((atual, "\n".join(corpo)))

    lista = None  # 'ul' | 'ol' | 'task'
    def fecha_lista():
        nonlocal lista
        if lista:
            corpo.append("</ul>" if lista in ("ul", "task") else "</ol>")
            lista = None

    while i < len(linhas):
        l = linhas[i]
        if l.startswith("# "):
            i += 1; continue
        if l.startswith("## "):
            fecha_lista(); fecha(); atual = l[3:].strip(); corpo = []; i += 1; continue
        if l.startswith("### "):
            fecha_lista(); corpo.append("<h4>" + inline(l[4:].strip()) + "</h4>"); i += 1; continue
        if l.startswith("| "):
            fecha_lista()
            rows = []
            while i < len(linhas) and linhas[i].startswith("|"):
                rows.append([c.strip() for c in linhas[i].strip().strip("|").split("|")]); i += 1
            cab, dados = rows[0], [r for r in rows[1:] if not set("".join(r)) <= set("-: ")]
            corpo.append('<div class="tablewrap"><table><thead><tr>' + "".join("<th>" + inline(c) + "</th>" for c in cab) +
                         "</tr></thead><tbody>" + "".join("<tr>" + "".join("<td>" + inline(c) + "</td>" for c in r) + "</tr>" for r in dados) +
                         "</tbody></table></div>")
            continue
        m = re.match(r"^- \[ \] (.*)", l)
        if m:
            if lista != "task": fecha_lista(); corpo.append('<ul class="bib-tarefas">'); lista = "task"
            corpo.append("<li><label><input type=\"checkbox\"> " + inline(m.group(1)) + "</label></li>"); i += 1; continue
        m = re.match(r"^- (.*)", l)
        if m:
            if lista != "ul": fecha_lista(); corpo.append("<ul>"); lista = "ul"
            corpo.append("<li>" + inline(m.group(1)) + "</li>"); i += 1; continue
        m = re.match(r"^\d+\. (.*)", l)
        if m:
            if lista != "ol": fecha_lista(); corpo.append("<ol>"); lista = "ol"
            corpo.append("<li>" + inline(m.group(1)) + "</li>"); i += 1; continue
        if not l.strip():
            fecha_lista(); i += 1; continue
        fecha_lista(); corpo.append("<p>" + inline(l.strip()) + "</p>"); i += 1
    fecha_lista(); fecha()
    return secoes


def detalhes(secoes, aberto_primeiro=True):
    out = []
    for n, (t, h) in enumerate(secoes):
        out.append('<details class="hp"%s><summary>%s</summary><div class="hb">%s</div></details>'
                   % (" open" if (n == 0 and aberto_primeiro) else "", inline(t), h))
    return "\n".join(out)


# ---------------------------------------------------------------- cópia
shutil.rmtree(DEST, ignore_errors=True)
shutil.copytree("admin", DEST)
os.makedirs(os.path.join(DEST, "materiais"), exist_ok=True)
for f in sorted(os.listdir("manual/materiais-vendas")):
    if f.endswith(".pdf"):
        shutil.copy(os.path.join("manual/materiais-vendas", f), os.path.join(DEST, "materiais", f))
shutil.copy("paineis/crm-sites/biblioteca.js", os.path.join(DEST, "biblioteca.js"))


def troca(s, a, b, n=1):
    assert s.count(a) == n, (a[:90], s.count(a))
    return s.replace(a, b)


# ---------------------------------------------------------------- index.html
p = os.path.join(DEST, "index.html")
s = open(p, encoding="utf-8").read()
s = troca(s, "<title>Painel · Bistrô Connect</title>", "<title>CRM · Mr. Connect</title>")
s = troca(s, "family=Poppins:wght@500;600;700", "family=Poppins:wght@300;500;600;700;800")
s = troca(s, '<script src="../assets/config.js"></script>',
          '<script src="/assets/config.js"></script>\n'
          '<script>/* mesmo banco do site de vendas: usa a configuração do domínio */'
          '(function(){var B=window.BISTRO||{},C=window.BC||{};window.BISTRO={whatsapp:B.whatsapp||String(C.suporteWhatsapp||"").replace(/\\D/g,""),'
          'supabaseUrl:B.supabaseUrl||C.supabaseUrl||"",supabaseKey:B.supabaseKey||C.supabaseKey||""}})();</script>')
s = troca(s, '<script src="painel.js" defer></script>', '<script src="biblioteca.js" defer></script>\n<script src="painel.js" defer></script>')
s = troca(s, '<div class="auth-brand"><img src="img/logo.png" alt=""><div><b class="marca-nome">Bistrô Connect</b><small>Painel administrativo</small></div></div>',
          '<div class="auth-brand mc-auth"><div><b class="mc-marca" aria-label="Mr. Connect"><span class="mr">Mr.</span><span class="cn">Connect</span></b><small class="mc-tag">A evolução digital da sua marca.</small><small>CRM da holding · Bistrô Connect</small></div></div>')
s = troca(s, '<div class="side-brand"><img src="img/logo.png" alt=""><div><b class="marca-nome">Bistrô Connect</b><small>Painel</small></div></div>',
          '<div class="side-brand"><div><b class="mc-marca" aria-label="Mr. Connect"><span class="mr">Mr.</span><span class="cn">Connect</span></b><small>CRM · Sites personalizados</small></div></div>')
s = troca(s, '<a class="btn ghost-escuro small" href="../" target="_blank" rel="noopener">Ver site ↗</a>',
          '<a class="btn ghost-escuro small" href="../" target="_blank" rel="noopener">Página de vendas ↗</a>')

# menu: Biblioteca (Materiais, Scripts, Objeções, Manual)
ico_doc = '<svg viewBox="0 0 24 24"><path d="M4 5a2 2 0 0 1 2-2h12v16H6a2 2 0 0 0-2 2z"/><path d="M8 7h7M8 11h5"/></svg>'
ico_obj = '<svg viewBox="0 0 24 24"><path d="M12 3l9 16H3z"/><path d="M12 10v4M12 17h.01"/></svg>'
ico_man = '<svg viewBox="0 0 24 24"><path d="M12 6c-2-2-5-2-8-1v14c3-1 6-1 8 1 2-2 5-2 8-1V5c-3-1-6-1-8 1z"/><path d="M12 6v14"/></svg>'
a = s.index('      <button type="button" data-aba="scripts">'); b = s.index("</button>", a) + len("</button>\n")
bot_scripts = s[a:b]; s = s[:a] + s[b:]
a = s.index('      <button type="button" data-aba="ajuda">'); b = s.index("</button>", a) + len("</button>\n")
s = s[:a] + s[b:]
s = troca(s, '      <span class="side-grupo">Sistema</span>\n',
          '      <span class="side-grupo">Biblioteca</span>\n'
          '      <button type="button" data-aba="materiais">' + ico_doc + '<span>Materiais de venda</span></button>\n'
          + bot_scripts +
          '      <button type="button" data-aba="objecoes">' + ico_obj + '<span>Objeções</span></button>\n'
          '      <button type="button" data-aba="ajuda">' + ico_man + '<span>Manual de operação</span></button>\n'
          '      <span class="side-grupo">Sistema</span>\n')

# abas novas
s = troca(s, '    <!-- AJUDA -->',
          '    <!-- MATERIAIS -->\n    <section class="panel" data-panel="materiais" hidden><div id="bibMateriais" class="bib-col"></div></section>\n\n'
          '    <!-- OBJEÇÕES -->\n    <section class="panel" data-panel="objecoes" hidden>\n'
          '      <div class="toolbar"><input type="search" id="objBusca" placeholder="Buscar objeção…" aria-label="Buscar objeção" maxlength="60"></div>\n'
          '      <p class="muted bib-dica">Valide ("faz sentido", "entendo"), responda com um fato ou um número e termine com uma pergunta que leva ao próximo passo.</p>\n'
          '      <div id="bibObjecoes"></div>\n    </section>\n\n    <!-- AJUDA -->')
s = troca(s, '<div class="toolbar"><label class="inline-lbl">Preencher para<select id="scLead"><option value="">Nenhum lead (texto com campos)</option></select></label></div>',
          '<div class="toolbar"><label class="inline-lbl">Preencher para<select id="scLead"><option value="">Nenhum lead (texto com campos)</option></select></label>'
          '<input type="search" id="scBusca" placeholder="Buscar mensagem…" aria-label="Buscar mensagem" maxlength="60"></div>\n'
          '      <div class="bib-filtros" id="scCats" role="group" aria-label="Filtrar por etapa"></div>')

# manual de operação + resumo do playbook no lugar da ajuda antiga
man = md_html(open("manual/manual-de-operacao.md", encoding="utf-8").read())
pb = md_html(open("manual/playbook-resumo.md", encoding="utf-8").read())
a = s.index('<div id="hpLista">') + len('<div id="hpLista">'); b = s.index("\n      </div>\n      <p class=\"muted\" id=\"hpVazio\"", a)
s = s[:a] + "\n<h3 class=\"bib-grupo\">Manual de operação</h3>\n" + detalhes(man) + \
    "\n<h3 class=\"bib-grupo\">Playbook de vendas · resumo</h3>\n" + detalhes(pb, False) + "\n" + s[b:]
s = s.replace('placeholder="Buscar na ajuda…" aria-label="Buscar na ajuda"', 'placeholder="Buscar no manual…" aria-label="Buscar no manual"')

# planos atuais nos seletores
s = troca(s, '<label>Plano<select id="qPlano"><option>Essencial</option><option selected>Profissional</option><option>Premium</option></select></label>',
          '<label>Plano<select id="qPlano"><option>Cardápio Digital</option><option selected>Site Gastronômico</option><option>Digital Experience</option><option>Signature</option></select></label>')
s = troca(s, '<select id="fPlano"><option value="">—</option><option>Essencial</option><option>Profissional</option><option>Premium</option></select>',
          '<select id="fPlano"><option value="">—</option><option>Cardápio Digital</option><option>Site Gastronômico</option><option>Digital Experience</option><option>Signature</option></select>')
open(p, "w", encoding="utf-8").write(s)

# ---------------------------------------------------------------- painel.js
p = os.path.join(DEST, "painel.js")
j = open(p, encoding="utf-8").read()
a = j.index("const PLANOS={"); b = j.index("};", a) + 2
j = j[:a] + r"""const PLANOS={
  'Cardápio Digital':{impl:997,mens:149,prazo:'até 7 dias úteis',itens:[['Cardápio digital interativo com fotos, categorias e opcionais',1,697],['Pedido enviado pronto ao WhatsApp da casa',1,0],['QR Code para mesas e balcão + link para a bio',1,150],['Cadastro do cardápio pela nossa equipe',1,150]],incl:['Hospedagem e certificado de segurança','Ajustes de conteúdo e banners de datas comemorativas','Suporte pelo WhatsApp','Treinamento da equipe']},
  'Site Gastronômico':{impl:1497,mens:149,prazo:'até 7 dias úteis',itens:[['Site com a identidade da casa (modelo gastronômico)',1,897],['Cardápio com pedido no WhatsApp',1,300],['Domínio próprio com HTTPS',1,150],['QR Code e link para as redes',1,150]],incl:['Hospedagem e certificado de segurança','Ajustes de conteúdo e banners de datas comemorativas','Suporte pelo WhatsApp','Treinamento da equipe']},
  'Digital Experience':{impl:2997,mens:199,prazo:'até 7 dias úteis',itens:[['Site com a identidade da casa e cardápio com pedido',1,1497],['Painel de pedidos e rastreio do pedido',1,500],['Perfil da empresa no Google otimizado',1,300],['500 cartões de volta + display de balcão',1,250],['Campanha de lançamento (mensagens, post e stories)',1,250],['30 dias de acompanhamento',1,200]],incl:['Hospedagem e certificado de segurança','Ajustes de conteúdo e banners de datas comemorativas','Suporte pelo WhatsApp','Treinamento da equipe','Relatório de pedidos do canal próprio']},
  'Signature':{impl:0,mens:0,prazo:'definido no diagnóstico',itens:[['Imersão e estratégia',1,0],['Direção criativa e arquitetura',1,0],['Design e desenvolvimento exclusivos',1,0],['Refinamento e publicação',1,0]],incl:['Valores definidos depois do diagnóstico','Hospedagem e suporte conforme o projeto']}
};"""[0:] + j[b:]
# scripts: os da Biblioteca (os 7 primeiros mantêm o papel de cada etapa do funil)
a = j.index("const SCRIPTS=["); b = j.index("]];", a) + 3
j = j[:a] + "const SCRIPTS=(window.BC_SCRIPTS||[]).map(s=>[s.t,s.x,s.c||'',s.aviso||s.nota||'',s.tag||'']);" + j[b:]
j = troca(j, "const r={nome:primeiroNome(l.responsavel)||'[nome]',estabelecimento:l.nome||'[estabelecimento]',",
          "const r={nome:primeiroNome(l.responsavel)||'',estabelecimento:l.nome||'',")
j = troca(j, "return txt.replace(/\\[(nome|estabelecimento|data|dia|chave|marca|eu)\\]/g,(m,k)=>r[k])}",
          "return txt.replace(/\\[(nome|estabelecimento|loja|pizzaria|data|dia|chave|marca|eu)\\]/gi,(m,k)=>{k=k.toLowerCase();if(k==='loja'||k==='pizzaria')k='estabelecimento';return r[k]||m})}")
a = j.index("function renderScripts(){"); b = j.index("$('#scLead').addEventListener('change',renderScripts);", a)
j = j[:a] + r"""let scCat='';
function renderScripts(){const sel=$('#scLead'),l=L(sel.value),q=String(($('#scBusca')||{}).value||'').trim().toLowerCase();
  const cats=[...new Set(SCRIPTS.map(s=>s[2]))];
  $('#scCats').innerHTML=['',...cats].map(c=>`<button type="button" class="chip${c===scCat?' info':''}" data-cat="${esc(c)}">${esc(c||'Todas')}</button>`).join('');
  let html='',grupo=null;
  SCRIPTS.forEach((s,i)=>{if(scCat&&s[2]!==scCat)return;if(q&&!(s[0]+' '+s[1]).toLowerCase().includes(q))return;
    if(s[2]!==grupo){grupo=s[2];html+=`<h3 class="bib-grupo">${esc(grupo)}</h3>`}
    const txt=preencher(s[1],l),z=l?zapUrl(l.whatsapp,txt):'';
    html+=`<div class="box script"><div class="box-head"><b>${esc(s[0])}</b>${s[4]?`<span class="chip">${esc(s[4])}</span>`:''}</div>${s[3]?`<p class="bib-aviso">${esc(s[3])}</p>`:''}<pre id="sc${i}">${esc(txt)}</pre><div class="acoes-linha"><button class="btn small" data-copy="${i}" type="button">Copiar</button>${z?`<a class="btn zap small" href="${esc(z)}" target="_blank" rel="noopener noreferrer">Enviar para ${esc(primeiroNome(l.responsavel)||l.nome)}</a>`:''}</div></div>`});
  $('#scripts').innerHTML=html||'<p class="muted">Nenhuma mensagem com esse termo.</p>'}
$('#scBusca').addEventListener('input',renderScripts);
$('#scCats').addEventListener('click',e=>{const b=e.target.closest('[data-cat]');if(!b)return;scCat=b.dataset.cat;renderScripts()});
""" + j[b:]
# só a linha de sites: carrega filtrando e grava marcando
j = troca(j, "if(col==='leads')leads=arr;else orcs=arr;", "const minha=arr.filter(x=>x.linha==='sites');if(col==='leads')leads=minha;else orcs=minha;")
j = troca(j, "const doc=comHistorico(col,cur,Object.assign(limpaDoc(cur||{}),patch),acao);",
          "const doc=comHistorico(col,cur,Object.assign(limpaDoc(cur||{}),patch),acao);doc.linha='sites';")
# configuração própria (marca, metas, Pix) separada da plataforma
j = troca(j, "db.from('config').select('doc').eq('id','empresa')", "db.from('config').select('doc').eq('id','empresa-sites')")
j = troca(j, "db.from('config').upsert({id:'empresa',doc:d})", "db.from('config').upsert({id:'empresa-sites',doc:d})")
# a barra lateral e a aba do navegador são da holding; a marca do orçamento continua editável em Ajustes
j = troca(j, "function aplicaMarca(){document.querySelectorAll('.marca-nome').forEach(e=>e.textContent=cfg.marca||'Bistrô Connect');document.title='Painel · '+(cfg.marca||'Bistrô Connect')}",
          "function aplicaMarca(){document.title='CRM · Mr. Connect'}")
j = troca(j, "scripts:'Scripts de venda',", "scripts:'Scripts de venda',materiais:'Materiais de venda',objecoes:'Objeções e respostas',")
j = j.replace("ajuda:'Ajuda · como tudo funciona'", "ajuda:'Manual de operação'")
# planos nos dados de demonstração e nos padrões
j = j.replace("plano:'Essencial',implantacao:997,mensalidade:149", "plano:'Cardápio Digital',implantacao:997,mensalidade:149")
j = j.replace("plano:'Premium',implantacao:2497,mensalidade:299", "plano:'Digital Experience',implantacao:2997,mensalidade:199")
j = j.replace("plano:'Profissional',implantacao:1497,mensalidade:199", "plano:'Site Gastronômico',implantacao:1497,mensalidade:149")
j = j.replace("PLANOS.Profissional", "PLANOS['Site Gastronômico']").replace("PLANOS.Premium", "PLANOS['Digital Experience']").replace("PLANOS.Essencial", "PLANOS['Cardápio Digital']")
j = j.replace("plano:'Profissional'", "plano:'Site Gastronômico'").replace("plano:'Premium'", "plano:'Digital Experience'").replace("plano:'Essencial'", "plano:'Cardápio Digital'")
j = j.replace("o.plano||'Profissional'", "o.plano||'Site Gastronômico'")
j = j.replace("setPlano('Profissional')", "setPlano('Site Gastronômico')").replace("$('#qPlano').value='Profissional'", "$('#qPlano').value='Site Gastronômico'")
left = re.findall(r"Essencial|Profissional|Premium", j)
assert not left, [j[m.start()-80:m.end()+40] for m in re.finditer(r"Essencial|Profissional|Premium", j)][:3]
open(p, "w", encoding="utf-8").write(j)

# ---------------------------------------------------------------- estilos da biblioteca
css = r"""
/* ===== CRM Mr. Connect: marca e Biblioteca ===== */
.mc-marca{display:inline-flex;align-items:baseline;gap:.08em;font-family:Poppins,var(--f-display,sans-serif);font-size:22px;line-height:1.05;letter-spacing:-.01em;background:linear-gradient(180deg,#F3E2BF 0%,#D9B985 55%,#B8935A 100%);-webkit-background-clip:text;background-clip:text;color:transparent}
.mc-marca .mr{font-weight:800}
.mc-marca .cn{font-weight:300}
.mc-auth .mc-marca{font-size:34px}
.mc-tag{display:block;margin-top:4px;font-size:11px!important;letter-spacing:.32em;text-transform:none;color:#CDBB9B!important}
[data-tema="light"] .mc-marca,.side .mc-marca{filter:drop-shadow(0 1px 0 rgba(90,60,20,.25))}
.bib-col{display:flex;flex-direction:column;gap:16px}
.bib-tit{font-size:16px}
.bib-doc p{margin:0}
.bib-aviso{margin:0;padding:9px 12px;border-radius:10px;background:var(--warn-soft);color:var(--warn);font-size:13px;line-height:1.45}
.bib-pre{white-space:pre-wrap;font-family:var(--f-body);font-size:14px;margin:0 0 10px;padding:12px;background:var(--hover);border:1px solid var(--line);border-radius:10px}
.bib-grupo{grid-column:1/-1;margin:14px 0 2px;font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.bib-grupo:first-child{margin-top:0}
.bib-filtros{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 14px}
.bib-filtros .chip{cursor:pointer}
.bib-dica{margin:0 0 12px}
#hpLista h4{margin:14px 0 6px;font-size:14px}
#hpLista .tablewrap{margin:8px 0}
.bib-tarefas{list-style:none;padding-left:0}
.bib-tarefas li{margin:4px 0}
"""
open(os.path.join(DEST, "painel.css"), "a", encoding="utf-8").write(css)

subprocess.run(["python3", "ferramentas/csp.py", os.path.join(DEST, "index.html")], check=True)
print("CRM Mr. Connect montado em", os.path.relpath(DEST, RAIZ))
