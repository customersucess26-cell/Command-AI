#!/usr/bin/env python3
"""Gera a entrega de um cliente a partir de um modelo de site premium, ligado ao motor Bistrô Connect.

Uso:
  python3 ferramentas/novo-cliente.py --modelo hamburgueria --cliente "Forno do Zé"
  python3 ferramentas/novo-cliente.py --dados clientes/forno-do-ze.json            (dados do briefing)
  opções: --slug forno-do-ze  --whatsapp 42999998888  --dominio https://fornodoze.com.br
          --fotos pasta/com/fotos  --caminho /   --saida entregas  --sem-zip

O que sai em entregas/<slug>/site (e entregas/<slug>.zip), pronto para subir na public_html do cliente:
  index.html + img/          o modelo, sem editar o HTML (tudo que muda está em assets/config.js)
  assets/config.js           marca, textos, fotos, contato, slug da loja e o motor (chave pública)
  assets/motor.js, marca.js  ligação com o banco da plataforma e aplicação da marca
  pedido.html + pedido.php   acompanhamento do pedido no domínio do cliente (/p/<código>)
  admin/                     painel completo (pedidos, cardápio, clientes, financeiro, WhatsApp, cupons, mesas)
  .htaccess                  segurança e o link curto /p/<código>

O motor (URL e chave anon do Supabase da plataforma) vem de clientes/motor.json, se existir,
ou de plataforma/assets/config.js. A chave é a pública (anon); nunca use a service_role.
"""
import argparse, json, os, re, shutil, subprocess, sys, unicodedata, zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELOS = {
    "hamburgueria": "sites/hamburgueria-bruto",
    "pizzaria": "sites/pizzaria-fornalha",
    "restaurante": "sites/ambar",
    "padaria": "sites/padaria-cafe",
}
PRONTOS = {"hamburgueria"}   # modelos já ligados ao motor e à marca única (os outros entram nas próximas etapas)


def slugify(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t)).strip("-")[:60]


def le_motor():
    p = os.path.join(RAIZ, "clientes", "motor.json")
    if os.path.exists(p):
        m = json.load(open(p, encoding="utf-8"))
        return m.get("supabaseUrl", ""), m.get("supabaseKey", ""), m.get("plataforma", "")
    txt = open(os.path.join(RAIZ, "plataforma/assets/config.js"), encoding="utf-8").read()
    u = re.search(r'supabaseUrl:\s*"([^"]*)"', txt)
    k = re.search(r'supabaseKey:\s*"([^"]*)"', txt)
    s = re.search(r'\bsite:\s*"([^"]*)"', txt)
    return (u.group(1) if u else ""), (k.group(1) if k else ""), (s.group(1) if s else "")


def js(v):
    return json.dumps(v, ensure_ascii=False, indent=2).replace("\n", "\n  ")


def escreve_config(dest, d, url, chave, plat=""):
    marca = {"titulo": "", "descricao": "", "logo": "", "corNavegador": "", "cores": {}, "fontes": {}}
    marca.update(d.get("marca") or {})
    contato = {"endereco": "", "horario": "", "instagram": "", "whatsappTexto": ""}
    contato.update(d.get("contato") or {})
    txt = f'''/* Configuração do site {d["nome"]} · tudo que muda de um cliente para outro fica AQUI. O HTML do modelo não é editado.
   Este arquivo é público: só a chave "anon" do Supabase, nunca a "service_role". Gerado por ferramentas/novo-cliente.py */

/* Motor Bistrô Connect (banco da plataforma). Vazio = modo demonstração: cardápio do próprio site e pedido só pelo WhatsApp. */
window.BC = {{
  supabaseUrl: {json.dumps(url)},
  supabaseKey: {json.dumps(chave)},
  site: {json.dumps(d.get("dominio", "").rstrip("/"))},
  plataforma: {json.dumps(plat.rstrip("/"))}   // endereço da plataforma (para fotos cadastradas com caminho dela)
}};

window.LOJA = {{
  slug: {json.dumps(d["slug"])},
  nome: {json.dumps(d["nome"], ensure_ascii=False)},
  whatsapp: {json.dumps(d.get("whatsapp", ""))},
  cor: {json.dumps(d.get("cor", "#C9A35B"))},
  recursos: {{ pedidos: true }},
  marca: {js(marca)},
  textos: {js(d.get("textos") or {})},
  imagens: {js(d.get("imagens") or {})},
  contato: {js(contato)},
  ocultar: {js(d.get("ocultar") or [])}
}};
'''
    open(os.path.join(dest, "assets/config.js"), "w", encoding="utf-8").write(txt)


