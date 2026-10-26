// Bistrô Connect · whats-webhook
// Recebe da Meta (WhatsApp Cloud API) as mensagens que chegam no número da loja, guarda no banco
// (aparecem no painel, aba Atendimento) e, com o robô ligado, responde o básico sozinho:
// cardápio, "cadê meu pedido?", horário/endereço, entrega e pagamento, e chama a equipe quando pedem.
//
// Segredos (Supabase › Edge Functions › Secrets):
//   WA_VERIFY_TOKEN  frase combinada com a Meta na hora de cadastrar o webhook
//   WA_APP_SECRET    "Chave secreta do app" (Meta › App › Configurações › Básico): confere que quem chama é a Meta
//   WA_TOKEN         token permanente do usuário do sistema (usado quando a loja não tem token próprio)
//   SITE_URL         opcional, padrão https://bistroconnect.com.br
// Esta função precisa ficar com "Verify JWT" DESLIGADO (a Meta não manda login do Supabase).

const env = (k: string, d = "") => Deno.env.get(k) ?? d;
const REST = env("REST_URL", env("SUPABASE_URL") + "/rest/v1");
const SERVICE = env("SUPABASE_SERVICE_ROLE_KEY");
const GRAPH = env("GRAPH_URL", "https://graph.facebook.com/v21.0");
const SITE = env("SITE_URL", "https://bistroconnect.com.br").replace(/\/+$/, "");

async function rpc(fn: string, args: Record<string, unknown>) {
  const r = await fetch(`${REST}/rpc/${fn}`, {
    method: "POST",
    headers: { apikey: SERVICE, Authorization: `Bearer ${SERVICE}`, "Content-Type": "application/json" },
    body: JSON.stringify(args),
  });
  const t = await r.text();
  if (!r.ok) throw new Error(`${fn}: ${r.status} ${t}`);
  return t ? JSON.parse(t) : null;
}

