"""
Construye el sitio de Viple Consultores en la carpeta _site/.

- Envuelve cada página de src/pages/ con la plantilla común src/layout.html
  (encabezado, menú y pie de página).
- Genera las secciones «Cómo mejorar el trabajo legal» (content/notas), «Te ayudamos
  con tus dudas» (content/dudas, temas en content/temas-dudas) y
  «Novedades» (content/novedades) a partir de los artículos guardados
  desde el panel de administración (/admin).

Netlify ejecuta este archivo automáticamente en cada publicación.
Para probarlo en tu computadora:  python build.py
"""
import html
import hashlib
import json
import math
import re
import shutil
from pathlib import Path
from urllib.parse import quote

import markdown

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "_site"
SITE_URL = "https://vipleconsultores.com"
DEFAULT_AUTHOR = "Gabriel Villavicencio Bedoya"

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

# Sección editorial «Ideas y análisis» (se guarda en content/notas)
IDEAS = {
    "name": "notas",
    "label": "¿Tu equipo odia a Legal?",
    "h1": "Cómo organizar el trabajo legal para que no se convierta en un cuello de botella",
    "intro": ("Consejos prácticos para que tu equipo sepa qué contratos puede cerrar con condiciones ya aprobadas, "
              "cuándo conviene involucrar a un abogado en un proyecto y cómo aprovechar lo que ya negoció con un "
              "cliente para llegar mejor preparado al siguiente acuerdo"),
    "empty": "Muy pronto publicaremos los primeros artículos.",
    "nav": "notas",
    "featured_label": "Artículo destacado",
    "more": "Leer artículo →",
    "related": "Otros artículos",
}

# Sección «Te ayudamos con tus dudas» (notas en content/dudas, temas en content/temas-dudas)
DUDAS = {
    "name": "dudas",
    "label": "Te ayudamos con tus dudas",
    "intro": "Encuentra respuestas a preguntas legales sobre situaciones de tu vida diaria o de tu negocio.",
    "empty": "Muy pronto publicaremos las primeras respuestas.",
}
PUBLICOS = {"personas": "Para personas", "negocios": "Para negocios", "ambos": "Para personas y negocios"}

# Sección «Novedades» (sin cambios de diseño por ahora)
NOVEDADES = {
    "name": "novedades",
    "nav": "novedades",
    "eyebrow": "Novedades",
    "h1": "Novedades normativas y asuntos de interés",
    "intro": "Nuevas normas, cambios regulatorios y temas de actualidad relevantes para tu empresa.",
    "item_label": "Novedad",
    "empty": "Todavía no hay novedades publicadas. Vuelve pronto.",
}

LAYOUT = (SRC / "layout.html").read_text(encoding="utf-8")
# Versión de CSS/JS en la URL: cada cambio obliga al navegador a descargar la hoja nueva (evita ver estilos viejos)
for _f in ("css/site.css", "js/site.js"):
    _v = hashlib.md5((ROOT / "assets" / _f).read_bytes()).hexdigest()[:8]
    LAYOUT = LAYOUT.replace(f"/assets/{_f}", f"/assets/{_f}?v={_v}")
SITEMAP = []


def esc(s):
    return html.escape(str(s or ""), quote=True)


def fecha_larga(iso):
    try:
        y, m, d = (int(x) for x in str(iso)[:10].split("-"))
        return f"{d} de {MESES[m - 1]} de {y}"
    except Exception:
        return ""


def minutos_lectura(texto):
    palabras = len(re.findall(r"\w+", texto or ""))
    return max(1, math.ceil(palabras / 200))


def brand(logo=None):
    return ('<a class="brand" href="/" aria-label="Viple Consultores – Inicio">'
            '<img src="/assets/img/logo-viple-horizontal.png" alt="Viple Consultores · Legal &amp; Compliance" '
            'width="349" height="212"></a>')


# ---------- Íconos (trazo simple, heredan el color del texto) ----------
# En las páginas se usan como {{icon:nombre}}

