/* Proposta Mr. Connect: padrões por plano (texto da capa, o que está incluído, etapas e garantia).
   O desenho da folha (2 páginas A4) está em painel.js (drawSheet), montado por ferramentas/montar-crm-sites.py.
   Editar aqui e rodar o montador de novo. {est} vira o nome do estabelecimento. */
window.MC_PROPOSTA = {
  garantia: 'Se o que for publicado não corresponder a esta proposta, ajustamos sem custo até a sua aprovação.',
  cuidado: 'Plano de cuidado',
  /* marca que assina a proposta: gastronomia = Bistrô Connect; outros nichos = Mr. Connect */
  marcas: {
    bistro: { nome: 'Bistrô Connect', slogan: 'A evolução digital da sua gastronomia', logo: 'img/logo-bistro-connect-clara.png' },
    mc: { nome: 'Mr. Connect', slogan: 'A evolução digital da sua marca.' }
  },
  marcaDoPlano: { 'Cardápio Digital': 'bistro', 'Site Gastronômico': 'bistro', 'Digital Experience': 'bistro', 'Signature': 'bistro', 'Página comercial': 'mc', 'Site institucional': 'mc' },
  planos: {
    'Página comercial': {
      titulo: 'Página comercial com painel de leads',
      intro: 'Uma página que apresenta o seu trabalho com autoridade, leva o visitante até o contato e entrega cada pedido organizado num painel só seu.',
      incluido: 'A página: Design sob medida com a sua identidade visual; Texto de vendas estruturado como uma oferta; Versão para celular desenhada à parte\nCaptação: Formulário que abre o WhatsApp com os dados preenchidos; Painel de leads com funil, agenda e histórico; Login em duas etapas e dados em seu nome\nEntrega: Publicação no seu domínio; Treinamento do painel por videochamada; 30 dias de ajustes após a publicação',
      etapas: 'Dia 1 | Aceite | Assinatura e primeira parcela\nDia 2 a 4 | Revisão | Você testa e pede ajustes\nDia 5 | Publicação | Página e painel no seu domínio\nDia 6 | Treinamento | Videochamada para usar o painel'
    },
    'Site institucional': {
      titulo: 'Site institucional sob medida',
      intro: 'Um site que apresenta a {est} com clareza e autoridade, pensado para transformar visitas em contatos.',
      incluido: 'O site: Design sob medida com a sua identidade visual; Páginas de serviços, sobre e contato; Versão para celular desenhada à parte\nCaptação: Formulário e botão de WhatsApp; Pronto para aparecer no Google; Integração com Instagram\nEntrega: Publicação no seu domínio; Treinamento por videochamada; 30 dias de ajustes após a publicação',
      etapas: 'Dia 1 | Aceite | Assinatura e primeira parcela\nDia 2 a 5 | Criação | Design e textos com os seus materiais\nDia 6 a 7 | Revisão | Você testa e pede ajustes\nAté o dia 10 | Publicação | No ar no seu domínio e treinamento'
    },
    'Cardápio Digital': {
      titulo: 'Cardápio digital com pedido direto',
      intro: 'Um cardápio com a cara da {est}, que o cliente abre pelo celular, monta o pedido e envia pronto para o seu WhatsApp. Sem comissão por pedido.',
      incluido: 'O cardápio: Fotos, categorias, preços e opcionais; Link próprio para a bio e o WhatsApp; QR Code para mesas e balcão\nPedidos: Pedido chega pronto no WhatsApp do seu negócio; Total calculado pelo sistema; Entrega ou retirada e forma de pagamento\nEntrega: Cadastro do cardápio pela nossa equipe; Treinamento da equipe; Suporte pelo WhatsApp',
      etapas: 'Dia 1 | Aceite | Assinatura e primeira parcela\nDia 2 a 4 | Montagem | Cadastramos o cardápio com os seus materiais\nDia 5 | Revisão | Você testa e pede ajustes\nAté o dia 7 | No ar | QR Codes, link e treinamento da equipe'
    },
    'Site Gastronômico': {
      titulo: 'Site gastronômico com pedido direto',
      intro: 'Um site com a identidade da {est}, que apresenta a sua marca com autoridade e leva o cliente direto ao pedido, com tudo organizado no WhatsApp e sem comissão.',
      incluido: 'O site: Design com a identidade visual da sua marca; Fotos, história, horários e mapa; Versão para celular desenhada à parte\nPedidos: Cardápio com pedido no WhatsApp; Opcionais e taxa de entrega por bairro; QR Code e links para as redes\nEntrega: Publicação no seu domínio com HTTPS; Treinamento da equipe; Ajustes até a sua aprovação',
      etapas: 'Dia 1 | Aceite | Assinatura e primeira parcela\nDia 2 a 4 | Montagem | Site e cardápio com os seus materiais\nDia 5 a 6 | Revisão | Você testa e pede ajustes\nAté o dia 7 | Publicação | No ar no seu domínio e equipe treinada'
    },
    'Digital Experience': {
      titulo: 'Canal próprio de pedidos completo',
      intro: 'Site, painel de pedidos e lançamento para que quem já conhece a {est} passe a pedir direto, com a operação organizada do pedido à entrega.',
      incluido: 'O site: Design com a identidade visual da sua marca; Cardápio com pedido no WhatsApp; Publicação no seu domínio com HTTPS\nPedidos e painel: Painel com alerta e quadro por etapa; Rastreio do pedido para o cliente; 500 cartões de volta e display de balcão\nLançamento: Perfil da empresa no Google ajustado, com o seu acesso; Peças de lançamento para redes e WhatsApp; 30 dias de acompanhamento',
      etapas: 'Dia 1 | Aceite | Assinatura e primeira parcela\nDia 2 a 4 | Montagem | Site, cardápio e painel prontos\nDia 5 a 6 | Revisão | Você testa e pede ajustes\nAté o dia 7 | Lançamento | No ar, equipe treinada e peças de lançamento'
    },
    'Signature': {
      titulo: 'Projeto digital exclusivo',
      intro: 'Uma experiência criada do zero a partir da marca {est}: estratégia, direção criativa, design e desenvolvimento sob medida.',
      incluido: 'Estratégia: Imersão no negócio e no público; Diagnóstico e referências; Arquitetura da informação\nCriação: Direção criativa e conceito; Design exclusivo, sem modelo; Versão para celular desenhada à parte\nEntrega: Desenvolvimento e integrações; Publicação no seu domínio; Treinamento e acompanhamento',
      etapas: 'Semana 1 | Imersão | Entrevista, referências e diagnóstico\nSemana 2 | Direção criativa | Conceito e estrutura aprovados\nSemanas 3 e 4 | Design e código | Telas e desenvolvimento\nFinal | Publicação | Ajustes, publicação e treinamento'
    }
  }
};
