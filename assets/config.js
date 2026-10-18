/* Configuração do site eBistrô. Preencha antes de publicar.
   Este arquivo é público: coloque aqui só chaves feitas para o navegador
   (a "anon key" do Supabase, nunca a "service_role"). */
window.BISTRO = {
  // WhatsApp que recebe os contatos: 55 + DDD + número, só dígitos. Ex.: "5542999999999"
  whatsapp: "",
  // ID do Meta Pixel (opcional). Vazio = pixel desligado.
  pixelId: "",
  // Supabase (opcional): grava os leads do formulário e do chat na tabela "leads".
  // A tabela precisa de RLS que permita só INSERT para o papel anon.
  supabaseUrl: "",
  supabaseKey: "",
  // Função que responde no chat com IA (opcional). Vazio = respostas automáticas.
  aiUrl: ""
};
if (!window.BISTRO.whatsapp) console.warn("eBistrô: preencha o WhatsApp em assets/config.js; sem ele os botões de contato não chegam até você.");