ICONS = {
    "building": '<path d="M4 21V5.5l8-3 8 3V21"/><path d="M2 21h20"/><path d="M8.5 9h1.5M14 9h1.5M8.5 13h1.5M14 13h1.5"/><path d="M10 21v-4h4v4"/>',
    "doc-pen": '<path d="M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h5.5"/><path d="M14 3l5 5h-5z"/><path d="M8 11h6M8 15h3.5"/><path d="M19 13l2 2-6.5 6.5H12.5v-2z"/>',
    "doc-search": '<path d="M13 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h5"/><path d="M13 3l5 5h-5z"/><path d="M8 11h5M8 15h2.5"/><circle cx="16.5" cy="16.5" r="3"/><path d="M18.7 18.7 21 21"/>',
    "doc-check": '<path d="M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8z"/><path d="M14 3v5h5"/><path d="M8.5 14.5l2.5 2.5 4.5-5"/>',
    "shield-lock": '<path d="M12 2.5l8 3v5.8c0 4.9-3.4 8.8-8 10.7-4.6-1.9-8-5.8-8-10.7V5.5z"/><rect x="9" y="11" width="6" height="5" rx="1"/><path d="M10.2 11V9.6a1.8 1.8 0 0 1 3.6 0V11"/>',
    "shield-check": '<path d="M12 2.5l8 3v5.8c0 4.9-3.4 8.8-8 10.7-4.6-1.9-8-5.8-8-10.7V5.5z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "megaphone": '<path d="M3 10v4a1 1 0 0 0 1 1h3l9 5V4L7 9H4a1 1 0 0 0-1 1z"/><path d="M7 15l1.5 5H11l-1.5-5"/><path d="M19 9.5a3 3 0 0 1 0 5"/>',
    "tools": '<rect x="3" y="8" width="18" height="12" rx="1.5"/><path d="M9 8V5.5A1.5 1.5 0 0 1 10.5 4h3A1.5 1.5 0 0 1 15 5.5V8"/><path d="M3 13h18"/><path d="M10 12v3h4v-3"/>',
    "trend": '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 6-6"/><path d="M15 8h5v5"/>',
    "grid": '<rect x="3.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.5"/>',
    "book": '<path d="M12 6.5C10 5 7 4.5 3 5v14c4-.5 7 0 9 1.5 2-1.5 5-2 9-1.5V5c-4-.5-7 0-9 1.5z"/><path d="M12 6.5v14"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6"/><circle cx="17" cy="9" r="2.5"/><path d="M17.5 14c2.4.2 4 2 4 4.5"/>',
    "refresh": '<path d="M20 11a8 8 0 0 0-14.5-4.5L3 9"/><path d="M3 4v5h5"/><path d="M4 13a8 8 0 0 0 14.5 4.5L21 15"/><path d="M21 20v-5h-5"/>',
    "layers": '<path d="M12 3l9 4.5-9 4.5-9-4.5z"/><path d="M3 12l9 4.5 9-4.5"/><path d="M3 16.5 12 21l9-4.5"/>',
    "database": '<ellipse cx="12" cy="5.5" rx="7.5" ry="2.5"/><path d="M4.5 5.5v13c0 1.4 3.4 2.5 7.5 2.5s7.5-1.1 7.5-2.5v-13"/><path d="M4.5 12c0 1.4 3.4 2.5 7.5 2.5s7.5-1.1 7.5-2.5"/>',
    "clipboard": '<rect x="5" y="4" width="14" height="17" rx="1.5"/><path d="M9 3h6v3H9z"/><path d="M8.5 10.5h7M8.5 14h7M8.5 17.5h4"/>',
    "bell": '<path d="M6 16v-5a6 6 0 0 1 12 0v5l2 2H4z"/><path d="M10 20.5a2 2 0 0 0 4 0"/>',
    "user-shield": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.6 2.9-6 6.5-6 1.3 0 2.5.3 3.5.9"/><path d="M18 13l3.5 1.3v2.5c0 2.2-1.5 3.9-3.5 4.7-2-.8-3.5-2.5-3.5-4.7v-2.5z"/>',
    "tag": '<path d="M3 12V4a1 1 0 0 1 1-1h8l9 9-9 9z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
    "headset": '<path d="M4 14v-2a8 8 0 0 1 16 0v2"/><rect x="3" y="13" width="4" height="6" rx="1.5"/><rect x="17" y="13" width="4" height="6" rx="1.5"/><path d="M19 19v.5a2.5 2.5 0 0 1-2.5 2.5H13"/>',
    "scale": '<path d="M12 3v18M7 21h10M5 7h14"/><path d="M5 7l-3 7a3 3 0 0 0 6 0z"/><path d="M19 7l-3 7a3 3 0 0 0 6 0z"/>',
    "checklist": '<path d="M10 6h11M10 12h11M10 18h11"/><path d="M3 6l1.5 1.5L7 5M3 12l1.5 1.5L7 11M3 18l1.5 1.5L7 17"/>',
    "approve": '<rect x="3" y="4" width="18" height="16" rx="1.5"/><path d="M3 9h18"/><path d="M8.5 14.5l2.5 2.5 4.5-5"/>',
    "bulb": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2v.1h5v-.1c0-.8.4-1.5 1-2A6 6 0 0 0 12 3z"/>',
    "alert": '<path d="M12 3.5 21.5 20h-19z"/><path d="M12 10v4.5"/><path d="M12 17.5h.01"/>',
    "chevron": '<path d="M9 5l7 7-7 7"/>',
    "arrow-left": '<path d="M19 12H5M11 6l-6 6 6 6"/>',
    "arrow-right": '<path d="M5 12h14M13 6l6 6-6 6"/>',
}

# Ícono de cada servicio (por su dirección); si falta, se usa el de documento
SVC_ICONS = {
    "estructura-empresarial": "building",
    "contratos": "doc-pen",
    "proteccion-de-datos": "shield-lock",
    "reclamos-y-denuncias": "megaphone",
    "herramientas-legales": "tools",
    "protegemos-tu-inversion": "trend",
}


def icon(name, cls="ico-svg"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">'
            f'{ICONS.get(name, ICONS["doc-check"])}</svg>')


# ---------- Servicios (fuente única: content/servicios.json) ----------

SERVICIOS = json.loads((ROOT / "content" / "servicios.json").read_text(encoding="utf-8"))["servicios"]


def svc_menu():
    return "\n".join(f'              <li><a href="/servicios/{s["slug"]}/">{esc(s.get("menu") or s["name"])}</a></li>'
                     for s in SERVICIOS)


