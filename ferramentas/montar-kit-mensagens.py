#!/usr/bin/env python3
"""Kit de mensagens de venda do Bistrô Connect (WhatsApp e Instagram).
Gera manual/Kit-de-Mensagens-Bistro-Connect.pdf e manual/kit-de-mensagens.txt.
Texto só promete o que a plataforma faz hoje. Troque os [colchetes] antes de enviar."""
import html, subprocess

VOCE = "[Nome]"
# (secao, intro, [(rotulo, quando, texto)])
S = []

S.append(("1", "Antes de enviar", "Cinco regras que valem mais que qualquer texto.", [
 ("Regra 1", "", "Mande para quem tem o contato PUBLICADO como contato comercial (Instagram, Google, cardápio). Uma mensagem por pessoa, nunca lista de transmissão."),
 ("Regra 2", "", "Fale fora do pico. Padaria e café: entre 14h e 16h. Hamburgueria e pizzaria: entre 15h e 17h. Nunca na hora do almoço ou do jantar."),
 ("Regra 3", "", "Troque [Nome], [Loja] e [item] antes de mandar. Uma mensagem que cita um produto da casa é lida. Uma genérica é apagada."),
 ("Regra 4", "", "O objetivo da primeira mensagem não é vender. É ganhar uma resposta. Quem responde, você leva para a demonstração de 10 minutos."),
 ("Regra 5", "", "Se a pessoa disser que não quer, agradeça e pare. Isso protege o seu número e a sua marca. Em toda mensagem fria, deixe a saída fácil."),
]))

S.append(("2", "Primeiro contato", "Escolha uma. Cada uma abre por um ângulo diferente.", [
 ("1A · A pergunta da comissão", "Dono que vende por app de delivery",
  "Oi, [Nome]! Aqui é o [Seu nome], da Bistrô Connect.\n\nUma pergunta rápida: no fim do mês, quanto do que a [Loja] vende pelo [iFood/app] fica de comissão?\n\nFaço o cardápio próprio da loja, onde o cliente pede direto com você e não existe comissão por pedido. Posso te mostrar em 2 minutos como fica o da [Loja]?"),
 ("1B · A conta pronta", "Quando você quer usar número, não pergunta",
  "Oi, [Nome], tudo bem?\n\nUma conta que quase ninguém faz: quem vende R$ 10 mil por mês no app, se pagar 23% de comissão, deixa R$ 2.300 por mês lá.\n\nNo cardápio próprio da Bistrô Connect, a mensalidade para essa mesma venda é R$ 49, e não tem comissão por pedido.\n\nQuer ver como ficaria o cardápio da [Loja]? Se o seu percentual for outro, eu refaço a conta com o seu número."),
 ("1C · O elogio específico", "Quando você conhece a loja pelo Instagram",
  "Oi, [Nome]! Vi o [item] da [Loja] no Instagram e deu vontade de pedir.\n\nUma ideia: um link só seu, onde o cliente escolhe, finaliza e acompanha o pedido pelo celular. O pedido cai no seu painel organizado, com alerta sonoro, e sem comissão por pedido.\n\nPosso montar um exemplo com os produtos da [Loja] para você ver? Sem compromisso."),
 ("1D · Direct do Instagram", "Mensagem curta para DM",
  "Oi, [Nome]! A [Loja] está linda por aqui.\n\nVocê já tem um cardápio próprio para o cliente pedir direto, sem passar por app? Eu ajudo lojas a ter isso, sem comissão por pedido. Se quiser, te mostro um exemplo de 1 minuto."),
 ("1E · Depois de visitar a loja", "Você passou no balcão e conversou",
  "Oi, [Nome]! Foi um prazer conhecer a [Loja] hoje. Aquele [item] estava ótimo.\n\nComo combinamos, segue o exemplo do cardápio próprio: [LINK DO EXEMPLO]\n\nÉ o mesmo que o cliente usaria no seu celular. Se gostar, a gente monta o da [Loja] com as suas fotos e preços."),
 ("1F · Indicação", "Quando alguém indicou",
  "Oi, [Nome]! Aqui é o [Seu nome]. O [Quem indicou] falou muito bem da [Loja] e disse que você pode gostar do que eu faço.\n\nEu monto o cardápio próprio da loja, para o cliente pedir direto, sem comissão por pedido. Posso te mostrar em 2 minutos, no seu horário?"),
]))

