"""Gera los-5-pilares-v34-es.html (posicionamento de ecossistema): página de vendas no roteiro estratégico de 14 blocos.
Tudo embutido num único arquivo (imagens, vídeo da bússola, CSS e JS).
Uso: python3 build_v23.py
"""
import base64, hashlib, io, pathlib, random, re
from PIL import Image

HERE = pathlib.Path(__file__).parent
SRC = HERE / 'fonte'
IMG = HERE / 'es' / 'assets' / 'img'

CFG = {
    'moeda': 'US$', 'preco': '19,90', 'garantiaDias': 7,
    'checkout': 'https://pay.hotmart.com/Y103646836P?checkoutMode=10&bid=1788666404224&fbclid=fbclid',
    'pixel': '1066235421205419',
}


def img(path, w=None, crop=None, q=82):
    im = Image.open(path).convert('RGB')
    if crop:
        im = im.crop(crop)
    if w and im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, 'WEBP', quality=q, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode(), im.width, im.height


def raw(path, alt, cls='', lazy=True):
    im = Image.open(path)
    src = 'data:image/webp;base64,' + base64.b64encode(pathlib.Path(path).read_bytes()).decode()
    ld = ' loading="lazy" decoding="async"' if lazy else ''
    c = f' class="{cls}"' if cls else ''
    return f'<img{c} src="{src}" alt="{alt}" width="{im.width}" height="{im.height}"{ld}>'


def tag(path, alt, cls='', w=None, crop=None, lazy=True, q=82):
    src, W, H = img(path, w, crop, q)
    ld = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
    c = f' class="{cls}"' if cls else ''
    return f'<img{c} src="{src}" alt="{alt}" width="{W}" height="{H}"{ld}>'


LOGO = tag(IMG / 'logo.webp', 'Los 5 Pilares de la Prosperidad', w=360, lazy=False, q=90)
LOGO_F = tag(IMG / 'logo.webp', 'Los 5 Pilares de la Prosperidad', w=240, q=88)
HERO_ART = tag(SRC / 'hero-ecosistema.webp', 'El ecosistema Los 5 Pilares de la Prosperidad en la computadora, la tableta y el celular, con audio para escuchar los contenidos', 'hero-art-img', w=1672, lazy=False, q=88)
_m = Image.open(SRC / 'montana-amanecer.png').convert('RGB').transpose(Image.FLIP_LEFT_RIGHT)
_b = io.BytesIO(); _m.save(_b, 'WEBP', quality=80, method=6)
HERO_BG = 'data:image/webp;base64,' + base64.b64encode(_b.getvalue()).decode()
TORRE = raw(SRC / 'hd-hoy.webp', 'Pantalla real de la plataforma: el panel Hoy con la prioridad del día, la jornada y los cinco pilares')
ESTATUA = tag(SRC / 'estatua-hd.webp', 'Una estatua que se esculpe a sí misma con martillo y cincel, entre chispas doradas', 'forge-img', w=1300, q=86)
AGUILA = tag(SRC / 'aguila.webp', 'Un águila vuela sobre las montañas al amanecer', q=86)
LEON = tag(SRC / 'leon.webp', 'Un león avanza de frente sobre las rocas', q=86)
LOBO = tag(SRC / 'lobo.webp', 'Un lobo camina de frente bajo la luna llena', q=86)
TRIO = tag(SRC / 'colagem-animais.webp', 'Águila, león y lobo: foco, ejecución y disciplina', 'fx-img', crop=(716, 520, 1536, 1024), q=84)
POSTER = img(SRC / 'brujula-poster.png', w=560, q=78)[0]
VIDEO = base64.b64encode((SRC / 'brujula.mp4').read_bytes()).decode()

SHOTS = [
    ('hd-diagnostico', 'Pantalla real: el diagnóstico de los cinco pilares'),
    ('hd-hoy', 'Pantalla real: el panel Hoy muestra la prioridad del día'),
    ('hd-salud', 'Pantalla real: un capítulo de la biblioteca con el audio para escuchar'),
    ('hd-jornada', 'Pantalla real: la jornada de 90 misiones'),
    ('hd-agenda', 'Pantalla real: la agenda de estudio y el seguimiento semanal'),
]
SHOT_TAGS = []
for i, (n, alt) in enumerate(SHOTS):
    SHOT_TAGS.append(raw(SRC / f'{n}.webp', alt, 'on' if i == 0 else '', lazy=i > 0))
MOCK = tag(SRC / 'mockup-plataforma.webp', 'El ecosistema Los 5 Pilares en la computadora, el notebook, el celular y la tableta: panel, jornada de 90 días, cinco pilares y biblioteca de contenidos', 'mock-img', q=88)
FONE = tag(SRC / 'audio-fone.webp', 'Audífonos y celular reproduciendo el audio de un capítulo de Los 5 Pilares', 'fone-img', q=86)
RSHOTS = ''.join(raw(SRC / f'hd-r{i}.webp', alt, 'on' if i == 1 else '') for i, alt in [(1, 'Pantalla real: recurso Gestión del Tiempo'), (2, 'Pantalla real: recurso Inteligencia Emocional'), (3, 'Pantalla real: recurso Comunicación'), (4, 'Pantalla real: recurso El Mapa, 21 oportunidades')])
DEV = {
 'desk': raw(SRC / 'hd-hoy.webp', 'Pantalla real en la computadora: panel Hoy'),
 'lap': raw(SRC / 'hd-jornada.webp', 'Pantalla real en el notebook: jornada de 90 misiones'),
 'tab': raw(SRC / 'hd-salud.webp', 'Pantalla real en la tableta: biblioteca de contenidos'),
 'pho': tag(IMG / 'tela-hoy.webp', 'Pantalla real en el celular: panel Hoy', w=420, q=84),
}
PHONES = [tag(IMG / f'tela-{n}.webp', alt, w=420, q=80) for n, alt in
          [('jornada', 'Pantalla real en el celular: jornada'), ('hoy', 'Pantalla real en el celular: panel Hoy'), ('practicar', 'Pantalla real en el celular: cronograma de aplicación')]]
PISOS = {k: tag(IMG / f'piso-{k}.webp', alt, q=86) for k, alt in [
    ('salud', 'Piso de Salud: una mujer medita en un gimnasio luminoso'),
    ('espiritualidad', 'Piso de Espiritualidad: una persona medita frente al atardecer'),
    ('relaciones', 'Piso de Relaciones: una familia ríe junta en el sofá'),
    ('carrera', 'Piso de Carrera: un profesional trabaja frente a la ciudad'),
    ('finanzas', 'Piso de Finanzas: monedas que crecen y una alcancía dorada'),
]}

random.seed(11)
EMBERS = ''.join('<i style="--x:%d%%;--s:%dpx;--d:%.1fs;--t:%.1fs;--w:%dpx"></i>' % (
    random.randint(3, 97), random.randint(2, 4), random.uniform(0, 7), random.uniform(5, 9), random.randint(-50, 50)) for _ in range(28))

ICON = {
    'panel': '<rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/>',
    'radar': '<path d="M12 3l8.5 6.2-3.2 10H6.7L3.5 9.2z"/><path d="M12 8l4.2 3-1.6 4.8H9.4L7.8 11z"/>',
    'book': '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5z"/><path d="M4 20.5A2.5 2.5 0 0 0 6.5 23H20v-5"/>',
    'cal': '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4M8 14h3M13 14h3M8 17h3"/>',
    'check': '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M7.5 12.5l3 3 6-7"/>',
    'note': '<path d="M5 3h10l4 4v14H5z"/><path d="M15 3v4h4M8 12h8M8 16h5"/>',
    'trend': '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    'audio': '<path d="M4 14v-2a8 8 0 0 1 16 0v2"/><rect x="3" y="14" width="4" height="7" rx="1.5"/><rect x="17" y="14" width="4" height="7" rx="1.5"/>',
}


def ico(k):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICON[k]}</svg>'


PICON = {
 'salud': '<path d="M19 14c1.5-1.5 3-3.2 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.8 0-3 .5-4.5 2-1.5-1.5-2.7-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4 3 5.5l7 7z"/><path d="M3.5 12h5l1.5-2.5 2.5 5 1.5-2.5h6.5"/>',
 'espiritualidad': '<path d="M12 3v18M6.5 8.5h11"/>',
 'relaciones': '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
 'carrera': '<rect x="2" y="7" width="20" height="14" rx="2.5"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2M2 13h20M10.5 13v2h3v-2"/>',
 'finanzas': '<circle cx="8.5" cy="8.5" r="5.5"/><path d="M18.1 10.4a5.5 5.5 0 1 1-7.7 7.7M7.5 6.5h1.2v4M16.8 13.9l.7.7-2.8 2.8"/>',
}

PILARES = [
    ('01', 'Salud física y mental', 'Tu energía es uno de los recursos más importantes de tu vida.',
     'Aprende sobre sueño, nutrición, movimiento, fuerza, recuperación, movilidad y prevención del agotamiento. Explora prácticas y estrategias para desarrollar una rutina más consciente de cuidado del cuerpo y de la mente.',
     ['Sueño', 'Nutrición', 'Movimiento', 'Recuperación', 'Agotamiento'], 'salud'),
    ('02', 'Desarrollo personal y espiritualidad', 'Descubre lo que orienta tus decisiones y la dirección que quieres seguir.',
     'Trabaja propósito, autoconocimiento, creencias, objetivos, fe, crecimiento personal y aplicación de las enseñanzas cristianas. Un camino para reflexionar sobre tus valores, fortalecer tu dirección y convertir la intención en actitudes.',
     ['Propósito', 'Autoconocimiento', 'Fe cristiana', 'Valores', 'Objetivos'], 'espiritualidad'),
    ('03', 'Relaciones: capital social', 'Las conexiones que construyes también forman parte de tu prosperidad.',
     'Explora comunicación, respeto, relaciones afectivas, familia, networking, conexiones profesionales y el desarrollo de relaciones más conscientes. Porque construir una buena vida también implica aprender a relacionarte mejor.',
     ['Comunicación', 'Familia', 'Pareja', 'Networking', 'Respeto'], 'relaciones'),
    ('04', 'Carrera y emprendimiento', 'Desarrolla una trayectoria profesional con más dirección y estrategia.',
     'Explora mentalidad de crecimiento, productividad, posicionamiento, alto rendimiento sostenible, monetización del conocimiento y marca personal. Conoce fundamentos para desarrollar tus capacidades y construir nuevas posibilidades profesionales.',
     ['Productividad', 'Posicionamiento', 'Marca personal', 'Monetización', 'Rendimiento'], 'carrera'),
    ('05', 'Finanzas: la palanca de la libertad', 'El dinero necesita dirección para contribuir al futuro que deseas.',
     'Aprende fundamentos de organización financiera, creencias, consumo consciente, generación de ingresos, deudas, inversiones, planificación y construcción de patrimonio. El objetivo es desarrollar una relación más consciente y estratégica con el dinero.',
     ['Organización', 'Deudas', 'Consumo consciente', 'Inversiones', 'Patrimonio'], 'finanzas'),
]

BONOS = [
    ('01', 'Gestión del tiempo', 'Aprende a analizar tus 168 horas semanales, combatir la fragmentación de la atención, organizar prioridades y desarrollar períodos de trabajo profundo.', ['Tus 168 horas', 'Atención', 'Prioridades', 'Trabajo profundo']),
    ('02', 'Inteligencia emocional', 'Explora gatillos emocionales, patrones de reacción, autocontrol y estrategias para lidiar mejor con situaciones de presión.', ['Gatillos', 'Patrones de reacción', 'Autocontrol', 'Presión']),
    ('03', 'Comunicación', 'Desarrolla claridad, influencia ética, encuadre de mensajes, comunicación persuasiva, negociación y técnicas para conducir conversaciones.', ['Claridad', 'Influencia ética', 'Negociación', 'Conversaciones']),
    ('04', 'El Mapa: 21 oportunidades de negocio', 'Una guía para explorar posibilidades de negocios digitales, conocer distintos modelos de actuación, estudiar oportunidades y desarrollar un plan de ejecución.', ['Negocios digitales', 'Modelos', 'Oportunidades', 'Plan de ejecución']),
]

STEPS6 = [
    ('Tu diagnóstico', 'Responde 15 afirmaciones y visualiza tu mapa inicial de los cinco pilares.'),
    ('Tu prioridad', 'Identifica el punto que merece más atención en este momento.'),
    ('Tu contenido', 'Explora la biblioteca por dimensiones y temas, en texto o en audio para escuchar en el tránsito o en tus tareas del día, a tu propio ritmo.'),
    ('Tu práctica', 'Sigue ejercicios, misiones y checklists organizados en una trilla de aplicación.'),
    ('Tu progreso', 'Registra anotaciones y acompaña los pasos que ya diste.'),
]

FEATS = [
    ('panel', 'Panel con visión general de los cinco pilares'),
    ('radar', 'Diagnóstico y visualización del equilibrio entre las áreas'),
    ('book', 'Biblioteca integrada de contenidos, organizada por dimensiones'),
    ('audio', 'Audio en cada capítulo, para escuchar donde estés'),
    ('cal', 'Cronograma de aplicación'),
    ('check', 'Ejercicios y checklists'),
    ('note', 'Registro de anotaciones'),
    ('trend', 'Seguimiento de tu progreso'),
]

OBJ = [
    ('«Mi rutina ya es muy acelerada. ¿Voy a poder seguirlo?»', 'La biblioteca está organizada en capítulos, con ejercicios, rutas de aplicación y audio en cada capítulo: puedes escucharlo en el auto o en casa mientras haces tus rutinas. Empiezas por una prioridad y avanzas de forma gradual, sin intentar transformar todas las áreas al mismo tiempo.'),
    ('«Ya compré otros cursos y nunca puse nada en práctica.»', 'Aquí el contenido viene acompañado de herramientas de aplicación, checklists, misiones y seguimiento del progreso. El objetivo es facilitar el paso del conocimiento a la acción.'),
    ('«¿Es solo un ebook o un curso?»', 'No. Los contenidos son solo una parte. Los 5 Pilares es un ecosistema digital que integra diagnóstico, una biblioteca organizada por dimensiones, la jornada de 90 misiones, ejercicios, checklists, audio, anotaciones y seguimiento del progreso en un solo entorno.'),
    ('«¿Esto es solo para ganar dinero?»', 'No. Las finanzas son solo una de las cinco dimensiones. La propuesta también abarca salud, desarrollo personal y espiritualidad, relaciones y carrera.'),
    ('«¿Necesito saber de estas áreas?»', 'No. El contenido está organizado para presentar fundamentos, conceptos y prácticas que te ayudan a desarrollar tu comprensión poco a poco.'),
    ('«¿Voy a tener resultados garantizados?»', 'No existe promesa de resultados automáticos. La plataforma ofrece conocimiento, estructura y herramientas de práctica. Tu evolución dependerá de tus decisiones, de tu dedicación y de tus circunstancias.'),
    ('«¿Cómo recibo el acceso?»', 'Al confirmarse el pago en Hotmart, te llega el enlace al correo. Se abre en el celular, la tableta o la computadora, en español y portugués.'),
]

check = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'


def lst(items):
    return ''.join(f'<li>{check}<span>{x}</span></li>' for x in items)


pilares_html = ''.join(f'''
   <article class="pillar rv">
    <div class="medal" aria-hidden="true"><i class="medal-ring"></i><div class="medal-in"><svg viewBox="0 0 24 24">{PICON[k]}</svg></div><span class="medal-n">{n}</span></div>
    <div class="pillar-txt">
     <p class="pillar-n"><span>Dimensión</span> {n}</p>
     <h3>{t}</h3>
     <p class="pillar-lead">{lead}</p>
     <p>{body}</p>
     <ul class="chips">{''.join(f'<li>{c}</li>' for c in chips)}</ul>
    </div>
   </article>''' for i, (n, t, lead, body, chips, k) in enumerate(PILARES))

bonos_html = ''.join(f'''
    <article class="bono rv spot">
     <div class="bono-top"><span class="bono-n">{n}</span><span class="bono-k">Recurso {n}</span></div>
     <h3>{t}</h3>
     <p>{d}</p>
     <ul class="chips sm">{''.join(f'<li>{c}</li>' for c in chips)}</ul>
    </article>''' for n, t, d, chips in BONOS)

steps_html = ''.join(f'<li><button type="button" role="tab" aria-selected="{"true" if i == 0 else "false"}" data-i="{i}"><em>0{i+1}</em><b>{t}</b><i class="bar"></i></button></li>' for i, (t, d) in enumerate(STEPS6))
feats_html = ''.join(f'<li class="rv">{ico(k)}<span>{t}</span></li>' for k, t in FEATS)
obj_html = ''.join(f'<details{" open" if i == 0 else ""}><summary>{q}</summary><p>{a}</p></details>' for i, (q, a) in enumerate(OBJ))

