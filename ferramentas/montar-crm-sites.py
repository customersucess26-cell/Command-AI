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
          '<label>Plano<select id="qPlano"><optgroup label="Gastronomia · Bistrô Connect"><option>Cardápio Digital</option><option selected>Site Gastronômico</option><option>Digital Experience</option><option>Signature</option></optgroup><optgroup label="Outros nichos · Mr. Connect"><option>Página comercial</option><option>Site institucional</option></optgroup></select></label>\n            <label>Marca da proposta<select id="qMarca"><option value="bistro">Bistrô Connect (gastronomia)</option><option value="mc">Mr. Connect (outros nichos)</option></select></label>')
s = troca(s, '<select id="fPlano"><option value="">—</option><option>Essencial</option><option>Profissional</option><option>Premium</option></select>',
          '<select id="fPlano"><option value="">—</option><option>Cardápio Digital</option><option>Site Gastronômico</option><option>Digital Experience</option><option>Signature</option><option>Página comercial</option><option>Site institucional</option></select>')
open(p, "w", encoding="utf-8").write(s)

# ---------------------------------------------------------------- painel.js
p = os.path.join(DEST, "painel.js")
j = open(p, encoding="utf-8").read()
a = j.index("const PLANOS={"); b = j.index("};", a) + 2
j = j[:a] + r"""const PLANOS={
  'Cardápio Digital':{impl:997,mens:149,prazo:'até 7 dias úteis',itens:[['Cardápio digital interativo com fotos, categorias e opcionais',1,697],['Pedido enviado pronto ao WhatsApp da casa',1,0],['QR Code para mesas e balcão + link para a bio',1,150],['Cadastro do cardápio pela nossa equipe',1,150]],incl:['Hospedagem e certificado de segurança','Ajustes de conteúdo e banners de datas comemorativas','Suporte pelo WhatsApp','Treinamento da equipe']},
  'Site Gastronômico':{impl:1497,mens:149,prazo:'até 7 dias úteis',itens:[['Site com a identidade da casa (modelo gastronômico)',1,897],['Cardápio com pedido no WhatsApp',1,300],['Domínio próprio com HTTPS',1,150],['QR Code e link para as redes',1,150]],incl:['Hospedagem e certificado de segurança','Ajustes de conteúdo e banners de datas comemorativas','Suporte pelo WhatsApp','Treinamento da equipe']},
  'Digital Experience':{impl:2997,mens:199,prazo:'até 7 dias úteis',itens:[['Site com a identidade da casa e cardápio com pedido',1,1497],['Painel de pedidos e rastreio do pedido',1,500],['Perfil da empresa no Google otimizado',1,300],['500 cartões de volta + display de balcão',1,250],['Campanha de lançamento (mensagens, post e stories)',1,250],['30 dias de acompanhamento',1,200]],incl:['Hospedagem e certificado de segurança','Ajustes de conteúdo e banners de datas comemorativas','Suporte pelo WhatsApp','Treinamento da equipe','Relatório de pedidos do canal próprio']},
  'Página comercial':{impl:2000,mens:149,prazo:'até 6 dias úteis',itens:[['Página comercial premium — Design, texto de vendas, versão celular e integrações',1,1500],['Painel de leads — Funil, agenda, histórico e login seguro',1,500]],incl:['Hospedagem e verificação mensal','Até 2 ajustes de conteúdo por mês','Suporte pelo WhatsApp']},
  'Site institucional':{impl:0,mens:0,prazo:'até 10 dias úteis',itens:[['Site institucional sob medida — Design, textos, versão celular e integrações',1,0]],incl:['Hospedagem e verificação mensal','Até 2 ajustes de conteúdo por mês','Suporte pelo WhatsApp']},
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


# ---------------------------------------------------------------- plano de negócio da holding (sem a oferta antiga)
p2 = os.path.join(DEST, "index.html")
h = open(p2, encoding="utf-8").read()
h = re.sub(r'<a class="btn link small" href="https://claude\.ai/code/artifact/[^"]*" target="_blank" rel="noopener noreferrer">Abrir plano completo ↗</a>',
           '<button class="btn link small" type="button" data-aba="ajuda">Abrir o manual de operação</button>', h)
a = h.index('      <h2 class="h-sec">Plano de 90 dias</h2>'); b = h.index('    </section>', a)
h = h[:a] + """      <h2 class="h-sec">Plano dos primeiros 30 dias</h2>
      <div class="steps90">
        <div class="box"><span class="tag">Dias 1 a 3</span><b>Preparação</b><ul class="tight"><li>Contrato de 1 página e link de pagamento</li><li>Calculadora da comissão impressa e no celular</li><li>3 modelos de prévia prontos</li><li>100 leads pontuados no CRM</li></ul></div>
        <div class="box"><span class="tag">Semana 1</span><b>Lista A presencial</b><ul class="tight"><li>Leads da lista A com prévia e visita</li><li>20 abordagens por dia útil</li><li>8 demonstrações</li></ul></div>
        <div class="box"><span class="tag">Semana 2</span><b>Volume</b><ul class="tight"><li>Mais 100 leads</li><li>Cadência de 7 toques rodando</li><li>12 demonstrações</li><li>Primeiros sites em produção</li></ul></div>
        <div class="box"><span class="tag">Semanas 3 e 4</span><b>Prova e indicação</b><ul class="tight"><li>Primeiros sites no ar e print dos pedidos diretos</li><li>Pedido de indicação a cada cliente</li><li>Cidades vizinhas por videochamada</li><li>Fechar o mês e medir as taxas do funil</li></ul></div>
      </div>
      <div class="box"><div class="box-head"><h2>Rotina de um dia de vendas</h2></div><table class="data compacta"><tbody>
        <tr><td><b>8h às 10h</b></td><td>Prospecção: 20 abordagens com prévia, sem interrupção</td></tr>
        <tr><td><b>10h às 11h30</b></td><td>Produção das prévias do dia seguinte</td></tr>
        <tr><td><b>11h30 às 14h</b></td><td>Entregas e implantação (o restaurante está no pico, não aborde)</td></tr>
        <tr><td><b>14h às 17h</b></td><td>Visitas e demonstrações</td></tr>
        <tr><td><b>17h às 18h</b></td><td>Follow-ups, CRM atualizado e plano de amanhã</td></tr></tbody></table></div>