def svc_panels(summary=False):
    cards = ""
    for s in SERVICIOS:
        resumen = f'<span class="svc-sum">{esc(s["summary"])}</span>' if summary else ""
        cards += f"""<a class="svc-card" href="/servicios/{s["slug"]}/">
        <span class="svc-ico">{icon(SVC_ICONS.get(s["slug"], "doc-check"))}</span>
        <span class="svc-txt"><span class="svc-name">{esc(s["name"])}</span>{resumen}</span>
        <span class="svc-chev">{icon("chevron")}</span>
      </a>"""
    return f'<div class="svc-cards{" with-sum" if summary else ""}">{cards}</div>'


# Enlaces de las preguntas: a la respuesta elegida en el panel (si existe) o a «¿Tienes preguntas?»
DUDAS_SLUGS = set()


def pregunta_url(p):
    slug = str(p.get("respuesta") or "").strip()
    return f"/dudas/{slug}/" if slug in DUDAS_SLUGS else "/dudas/"


def preguntas_de(s):
    return [p for p in (s.get("preguntas") or []) if isinstance(p, dict) and str(p.get("pregunta") or "").strip()]


def pregunta_items(s):
    return "".join(f'<li><a href="{pregunta_url(p)}"><span>{esc(p["pregunta"])}</span>{icon("arrow-right", "q-arrow")}</a></li>'
                   for p in preguntas_de(s))


def svc_preguntas(slug):
    s = next((x for x in SERVICIOS if x["slug"] == slug), None)
    if not s or not preguntas_de(s):
        return ""
    return f"""<div class="rel-q">
      <h2>Preguntas relacionadas</h2>
      <ul>{pregunta_items(s)}</ul>
    </div>"""


def svc_nav(slug):
    i = next((n for n, x in enumerate(SERVICIOS) if x["slug"] == slug), None)
    if i is None:
        return ""
    links = ""
    if i > 0:
        a = SERVICIOS[i - 1]
        links += f'<a class="prev" href="/servicios/{a["slug"]}/"><small>← Anterior</small>{esc(a["name"])}</a>'
    if i < len(SERVICIOS) - 1:
        b = SERVICIOS[i + 1]
        links += f'<a class="next" href="/servicios/{b["slug"]}/"><small>Siguiente →</small>{esc(b["name"])}</a>'
    return f'<div class="wrap"><nav class="svc-nav" aria-label="Otros servicios">{links}</nav></div>'


def preguntas_carrusel():
    con = [s for s in SERVICIOS if preguntas_de(s)]
    if not con:
        return ""
    n = len(con)
    slides = ""
    for i, s in enumerate(con, 1):
        slides += f"""<div class="faq-slide" role="group" aria-roledescription="diapositiva" aria-label="{i} de {n}: {esc(s["name"])}">
          <a class="faq-svc" href="/servicios/{s["slug"]}/">{icon(SVC_ICONS.get(s["slug"], "doc-check"))}<span>{esc(s["name"])}</span></a>
          <ul class="faq-q">{pregunta_items(s)}</ul>
        </div>"""
    dots = "".join(f'<button type="button" data-dot="{i}" aria-label="Ver preguntas de {esc(s["name"])}"></button>'
                   for i, s in enumerate(con))
    return f"""<section class="home-faq">
  <div class="wrap faq-grid">
    <div class="faq-head">
      <h2>¿Tienes preguntas?</h2>
      <p>Preguntas frecuentes sobre cada uno de nuestros servicios.</p>
      <a class="faq-all" href="/dudas/">Ver todas las preguntas <span aria-hidden="true">→</span></a>
    </div>
    <div class="faq-carousel" data-carousel>
      <div class="faq-track" tabindex="0" role="region" aria-roledescription="carrusel" aria-label="Preguntas por servicio">{slides}</div>
      <div class="faq-nav">
        <button type="button" class="faq-arrow" data-prev aria-label="Servicio anterior">{icon("arrow-left")}</button>
        <div class="faq-dots">{dots}</div>
        <button type="button" class="faq-arrow" data-next aria-label="Servicio siguiente">{icon("arrow-right")}</button>
      </div>
    </div>
  </div>
</section>"""


def fill_services(text):
    text = text.replace("{{svc_panels}}", svc_panels())
    text = text.replace("{{svc_panels_sum}}", svc_panels(summary=True))
    text = text.replace("{{preguntas_carrusel}}", preguntas_carrusel())
    for s in SERVICIOS:
        text = text.replace("{{svc:" + s["slug"] + "}}", esc(s["name"]))
        text = text.replace("{{svc_preguntas:" + s["slug"] + "}}", svc_preguntas(s["slug"]))
        text = text.replace("{{svc_nav:" + s["slug"] + "}}", svc_nav(s["slug"]))
    text = re.sub(r"\{\{icon:([a-z0-9-]+)\}\}", lambda m: icon(m.group(1)), text)
    return text


def render(url, content, title, description, nav="", logo="cuadrado",
           og_image="/assets/img/logo-cuadrado.png", og_type="website", head_extra=""):
    page = LAYOUT
    for key, val in {
        "{{title}}": esc(title),
        "{{description}}": esc(description),
        "{{url}}": url,
        "{{og_image}}": og_image,
        "{{og_type}}": og_type,
        "{{head_extra}}": head_extra,
        "{{brand}}": brand(logo),
        "{{svc_menu}}": svc_menu(),
        "{{content}}": content,
    }.items():
        page = page.replace(key, val)
    if nav:
        page = page.replace(f'data-nav="{nav}"', f'data-nav="{nav}" aria-current="page"')
    if url == "/":
        page = page.replace("<body>", '<body class="is-home">', 1)
    dest = OUT / url.strip("/") / "index.html" if url != "/" else OUT / "index.html"
    if url.endswith(".html"):
        dest = OUT / url.strip("/")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page, encoding="utf-8")
    if not url.endswith(".html"):
        SITEMAP.append(url)


