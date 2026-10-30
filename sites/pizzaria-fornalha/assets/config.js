/* Configuração do site Fornalha Pizzaria. Este arquivo é público: só a chave "anon" do Supabase, nunca a "service_role". */
window.LOJA = {
  nome: "Fornalha Pizzaria",
  // WhatsApp que recebe os pedidos: DDD + número (ou 55 + DDD + número)
  whatsapp: "",
  // Supabase da loja (opcional). Vazio = cardápio do próprio site e pedido só pelo WhatsApp.
  supabaseUrl: "",
  supabaseKey: "",
  // Cor da marca no painel
  cor: "#D63A2A",
  recursos: { pedidos: true }
};