""" + h[b:]
open(p2, "w", encoding="utf-8").write(h)
j = open(os.path.join(DEST, "painel.js"), encoding="utf-8").read()
j = troca(j, "O ${esc(cfg.marca||'Bistrô Connect')} vende cardápio digital com pedido direto no WhatsApp para padarias, cafés e restaurantes de Ponta Grossa, cobrando implantação + mensalidade, sem comissão por pedido.",
          "A Mr. Connect, holding da ${esc(cfg.marca||'Bistrô Connect')}, vende presença digital para restaurantes: Site Gastronômico, Digital Experience, projetos Signature e Cardápio Digital, cobrando implantação + mensalidade, sem comissão por pedido.")
j = troca(j, "<td>${brl0(p.impl)}</td><td>${brl0(p.mens)}/mês</td>", "<td>${p.impl?brl0(p.impl):'Sob orçamento'}</td><td>${p.mens?brl0(p.mens)+'/mês':'Sob orçamento'}</td>")
open(os.path.join(DEST, "painel.js"), "w", encoding="utf-8").write(j)
# ---------------------------------------------------------------- PROPOSTA Mr. Connect + tema (acrescentado ao montador)
shutil.copy("paineis/crm-sites/proposta.js", os.path.join(DEST, "proposta.js"))
open(os.path.join(DEST, "painel.css"), "a", encoding="utf-8").write(open("paineis/crm-sites/tema.css", encoding="utf-8").read())
p3 = os.path.join(DEST, "index.html")
h = open(p3, encoding="utf-8").read()
h = troca(h, '<script src="biblioteca.js" defer></script>', '<script src="proposta.js" defer></script>\n<script src="biblioteca.js" defer></script>')
h = troca(h, '<h2 id="qTitulo">Novo orçamento</h2>', '<h2 id="qTitulo">Nova proposta</h2>')
h = troca(h, '<label class="full inline"><input type="checkbox" id="qLanc"> Oferta de lançamento (50% na implantação, em troca de depoimento)</label>',
          '<label class="full inline" hidden><input type="checkbox" id="qLanc"> Oferta de lançamento</label>')
h = troca(h, 'value="5 dias úteis após o recebimento do material"', 'value="até 7 dias úteis após o recebimento dos materiais"')
h = troca(h, '            <div class="full"><span class="lbl-form">Itens da implantação</span>',
 '            <label class="full">Título da proposta<input id="qTit" maxlength="90"></label>\n'
 '            <label class="full">Apresentação<textarea id="qIntro" maxlength="400"></textarea></label>\n'
 '            <div class="full"><span class="lbl-form">Prévia do projeto na capa (opcional)</span><div class="q-prev"><input type="file" id="qPrevArq" accept="image/*" aria-label="Imagem da prévia"><img id="qPrevImg" alt="" hidden><button type="button" class="btn small" id="qPrevTirar" hidden>Tirar imagem</button></div></div>\n'
 '            <label class="full">O que está incluído <span class="muted fino">(uma linha por coluna: Título: item; item; item)</span><textarea id="qIncl" maxlength="900"></textarea></label>\n'
 '            <div class="full"><span class="lbl-form">Itens do investimento <span class="muted fino">(use " — " para pôr uma descrição embaixo do item)</span></span>')
h = troca(h, '            <label>Validade (dias)<input id="qVal"',
 '            <label>Parcelas no cartão<input id="qParc" inputmode="numeric" maxlength="2" value="3"></label>\n'
 '            <label class="inline"><input type="checkbox" id="qCuidOpc"> Plano de cuidado opcional</label>\n'
 '            <label>Validade (dias)<input id="qVal"')
h = troca(h, '            <label class="full">Observações<textarea id="qObs"',
 '            <label class="full">Como acontece <span class="muted fino">(uma linha por etapa: Quando | Etapa | Descrição)</span><textarea id="qEtapas" maxlength="600"></textarea></label>\n'
 '            <label class="full">Garantia<input id="qGar" maxlength="220"></label>\n'
 '            <label class="full">Observações<textarea id="qObs"')
h = troca(h, '<button type="submit" class="btn primary" id="qSalvar">Salvar orçamento</button>', '<button type="submit" class="btn primary" id="qSalvar">Salvar proposta</button>')
h = troca(h, '<div class="sheet" id="sheet"></div>', '<div class="sheet mc" id="sheet"></div>')
h = h.replace('<h2>Orçamentos enviados</h2>', '<h2>Propostas enviadas</h2>')
open(p3, "w", encoding="utf-8").write(h)

j = open(os.path.join(DEST, "painel.js"), encoding="utf-8").read()
j = troca(j, "function nextNumero(){const y=hoje().slice(0,4),ns=orcs.filter(o=>String(o.numero||'').startsWith('BT-'+y))",
             "function nextNumero(){const y=hoje().slice(0,4),ns=orcs.filter(o=>/^(MC|BT)-/.test(String(o.numero||''))&&String(o.numero).slice(3,7)===y)")
j = troca(j, "return 'BT-'+y+'-'+String(", "return 'MC-'+y+'-'+String(")
# qData: campos novos da proposta
j = troca(j, "obs:$('#qObs').value.trim(),leadId:$('#qLead').value||''}}",
          "obs:$('#qObs').value.trim(),leadId:$('#qLead').value||'',titulo:$('#qTit').value.trim(),intro:$('#qIntro').value.trim(),incluido:$('#qIncl').value.trim(),etapas:$('#qEtapas').value.trim(),garantia:$('#qGar').value.trim(),parcelas:Math.min(12,Math.max(1,num($('#qParc').value)||3)),cuidadoOpc:$('#qCuidOpc').checked,previa:qPrev||'',marca:$('#qMarca').value||'bistro'}}")
j = troca(j, "let db=null, demo=false,", "let qPrev='';\nlet db=null, demo=false,")
# plano escolhido preenche os textos padrão da proposta
j = troca(j, "function setPlano(p){const P=PLANOS[p];qItems=P.itens.map(i=>({d:i[0],q:i[1],v:i[2]}));$('#qMens').value=P.mens;drawItems();drawSheet()}",
          "function setPlano(p){const P=PLANOS[p];qItems=P.itens.map(i=>({d:i[0],q:i[1],v:i[2]}));$('#qMens').value=P.mens;$('#qPrazo').value=P.prazo?P.prazo+' após o recebimento dos materiais':$('#qPrazo').value;const M=(window.MC_PROPOSTA||{}),D=(M.planos||{})[p]||{};$('#qTit').value=D.titulo||'';$('#qIntro').value=D.intro||'';$('#qIncl').value=D.incluido||'';$('#qEtapas').value=D.etapas||'';$('#qGar').value=M.garantia||'';$('#qMarca').value=(M.marcaDoPlano||{})[p]||'bistro';$('#qCuidOpc').checked=((M.marcaDoPlano||{})[p]==='mc');drawItems();drawSheet()}")
# folha nova
a = j.index("function drawSheet(){"); b = j.index("function fitSheet(){", a)
j = j[:a] + r"""function mcLinhas(t){return String(t||'').split('\n').map(x=>x.trim()).filter(Boolean)}
function drawSheet(){if(!$('#sheet'))return;const o=qData(),P=PLANOS[o.plano]||PLANOS['Site Gastronômico'],M=window.MC_PROPOSTA||{},mk=esc(cfg.marca||'Bistrô Connect');
  const est=o.est||'sua casa',quem=o.resp||o.est||'Cliente',intro=esc((o.intro||'').replace(/\{est\}/g,est));
  const MK=((M.marcas||{})[o.marca]||(M.marcas||{}).mc||{nome:'Mr. Connect',slogan:'A evolução digital da sua marca.'}),nomeMk=esc(MK.nome);
  const wm=(s)=>MK.logo?`<div class="wm wm-img"><img src="${esc(MK.logo)}" alt="${nomeMk}" style="height:${Math.round(s*1.6)}px"></div>`:`<div class="wm" style="font-size:${s}px"><span class="mr">Mr.</span><span class="cn">Connect</span><small>${esc(MK.slogan)}</small></div>`;
  const cols=mcLinhas(o.incluido).slice(0,3).map(l=>{const k=l.indexOf(':'),t=k>0?l.slice(0,k):'',it=(k>0?l.slice(k+1):l).split(';').map(x=>x.trim()).filter(Boolean);return `<div><h3>${esc(t)}</h3><ul>${it.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div>`}).join('');
  const etapas=mcLinhas(o.etapas).slice(0,4).map(l=>{const p=l.split('|').map(x=>x.trim());return `<div><small>${esc(p[0]||'')}</small><b>${esc(p[1]||'')}</b><span>${esc(p[2]||'')}</span></div>`}).join('');
  const itens=o.itens.map(i=>{const k=String(i.d||'').split(' — '),q=i.q||0;return `<tr><td><b>${esc(k[0])}</b>${k[1]?`<small>${esc(k.slice(1).join(' — '))}</small>`:''}</td><td class="n">${esc(q)}</td><td class="n">${i.v?brl(i.v):'incluso'}</td><td class="n">${i.v?brl(q*i.v):'—'}</td></tr>`}).join('');
  const tot=o.totalImpl,par=o.parcelas||3,sob=!tot;
  const previa=o.previa?`<div class="previa"><div class="tela"><div class="bar"><i></i><i></i><i></i></div><div class="shot"><img src="${esc(o.previa)}" alt=""></div></div></div>`:'';
  const rod=`<div class="rod"><span><b>${nomeMk}</b> · ${esc(MK.slogan)}</span><span>WhatsApp ${esc(cfg.whats)}${cfg.site?' · '+esc(cfg.site):''}</span></div>`;
  $('#sheet').innerHTML=`
  <div class="pg">
    <div class="capa${previa?'':' sem-img'}">
      <div class="topo">${wm(30)}<div class="num"><b>${esc(o.numero)}</b><span>Emitida em ${fmtDataLonga(o.data)}</span><span>Válida até ${fmtDataLonga(o.validoAte)}</span></div></div>
      <div class="capa-txt"><div class="para">Proposta para ${esc(quem)}</div><h1>${esc(o.titulo||'Proposta '+o.plano)}</h1><p>${intro}</p></div>
      ${previa}
    </div>
    <div class="corpo">
      <div class="quem">
        <div><div class="lbl">Para</div><b>${esc(o.resp||o.est||'Nome do cliente')}</b>${o.resp&&o.est?`<span>${esc(o.est)}</span>`:''}${o.whats?`<span>WhatsApp ${esc(o.whats)}</span>`:''}${o.local?`<span>${esc(o.local)}</span>`:''}</div>
        <div><div class="lbl">De</div><b>${esc(cfg.nome||'Adilson')} · ${nomeMk}</b><span>WhatsApp ${esc(cfg.whats)}</span>${cfg.email?`<span>${esc(cfg.email)}</span>`:''}<span>${esc(cfg.cidade||'')}</span>${cfg.doc?`<span>${esc(cfg.doc)}</span>`:''}</div>
      </div>
      <div class="tit"><h2>O que está incluído</h2></div>
      <div class="incl">${cols}</div>
    </div>
    ${rod}
  </div>
  <div class="pg">
    <div class="faixa">${wm(22)}<div class="ref">Proposta<b>${esc(o.numero)}</b></div></div>
    <div class="corpo">
      <div class="tit" style="margin-top:6px"><h2>Investimento</h2></div>
      <table class="itens"><thead><tr><th>Item</th><th class="n">Qtd.</th><th class="n">Valor</th><th class="n">Total</th></tr></thead><tbody>${itens}${o.desconto?`<tr class="desc"><td><b style="color:#2F7A55">Desconto (${esc(o.descPct)}%)</b></td><td></td><td></td><td class="n">− ${brl(o.desconto)}</td></tr>`:''}</tbody></table>
      <div class="inv">
        <div>
          ${o.mens?`<div class="cuidado"><div class="cab"><b>${esc(M.cuidado||'Plano de cuidado')}${o.cuidadoOpc?' (opcional)':''}</b><strong>${brl(o.mens)}/mês</strong></div><ul>${P.incl.map(x=>`<li>${esc(x)}</li>`).join('')}</ul><div class="obs">${o.cuidadoOpc?'A mensalidade é opcional e começa no mês seguinte à publicação.':'Começa quando o projeto vai ao ar, com contrato mínimo de 6 meses.'}</div></div>`:''}
          <div class="pag"><p><b>Pagamento:</b> ${esc(o.pag)}${cfg.pix?' · Chave Pix: '+esc(cfg.pix):''}</p><p class="m"><b>Prazo:</b> ${esc(o.prazo)}.</p>${o.obs?`<p class="m">${esc(o.obs)}</p>`:''}</div>
        </div>
        <div class="total"><div class="k">Investimento total</div><div class="v">${sob?'Sob orçamento':brl(tot)}</div>${sob?'':`<div class="l"><span>À vista no Pix</span><b>${brl(tot)}</b></div><div class="l"><span>Em duas partes</span><b>2 × ${brl(tot/2)}</b></div><div class="l"><span>No cartão</span><b>${par} × ${brl(tot/par)}</b></div>`}</div>
      </div>
      <div class="tit"><h2>Como acontece</h2></div>
      <div class="etapas">${etapas}</div>
      ${o.garantia?`<div class="garantia"><i>✓</i><div><b>Garantia de entrega</b><span>${esc(o.garantia)}</span></div></div>`:''}
      <div class="assin"><div>${esc(cfg.nome||'Adilson')} · ${nomeMk}</div><div>${esc(o.resp||o.est||'Cliente')} · aceite e data</div></div>
    </div>
    ${rod}
  </div>`;
  fitSheet()}
