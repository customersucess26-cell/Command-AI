"""Troca linhas de texto de um PDF de proposta mantendo layout, fonte, cor e espaçamento.
Uso: python3 ferramentas/corrigir-proposta-pdf.py entrada.pdf saida.pdf pasta-fontes trocas.json
trocas.json: [[pagina (0 = primeira), "linha original exata", "linha nova", "l", "r" ou "c"], ...]
pasta-fontes: Lato-Regular.ttf, Lato-Bold.ttf, EBG-Regular.ttf, EBG-Italic.ttf
(npm pack @fontsource/lato @fontsource/eb-garamond e converter woff2 em ttf com fontTools)."""
import sys, json, re, pymupdf as fitz
src, dst, fd, tj = sys.argv[1:5]
FONTES = {"lato": "Lato-Regular.ttf", "latob": "Lato-Bold.ttf", "ebg": "EBG-Regular.ttf", "ebgi": "EBG-Italic.ttf"}
font = {k: fitz.Font(fontfile=f"{fd}/{v}") for k, v in FONTES.items()}
doc = fitz.open(src)

def qual(span):
    n = span["font"]
    m = re.search(r"Type3 \((\d+) 0 R\)", n)
    if m:
        fdsc = doc.xref_get_key(int(m.group(1)), "FontDescriptor")[1]
        n = doc.xref_get_key(int(fdsc.split()[0]), "FontName")[1] if fdsc != "null" else ""
        return "ebgi" if "Italic" in n else "ebg"
    return "latob" if "Bold" in n else "lato"

plan = {}
for p, old, new, al in json.load(open(tj)):
    hit = [l for b in doc[p].get_text("dict")["blocks"] for l in b.get("lines", [])
           if "".join(s["text"] for s in l["spans"]).strip() == old]
    assert hit, f"não achei na página {p + 1}: {old}"
    l = hit[0]; s = l["spans"][0]; k = qual(s)
    x0, y0, x1, y1 = l["bbox"]
    nat = font[k].text_length(old, fontsize=s["size"])
    esp = (x1 - x0 - nat) / max(1, len(old) - 1)  # espaçamento real da linha (pode ser negativo)
    if abs(esp) < 0.05: esp = 0.0
    w = font[k].text_length(new, fontsize=s["size"]) + esp * (len(new) - 1)
    x = x1 - w if al == "r" else (x0 + x1 - w) / 2 if al == "c" else x0
    plan.setdefault(p, []).append(dict(r=fitz.Rect(x0 - .5, y0 + 1, x1 + .5, y1 - 1), x=x, y=s["origin"][1],
                                       t=new, sz=s["size"], c=s["color"], k=k, esp=esp))
    print(f"p{p + 1} [{k}{' esp %.2f' % esp if esp else ''}] {x:.0f}-{x + w:.0f} (antes {x0:.0f}-{x1:.0f}) {new}")
for p, items in plan.items():
    pg = doc[p]
    for it in items: pg.add_redact_annot(it["r"], fill=False)
    pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    for it in items:
        c = it["c"]; cor = ((c >> 16) & 255) / 255, ((c >> 8) & 255) / 255, (c & 255) / 255
        tw = fitz.TextWriter(pg.rect, color=cor)
        x = it["x"]
        if it["esp"]:
            for ch in it["t"]:
                tw.append((x, it["y"]), ch, font=font[it["k"]], fontsize=it["sz"])
                x += font[it["k"]].text_length(ch, fontsize=it["sz"]) + it["esp"]
        else:
            tw.append((x, it["y"]), it["t"], font=font[it["k"]], fontsize=it["sz"])
        tw.write_text(pg)
m = doc.metadata; m["title"] = "BistrôConnect | Proposta Comercial Digital Experience"; doc.set_metadata(m)
doc.save(dst, garbage=3, deflate=True)