async function confereAssinatura(corpo: string, cabecalho: string | null) {
  const segredo = env("WA_APP_SECRET");
  if (!segredo) return true; // sem segredo configurado (só em teste)
  if (!cabecalho?.startsWith("sha256=")) return false;
  const chave = await crypto.subtle.importKey("raw", new TextEncoder().encode(segredo), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = new Uint8Array(await crypto.subtle.sign("HMAC", chave, new TextEncoder().encode(corpo)));
  const hex = [...sig].map((b) => b.toString(16).padStart(2, "0")).join("");
  const veio = cabecalho.slice(7);
  if (veio.length !== hex.length) return false;
  let dif = 0;
  for (let i = 0; i < hex.length; i++) dif |= hex.charCodeAt(i) ^ veio.charCodeAt(i);
  return dif === 0;
}

export async function enviaTexto(phoneNumberId: string, token: string, para: string, texto: string) {
  const r = await fetch(`${GRAPH}/${phoneNumberId}/messages`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({ messaging_product: "whatsapp", recipient_type: "individual", to: para, type: "text", text: { preview_url: true, body: texto } }),
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error("Meta: " + (j?.error?.message || r.status));
  return String(j?.messages?.[0]?.id || "");
}

// ---------------- robô ----------------
type Loja = { nome: string; slug: string; horario: string; endereco: string; taxa: number; minimo: number; aberta: boolean; entrega: boolean; retirada: boolean; pagamentos: string[] };
type Pedido = { code: string; status: string; tipo: string; track_code: string; total: number; pago: boolean } | null;

const brl = (n: number) => "R$ " + Number(n || 0).toFixed(2).replace(".", ",");
const norm = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

export function intencao(texto: string): string {
  const t = " " + norm(texto).replace(/[^a-z0-9 ]+/g, " ").replace(/\s+/g, " ").trim() + " ";
  const n = t.trim();
  if (n === "1") return "cardapio";
  if (n === "2") return "pedido";
  if (n === "3") return "horario";
  if (n === "4") return "entrega";
  if (n === "5") return "equipe";
  if (/ (atendente|humano|pessoa|alguem|falar com|reclama|problema|errad|cancel)/.test(t)) return "equipe";
  if (/ (cade|meu pedido|status|demora|chega|saiu|acompanh|rastre|ja vem|vai demorar|previsao)/.test(t)) return "pedido";
  if (/ (cardapio|menu|preco|valor|quanto custa|quero pedir|fazer pedido|fazer um pedido|tem (o que|oq)|opcoes)/.test(t)) return "cardapio";
  if (/ (horario|abre|abert|fecha|funciona|endereco|onde fica|localiza|como chego)/.test(t)) return "horario";
  if (/ (entrega|entregam|taxa|frete|delivery|retir|buscar)/.test(t)) return "entrega";
  if (/ (pagamento|pagar|pix|cartao|dinheiro|debito|credito)/.test(t)) return "pagamento";
  if (/ (obrigad|valeu|vlw|show|perfeito|top)/.test(t)) return "obrigado";
  if (/ (oi|ola|bom dia|boa tarde|boa noite|eai|e ai|opa) /.test(t)) return "oi";
  return "";
}

function statusPedido(p: NonNullable<Pedido>) {
  const ent = p.tipo === "entrega";
  const frase: Record<string, string> = {
    novo: `Recebemos o seu pedido ${p.code} e já vamos confirmar.`,
    confirmado: `O seu pedido ${p.code} foi confirmado.`,
    em_preparo: `O seu pedido ${p.code} está sendo preparado agora.`,
    pronto: ent ? `O seu pedido ${p.code} saiu para entrega!` : `O seu pedido ${p.code} está pronto para retirar.`,
    entregue: ent ? `O seu pedido ${p.code} já foi entregue. Bom apetite!` : `O seu pedido ${p.code} já foi retirado. Bom apetite!`,
    cancelado: `O pedido ${p.code} foi cancelado. Se tiver alguma dúvida, responda aqui que a equipe te atende.`,
  };
  let t = frase[p.status] || `O seu pedido ${p.code} está em andamento.`;
  if (p.track_code && p.status !== "cancelado") t += `\n\nAcompanhe em tempo real:\n${SITE}/p/${p.track_code}`;
  return t;
}

const OPCOES = "Responda com um número:\n1 - Cardápio e pedido\n2 - Meu pedido\n3 - Horário e endereço\n4 - Entrega e pagamento\n5 - Falar com a equipe";

export function resposta(texto: string, nome: string, nova: boolean, l: Loja, p: Pedido): { texto: string; modo?: string } | null {
  const link = `${SITE}/l/${l.slug}`;
  const primeiro = String(nome || "").trim().split(/\s+/)[0] || "";
  const ola = `Olá${primeiro ? ", " + primeiro : ""}! Aqui é ${l.nome}.`;
  const fechada = l.aberta ? "" : "\n\nNo momento não estamos recebendo pedidos pelo cardápio. Assim que voltarmos, é só pedir por lá.";
  const entrega = [
    l.entrega ? (l.taxa > 0 ? `Entregamos com taxa de ${brl(l.taxa)}` : "A entrega é grátis") + (l.minimo > 0 ? `, pedido mínimo de ${brl(l.minimo)}` : "") + "." : "",
    l.retirada ? (l.endereco ? `Também dá para retirar aqui: ${l.endereco}.` : "Também dá para retirar na loja.") : "",
  ].filter(Boolean).join("\n");
  const pags = (l.pagamentos || []).join(", ");
  const it = intencao(texto);
  const prefixo = nova ? ola + "\n\n" : "";
  switch (it) {
    case "cardapio":
      return { texto: `${prefixo}Aqui está o nosso cardápio, com fotos e preços:\n${link}\n\nVocê escolhe, confirma e o pedido chega certinho para a gente.${fechada}` };
    case "pedido":
      if (p) return { texto: prefixo + statusPedido(p), modo: p.status === "cancelado" ? "humano" : undefined };
      return { texto: `${prefixo}Não encontrei pedido recente feito com este número. Me diga o seu nome que alguém da equipe confere para você.`, modo: "humano" };
    case "horario":
      return { texto: prefixo + ([l.horario ? `Nosso horário: ${l.horario}.` : "", l.endereco ? `Endereço: ${l.endereco}.` : ""].filter(Boolean).join("\n") || "Já chamei alguém da equipe para te passar o horário de hoje."), modo: l.horario || l.endereco ? undefined : "humano" };
    case "entrega":
      return { texto: prefixo + [entrega, pags ? `Formas de pagamento: ${pags}.` : ""].filter(Boolean).join("\n\n") + `\n\nPara pedir: ${link}` };
    case "pagamento":
      return { texto: prefixo + (pags ? `Aceitamos: ${pags}.` : "Já chamei alguém da equipe para combinar o pagamento.") + `\n\nPara pedir: ${link}` };
    case "equipe":
      return { texto: `${prefixo}Certo! Já chamei alguém da equipe. É só aguardar um pouquinho que já te respondemos por aqui.`, modo: "humano" };
    case "obrigado":
      return nova ? null : { texto: "Nós que agradecemos! Quando quiser pedir de novo:\n" + link };
  }
  if (!nova && it !== "oi") return null; // conversa em andamento e o robô não entendeu: fica para a equipe
  let t = `${ola}\n\nPara pedir, é só abrir o nosso cardápio:\n${link}${fechada}`;
  if (p && !["entregue", "cancelado"].includes(p.status)) t += "\n\n" + statusPedido(p);
  return { texto: t + "\n\n" + OPCOES };
}

// ---------------- mensagem da Meta → banco ----------------
function conteudo(m: any): { tipo: string; texto: string; midia: string } {
  const tipo = String(m.type || "text");
  switch (tipo) {
    case "text": return { tipo, texto: m.text?.body || "", midia: "" };
    case "image": case "video": case "document": case "sticker":
      return { tipo, texto: m[tipo]?.caption || m[tipo]?.filename || "", midia: m[tipo]?.id || "" };
    case "audio": return { tipo, texto: "", midia: m.audio?.id || "" };
    case "button": return { tipo: "text", texto: m.button?.text || "", midia: "" };
    case "interactive": return { tipo: "text", texto: m.interactive?.button_reply?.title || m.interactive?.list_reply?.title || "", midia: "" };
    case "location": {
      const lc = m.location || {};
      return { tipo, texto: [lc.name, lc.address, `https://maps.google.com/?q=${lc.latitude},${lc.longitude}`].filter(Boolean).join("\n"), midia: "" };
    }
    case "reaction": return { tipo, texto: m.reaction?.emoji || "", midia: "" };
    default: return { tipo, texto: "", midia: "" };
  }
}

async function trataMensagem(v: any, m: any) {
  const phoneId = String(v.metadata?.phone_number_id || "");
  const contato = (v.contacts || []).find((c: any) => c.wa_id === m.from) || v.contacts?.[0] || {};
  const c = conteudo(m);
  const quando = new Date(Number(m.timestamp || 0) * 1000 || Date.now()).toISOString();
  const r = await rpc("whats_recebe", {
    p_phone_number_id: phoneId, p_wa_id: String(m.from), p_nome: contato.profile?.name || "", p_wamid: String(m.id || ""),
    p_tipo: c.tipo, p_texto: c.texto, p_midia: c.midia, p_quando: quando,
  });
  if (!r?.ok || !r.responde || c.tipo === "reaction") return;
  const resp = resposta(c.texto, contato.profile?.name || "", !!r.nova, r.loja, r.pedido);
  if (!resp) return;
  const token = r.token || env("WA_TOKEN");
  let wamid = "", status = "sent";
  try { wamid = await enviaTexto(r.phone_number_id, token, r.wa_id, resp.texto); }
  catch (e) { status = "failed"; console.error(e); }
  await rpc("whats_saida", { p_conversa: r.conversa_id, p_texto: resp.texto, p_wamid: wamid, p_autor: "robô", p_status: status, p_modo: resp.modo ?? null });
}

export async function trata(corpo: any) {
  for (const e of corpo?.entry || []) {
    for (const ch of e.changes || []) {
      if (ch.field !== "messages") continue;
      const v = ch.value || {};
      for (const m of v.messages || []) {
        try { await trataMensagem(v, m); } catch (err) { console.error(err); }
      }
      for (const s of v.statuses || []) {
        try { await rpc("whats_status", { p_wamid: String(s.id), p_status: String(s.status) }); } catch (err) { console.error(err); }
      }
    }
  }
}

if (import.meta.main) Deno.serve(async (req) => {
  const url = new URL(req.url);
  if (req.method === "GET") {
    // a Meta confere o endereço uma vez, na hora de cadastrar o webhook
    const ok = url.searchParams.get("hub.mode") === "subscribe" && env("WA_VERIFY_TOKEN") !== "" &&
      url.searchParams.get("hub.verify_token") === env("WA_VERIFY_TOKEN");
    return ok ? new Response(url.searchParams.get("hub.challenge") || "", { status: 200 }) : new Response("proibido", { status: 403 });
  }
  if (req.method !== "POST") return new Response("método não aceito", { status: 405 });
  const bruto = await req.text();
  if (!(await confereAssinatura(bruto, req.headers.get("x-hub-signature-256")))) return new Response("assinatura inválida", { status: 401 });
  let corpo: any;
  try { corpo = JSON.parse(bruto); } catch { return new Response("ok"); }
  await trata(corpo);
  return new Response("ok");
});
