// Bistrô Connect · whats-enviar
// Chamada pelo painel (aba Atendimento) com o login da pessoa da equipe:
//   { acao: "enviar", conversa, texto, auto? }  manda a resposta para o WhatsApp do cliente (auto = aviso do sistema, o robô continua)
//   { acao: "midia", mensagem }          devolve a foto/áudio que o cliente mandou
// A permissão é conferida no banco (whats_responder / whats_midia), com o login de quem chamou.
// Segredos: WA_TOKEN (token geral, quando a loja não tem token próprio). "Verify JWT" pode ficar ligado.

const env = (k: string, d = "") => Deno.env.get(k) ?? d;
const REST = env("REST_URL", env("SUPABASE_URL") + "/rest/v1");
const SERVICE = env("SUPABASE_SERVICE_ROLE_KEY");
const ANON = env("SUPABASE_ANON_KEY");
const GRAPH = env("GRAPH_URL", "https://graph.facebook.com/v21.0");
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const json = (o: unknown, status = 200) => new Response(JSON.stringify(o), { status, headers: { ...CORS, "Content-Type": "application/json" } });

async function rpc(fn: string, args: Record<string, unknown>, jwt?: string) {
  const r = await fetch(`${REST}/rpc/${fn}`, {
    method: "POST",
    headers: { apikey: jwt ? ANON : SERVICE, Authorization: `Bearer ${jwt || SERVICE}`, "Content-Type": "application/json" },
    body: JSON.stringify(args),
  });
  const t = await r.text();
  const j = t ? JSON.parse(t) : null;
  if (!r.ok) {
    const e = new Error(j?.message || `${fn}: ${r.status}`) as Error & { hint?: string; code?: string; status?: number };
    e.hint = j?.hint; e.code = j?.code; e.status = r.status;
    throw e;
  }
  return j;
}

// celular do Brasil que chega sem o 9 (55 + DDD + 8 dígitos) é enviado com o 9
const comNove = (n: string) => /^55\d{2}[6-9]\d{7}$/.test(n) ? n.slice(0, 4) + "9" + n.slice(4) : n;

async function tokenDa(loja: string) {
  return (await rpc("whats_token", { p_loja: loja })) || env("WA_TOKEN");
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return json({ erro: "método não aceito" }, 405);
  const jwt = (req.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
  if (!jwt || jwt === ANON) return json({ erro: "Entre no painel de novo." }, 401);
  let b: any;
  try { b = await req.json(); } catch { return json({ erro: "pedido inválido" }, 400); }

  try {
    if (b.acao === "midia") {
      const m = await rpc("whats_midia", { p_mensagem: Number(b.mensagem) }, jwt);
      const token = await tokenDa(m.loja_id);
      const info = await fetch(`${GRAPH}/${m.midia_id}`, { headers: { Authorization: `Bearer ${token}` } }).then((r) => r.json());
      if (!info?.url) return json({ erro: "A mídia não está mais disponível (a Meta guarda por 30 dias)." }, 404);
      const arq = await fetch(info.url, { headers: { Authorization: `Bearer ${token}` } });
      if (!arq.ok) return json({ erro: "Não foi possível baixar a mídia." }, 502);
      return new Response(arq.body, { headers: { ...CORS, "Content-Type": info.mime_type || "application/octet-stream", "Cache-Control": "private, max-age=3600" } });
    }

    const r = await rpc("whats_responder", { p_conversa: Number(b.conversa), p_texto: String(b.texto || ""), p_auto: b.auto === true }, jwt);
    const token = await tokenDa(r.loja_id);
    const envio = await fetch(`${GRAPH}/${r.phone_number_id}/messages`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ messaging_product: "whatsapp", recipient_type: "individual", to: comNove(r.wa_id), type: "text", text: { preview_url: true, body: String(b.texto).trim() } }),
    });
    const j = await envio.json().catch(() => ({}));
    if (!envio.ok) {
      await rpc("whats_enviada", { p_mensagem: r.id, p_wamid: "", p_status: "failed" });
      return json({ erro: "O WhatsApp recusou o envio: " + (j?.error?.message || envio.status) }, 502);
    }
    const wamid = String(j?.messages?.[0]?.id || "");
    await rpc("whats_enviada", { p_mensagem: r.id, p_wamid: wamid, p_status: "sent" });
    return json({ ok: true, id: r.id, wamid });
  } catch (e) {
    const err = e as Error & { hint?: string; status?: number };
    return json({ erro: err.message, hint: err.hint || "" }, err.status === 401 || err.status === 403 ? 403 : 400);
  }
});
