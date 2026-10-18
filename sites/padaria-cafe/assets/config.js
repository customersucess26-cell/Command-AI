/* Configuração do site Padaria & Café. Este arquivo é público: só a chave "anon" do Supabase, nunca a "service_role". */
window.LOJA = {
  nome: "Padaria & Café",
  // WhatsApp que recebe as encomendas: 55 + DDD + número, só dígitos. Ex.: "5542999998888"
  whatsapp: "",
  // Supabase da padaria. Vazio = site em modo demonstração (encomendas só pelo WhatsApp, nada fica salvo para a loja).
  supabaseUrl: "",
  supabaseKey: "",
  // identificador da loja no banco (tabela stores). Só mude se criou outra loja no mesmo Supabase.
  slug: "loja",
  // cor da marca na página de rastreio
  cor: "#B0703F"
};
if (!window.LOJA.whatsapp && window.console) console.warn("Padaria: preencha o WhatsApp em assets/config.js");
