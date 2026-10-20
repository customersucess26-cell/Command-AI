"""Página de vendas v7c: seção "Sob medida" (site completo com painel personalizado) depois dos planos,
e a opção "Site sob medida" no formulário. Pode rodar de novo: não duplica nada.
Uso: python3 ferramentas/vendas-v7c.py && python3 ferramentas/csp.py plataforma/index.html"""
ARQ = "plataforma/index.html"
MARCA = 'id="sob-medida"'
s = open(ARQ, encoding="utf-8").read()
if MARCA in s:
    raise SystemExit("plataforma/index.html já está na v7c")

SECAO = '''  <section id="sob-medida">
    <div class="in case">
      <div>
        <p class="eyebrow">Sob medida</p>
        <h2 style="margin-top:12px">Quer um site só seu, com painel personalizado?</h2>
        <p style="color:var(--ink-soft);margin-top:16px;max-width:46ch">Além da loja pronta, nós também construímos o site completo do seu restaurante: visual com a cara da sua marca, cardápio, pedidos e um painel feito para a sua rotina. Você conversa com a gente e recebe um orçamento fechado.</p>
      </div>
      <div class="case-card">
        <span class="tag">Projeto sob medida</span>
        <h3 style="font-size:24px;position:relative">Site e painel feitos para você</h3>
        <ul>
          <li>Visual exclusivo, com a identidade da sua marca</li>
          <li>Painel de pedidos e cardápio ajustados à sua operação</li>
          <li>Hospedagem e certificado de segurança incluídos</li>
          <li>Treinamento da sua equipe e suporte pelo WhatsApp</li>
        </ul>
        <a class="btn btn-mint" href="#contato" style="position:relative;align-self:flex-start" data-track="cta-sob-medida">Pedir um orçamento</a>
      </div>
    </div>
  </section>

'''
i = s.index('id="planos"')
j = s.index("\n  <section>", i)          # a próxima seção depois dos planos (perguntas)
s = s[:j + 1] + SECAO + s[j + 1:]
velho = "<option>Sem limites</option></select>"
assert s.count(velho) == 1
s = s.replace(velho, "<option>Sem limites</option><option>Site sob medida</option></select>")
open(ARQ, "w", encoding="utf-8").write(s)
print("v7c aplicada em", ARQ)