S.append(("3", "Follow-up", "A maioria das vendas acontece depois da segunda mensagem. Espaçamento: 1 dia, 3 dias, 7 dias.", [
 ("Dia 1 · Leve", "Sem resposta no dia seguinte",
  "Oi, [Nome]! Só para a minha mensagem não se perder no meio dos pedidos.\n\nSe for mais fácil, responde só 'mostra' que eu te mando agora um exemplo de cardápio, em 1 minuto de leitura."),
 ("Dia 3 · A conta da loja", "Segundo toque, com número",
  "[Nome], fiz uma conta rápida para a [Loja], como exemplo:\n\nSe a loja vende R$ 6 mil por mês pelo app e paga 23%, são R$ 1.380 de comissão. Se um terço dessas vendas passasse a vir direto, são R$ 460 que ficam no seu caixa todo mês.\n\nO exemplo é com números redondos. Se me disser o seu faturamento e o seu percentual, eu refaço com o real."),
 ("Dia 7 · A despedida", "Último toque, sem pressão",
  "Oi, [Nome]. Não quero encher a sua caixa de mensagem, então essa é a última sobre o assunto.\n\nSe um dia fizer sentido ter o cardápio próprio da [Loja], com pedido direto e sem comissão por pedido, é só me chamar aqui. Sucesso por aí!"),
]))

S.append(("4", "Quando respondem", "Conduza em 3 passos: qualificar, mostrar, propor.", [
 ("Respondeu 'pode mostrar'", "Mande o exemplo e já qualifique",
  "Combinado! Esse é o exemplo de como o cliente vê o cardápio no celular: [LINK DO EXEMPLO]\n\nPara eu montar o da [Loja] de um jeito que faça sentido: hoje o pedido chega por onde, WhatsApp, app, telefone? E mais ou menos quantos pedidos por dia?"),
 ("Respondeu 'quanto custa?'", "Responda com a regra, não com 'depende'",
  "A mensalidade acompanha o que a loja vende pela plataforma no mês, e tem teto:\n\nAté R$ 3 mil por mês: condição de convite (vagas limitadas)\nAté R$ 10 mil: R$ 49\nAté R$ 30 mil: R$ 99\nAcima disso: R$ 199\n\nNão tem comissão por pedido e todos os planos têm todos os recursos. Quer que eu veja em qual faixa a [Loja] começa?"),
 ("Respondeu 'como funciona?'", "Quatro linhas, sem manual",
  "É simples:\n\n1. O cliente abre o link da [Loja], escolhe os itens e envia o pedido\n2. O pedido cai no seu painel com alerta sonoro, já organizado\n3. O cliente acompanha as etapas pelo celular (recebido, preparo, entrega)\n4. Você fica com o contato de quem pediu\n\nPosso te mostrar o painel funcionando agora, em 10 minutos? Qual horário é melhor hoje?"),
 ("Marcar a demonstração", "Feche o horário",
  "Perfeito! Seguem dois horários para a demonstração de 10 minutos, pelo WhatsApp ou chamada de vídeo:\n\nHoje às [HH:MM] ou amanhã às [HH:MM]\n\nQual fica melhor? Se tiver o cardápio em foto ou PDF, pode me mandar antes, que eu já deixo o exemplo com os seus produtos."),
]))

