/* Configuração do site · tudo que muda de um cliente para outro fica AQUI. O HTML do modelo não é editado.
   Este arquivo é público: só a chave "anon" do Supabase, nunca a "service_role". Gerado por ferramentas/novo-cliente.py */

/* Motor Bistrô Connect (banco da plataforma). Vazio = modo demonstração: cardápio do próprio site e pedido só pelo WhatsApp. */
window.BC = {
  supabaseUrl: "https://wiykwrnviqyrywelpawf.supabase.co",
  supabaseKey: "",  // cole aqui a chave anon (a mesma do plataforma/assets/config.js do servidor). Vazia = modo demonstração
  site: "",         // endereço do site do cliente, sem barra no fim (ex.: "https://brutoburger.com.br"). Vazio = o endereço atual
  plataforma: "https://bistroconnect.com.br"    // endereço da plataforma (ex.: "https://app.bistroconnect.com.br"), para fotos cadastradas com caminho dela
};

window.LOJA = {
  slug: "hamburgueria",  // identificador da loja na plataforma (o mesmo usado no painel)
  nome: "Bruto Burger Co.",
  whatsapp: "",     // WhatsApp que recebe os pedidos (55 + DDD + número). O painel pode trocar depois.
  cor: "#E0301E",   // cor da marca no painel e no rastreio
  recursos: { pedidos: true },

  marca: {
    titulo: "",       // título da aba e do Google. Vazio = o do modelo
    descricao: "",    // resumo que aparece no Google
    logo: "",         // logo em imagem (ex.: "img/logo.png"). Vazio = logotipo em texto (textos.logo)
    corNavegador: "",
    cores: {},        // variáveis do modelo, ex.: { ember: "#FF6A1A", red: "#E0301E", mustard: "#F4B63A", bg: "#0D0C0B", cream: "#F3E9D8" }
    fontes: {}        // opcional: { url: "https://fonts.googleapis.com/css2?family=...", display: "\"Anton\", sans-serif", script: "...", body: "..." }
  },

  /* textos do site (vazio = texto do modelo). Chaves: veja o data-t de cada elemento no index.html ou o LEIA-ME do modelo */
  textos: {},

  /* fotos (vazio = foto do modelo): hero, fogo, batata e as fotos do cardápio de demonstração */
  imagens: {},

  /* contato mostrado no site antes de o painel carregar (o painel tem a palavra final) */
  contato: { endereco: "", horario: "", instagram: "", whatsappTexto: "" },

  /* blocos que não se aplicam a este cliente, ex.: ["depoimentos"] enquanto não houver depoimentos reais */
  ocultar: []
};