def parse_page(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"\s*<!--(\{.*?\})-->", text, re.S)
    meta = json.loads(m.group(1)) if m else {}
    body = text[m.end():] if m else text
    return meta, body


# ---------- Carga de artículos ----------

def load_items(name):
    items = []
    folder = ROOT / "content" / name
    if not folder.exists():
        return items
    for f in sorted(folder.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ! No se pudo leer {f.name}: {e}")
            continue
        if data.get("draft"):
            continue
        data["slug"] = f.stem
        data["date"] = str(data.get("date") or "")[:10]
        if not data["date"]:
            m = re.match(r"(\d{4}-\d{2}-\d{2})", f.stem)
            data["date"] = m.group(1) if m else ""
        data["collection"] = name
        data["url"] = f"/{name}/{f.stem}/"
        data["minutes"] = minutos_lectura(data.get("body"))
        items.append(data)
    items.sort(key=lambda d: (d["date"], d["slug"]), reverse=True)
    return items


# ---------- Tarjeta genérica (Novedades y bloque del inicio) ----------

def card(item):
    thumb = (f'<img src="{esc(item["image"])}" alt="{esc(item.get("image_alt") or "")}" loading="lazy">'
             if item.get("image") else "")
    cat = item.get("category") or ""
    pill = f'<span class="pill">{esc(cat)}</span>' if cat else ""
    data_cat = f' data-cat="{esc(cat)}"' if item["collection"] == "novedades" else ""
    return f'''<a class="post-card"{data_cat} href="{item["url"]}">
      <div class="thumb">{thumb}</div>
      <div class="txt">
        <div class="meta">{pill}<time datetime="{item["date"]}">{fecha_larga(item["date"])}</time></div>
        <h3>{esc(item.get("title"))}</h3>
        <p>{esc(item.get("summary"))}</p>
      </div>
    </a>'''


def empty_box(msg):
    return (f'<div class="empty"><img src="/assets/img/logo-cuadrado.png" alt="">'
            f'<p>{esc(msg)}</p></div>')


def filter_buttons(items):
    cats = sorted({i.get("category") for i in items if i.get("category")})
    if len(cats) < 2:
        return ""
    return ('<div class="filters" role="group" aria-label="Filtrar por categoría">'
            '<button data-cat="todas" aria-pressed="true">Todas</button>'
            + "".join(f'<button data-cat="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in cats)
            + "</div>")


# ---------- Sección «Ideas y análisis» ----------

def ed_meta(item):
    return (f'<time datetime="{item["date"]}">{fecha_larga(item["date"])}</time>'
            f'<span aria-hidden="true">·</span><span>{item["minutes"]} min de lectura</span>')


def ed_card(item):
    cat = item.get("category") or ""
    return f'''<a class="ed-card" data-filter-item data-cat="{esc(cat)}" href="{item["url"]}">
      <span class="ed-cat">{esc(cat)}</span>
      <h3>{esc(item.get("title"))}</h3>
      <p>{esc(item.get("summary"))}</p>
      <span class="ed-meta">{ed_meta(item)}</span>
    </a>'''


def ed_featured(item, cfg):
    cat = item.get("category") or ""
    img = (f'<div class="ed-feat-img"><img src="{esc(item["image"])}" alt="{esc(item.get("image_alt") or "")}"></div>'
           if item.get("image") else "")
    return f'''<a class="ed-featured{' has-img' if img else ''}" data-filter-item data-cat="{esc(cat)}" href="{item["url"]}">
      <div class="ed-feat-txt">
        <span class="ed-label">{cfg["featured_label"]}</span>
        <span class="ed-cat">{esc(cat)}</span>
        <h2>{esc(item.get("title"))}</h2>
        <p>{esc(item.get("summary"))}</p>
        <span class="ed-meta">{ed_meta(item)}</span>
        <span class="ed-more">{cfg["more"]}</span>
      </div>
      {img}
    </a>'''


def build_editorial(cfg, items):
    name = cfg["name"]
    if items:
        featured = next((i for i in items if i.get("featured")), items[0])
        rest = [i for i in items if i is not featured]
        cards = ('<div class="ed-grid">' + "".join(ed_card(i) for i in rest) + "</div>") if rest else ""
        listing = f'''{filter_buttons(items)}
    {ed_featured(featured, cfg)}
    {cards}'''
    else:
        listing = empty_box(cfg["empty"])
    content = f'''
<div class="page-head ed-head">
  <div class="wrap">
    <h1>{cfg["h1"]}</h1>
    <p>{cfg["intro"]}.</p>
  </div>
</div>
<section class="ed">
  <div class="wrap">
    {listing}
  </div>
</section>'''
    render(f"/{name}/", content, f'{cfg["label"]} | Viple Consultores', cfg["intro"] + ".", nav=cfg["nav"])

    for item in items:
        render_article(cfg, item, items)


def share_links(item):
    url = SITE_URL + item["url"]
    u, t = quote(url, safe=""), quote(item.get("title") or "", safe="")
    links = [
        ("LinkedIn", f"https://www.linkedin.com/sharing/share-offsite/?url={u}"),
        ("X", f"https://twitter.com/intent/tweet?url={u}&text={t}"),
        ("WhatsApp", f"https://wa.me/?text={t}%20{u}"),
        ("Correo", f"mailto:?subject={t}&body={u}"),
    ]
    out = "".join(f'<a href="{esc(h)}" target="_blank" rel="noopener">{n}</a>' for n, h in links)
    out += f'<button type="button" data-copy="{esc(url)}">Copiar enlace</button>'
    return f'<div class="ed-share"><span>Compartir</span>{out}</div>'


def related(item, items, n=3):
    others = [i for i in items if i is not item]
    same = [i for i in others if i.get("category") and i.get("category") == item.get("category")]
    rest = [i for i in others if i not in same]
    return (same + rest)[:n]


def render_article(cfg, item, items):
    name = cfg["name"]
    body_html = markdown.markdown(item.get("body") or "", extensions=["extra", "sane_lists"])
    author = item.get("author") or DEFAULT_AUTHOR
    cat = item.get("category") or ""
    cover = (f'<figure class="ed-cover"><img src="{esc(item["image"])}" alt="{esc(item.get("image_alt") or "")}"></figure>'
             if item.get("image") else "")
    sources = [s for s in (item.get("sources") or []) if isinstance(s, dict) and (s.get("url") or s.get("title"))]
    sources_html = ""
    if sources:
        lis = "".join(
            f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s.get("title") or s["url"])}</a></li>'
            if s.get("url") else f'<li>{esc(s.get("title"))}</li>' for s in sources)
        sources_html = f'<aside class="ed-sources"><h2>Fuentes</h2><ul>{lis}</ul></aside>'
    rel = related(item, items)
    rel_html = (f'''<section class="ed-related">
  <div class="wrap">
    <h2>{cfg["related"]}</h2>
    <div class="ed-grid">{"".join(ed_card(i) for i in rel)}</div>
  </div>
</section>''' if rel else "")
    photo = ('<img src="/assets/img/gabriel.jpg" alt="">' if "villavicencio" in author.lower() else "")
    content = f'''
<div class="page-head ed-head ed-article-head">
  <div class="wrap ed-narrow">
    <a class="ed-back-top" href="/{name}/">← {cfg["label"]}</a>
    <span class="ed-cat">{esc(cat)}</span>
    <h1>{esc(item.get("title"))}</h1>
    <p class="ed-byline">Por {esc(author)} <span aria-hidden="true">·</span> <time datetime="{item["date"]}">{fecha_larga(item["date"])}</time> <span aria-hidden="true">·</span> {item["minutes"]} min de lectura</p>
  </div>
</div>
<section class="ed">
  <article class="wrap ed-narrow">
    {cover}
    <div class="prose ed-prose">{body_html}</div>
    {sources_html}
    {share_links(item)}
    <div class="author-line">{photo}<div><strong>{esc(author)}</strong>Viple Consultores · Legal &amp; Compliance</div></div>
    <a class="back" href="/{name}/">← Volver a {cfg["label"]}</a>
  </article>
</section>
{rel_html}'''
    image = item.get("image") or "/assets/img/logo-cuadrado.png"
    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": item.get("title"),
        "description": item.get("summary"),
        "datePublished": item["date"],
        "author": {"@type": "Person", "name": author},
        "publisher": {"@type": "Organization", "name": "Viple Consultores",
                      "logo": {"@type": "ImageObject", "url": SITE_URL + "/assets/img/logo-cuadrado.png"}},
        "image": SITE_URL + image,
        "articleSection": cat,
        "mainEntityOfPage": SITE_URL + item["url"],
    }
    head_extra = (f'<meta property="article:published_time" content="{item["date"]}">\n'
                  f'<meta property="article:section" content="{esc(cat)}">\n'
                  f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')
    render(item["url"], content, f'{item.get("title")} | Viple Consultores',
           item.get("summary") or cfg["intro"], nav=cfg["nav"], og_image=image,
           og_type="article", head_extra=head_extra)


# ---------- Sección «Te ayudamos con tus dudas» ----------

def load_temas():
    temas = {}
    folder = ROOT / "content" / "temas-dudas"
    for f in (sorted(folder.glob("*.json")) if folder.exists() else []):
        try:
            t = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ! No se pudo leer el tema {f.name}: {e}")
            continue
        tid = str(t.get("id") or f.stem).strip()
        try:
            orden = int(t.get("order", 99))
        except (TypeError, ValueError):
            orden = 99
        temas[tid] = {"id": tid, "name": t.get("name") or tid, "order": orden}
    return temas


def texto_plano(md, n=170):
    txt = re.sub(r"<[^>]+>", " ", markdown.markdown(md or ""))
    txt = re.sub(r"\s+", " ", html.unescape(txt)).strip()
    return txt if len(txt) <= n else txt[:n].rsplit(" ", 1)[0] + "…"


def prep_dudas(items, temas):
    revisar = []
    for it in items:
        aud = str(it.get("audience") or "").strip().lower()
        it["aud"] = aud if aud in PUBLICOS else ""
        it["tema"] = temas.get(str(it.get("topic") or "").strip())
        it["resumen"] = it.get("summary") or texto_plano(it.get("body"))
        if not it["aud"] or not it["tema"]:
            revisar.append(it["slug"])
    if revisar:
        print("  ! Dudas sin público o tema válido (solo visibles en «Ver todo»): " + ", ".join(revisar))
    return items


def duda_card(it):
    tema = it["tema"]["name"] if it["tema"] else ""
    tid = it["tema"]["id"] if it["tema"] else ""
    aud = PUBLICOS.get(it["aud"], "")
    meta = (f'<span class="dd-topic">{esc(tema)}</span>' if tema else "") + \
           (f'<span class="dd-aud">{aud}</span>' if aud else "")
    return f'''<li class="dd-item" data-aud="{it["aud"]}" data-topic="{esc(tid)}">
      <a href="{it["url"]}">
        <span class="dd-meta">{meta}</span>
        <h3>{esc(it.get("title"))}</h3>
        <p>{esc(it["resumen"])}</p>
        <span class="dd-more">Leer respuesta →</span>
      </a>
    </li>'''


def build_dudas(items, temas):
    name = DUDAS["name"]
    if items:
        usados = {it["tema"]["id"] for it in items if it["tema"]}
        lista = sorted((t for t in temas.values() if t["id"] in usados), key=lambda t: (t["order"], t["name"]))
        topic_btns = ('<button type="button" data-topic="" aria-pressed="true">Todos los temas</button>' +
                      "".join(f'<button type="button" data-topic="{esc(t["id"])}" aria-pressed="false">{esc(t["name"])}</button>'
                              for t in lista))
        listing = f'''<div class="dd-filters" data-dd-filters>
      <p class="dd-q" id="dd-q-aud">¿Qué información buscas?</p>
      <div class="seg" role="group" aria-labelledby="dd-q-aud">
        <button type="button" data-aud="todo" aria-pressed="true">Ver todo</button>
        <button type="button" data-aud="personas" aria-pressed="false">Para mí</button>
        <button type="button" data-aud="negocios" aria-pressed="false">Para mi negocio</button>
      </div>
      <h2 class="dd-h" id="dd-q-topic">Explora por tema</h2>
      <div class="chips" role="group" aria-labelledby="dd-q-topic">{topic_btns}</div>
    </div>
    <p class="dd-count" aria-live="polite" data-dd-count></p>
    <ul class="dd-list" data-dd-list>{"".join(duda_card(it) for it in items)}</ul>
    <p class="dd-none" data-dd-none hidden>Todavía no hay preguntas para esta combinación. Prueba con otro tema o con «Ver todo».</p>'''
    else:
        listing = empty_box(DUDAS["empty"])
    content = f'''
<div class="page-head ed-head">
  <div class="wrap">
    <h1>{DUDAS["label"]}</h1>
    <p>{DUDAS["intro"]}</p>
  </div>
</div>
<section class="ed dd">
  <div class="wrap">
    {listing}
  </div>
</section>'''
    render(f"/{name}/", content, f'{DUDAS["label"]} | Viple Consultores', DUDAS["intro"], nav="dudas")
    for it in items:
        render_duda(it, items)


def render_duda(it, items):
    name = DUDAS["name"]
    body_html = markdown.markdown(it.get("body") or "", extensions=["extra", "sane_lists"])
    author = it.get("author") or DEFAULT_AUTHOR
    tema = it["tema"]["name"] if it["tema"] else ""
    aud = PUBLICOS.get(it["aud"], "")
    adjunto = ""
    if it.get("attachment"):
        adjunto = (f'<p class="dd-file"><a href="{esc(it["attachment"])}" target="_blank" rel="noopener">'
                   f'Descargar archivo de apoyo</a></p>')
    sources = [x for x in (it.get("sources") or []) if isinstance(x, dict) and (x.get("url") or x.get("title"))]
    sources_html = ""
    if sources:
        lis = "".join(
            f'<li><a href="{esc(x["url"])}" target="_blank" rel="noopener">{esc(x.get("title") or x["url"])}</a></li>'
            if x.get("url") else f'<li>{esc(x.get("title"))}</li>' for x in sources)
        sources_html = f'<aside class="ed-sources"><h2>Fuentes</h2><ul>{lis}</ul></aside>'
    otros = [i for i in items if i is not it]
    mismo = [i for i in otros if i["tema"] and it["tema"] and i["tema"]["id"] == it["tema"]["id"]]
    rel = (mismo + [i for i in otros if i not in mismo])[:3]
    rel_html = (f'''<section class="ed-related">
  <div class="wrap">
    <h2>Otras preguntas</h2>
    <ul class="dd-list">{"".join(duda_card(i) for i in rel)}</ul>
  </div>
</section>''' if rel else "")
    tags = (f'<span class="ed-cat">{esc(tema)}</span>' if tema else "") + \
           (f'<span class="dd-aud on-dark">{aud}</span>' if aud else "")
    content = f'''
<div class="page-head ed-head ed-article-head">
  <div class="wrap ed-narrow">
    <a class="ed-back-top" href="/{name}/">← {DUDAS["label"]}</a>
    <div class="dd-tags">{tags}</div>
    <h1>{esc(it.get("title"))}</h1>
    <p class="ed-byline">Por {esc(author)} <span aria-hidden="true">·</span> <time datetime="{it["date"]}">{fecha_larga(it["date"])}</time> <span aria-hidden="true">·</span> {it["minutes"]} min de lectura</p>
  </div>
</div>
<section class="ed">
  <article class="wrap ed-narrow">
    <div class="prose ed-prose">{body_html}</div>
    {adjunto}
    {sources_html}
    {share_links(it)}
    <a class="back" href="/{name}/">← Volver a {DUDAS["label"]}</a>
  </article>
</section>
{rel_html}'''
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": it.get("title"),
          "description": it["resumen"], "datePublished": it["date"],
          "author": {"@type": "Person", "name": author},
          "publisher": {"@type": "Organization", "name": "Viple Consultores", "url": SITE_URL},
          "mainEntityOfPage": SITE_URL + it["url"]}
    render(it["url"], content, f'{it.get("title")} | Viple Consultores', it["resumen"], nav="dudas",
           og_type="article",
           head_extra=f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')


def dudas_home(items):
    destacadas = [i for i in items if i.get("featured_home")]
    elegidas = (destacadas or items)[:3]
    if elegidas:
        cuerpo = f'<ul class="dd-list dd-home">{"".join(duda_card(i) for i in elegidas)}</ul>'
    else:
        cuerpo = f'<p class="dd-soon">{esc(DUDAS["empty"])}</p>'
    return f'''<section class="home-dudas">
  <div class="wrap">
    <div class="section-head reveal">
      <h2>¿Tienes preguntas?</h2>
      <p>{DUDAS["intro"]}</p>
    </div>
    {cuerpo}
    <p class="dd-all"><a href="/dudas/">Ver todas las preguntas →</a></p>
  </div>
</section>'''


# ---------- Sección «Novedades» ----------

def build_novedades(items):
    cfg = NOVEDADES
    name = cfg["name"]
    filters = filter_buttons(items)
    listing = ('<div class="posts">' + "".join(card(i) for i in items) + "</div>") if items else empty_box(cfg["empty"])
    content = f'''
<div class="page-head">
  <div class="wrap">
    <div class="eyebrow">{cfg["eyebrow"]}</div>
    <h1>{cfg["h1"]}</h1>
    <p>{cfg["intro"]}</p>
  </div>
</div>
<section>
  <div class="wrap">
    {filters}
    {listing}
  </div>
</section>'''
    render(f"/{name}/", content, f'{cfg["eyebrow"]} | Viple Consultores', cfg["intro"], nav=cfg["nav"])

    for item in items:
        body_html = markdown.markdown(item.get("body") or "", extensions=["extra", "sane_lists"])
        cover = (f'<figure class="cover"><img src="{esc(item["image"])}" alt="{esc(item.get("image_alt") or "")}"></figure>'
                 if item.get("image") else "")
        author = item.get("author") or DEFAULT_AUTHOR
        eyebrow = item.get("category") or cfg["item_label"]
        source = ""
        if item.get("source_url") or item.get("source_name"):
            label = esc(item.get("source_name") or item.get("source_url"))
            link = (f'<a href="{esc(item["source_url"])}" target="_blank" rel="noopener">{label}</a>'
                    if item.get("source_url") else label)
            source = f'<div class="source-box">Fuente: {link}</div>'
        photo = ('<img src="/assets/img/gabriel.jpg" alt="">'
                 if "villavicencio" in author.lower() else "")
        content = f'''
<div class="page-head">
  <div class="wrap">
    <div class="crumbs"><a href="/{name}/">{cfg["eyebrow"]}</a> / {esc(eyebrow)}</div>
    <h1>{esc(item.get("title"))}</h1>
    <p><time datetime="{item["date"]}">{fecha_larga(item["date"])}</time> · Por {esc(author)}</p>
  </div>
</div>
<section>
  <article class="wrap article">
    {cover}
    <div class="prose">{body_html}</div>
    {source}
    <div class="author-line">{photo}<div><strong>{esc(author)}</strong>Viple Consultores · Legal &amp; Compliance</div></div>
    <a class="back" href="/{name}/">← Ver todas las {cfg["eyebrow"].lower()}</a>
  </article>
</section>'''
        render(item["url"], content, f'{item.get("title")} | Viple Consultores',
               item.get("summary") or cfg["intro"], nav=cfg["nav"],
               og_image=item.get("image") or "/assets/img/logo-cuadrado.png")


# ---------- Sección «Presentaciones especiales» (content/presentaciones) ----------

PRESENTACIONES = {
    "h1": "Presentaciones especiales",
    "intro": "Presentaciones que hemos preparado sobre temas legales de interés para personas y empresas.",
    "empty": "Muy pronto publicaremos nuestras primeras presentaciones.",
}

ICONO_PRES = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" '
              'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
              '<rect x="3" y="4" width="18" height="12" rx="1"/><path d="M12 16v4M8 20h8"/>'
              '<path d="M7 12l3-3 2 2 4-4"/></svg>')