S.append(("5", "Objeções", "Cada resposta reconhece a dúvida, devolve um fato e termina em uma pergunta.", [
 ("'Já uso o iFood'", "A mais comum",
  "Faz sentido, e eu não peço para você sair de lá. O app traz cliente novo, e isso vale muito. O cardápio próprio é para quem já conhece a [Loja] pedir direto, sem comissão. E tem o cartão de volta: um cartão com QR e desconto que vai na sacola do app e leva o cliente para o seu cardápio no próximo pedido. Quer ver como funciona?"),
 ("'Meu movimento já está bom'", "Quem está lotado",
  "Movimento bom é a melhor hora para ter isso. O cardápio atende quem chega pelo celular fora do horário, quando a equipe está ocupada ou a fila está grande. São pedidos que hoje você nem vê passar. Posso te mostrar em 5 minutos?"),
 ("'É caro'", "Mostre a conta",
  "Entendo. Por isso a mensalidade acompanha a sua venda: se a loja vende pouco pela plataforma, paga pouco, e o teto é R$ 199. Em comparação, 23% de R$ 10 mil é R$ 2.300 de comissão por mês no app. Quanto a [Loja] paga hoje de comissão? Eu faço a comparação com o seu número."),
 ("'Não tenho tempo para isso'", "Dono sobrecarregado",
  "Justamente por isso. O painel foi feito para quem não tem tempo: o pedido chega pronto, com itens, endereço e pagamento, sem você digitar nada. E se preferir, eu cadastro o cardápio com você, por mensagem. Hoje eu só preciso de 10 minutos seus. Qual horário é menos corrido?"),
 ("'Não entendo de tecnologia'", "Receio de complicar",
  "Se você usa WhatsApp, você usa o painel. É botão grande, tudo em português, e eu acompanho você nos primeiros pedidos. Quer ver como é, sem compromisso?"),
 ("'Meu cliente não vai pedir por link'", "Dúvida de adoção",
  "É uma dúvida justa. O cliente que já pede pelo WhatsApp ou pelo app já está acostumado a tocar em links. E o pedido leva menos toques que mandar mensagem. O melhor é testar com os seus clientes mais fiéis primeiro. Posso montar um exemplo para você experimentar?"),
 ("'Já tenho site / só uso WhatsApp'", "Alternativa atual",
  "Ótimo, então a [Loja] já está online. O que muda é o pedido: no site ou no WhatsApp, quem anota é você. No cardápio da Bistrô Connect, o cliente monta o pedido, o total sai certo e você recebe tudo organizado no painel. Posso te mostrar a diferença em 2 minutos?"),
 ("'Preciso pensar'", "Não force, ancore o próximo passo",
  "Claro, sem pressa. Para ajudar na decisão, posso te mandar um exemplo do cardápio da [Loja] pronto para você testar com calma? Depois eu falo com você na [dia] para ouvir o que achou. Pode ser?"),
 ("'E se eu não gostar?'", "Medo do compromisso",
  "Você cancela quando quiser, sem multa e sem fidelidade, e pode pedir uma cópia dos dados da sua loja antes. Assim a decisão fica fácil: se não ajudar, você sai."),
 ("'Isso tem comissão?'", "Pergunta direta",
  "Não. Zero comissão por pedido. Você paga só a mensalidade, que acompanha o que a loja vendeu no mês e nunca passa de R$ 199."),
]))

S.append(("6", "Fechamento", "Peça o próximo passo de forma concreta.", [
 ("Fechamento direto", "Já demonstrou interesse",
  "Então vamos colocar a [Loja] no ar! Para começar eu preciso de 3 coisas:\n\n1. O nome da loja e a cor da sua marca\n2. O cardápio com os preços (foto ou PDF servem)\n3. O horário de funcionamento e se faz entrega ou só retirada\n\nCom isso eu monto o primeiro cardápio e te mando para você aprovar. Pode me enviar agora?"),
 ("Fechamento por escolha", "Quando está indeciso entre dois caminhos",
  "Duas formas de começar, escolhe a que preferir:\n\nA) Você mesmo cadastra os produtos pelo painel, no seu ritmo, e eu te acompanho\nB) Você me manda o cardápio e eu cadastro tudo com você (serviço à parte, combinado conforme o tamanho do cardápio)\n\nQual faz mais sentido para a [Loja]?"),
 ("Fechamento com condição de convite", "Loja que vende até R$ 3 mil/mês",
  "Tenho algumas vagas de convite para lojas que vendem até R$ 3 mil por mês pela plataforma. Se a [Loja] encaixar, você começa nessa condição. Quer que eu reserve uma vaga para você hoje?"),
 ("Antes de sumir", "Última tentativa depois da demo",
  "Oi, [Nome]! Passando para saber o que você achou do cardápio da [Loja] que eu montei. Se tiver alguma dúvida, me fala que eu resolvo agora. Se não for o momento, sem problema, eu guardo o seu cardápio aqui."),
]))