CSS = r'''
:root{--bg:#070708;--bg2:#0d0c0f;--card:#111014;--card2:#16141a;--text:#f4efe6;--mut:#bab3a6;--dim:#857f74;
 --hair:rgba(255,236,200,.09);--hair2:rgba(255,236,200,.16);--gold:#d9ae5c;--gold2:#f3d48d;--gold3:#a87e2f;
 --h:'Bebas Neue','Oswald','Arial Narrow',Impact,sans-serif;--s:'Cormorant Garamond',Georgia,'Times New Roman',serif;--b:'DM Sans','Segoe UI',system-ui,-apple-system,Arial,sans-serif;
 --ease:cubic-bezier(.2,.7,.1,1);color-scheme:dark}
*{box-sizing:border-box}
html{background:var(--bg);-webkit-text-size-adjust:100%;scroll-behavior:smooth;overflow-x:clip}
body{margin:0;background:radial-gradient(1200px 700px at 80% -10%,rgba(217,174,92,.08),transparent 70%),var(--bg);color:var(--text);font:400 18px/1.65 var(--b);-webkit-font-smoothing:antialiased;overflow-x:clip}
body::after{content:"";position:fixed;inset:0;z-index:90;pointer-events:none;opacity:.05;mix-blend-mode:overlay;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)'/%3E%3C/svg%3E")}
img{max-width:100%;height:auto;display:block}
a{color:inherit}
h1,h2,h3,p,ul,ol,figure,blockquote{margin:0}
ul,ol{padding:0;list-style:none}
:focus-visible{outline:2px solid var(--gold2);outline-offset:4px;border-radius:6px}
.skip{position:fixed;left:12px;top:12px;z-index:100;padding:10px 16px;border-radius:8px;background:var(--gold);color:#140e04;font-weight:700;transform:translateY(-300%);opacity:0;pointer-events:none}
.skip:focus-visible{transform:none;opacity:1;pointer-events:auto}
.wrap{width:min(1180px,100% - 48px);margin-inline:auto}
.narrow{width:min(860px,100% - 48px);margin-inline:auto}
@media(max-width:600px){.wrap,.narrow{width:calc(100% - 36px)}}
.sec{position:relative;padding:clamp(88px,10vw,150px) 0}
.xx-old::before{content:"";position:absolute;top:0;left:50%;width:min(1180px,90%);height:1px;transform:translateX(-50%);background:linear-gradient(90deg,transparent,rgba(217,174,92,.35) 40%,transparent 48%,transparent 52%,rgba(217,174,92,.35) 60%,transparent)}
.xx-old::after{content:"";position:absolute;top:-6px;left:50%;width:12px;height:12px;margin-left:-6px;transform:rotate(45deg);border:1px solid rgba(217,174,92,.7);background:#0a090c;box-shadow:0 0 18px rgba(217,174,92,.5)}

.center{text-align:center}
/* tipografia */
.kick{display:inline-flex;align-items:center;gap:12px;margin-bottom:22px;font:700 12.5px/1.3 var(--b);letter-spacing:.28em;text-transform:uppercase;color:var(--gold)}
.kick::before{content:"";width:28px;height:1px;background:currentColor}
.center .kick::after{content:"";width:28px;height:1px;background:currentColor}
h1,h2{font-family:var(--h);font-weight:400;letter-spacing:.005em;line-height:.96;text-wrap:balance}
h1{font-size:clamp(56px,7.4vw,112px)}
h2{font-size:clamp(44px,5.4vw,80px)}
h3{font:400 clamp(30px,2.6vw,40px)/1 var(--h);letter-spacing:.01em}
.it{display:block;margin-top:.12em;font:500 italic .62em/1.08 var(--s);letter-spacing:0;text-transform:none;background:linear-gradient(100deg,#f7dfa4,#d9ae5c 35%,#fff1c9 50%,#d9ae5c 65%,#f7dfa4);background-size:220% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;animation:sheen 9s ease-in-out infinite;padding-bottom:.06em}
@keyframes sheen{0%,100%{background-position:100% 0}50%{background-position:0 0}}
.lead{font-size:clamp(19px,1.5vw,22px);line-height:1.6;color:var(--mut)}
.lead b,.mut b{color:var(--text);font-weight:600}
.mut{color:var(--mut)}
.quote{font:500 italic clamp(28px,2.8vw,40px)/1.25 var(--s);color:var(--gold2);text-wrap:balance}
p+p{margin-top:18px}
/* botões */
.cta{position:relative;display:inline-flex;align-items:center;justify-content:center;gap:12px;min-height:62px;padding:18px 34px;border-radius:10px;border:0;cursor:pointer;overflow:hidden;isolation:isolate;
 background:linear-gradient(180deg,#f7dcaa,#d9ae5c 60%,#c4964a);color:#190f02;font:700 15.5px/1.2 var(--b);letter-spacing:.08em;text-transform:uppercase;text-decoration:none;
 box-shadow:0 20px 50px -18px rgba(217,174,92,.75),inset 0 1px 0 rgba(255,255,255,.55);transition:transform .3s var(--ease),box-shadow .3s}
.cta::after{content:"";position:absolute;inset:0 auto 0 -60%;width:40%;z-index:-1;background:linear-gradient(100deg,transparent,rgba(255,255,255,.65),transparent);transform:skewX(-20deg);animation:sweep 4.5s ease-in-out infinite}
@keyframes sweep{0%,60%{left:-60%}100%{left:130%}}
.cta:hover{transform:translateY(-2px);box-shadow:0 26px 60px -16px rgba(217,174,92,.95),inset 0 1px 0 rgba(255,255,255,.55)}
.cta svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2.2}
.ghost{display:inline-flex;align-items:center;gap:10px;min-height:56px;padding:14px 26px;border-radius:10px;border:1px solid var(--hair2);color:var(--text);font:600 15px var(--b);text-decoration:none;transition:border-color .3s,color .3s}
.ghost:hover{border-color:var(--gold);color:var(--gold2)}
.micro{margin-top:16px;font-size:14px;color:var(--dim);letter-spacing:.02em}
@media(max-width:600px){.cta{width:100%;padding:18px 20px;font-size:14.5px}}
/* topo */
.top{position:absolute;inset:0 0 auto;z-index:20;display:flex;align-items:center;justify-content:space-between;padding:22px max(24px,calc((100% - 1180px)/2))}
.top img{height:54px;width:auto}
.top a.mini{padding:10px 18px;border:1px solid var(--hair2);border-radius:999px;font:600 14px var(--b);text-decoration:none;background:rgba(7,7,8,.4);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px)}
.top a.mini:hover{border-color:var(--gold);color:var(--gold2)}
/* 1 · hero */
.hero{position:relative;min-height:100svh;display:flex;align-items:center;padding:130px 0 90px;overflow:hidden;isolation:isolate}
.hero-art{position:absolute;z-index:-1;right:max(-60px,calc((100% - 1180px)/2 - 120px));top:50%;width:min(860px,62vw);transform:translateY(-50%)}
.hero-img{width:100%;animation:kb 26s ease-in-out infinite alternate;-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 24%,#000 80%,transparent 100%),linear-gradient(180deg,transparent 0,#000 22%,#000 74%,transparent 100%);-webkit-mask-composite:source-in;mask-image:linear-gradient(90deg,transparent 0,#000 24%,#000 80%,transparent 100%),linear-gradient(180deg,transparent 0,#000 22%,#000 74%,transparent 100%);mask-composite:intersect}
@keyframes kb{to{transform:scale(1.07) translate(-1.5%,-1%)}}
.hero-glow{position:absolute;inset:10% 20% 10% 25%;border-radius:50%;background:radial-gradient(closest-side,rgba(255,180,80,.22),transparent 75%);filter:blur(20px);animation:pulse 5s ease-in-out infinite;z-index:-1}
@keyframes pulse{50%{opacity:.55;transform:scale(1.08)}}
.embers{position:absolute;inset:0;overflow:hidden;pointer-events:none;z-index:-1}
.embers i{position:absolute;left:var(--x);bottom:-12px;width:var(--s);height:var(--s);border-radius:50%;background:#ffd27a;box-shadow:0 0 10px 2px rgba(255,170,60,.8);opacity:0;animation:ember var(--t) linear var(--d) infinite}
@keyframes ember{0%{transform:translate(0,0);opacity:0}10%{opacity:.9}100%{transform:translate(var(--w),-90vh);opacity:0}}
.hero-bg{position:absolute;inset:0;z-index:-2;overflow:hidden}
.hero-bg img{width:100%;height:100%;object-fit:cover;object-position:60% 40%;animation:kb 30s ease-in-out infinite alternate}
.hero::after{content:"";position:absolute;inset:0;z-index:-1;pointer-events:none;background:linear-gradient(90deg,rgba(7,7,8,.94) 0%,rgba(7,7,8,.78) 34%,rgba(7,7,8,.15) 66%,rgba(7,7,8,.05) 100%),linear-gradient(0deg,var(--bg) 0%,transparent 28%),linear-gradient(180deg,rgba(7,7,8,.6),transparent 22%)}
.hero-in{max-width:640px}
.hero h1 .it{font-size:.5em}
.hero .lead{margin-top:30px;max-width:560px}
.hero .lead+.lead{margin-top:16px}
.hero-cta{margin-top:38px}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));margin-top:44px;max-width:640px;border-top:1px solid rgba(217,174,92,.3);border-bottom:1px solid rgba(217,174,92,.3);background:linear-gradient(180deg,rgba(7,7,8,.55),rgba(7,7,8,.25));-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px)}
.stats li{position:relative;display:flex;flex-direction:column;gap:8px;padding:18px 16px 18px}
.stats li+li::before{content:"";position:absolute;left:0;top:18px;bottom:18px;width:1px;background:linear-gradient(180deg,transparent,rgba(217,174,92,.45),transparent)}
.stats b{display:flex;align-items:flex-end;height:46px;font:400 50px/.9 var(--h);font-weight:400;color:transparent;background:linear-gradient(180deg,#fff1c9,#d9ae5c 70%,#a87e2f);-webkit-background-clip:text;background-clip:text;font-variant-numeric:tabular-nums}
.stats b.ico-a svg{width:40px;height:40px;fill:none;stroke:#e3b867;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 8px rgba(217,174,92,.5))}
.stats span{font:600 11.5px/1.35 var(--b);letter-spacing:.14em;text-transform:uppercase;color:var(--mut)}
@media(max-width:600px){.stats{grid-template-columns:1fr 1fr}.stats li:nth-child(3)::before{display:none}.stats li:nth-child(n+3){border-top:1px solid rgba(217,174,92,.18)}.stats b{font-size:42px;height:40px}}
@media(max-width:900px){.hero{padding:120px 0 70px}.hero-bg img{object-position:78% 40%}
 .hero::after{background:linear-gradient(0deg,var(--bg) 0%,rgba(7,7,8,.82) 45%,rgba(7,7,8,.45) 100%)}}
/* faixa dos pilares */
.marquee{position:relative;overflow:hidden;border-block:1px solid var(--hair);background:#0b0a0d;padding:18px 0}
.marquee-in{display:flex;gap:42px;width:max-content;animation:mq 40s linear infinite;font:400 28px/1 var(--h);letter-spacing:.06em;color:var(--mut);white-space:nowrap}
.marquee-in span{display:inline-flex;align-items:center;gap:42px}
.marquee-in span::after{content:"✦";color:var(--gold);font-size:16px}
@keyframes mq{to{transform:translateX(-50%)}}
/* 2 · identificação */
.ident{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(30px,4vw,60px);align-items:center}
.later{margin:32px 0 30px;border-top:1px solid var(--hair)}
.later li{display:grid;grid-template-columns:1fr auto;gap:16px;align-items:baseline;padding:16px 0;border-bottom:1px solid var(--hair);font-size:18px}
.later li em{font:500 italic 19px var(--s);color:var(--gold);white-space:nowrap}
.brj{position:relative;margin:0 -6% 0 0;aspect-ratio:1/1;isolation:isolate}
.brj::after{content:"";position:absolute;inset:4%;border-radius:50%;border:1px dashed rgba(217,174,92,.3);animation:rot 40s linear infinite;pointer-events:none}
.brj video{width:100%;height:100%;object-fit:cover;transform:scale(1.18);-webkit-mask-image:radial-gradient(closest-side,#000 64%,transparent 100%);mask-image:radial-gradient(closest-side,#000 64%,transparent 100%)}
.brj::before{content:"";position:absolute;inset:10%;border-radius:50%;background:radial-gradient(closest-side,rgba(217,160,70,.28),transparent 72%);filter:blur(18px);z-index:-1;animation:pulse 5s ease-in-out infinite}
.bigq{margin-top:clamp(70px,8vw,110px);padding:clamp(34px,4vw,56px);border-radius:24px;border:1px solid var(--hair2);background:radial-gradient(80% 120% at 50% 0,rgba(217,174,92,.10),transparent 70%),var(--card);text-align:center}
.bigq .kick{margin-bottom:16px}
@media(max-width:900px){.ident{grid-template-columns:1fr}.brj{max-width:460px;margin:0 auto;order:-1}}
/* 3 · quebra de crença */
.why{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:54px auto 50px;max-width:1180px;counter-reset:w}
.why li{counter-increment:w;position:relative;padding:34px 28px 30px;border-radius:20px;border:1px solid var(--hair);background:linear-gradient(180deg,rgba(255,240,210,.045),rgba(255,240,210,.01));text-align:left;font:400 clamp(28px,2.4vw,36px)/1.04 var(--h);letter-spacing:.01em;color:var(--text);overflow:hidden}
.why li::before{content:"0" counter(w);display:block;margin-bottom:18px;font:400 64px/.8 var(--h);color:transparent;-webkit-text-stroke:1px rgba(217,174,92,.6)}
.why li b{display:block;margin-top:6px;font-weight:400;color:var(--gold2)}
.why li::after{content:"";position:absolute;left:28px;right:28px;bottom:0;height:2px;background:linear-gradient(90deg,var(--gold),transparent)}
@media(max-width:900px){.why{grid-template-columns:1fr}}
.belief .lead{max-width:62ch;margin-inline:auto}
.belief .quote{max-width:30ch;margin-inline:auto}
.belief .quote{margin-top:46px}
/* pontes: estátua e três forças */
.forge{position:relative;padding:clamp(60px,7vw,110px) 0;overflow:hidden;background:radial-gradient(50% 60% at 32% 50%,rgba(217,150,60,.12),transparent 70%),linear-gradient(180deg,var(--bg),#020203 16%,#020203 84%,var(--bg))}
.forge-in{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,.7fr);gap:clamp(20px,4vw,60px);align-items:center}
.forge-art{position:relative;margin:0;isolation:isolate;aspect-ratio:1487/1058;display:grid;place-items:center}
.forge-img{position:relative;width:100%;-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 9%,#000 91%,transparent 100%),linear-gradient(180deg,transparent 0,#000 6%,#000 90%,transparent 100%);-webkit-mask-composite:source-in;mask-image:linear-gradient(90deg,transparent 0,#000 9%,#000 91%,transparent 100%),linear-gradient(180deg,transparent 0,#000 6%,#000 90%,transparent 100%);mask-composite:intersect}
.forge-rays{position:absolute;inset:-14%;z-index:-2;border-radius:50%;background:repeating-conic-gradient(rgba(243,212,141,.16) 0 4deg,transparent 4deg 15deg);-webkit-mask-image:radial-gradient(closest-side,transparent 22%,#000 40%,transparent 92%);mask-image:radial-gradient(closest-side,transparent 22%,#000 40%,transparent 92%);animation:rot 60s linear infinite}
.forge-halo{position:absolute;inset:14% 18%;z-index:-1;border-radius:50%;background:radial-gradient(closest-side,rgba(255,190,90,.38),rgba(217,140,40,.12) 60%,transparent 75%);filter:blur(16px);animation:pulse 4.5s ease-in-out infinite}
.forge-glow{position:absolute;left:62.5%;top:64%;width:150px;height:150px;margin:-75px 0 0 -75px;border-radius:50%;background:radial-gradient(circle,rgba(255,236,190,.95),rgba(255,190,90,.35) 30%,transparent 65%);mix-blend-mode:screen;animation:spark 2.4s ease-in-out infinite;z-index:2;pointer-events:none}
.forge-art .embers{z-index:3}
.strike{width:100%;transform-origin:45% 95%;animation:strike 2.4s cubic-bezier(.5,0,.2,1) infinite}
@keyframes strike{0%,8%{transform:none}62%{transform:translateY(-1.4%) rotate(-1.2deg)}74%{transform:translateY(.9%) rotate(.5deg)}80%{transform:translateY(-.2%) rotate(-.1deg)}88%,100%{transform:none}}
.forge-glow{animation:flash 2.4s ease-out infinite!important}
@keyframes flash{0%,72%{opacity:.25;transform:scale(.6)}75%{opacity:1;transform:scale(1.55)}86%{opacity:.55;transform:scale(1)}100%{opacity:.25;transform:scale(.6)}}
.forge-wave{position:absolute;left:62.5%;top:64%;width:90px;height:90px;margin:-45px 0 0 -45px;border-radius:50%;border:2px solid rgba(255,220,150,.85);opacity:0;z-index:2;animation:wave 2.4s ease-out infinite;pointer-events:none}
@keyframes wave{0%,73%{opacity:0;transform:scale(.2)}75%{opacity:1;transform:scale(.3)}100%{opacity:0;transform:scale(2.6)}}
.burst{position:absolute;left:62.5%;top:64%;z-index:3;pointer-events:none}
.burst b{position:absolute;left:0;top:0;width:4px;height:4px;border-radius:50%;background:#ffe2a4;box-shadow:0 0 8px 2px rgba(255,180,80,.9);opacity:0;animation:spk 2.4s ease-out infinite}
@keyframes spk{0%,73%{opacity:0;transform:translate(0,0)}75%{opacity:1;transform:translate(0,0)}100%{opacity:0;transform:translate(calc(var(--dx)*1px),calc(var(--dy)*1px + 40px))}}
@keyframes spark{0%,100%{opacity:.35;transform:scale(.7)}40%{opacity:1;transform:scale(1.2)}50%{opacity:.6;transform:scale(.95)}}
.forge-k{margin-top:22px;font:400 30px/1 var(--h);letter-spacing:.03em;color:var(--text)}
@media(max-width:900px){.forge-in{grid-template-columns:1fr}.forge-art{margin:0 -18px}}
@media(max-width:900px){.forge-art{margin:0 -30px}}
.trio3{display:grid;grid-template-columns:repeat(3,1fr);gap:clamp(18px,3vw,40px);margin-top:56px;text-align:center}
.fz figure{margin:0 0 -30px}
.fz img{width:100%;aspect-ratio:1/1;object-fit:cover;-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 16%,#000 84%,transparent 100%),linear-gradient(180deg,transparent 0,#000 14%,#000 62%,transparent 96%);-webkit-mask-composite:source-in;mask-image:linear-gradient(90deg,transparent 0,#000 16%,#000 84%,transparent 100%),linear-gradient(180deg,transparent 0,#000 14%,#000 62%,transparent 96%);mask-composite:intersect;transition:transform 1.2s var(--ease)}
.fz:hover img{transform:scale(1.04)}
.fz span{position:relative;font:700 12px var(--b);letter-spacing:.26em;text-transform:uppercase;color:var(--gold)}
.fz h3{position:relative;margin:8px 0 10px;font-size:clamp(38px,3.4vw,48px)}
.fz p{position:relative;color:var(--mut);font-size:16.5px;max-width:34ch;margin-inline:auto}
@media(max-width:900px){.trio3{grid-template-columns:1fr;gap:30px}.fz img{max-width:380px;margin:0 auto}}
/* 4 · solução */
.sol-head .lead{max-width:58ch;margin:24px auto 0}
.sol-head .lead+.lead{margin-top:14px}
.showcase{position:relative;margin:56px auto 0;max-width:1180px;border-radius:16px;overflow:hidden;border:1px solid rgba(217,174,92,.35);background:#05070f;
 box-shadow:0 80px 160px -60px rgba(0,0,0,1),0 0 140px -40px rgba(217,174,92,.45);transform-origin:50% 100%}
.showcase::after{content:"";position:absolute;inset:0;pointer-events:none;border-radius:inherit;box-shadow:inset 0 1px 0 rgba(255,255,255,.08)}
.showcase .chrome,.screen .chrome{display:flex;align-items:center;gap:7px;padding:12px 16px;background:#141218;border-bottom:1px solid var(--hair)}
.showcase .chrome i,.screen .chrome i{width:11px;height:11px;border-radius:50%;background:#3a3530}
.showcase .chrome span{margin-left:12px;font-size:13px;color:var(--dim)}
.showcase img{width:100%;height:auto}
.js .showcase.rv{opacity:0;transform:perspective(1800px) rotateX(16deg) translateY(60px) scale(.96);transition:opacity 1.1s var(--ease),transform 1.5s var(--ease)}
.js .showcase.rv.in{opacity:1;transform:none}
.real{margin-top:14px;font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:var(--dim)}
.struct{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:28px 0 0;counter-reset:st}
.struct li{counter-increment:st;position:relative;padding:22px 22px 22px 66px;border:1px solid var(--hair);border-radius:14px;background:var(--card);font-size:17px;line-height:1.45}
.struct li::before{content:"0" counter(st);position:absolute;left:20px;top:18px;font:400 30px/1 var(--h);color:var(--gold)}
@media(max-width:900px){.struct{grid-template-columns:1fr 1fr}}
@media(max-width:560px){.struct{grid-template-columns:1fr}}
/* 5 · pilares */
.pillars{margin:64px auto 0;max-width:1000px;border-top:1px solid var(--hair)}
.pillar{display:grid;grid-template-columns:150px minmax(0,1fr);gap:clamp(28px,4vw,56px);align-items:start;padding:clamp(40px,4.5vw,56px) 0;border-bottom:1px solid var(--hair)}
.medal{position:relative;width:132px;height:132px;border-radius:50%;padding:2px;background:conic-gradient(from 210deg,#7a5a22,#f3d48d,#d9ae5c,#fff1c9,#a87e2f,#7a5a22);box-shadow:0 24px 60px -24px rgba(217,174,92,.6),0 0 0 10px rgba(217,174,92,.05)}
.medal-in{display:grid;place-items:center;width:100%;height:100%;border-radius:50%;background:radial-gradient(70% 70% at 50% 35%,#24201a,#0c0b0e 75%)}
.medal svg{width:54px;height:54px;fill:none;stroke:url(#gg);stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 10px rgba(217,174,92,.45));transition:transform .8s var(--ease)}
.pillar:hover .medal svg{transform:scale(1.08)}
.medal-n{position:absolute;right:-6px;bottom:2px;display:grid;place-items:center;width:40px;height:40px;border-radius:50%;background:linear-gradient(180deg,#f7dcaa,#c4964a);color:#190f02;font:400 20px/1 var(--h);box-shadow:0 6px 16px -4px rgba(0,0,0,.8)}
.pillar-n{font:700 12.5px var(--b);letter-spacing:.28em;text-transform:uppercase;color:var(--gold)}
.pillar-n span{color:var(--dim)}
.pillar h3{margin:8px 0 12px;font-size:clamp(36px,3.4vw,50px);line-height:.95}
.pillar-lead{font:500 italic clamp(22px,1.8vw,26px)/1.3 var(--s);color:var(--gold2)}
.pillar-txt>p:not(.pillar-n):not(.pillar-lead){margin-top:16px;color:var(--mut)}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:22px}
.chips li{padding:7px 14px;border:1px solid var(--hair2);border-radius:999px;font-size:13.5px;color:var(--mut)}
.chips.sm li{padding:5px 11px;font-size:12.5px}
@media(max-width:700px){.pillar{grid-template-columns:84px minmax(0,1fr);gap:20px}.medal{width:80px;height:80px}.medal svg{width:34px;height:34px}.medal-n{width:28px;height:28px;font-size:15px;right:-6px;bottom:-2px}.pillar h3{font-size:34px}}
/* áudio */
.audio-in{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:clamp(40px,6vw,90px);align-items:center}
.audio-card{position:relative;padding:clamp(28px,4vw,46px);border-radius:24px;border:1px solid rgba(217,174,92,.35);background:radial-gradient(90% 80% at 50% 0,rgba(217,174,92,.16),transparent 70%),var(--card);box-shadow:0 50px 100px -50px rgba(217,174,92,.45)}
.wave{display:flex;align-items:center;gap:5px;height:150px}
.wave i{flex:1;height:var(--h);border-radius:999px;background:linear-gradient(180deg,var(--gold2),var(--gold3));transform-origin:center;animation:wv 1.6s ease-in-out var(--d) infinite}
@keyframes wv{0%,100%{transform:scaleY(.35)}50%{transform:scaleY(1)}}
.player{display:flex;align-items:center;gap:16px;margin-top:28px;padding-top:24px;border-top:1px solid var(--hair)}
.play{position:relative;flex:none;width:58px;height:58px;border-radius:50%;background:linear-gradient(180deg,#f7dcaa,#d9ae5c);box-shadow:0 0 0 8px rgba(217,174,92,.12),0 14px 30px -10px rgba(217,174,92,.7)}
.play::after{content:"";position:absolute;left:23px;top:18px;border-left:16px solid #190f02;border-top:11px solid transparent;border-bottom:11px solid transparent}
.player b{display:block;font:400 24px/1 var(--h);letter-spacing:.02em}
.player small{display:block;margin-top:4px;font-size:14px;color:var(--mut)}
.ctx{display:flex;flex-wrap:wrap;gap:10px;margin-top:26px}
.ctx li{padding:9px 16px;border:1px solid rgba(217,174,92,.35);border-radius:999px;font:600 13px var(--b);letter-spacing:.14em;text-transform:uppercase;color:var(--gold2)}
@media(max-width:900px){.audio-in{grid-template-columns:1fr}.audio-card{order:2}.wave{height:110px}}
/* 6 · diferencial */
.app{margin-top:56px}
.tabs{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:22px}
.tabs button{position:relative;width:100%;height:100%;display:block;padding:18px 18px 20px;border:1px solid var(--hair);border-radius:14px;background:transparent;color:var(--mut);font:inherit;text-align:left;cursor:pointer;overflow:hidden;transition:border-color .4s,background-color .4s,color .4s}
.tabs b{display:block;font:400 24px/1 var(--h);letter-spacing:.02em;color:var(--text);margin-bottom:6px}
.tabs span{display:block;font-size:14px;line-height:1.4}
.tabs .bar{position:absolute;left:0;bottom:0;height:2px;width:100%;background:var(--gold);transform:scaleX(0);transform-origin:left}
.tabs button[aria-selected=true]{border-color:rgba(217,174,92,.5);background:linear-gradient(180deg,rgba(217,174,92,.14),rgba(217,174,92,.02));color:var(--text)}
.tabs button[aria-selected=true] b{color:var(--gold2)}
.tabs button[aria-selected=true] .bar{animation:fill var(--dur,5.5s) linear forwards}
@keyframes fill{to{transform:scaleX(1)}}
.screen{position:relative;border-radius:16px;overflow:hidden;border:1px solid rgba(217,174,92,.35);background:#05070f;box-shadow:0 80px 160px -60px rgba(0,0,0,1),0 0 140px -40px rgba(217,174,92,.4)}
.screen .view{position:relative;aspect-ratio:1440/900}
.screen .view img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0;transform:scale(1.02);transition:opacity .8s var(--ease),transform 1.2s var(--ease)}
.screen .view img.on{opacity:1;transform:none}

@media(max-width:900px){.tabs{display:flex;overflow-x:auto;scrollbar-width:none;margin-inline:-18px;padding-inline:18px}.tabs::-webkit-scrollbar{display:none}.tabs li{flex:none}.tabs span{display:none}.tabs button{padding:14px 18px;white-space:nowrap}.tabs b{font-size:21px;margin:0}}
.app{position:relative}
.phand{position:absolute;left:0;top:0;z-index:6;width:40px;pointer-events:none;opacity:0;transform:translate(-36%,-8%);transition:left .9s cubic-bezier(.45,0,.2,1),top .9s cubic-bezier(.45,0,.2,1),opacity .4s}
.phand.on{opacity:1}
.phand svg{display:block;width:100%;filter:drop-shadow(0 8px 12px rgba(0,0,0,.75));transition:transform .15s}
.phand.click svg{transform:scale(.8)}
.phand i{position:absolute;left:36%;top:8%;width:52px;height:52px;margin:-26px 0 0 -26px;border-radius:50%;border:2px solid rgba(243,212,141,.95);opacity:0}
.phand.click i{animation:rp .6s ease-out}
@keyframes rp{0%{opacity:1;transform:scale(.3)}100%{opacity:0;transform:scale(1.6)}}
@media(max-width:900px){.phand{width:30px}}
/* teste */
.quizbox{margin-top:clamp(70px,8vw,110px);display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:clamp(30px,4vw,60px);align-items:start;padding:clamp(28px,4vw,52px);border-radius:24px;border:1px solid var(--hair2);background:radial-gradient(70% 90% at 0 0,rgba(217,174,92,.10),transparent 70%),var(--card)}
.quizbox h3{font-size:clamp(34px,3.2vw,46px)}
.quizbox .mut{margin-top:14px;font-size:16.5px}
.quiz{min-height:330px}
.q-prog{display:grid;grid-template-columns:repeat(5,1fr);gap:6px;margin-bottom:22px}
.q-prog i{height:3px;border-radius:2px;background:var(--hair2)}
.q-prog i.on{background:var(--gold)}
.q-n{font:700 12px var(--b);letter-spacing:.24em;text-transform:uppercase;color:var(--gold)}
.q-t{margin:10px 0 20px;font:400 clamp(30px,2.6vw,38px)/1.02 var(--h);letter-spacing:.01em}
.q-o{display:grid;gap:10px}
.q-o button{display:flex;align-items:center;gap:14px;width:100%;min-height:60px;padding:14px 18px;border-radius:12px;border:1px solid var(--hair2);background:var(--bg2);color:var(--text);font:500 16.5px/1.35 var(--b);text-align:left;cursor:pointer;transition:border-color .2s,background-color .2s}
.q-o button b{flex:none;display:grid;place-items:center;width:30px;height:30px;border-radius:50%;border:1px solid var(--hair2);font-size:13px;color:var(--mut)}
.q-o button:hover,.q-o button:focus-visible{border-color:var(--gold);background:rgba(217,174,92,.08)}
.q-o button:hover b{background:var(--gold);color:#140e04;border-color:var(--gold)}
.res h4{margin:8px 0 10px;font:400 clamp(34px,3vw,44px)/1 var(--h);letter-spacing:.01em;color:var(--gold2)}
.res>p{color:var(--mut)}
.bars{display:grid;gap:12px;margin:24px 0 26px}
.bar2{display:grid;grid-template-columns:150px 1fr 38px;gap:12px;align-items:center;font-size:14.5px}
.bar2 i{height:10px;border-radius:999px;background:var(--hair2);overflow:hidden}
.bar2 i b{display:block;height:100%;width:var(--w,0);border-radius:inherit;background:linear-gradient(90deg,var(--gold3),var(--gold2));transition:width 1.1s var(--ease)}
.bar2 em{font-style:normal;color:var(--dim);text-align:right}
.bar2.low span{color:var(--gold2);font-weight:600}
.redo{display:block;margin:14px auto 0;background:none;border:0;color:var(--dim);font:500 14.5px var(--b);text-decoration:underline;text-underline-offset:4px;cursor:pointer}
@media(max-width:900px){.quizbox{grid-template-columns:1fr}}
@media(max-width:480px){.bar2{grid-template-columns:104px 1fr 32px;font-size:13px}}
/* 7 · bônus */
.bono-shot{width:100%;border-radius:14px;border:1px solid var(--hair2);box-shadow:0 50px 100px -50px rgba(0,0,0,.95);-webkit-mask-image:linear-gradient(180deg,#000 60%,transparent);mask-image:linear-gradient(180deg,#000 60%,transparent)}
.bono-hero{position:relative;margin:56px auto -90px;width:min(900px,100%);z-index:0}
.bono-hero figcaption{position:absolute;left:50%;top:18px;transform:translateX(-50%);padding:6px 14px;border-radius:999px;background:rgba(7,7,8,.75);border:1px solid var(--hair2);font-size:12.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--gold2);white-space:nowrap}
.bonos{position:relative;z-index:1;display:grid;grid-template-columns:1fr 1fr;gap:16px}
.bono{position:relative;padding:34px 34px 30px;border-radius:20px;border:1px solid var(--hair);background:linear-gradient(180deg,rgba(22,20,26,.92),rgba(13,12,15,.96));-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);overflow:hidden;transition:border-color .4s,transform .4s var(--ease)}
.bono:hover{border-color:rgba(217,174,92,.45);transform:translateY(-4px)}
.bono-top{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:18px}
.bono-n{font:400 92px/.8 var(--h);color:transparent;-webkit-text-stroke:1.2px rgba(217,174,92,.65)}
.bono-k{padding:6px 12px;border-radius:999px;background:rgba(217,174,92,.12);font:700 11.5px var(--b);letter-spacing:.2em;text-transform:uppercase;color:var(--gold2)}
.bono h3{margin-bottom:12px}
.bono p{color:var(--mut);font-size:16.5px}
.disc{margin-top:22px;font-size:13.5px;color:var(--dim);text-align:center}
@media(max-width:760px){.bonos{grid-template-columns:1fr}.bono-hero{margin-bottom:-40px}}
/* luz que segue o cursor */
.spot{--x:50%;--y:50%}
.spot::after{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;background:radial-gradient(300px circle at var(--x) var(--y),rgba(217,174,92,.13),transparent 70%);opacity:0;transition:opacity .3s}
.spot:hover::after{opacity:1}
/* 8 · experiência: conjunto de aparelhos */
.devices{position:relative;width:100%;max-width:1120px;aspect-ratio:1120/600;margin:60px auto 0}
.devices::before{content:"";position:absolute;left:10%;right:10%;bottom:-2%;height:18%;border-radius:50%;background:radial-gradient(closest-side,rgba(217,174,92,.28),transparent 75%);filter:blur(20px)}
.dv{position:absolute}
.dv .scr{position:relative;overflow:hidden;background:#05070f}
.dv .scr img{width:100%;height:100%;object-fit:cover;object-position:0 0}
.dv .scr::after{content:"";position:absolute;inset:0;background:linear-gradient(125deg,rgba(255,255,255,.10),transparent 38%);pointer-events:none}
.desk{left:19%;top:0;width:62%}
.desk .scr{aspect-ratio:16/10;border:10px solid #101013;border-bottom-width:22px;border-radius:14px;outline:1px solid rgba(217,174,92,.35);box-shadow:0 50px 100px -50px rgba(0,0,0,1),0 0 120px -40px rgba(217,174,92,.45)}
.desk .neck{display:block;width:12%;height:7%;margin:0 auto;background:linear-gradient(90deg,#17161a,#2a2830,#17161a)}
.desk .stand{display:block;width:30%;height:2.2%;margin:0 auto;border-radius:6px 6px 2px 2px;background:linear-gradient(180deg,#2c2a31,#121114)}
.desk .neck{height:44px}.desk .stand{height:10px}
.lap{left:0;bottom:3%;width:44%;z-index:2}
.lap .scr{aspect-ratio:16/10;margin:0 7%;border:8px solid #0e0e11;border-bottom-width:12px;border-radius:12px 12px 2px 2px;outline:1px solid rgba(217,174,92,.3);box-shadow:0 40px 80px -40px rgba(0,0,0,1)}
.lap .kb{display:block;height:16px;border-radius:2px 2px 14px 14px;background:linear-gradient(180deg,#3a3840,#18171b 60%,#0b0b0d);box-shadow:0 20px 40px -20px rgba(0,0,0,1)}
.tab{right:4%;bottom:4%;width:27%;z-index:2}
.tab .scr{aspect-ratio:4/3;border:12px solid #0e0e11;border-radius:22px;outline:1px solid rgba(217,174,92,.3);box-shadow:0 40px 80px -40px rgba(0,0,0,1)}
.pho{right:28%;bottom:0;width:11.5%;z-index:3}
.pho .scr{aspect-ratio:9/19;border:6px solid #0b0b0e;border-radius:24px;outline:1px solid rgba(217,174,92,.35);box-shadow:0 40px 80px -30px rgba(0,0,0,1)}
.tap{position:absolute;z-index:5;width:clamp(26px,3.4vw,42px);pointer-events:none;transform:translate(-36%,-8%);animation:tap 8s ease-in-out infinite}
.tap svg{display:block;width:100%;filter:drop-shadow(0 6px 10px rgba(0,0,0,.7))}
.tap i{position:absolute;left:36%;top:8%;width:46px;height:46px;margin:-23px 0 0 -23px;border-radius:50%;border:2px solid rgba(243,212,141,.9);opacity:0;animation:ripple 8s ease-out infinite}
.t1{left:30%;top:34%}.t2{left:18%;top:72%;animation-delay:2s}.t2 i{animation-delay:2s}.t3{left:86%;top:66%;animation-delay:4s}.t3 i{animation-delay:4s}.t4{left:66%;top:78%;animation-delay:6s}.t4 i{animation-delay:6s}
@keyframes tap{0%,100%{opacity:0;transform:translate(-36%,10%) scale(1)}6%{opacity:1;transform:translate(-36%,-8%) scale(1)}10%{transform:translate(-36%,-8%) scale(.82)}14%{transform:translate(-36%,-8%) scale(1)}22%{opacity:1}26%{opacity:0}}
@keyframes ripple{0%,9%{opacity:0;transform:scale(.3)}10%{opacity:1;transform:scale(.4)}20%{opacity:0;transform:scale(1.5)}100%{opacity:0}}
.feats{display:grid;gap:10px;grid-template-columns:1fr 1fr;max-width:980px;margin:26px auto 30px}
.feats li{display:flex;align-items:center;gap:16px;padding:14px 18px;border:1px solid var(--hair);border-radius:12px;background:var(--card);font-size:17px}
.feats svg{flex:none;width:24px;height:24px;fill:none;stroke:var(--gold);stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
@media(max-width:760px){.feats{grid-template-columns:1fr}.devices{aspect-ratio:1120/680}.desk .scr{border-width:6px;border-bottom-width:12px;border-radius:8px}.desk .neck{height:18px}.desk .stand{height:5px}.lap .scr{border-width:4px;border-bottom-width:6px}.lap .kb{height:8px}.tab .scr{border-width:6px;border-radius:12px}.pho .scr{border-width:3px;border-radius:10px}}
/* 9 · para quem */
.forwho{display:grid;grid-template-columns:1fr 1fr;gap:12px 40px;margin:48px 0 40px}
.forwho li{display:flex;gap:14px;padding:16px 0;border-bottom:1px solid var(--hair);font-size:18px}
.forwho svg,.offer-col svg,.price-info svg{flex:none;width:20px;height:20px;margin-top:4px;fill:none;stroke:var(--gold);stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
.note{padding:24px 28px;border-radius:16px;border:1px solid var(--hair2);background:var(--card);color:var(--mut);font-size:16.5px}
.note b{color:var(--text)}
@media(max-width:760px){.forwho{grid-template-columns:1fr}}
/* 10 · objeções */
.obj{margin-top:46px}
.obj details{border-top:1px solid var(--hair)}
.obj details:last-child{border-bottom:1px solid var(--hair)}
.obj summary{list-style:none;display:flex;justify-content:space-between;align-items:center;gap:20px;padding:26px 0;cursor:pointer;font:500 italic clamp(22px,2vw,27px)/1.3 var(--s);color:var(--text)}
.obj summary::-webkit-details-marker{display:none}
.obj summary::after{content:"";flex:none;width:34px;height:34px;border-radius:50%;border:1px solid var(--hair2);background:linear-gradient(var(--gold),var(--gold)) center/12px 1.5px no-repeat,linear-gradient(var(--gold),var(--gold)) center/1.5px 12px no-repeat;transition:transform .4s var(--ease)}
.obj details[open] summary::after{transform:rotate(45deg)}
.obj details p{padding:0 60px 26px 0;color:var(--mut);font-size:17.5px}
/* 11 · oferta */
.offer-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:56px}
.offer-col{position:relative;padding:32px 28px;border-radius:20px;border:1px solid var(--hair);background:var(--card)}
.offer-col .k{font:700 12px var(--b);letter-spacing:.24em;text-transform:uppercase;color:var(--gold)}
.offer-col h3{margin:10px 0 18px;font-size:32px}
.offer-col li{display:flex;gap:12px;padding:10px 0;border-top:1px solid var(--hair);font-size:16px}
.offer-col.main{border-color:rgba(217,174,92,.45);background:radial-gradient(100% 70% at 50% 0,rgba(217,174,92,.13),transparent 70%),var(--card)}
.allin{margin-top:30px;text-align:center;font:500 italic clamp(24px,2.2vw,30px)/1.3 var(--s);color:var(--gold2)}
@media(max-width:900px){.offer-grid{grid-template-columns:1fr}}
/* 12 · investimento */
.price-wrap{position:relative;width:min(620px,100%);margin:56px auto 0;padding:2px;border-radius:28px;background:conic-gradient(from var(--a,0deg),#7a5a22,#f3d48d,#d9ae5c,#fff1c9,#a87e2f,#7a5a22);animation:spin 8s linear infinite}
@property --a{syntax:'<angle>';inherits:false;initial-value:0deg}
@keyframes spin{to{--a:360deg}}
.price-wrap::before{content:"";position:absolute;inset:-40px;z-index:-1;border-radius:60px;background:radial-gradient(closest-side,rgba(217,174,92,.28),transparent 75%);filter:blur(30px)}
.price{padding:clamp(34px,5vw,54px);border-radius:26px;background:radial-gradient(90% 60% at 50% 0,rgba(217,174,92,.15),transparent 70%),#0d0c10;text-align:center}
.price .pname{font:400 34px/1 var(--h);letter-spacing:.04em}
.price .by{margin-top:22px;font:500 italic 22px var(--s);color:var(--mut)}
.amount{display:flex;justify-content:center;align-items:flex-start;gap:8px;margin:2px 0 6px}
.amount .cur{margin-top:20px;font:400 34px var(--h);color:var(--gold2)}
.amount .num{font:400 clamp(110px,13vw,160px)/.86 var(--h);background:linear-gradient(180deg,#fff3d1,#d9ae5c 70%,#a87e2f);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 12px 30px rgba(217,174,92,.35))}
.price .cond{font-size:15.5px;color:var(--mut)}
.price .cta{width:100%;margin-top:28px}
.price-info{display:grid;gap:10px;margin-top:26px;padding-top:24px;border-top:1px solid var(--hair);text-align:left}
.price-info li{display:flex;gap:12px;font-size:15px;color:var(--mut)}
.decide{max-width:62ch;margin:22px auto 0}
/* 13 · garantia */
.guar{display:grid;grid-template-columns:auto 1fr;gap:clamp(30px,5vw,64px);align-items:center;padding:clamp(32px,4vw,56px);border-radius:24px;border:1px solid rgba(217,174,92,.3);background:radial-gradient(70% 120% at 0 50%,rgba(217,174,92,.12),transparent 60%),var(--card)}
.seal{position:relative;width:200px;height:200px;display:grid;place-items:center}
.seal svg{position:absolute;inset:0;animation:rot 30s linear infinite}
@keyframes rot{to{transform:rotate(360deg)}}
.seal text{font:700 13px var(--b);letter-spacing:.2em;text-transform:uppercase;fill:var(--gold)}
.seal .core{width:128px;height:128px;border-radius:50%;display:grid;place-items:center;text-align:center;background:radial-gradient(circle at 35% 30%,#fbe2ad,#c9933f 55%,#7d5520);color:#2a1a05;box-shadow:0 0 0 6px rgba(217,174,92,.15),0 20px 50px -15px rgba(0,0,0,.9),inset 0 2px 6px rgba(255,255,255,.5)}
.seal b{display:block;font:400 64px/.85 var(--h)}
.seal small{font:800 11px var(--b);letter-spacing:.2em;text-transform:uppercase}
.guar h2{font-size:clamp(40px,4.2vw,62px)}
.guar p{margin-top:18px;color:var(--mut)}
@media(max-width:760px){.guar{grid-template-columns:1fr;justify-items:center;text-align:center}.seal{width:170px;height:170px}.seal .core{width:110px;height:110px}}
/* 14 · fechamento */
.close{position:relative;padding:clamp(80px,9vw,130px) 0 clamp(90px,10vw,140px);overflow:hidden;background:radial-gradient(60% 50% at 50% 28%,rgba(217,174,92,.12),transparent 70%),#030304}
.fx{position:relative;width:min(560px,96%);aspect-ratio:1/1;margin:0 auto -30px;display:grid;place-items:center;isolation:isolate}
.fx i{position:absolute;display:block;pointer-events:none}
.fx-rays{inset:-16%;border-radius:50%;background:repeating-conic-gradient(rgba(243,212,141,.2) 0 5deg,transparent 5deg 17deg);-webkit-mask-image:radial-gradient(closest-side,transparent 30%,#000 46%,transparent 100%);mask-image:radial-gradient(closest-side,transparent 30%,#000 46%,transparent 100%);animation:rot 50s linear infinite;z-index:-3}
.fx-halo{inset:8%;border-radius:50%;background:radial-gradient(closest-side,rgba(255,196,96,.45),rgba(217,140,40,.15) 55%,transparent 72%);filter:blur(10px);animation:pulse 4.5s ease-in-out infinite;z-index:-2}
.fx-ring{border-radius:50%;z-index:-1}
.fx-ring.r1{inset:11%;border:1.5px solid rgba(243,212,141,.5);border-left-color:transparent;border-bottom-color:transparent;animation:rot 10s linear infinite}
.fx-ring.r2{inset:5%;border:1px dashed rgba(243,212,141,.3);animation:rot 34s linear infinite reverse}
.fx-img{width:94%;-webkit-mask-image:radial-gradient(ellipse 50% 50% at 50% 50%,#000 58%,transparent 99%);mask-image:radial-gradient(ellipse 50% 50% at 50% 50%,#000 58%,transparent 99%);animation:breath 6s ease-in-out infinite}
@keyframes breath{50%{transform:scale(1.03)}}
.close .embers{z-index:0}
.close-in{position:relative;z-index:1;text-align:center}
.close .not{margin:34px auto 0;display:grid;gap:6px;max-width:44ch;font-size:19px;color:var(--mut)}
.close .but{margin:22px auto 0;max-width:56ch;font-size:19px;color:var(--text)}
.close .quote{margin-top:34px}
.close .cta{margin-top:40px}
.sign{margin-top:46px;font:700 12.5px var(--b);letter-spacing:.24em;text-transform:uppercase;color:var(--dim)}
.foot{padding:56px 0 120px;border-top:1px solid var(--hair);color:var(--dim);font-size:13.5px;line-height:1.6}
.foot img{width:120px;margin-bottom:20px;opacity:.85}
.foot p+p{margin-top:10px}
/* barra fixa no celular */
.dock{position:fixed;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom));z-index:60;display:none;align-items:center;justify-content:space-between;gap:12px;padding:10px 10px 10px 18px;border-radius:14px;background:rgba(16,15,19,.94);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);border:1px solid var(--hair2);transform:translateY(160%);visibility:hidden;transition:transform .5s var(--ease),visibility 0s .5s}
.dock.on{transform:none;visibility:visible;transition:transform .5s var(--ease)}
.dock b{display:block;font:400 22px/1 var(--h);letter-spacing:.03em}
.dock span{font-size:13px;color:var(--gold2)}
.dock a{min-height:46px;padding:12px 18px;width:auto;font-size:13px}
@media(max-width:900px){.dock{display:flex}}
/* entrada */
.js .rv{opacity:0;transform:translateY(30px);transition:opacity .9s var(--ease),transform 1s var(--ease)}
.js .rv.in{opacity:1;transform:none}
.js.ok .rv{opacity:1;transform:none}
@media(prefers-reduced-motion:reduce){.js .rv{opacity:1;transform:none;transition:none}.hero-bg img,.forge-img{animation:none}}

/* ===== v27 · efeitos ===== */
.progress{position:fixed;inset:0 0 auto;height:3px;z-index:95;pointer-events:none;background:rgba(255,236,200,.05)}
.progress i{display:block;height:100%;width:100%;transform:scaleX(0);transform-origin:left;background:linear-gradient(90deg,#a87e2f,#f3d48d,#fff1c9);box-shadow:0 0 12px rgba(243,212,141,.8)}
.glow-cursor{position:fixed;left:0;top:0;width:520px;height:520px;margin:-260px 0 0 -260px;border-radius:50%;pointer-events:none;z-index:1;background:radial-gradient(closest-side,rgba(217,174,92,.09),transparent 70%);opacity:0;transition:opacity .6s;will-change:transform}
.glow-cursor.on{opacity:1}
main,footer{position:relative;z-index:2}
.hero h1 .wd{display:inline-block;opacity:0;transform:translateY(.45em) rotate(2deg);filter:blur(8px);transition:opacity .9s var(--ease),transform 1s var(--ease),filter .9s var(--ease);transition-delay:calc(var(--i)*70ms + 150ms)}
.hero h1.go .wd{opacity:1;transform:none;filter:none}

.hero-bg img{will-change:transform}
.showcase{transition:transform .25s ease-out}
.showcase .glare{position:absolute;inset:0;pointer-events:none;background:radial-gradient(600px circle at var(--gx,50%) var(--gy,0%),rgba(255,240,200,.10),transparent 55%);opacity:0;transition:opacity .4s;z-index:2}
.showcase:hover .glare{opacity:1}
.cta{--mx:0px;--my:0px;transform:translate(var(--mx),var(--my))}
.cta:hover{transform:translate(var(--mx),calc(var(--my) - 2px))}
.medal-ring{position:absolute;inset:-12px;border-radius:50%;border:1px dashed rgba(217,174,92,.45);animation:rot 26s linear infinite;pointer-events:none}
.pillar:hover .medal-ring{animation-duration:6s;border-color:rgba(243,212,141,.8)}
.medal{transition:box-shadow .6s}
.pillar:hover .medal{box-shadow:0 24px 70px -18px rgba(217,174,92,.9),0 0 0 10px rgba(217,174,92,.08)}
.kick{position:relative}
.rv.in .kick::before,.kick.rv.in::before{animation:kline 1s var(--ease) both}
@keyframes kline{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.why li,.struct li,.offer-col,.bono,.feats li{transition:transform .5s var(--ease),border-color .4s,box-shadow .5s}
.why li:hover,.struct li:hover,.offer-col:hover,.feats li:hover{transform:translateY(-4px);border-color:rgba(217,174,92,.4);box-shadow:0 30px 60px -30px rgba(217,174,92,.35)}
.amount .num{font-variant-numeric:tabular-nums}
.price-wrap{transition:transform .6s var(--ease)}
.price-wrap:hover{transform:translateY(-4px)}
.sec>.wrap,.sec>.narrow{position:relative}
@media(prefers-reduced-motion:reduce){.hero h1 .wd{opacity:1;transform:none;filter:none}.glow-cursor,.progress{display:none}}

/* v30 · blocos bem separados */
.blk{position:relative}
.tone-a{background:#060607}
.tone-b{background:radial-gradient(70% 60% at 50% 0,rgba(217,174,92,.10),transparent 70%),linear-gradient(180deg,#1a171e,#121015)}
.tone-b .why li,.tone-b .struct li,.tone-b .feats li,.tone-b .bono,.tone-b .offer-col,.tone-b .guar,.tone-b .obj details{background:rgba(6,6,7,.45)}
.blk::before{content:"";position:absolute;top:0;left:0;right:0;height:1px;z-index:3;background:linear-gradient(90deg,transparent,rgba(217,174,92,.55) 30%,rgba(243,212,141,.9) 50%,rgba(217,174,92,.55) 70%,transparent);transform:none;width:auto}
.blk::after{content:attr(data-n);position:absolute;top:0;left:50%;z-index:4;transform:translate(-50%,-50%);padding:7px 16px;border-radius:999px;border:1px solid rgba(217,174,92,.6);background:#0c0b0e;box-shadow:0 0 0 6px rgba(6,6,7,.9),0 0 24px rgba(217,174,92,.35);font:700 11px/1 var(--b);letter-spacing:.24em;text-transform:uppercase;color:var(--gold2);white-space:nowrap;width:auto;height:auto;margin:0;border-radius:999px}
.tone-b+.tone-a::before,.tone-a+.tone-b::before{box-shadow:0 0 30px rgba(217,174,92,.35)}
.blk .wrap,.blk .narrow{position:relative;z-index:1}
@media(max-width:600px){.blk::after{font-size:9.5px;letter-spacing:.18em;padding:6px 12px}}

/* v31 · topo com a imagem do ecossistema */
.hero{background:radial-gradient(60% 70% at 78% 45%,rgba(217,150,60,.16),transparent 70%),radial-gradient(40% 50% at 10% 20%,rgba(217,174,92,.05),transparent 70%),var(--bg);padding:120px 0 80px}
.hero::after{background:linear-gradient(0deg,var(--bg) 0%,transparent 18%)!important}
.hero-grid{display:grid;grid-template-columns:minmax(0,.86fr) minmax(0,1.14fr);gap:clamp(24px,3vw,48px);align-items:center;width:min(1360px,100% - 48px)}
.hero-in{max-width:none}
.hero h1{font-size:clamp(50px,4.7vw,80px)}
.hero .lead{font-size:clamp(17px,1.25vw,19px);max-width:none}
.hero .stats{max-width:none}
.hero-art{position:relative;top:auto;right:auto;width:auto;z-index:auto;transform:none;margin:0 -4% 0 0;isolation:isolate}
.hero-art-img{width:100%;height:auto;animation:float 7s ease-in-out infinite;-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 7%,#000 94%,transparent 100%),linear-gradient(180deg,transparent 0,#000 7%,#000 90%,transparent 100%);-webkit-mask-composite:source-in;mask-image:linear-gradient(90deg,transparent 0,#000 7%,#000 94%,transparent 100%),linear-gradient(180deg,transparent 0,#000 7%,#000 90%,transparent 100%);mask-composite:intersect}
.ha-glow{position:absolute;inset:12% 8%;z-index:-1;border-radius:50%;background:radial-gradient(closest-side,rgba(255,180,80,.30),transparent 75%);filter:blur(30px);animation:pulse 5s ease-in-out infinite}
@keyframes float{50%{transform:translateY(-10px)}}
@media(max-width:1000px){.hero-grid{grid-template-columns:1fr}.hero-art{order:-1;margin:-20px -18px 10px}.hero{padding:96px 0 60px}.hero h1{font-size:clamp(44px,11vw,64px)}}
@media(prefers-reduced-motion:reduce){.hero-art-img{animation:none}}

/* v32 · imagem e texto lado a lado, mesma altura */
.hero{min-height:auto;padding:110px 0 70px}
.hero-grid{grid-template-columns:minmax(0,.82fr) minmax(0,1.18fr);align-items:stretch;column-gap:clamp(20px,2.5vw,40px);row-gap:44px;width:min(1400px,100% - 48px)}
.hero-in{display:flex;flex-direction:column;justify-content:center}
.hero h1{font-size:clamp(48px,4.4vw,76px)}
.hero .lead{font-size:clamp(16.5px,1.15vw,18.5px);margin-top:22px}
.hero .lead+.lead{margin-top:12px}
.hero-cta{margin-top:30px}
.hero-art{display:flex;align-items:center;justify-content:flex-start;margin:0 calc(-1 * max(24px,(100vw - 1400px)/2)) 0 -2%}
.hero-art-img{width:100%;height:100%;max-height:none;object-fit:cover;object-position:56% 50%;
 -webkit-mask-image:linear-gradient(90deg,transparent 0,#000 8%,#000 92%,transparent 100%),linear-gradient(180deg,transparent 0,#000 6%,#000 92%,transparent 100%);mask-image:linear-gradient(90deg,transparent 0,#000 8%,#000 92%,transparent 100%),linear-gradient(180deg,transparent 0,#000 6%,#000 92%,transparent 100%)}
.hero-stats{grid-column:1 / -1;margin-top:0!important;max-width:none!important}
.hero-stats li{padding:22px 24px}
@media(max-width:1000px){.hero-grid{grid-template-columns:1fr;row-gap:28px}.hero-art{order:-1;margin:-10px -18px 0;aspect-ratio:1672/941}.hero-art-img{object-fit:contain}.hero-stats{grid-column:auto}}

/* v32b · fundo do topo na mesma cor das bordas da imagem */
.hero{background:radial-gradient(55% 70% at 74% 52%,rgba(120,60,10,.22),transparent 72%),linear-gradient(180deg,#000 0%,#030201 35%,#0a0602 75%,#120a03 100%)!important}
.hero::after{background:linear-gradient(180deg,transparent 80%,#070708 100%)!important}
.hero .embers{opacity:.7}
.hero-art-img{object-position:74% 50%;-webkit-mask-image:linear-gradient(90deg,transparent 0,rgba(0,0,0,.35) 8%,#000 22%,#000 100%),linear-gradient(180deg,transparent 0,#000 14%,#000 82%,transparent 100%)!important;-webkit-mask-composite:source-in!important;mask-image:linear-gradient(90deg,transparent 0,rgba(0,0,0,.35) 8%,#000 22%,#000 100%),linear-gradient(180deg,transparent 0,#000 14%,#000 82%,transparent 100%)!important;mask-composite:intersect!important}
.hero-stats{background:rgba(0,0,0,.35)!important;border-color:rgba(217,174,92,.25)!important}

/* v32c · imagem inteira, sem corte, da coluna até a borda da tela */
.hero-art-img{object-fit:contain!important;height:auto!important;width:100%!important;max-height:100%}
@media(min-width:1001px){.hero-grid{align-items:center}.hero-art{align-self:stretch}}

/* v33 · áudio com o fone */
.tone-x{background:#000}
.audio-in{grid-template-columns:minmax(0,1.45fr) minmax(0,.85fr)!important;align-items:center;width:min(1400px,100% - 48px)!important;gap:clamp(10px,2vw,30px)!important}
.audio h2{font-size:clamp(40px,3.6vw,60px)}
.fone{position:relative;margin:0 0 0 calc(-1 * max(24px,(100vw - 1400px)/2));isolation:isolate}
.fone-img{width:100%;height:auto;-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 6%,#000 86%,transparent 100%),linear-gradient(180deg,transparent 0,#000 8%,#000 88%,transparent 100%);-webkit-mask-composite:source-in;mask-image:linear-gradient(90deg,transparent 0,#000 6%,#000 86%,transparent 100%),linear-gradient(180deg,transparent 0,#000 8%,#000 88%,transparent 100%);mask-composite:intersect;animation:float 7s ease-in-out infinite}
.fone-glow{position:absolute;inset:18% 22%;z-index:-1;border-radius:50%;background:radial-gradient(closest-side,rgba(255,180,80,.35),transparent 75%);filter:blur(30px);animation:pulse 4s ease-in-out infinite}
.fone-wave{position:absolute;left:66.5%;top:56.5%;display:flex;gap:3px;align-items:center;height:5.5%;transform:translate(-50%,-50%);mix-blend-mode:screen}
.fone-wave i{width:4px;height:100%;border-radius:4px;background:#ffd98a;box-shadow:0 0 8px #ffb84d;animation:wv 1.1s ease-in-out var(--d) infinite}
@media(max-width:900px){.audio-in{grid-template-columns:1fr!important}.fone{margin:0 -18px;order:-1}}
/* v33 · vitrine dos recursos */
.eco{position:relative;margin-top:50px}
.rtabs{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:22px}
.rtabs button{position:relative;width:100%;height:100%;display:block;padding:18px 18px 20px;border:1px solid var(--hair);border-radius:14px;background:rgba(6,6,7,.5);color:var(--mut);font:inherit;text-align:left;cursor:pointer;overflow:hidden;transition:border-color .4s,background-color .4s}
.rtabs .rn{display:block;font:400 34px/.9 var(--h);color:transparent;-webkit-text-stroke:1px rgba(217,174,92,.7);margin-bottom:10px}
.rtabs b{display:block;font:400 23px/1 var(--h);letter-spacing:.02em;color:var(--text);margin-bottom:6px}
.rtabs small{display:block;font-size:13.5px;line-height:1.4}
.rtabs .bar{position:absolute;left:0;bottom:0;height:2px;width:100%;background:var(--gold);transform:scaleX(0);transform-origin:left}
.rtabs button[aria-selected=true]{border-color:rgba(217,174,92,.55);background:linear-gradient(180deg,rgba(217,174,92,.16),rgba(217,174,92,.03))}
.rtabs button[aria-selected=true] b{color:var(--gold2)}
.rtabs button[aria-selected=true] .rn{color:var(--gold2);-webkit-text-stroke:0}
.rtabs button[aria-selected=true] .bar{animation:fill 7s linear forwards}
.screen .chrome span{margin-left:12px;font-size:13px;color:var(--dim)}
.screen .view img{object-fit:cover;object-position:0 0}
@media(max-width:900px){.rtabs{display:flex;overflow-x:auto;scrollbar-width:none;margin-inline:-18px;padding-inline:18px}.rtabs::-webkit-scrollbar{display:none}.rtabs li{flex:none;width:72%}.rtabs small{display:none}}

/* v34 · plataforma: mockup com pontos interativos */
.mock{position:relative;margin:30px calc(-1 * max(0px,(100vw - 1180px)/2 - 60px)) 0;isolation:isolate}
.mock-img{width:100%;height:auto;display:block;-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 6%,#000 94%,transparent 100%),linear-gradient(180deg,transparent 0,#000 6%,#000 90%,transparent 100%);-webkit-mask-composite:source-in;mask-image:linear-gradient(90deg,transparent 0,#000 6%,#000 94%,transparent 100%),linear-gradient(180deg,transparent 0,#000 6%,#000 90%,transparent 100%);mask-composite:intersect}
.mock-glow{position:absolute;inset:12% 18%;z-index:-1;border-radius:50%;background:radial-gradient(closest-side,rgba(255,170,70,.30),transparent 75%);filter:blur(40px);animation:pulse 5s ease-in-out infinite}
.hs{position:absolute;left:var(--x);top:var(--y);z-index:3;width:38px;height:38px;margin:-19px 0 0 -19px;border-radius:50%;border:0;padding:0;cursor:pointer;background:radial-gradient(circle,#ffe7b3,#d9ae5c 60%,#a87e2f);color:#190f02;font:400 20px/38px var(--h);box-shadow:0 0 0 6px rgba(217,174,92,.25),0 10px 24px -6px rgba(0,0,0,.9);transition:transform .4s var(--ease)}
.hs::before,.hs::after{content:"";position:absolute;inset:-6px;border-radius:50%;border:2px solid rgba(243,212,141,.75);animation:hsring 2.2s ease-out infinite;pointer-events:none}
.hs::after{animation-delay:1.1s}
@keyframes hsring{0%{transform:scale(.7);opacity:1}100%{transform:scale(2.1);opacity:0}}
.hs.on{transform:scale(1.25);box-shadow:0 0 0 8px rgba(243,212,141,.35),0 0 40px rgba(255,200,110,.9)}
.tip{position:absolute;left:var(--x);top:var(--y);z-index:4;width:min(300px,34vw);padding:16px 18px;border-radius:14px;border:1px solid rgba(217,174,92,.55);background:rgba(10,9,12,.88);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);box-shadow:0 30px 60px -20px rgba(0,0,0,.95),0 0 40px -10px rgba(217,174,92,.45);opacity:0;pointer-events:none;transform:translate(34px,-50%) scale(.94);transition:opacity .45s var(--ease),transform .55s var(--ease)}
.tip.l{transform:translate(calc(-100% - 34px),-50%) scale(.94)}
.tip.on{opacity:1;transform:translate(34px,-50%)}
.tip.l.on{transform:translate(calc(-100% - 34px),-50%)}
.tip b{display:block;font:400 26px/1 var(--h);letter-spacing:.02em;color:var(--gold2);margin-bottom:6px}
.tip span{display:block;font-size:14.5px;line-height:1.45;color:#e7e2d8}
.stepper{position:relative;display:grid;grid-template-columns:repeat(5,1fr);gap:0;margin:30px auto 0;max-width:1000px;padding-top:0;overflow:visible}
.stepper::before{content:"";position:absolute;left:10%;right:10%;top:19px;height:1px;background:rgba(217,174,92,.3)}
.stepper button{position:relative;width:100%;display:flex;flex-direction:column;align-items:center;gap:10px;padding:0 8px 14px;overflow:visible!important;border:0!important;background:none!important;color:var(--mut);font:inherit;cursor:pointer;text-align:center}
.stepper em{position:relative;display:grid;place-items:center;width:38px;height:38px;margin-top:0;border-radius:50%;border:1px solid rgba(217,174,92,.45);background:#0b0a0d;font:400 18px/1 var(--h);font-style:normal;color:var(--gold);transition:all .4s var(--ease)}
.stepper b{font:400 21px/1 var(--h)!important;letter-spacing:.03em;color:var(--mut)!important;margin:0!important}
.stepper .bar{position:absolute;left:25%;right:25%;bottom:0;height:2px;background:var(--gold);transform:scaleX(0)}
.stepper button[aria-selected=true] em{background:radial-gradient(circle,#ffe7b3,#d9ae5c 60%,#a87e2f);color:#190f02;border-color:transparent;box-shadow:0 0 24px rgba(243,212,141,.7)}
.stepper button[aria-selected=true] b{color:var(--gold2)!important}
.stepper button[aria-selected=true] .bar{animation:fill 4.6s linear forwards}
@media(max-width:900px){.mock{margin:20px -18px 0}.hs{width:28px;height:28px;margin:-14px 0 0 -14px;font-size:15px;line-height:28px}.tip{display:none}.stepper{display:flex;overflow-x:auto;scrollbar-width:none;max-width:none;margin-inline:-18px;padding:18px 18px 0}.stepper::-webkit-scrollbar{display:none}.stepper li{flex:none;width:34%}.stepper::before{left:0;right:0}}
'''

