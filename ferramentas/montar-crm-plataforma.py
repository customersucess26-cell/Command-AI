"""Copia o seu painel de leads e orçamentos (admin/ do site oficial) para plataforma/crm/.
Ele continua usando o Supabase do SITE OFICIAL, lido de window.BISTRO no assets/config.js da plataforma.
Rode de novo sempre que mudar algo em admin/:  python3 ferramentas/montar-crm-plataforma.py"""
import os, shutil, subprocess
DEST = "plataforma/crm"
shutil.rmtree(DEST, ignore_errors=True)
shutil.copytree("admin", DEST)
p = os.path.join(DEST, "index.html")
s = open(p, encoding="utf-8").read()
def troca(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)
# na plataforma o config.js tem a plataforma inteira: o painel não pode gerar um config.js só com o CRM
troca('''<p class="muted">Este navegador já está ligado ao painel. Para o <b>formulário e a Bia do site</b> também gravarem os leads, baixe o <code>config.js</code> e envie para a pasta <code>assets/</code> na Hostinger, substituindo o antigo.</p>
        <button class="btn big" type="button" id="btnBaixaCfg">Baixar config.js</button>''',
      '''<p class="muted">Este navegador já está ligado ao painel. Para o <b>formulário e a Bia da página de vendas</b> também gravarem os leads, preencha <code>supabaseUrl</code> e <code>supabaseKey</code> no bloco <code>window.BISTRO</code> do <code>assets/config.js</code> da plataforma, com estes mesmos dados.</p>
        <button class="btn big" type="button" id="btnBaixaCfg" hidden>Baixar config.js</button>''')
open(p, "w", encoding="utf-8").write(s)
subprocess.run(["python3", "ferramentas/csp.py", p], check=True)
print("CRM copiado para", DEST)