S.append(("7", "Depois da venda", "O cliente que fica é o que indica.", [
 ("Boas-vindas", "Logo após assinar",
  "Bem-vindo à Bistrô Connect, [Nome]! A [Loja] já está no ar. Seu link: [LINK DA LOJA]\n\nPrimeiros passos: 1) conferir o cardápio, 2) mandar o link para 5 clientes fiéis, 3) pôr o link na bio do Instagram. Qualquer dúvida me chama aqui."),
 ("Primeira semana", "7 dias depois",
  "Oi, [Nome]! Já faz uma semana. Quantos pedidos chegaram pelo link? Se ainda forem poucos, me conta onde você divulgou, que eu te ajudo a ajustar (texto da bio, QR no balcão, cartão de volta na sacola do app)."),
 ("Pedido de indicação", "Quando o cliente estiver satisfeito",
  "[Nome], fico feliz que a [Loja] esteja gostando! Você conhece mais algum dono de padaria, café ou restaurante que sofre com comissão de app? Se me apresentar, eu cuido dele com o mesmo carinho."),
]))

S.append(("8", "Áudio de 30 segundos", "Para quem responde melhor por voz. Grave com calma e sorrindo.", [
 ("Roteiro do áudio", "Depois de a pessoa responder o primeiro contato",
  "Oi, [Nome], aqui é o [Seu nome], da Bistrô Connect. Obrigado por responder! Resumindo bem rápido: eu monto o cardápio próprio da sua loja, onde o cliente escolhe, finaliza e acompanha o pedido pelo celular. O pedido cai no seu painel, já organizado, e não existe comissão por pedido. Quero te mostrar funcionando, leva 10 minutos. Que horário fica bom para você hoje?"),
]))

S.append(("9", "Roteiro da demonstração de 10 minutos", "A ordem que mais convence.", [
 ("Minuto 0 a 2", "", "Pergunte: 'Quantos pedidos por dia você recebe e por onde?' Anote o número e a comissão que paga. Isso vira a conta do final."),
 ("Minuto 2 a 5", "", "Mostre o cardápio no celular: fotos, sacola, finalizar e o pedido enviado com o cartão do pedido. Deixe a pessoa fazer um pedido de teste no próprio celular."),
 ("Minuto 5 a 8", "", "Mostre o painel: o pedido chegando com alerta sonoro, a mudança de etapa e a tela de rastreio do cliente mudando sozinha."),
 ("Minuto 8 a 10", "", "Faça a conta com o número que ela te deu e mostre o cartão de volta. Termine com: 'Quer que eu monte o da sua loja hoje?'"),
]))

# ---------------------------------------------------------------- TXT
txt = ["KIT DE MENSAGENS · BISTRÔ CONNECT", "Troque os [colchetes] antes de enviar.\n"]
for n, t, intro, itens in S:
    txt.append(f"\n{'=' * 60}\n{n}. {t.upper()}\n{intro}\n{'=' * 60}")
    for r, q, m in itens:
        txt.append(f"\n--- {r}" + (f" ({q})" if q else "") + f" ---\n{m}")
open("manual/kit-de-mensagens.txt", "w", encoding="utf-8").write("\n".join(txt) + "\n")

# ---------------------------------------------------------------- HTML / PDF
def bloco(r, q, m):
    corpo = html.escape(m).replace("\n", "<br>")
    return f'<div class="msg"><div class="cab"><b>{html.escape(r)}</b>{f"<span>{html.escape(q)}</span>" if q else ""}</div><div class="zap">{corpo}</div></div>'

secs = ""
for n, t, intro, itens in S:
    secs += f'<section class="sec"><div class="cap"><span class="n">{n}</span><h2>{html.escape(t)}</h2></div><p class="intro">{html.escape(intro)}</p>' + "".join(bloco(*i) for i in itens) + "</section>"

