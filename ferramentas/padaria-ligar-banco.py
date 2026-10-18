#!/usr/bin/env python3
"""Liga o código compilado do modelo Padaria & Café (v17) ao Supabase de verdade.

O build original vem com o banco desligado (modo demonstração). Este script troca
só os pontos de conexão, sem mexer no visual nem nas regras do site:
  * URL/chave do Supabase, nome da loja e WhatsApp vêm de assets/config.js (window.LOJA);
  * textos do site ficam num documento jsonb (tabela settings, coluna data);
  * usuários do painel são listados pela função admin_list_users (sem servidor Node);
  * o pedido ganha o link de rastreio (pedido.html) na mensagem e na tela final.

    python3 ferramentas/padaria-ligar-banco.py app-original.js sites/padaria-cafe/assets/app.js
"""
import sys

ENTRADA, SAIDA = sys.argv[1], sys.argv[2]
s = open(ENTRADA, encoding="utf-8").read()


def troca(velho, novo, vezes=1):
    global s
    n = s.count(velho)
    assert n == vezes, (n, velho[:90])
    s = s.replace(velho, novo)


USUARIOS = ('Por seguran\\xE7a, usu\\xE1rios do painel s\\xE3o criados e removidos no Supabase '
            '(Authentication > Users e tabela admins). Veja o SEGURANCA.md.')

# conexão com o Supabase (sessão só nesta aba: fechou, saiu)
troca('function Wm(){throw new Error("Supabase n\\xE3o configurado (demo)")}',
      'function Wm(u,k){return window.supabase.createClient(u,k,{auth:{persistSession:!0,storage:window.sessionStorage}})}')
troca('var Ul="",Hm="",ql=!!(Ul&&Hm&&!Ul.includes("xxxxxxxx"))',
      'var Ul=(window.LOJA&&window.LOJA.supabaseUrl)||"",Hm=(window.LOJA&&window.LOJA.supabaseKey)||"",'
      'ql=!!(Ul&&Hm&&!Ul.includes("xxxxxxxx")&&window.supabase)')
troca('Jm=typeof process<"u"&&process.env.NEXT_PUBLIC_STORE_SLUG||"loja"',
      'Jm=(window.LOJA&&window.LOJA.slug)||"loja"')

# nome e WhatsApp padrão vêm do config.js (o painel pode trocar depois)
troca('store_name:"Nome da Loja"', 'store_name:(window.LOJA&&window.LOJA.nome)||"Nome da Loja"')
troca('whatsapp:"5500000000000"', 'whatsapp:(window.LOJA&&window.LOJA.whatsapp)||""')

# textos do site num documento só (settings.data)
troca('settings:{...Fe.settings,...a.data??{}}', 'settings:__zap({...Fe.settings,...a.data?.data??{}})')
troca('upsert({...r,store_id:await Ct(),updated_at:new Date().toISOString()})',
      'upsert({data:r,store_id:await Ct()})')

# usuários do painel: lista pelo banco; criar/apagar só no Supabase
troca('let{users:e}=await ui("/api/admin/users");return e.map(',
      'let{data:e,error:x}=await Z().rpc("admin_list_users");if(x)throw new Error(x.message);return(e||[]).map(')
for metodo in ("POST", "PATCH", "DELETE"):
    troca(f'await ui("/api/admin/users",{{method:"{metodo}",',
          f'throw new Error("{USUARIOS}");await ui("/api/admin/users",{{method:"{metodo}",')
troca('redirectTo:location.origin+"/admin"', 'redirectTo:location.href.split("#")[0]')

# rastreio: link na mensagem do WhatsApp e botão na tela final
troca('`Para: ${e.scheduled_for}`,', '`Para: ${e.scheduled_for}`,e.track_token?`Acompanhe: ${__rastreio(e.track_token)}`:"",')
troca('(0,I.jsx)("button",{className:"btn btn-ghost",onClick:n,children:"Fechar"})]})})]})]})}',
      'h.track_token&&(0,I.jsx)("a",{className:"btn btn-ghost",href:__rastreio(h.track_token),target:"_blank",'
      'rel:"noopener",children:"Acompanhar pedido"}),'
      '(0,I.jsx)("button",{className:"btn btn-ghost",onClick:n,children:"Fechar"})]})})]})]})}')

topo = ('var __rastreio=function(t){return new URL("pedido.html#"+t,location.href).href};'
        'var __zap=function(c){if(!c.whatsapp)c.whatsapp=(window.LOJA&&window.LOJA.whatsapp)||"";return c};\n')
corpo = s.lstrip("\n")
assert corpo.startswith('"use strict";')
open(SAIDA, "w", encoding="utf-8").write('"use strict";' + topo + corpo[len('"use strict";'):])
print("ok")
