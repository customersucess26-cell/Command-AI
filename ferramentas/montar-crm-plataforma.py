"""Copia o seu painel de leads e orçamentos (admin/ do site oficial) para plataforma/crm/.
Ele usa o mesmo Supabase da plataforma (window.BISTRO no assets/config.js aponta para o mesmo banco; tabelas em plataforma/supabase/03-crm.sql).
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
      '''<p class="muted">Este navegador já está ligado ao painel. Na plataforma, o formulário e a Bia da página de vendas gravam no mesmo banco e o <code>config.js</code> já está certo, então não é preciso baixar nada.</p>
        <button class="btn big" type="button" id="btnBaixaCfg" hidden>Baixar config.js</button>''')
open(p, "w", encoding="utf-8").write(s)
subprocess.run(["python3", "ferramentas/csp.py", p], check=True)
print("CRM copiado para", DEST)