HTML = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Kit de mensagens · Bistrô Connect</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&display=swap">
<style>
@page{{size:A4;margin:16mm 16mm 18mm}}@page :first{{margin:0}}
:root{{--navy:#0E1526;--ouro:#C9A24A;--ouro2:#F3E3B8;--tinta:#1C2433;--suave:#5E6878;--linha:#E6E8EC;--creme:#FAF7F0}}
*{{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}}body{{margin:0;font:10.4pt/1.55 'DM Sans',Arial,sans-serif;color:var(--tinta)}}
h1,h2{{font-family:'Poppins',Arial,sans-serif;color:var(--navy);margin:0}}
.capa{{width:210mm;height:297mm;background:radial-gradient(120% 80% at 85% 0%,#1C3A63 0%,var(--navy) 55%,#080C17 100%);color:#fff;display:flex;flex-direction:column;justify-content:space-between;padding:24mm 22mm;page-break-after:always}}
.capa .topo{{font:600 8.6pt 'Poppins';letter-spacing:.32em;color:var(--ouro);text-transform:uppercase}}
.capa img{{width:130mm;display:block;margin:0 auto 12mm}}.capa h1{{color:#fff;font-size:30pt;text-align:center;line-height:1.14}}.capa h1 em{{font-style:normal;color:var(--ouro)}}
.capa .linha{{width:56mm;height:3px;background:linear-gradient(90deg,transparent,var(--ouro),transparent);margin:9mm auto}}
.capa p{{text-align:center;color:#C9D3E3;font-size:12pt;max-width:140mm;margin:0 auto}}
.capa .pe{{display:flex;justify-content:space-between;color:#8E9AB0;font-size:9pt;border-top:1px solid rgba(255,255,255,.14);padding-top:5mm}}
.sec{{margin-top:9mm}}.sec:first-of-type{{margin-top:0}}.cap{{break-after:avoid}}.intro{{break-after:avoid}}
.cap{{display:flex;align-items:center;gap:12px;margin-bottom:4px}}.cap .n{{width:42px;height:42px;border-radius:13px;background:var(--navy);color:var(--ouro);font:700 17pt 'Poppins';display:grid;place-items:center}}.cap h2{{font-size:20pt}}
.intro{{color:var(--suave);margin:0 0 12px;padding-bottom:10px;border-bottom:2px solid var(--ouro2)}}
.msg{{margin:0 0 11px;break-inside:avoid}}
.cab{{display:flex;gap:10px;align-items:baseline;margin-bottom:4px}}.cab b{{font:600 10.4pt 'Poppins';color:var(--navy)}}.cab span{{font-size:8.8pt;color:var(--suave)}}
.zap{{background:#E7F8DC;border:1px solid #CDE9BC;border-radius:4px 14px 14px 14px;padding:10px 14px;font-size:10.2pt;line-height:1.5;color:#12281A}}
.dica{{background:var(--creme);border-left:4px solid var(--ouro);border-radius:0 10px 10px 0;padding:9px 13px;margin:10px 0;font-size:9.6pt;color:var(--suave)}}
</style></head><body>
<section class="capa"><div class="topo">Kit de mensagens</div>
<div><img src="carta-img/logo-clara.png" alt="Bistrô Connect"><h1>Mensagens prontas<br><em>para vender</em></h1><div class="linha"></div>
<p>Primeiro contato, follow-up, respostas às objeções, fechamento e pós-venda. Para WhatsApp e Instagram.</p></div>
<div class="pe"><span>bistroconnect.com.br</span><span>Troque os [colchetes] antes de enviar</span></div></section>
{secs}
</body></html>'''
open("manual/kit-de-mensagens.html", "w", encoding="utf-8").write(HTML)
js = r"""const{chromium}=require('playwright');const path=require('path');(async()=>{const b=await chromium.launch();const pg=await b.newPage();
await pg.goto('file://'+path.resolve('manual/kit-de-mensagens.html'),{waitUntil:'networkidle'});await pg.waitForTimeout(1200);
await pg.pdf({path:'manual/Kit-de-Mensagens-Bistro-Connect.pdf',format:'A4',printBackground:true,preferCSSPageSize:true});await b.close()})();"""
open("/tmp/ot-kit-pdf.js", "w").write(js)
r = subprocess.run(["node", "/tmp/ot-kit-pdf.js"], capture_output=True, text=True)
print(r.stdout, r.stderr)
total = sum(len(i) for _, _, _, i in S)
print("mensagens:", total)