HTML = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src SCRIPTHASHES https://connect.facebook.net; style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data: https:; connect-src https:; media-src blob:; object-src 'none'; base-uri 'none'; form-action 'none'">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Los 5 Pilares de la Prosperidad · Ecosistema digital de desarrollo integral</title>
<meta name="description" content="Un ecosistema digital de desarrollo integral que conecta cinco dimensiones fundamentales de la vida con diagnóstico, biblioteca de contenidos, jornada de aplicación, audio y seguimiento del progreso.">
<meta name="theme-color" content="#070708">
<meta property="og:type" content="website">
<meta property="og:title" content="Los 5 Pilares de la Prosperidad · Un ecosistema, cinco dimensiones">
<meta property="og:description" content="Un ecosistema digital de desarrollo integral: diagnóstico, biblioteca de contenidos, jornada de 90 misiones, audio y seguimiento del progreso en cinco dimensiones de la vida.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Cormorant+Garamond:ital,wght@1,500;1,600&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap">
<script>document.documentElement.className+=' js';setTimeout(function(){{if(!window.__ok)document.documentElement.className+=' ok'}},2500)</script>
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">Saltar al contenido</a>
<div class="progress" aria-hidden="true"><i id="prog"></i></div>
<div class="glow-cursor" id="gcur" aria-hidden="true"></div>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><linearGradient id="gg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff1c9"/><stop offset=".55" stop-color="#e3b867"/><stop offset="1" stop-color="#a87e2f"/></linearGradient></defs></svg>