def pres_slides(it):
    return [s for s in (it.get("slides") or []) if isinstance(s, str) and s.strip()]


def pres_card(it):
    slides = pres_slides(it)
    portada = it.get("image") or (slides[0] if slides else "")
    img = f'<img src="{esc(portada)}" alt="" loading="lazy">' if portada else ICONO_PRES
    tag, attrs, more = "div", "", ""
    if slides:
        tag, attrs = "a", f' href="{it["url"]}"'
    elif it.get("link"):
        tag, attrs = "a", f' href="{esc(it["link"])}" target="_blank" rel="noopener"'
    if tag == "a":
        more = '<span class="pres-more">Ver presentación <span aria-hidden="true">→</span></span>'
    return f'''<li><{tag} class="pres-card"{attrs}>
      <div class="pres-img">{img}</div>
      <div class="pres-txt">
        <h3>{esc(it.get("title"))}</h3>
        <p>{esc(it.get("summary"))}</p>
        {more}
      </div>
    </{tag}></li>'''


def render_presentacion(it):
    slides = pres_slides(it)
    n = len(slides)
    figs = ""
    for i, s in enumerate(slides, 1):
        lazy = "" if i == 1 else ' loading="lazy"'
        figs += (f'<figure class="slide"><img src="{esc(s)}" alt="Diapositiva {i} de {n}: {esc(it.get("title"))}"'
                 f'{lazy} draggable="false"></figure>')
    nav = ('<div class="slides-nav"><button type="button" data-prev aria-label="Diapositiva anterior">←</button>'
           f'<span data-count aria-live="polite">1 / {n}</span>'
           '<button type="button" data-next aria-label="Diapositiva siguiente">→</button></div>') if n > 1 else ""
    body = markdown.markdown(it.get("body") or "", extensions=["extra", "sane_lists"])
    texto = f'<div class="prose pres-body">{body}</div>' if body.strip() else ""
    content = f'''
<div class="page-head">
  <div class="wrap">
    <div class="crumbs"><a href="/presentaciones/">{PRESENTACIONES["h1"]}</a></div>
    <h1>{esc(it.get("title"))}</h1>
    <p>{esc(it.get("summary"))}</p>
  </div>
</div>
<section class="pres-view">
  <div class="wrap">
    <div class="slides" data-slides>
      <div class="slides-track" tabindex="0" role="region" aria-label="Diapositivas de la presentación">{figs}</div>
      {nav}
    </div>
    {texto}
    <a class="back" href="/presentaciones/">← Ver todas las presentaciones</a>
  </div>
</section>'''
    render(it["url"], content, f'{it.get("title")} | Viple Consultores', it.get("summary") or PRESENTACIONES["intro"],
           nav="presentaciones", og_image=it.get("image") or slides[0])


