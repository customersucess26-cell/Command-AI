/* Configuração da plataforma Bistrô Connect. Este arquivo é público: só chaves feitas para o navegador
   (a chave "anon" do Supabase, IDs de Pixel e do Google). Nunca coloque aqui a "service_role". */
window.BC = {
  nome: "Bistrô Connect",
  // Supabase da PLATAFORMA (Project Settings > API): URL e chave anon/public
  supabaseUrl: "",
  supabaseKey: "",
  // WhatsApp do suporte da plataforma (55 + DDD + número)
  suporteWhatsapp: "",
  // endereço público da plataforma, sem barra no fim (ex.: "https://bistroconnect.com.br"). Vazio = o endereço atual.
  site: "",

  // ---- Campanhas (opcional). Vazio = desligado. Só carregam depois que o visitante aceita os cookies. ----
  // Meta Pixel: Gerenciador de Eventos > Fontes de dados > ID do conjunto de dados (só números)
  pixelId: "",
  // Google Ads: Metas > Conversões > Configurar tag. O ID começa com AW-
  googleAdsId: "",
  // Rótulo da conversão "Loja criada" (o texto depois da barra em AW-123456789/AbCdEf...)
  googleAdsRotuloLoja: "",
  // Rótulo da conversão "Pedido de ajuda" (formulário "Quero ajuda para montar")
  googleAdsRotuloLead: "",
  // Google Analytics 4: Administrador > Fluxos de dados. O ID começa com G-
  googleAnalyticsId: "",

  // ---- Dados da empresa (aparecem nos Termos de uso e na Política de privacidade) ----
  empresa: {
    razaoSocial: "",   // ex.: "Adilson Rutes Marketing Digital LTDA"
    cnpj: "",          // ex.: "00.000.000/0001-00"
    email: "",         // e-mail para assuntos de privacidade e suporte
    cidade: ""         // ex.: "Ponta Grossa/PR" (foro dos Termos)
  }
};

/* Seu painel de leads (CRM, em /crm/) e o formulário "Quero ajuda para montar" da página de vendas.
   Use o Supabase do SITE OFICIAL (projeto "site-oficial", onde ficam os leads), NÃO o da plataforma. */
window.BISTRO = {
  whatsapp: window.BC.suporteWhatsapp,
  supabaseUrl: "",
  supabaseKey: ""
};