<header class="top">
 {LOGO}
 <a class="mini" data-co href="#inversion">Acceso · <span data-price>US$ 19,90</span></a>
</header>

<main id="main">

<!-- BLOQUE 1 · HERO -->
<section class="hero" aria-labelledby="h1">
 <div class="embers" aria-hidden="true">{EMBERS}</div>
 <div class="wrap hero-grid">
  <div class="hero-in">
   <p class="kick rv">Una nueva mirada sobre lo que significa prosperar</p>
   <h1 id="h1" class="rv">No basta con conquistar más.<span class="it">Hay que construir una vida capaz de sostener tus conquistas.</span></h1>
   <p class="lead rv">Puedes estar creciendo en tu profesión, trabajando por tu libertad financiera y persiguiendo tus objetivos. Pero <b>¿tu salud, tus relaciones, tu vida espiritual y tu desarrollo están creciendo al mismo ritmo?</b></p>
   <p class="lead rv">Conoce <b>Los 5 Pilares de la Prosperidad</b>: un ecosistema digital de desarrollo integral que conecta cinco dimensiones fundamentales de la vida con diagnóstico, biblioteca de contenidos, rutas de aplicación, ejercicios prácticos, audio y herramientas de seguimiento.</p>
   <div class="hero-cta rv"><a class="cta" data-co href="#inversion">Quiero empezar a construir mis 5 pilares <svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a></div>
  </div>
  <figure class="hero-art rv"><i class="ha-glow" aria-hidden="true"></i>{HERO_ART}</figure>
   <ul class="stats hero-stats rv">
    <li><b data-count="5">5</b><span>Dimensiones de desarrollo</span></li>
    <li><b data-count="90">90</b><span>Misiones guiadas</span></li>
    <li><b class="ico-a"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 14v-2a8 8 0 0 1 16 0v2"/><rect x="3" y="14" width="4" height="7" rx="1.5"/><rect x="17" y="14" width="4" height="7" rx="1.5"/></svg></b><span>Audio para acompañar el aprendizaje</span></li>
    <li><b data-count="1">1</b><span>Ecosistema integrado</span></li>
   </ul>
 </div>