def build_presentaciones(items):
    cfg = PRESENTACIONES
    listing = ('<ul class="pres-list">' + "".join(pres_card(i) for i in items) + "</ul>") if items else empty_box(cfg["empty"])
    content = f'''
<div class="page-head">
  <div class="wrap">
    <h1>{cfg["h1"]}</h1>
    <p>{cfg["intro"]}</p>
  </div>
</div>
<section class="pres">
  <div class="wrap">
    {listing}
  </div>
</section>'''
    render("/presentaciones/", content, f'{cfg["h1"]} | Viple Consultores', cfg["intro"], nav="presentaciones")
    for it in items:
        if pres_slides(it):
            render_presentacion(it)


# ---------- Bloque «lo último» del inicio ----------

def latest_block(all_items):
    if not all_items:
        return ""
    cards = "".join(card(i) for i in all_items[:3])
    return f'''<section style="background:var(--sage-light)">
  <div class="wrap">
    <div class="section-head reveal">
      <h2>Lo último publicado</h2>
      <p>Artículos sobre cómo mejorar el trabajo legal, nuevas normas y asuntos de interés para tu empresa.
      <br><a href="/notas/" style="color:var(--navy)">Ver «¿Tu equipo odia a Legal?»</a> · <a href="/novedades/" style="color:var(--navy)">Ver novedades</a></p>
    </div>
    <div class="posts">{cards}</div>
  </div>
</section>'''