def copia_rastreio(dest, d, caminho):
    pl = os.path.join(RAIZ, "plataforma")
    h = open(os.path.join(pl, "pedido.html"), encoding="utf-8").read()
    nome = d["nome"]
    h = h.replace('src="/assets/', f'src="{caminho}assets/').replace('href="/"', f'href="{caminho}"')
    h = re.sub(r'<img src="[^"]*logo-bistro-connect[^"]*" alt="Bistrô Connect">',
               '<b class="marca-nome">' + re.sub(r"[<>&\"]", "", nome) + '</b>', h)
    h = re.sub(r'<p class="rod"><b>Bistrô Connect</b>[^<]*</p>',
               '<p class="rod"><b>' + re.sub(r"[<>&\"]", "", nome) + '</b>Obrigado pela preferência.</p>', h)
    host = re.sub(r"^https?://", "", d.get("dominio", "")).strip("/") or ""
    h = h.replace('<span id="dominio">bistroconnect.com.br</span>', '<span id="dominio">' + re.sub(r"[^\w.-]", "", host) + '</span>')
    if not host: h = h.replace('<span class="dom">', '<span class="dom" hidden>', 1)
    h = h.replace("</style>", ".faixa .marca-nome{font:700 15px/1 var(--f-display,inherit);letter-spacing:.04em;color:#fff}\n</style>", 1)
    open(os.path.join(dest, "pedido.html"), "w", encoding="utf-8").write(h)
    p = open(os.path.join(pl, "assets/pedido.js"), encoding="utf-8").read()
    p = p.replace('if (p.slug && /^[a-z0-9-]{3,40}$/.test(p.slug)) $("voltar").href = "/l/" + p.slug;', "")
    open(os.path.join(dest, "assets/pedido.js"), "w", encoding="utf-8").write(p)
    php = open(os.path.join(pl, "pedido.php"), encoding="utf-8").read()
    nm = nome.replace("\\", "").replace("'", "\\'")
    php = php.replace("'Bistrô Connect'", f"'{nm}'").replace('content="Bistrô Connect"', 'content="' + nome.replace('"', "") + '"')
    php = php.replace("'/assets/img/og-bistro-connect.jpg'", f"'{caminho}img/hero.jpg'")
    open(os.path.join(dest, "pedido.php"), "w", encoding="utf-8").write(php)
    shutil.copy(os.path.join(pl, "pedido-lib.php"), os.path.join(dest, "pedido-lib.php"))


def copia_painel(dest, d):
    pl = os.path.join(RAIZ, "plataforma")
    adm = os.path.join(dest, "admin")
    shutil.rmtree(adm, ignore_errors=True)
    os.makedirs(adm)
    for f in ("painel.css", "painel.js"):
        shutil.copy(os.path.join(pl, "painel", f), adm)
    h = open(os.path.join(pl, "painel/index.html"), encoding="utf-8").read()
    h = h.replace('<script src="../assets/exemplo.js?v=20261030b" defer></script>\n', "")
    h = h.replace('<p class="muted fino centro">Ainda não tem loja? <a href="../index.html#contato">Peça sua vaga</a></p>', '<p class="muted fino centro">Acesso da equipe de ' + re.sub(r"[<>&]", "", d["nome"]) + '.</p>')
    h = h.replace('<b class="loja-nome">Minha loja</b>', '<b class="loja-nome">' + re.sub(r"[<>&]", "", d["nome"]) + '</b>')
    h = h.replace("<title>Painel · Bistrô Connect</title>", "<title>Painel · " + re.sub(r"[<>&]", "", d["nome"]) + "</title>")
    open(os.path.join(adm, "index.html"), "w", encoding="utf-8").write(h)
    os.makedirs(os.path.join(dest, "assets/vendor"), exist_ok=True)
    for f in os.listdir(os.path.join(pl, "assets/vendor")):
        shutil.copy(os.path.join(pl, "assets/vendor", f), os.path.join(dest, "assets/vendor", f))
    shutil.copy(os.path.join(RAIZ, "admin/.htaccess"), os.path.join(adm, ".htaccess"))