</section>

<div class="marquee" aria-hidden="true"><div class="marquee-in"><span>Salud física y mental</span><span>Desarrollo personal y espiritualidad</span><span>Relaciones</span><span>Carrera y emprendimiento</span><span>Finanzas</span><span>Salud física y mental</span><span>Desarrollo personal y espiritualidad</span><span>Relaciones</span><span>Carrera y emprendimiento</span><span>Finanzas</span></div></div>

<!-- BLOQUE 2 · IDENTIFICACIÓN -->
<section data-n="01 · Tu realidad" class="blk tone-a sec" aria-labelledby="h2b">
 <div class="wrap">
  <div class="ident">
   <div>
    <h2 id="h2b" class="rv">Tal vez estás conquistando algunas cosas…<span class="it">pero sientes que todavía falta algo.</span></h2>
    <p class="lead rv" style="margin-top:28px">Te despiertas, trabajas, resuelves problemas, cumples compromisos e intentas dar cuenta de todo. Y en medio de esa rutina, algunas cosas importantes empiezan a quedar para después.</p>
    <ul class="later rv">
     <li><span>La salud queda</span><em>para cuando haya tiempo.</em></li>
     <li><span>La familia queda</span><em>para cuando baje el trabajo.</em></li>
     <li><span>El desarrollo personal queda</span><em>para cuando la rutina se calme.</em></li>
     <li><span>La organización financiera queda</span><em>para el próximo mes.</em></li>
     <li><span>Y tus objetivos más importantes</span><em>siguen esperando.</em></li>
    </ul>
    <p class="mut rv">No necesariamente porque no tengas ganas de cambiar. Sino porque <b>es difícil cuidar de todo cuando no tienes claridad sobre lo que necesita atención primero.</b></p>
   </div>
   <figure class="brj rv" aria-hidden="true"><video id="brj" muted autoplay loop playsinline preload="none" poster="{POSTER}" width="560" height="560"></video></figure>
  </div>
  <div class="bigq rv">
   <p class="kick">Hay una pregunta que merece hacerse</p>
   <p class="quote">¿Estás realmente construyendo la vida que deseas, o solo administrando las responsabilidades que aparecen cada día?</p>
  </div>
 </div>
