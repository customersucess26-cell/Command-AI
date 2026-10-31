"""Junta um site de sites/<pasta>/ num único HTML de demonstração (fotos, vídeo e configuração dentro do arquivo).
Abre em qualquer navegador, sem servidor e sem internet (só as fontes do Google vêm de fora).
Uso:  python3 ferramentas/montar-modelo-unico.py pizzaria-fornalha   ->  modelos/pizzaria-fornalha.html"""
import base64, os, re, subprocess, sys
pasta = sys.argv[1] if len(sys.argv) > 1 else "pizzaria-fornalha"
base = os.path.join("sites", pasta)
html = open(os.path.join(base, "index.html"), encoding="utf-8").read()
MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp", ".svg": "image/svg+xml", ".mp4": "video/mp4", ".webm": "video/webm"}
def uri(rel):
    p = os.path.join(base, rel)
    if p.endswith('.mp4'):
        leve = '/tmp/modelo-unico-video.mp4'
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',p,'-vf','scale=540:-2','-an','-c:v','libx264','-preset','slow','-crf','31','-movflags','+faststart',leve],check=True)
        p = leve
    elif p.endswith('.webm'):
        leve = '/tmp/modelo-unico-video.webm'
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',p,'-vf','scale=540:-2','-an','-c:v','libvpx-vp9','-b:v','0','-crf','44','-row-mt','1','-deadline','good','-cpu-used','4',leve],check=True)
        p = leve
    return "data:%s;base64,%s" % (MIME[os.path.splitext(p)[1].lower()], base64.b64encode(open(p, "rb").read()).decode())
# 1) configuração junto (sem arquivo externo)
cfg = open(os.path.join(base, "assets/config.js"), encoding="utf-8").read()
html = html.replace('<script src="assets/config.js"></script>', "<script>\n" + cfg + "\n</script>")
# 2) vídeo leve em mp4 (Safari/iPhone) e webm (Chrome, Firefox, Android)
# 3) imagens pedidas por código ("img/"+nome+".jpg"): mapa com todas as que existem em img/
todas = sorted(f for f in os.listdir(os.path.join(base, "img")) if os.path.splitext(f)[1].lower() in MIME )
usadas = set(re.findall(r'img/[\w.-]+\.(?:jpg|jpeg|png|webp|mp4|webm)', html))
dinam = ["camada-", "lata-", "res-", "beb-"] + [f[:-len(os.path.splitext(f)[1])] for f in todas]
for f in todas:
    nome = os.path.splitext(f)[0]
    if "img/" + f in usadas or any(nome.startswith(p) for p in ("camada-", "lata-", "res-", "beb-")) or ('"' + nome + '"' in html):
        usadas.add("img/" + f)
mapa = {k: uri(k) for k in sorted(usadas) if os.path.exists(os.path.join(base, k))}
# literais "img/arquivo" viram data URI direto (HTML, CSS e JS)
for k, v in mapa.items():
    html = html.replace('"' + k + '"', '"' + v + '"').replace("'" + k + "'", "'" + v + "'").replace("(" + k + ")", "(" + v + ")")
# montagens dinâmicas passam pelo mapa
js_mapa = "<script>window.__IMG=" + "{" + ",".join('"%s":"%s"' % kv for kv in mapa.items()) + "};function U(p){return window.__IMG[p]||p}</script>\n"
html = html.replace("<script>\n" + cfg, js_mapa + "<script>\n" + cfg, 1)
trocas = [
    ('IMG[k]="img/"+k+".webp"', 'IMG[k]=U("img/"+k+".webp")'),
    ('IMG[k]="img/"+k+".jpg"', 'IMG[k]=U("img/"+k+".jpg")'),
    ('"img/res-"+r[2]+".jpg"', 'U("img/res-"+r[2]+".jpg")'),
    ("src=\"img/lata-'+l+'.webp\"", "src=\"'+U('img/lata-'+l+'.webp')+'\""),
    ("src=\"img/camada-'+e.n+'.jpg\"", "src=\"'+U('img/camada-'+e.n+'.jpg')+'\""),
    ("src=\"img/'+n+'.jpg\"", "src=\"'+U('img/'+n+'.jpg')+'\""),
    ("src=\"img/'+f[0]+'.webp\"", "src=\"'+U('img/'+f[0]+'.webp')+'\""),
]
for a, b in trocas:
    html = html.replace(a, b)
# 4) demonstração: tira o link do painel e o rastreio (precisam do servidor)
html = re.sub(r'\s*·?\s*<a href="admin/"[^>]*>[^<]*</a>', "", html)
sobra = sorted(set(re.findall(r'["\'(]img/[\w.-]+', html.replace(js_mapa, ""))) - {'"img/res-', "'img/camada-", "'img/lata-", "'img/", '"img/'})
os.makedirs("modelos", exist_ok=True)
out = os.path.join("modelos", pasta + ".html")
open(out, "w", encoding="utf-8").write(html)
# demonstração: a hospedagem (LiteSpeed/CDN da Hostinger) pode reescrever ou adiar os scripts da página;
# com a CSP por resumo (hash) o navegador bloquearia tudo. Aqui não há login nem dados, então libera os scripts da própria página.
html = open(out, encoding="utf-8").read()
html = re.sub(r"script-src [^;]*;", "script-src 'self' 'unsafe-inline' https:;", html, count=1)
open(out, "w", encoding="utf-8").write(html)
print(out, round(os.path.getsize(out) / 1e6, 1), "MB ·", len(mapa), "arquivos embutidos ·", "sobrou referência externa:" if sobra else "nenhuma referência externa", " ".join(sobra))