# ---------- Construcción ----------

def main():
    # En Windows/OneDrive alguna carpeta puede quedar bloqueada: se borra lo posible y se sobrescribe el resto
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT / "assets", OUT / "assets", dirs_exist_ok=True)
    shutil.copytree(ROOT / "admin", OUT / "admin", dirs_exist_ok=True)

    ideas = load_items("notas")
    novedades = load_items("novedades")
    temas = load_temas()
    dudas = prep_dudas(load_items("dudas"), temas)
    DUDAS_SLUGS.update(d["slug"] for d in dudas)
    everything = sorted(ideas + novedades, key=lambda d: d["date"], reverse=True)

    for path in sorted((SRC / "pages").rglob("*.html")):
        rel = path.relative_to(SRC / "pages").as_posix()
        if rel == "index.html":
            url = "/"
        elif rel.endswith("/index.html"):
            url = "/" + rel[: -len("index.html")]
        else:
            url = "/" + rel[: -len(".html")] + "/"
        if rel == "404.html":
            url = "/404.html"
        meta, body = parse_page(path)
        body = body.replace("{{latest}}", latest_block(everything))
        body = body.replace("{{dudas_home}}", dudas_home(dudas))
        body = fill_services(body)
        meta["title"] = fill_services(meta.get("title", "Viple Consultores")).replace("&amp;", "&")
        render(url, body, meta.get("title", "Viple Consultores"), meta.get("description", ""),
               nav=meta.get("nav", ""), logo=meta.get("logo", "cuadrado"),
               og_image=meta.get("og_image", "/assets/img/logo-cuadrado.png"))

    build_editorial(IDEAS, ideas)
    build_dudas(dudas, temas)
    build_novedades(novedades)
    build_presentaciones(load_items("presentaciones"))

    urls = "".join(f"<url><loc>{SITE_URL}{u}</loc></url>" for u in SITEMAP)
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>',
        encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nDisallow: /admin/\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")

    print(f"Sitio generado en _site/ · {len(SITEMAP)} páginas · "
          f"{len(ideas)} artículos · {len(dudas)} dudas · {len(novedades)} novedades")


if __name__ == "__main__":
    main()
