/* Biblioteca do CRM de Sites Personalizados: scripts, objeções e materiais de venda.
   Fonte: Arsenal de Mensagens, Playbook de Vendas e Cartas de Vendas da Bistrô Connect (manual/materiais-vendas/).
   Editar aqui e rodar: python3 ferramentas/montar-crm-sites.py
   Campos entre colchetes ([nome], [Loja], [estabelecimento], [data], [eu], [marca], [chave], [dia]) são preenchidos
   com o lead escolhido na aba Scripts. Os demais ([link], [vídeo], [prato mais elogiado]...) você troca à mão. */
(function () {
'use strict';
var AVISO_OFERTA = 'Cita a oferta anterior (Casa Cheia, Loja no Ar ou garantia de 30 pedidos). Confirme a oferta vigente antes de usar.';

/* As 7 primeiras mensagens mantêm a ordem do CRM (o funil usa cada uma numa etapa). */
window.BC_SCRIPTS = [
 {c:'Funil do CRM', t:'Primeira mensagem', x:'Oi, [nome]! Sou o [eu], da [marca], aqui de Ponta Grossa. Vi as avaliações da [estabelecimento] no Google, parabéns! Montei uma ideia de como ficaria o site de vocês com o pedido direto no WhatsApp, sem comissão por pedido: [link]. Posso te mostrar em 10 minutos esta semana?'},
 {c:'Funil do CRM', t:'Retorno (sem resposta em 2 dias)', x:'Oi, [nome]! Conseguiu ver a ideia do site da [estabelecimento]? Ela já está com a cara de vocês. Se preferir, passo aí rapidinho e te mostro no celular.'},
 {c:'Funil do CRM', t:'Envio da proposta', x:'[nome], como combinamos, segue a proposta do projeto digital da [estabelecimento]. Ela vale até [data]. O site fica no ar em até 7 dias úteis depois que recebermos os materiais. Qualquer dúvida, me chama aqui!'},
 {c:'Funil do CRM', t:'Cobrança da proposta', x:'Oi, [nome]! Conseguiu dar uma olhada na proposta? A validade vai até [data]. Se quiser, ajusto algum item para caber melhor no seu momento.'},
 {c:'Funil do CRM', t:'Pedido de materiais (início da implantação)', x:'Bem-vindo à [marca]! Para começar, me manda por aqui:\n1) logo (PNG ou SVG)\n2) cardápio com preços e opcionais\n3) fotos da fachada, do salão e dos pratos\n4) WhatsApp que recebe os pedidos\n5) endereço, horário e Instagram\n6) bairros atendidos e taxa de entrega\n7) formas de pagamento\n8) domínio (se já tiver)\nO prazo de 7 dias úteis começa quando tudo chegar.'},
 {c:'Funil do CRM', t:'Pedido de indicação', x:'[nome], que bom que o site está trazendo pedidos! Você conhece outro dono de restaurante, café, pizzaria ou hamburgueria que ia gostar? Se ele fechar, o seu próximo mês de mensalidade fica por nossa conta.'},
 {c:'Funil do CRM', t:'Cobrança gentil da mensalidade', x:'Oi, [nome]! Passando para lembrar da mensalidade da [marca] com vencimento dia [dia]. Segue a chave Pix: [chave]. Qualquer coisa me chama!'},

 {c:'Primeiro contato', t:'A · A pergunta que quebra o roteiro', tag:'Operação', x:'Oi, [Nome]! Uma pergunta rápida sobre a [Loja].\nQuando vocês estão no pico dos pedidos, o cliente já consegue montar o pedido sozinho ou alguém precisa ficar conferindo item, quantidade, entrega e endereço nas mensagens?\nPergunto porque trabalho com a Bistrô Connect, e a ideia é justamente fazer o cliente montar o pedido e ele chegar organizado no WhatsApp da loja, sem comissão por pedido.\nTenho um exemplo prático para te mostrar. Posso te enviar?'},
 {c:'Primeiro contato', t:'B · O contra-ataque inteligente', tag:'Canal próprio', x:'[Nome], não vou te sugerir abandonar o iFood.\nA pergunta é outra: quando um cliente que já conhece a [Loja] quer comprar novamente, você tem um jeito simples de levar esse pedido para um canal próprio, sem comissão por pedido?\nA Bistrô Connect foi pensada para esse cenário: o cliente escolhe no seu cardápio e envia o pedido organizado pelo WhatsApp.\nPosso te mostrar essa ideia funcionando?'},
 {c:'Primeiro contato', t:'C · A curiosidade sobre o pedido perdido', tag:'Atrito', x:'Oi, [Nome]. Tem uma pergunta que vale fazer em qualquer negócio de comida:\nQuantas vezes o cliente desiste não porque não quer comprar, mas porque precisa perguntar, esperar resposta, confirmar o total e só então conseguir pedir?\nA Bistrô Connect organiza essa etapa: o cliente escolhe os produtos no cardápio e o pedido chega estruturado no WhatsApp da loja.\nSe esse tipo de situação acontece por aí, posso te mostrar um exemplo bem rápido.'},
 {c:'Primeiro contato', t:'D · Convite para uma análise personalizada', tag:'Diagnóstico', x:'Oi, [Nome]! Vi a [Loja] e queria te propor algo diferente de uma apresentação comercial.\nPosso olhar para o jeito como vocês recebem pedidos e te mostrar uma oportunidade de simplificar esse processo?\nSe fizer sentido, te explico como a Bistrô Connect pode ajudar. Se a operação já estiver redonda, pelo menos a gente não perde tempo com uma solução desnecessária.\nPode ser?'},
 {c:'Primeiro contato', t:'Vídeo da prévia · lista A', tag:'Playbook', x:'Oi, [Nome]! Montei uma ideia de como ficaria o site da [Loja], com o [prato mais elogiado] em destaque e o pedido direto pelo celular. Gravei 1 minutinho mostrando: [vídeo]. Seria loucura pensar em ter isso no ar ainda este mês?'},
 {c:'Primeiro contato', t:'Diagnóstico de 10 minutos · quem vende muito no app', tag:'Playbook', x:'Oi, [Nome]! Faço um diagnóstico de 10 minutos para lojas que vendem pelo [app]: mostro quanto a [Loja] deixa de comissão no ano e quanto dá para trazer de volta para o pedido direto. Te mando o seu número por aqui. Faz sentido para você?'},
 {c:'Primeiro contato', t:'Visita no balcão · 30 segundos', tag:'Playbook', x:'Oi, tudo bem? Sou o [eu], trabalho com restaurantes aqui da cidade. Não vim vender nada agora: fiz uma prévia do site de vocês e queria só mostrar em 30 segundos (mostra o celular). Quem é a melhor pessoa para eu mandar isso, e qual horário é mais tranquilo para conversar 10 minutos?'},

 {c:'Por tipo de casa', t:'Padarias e confeitarias', tag:'Encomendas', x:'Oi, [Nome]! Pensei em uma situação comum em padarias: alguém quer encomendar pão, doces ou um bolo, mas precisa perguntar disponibilidade, preço e horário pelo WhatsApp.\nA Bistrô Connect permite organizar os produtos num cardápio online e receber o pedido estruturado no WhatsApp.\nA [Loja] recebe muitas encomendas pelo WhatsApp hoje?'},
 {c:'Por tipo de casa', t:'Hamburguerias', tag:'Pedido completo', x:'Oi, [Nome]! Em hamburgueria, um pedido pode ter vários detalhes: ponto da carne, adicionais, bebidas e observações.\nQuando tudo fica espalhado nas mensagens, conferir cada detalhe pode dar trabalho.\nA Bistrô Connect permite que o cliente escolha os itens no cardápio e envie o pedido organizado. Hoje vocês recebem muitos pedidos manualmente no WhatsApp?'},
 {c:'Por tipo de casa', t:'Pizzarias', tag:'Personalização', x:'Oi, [Nome]! Tenho uma pergunta sobre os pedidos da [Loja].\nQuando o cliente escolhe sabores, tamanho, adicionais e entrega, ele consegue montar tudo sozinho ou sua equipe precisa confirmar cada detalhe por mensagem?\nPergunto porque a Bistrô Connect organiza a escolha no cardápio e encaminha o pedido completo ao WhatsApp da loja.\nPosso te mostrar um exemplo?'},
 {c:'Por tipo de casa', t:'Cafés e restaurantes', tag:'Atendimento', x:'Oi, [Nome]! Uma ideia para a [Loja]: facilitar para o cliente consultar o cardápio, escolher o que deseja e enviar o pedido sem depender de várias mensagens.\nCom a Bistrô Connect, o pedido vai organizado para o WhatsApp, e o cliente pode acompanhar o andamento pelo link.\nVocês já têm um canal próprio assim ou ainda concentram os pedidos no atendimento manual?'},

 {c:'Depois da resposta', t:'Quando responde: "Pode mandar"', tag:'Interesse', x:'Perfeito, [Nome]. Olha este exemplo:\nhttps://bistroconnect.com.br/gastronomia/\nA proposta é simples: o cliente monta o pedido no cardápio, recebe as opções e envia tudo organizado para o WhatsApp da loja. Você também tem painel para acompanhar os pedidos e link para o cliente acompanhar o andamento.\nPara eu te mostrar a parte mais relevante: hoje os pedidos da [Loja] vêm mais pelo aplicativo, pelo WhatsApp ou pelos dois?'},
 {c:'Depois da resposta', t:'Quando pergunta: "O que vocês fazem exatamente?"', tag:'Explicação', x:'A Bistrô Connect ajuda a loja a ter um canal próprio de pedidos.\nEm vez de o cliente precisar perguntar tudo pelo WhatsApp, ele acessa o cardápio, escolhe os produtos e envia o pedido com os detalhes organizados.\nVocê recebe o pedido no WhatsApp, acompanha tudo pelo painel e o cliente acompanha o andamento.\nTudo isso sem comissão por pedido.\nA ideia é facilitar o pedido direto, não obrigar você a abandonar o que já funciona.'},
 {c:'Depois da resposta', t:'Quando há interesse, mas falta clareza', tag:'Qualificação', x:'Entendi. Antes de falar em plano, quero ver se realmente faz sentido para a [Loja].\nMe conta uma coisa: hoje você gostaria mais de reduzir a dependência das comissões, organizar os pedidos que chegam pelo WhatsApp ou facilitar que os clientes comprem diretamente com você?\nDependendo da sua resposta, eu te mostro só a parte que pode ajudar no seu caso.'},
 {c:'Depois da resposta', t:'Quando a pessoa pergunta o preço (tabela atual)', tag:'Preço', x:'Os valores são fixos e nenhum plano cobra comissão por pedido:\n• Cardápio Digital: R$ 997 de implantação + a partir de R$ 149/mês\n• Site Gastronômico (site com a identidade da casa e cardápio com pedido): R$ 1.497 + R$ 149/mês\n• Digital Experience (site + painel de pedidos e rastreio + Google + 30 dias de acompanhamento): R$ 2.997 + R$ 199/mês\n• Signature (projeto exclusivo, criado do zero): sob orçamento\nPagamento: 50% no início e 50% na entrega, ou parcelado no cartão. A mensalidade tem contrato mínimo de 6 meses; depois você cancela quando quiser.\nMe conta como a [Loja] recebe pedidos hoje que eu te digo qual faz mais sentido.', nota:'Preços atualizados para a tabela da página de vendas. O PDF do Arsenal traz a versão anterior.'},
 {c:'Depois da resposta', t:'Áudio de aproximadamente 25 segundos', tag:'Áudio', x:'Fala, [Nome], tudo bem? Vou resumir a ideia. A Bistrô Connect cria um cardápio próprio para sua loja. O cliente escolhe o que quer, envia o pedido completo para seu WhatsApp e pode acompanhar o andamento. Você não paga comissão por pedido e ainda tem um painel para organizar os produtos e acompanhar as vendas. A ideia é facilitar a operação, não complicar. Quer ver um exemplo de como ficaria para vocês?'},

 {c:'Follow-up', t:'Um novo ponto de vista', tag:'Retomada', x:'Oi, [Nome]! Fiquei pensando numa coisa sobre a rotina da [Loja].\nTalvez você não precise de mais um canal para administrar. Talvez precise que o canal de pedidos que já usa funcione melhor.\nÉ justamente essa a proposta da Bistrô Connect: o cliente monta o pedido e ele chega organizado no WhatsApp.\nIsso resolveria alguma dificuldade da sua operação hoje?'},
 {c:'Follow-up', t:'O custo de não saber', tag:'Cálculo', x:'[Nome], uma última ideia que vale considerar.\nMuita gente compara apenas a mensalidade de uma ferramenta, mas deixa de avaliar quanto custa responder pedidos manualmente, corrigir informações ou pagar comissão nos pedidos que poderiam vir diretamente.\nNão significa que a solução faça sentido para toda loja. O que vale é comparar com os números da sua.\nQuer fazer essa conta comigo?'},
 {c:'Follow-up', t:'Encerramento elegante', tag:'Último contato', x:'Oi, [Nome]! Vou encerrar por aqui para não ocupar seu tempo com mensagens sobre um assunto que talvez não seja prioridade agora.\nSe em algum momento fizer sentido organizar os pedidos pelo WhatsApp ou criar um canal próprio sem comissão por pedido, a Bistrô Connect fica à disposição.\nSucesso para você e para a equipe da [Loja]!'},

 {c:'Fechamento', t:'A · Conectado ao problema', tag:'Direto', x:'[Nome], pelo que você me contou, o ponto principal da [Loja] é [problema mencionado pelo cliente].\nA Bistrô Connect pode ajudar justamente nessa etapa: o cliente monta o pedido no cardápio, você recebe as informações organizadas e acompanha a operação pelo painel.\nMinha sugestão é começarmos pelo que você realmente precisa, sem complicar sua rotina.\nVamos olhar a configuração da [Loja] juntos?'},
 {c:'Fechamento', t:'B · Reduzir o risco percebido', tag:'Confiança', x:'[Nome], você não precisa decidir com base apenas no que eu estou dizendo.\nPodemos avaliar como o cardápio ficaria para a [Loja], quais produtos entrariam primeiro e como seus clientes acessariam o link.\nNão há comissão por pedido, você aprova tudo antes de publicar e paga a segunda metade só na entrega.\nQuer dar o próximo passo e ver como começar?'},
 {c:'Fechamento', t:'C · Pergunta de escolha', tag:'Escolha', x:'Perfeito, [Nome]. Para a [Loja], vejo dois próximos passos possíveis:\nA) Você conhece melhor os modelos e avalia o funcionamento.\nB) A gente olha a sua operação e começa a estruturar o cardápio com os produtos mais importantes.\nQual dos dois faz mais sentido para você agora?'},
 {c:'Fechamento', t:'Escolha entre dois sins', tag:'Playbook', x:'Prefere pagar à vista no Pix ou dividir no cartão?'},
 {c:'Fechamento', t:'Resumo do próprio cliente', tag:'Playbook', x:'Você me disse que paga R$ [valor] por mês e que o cliente fiel pede sempre pelo app. Isso resolve as duas coisas. Faz sentido começar?'},
 {c:'Fechamento', t:'Vaga real', tag:'Playbook', x:'Tenho [2] vagas de site para este mês. Se quiser, eu reservo a da [Loja] agora e começamos as fotos na [dia da semana].', nota:'Só use com o número real de vagas.'},
 {c:'Fechamento', t:'Próximo passo pequeno', tag:'Playbook', x:'Para começar eu só preciso do logo e de 10 fotos. Me manda hoje que amanhã você já vê o rascunho.'},
 {c:'Fechamento', t:'Degrau de baixo', tag:'Playbook', x:'Se o site não cabe agora, começamos pelo Cardápio Digital e você sobe para o site quando os pedidos diretos aparecerem.'},

 {c:'Oferta anterior', t:'Mensagem da oferta Casa Cheia', tag:'Depois da demonstração', aviso:AVISO_OFERTA, x:'[Nome], pelo que você me mostrou, o Casa Cheia resolve tudo de uma vez:\n• Site da [Loja] com domínio próprio\n• Cardápio com pedido direto no WhatsApp, sem comissão\n• Google, 500 cartões de volta e lançamento para os seus clientes\n• 30 dias comigo ajustando tudo\nSeparado, isso passa de R$ 6.800. No Casa Cheia: R$ 2.997 + R$ 199/mês.\nE tem a garantia: se em 60 dias o site não receber 30 pedidos diretos, eu sigo trabalhando sem custo até chegar.\nTenho [2] vagas este mês. Reservo a sua?'}
];

/* Objeções: a fórmula é validar, responder com fato ou número e terminar com uma pergunta. */
window.BC_OBJECOES = [
 {q:'"Já uso iFood."', f:'Arsenal', r:'E faz sentido continuar usando, [Nome]. Não estou propondo abrir mão de um canal que já traz clientes.\nA ideia é criar outra opção para quem já conhece a [Loja] e quer pedir novamente de forma direta, sem comissão por pedido.\nVocê não precisa mudar tudo de uma vez. Quer ver como funcionaria esse segundo canal?'},
 {q:'"Já recebo pedidos pelo WhatsApp."', f:'Arsenal', r:'Ótimo! Então você já tem um canal que seus clientes conhecem.\nA diferença é que, com a Bistrô Connect, o cliente escolhe os produtos, informa os detalhes e envia o pedido estruturado. Você continua recebendo pelo WhatsApp, mas reduz a necessidade de montar cada pedido manualmente.\nHoje o que mais atrapalha nesse processo: responder as dúvidas ou conferir os pedidos?'},
 {q:'"Achei caro." / "Está caro."', f:'Arsenal', r:'Entendo, [Nome]. E não quero te convencer de que vale a pena sem fazer a conta certa.\nO importante é comparar a mensalidade com o benefício que o canal pode trazer, considerando as vendas que realmente migrariam para ele, os descontos que você pretende oferecer e os custos de operação.\nSe você me disser aproximadamente quanto vende hoje pelos aplicativos e qual taxa paga, faço uma simulação para sua loja. Aí você decide com números, não com promessa.'},
 {q:'"Está caro." (venda grande)', f:'Playbook', r:'Entendo. Comparado com o quê? (deixe ele falar)\nVocê me disse que deixa R$ [X] por mês no app. O pacote se paga quando [X ÷ comissão por pedido] clientes passam a pedir direto. É caro ou é investimento que volta?\nProblema de preço é quase sempre problema de valor mal mostrado.'},
 {q:'"Estou sem tempo."', f:'Arsenal', r:'Imagino. Quem está tocando uma loja tem outras prioridades além de aprender um sistema novo.\nPor isso, a proposta é começar de forma simples, com a nossa equipe fazendo a configuração. Você manda fotos e preços, e a gente monta.\nPodemos primeiro olhar um exemplo e verificar se a estrutura faz sentido para sua rotina. Sem precisar decidir agora.'},
 {q:'"Meus clientes não vão usar link."', f:'Arsenal', r:'É uma dúvida justa. Não adianta criar uma ferramenta que ninguém utiliza.\nA vantagem é que seus clientes já estão acostumados a usar o celular para consultar informações e conversar com a loja.\nMinha sugestão seria começar divulgando o link para quem já compra de vocês com frequência, observar a resposta e ajustar a comunicação.\nAssim você testa a aceitação com clientes reais, sem depender de uma previsão.'},
 {q:'"Já tenho site."', f:'Arsenal', r:'Excelente. Ter um site já é um bom ponto de partida.\nA pergunta é se o cliente consegue consultar seus produtos, montar o pedido e enviar os detalhes para sua operação sem depender de várias mensagens.\nA Bistrô Connect tem o cardápio com pedidos integrados e painel de gestão. Dependendo do que seu site já faz, pode haver uma vantagem ou nenhuma necessidade de trocar.\nO que o seu site permite fazer hoje?'},
 {q:'"Vou pensar."', f:'Arsenal', r:'Claro, [Nome]. É uma decisão que precisa fazer sentido para a loja.\nPara eu não ficar te mandando informações sem necessidade: o que você ainda precisa avaliar melhor — o preço, a utilidade para a operação ou se seus clientes vão usar?\nSe eu conseguir esclarecer esse ponto, ótimo. Se não for o momento, sem problema.'},
 {q:'"Me manda o material que depois eu vejo."', f:'Arsenal', r:'Combinado! Aqui está o site com os modelos e os detalhes:\nhttps://bistroconnect.com.br/gastronomia/\nPara facilitar sua avaliação, eu começaria olhando o exemplo do pedido e os planos.\nSe a ideia fizer sentido para a [Loja], podemos depois ver juntos como ficaria na prática.'},
 {q:'"Me manda uma proposta por e-mail."', f:'Playbook', r:'Mando, claro. Antes, para a proposta não ficar genérica: o que precisa estar nela para você dizer sim?\nDepois, envie em PDF de uma página e já marque o retorno.'},
 {q:'"Isso garante que vou vender mais?"', f:'Arsenal', r:'Prefiro ser transparente: não seria correto prometer um aumento de vendas sem conhecer sua operação.\nA Bistrô Connect oferece um canal próprio de pedidos, organização da operação e ausência de comissão por pedido. O resultado depende também de quantos clientes conhecerão e usarão esse canal.\nA melhor maneira de avaliar é testar com seus clientes atuais, acompanhar os pedidos e decidir com dados reais.'},
 {q:'"Não tenho o dinheiro agora."', f:'Playbook', aviso:AVISO_OFERTA, r:'Faz sentido. Por isso existem duas portas: parcelado no cartão, ou 50% agora e 50% na entrega.\nSe nem isso couber, começamos por um plano menor e o próprio pedido direto ajuda a pagar o resto.'},
 {q:'"Vou ver com meu sócio ou esposa."', f:'Playbook', r:'Ótimo, decisão boa é a dois. O que você acha que ele vai perguntar?\nVamos marcar 10 minutos com ele, que eu mostro a conta. Amanhã às [hora] ou quinta às [hora]?'},
 {q:'"Meu sobrinho faz site."', f:'Playbook', r:'Que bom ter alguém de confiança. A diferença está no que vem junto: cardápio com pedido e rastreio, cartão de volta, Google e 30 dias de acompanhamento. O site é a menor parte.'},
 {q:'"Já tentei site e não deu em nada."', f:'Playbook', aviso:AVISO_OFERTA, r:'Isso acontece muito: o site fica bonito e ninguém sabe que existe. Por isso o plano vem com lançamento para a sua lista, cartão na sacola e acompanhamento nos primeiros 30 dias.'},
 {q:'"E se não der resultado?"', f:'Playbook', aviso:AVISO_OFERTA, r:'Apresente a garantia, se ela estiver valendo e escrita no contrato: "O risco fica comigo. Se não chegar em 30 pedidos, eu continuo trabalhando sem custo até chegar."\nSem garantia vigente, use a resposta de "Isso garante que vou vender mais?".'}
];

/* Materiais: arquivos em materiais/ (copiados de manual/materiais-vendas/ pelo montar-crm-sites.py). */
window.BC_MATERIAIS = [
 {id:'playbook', titulo:'Playbook de Vendas', tipo:'Uso interno', pags:15, arq:'playbook-de-vendas.pdf',
  desc:'Meta e funil, os 8 hábitos de quem vende muito, escada de produtos, pontuação do lead, método Prévia Primeiro, cadência de 7 toques, reunião de 15 minutos, objeções, rotina diária, métricas e escala.',
  aviso:'Escrito para a oferta anterior (Casa Cheia, Loja no Ar, Gestão Casa Cheia). O método vale; os preços e nomes dos planos seguem a tabela atual acima.'},
 {id:'arsenal', titulo:'Arsenal de Mensagens', tipo:'Uso interno', pags:16, arq:'arsenal-de-mensagens.pdf',
  desc:'Mensagens prontas para WhatsApp e Instagram: primeiro contato, por tipo de casa, depois da resposta, objeções, follow-up, fechamento e fluxo de conversa. Todas estão na aba Scripts, prontas para copiar.',
  aviso:'A mensagem de preço e a da oferta Casa Cheia são da versão anterior. Na aba Scripts, a de preço já está com a tabela atual.'},
 {id:'carta-v2', titulo:'Carta de Vendas · Site de marca', tipo:'Para o cliente', pags:11, arq:'carta-de-vendas-v2.pdf',
  desc:'Carta de apresentação: a conta da comissão, as seis dores do restaurante, cardápio e pedido, rastreio, painel, cartão de volta, investimento e os sites de marca.',
  aviso:'Mostra Cardápio Digital a R$ 497 + R$ 149/mês e Casa Cheia a R$ 2.997. Confira se esses valores ainda valem antes de enviar.'},
 {id:'carta-plataforma', titulo:'Carta de Vendas · Plataforma', tipo:'Para o cliente', pags:11, arq:'carta-de-vendas-plataforma.pdf',
  desc:'Versão para a plataforma de cardápio e pedidos, com mensalidade por faixa de venda (R$ 49 a R$ 199) e sem taxa de implantação.',
  aviso:'É a oferta da plataforma, não a dos sites personalizados. Use só para quem vai entrar pela plataforma.'}
];

window.BC_PLANOS_ATUAIS = [
 ['Cardápio Digital','R$ 997','a partir de R$ 149/mês','Cardápio interativo e pedido enviado ao WhatsApp'],
 ['Site Gastronômico','R$ 1.497','R$ 149/mês','Site com a identidade da casa, cardápio com pedido, domínio próprio, QR Code e links'],
 ['Digital Experience','R$ 2.997','R$ 199/mês','Tudo do Site Gastronômico + painel de pedidos e rastreio, Google otimizado, 500 cartões de volta e display, campanha de lançamento e 30 dias de acompanhamento'],
 ['Signature','Sob orçamento','Sob orçamento','Projeto exclusivo, criado do zero']
];

/* ---------- desenho das abas novas ---------- */
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function $(s){return document.querySelector(s)}
var ICO_PDF='<svg viewBox="0 0 24 24"><path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5"/></svg>';

function desenhaMateriais(){
  var el=$('#bibMateriais');if(!el)return;
  var planos='<section class="bib-sec"><div class="bib-sec-cab"><div><span class="bib-kicker">Use esta na conversa</span><h2>Tabela de preços vigente</h2></div><p class="muted fino">Pagamento 50% no aceite e 50% na entrega, ou parcelado no cartão. Mensalidade a partir da publicação, contrato mínimo de 6 meses. Prazo de até 7 dias úteis depois dos materiais.</p></div>'+
    '<div class="bib-planos">'+window.BC_PLANOS_ATUAIS.map(function(p,i){return '<article class="bib-plano'+(i===2?' destaque':'')+'">'+(i===2?'<span class="bib-selo">Mais completo</span>':'')+
      '<h3>'+esc(p[0])+'</h3><div class="bib-preco"><b>'+esc(p[1])+'</b><span>'+(/orçamento/i.test(p[1])?'':'implantação')+'</span></div><div class="bib-mens">'+esc(p[2])+'</div><p>'+esc(p[3])+'</p></article>'}).join('')+'</div></section>';
  var grupos=[['Uso interno','Para a equipe estudar e consultar'],['Para o cliente','Pode enviar ou apresentar']];
  var docs=grupos.map(function(g){var lista=window.BC_MATERIAIS.filter(function(m){return m.tipo===g[0]});
    return '<section class="bib-sec"><div class="bib-sec-cab"><div><span class="bib-kicker">'+esc(g[1])+'</span><h2>'+esc(g[0])+'</h2></div></div><div class="bib-docs">'+lista.map(function(m){
      var url='materiais/'+m.arq,capa='materiais/capa-'+m.arq.replace(/\.pdf$/,'')+'.jpg';
      return '<article class="bib-doc"><a class="bib-capa" href="'+esc(url)+'" target="_blank" rel="noopener" aria-label="Abrir '+esc(m.titulo)+'"><img src="'+esc(capa)+'" alt="" loading="lazy"><span>'+ICO_PDF+' '+m.pags+' páginas</span></a>'+
        '<div class="bib-doc-txt"><h3>'+esc(m.titulo)+'</h3><p class="muted">'+esc(m.desc)+'</p>'+(m.aviso?'<details class="bib-aviso-d"><summary>Atenção antes de usar</summary><p>'+esc(m.aviso)+'</p></details>':'')+
        '<div class="acoes-linha"><a class="btn small primary" href="'+esc(url)+'" target="_blank" rel="noopener">Abrir</a><a class="btn small" href="'+esc(url)+'" download>Baixar</a>'+
        (m.tipo==='Para o cliente'?'<button class="btn small" type="button" data-copiar-link="'+esc(url)+'">Copiar link</button>':'')+'</div></div></article>'}).join('')+'</div></section>'}).join('');
  el.innerHTML=planos+docs;
}

var objSel=0;
function desenhaObjecoes(){
  var el=$('#bibObjecoes');if(!el)return;var b=String(($('#objBusca')||{}).value||'').toLowerCase().trim();
  var vis=[];window.BC_OBJECOES.forEach(function(o,i){if(!b||(o.q+' '+o.r).toLowerCase().indexOf(b)>=0)vis.push(i)});
  if(vis.indexOf(objSel)<0)objSel=vis.length?vis[0]:-1;
  var lista=vis.map(function(i){var o=window.BC_OBJECOES[i];return '<button type="button" class="sc-item'+(i===objSel?' on':'')+'" data-obj="'+i+'"><b>'+esc(o.q)+'</b><span>'+esc(o.f)+(o.aviso?' · confira a oferta':'')+'</span></button>'}).join('');
  var o=objSel>=0?window.BC_OBJECOES[objSel]:null;
  var leitor=o?'<div class="sc-cab"><div><span class="sc-cat">Cliente diz</span><h3>'+esc(o.q)+'</h3></div><span class="chip">'+esc(o.f)+'</span></div>'+
    (o.aviso?'<p class="bib-aviso">'+esc(o.aviso)+'</p>':'')+'<pre class="sc-texto" id="objTxt">'+esc(o.r)+'</pre>'+
    '<div class="sc-acoes"><button class="btn primary" type="button" data-copiar="objTxt">Copiar resposta</button></div>'+
    '<div class="obj-formula"><b>A fórmula</b><ol><li>Valide: “faz sentido”, “entendo”.</li><li>Responda com um fato ou um número, nunca com opinião.</li><li>Termine com uma pergunta que leva ao próximo passo.</li></ol></div>'
    :'<div class="sc-vazio">Nenhuma objeção com esse termo.</div>';
  el.innerHTML='<div class="sc-split"><nav class="sc-lista" aria-label="Objeções">'+(lista||'<p class="muted fino" style="padding:12px">Nada encontrado.</p>')+'</nav><div class="sc-leitor box">'+leitor+'</div></div>';
}

/* manual: índice lateral com os títulos, rolagem até a seção e destaque da seção aberta */
function montaIndice(){
  var nav=$('#hpIndice'),lista=$('#hpLista');if(!nav||!lista)return;var html='',n=0;
  [].forEach.call(lista.children,function(el){
    if(el.tagName==='H3'){html+='<span class="hp-ind-grupo">'+esc(el.textContent)+'</span>'}
    else if(el.matches&&el.matches('details.hp')){var id='hp'+(n++);el.id=id;html+='<a href="#'+id+'" data-hp="'+id+'">'+esc(el.querySelector('summary').textContent)+'</a>'}
  });
  nav.innerHTML=html;
  nav.addEventListener('click',function(e){var a=e.target.closest('[data-hp]');if(!a)return;e.preventDefault();var d=document.getElementById(a.dataset.hp);if(!d)return;d.open=true;d.hidden=false;d.scrollIntoView({behavior:'smooth',block:'start'});marca(a.dataset.hp)});
  lista.addEventListener('toggle',function(e){if(e.target.open)marca(e.target.id)},true);
  function marca(id){[].forEach.call(nav.querySelectorAll('a'),function(x){x.classList.toggle('on',x.dataset.hp===id)})}
}
function copiar(txt){
  if(navigator.clipboard)return navigator.clipboard.writeText(txt).then(function(){aviso('Copiado')},function(){aviso('Selecione e copie com Ctrl+C')});
  aviso('Selecione e copie com Ctrl+C');
}
function aviso(t){var x=$('#toast');if(!x)return;x.textContent=t;x.hidden=false;clearTimeout(aviso.t);aviso.t=setTimeout(function(){x.hidden=true},2600)}
document.addEventListener('click',function(e){
  var c=e.target.closest('[data-copiar]');if(c){var p=document.getElementById(c.dataset.copiar);if(p)copiar(p.textContent);return}
  var l=e.target.closest('[data-copiar-link]');if(l){copiar(new URL(l.dataset.copiarLink,location.href).href);return}
  var ob=e.target.closest('[data-obj]');if(ob){objSel=+ob.dataset.obj;desenhaObjecoes()}
});
document.addEventListener('input',function(e){if(e.target&&e.target.id==='objBusca')desenhaObjecoes()});
function inicia(){desenhaMateriais();desenhaObjecoes();montaIndice()}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',inicia);else inicia();
})();