""" + j[b:]
# abrir proposta salva: campos novos
j = troca(j, "$('#qObs').value=o.obs||'';drawItems();drawSheet();abrirAba('orcamentos')}",
          "$('#qObs').value=o.obs||'';const D=((window.MC_PROPOSTA||{}).planos||{})[o.plano]||{};$('#qTit').value=o.titulo||D.titulo||'';$('#qIntro').value=o.intro||D.intro||'';$('#qIncl').value=o.incluido||D.incluido||'';$('#qEtapas').value=o.etapas||D.etapas||'';$('#qGar').value=o.garantia!=null?o.garantia:((window.MC_PROPOSTA||{}).garantia||'');$('#qParc').value=o.parcelas||3;$('#qCuidOpc').checked=!!o.cuidadoOpc;$('#qMarca').value=o.marca||(((window.MC_PROPOSTA||{}).marcaDoPlano||{})[o.plano])||'bistro';mcPrev(o.previa||'');drawItems();drawSheet();abrirAba('orcamentos')}")
j = troca(j, "function novoOrc(leadId){qEdit=null;$('#qForm').reset();$('#qTitulo').textContent='Novo orçamento';",
          "function mcPrev(u){qPrev=u||'';const im=$('#qPrevImg');im.hidden=!qPrev;if(qPrev)im.src=qPrev;$('#qPrevTirar').hidden=!qPrev;$('#qPrevArq').value=''}\nfunction novoOrc(leadId){qEdit=null;$('#qForm').reset();mcPrev('');$('#qTitulo').textContent='Nova proposta';")
j = troca(j, "$('#qTitulo').textContent='Orçamento '+o.numero;$('#qLead')", "$('#qTitulo').textContent='Proposta '+o.numero;$('#qLead')")
j = troca(j, "['qEst','qResp','qWhats','qLocal','qMens','qDesc','qVal','qPrazo','qPag','qObs'].forEach(id=>$('#'+id).addEventListener('input',drawSheet));",
          "['qEst','qResp','qWhats','qLocal','qMens','qDesc','qVal','qPrazo','qPag','qObs','qTit','qIntro','qIncl','qEtapas','qGar','qParc'].forEach(id=>$('#'+id).addEventListener('input',drawSheet));\n$('#qCuidOpc').addEventListener('change',drawSheet);\n$('#qMarca').addEventListener('change',drawSheet);\n"
          "$('#qPrevTirar').addEventListener('click',()=>{mcPrev('');drawSheet()});\n"
          "$('#qPrevArq').addEventListener('change',e=>{const f=e.target.files&&e.target.files[0];if(!f)return;if(!/^image\\//.test(f.type)){toast('Escolha uma imagem');return}const r=new FileReader();r.onload=()=>{const im=new Image();im.onload=()=>{const W=Math.min(1100,im.width),H=Math.round(im.height*W/im.width),c=document.createElement('canvas');c.width=W;c.height=H;c.getContext('2d').drawImage(im,0,0,W,H);mcPrev(c.toDataURL('image/jpeg',0.82));drawSheet()};im.src=r.result};r.readAsDataURL(f)});")
j = troca(j, "nome=('Orcamento '+o.numero+' - '+(o.est||'cliente'))", "nome=('Proposta '+o.numero+' - '+(o.resp||o.est||'cliente'))")
j = troca(j, "return `Olá${o.resp?', '+primeiroNome(o.resp):''}! Segue o orçamento ${o.numero} do cardápio digital da ${o.est||'sua casa'} (plano ${o.plano}).",
          "return `Olá${o.resp?', '+primeiroNome(o.resp):''}! Segue a proposta ${o.numero} do projeto da ${o.est||'sua casa'} (${o.plano}).")
j = troca(j, "${cfg.nome||'Adilson'} · ${cfg.marca||'Bistrô Connect'}`}", "${cfg.nome||'Adilson'} · '+((o.marca==='mc')?'Mr. Connect':'Bistrô Connect')+'`}")
open(os.path.join(DEST, "painel.js"), "w", encoding="utf-8").write(j)


# PDF da proposta: uma imagem por página A4 (sem sobra de página em branco)
j = open(os.path.join(DEST, "painel.js"), encoding="utf-8").read()
j = troca(j, "const canvas=await html2canvas($('#sheet'),{scale:2,backgroundColor:'#ffffff',useCORS:true,logging:false});s.style.transform=prev;",
          "const pgs=[...document.querySelectorAll('#sheet .pg')];if(pgs.length){const {jsPDF}=window.jspdf,pdf=new jsPDF({unit:'mm',format:'a4'});for(let i=0;i<pgs.length;i++){const c=await html2canvas(pgs[i],{scale:2,backgroundColor:'#ffffff',useCORS:true,logging:false});if(i)pdf.addPage();pdf.addImage(c.toDataURL('image/jpeg',0.92),'JPEG',0,0,210,297)}s.style.transform=prev;const o=qData(),nome=('Proposta '+o.numero+' - '+(o.resp||o.est||'cliente')).replace(/[\\\\/:*?\"<>|]/g,'')+'.pdf';pdf.save(nome);st.textContent='PDF baixado: '+nome;fitSheet();btn.disabled=false;return}\n    const canvas=await html2canvas($('#sheet'),{scale:2,backgroundColor:'#ffffff',useCORS:true,logging:false});s.style.transform=prev;")
j = j.replace("orcamentos:'Orçamentos'", "orcamentos:'Propostas'")
open(os.path.join(DEST, "painel.js"), "w", encoding="utf-8").write(j)
h = open(os.path.join(DEST, "index.html"), encoding="utf-8").read()
h = troca(h, "<span>Orçamentos</span>", "<span>Propostas</span>")
h = h.replace('>+ Orçamento<', '>+ Proposta<')
open(os.path.join(DEST, "index.html"), "w", encoding="utf-8").write(h)
subprocess.run(["python3", "ferramentas/csp.py", os.path.join(DEST, "index.html")], check=True)
print("CRM Mr. Connect montado em", os.path.relpath(DEST, RAIZ))
