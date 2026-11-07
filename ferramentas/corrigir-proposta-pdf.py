import sys, pymupdf as fitz
src, dst, fontdir = sys.argv[1:4]
F = fontdir + "/Lato-Regular.ttf"
font = fitz.Font(fontfile=F)
# (página, texto original exato da linha, texto novo, alinhamento)
R = [
 (5, 'Consultar o financeiro, responder no WhatsApp, mudar um preço ou tirar do cardápio o prato que',
     'Consultar o financeiro, acompanhar os pedidos, mudar um preço ou tirar do cardápio o prato que', 'l'),
 (5, 'Conversas • respostas rápidas', 'Ativado após aprovação da Meta', 'r'),
 (5, 'automática com banco ou maquininha. A ativação do atendimento por WhatsApp é alinhada na implantação.',
     'automática com banco ou maquininha. O atendimento por WhatsApp no painel é ativado após a aprovação da conta pela Meta.', 'l'),
 (6, 'O rastreio faz parte do Digital Experience. As etapas são configuradas conforme a operação do restaurante.',
     'O rastreio faz parte do Digital Experience. As cinco etapas são atualizadas pela sua equipe no painel.', 'l'),
 (7, 'Campanha de lançamento', 'Peças de lançamento', 'l'),
 (7, 'Google otimizado, 500 cartões, display de balcão, campanha de lançamento e 30 dias de acompanhamento.',
     'Google otimizado, 500 cartões, display de balcão, peças de lançamento e 30 dias de acompanhamento.', 'l'),
 (8, 'Otimização do perfil da empresa.', 'Ajuste do perfil da empresa, com o seu acesso.', 'l'),
 (8, '500 cartões, display de balcão, campanha e 30 dias de', '500 cartões, display de balcão, peças de lançamento e', 'l'),
 (8, 'acompanhamento.', '30 dias de acompanhamento.', 'l'),
 (8, 'exemplos da sua operação.', 'as nossas demonstrações ao vivo.', 'l'),
]
doc = fitz.open(src)
plan = {}
for p, old, new, al in R:
    hit = None
    for b in doc[p].get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            if "".join(s["text"] for s in l["spans"]).strip() == old:
                hit = l
    assert hit, (p, old)
    s = hit["spans"][0]
    x0, y0, x1, y1 = hit["bbox"]
    w = font.text_length(new, fontsize=s["size"])
    x = x1 - w if al == "r" else x0
    plan.setdefault(p, []).append((fitz.Rect(x0 - .5, y0 + 1, x1 + .5, y1 - 1), x, s["origin"][1], new, s["size"], s["color"], x + w))
for p, items in plan.items():
    pg = doc[p]
    for r, *_ in items:
        pg.add_redact_annot(r, fill=False)
    pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE, text=fitz.PDF_REDACT_TEXT_REMOVE)
    for r, x, y, new, size, color, xe in items:
        c = ((color >> 16) & 255) / 255, ((color >> 8) & 255) / 255, (color & 255) / 255
        pg.insert_text((x, y), new, fontsize=size, fontname="LatoR", fontfile=F, color=c)
        print(p + 1, f"x {x:.0f}-{xe:.0f}", new)
m = doc.metadata; m["title"] = "BistrôConnect | Proposta Comercial Digital Experience"; doc.set_metadata(m)
doc.save(dst, garbage=3, deflate=True)
