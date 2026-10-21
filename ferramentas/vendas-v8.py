"""Página de vendas v8: os celulares da página mostram as lojas REAIS da plataforma (prints em assets/img/lojas/),
em vez de cardápios de mentira. O visitante rola dentro do celular para ver o cardápio, as seções e as fotos.
Os prints saem de lojas de exemplo (padaria, café, hamburgueria, restaurante) abertas em /l/<endereço> no celular.
Uso: python3 ferramentas/vendas-v8.py && python3 ferramentas/csp.py plataforma/index.html
Pode rodar de novo: não duplica nada."""
import re

ARQ = "plataforma/index.html"
MARCA = "/* ===== v8: lojas reais nos celulares ===== */"
s = open(ARQ, encoding="utf-8").read()
if MARCA in s:
    raise SystemExit("plataforma/index.html já está na v8")


def troca(velho, novo, vezes=1):
    global s
    n = s.count(velho)
    assert n == vezes, (n, velho[:80])
    s = s.replace(velho, novo)


# 1) o celular mostra o print da loja real, rolável
a = s.index("  function mountMenu(phone,key){")
b = s.index("  var hero=document.getElementById('heroPhone');", a)
NOVO = """  function mountMenu(phone,key){
    var M=MODELS[key];phone.innerHTML='';
    var sc=el('div','screen real');sc.tabIndex=0;sc.setAttribute('aria-label','Loja de exemplo: '+M.brand+'. Role para ver o cardápio.');
    var im=el('img');im.src='/assets/img/lojas/'+key+'.jpg';im.alt='Cardápio da loja de exemplo '+M.brand;im.width=780;im.height=6800;im.decoding='async';
    if(phone.id!=='heroPhone')im.loading='lazy';
    sc.appendChild(im);phone.appendChild(sc)}
"""
s = s[:a] + NOVO + s[b:]

# 2) sem "dedo" de demonstração; o celular do topo troca de loja sozinho enquanto ninguém mexe
troca("document.querySelectorAll('[data-mount]').forEach(function(p,i){mountMenu(p,p.dataset.mount);autoLoop(p,1500+i*2200)});",
      "document.querySelectorAll('[data-mount]').forEach(function(p){mountMenu(p,p.dataset.mount)});")
troca("autoLoop(hero,600,NICHO?null:function(){cur=(cur+1)%ORDER.length;heroPick(ORDER[cur])});",
      "watch(hero);if(!NICHO&&!REDUCED)setInterval(function(){if(hero.__user||!hero.__vis||document.hidden)return;cur=(cur+1)%ORDER.length;heroPick(ORDER[cur])},5200);")

# 3) os nomes nos avisos de pedido são os das lojas reais dos prints
for velho, novo in (("brand:'Fermento'", "brand:'Padaria da Ana'"), ("brand:'Torra'", "brand:'Café da Joana'"),
                    ("brand:'Brasa'", "brand:'Burger do Beto'"), ("brand:'Alecrim'", "brand:'Âmbar Cozinha'")):
    troca(velho, novo)
troca("Novo pedido · Fermento", "Novo pedido · Padaria da Ana")

# 4) textos honestos
troca("Quatro estilos para começar, todos funcionando de verdade. Toque, escolha e envie um pedido de teste. Cores, fontes e fotos mudam para a cara da sua casa.",
      "São lojas reais da plataforma, do jeito que o seu cliente vai ver no celular. Role dentro do celular para ver o cardápio, as fotos e as seções. A cor da marca, a logo, a capa e os textos você troca pelo painel.")
troca("<b>Padaria</b><span>Claro e artesanal, em grade</span>", "<b>Padaria</b><span>Café escuro e dourado, artesanal</span>")
troca("<b>Café</b><span>Escuro e aconchegante, com vitrine</span>", "<b>Café e confeitaria</b><span>O mesmo estilo artesanal, com vitrine</span>")
troca("<b>Hamburgueria</b><span>Preto e marcante, foto em destaque</span>", "<b>Hamburgueria</b><span>Preto e vermelho, foto em destaque</span>")
troca("<b>Restaurante</b><span>Claro e elegante, prato em destaque</span>", "<b>Restaurante</b><span>Carvão e âmbar, elegante</span>")
troca("Escolha o modelo, toque em adicionar e envie o pedido.", "Loja real da plataforma. Escolha o modelo e role para ver o cardápio.")

# 4b) "Quer ir além?" (site completo) já existia: a seção "Sob medida" da v7c repetia o assunto. Sai a repetida e o
#     botão de orçamento passa para a seção que já mostra os sites
i = s.index('  <section id="sob-medida">')
j = s.index("  </section>\n\n", i) + len("  </section>\n\n")
s = s[:i] + s[j:]
k = s.index('id="sites"')
fim = s.index("    </div>\n  </section>", k)
s = s[:fim] + '      <p class="sites-cta"><a class="btn btn-mint" href="#contato" data-track="cta-sites">Pedir orçamento do meu site</a></p>\n' + s[fim:]

# 5) estilo do print rolável dentro do celular
CSS = """
/* ===== v8: lojas reais nos celulares ===== */
.screen.real{overflow-y:auto;overflow-x:hidden;-webkit-overflow-scrolling:touch;overscroll-behavior:contain;scrollbar-width:none;background:#120d09;display:block;border-radius:inherit;outline:none}
.screen.real::-webkit-scrollbar{display:none}
.screen.real img{display:block;width:100%;height:auto;max-width:none}
.sites-cta{text-align:center;margin:30px 0 0}
"""
k = s.index("</style>"); s = s[:k] + CSS + s[k:]
open(ARQ, "w", encoding="utf-8").write(s)
print("v8 aplicada em", ARQ)