</section>

<!-- BLOQUE 3 · QUIEBRE DE CREENCIA -->
<section data-n="02 · Nueva perspectiva" class="blk tone-b sec belief" aria-labelledby="h3b">
 <div class="wrap center">
  <p class="kick rv">Quiebre de creencia</p>
  <h2 id="h3b" class="rv">La prosperidad que buscas<span class="it">tal vez sea más grande de lo que imaginas.</span></h2>
  <p class="lead rv" style="margin-top:28px">Durante mucho tiempo nos acostumbraron a asociar la prosperidad sobre todo con dinero, patrimonio y logros profesionales. Pero piensa por un instante.</p>
  <ul class="why">
   <li class="rv">¿De qué sirve una carrera exitosa <b>si no puedes disfrutar la vida?</b></li>
   <li class="rv">¿De qué sirven los objetivos financieros <b>si no hay organización para alcanzarlos?</b></li>
   <li class="rv">¿De qué sirve saber tanto <b>si no conviertes el conocimiento en actitudes?</b></li>
  </ul>
  <p class="lead rv">La prosperidad también incluye la calidad de tus decisiones, tu salud, las personas a tu alrededor, tu dirección espiritual y la capacidad de construir un futuro con responsabilidad.</p>
  <p class="quote rv">Una vida verdaderamente bien construida no depende de una sola conquista. Depende de fundamentos que necesitan caminar juntos.</p>
 </div>
</section>

<!-- PUENTE · LA ESTATUA -->
<section data-n="03 · El proceso" class="blk tone-x forge" aria-labelledby="hfg">
 <div class="wrap forge-in">
  <figure class="forge-art rv"><i class="forge-rays" aria-hidden="true"></i><i class="forge-halo" aria-hidden="true"></i><div class="strike">{ESTATUA}</div><i class="forge-glow" aria-hidden="true"></i><i class="forge-wave" aria-hidden="true"></i><div class="burst" aria-hidden="true"><b style="--dx:60;--dy:-70"></b><b style="--dx:90;--dy:-20"></b><b style="--dx:70;--dy:40"></b><b style="--dx:30;--dy:-95"></b><b style="--dx:-20;--dy:-80"></b><b style="--dx:110;--dy:-55"></b><b style="--dx:45;--dy:75"></b><b style="--dx:-40;--dy:-40"></b><b style="--dx:120;--dy:10"></b><b style="--dx:10;--dy:-120"></b></div><div class="embers" aria-hidden="true">{EMBERS}</div></figure>
  <div>
   <p class="kick rv">90 días · 90 golpes de cincel</p>
   <h2 id="hfg" class="rv">Tu vida no se arregla de un día para otro.<span class="it">Se esculpe, un golpe por día.</span></h2>
   <p class="lead rv" style="margin-top:24px">Nadie va a esculpirla por ti, y tampoco hace falta hacerlo todo hoy. Cada misión de 10 a 30 minutos es un golpe de cincel sobre el pilar que más lo necesita.</p>
   <p class="forge-k rv">En 90 días, la forma aparece.</p>
  </div>
 </div>
</section>

<!-- BLOQUE 4 · LA SOLUCIÓN -->
<section data-n="04 · La solución" class="blk tone-b sec sol" aria-labelledby="h4b">
 <div class="wrap">
  <div class="center sol-head">
   <p class="kick rv">La solución</p>
   <h2 id="h4b" class="rv">Para reunir esos fundamentos en un solo lugar<span class="it">nació Los 5 Pilares de la Prosperidad.</span></h2>
   <p class="lead rv">Imagina tener un entorno digital donde diferentes dimensiones de tu vida dejan de ser temas aislados y pasan a formar parte de una misma jornada.</p>
   <p class="lead rv">Un lugar donde puedes visualizar tu punto de partida, profundizar tus conocimientos, identificar tus prioridades, realizar prácticas y acompañar el camino que estás construyendo.</p>
  </div>
  <figure class="showcase rv"><div class="chrome" aria-hidden="true"><i></i><i></i><i></i><span>Los 5 Pilares · Hoy</span></div>{TORRE}</figure>
  <p class="real center">Pantalla real de la plataforma</p>
  <p class="quote center rv" style="max-width:36ch;margin:52px auto 0">Eso es Los 5 Pilares de la Prosperidad: un ecosistema que conecta cinco dimensiones fundamentales del desarrollo humano.</p>
  <p class="lead center rv" style="margin-top:40px">En vez de información dispersa, tienes una estructura para:</p>
  <ol class="struct">
   <li class="rv">Entender tu punto de partida.</li>
   <li class="rv">Identificar qué áreas merecen más atención.</li>
   <li class="rv">Profundizar en los fundamentos de cada dimensión.</li>
   <li class="rv">Hacer ejercicios y acciones prácticas.</li>
   <li class="rv">Registrar tus reflexiones.</li>
   <li class="rv">Acompañar tu propio progreso.</li>
  </ol>
  <p class="quote center rv" style="max-width:34ch;margin:46px auto 0">No se trata de consumir más contenido. Se trata de tener una referencia para organizar lo que aprendes y ponerlo en práctica, un paso a la vez.</p>
 </div>
</section>

<!-- BLOQUE 5 · LOS CINCO PILARES -->
<section data-n="05 · Las 5 dimensiones" class="blk tone-a sec" id="pilares" aria-labelledby="h5b">
 <div class="wrap">
  <div class="center">
   <p class="kick rv">Cinco dimensiones de desarrollo</p>
   <h2 id="h5b" class="rv">Un ecosistema. Cinco dimensiones.<span class="it">Una vida que merece ser construida por completo.</span></h2>
  </div>
  <div class="pillars">{pilares_html}
  </div>
 </div>
</section>

<!-- ÁUDIO EN CADA CAPÍTULO -->
<section data-n="06 · En audio" class="blk tone-x sec audio" aria-labelledby="hau">
 <div class="wrap audio-in">
  <figure class="fone rv"><i class="fone-glow" aria-hidden="true"></i>{FONE}<div class="fone-wave" aria-hidden="true"><i style="--d:0.00s"></i><i style="--d:0.12s"></i><i style="--d:0.24s"></i><i style="--d:0.36s"></i><i style="--d:0.48s"></i><i style="--d:0.60s"></i><i style="--d:0.72s"></i><i style="--d:0.84s"></i><i style="--d:0.96s"></i></div></figure>
  <div>
   <p class="kick rv">Lee o escucha</p>
   <h2 id="hau" class="rv">Los contenidos también en audio.<span class="it">Escúchalos en el tránsito, en el transporte o mientras haces las tareas del día a día.</span></h2>
   <p class="lead rv" style="margin-top:24px">No necesitas sentarte frente a una pantalla para avanzar. Cada capítulo de la biblioteca tiene audio: escúchalo en el tránsito, en el bus o el metro, mientras cocinas, ordenas la casa o haces ejercicio. Después vuelves a la plataforma para hacer el ejercicio y marcar tu checklist.</p>
   <ul class="ctx rv"><li>En el tránsito</li><li>En el transporte</li><li>En las tareas de casa</li><li>Entrenando</li></ul>
  </div>
 </div>
</section>

<!-- BLOQUE 6 · EL DIFERENCIAL -->
<section data-n="07 · La plataforma" class="blk tone-a sec" id="plataforma" aria-labelledby="h6b">
 <div class="wrap">
  <div class="center">
   <p class="kick rv">Una experiencia integrada</p>
   <h2 id="h6b" class="rv">No recibes solo conocimiento.<span class="it">Recibes una estructura para ponerlo en movimiento.</span></h2>
   <p class="lead rv" style="margin:26px auto 0;max-width:60ch">Imagina abrir tu plataforma y encontrar, en un solo entorno, todo lo que necesitas para tu jornada de desarrollo.</p>
  </div>
  <div class="app">
   <span class="phand" id="phand" aria-hidden="true"><svg viewBox="0 0 24 24"><path fill="#fff" stroke="#14141a" stroke-width="1.3" stroke-linejoin="round" d="M9 2.5c.9 0 1.6.7 1.6 1.6v6.2l.6-.1c.9-.1 1.6.4 1.8 1.2l.1.2.4-.1c.9-.1 1.6.4 1.8 1.2l.1.3h.3c.9 0 1.6.7 1.7 1.6v3.3c0 3-2.4 5.4-5.4 5.4h-1.4c-1.8 0-3.4-.9-4.4-2.3l-3-4.3c-.5-.7-.3-1.7.4-2.2.7-.5 1.6-.4 2.2.2l1.6 1.7V4.1c0-.9.7-1.6 1.6-1.6z"/></svg><i></i></span>
   <figure class="mock rv"><i class="mock-glow" aria-hidden="true"></i>{MOCK}<button type="button" class="hs r" style="--x:33%;--y:35%" data-i="0" aria-label="Paso 1"><span>1</span></button><button type="button" class="hs r" style="--x:48%;--y:33%" data-i="1" aria-label="Paso 2"><span>2</span></button><button type="button" class="hs l" style="--x:80%;--y:56%" data-i="2" aria-label="Paso 3"><span>3</span></button><button type="button" class="hs r" style="--x:27%;--y:69%" data-i="3" aria-label="Paso 4"><span>4</span></button><button type="button" class="hs l" style="--x:74%;--y:26%" data-i="4" aria-label="Paso 5"><span>5</span></button><div class="tip r" style="--x:33%;--y:35%" data-i="0" aria-hidden="true"><b>{STEPS6[0][0]}</b><span>{STEPS6[0][1]}</span></div><div class="tip r" style="--x:48%;--y:33%" data-i="1" aria-hidden="true"><b>{STEPS6[1][0]}</b><span>{STEPS6[1][1]}</span></div><div class="tip l" style="--x:80%;--y:56%" data-i="2" aria-hidden="true"><b>{STEPS6[2][0]}</b><span>{STEPS6[2][1]}</span></div><div class="tip r" style="--x:27%;--y:69%" data-i="3" aria-hidden="true"><b>{STEPS6[3][0]}</b><span>{STEPS6[3][1]}</span></div><div class="tip l" style="--x:74%;--y:26%" data-i="4" aria-hidden="true"><b>{STEPS6[4][0]}</b><span>{STEPS6[4][1]}</span></div></figure>
   <ul class="tabs stepper" role="tablist" aria-label="Lo que encuentras en la plataforma">{steps_html}</ul>

  </div>
  <div class="quizbox rv" id="diagnostico">
   <div>
    <p class="kick">Pruébalo ahora · gratis</p>
    <h3>Descubre tu punto de partida en 2 minutos.</h3>
    <p class="mut">Esta es la versión corta del diagnóstico: 5 preguntas, una por pilar. Sin pedir tu correo, y tus respuestas no salen de tu pantalla. Dentro de la plataforma, el diagnóstico completo tiene 15 afirmaciones.</p>
   </div>
   <div class="quiz" id="quiz" aria-live="polite"><noscript><p>La prueba necesita JavaScript activado.</p></noscript></div>
  </div>
 </div>
</section>