def escreve_htaccess(dest):
    h = open(os.path.join(RAIZ, ".htaccess"), encoding="utf-8").read()
    regra = "\n# Link curto de acompanhamento do pedido: /p/<código> abre pedido.html com a prévia certa no WhatsApp\nRewriteRule ^p/([a-f0-9]{16})/?$ pedido.php?c=$1 [L,QSA]\n"
    h = h.replace("RewriteEngine On\n", "RewriteEngine On\n" + regra, 1)
    open(os.path.join(dest, ".htaccess"), "w", encoding="utf-8").write(h)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--modelo", choices=sorted(MODELOS))
    ap.add_argument("--cliente")
    ap.add_argument("--slug")
    ap.add_argument("--whatsapp", default="")
    ap.add_argument("--dominio", default="")
    ap.add_argument("--dados", help="JSON do briefing (nome, modelo, slug, whatsapp, dominio, marca, textos, imagens, contato, ocultar)")
    ap.add_argument("--fotos", help="pasta com as fotos do cliente (vão para img/cliente/)")
    ap.add_argument("--caminho", default="/", help="pasta do site no domínio (padrão: raiz /)")
    ap.add_argument("--saida", default="entregas")
    ap.add_argument("--sem-zip", action="store_true")
    a = ap.parse_args()

    d = {}
    if a.dados:
        d = json.load(open(a.dados, encoding="utf-8"))
    d["modelo"] = a.modelo or d.get("modelo")
    d["nome"] = a.cliente or d.get("nome")
    if not d["modelo"] or not d["nome"]:
        sys.exit("Informe --modelo e --cliente (ou um --dados com modelo e nome).")
    if d["modelo"] not in PRONTOS:
        sys.exit(f"O modelo '{d['modelo']}' ainda não está ligado ao motor. Prontos: {', '.join(sorted(PRONTOS))}.")
    d["slug"] = slugify(a.slug or d.get("slug") or d["nome"])
    if a.whatsapp: d["whatsapp"] = re.sub(r"\D", "", a.whatsapp)
    if a.dominio: d["dominio"] = a.dominio
    caminho = "/" + a.caminho.strip("/") + "/" if a.caminho.strip("/") else "/"

    url, chave, plat = le_motor()
    saida = os.path.join(RAIZ, a.saida, d["slug"])
    dest = os.path.join(saida, "site")
    shutil.rmtree(saida, ignore_errors=True)
    shutil.copytree(os.path.join(RAIZ, MODELOS[d["modelo"]]), dest,
                    ignore=shutil.ignore_patterns("LEIA-ME*", "admin", "pedido.html", "*.bak"))
    for f in ("motor.js", "marca.js"):
        shutil.copy(os.path.join(RAIZ, "paineis/motor", f), os.path.join(dest, "assets", f))
    if a.fotos:
        fd = os.path.join(dest, "img/cliente")
        os.makedirs(fd, exist_ok=True)
        for f in sorted(os.listdir(a.fotos)):
            if re.search(r"\.(jpe?g|png|webp|avif|svg)$", f, re.I):
                shutil.copy(os.path.join(a.fotos, f), os.path.join(fd, slugify(os.path.splitext(f)[0]) + os.path.splitext(f)[1].lower()))
    escreve_config(dest, d, url, chave, plat)
    copia_rastreio(dest, d, caminho)
    copia_painel(dest, d)
    escreve_htaccess(dest)
    subprocess.run([sys.executable, os.path.join(RAIZ, "ferramentas/csp.py"),
                    os.path.join(dest, "index.html"), os.path.join(dest, "pedido.html"), os.path.join(dest, "admin/index.html")], check=True)

    if not a.sem_zip:
        z = os.path.join(RAIZ, a.saida, d["slug"] + ".zip")
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for r, _, fs in os.walk(dest):
                for f in fs:
                    p = os.path.join(r, f)
                    zf.write(p, os.path.relpath(p, dest))
        print("zip:", os.path.relpath(z, RAIZ))

    falta = []
    if not url or not chave: falta.append("motor sem URL/chave: preencha clientes/motor.json (o site fica em modo demonstração)")
    if not d.get("whatsapp"): falta.append("WhatsApp da loja (o painel também pode preencher)")
    if not d.get("dominio"): falta.append("domínio do cliente (BC.site): sem ele, o link do rastreio usa o endereço atual")
    if "depoimentos" not in (d.get("ocultar") or []) and not any(k.startswith("depoimento") for k in (d.get("textos") or {})):
        falta.append("depoimentos: são exemplos do modelo. Troque por depoimentos reais ou adicione \"depoimentos\" em ocultar")
    print("site:", os.path.relpath(dest, RAIZ))
    print("loja na plataforma (slug):", d["slug"])
    if falta:
        print("\nAntes de publicar:")
        for f in falta: print(" -", f)


if __name__ == "__main__":
    main()
