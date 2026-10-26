# WhatsApp oficial no painel: como ligar

As mensagens que chegam no número da loja aparecem no painel (aba **Atendimento**). A equipe responde por lá
e o robô responde sozinho o básico (cardápio, "cadê meu pedido?" com o link do rastreio, horário, entrega,
pagamento e "falar com a equipe").

Peças:

| Peça | Onde fica | O que faz |
|---|---|---|
| `10-whatsapp.sql` | Supabase › SQL Editor | tabelas das conversas e regras de acesso |
| `whats-webhook` | Supabase › Edge Functions | recebe da Meta, guarda e o robô responde |
| `whats-enviar` | Supabase › Edge Functions | envia as respostas da equipe e abre fotos/áudios |
| painel | Hostinger `public_html/painel/` | a caixa de entrada |

## 1. Banco (uma vez)

Supabase › **SQL Editor** › cole o `10-whatsapp.sql` › **Run**.

## 2. As duas funções (uma vez)

Supabase › **Edge Functions** › **Deploy a new function** › **Via Editor**:

1. Nome `whats-webhook`: apague o código de exemplo, cole o `whats-webhook/index.ts` e clique em **Deploy**.
   Depois, em **Details** da função, **desligue** "Enforce JWT Verification" (a Meta não manda login do Supabase) e salve.
2. Nome `whats-enviar`: cole o `whats-enviar/index.ts` e clique em **Deploy** (este fica com JWT ligado).

## 3. App na Meta (uma vez, para a plataforma toda)

1. Em **business.facebook.com**, tenha o portfólio empresarial da Bistrô Connect (com o CNPJ; a verificação
   da empresa libera mais conversas por dia).
2. Em **developers.facebook.com** › Meus apps › **Criar app** › tipo **Empresa** › adicione o produto **WhatsApp**.
   A Meta já dá um número de teste para você experimentar.
3. **Segredos no Supabase** (Edge Functions › **Secrets**):
   - `WA_VERIFY_TOKEN`: invente uma frase (ex.: `bistro-webhook-2026`).
   - `WA_APP_SECRET`: Meta › seu app › Configurações do app › Básico › **Chave secreta do app**.
   - `WA_TOKEN`: token permanente. Configurações do negócio › Usuários › **Usuários do sistema** › adicionar (admin) ›
     atribuir o app e a conta do WhatsApp › **Gerar token** com `whatsapp_business_messaging` e `whatsapp_business_management`.
4. **Webhook**: Meta › WhatsApp › **Configuração** › Webhook › Editar:
   - URL de retorno: `https://SEU-PROJETO.supabase.co/functions/v1/whats-webhook`
   - Token de verificação: a mesma frase do `WA_VERIFY_TOKEN`
   - Em **Campos do webhook**, assine **messages**.
5. Para receber de qualquer cliente, deixe o app em modo **Ativo** (Publicar). A Meta pede a política de privacidade:
   `https://bistroconnect.com.br/privacidade.html`.

## 4. Ligar o número de uma loja

1. Meta › WhatsApp › **Configuração da API** › **Adicionar número de telefone**: cadastre o número da loja
   (com nome de exibição da loja). O número não pode estar em uso no aplicativo do WhatsApp ao mesmo tempo:
   use um chip novo ou apague a conta do app nesse número antes.
2. Copie o **ID do número de telefone** (Phone number ID) que aparece ali.
3. Supabase › SQL Editor (troque os valores):

```sql
insert into public.whats_contas (loja_id, phone_number_id, numero)
select id, '123456789012345', '5542999990000' from public.lojas where slug = 'padaria-da-ana'
on conflict (loja_id) do update set phone_number_id = excluded.phone_number_id, numero = excluded.numero, ativo = true;
```

Pronto: a aba Atendimento da loja vira a caixa de entrada. Se a loja usar um app/token próprio da Meta, grave o token dela:
`insert into public.whats_segredos (loja_id, token) select id, 'TOKEN' from public.lojas where slug = '...';`

## Regras do WhatsApp que o painel já respeita

- A loja pode responder livremente até **24 horas** depois da última mensagem do cliente. Depois disso o painel
  bloqueia o envio e avisa (passa a precisar de mensagem modelo aprovada pela Meta, que é paga).
- Responder o cliente que escreveu primeiro não tem custo por mensagem.
- Fotos, áudios e vídeos do cliente abrem pelo botão na conversa (a Meta guarda a mídia por 30 dias).

## Como o robô funciona

- Só responde quando o robô da loja está ligado e a conversa está com o robô (não com a equipe).
- Primeira mensagem (ou depois de 12 horas parado): saudação com o link do cardápio, o status do pedido em
  andamento (se houver) e o menu 1 a 5.
- Entende: cardápio/preço, "cadê meu pedido" (procura o pedido dos últimos 3 dias pelo telefone),
  horário/endereço, entrega/taxa, pagamento/pix, atendente.
- "Falar com a equipe", pedido não encontrado ou cancelado: passa a conversa para a equipe e fica quieto.
- Quando alguém da equipe responde, a conversa passa para a equipe. O botão **Devolver ao robô** devolve.
- Conversa em andamento que o robô não entende: ele não responde; fica marcada como não lida para a equipe.