<!-- BLOQUE 7 · LOS CUATRO BONOS -->
<section data-n="08 · Recursos complementarios" class="blk tone-b sec" id="bonos" aria-labelledby="h7b">
 <div class="wrap">
  <div class="center">
   <p class="kick rv">Recursos complementarios</p>
   <h2 id="h7b" class="rv">Y el ecosistema se completa<span class="it">con cuatro recursos complementarios.</span></h2>
   <p class="lead rv" style="margin:22px auto 0;max-width:58ch">Cuatro áreas que fortalecen tu jornada, integradas en el mismo entorno e incluidas en el mismo acceso.</p>
  </div>
  <div class="eco rv">
   <span class="phand" id="rhand" aria-hidden="true"><svg viewBox="0 0 24 24"><path fill="#fff" stroke="#14141a" stroke-width="1.3" stroke-linejoin="round" d="M9 2.5c.9 0 1.6.7 1.6 1.6v6.2l.6-.1c.9-.1 1.6.4 1.8 1.2l.1.2.4-.1c.9-.1 1.6.4 1.8 1.2l.1.3h.3c.9 0 1.6.7 1.7 1.6v3.3c0 3-2.4 5.4-5.4 5.4h-1.4c-1.8 0-3.4-.9-4.4-2.3l-3-4.3c-.5-.7-.3-1.7.4-2.2.7-.5 1.6-.4 2.2.2l1.6 1.7V4.1c0-.9.7-1.6 1.6-1.6z"/></svg><i></i></span>
   <ul class="rtabs" role="tablist" aria-label="Recursos complementarios"><li><button type="button" role="tab" aria-selected="true"><span class="rn">01</span><b>Gestión del tiempo</b><small>Tus 168 horas, prioridades y trabajo profundo.</small><i class="bar"></i></button></li><li><button type="button" role="tab" aria-selected="false"><span class="rn">02</span><b>Inteligencia emocional</b><small>Gatillos, autocontrol y presión.</small><i class="bar"></i></button></li><li><button type="button" role="tab" aria-selected="false"><span class="rn">03</span><b>Comunicación</b><small>Claridad, influencia ética y negociación.</small><i class="bar"></i></button></li><li><button type="button" role="tab" aria-selected="false"><span class="rn">04</span><b>El Mapa · 21 oportunidades</b><small>Negocios digitales y plan de ejecución.</small><i class="bar"></i></button></li></ul>
   <div class="screen big"><div class="chrome" aria-hidden="true"><i></i><i></i><i></i><span>Los 5 Pilares · Recursos complementarios</span></div><div class="view" id="rview">{RSHOTS}</div></div>
   <p class="real center">Pantallas reales · cada recurso con capítulos, audio, anotaciones y progreso</p>
  </div>
  <p class="disc">Las oportunidades presentadas en El Mapa son educativas. No representan promesa de ingresos ni garantía de resultados financieros.</p>
 </div>
</section>

<!-- BLOQUE 8 · LA EXPERIENCIA EN LA PRÁCTICA -->
<section data-n="09 · La experiencia" class="blk tone-a sec" aria-labelledby="h8b">
 <div class="wrap">
  <div class="center">
   <p class="kick rv">La experiencia en la práctica</p>
   <h2 id="h8b" class="rv">Tu evolución necesita ser acompañada,<span class="it">no solo deseada.</span></h2>
   <p class="lead rv" style="margin:24px auto 0;max-width:58ch">El mismo ecosistema en la computadora, el notebook, la tableta o el celular. Abres donde estés y sigues desde donde quedaste.</p>
  </div>
  <div class="devices rv" aria-hidden="true">
   <div class="dv desk"><div class="scr">{DEV['desk']}</div><i class="neck"></i><i class="stand"></i></div>
   <div class="dv lap"><div class="scr">{DEV['lap']}</div><i class="kb"></i></div>
   <div class="dv tab"><div class="scr">{DEV['tab']}</div></div>
   <div class="dv pho"><div class="scr">{DEV['pho']}</div></div>
   <span class="tap t1"><svg viewBox="0 0 24 24"><path fill="#fff" stroke="#14141a" stroke-width="1.3" stroke-linejoin="round" d="M9 2.5c.9 0 1.6.7 1.6 1.6v6.2l.6-.1c.9-.1 1.6.4 1.8 1.2l.1.2.4-.1c.9-.1 1.6.4 1.8 1.2l.1.3h.3c.9 0 1.6.7 1.7 1.6v3.3c0 3-2.4 5.4-5.4 5.4h-1.4c-1.8 0-3.4-.9-4.4-2.3l-3-4.3c-.5-.7-.3-1.7.4-2.2.7-.5 1.6-.4 2.2.2l1.6 1.7V4.1c0-.9.7-1.6 1.6-1.6z"/></svg><i></i></span><span class="tap t2"><svg viewBox="0 0 24 24"><path fill="#fff" stroke="#14141a" stroke-width="1.3" stroke-linejoin="round" d="M9 2.5c.9 0 1.6.7 1.6 1.6v6.2l.6-.1c.9-.1 1.6.4 1.8 1.2l.1.2.4-.1c.9-.1 1.6.4 1.8 1.2l.1.3h.3c.9 0 1.6.7 1.7 1.6v3.3c0 3-2.4 5.4-5.4 5.4h-1.4c-1.8 0-3.4-.9-4.4-2.3l-3-4.3c-.5-.7-.3-1.7.4-2.2.7-.5 1.6-.4 2.2.2l1.6 1.7V4.1c0-.9.7-1.6 1.6-1.6z"/></svg><i></i></span><span class="tap t3"><svg viewBox="0 0 24 24"><path fill="#fff" stroke="#14141a" stroke-width="1.3" stroke-linejoin="round" d="M9 2.5c.9 0 1.6.7 1.6 1.6v6.2l.6-.1c.9-.1 1.6.4 1.8 1.2l.1.2.4-.1c.9-.1 1.6.4 1.8 1.2l.1.3h.3c.9 0 1.6.7 1.7 1.6v3.3c0 3-2.4 5.4-5.4 5.4h-1.4c-1.8 0-3.4-.9-4.4-2.3l-3-4.3c-.5-.7-.3-1.7.4-2.2.7-.5 1.6-.4 2.2.2l1.6 1.7V4.1c0-.9.7-1.6 1.6-1.6z"/></svg><i></i></span><span class="tap t4"><svg viewBox="0 0 24 24"><path fill="#fff" stroke="#14141a" stroke-width="1.3" stroke-linejoin="round" d="M9 2.5c.9 0 1.6.7 1.6 1.6v6.2l.6-.1c.9-.1 1.6.4 1.8 1.2l.1.2.4-.1c.9-.1 1.6.4 1.8 1.2l.1.3h.3c.9 0 1.6.7 1.7 1.6v3.3c0 3-2.4 5.4-5.4 5.4h-1.4c-1.8 0-3.4-.9-4.4-2.3l-3-4.3c-.5-.7-.3-1.7.4-2.2.7-.5 1.6-.4 2.2.2l1.6 1.7V4.1c0-.9.7-1.6 1.6-1.6z"/></svg><i></i></span>
  </div>
  <p class="lead center rv" style="margin-top:56px">La plataforma reúne herramientas para que tu jornada sea más organizada:</p>
  <ul class="feats">{feats_html}</ul>
  <p class="mut center rv" style="max-width:62ch;margin:0 auto">No necesitas intentar cambiar todo al mismo tiempo. <b>Puedes empezar identificando una prioridad y avanzar de forma gradual y consciente.</b></p>
 </div>
</section>

<!-- PUENTE · LAS TRES FUERZAS -->
<section data-n="10 · Las 3 fuerzas" class="blk tone-b sec" id="fuerzas" aria-labelledby="hfz">
 <div class="wrap">
  <div class="center">
   <p class="kick rv">Lo que la jornada entrena en ti</p>
   <h2 id="hfz" class="rv">Foco, ejecución y disciplina.<span class="it">Las tres fuerzas que sostienen el cambio.</span></h2>
  </div>
  <div class="trio3">
   <article class="fz rv"><figure>{AGUILA}</figure><span>El águila</span><h3>Foco</h3><p>Ves tu vida desde arriba y eliges una prioridad, no diez. El diagnóstico te muestra por dónde empezar.</p></article>
   <article class="fz rv"><figure>{LEON}</figure><span>El león</span><h3>Ejecución</h3><p>Pasas del conocimiento a la acción, con misiones, ejercicios y checklists en cada etapa de la jornada.</p></article>
   <article class="fz rv"><figure>{LOBO}</figure><span>El lobo</span><h3>Disciplina</h3><p>Vuelves cada día, también cuando no hay ganas. Una misión corta por día, y la plataforma guarda tu progreso.</p></article>
  </div>
 </div>
</section>

<!-- BLOQUE 9 · PARA QUIÉN -->
<section data-n="11 · Para quién" class="blk tone-a sec" aria-labelledby="h9b">
 <div class="wrap">
  <p class="kick rv">Para quién fue creado</p>
  <h2 id="h9b" class="rv">Para quien desea construir<span class="it">una vida con más dirección.</span></h2>
  <ul class="forwho">
   {''.join(f'<li class="rv">{check}<span>{x}</span></li>' for x in ['Para quien siente que necesita organizar mejor sus prioridades.','Para quien busca desarrollar distintas áreas de su propia vida.','Para quien quiere convertir conocimiento en acciones prácticas.','Para quien desea crecer profesionalmente sin dejar de lado la salud y las relaciones.','Para quien valora el desarrollo personal, la fe cristiana y una vida orientada por principios.','Para quien entiende que prosperar también significa construir buenos fundamentos para el futuro.'])}
  </ul>
  <p class="note rv"><b>No es una fórmula de enriquecimiento instantáneo, ni una promesa de transformación sin esfuerzo.</b> Es una estructura de conocimiento y aplicación para quien está dispuesto a participar activamente de su propia evolución.</p>
 </div>
</section>

<!-- BLOQUE 10 · OBJECIONES -->
<section data-n="12 · Tus dudas" class="blk tone-b sec" aria-labelledby="h10b">
 <div class="narrow">
  <p class="kick rv">Objeciones</p>
  <h2 id="h10b" class="rv">Tal vez estés pensando<span class="it">algunas cosas en este momento.</span></h2>
  <div class="obj rv">{obj_html}</div>
 </div>
</section>

<!-- BLOQUE 11 · LA OFERTA -->
<section data-n="13 · La oferta" class="blk tone-a sec" id="oferta" aria-labelledby="h11b">
 <div class="wrap">
  <div class="center">
   <p class="kick rv">La oferta</p>
   <h2 id="h11b" class="rv">Imagina tener los cinco fundamentos<span class="it">organizados en una única experiencia.</span></h2>
   <p class="lead rv" style="margin:22px auto 0;max-width:62ch">No estás adquiriendo contenidos aislados. Estás accediendo a un ecosistema que integra diferentes dimensiones de desarrollo, conocimientos y herramientas de aplicación en un solo entorno digital.</p>
  </div>
  <div class="offer-grid">
   <div class="offer-col main rv spot"><p class="k">01 · Núcleo</p><h3>Cinco dimensiones centrales</h3><ul>{lst(['Salud física y mental','Desarrollo personal y espiritualidad','Relaciones: capital social','Carrera y emprendimiento','Finanzas: la palanca de la libertad'])}</ul></div>
   <div class="offer-col rv spot"><p class="k">02 · Complementos</p><h3>Cuatro recursos complementarios</h3><ul>{lst(['Gestión del tiempo','Inteligencia emocional','Comunicación','El Mapa — 21 oportunidades'])}</ul></div>
   <div class="offer-col rv spot"><p class="k">03 · Plataforma</p><h3>Herramientas del ecosistema</h3><ul>{lst(['Diagnóstico de las cinco dimensiones','Biblioteca integrada de contenidos','Cronograma de aplicación: 90 misiones','Ejercicios y checklists','Audio de los contenidos','Anotaciones','Panel y seguimiento del progreso'])}</ul></div>
  </div>
  <p class="allin rv">Todo reunido en una única jornada de desarrollo.</p>
 </div>
</section>

<!-- BLOQUE 12 · INVERSIÓN -->
<section data-n="14 · Inversión" class="blk tone-b sec" id="inversion" aria-labelledby="h12b">
 <div class="wrap center">
  <p class="kick rv">Inversión</p>
  <h2 id="h12b" class="rv">El próximo paso<span class="it">empieza con una decisión.</span></h2>
  <p class="lead decide rv">Puedes seguir intentando organizar cada área de tu vida por separado, o empezar a construir una visión más amplia de lo que merece tu atención.</p>
  <div class="price-wrap rv">
   <div class="price">
    <p class="pname">Los 5 Pilares de la Prosperidad</p>
    <p class="by" style="margin-top:8px">Ecosistema digital de desarrollo integral</p>
    <p class="by">Por apenas</p>
    <p class="amount"><span class="cur" data-cur>US$</span><span class="num" data-num id="pnum">19,90</span></p>
    <p class="cond">Pago único · sin mensualidad · <span data-perday>unos 22 centavos de dólar</span> por día de jornada</p>
    <a class="cta" data-co href="#inversion">Quiero acceder a Los 5 Pilares <svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
    <ul class="price-info">{lst(['Pago único y seguro en Hotmart.','Acceso inmediato: el enlace llega a tu correo al confirmarse el pago.','Precio en dólares: Hotmart lo convierte a tu moneda.','Funciona en el celular, la tableta o la computadora, en español y portugués.'])}</ul>
   </div>
  </div>
 </div>
</section>

<!-- BLOQUE 13 · GARANTÍA -->
<section data-n="15 · Garantía" class="blk tone-a sec" id="garantia" aria-labelledby="h13b">
 <div class="wrap">
  <div class="guar rv">
   <div class="seal" aria-hidden="true">
    <svg viewBox="0 0 200 200"><defs><path id="sp" d="M100 100m-84 0a84 84 0 1 1 168 0a84 84 0 1 1-168 0"/></defs><text><textPath href="#sp" textLength="520" lengthAdjust="spacing"><tspan data-gd>7</tspan> días de garantía · 100% de vuelta · sin preguntas ·</textPath></text></svg>
    <div class="core"><div><b data-gd>7</b><small>días</small></div></div>
   </div>
   <div>
    <p class="kick">Garantía y seguridad</p>
    <h2 id="h13b">Una decisión consciente<span class="it">necesita condiciones claras.</span></h2>
    <p>Tienes <b><span data-gd>7</span> días de garantía</b>. Entra, haz el diagnóstico y conoce la plataforma por dentro. Si dentro de ese plazo sientes que no es para ti, pides el reembolso directamente en Hotmart y recibes el 100% de lo que pagaste, sin preguntas.</p>
   </div>
  </div>
 </div>
</section>

<!-- BLOQUE 14 · CIERRE -->
<section data-n="16 · Tu decisión" class="blk tone-x close" aria-labelledby="h14b">
 <div class="embers" aria-hidden="true">{EMBERS}</div>
 <div class="fx" aria-hidden="true"><i class="fx-rays"></i><i class="fx-halo"></i><i class="fx-ring r1"></i><i class="fx-ring r2"></i>{TRIO}</div>
 <div class="narrow close-in">
  <h2 id="h14b" class="rv">Dentro de algunos años,<span class="it">¿qué te gustaría reconocer en la vida que estás construyendo hoy?</span></h2>
  <div class="not rv"><p>No solo tus logros profesionales.</p><p>No solo el dinero que lograste acumular.</p></div>
  <p class="but rv">También la salud que cuidaste, las relaciones que cultivaste, el conocimiento que aplicaste, la fe que fortaleciste y las decisiones que tomaste.</p>
  <p class="quote rv">El futuro no se construye solo con grandes conquistas. También es el resultado de los fundamentos que eliges desarrollar cada día.</p>
  <p class="lead rv" style="margin-top:26px;color:var(--text)">Empieza a mirar tu vida por completo.</p>
  <a class="cta rv" data-co href="#inversion">Quiero empezar mi jornada en los 5 pilares <svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
  <p class="quote rv" style="margin-top:44px;font-size:clamp(22px,2vw,28px)">Una vida bien construida comienza por los fundamentos correctos.</p>
  <p class="sign">Los 5 Pilares de la Prosperidad · AMR Growth</p>
 </div>
</section>
</main>

<footer class="foot">
 <div class="wrap">
  {LOGO_F}
  <p><b style="color:var(--mut)">Los 5 Pilares de la Prosperidad.</b> Una vida bien construida comienza por los fundamentos correctos.</p>
  <p>Contenido educativo. Los materiales sobre salud, finanzas y emprendimiento no sustituyen el acompañamiento profesional individualizado. Los resultados dependen de la aplicación y de las circunstancias de cada persona. Las estimaciones y ejemplos financieros presentados en los materiales no constituyen promesa de retorno.</p>
  <p>La compra se procesa en Hotmart. Este sitio no forma parte de Facebook, Instagram ni Google, ni está respaldado por ellos.</p>
 </div>
</footer>

<div class="dock" id="dock" aria-hidden="true"><div><b>Los 5 Pilares</b><span data-price>US$ 19,90</span></div><a class="cta" data-co href="#inversion" tabindex="-1">Empezar</a></div>

<script type="application/octet-stream" id="brj-data">{VIDEO}</script>
<script>APPJS</script>
</body>
</html>
'''

APPJS = r'''(function(){'use strict';window.__ok=1;
var C=CFG,$=function(s,r){return[].slice.call((r||document).querySelectorAll(s))},$1=function(s){return document.querySelector(s)};
var RM=false;try{RM=matchMedia('(prefers-reduced-motion: reduce)').matches}catch(e){}
function parse(p){var a=String(p).replace('.',',').split(',');var i=a[0]||'0',c=((a[1]||'')+'00').slice(0,2);return{txt:i+','+c,num:parseFloat(i+'.'+c)||0}}
var cur=C.moeda,P=parse(C.preco);
$('[data-price]').forEach(function(e){e.textContent=cur+' '+P.txt});$('[data-cur]').forEach(function(e){e.textContent=cur});$('[data-num]').forEach(function(e){e.textContent=P.txt});
$('[data-perday]').forEach(function(e){var d=P.num/90;e.textContent=d<1?'unos '+Math.round(d*100)+' centavos de dólar':cur+' '+d.toFixed(2).replace('.',',')});
$('[data-gd]').forEach(function(e){e.textContent=C.garantiaDias});
/* píxel */
var CUR=/US/.test(cur)?'USD':cur,PROD='Los 5 Pilares de la Prosperidad';
if(/^\d{8,20}$/.test(C.pixel)){!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src='https://connect.facebook.net/en_US/fbevents.js';s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script');fbq('init',C.pixel);fbq('track','PageView')}
var track=function(ev,d,c){try{if(window.fbq)fbq(c?'trackCustom':'track',ev,d||{})}catch(e){}};
track('ViewContent',{content_name:PROD,content_type:'product',value:P.num,currency:CUR});
/* checkout com UTM */
function ck(extra){try{var u=new URL(C.checkout),q=new URLSearchParams(location.search);['fbclid','utm_source','utm_medium','utm_campaign','utm_content','utm_term','src','sck'].forEach(function(k){if(q.get(k))u.searchParams.set(k,q.get(k))});if(!u.searchParams.get('src')&&q.get('utm_source'))u.searchParams.set('src',q.get('utm_source').slice(0,60));var s=[q.get('utm_campaign'),q.get('utm_content'),'v34',extra].filter(Boolean).join('|');if(!u.searchParams.get('sck')&&s)u.searchParams.set('sck',s.slice(0,120));return u.toString()}catch(e){return C.checkout}}
var CK=ck();$('[data-co]').forEach(function(a){a.href=CK;a.rel='noopener'});
document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('[data-co]');if(a)track('InitiateCheckout',{content_name:PROD,value:P.num,currency:CUR})},true);
/* entrada */
var io='IntersectionObserver' in window?new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{rootMargin:'0px 0px -8% 0px',threshold:.06}):null;
$('.rv').forEach(function(e,i){if(e.closest('.struct,.why,.feats,.forwho,.offer-grid,.bonos'))e.style.transitionDelay=((i%3)*.09)+'s';if(io&&!RM)io.observe(e);else e.classList.add('in')});

/* v33 · mão nos recursos */
(function(){var box=$1('.eco'),bt=$('.rtabs button'),im=$('#rview img'),hand=$1('#rhand'),scr=$1('#rview'),cur=0,t=[],run=false,user=false;if(!box||!bt.length)return;
var P=[[9,51],[31,24]];
function clr(){t.forEach(clearTimeout);t=[]}
function pos(x,y){var a=box.getBoundingClientRect();hand.style.left=(x-a.left)+'px';hand.style.top=(y-a.top)+'px'}
function click(){hand.classList.remove('click');void hand.offsetWidth;hand.classList.add('click')}
function show(i){cur=(i+bt.length)%bt.length;bt.forEach(function(b,k){b.setAttribute('aria-selected',k===cur)});im.forEach(function(e,k){e.classList.toggle('on',k===cur)})}
function at(p){var v=scr.getBoundingClientRect();pos(v.left+v.width*p[0]/100,v.top+v.height*p[1]/100)}
function step(i){clr();i=(i+bt.length)%bt.length;var r=bt[i].getBoundingClientRect();hand.classList.add('on');pos(r.left+r.width*.5,r.top+r.height*.6);
 t.push(setTimeout(function(){click();show(i)},950));
 t.push(setTimeout(function(){at(P[0])},2100));t.push(setTimeout(click,3100));
 t.push(setTimeout(function(){at(P[1])},3900));t.push(setTimeout(click,4900));
 t.push(setTimeout(function(){if(!user)step(i+1)},7000))}
bt.forEach(function(b,k){b.addEventListener('click',function(){user=true;clr();hand.classList.remove('on');show(k)})});
if('IntersectionObserver' in window){new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting&&!run&&!user){run=true;step(cur)}else if(!e.isIntersecting&&run){run=false;clr();hand.classList.remove('on')}})},{threshold:.35}).observe(box)}})();
/* plataforma: mockup com pontos interativos e mãozinha */
(function(){var app=$1('.app'),bt=$('.stepper button'),hs=$('.mock .hs'),tp=$('.mock .tip'),hand=$1('#phand'),cur=0,t=[],run=false,user=false;if(!app||!bt.length)return;
function clr(){t.forEach(clearTimeout);t=[]}
function pos(el){var a=app.getBoundingClientRect(),r=el.getBoundingClientRect();hand.style.left=(r.left+r.width/2-a.left)+'px';hand.style.top=(r.top+r.height/2-a.top)+'px'}
function click(){hand.classList.remove('click');void hand.offsetWidth;hand.classList.add('click')}
function show(i){cur=(i+bt.length)%bt.length;bt.forEach(function(b,k){b.setAttribute('aria-selected',k===cur)});hs.forEach(function(e,k){e.classList.toggle('on',k===cur)});tp.forEach(function(e,k){e.classList.toggle('on',k===cur)})}
function step(i){clr();i=(i+bt.length)%bt.length;hand.classList.add('on');pos(hs[i]);
 t.push(setTimeout(function(){click();show(i)},950));
 t.push(setTimeout(function(){if(!user)step(i+1)},4600))}
function pick(k){user=true;clr();hand.classList.remove('on');show(k)}
bt.forEach(function(b,k){b.addEventListener('click',function(){pick(k)})});
hs.forEach(function(b,k){b.addEventListener('click',function(){pick(k)})});
show(0);
if('IntersectionObserver' in window){new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting&&!run&&!user){run=true;step(cur)}else if(!e.isIntersecting&&run){run=false;clr();hand.classList.remove('on')}})},{threshold:.35}).observe(app)}})();
/* diagnóstico curto */
(function(){var box=$1('#quiz');if(!box)return;var qi=0,sc=[];
var Q=[['Salud','¿Cómo está tu energía en el día a día?',['Me despierto cansado y rindo poco','Varía: hay días buenos y días malos','Tengo energía y una rutina de cuidado']],
['Espiritualidad','¿Sabes hacia dónde vas?',['Corro mucho sin saber hacia dónde','Tengo pistas, pero no una dirección','Tengo sentido y dirección claros']],
['Relaciones','¿Cómo están las personas que amas?',['Estoy distante y sin tiempo para ellas','Estoy presente, pero podría cuidarlas mejor','Cercano y con conversaciones de calidad']],
['Carrera','¿Cómo está tu rumbo profesional?',['Ocupado, pero sin avanzar','Tengo ideas, pero ningún plan','Tengo dirección y metas claras']],
['Finanzas','¿Cómo está tu dinero?',['Se me escapa y una emergencia me quebraría','Pago las cuentas, pero sin ahorro ni plan','Ordenado, con ahorro y metas']]];
var N={Salud:'Salud física y mental',Espiritualidad:'Desarrollo personal y espiritualidad',Relaciones:'Relaciones',Carrera:'Carrera y emprendimiento',Finanzas:'Finanzas'};
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function prog(n){return '<div class="q-prog" aria-hidden="true">'+Q.map(function(_,i){return '<i class="'+(i<n?'on':'')+'"></i>'}).join('')+'</div>'}
function ask(first){var q=Q[qi];box.innerHTML=prog(qi)+'<p class="q-n">Pregunta '+(qi+1)+' de 5 · '+q[0]+'</p><p class="q-t" id="q-t" tabindex="-1">'+esc(q[1])+'</p><div class="q-o" role="group" aria-labelledby="q-t">'+q[2].map(function(o,k){return '<button type="button" data-k="'+(k+1)+'"><b>'+'ABC'.charAt(k)+'</b><span>'+esc(o)+'</span></button>'}).join('')+'</div>';
$('button',box).forEach(function(b){b.onclick=function(){if(!sc.length)track('QuizStart',{},true);sc.push(+b.dataset.k);qi++;qi<5?ask():res()}});if(!first)$1('#q-t').focus({preventScroll:true})}
function res(){var m=0;sc.forEach(function(s,i){if(s<sc[m])m=i});var firm=sc[m]===3,name=Q[m][0];
box.innerHTML='<div class="res">'+prog(5)+'<p class="q-n">Tu punto de partida</p><h4 id="res-h" tabindex="-1">'+(firm?'Tus pilares están firmes':'Empieza por: '+N[name])+'</h4><p>'+(firm?'Buen punto de partida. El ecosistema te ayuda a sostener y fortalecer cada dimensión.':'Es el área que hoy merece más atención. Dentro del ecosistema, el diagnóstico completo y los contenidos de esta dimensión en la biblioteca te muestran cómo empezar.')+'</p>'+
'<div class="bars" role="img" aria-label="'+Q.map(function(q,i){return q[0]+' '+sc[i]+' de 3'}).join(', ')+'">'+Q.map(function(q,i){return '<div class="bar2'+(i===m&&!firm?' low':'')+'"><span>'+q[0]+'</span><i><b data-w="'+Math.round(sc[i]/3*100)+'%"></b></i><em>'+sc[i]+'/3</em></div>'}).join('')+'</div>'+
'<a class="cta" style="width:100%" data-co href="'+esc(ck('quiz-'+name.toLowerCase()))+'" rel="noopener">Quiero acceder a Los 5 Pilares</a><button type="button" class="redo">Repetir la prueba</button></div>';
requestAnimationFrame(function(){requestAnimationFrame(function(){$('.bar2 b',box).forEach(function(b){b.style.setProperty('--w',b.dataset.w)})})});
box.querySelector('.redo').onclick=function(){qi=0;sc=[];ask()};$1('#res-h').focus({preventScroll:true});track('Lead',{content_name:'Diagnostico 5 Pilares',value:0,currency:CUR})}
ask(true)})();
/* objeções: uma aberta por vez */
$('.obj details').forEach(function(d){d.addEventListener('toggle',function(){if(d.open)$('.obj details').forEach(function(o){if(o!==d)o.open=false})})});
/* luz que segue o cursor */
try{if(matchMedia('(hover:hover)').matches)$('.spot').forEach(function(e){e.addEventListener('pointermove',function(v){var r=e.getBoundingClientRect();e.style.setProperty('--x',(v.clientX-r.left)+'px');e.style.setProperty('--y',(v.clientY-r.top)+'px')})})}catch(e){}
/* barra fixa no celular */
(function(){var d=$1('#dock'),h=$1('.hero'),pr=$1('#inversion'),cl=$1('.close'),tk=0;function u(){tk=0;var a=h.getBoundingClientRect().bottom<0,b=pr.getBoundingClientRect(),c=cl.getBoundingClientRect(),show=a&&!(b.top<innerHeight&&b.bottom>0)&&c.top>innerHeight*.5;d.classList.toggle('on',show);d.setAttribute('aria-hidden',!show);d.querySelector('a').tabIndex=show?0:-1}
addEventListener('scroll',function(){if(!tk){tk=1;requestAnimationFrame(u)}},{passive:true});u()})();
/* vídeo da bússola */
(function(){var v=$1('#brj'),d=$1('#brj-data');if(!v||!d||!window.Blob)return;v.muted=true;function load(){try{var b=atob(d.textContent.trim()),n=b.length,u=new Uint8Array(n);while(n--)u[n]=b.charCodeAt(n);v.src=URL.createObjectURL(new Blob([u],{type:'video/mp4'}));var p=v.play();if(p&&p.catch)p.catch(function(){})}catch(e){}}
if('IntersectionObserver' in window){var o=new IntersectionObserver(function(es){if(es[0].isIntersecting){o.disconnect();load()}},{rootMargin:'400px'});o.observe(v)}else load()})();

/* ===== v27 · efeitos ===== */
(function(){if(RM)return;var fine=false;try{fine=matchMedia('(hover:hover) and (pointer:fine)').matches}catch(e){}
/* barra de progresso + paralaxe do topo */
var pr=$1('#prog'),hb=$1('.hero-bg img'),tk=0;function sc(){tk=0;var h=document.documentElement.scrollHeight-innerHeight;pr.style.transform='scaleX('+(h>0?Math.min(1,scrollY/h):0)+')';if(hb&&scrollY<innerHeight*1.2)hb.style.transform='translateY('+(scrollY*.25)+'px) scale(1.06)'}
addEventListener('scroll',function(){if(!tk){tk=1;requestAnimationFrame(sc)}},{passive:true});sc();
/* título palavra por palavra */
var h=$1('#h1');if(h){var main=h.firstChild;if(main&&main.nodeType===3){var w=main.textContent.trim().split(/\s+/),fr=document.createDocumentFragment();w.forEach(function(x,i){var sp=document.createElement('span');sp.className='wd';sp.style.setProperty('--i',i);sp.textContent=x;fr.appendChild(sp);fr.appendChild(document.createTextNode(' '))});h.replaceChild(fr,main);h.setAttribute('aria-label',w.join(' ')+' '+(h.querySelector('.it')||{textContent:''}).textContent)}requestAnimationFrame(function(){requestAnimationFrame(function(){h.classList.add('go')})})}
/* contadores */
function count(el,to,dec,dur){var t0=performance.now();(function st(t){var k=Math.min(1,(t-t0)/dur),v=1-Math.pow(1-k,3),n=to*v;el.textContent=dec?n.toFixed(2).replace('.',','):Math.round(n);if(k<1)requestAnimationFrame(st);else el.textContent=dec?to.toFixed(2).replace('.',','):to})(t0)}
var cio=new IntersectionObserver(function(es){es.forEach(function(e){if(!e.isIntersecting)return;cio.unobserve(e.target);var el=e.target;if(el.id==='pnum')count(el,P.num,true,1600);else count(el,+el.dataset.count,false,1400)})},{threshold:.6});
$('[data-count]').forEach(function(e){cio.observe(e)});var pn=$1('#pnum');if(pn)cio.observe(pn);
if(!fine)return;
/* luz que segue o cursor */
var g=$1('#gcur'),gx=0,gy=0,cx=0,cy=0,on=false;addEventListener('pointermove',function(e){gx=e.clientX;gy=e.clientY;if(!on){on=true;g.classList.add('on');loop()}},{passive:true});
function loop(){cx+=(gx-cx)*.12;cy+=(gy-cy)*.12;g.style.transform='translate('+cx+'px,'+cy+'px)';requestAnimationFrame(loop)}
/* tela do sistema em 3D */
$('.showcase').forEach(function(sh){var gl=document.createElement('i');gl.className='glare';sh.appendChild(gl);
sh.addEventListener('pointermove',function(e){if(!sh.classList.contains('in'))return;var r=sh.getBoundingClientRect(),x=(e.clientX-r.left)/r.width,y=(e.clientY-r.top)/r.height;sh.style.transform='perspective(1800px) rotateX('+((.5-y)*6).toFixed(2)+'deg) rotateY('+((x-.5)*8).toFixed(2)+'deg)';sh.style.setProperty('--gx',(x*100)+'%');sh.style.setProperty('--gy',(y*100)+'%')});
sh.addEventListener('pointerleave',function(){sh.style.transform=''})});
/* botões magnéticos */
$('.cta').forEach(function(b){b.addEventListener('pointermove',function(e){var r=b.getBoundingClientRect();b.style.setProperty('--mx',((e.clientX-r.left-r.width/2)*.15).toFixed(1)+'px');b.style.setProperty('--my',((e.clientY-r.top-r.height/2)*.25).toFixed(1)+'px')});b.addEventListener('pointerleave',function(){b.style.setProperty('--mx','0px');b.style.setProperty('--my','0px')})});
})();
})();'''

import json
js = APPJS.replace('CFG', json.dumps(CFG, ensure_ascii=False))
html = HTML.replace('APPJS', js)
scripts = [b for a, b in re.findall(r'<script(?![^>]*\bsrc=)([^>]*)>(.*?)</script>', html, flags=re.S) if 'octet-stream' not in a]
hashes = ' '.join("'sha256-" + base64.b64encode(hashlib.sha256(x.encode()).digest()).decode() + "'" for x in scripts)
html = html.replace('SCRIPTHASHES', hashes)
out = HERE / 'los-5-pilares-v34-es.html'
out.write_text(html)
print(out, len(html) // 1024, 'KB', len(scripts), 'scripts')
