"""
Construye el sitio de Viple Consultores en la carpeta _site/.

- Envuelve cada página de src/pages/ con la plantilla común src/layout.html
  (encabezado, menú y pie de página).
- Genera «¿Tienes preguntas?» (/preguntas/, una página por pregunta publicada) desde
  content/preguntas, «¿Tu equipo odia a Legal?» (/gestion-legal/) desde content/notas,
  «Novedades» y «Presentaciones especiales», con los contenidos guardados desde el panel (/admin).
- Las secciones sin contenido publicado llevan noindex y no entran en el sitemap.
- El sitemap usa fechas editoriales guardadas (nunca la fecha del build).

Netlify ejecuta este archivo automáticamente en cada publicación.
Para probarlo en tu computadora:  python build.py
"""
import html
import hashlib
import json
import math
import re
import shutil
import unicodedata
from pathlib import Path
from urllib.parse import quote

import markdown

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "_site"
SITE_URL = "https://vipleconsultores.com"
ORG_ID = SITE_URL + "/#organization"
DEFAULT_AUTHOR = "Gabriel Villavicencio Bedoya"

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

# Fecha de la última modificación de las plantillas de los listados generados aquí
# (actualízala solo si cambias el texto o el diseño del listado)
LISTADOS_LASTMOD = "2026-11-10"

# «¿Tu equipo odia a Legal?»: artículos en content/notas, publicados en /gestion-legal/
IDEAS = {
    "name": "notas",
    "base": "gestion-legal",
    "label": "¿Tu equipo odia a Legal?",
    "h1": "Cómo organizar el trabajo legal para que no se convierta en un cuello de botella",
    "intro": ("Consejos prácticos para que tu equipo sepa qué contratos puede cerrar con condiciones ya aprobadas, "
              "cuándo conviene involucrar a un abogado en un proyecto y cómo aprovechar lo que ya negoció con un "
              "cliente para llegar mejor preparado al siguiente acuerdo"),
    "empty": "Muy pronto publicaremos los primeros artículos.",
    "nav": "gestion-legal",
    "featured_label": "Artículo destacado",
    "more": "Leer artículo →",
    "related": "Otros artículos",
}

# «¿Tienes preguntas?»: preguntas en content/preguntas, publicadas en /preguntas/<slug>/
PREGUNTAS = {
    "base": "preguntas",
    "label": "¿Tienes preguntas?",
    "intro": "Encuentra respuestas a preguntas legales sobre situaciones de tu vida diaria o de tu negocio.",
    "empty": "Muy pronto publicaremos las respuestas a las preguntas más frecuentes.",
}

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
    "group": '<circle cx="12" cy="7.5" r="3"/><path d="M6.5 20c0-3.3 2.5-5.5 5.5-5.5s5.5 2.2 5.5 5.5"/><circle cx="5" cy="9.5" r="2.2"/><path d="M1.5 18.5c0-2.3 1.5-4 3.6-4.2"/><circle cx="19" cy="9.5" r="2.2"/><path d="M22.5 18.5c0-2.3-1.5-4-3.6-4.2"/>',
    "hand-heart": '<path d="M12 11.5 8.6 8.2a2.2 2.2 0 0 1 3.1-3.1l.3.3.3-.3a2.2 2.2 0 0 1 3.1 3.1z"/><path d="M2.5 14.5h3l3.5 1h3.5a1.5 1.5 0 0 1 0 3H9"/><path d="M12.5 18.5l5.6-2.4a1.6 1.6 0 0 1 1.9 2.4L15 21H5.5l-3-1.5"/>',
    "zoom": '<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>',
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
    "constitucion-asociaciones": "group",
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


def svc_links():
    """Lista de enlaces a todos los servicios (p. ej. en /contacto/), en el orden de servicios.json."""
    return "\n".join(f'        <li><a href="/servicios/{s["slug"]}/">→ {esc(s["name"])}</a></li>' for s in SERVICIOS)


# Preguntas publicadas (se cargan en main() desde content/preguntas)
PUBLICADAS = []


def q_url(q):
    return f"/{PREGUNTAS['base']}/{q['slug']}/"


def q_items(qs):
    return "".join(f'<li><a href="{q_url(q)}"><span>{esc(q["pregunta"])}</span>{icon("arrow-right", "q-arrow")}</a></li>'
                   for q in qs)


def svc_preguntas(slug):
    qs = [q for q in PUBLICADAS if q["servicio_asociado"] == slug]
    if not qs:
        return ""
    return f"""<div class="rel-q">
      <h2>Preguntas relacionadas</h2>
      <ul>{q_items(qs)}</ul>
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


def destacadas_portada():
    qs = [q for q in PUBLICADAS if q.get("destacada")]
    qs.sort(key=lambda q: (q["orden_portada"], q["_svc_i"], q["orden"], q["pregunta"]))
    return qs[:5]


def preguntas_portada():
    qs = destacadas_portada()
    if not qs:
        return ""
    return f"""<section class="home-faq">
  <div class="wrap faq-grid">
    <div class="faq-head">
      <h2>¿Tienes preguntas?</h2>
      <p>Preguntas frecuentes sobre cada uno de nuestros servicios.</p>
    </div>
    <div class="faq-list">
      <ul class="faq-q">{q_items(qs)}</ul>
      <a class="faq-all" href="/{PREGUNTAS['base']}/">Ver todas las preguntas <span aria-hidden="true">→</span></a>
    </div>
  </div>
</section>"""


def fill_services(text):
    text = text.replace("{{svc_panels}}", svc_panels())
    text = text.replace("{{svc_panels_sum}}", svc_panels(summary=True))
    text = text.replace("{{preguntas_portada}}", preguntas_portada())
    text = text.replace("{{svc_links}}", svc_links())
    for s in SERVICIOS:
        text = text.replace("{{svc:" + s["slug"] + "}}", esc(s["name"]))
        text = text.replace("{{svc_preguntas:" + s["slug"] + "}}", svc_preguntas(s["slug"]))
        text = text.replace("{{svc_nav:" + s["slug"] + "}}", svc_nav(s["slug"]))
    text = re.sub(r"\{\{icon:([a-z0-9-]+)\}\}", lambda m: icon(m.group(1)), text)
    return text


def render(url, content, title, description, nav="", logo="cuadrado",
           og_image="/assets/img/logo-cuadrado.png", og_type="website", head_extra="",
           noindex=False, lastmod=None):
    if noindex:
        head_extra = '<meta name="robots" content="noindex, follow">\n' + head_extra
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
    # Sitemap: solo direcciones canónicas, indexables y publicadas
    if not url.endswith(".html") and not noindex:
        SITEMAP.append((url, lastmod))


def max_fecha(*fechas):
    validas = [f for f in fechas if f and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(f))]
    return max(validas) if validas else None


def parse_page(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"\s*<!--(\{.*?\})-->", text, re.S)
    meta = json.loads(m.group(1)) if m else {}
    body = text[m.end():] if m else text
    return meta, body


# ---------- Carga de artículos ----------

def load_items(name, base=None):
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
        data["url"] = f"/{base or name}/{f.stem}/"
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
    name = cfg["base"]
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
    render(f"/{name}/", content, f'{cfg["label"]} | Viple Consultores', cfg["intro"] + ".", nav=cfg["nav"],
           noindex=not items, lastmod=max_fecha(LISTADOS_LASTMOD, *(i["date"] for i in items)))

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
    name = cfg["base"]
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
           og_type="article", head_extra=head_extra, lastmod=max_fecha(item["date"]))


# ---------- Sección «¿Tienes preguntas?» (content/preguntas) ----------

SERVICE_NAMES = {s["slug"]: s["name"] for s in SERVICIOS}
SERVICE_ORDER = {s["slug"]: i for i, s in enumerate(SERVICIOS)}
# Etiqueta breve de cada servicio como categoría de presentaciones (mismo identificador que el servicio)
PRES_CAT = {s["slug"]: (s.get("categoria_corta") or "").strip() or s["name"] for s in SERVICIOS}


def texto_plano(md):
    txt = re.sub(r"<[^>]+>", " ", markdown.markdown(md or ""))
    return re.sub(r"\s+", " ", html.unescape(txt)).strip()


def _num(v, default):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def load_preguntas():
    """Lee content/preguntas. Devuelve las completas (respuesta, título SEO, descripción SEO y fecha).
    Las que aún no tienen respuesta se omiten en silencio; las que tienen respuesta pero les falta algo se avisan."""
    folder = ROOT / "content" / "preguntas"
    publicadas, total, revisar = [], 0, []
    for f in (sorted(folder.glob("*.json")) if folder.exists() else []):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ! No se pudo leer la pregunta {f.name}: {e}")
            continue
        total += 1
        q = {
            "pregunta": str(d.get("pregunta") or "").strip(),
            "slug": str(d.get("slug") or f.stem).strip(),
            "servicio_asociado": str(d.get("servicio_asociado") or "").strip(),
            "respuesta": str(d.get("respuesta") or "").strip(),
            "title": str(d.get("title") or "").strip(),
            "meta_description": str(d.get("meta_description") or "").strip(),
            "destacada": d.get("destacada") is True,
            "fecha": str(d.get("fecha_actualizacion") or "")[:10],
            "orden": _num(d.get("orden"), 99),
            "orden_portada": _num(d.get("orden_portada"), 99),
        }
        faltan = [k for k, v in (("pregunta", q["pregunta"]), ("respuesta", q["respuesta"]), ("title", q["title"]),
                                 ("meta_description", q["meta_description"]))
                  if not v]
        if q["servicio_asociado"] not in SERVICE_NAMES:
            faltan.append("servicio_asociado")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", q["slug"]):
            faltan.append("slug")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", q["fecha"]):
            faltan.append("fecha_actualizacion")
        if not q["respuesta"]:
            continue  # pregunta aún sin responder: no se muestra
        if faltan:
            revisar.append(f'{f.name} (falta: {", ".join(faltan)})')
            continue
        q["_svc_i"] = SERVICE_ORDER[q["servicio_asociado"]]
        publicadas.append(q)
    if revisar:
        print("  ! Preguntas con respuesta pero incompletas (NO se publican): " + "; ".join(revisar))
    vistos = set()
    for q in list(publicadas):
        if q["slug"] in vistos:
            print(f'  ! Slug repetido, se omite: {q["slug"]}')
            publicadas.remove(q)
        vistos.add(q["slug"])
    publicadas.sort(key=lambda q: (q["_svc_i"], q["orden"], q["pregunta"]))
    return publicadas, total


def titulo_seo(t):
    # Acepta títulos que ya terminan en «| Viple» o «| Viple Consultores» sin duplicar la marca
    t = re.sub(r"\s*\|\s*Viple(\s+Consultores)?\s*$", "", t.strip(), flags=re.I)
    return f"{t} | Viple Consultores"


def aviso_legal(que):
    """Aviso legal estándar al final de las respuestas y de las presentaciones (texto fijo, igual en todas)."""
    return (f'<aside class="aviso-legal" aria-label="Aviso legal"><p><strong>Aviso legal:</strong> '
            f'{que} tiene carácter general e informativo y no constituye asesoría legal, '
            f'ni crea una relación abogado-cliente. Su contenido puede no reflejar cambios normativos o criterios '
            f'posteriores a su publicación y no debe utilizarse como sustituto de una evaluación profesional de '
            f'un caso concreto. Antes de tomar decisiones, consulta con un abogado que pueda analizar tu situación '
            f'particular.</p></aside>')


def render_pregunta(q):
    base = PREGUNTAS["base"]
    svc = q["servicio_asociado"]
    body_html = markdown.markdown(q["respuesta"], extensions=["extra", "sane_lists"])
    content = f"""
<div class="page-head ed-head ed-article-head">
  <div class="wrap ed-narrow">
    <a class="ed-back-top" href="/{base}/">← {PREGUNTAS["label"]}</a>
    <span class="ed-cat">{esc(SERVICE_NAMES[svc])}</span>
    <h1>{esc(q["pregunta"])}</h1>
    <p class="ed-byline">Actualizado el <time datetime="{q["fecha"]}">{fecha_larga(q["fecha"])}</time></p>
  </div>
</div>
<section class="ed">
  <article class="wrap ed-narrow">
    <div class="prose ed-prose">{body_html}</div>
    {aviso_legal("La información contenida en esta respuesta")}
    <p class="q-svc">Servicio relacionado: <a href="/servicios/{svc}/">{esc(SERVICE_NAMES[svc])} <span aria-hidden="true">→</span></a></p>
    <div class="q-cta">
      <p>¿Quieres revisar tu caso?</p>
      <a class="btn" href="/contacto/">Conversemos</a>
    </div>
    {share_links({"url": q_url(q), "title": q["pregunta"]})}
    <a class="back" href="/{base}/">← Volver a {PREGUNTAS["label"]}</a>
  </article>
</section>"""
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "url": SITE_URL + q_url(q),
          "mainEntity": [{"@type": "Question", "name": q["pregunta"],
                          "acceptedAnswer": {"@type": "Answer", "text": texto_plano(q["respuesta"])}}]}
    render(q_url(q), content, titulo_seo(q["title"]), q["meta_description"], nav="preguntas", og_type="article",
           head_extra=f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>',
           lastmod=q["fecha"])


def build_preguntas(publicadas):
    base = PREGUNTAS["base"]
    if publicadas:
        grupos = ""
        for s in SERVICIOS:
            qs = [q for q in publicadas if q["servicio_asociado"] == s["slug"]]
            if not qs:
                continue
            lis = "".join(f'<li><a href="{q_url(q)}">{esc(q["pregunta"])}</a></li>' for q in qs)
            grupos += f"""<details class="acc">
      <summary><span class="acc-ico">{icon(SVC_ICONS.get(s["slug"], "doc-check"))}</span><span class="acc-name">{esc(s["name"])}</span><span class="acc-n">{len(qs)}</span></summary>
      <ul class="acc-list">{lis}</ul>
    </details>"""
        listing = f'<div class="acc-group">{grupos}</div>'
        ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": PREGUNTAS["label"],
              "url": f"{SITE_URL}/{base}/",
              "mainEntity": {"@type": "ItemList", "itemListElement": [
                  {"@type": "ListItem", "position": i, "url": SITE_URL + q_url(q), "name": q["pregunta"]}
                  for i, q in enumerate(publicadas, 1)]}}
        head_extra = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    else:
        listing = (f'<div class="empty"><img src="/assets/img/logo-cuadrado.png" alt="">'
                   f'<p>{esc(PREGUNTAS["empty"])}</p>'
                   f'<p>Si tienes una consulta, <a href="/contacto/">conversemos</a>.</p></div>')
        head_extra = ""
    content = f"""
<div class="page-head ed-head">
  <div class="wrap">
    <h1>{PREGUNTAS["label"]}</h1>
    <p>{PREGUNTAS["intro"]}</p>
  </div>
</div>
<section class="ed">
  <div class="wrap">
    {listing}
  </div>
</section>"""
    render(f"/{base}/", content, f'{PREGUNTAS["label"]} | Viple Consultores', PREGUNTAS["intro"], nav="preguntas",
           head_extra=head_extra, noindex=not publicadas,
           lastmod=max_fecha(LISTADOS_LASTMOD, *(q["fecha"] for q in publicadas)))
    for q in publicadas:
        render_pregunta(q)


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
    render(f"/{name}/", content, f'{cfg["eyebrow"]} | Viple Consultores', cfg["intro"], nav=cfg["nav"],
           noindex=not items, lastmod=max_fecha(LISTADOS_LASTMOD, *(i["date"] for i in items)))

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
               og_image=item.get("image") or "/assets/img/logo-cuadrado.png", lastmod=max_fecha(item["date"]))


# ---------- Sección «Presentaciones especiales» (content/presentaciones) ----------

PRESENTACIONES = {
    "h1": "Presentaciones especiales",
    "intro": "Presentaciones que hemos preparado sobre temas legales de interés para personas y empresas.",
    "empty": "Muy pronto publicaremos nuestras primeras presentaciones.",
}

# Divisiones del catálogo de presentaciones (además de los servicios).
# Para agregar un sector: añádelo aquí y en el campo «Sector económico» de admin/config.yml (mismo valor).
CAT_OTROS = ("otros", "Otros")
SECTORES = [
    ("retail", "Retail"),
    ("colegios", "Colegios"),
    ("inmobiliarias", "Inmobiliarias"),
    ("otros", "Otros"),
]
SECTOR_NAMES = dict(SECTORES)

ICONO_PRES = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" '
              'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
              '<rect x="3" y="4" width="18" height="12" rx="1"/><path d="M12 16v4M8 20h8"/>'
              '<path d="M7 12l3-3 2 2 4-4"/></svg>')


def slugify(texto):
    """Minúsculas sin tildes, números y guiones (para direcciones web)."""
    t = unicodedata.normalize("NFKD", str(texto or "")).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def recortar(texto, n=155):
    """Texto plano de hasta ~n caracteres, cortado en una palabra completa."""
    t = re.sub(r"\s+", " ", str(texto or "")).strip()
    if len(t) <= n:
        return t
    t = t[:n].rsplit(" ", 1)[0].rstrip(",;:")
    return t + "…"


def img_dims(src):
    """Ancho y alto reales de una imagen del sitio (JPG o PNG), leídos del archivo; None si no se puede."""
    try:
        f = ROOT / str(src).lstrip("/")
        d = f.read_bytes()
    except Exception:
        return None
    if d[:4] == bytes([0x89, 0x50, 0x4E, 0x47]):  # PNG
        return int.from_bytes(d[16:20], "big"), int.from_bytes(d[20:24], "big")
    if d[:2] != bytes([0xFF, 0xD8]):  # JPG
        return None
    i = 2
    while i + 9 < len(d):
        if d[i] != 0xFF:
            i += 1
            continue
        m = d[i + 1]
        if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7:
            i += 2
            continue
        largo = int.from_bytes(d[i + 2:i + 4], "big")
        if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            return int.from_bytes(d[i + 7:i + 9], "big"), int.from_bytes(d[i + 5:i + 7], "big")
        i += 2 + largo
    return None


def wh(src):
    """Atributos width/height para que el navegador conozca la proporción antes de cargar la imagen."""
    dm = img_dims(src)
    return f' width="{dm[0]}" height="{dm[1]}"' if dm else ""


def pres_slides(it):
    return [s for s in (it.get("slides") or []) if isinstance(s, str) and s.strip()]


def prep_presentaciones(items):
    """Dirección estable y metadatos SEO con valores predeterminados (sin modificar los datos guardados)."""
    vistos = {}
    for it in items:
        # Slug: el guardado en el panel; si no existe (entradas antiguas), el nombre del archivo sin tildes.
        # Nunca se deriva del título, para que cambiar el título no cambie la dirección.
        it["pslug"] = slugify(it.get("slug")) or slugify(it["slug"])
        it["url"] = f"/presentaciones/{it['pslug']}/"
        cat = str(it.get("categoria") or "").strip()
        it["cat"] = cat if (cat in SERVICE_NAMES or cat == CAT_OTROS[0]) else ""
        if cat and not it["cat"]:
            print(f'  ! Presentación con categoría desconocida «{cat}» (se muestra solo en «Todos»): {it["slug"]}')
        sec = str(it.get("sector") or "").strip()
        it["sector"] = sec if sec in SECTOR_NAMES else ""
        if sec and not it["sector"]:
            print(f'  ! Presentación con sector desconocido «{sec}» (se muestra solo en «Todos»): {it["slug"]}')
        it["seo_title"] = titulo_seo(str(it.get("title_seo") or "").strip() or str(it.get("title") or "").strip())
        it["seo_desc"] = (str(it.get("meta_description") or "").strip()
                          or recortar(it.get("summary")) or PRESENTACIONES["intro"])
        if it["pslug"] in vistos:
            print(f'  ! Dos presentaciones con la misma dirección /presentaciones/{it["pslug"]}/: {vistos[it["pslug"]]} y {it["slug"]}')
        vistos[it["pslug"]] = it["slug"]
    # Aviso: el mismo archivo de imagen usado en dos presentaciones (p. ej. dos veces «1.jpg»)
    usos = {}
    for it in items:
        for sld in pres_slides(it):
            usos.setdefault(sld, set()).add(it["slug"])
    repetidas = sorted(k for k, v in usos.items() if len(v) > 1)
    if repetidas:
        print("  ! Imágenes compartidas por varias presentaciones (una puede haber sobrescrito a la otra): "
              + ", ".join(repetidas[:6]) + (" …" if len(repetidas) > 6 else ""))
    return items


def parrafos(texto):
    """Respeta los párrafos del resumen (líneas en blanco) sin cambiar su contenido."""
    partes = [x.strip() for x in re.split(r"\n\s*\n", str(texto or "")) if x.strip()]
    return "".join(f"<p>{esc(x)}</p>" for x in partes)


def pres_card(it):
    slides = pres_slides(it)
    portada = it.get("image") or (slides[0] if slides else "")
    img = (f'<img src="{esc(portada)}" alt="Carátula: {esc(it.get("title"))}"{wh(portada)} loading="lazy">'
           if portada else ICONO_PRES)
    tag, attrs, more = "div", "", ""
    if slides:
        tag, attrs = "a", f' href="{it["url"]}"'
    elif it.get("link"):
        tag, attrs = "a", f' href="{esc(it["link"])}" target="_blank" rel="noopener"'
    if tag == "a":
        more = '<span class="pres-more">Ver presentación <span aria-hidden="true">→</span></span>'
    etiquetas = [("pres-cat", cat_nombre(it["cat"]))] if it["cat"] else []
    if it["sector"]:
        etiquetas.append(("pres-cat pres-sec", f'Sector: {SECTOR_NAMES[it["sector"]]}' if it["sector"] == "otros"
                          else SECTOR_NAMES[it["sector"]]))
    cat = (f'<span class="pres-tags">' + "".join(f'<span class="{c}">{esc(e)}</span>' for c, e in etiquetas)
           + '</span>') if etiquetas else ""
    return f'''<li class="pres-item" data-cat="{it["cat"]}" data-sector="{it["sector"]}"><{tag} class="pres-card"{attrs}>
      <div class="pres-img">{img}</div>
      <div class="pres-txt">
        {cat}
        <h2>{esc(it.get("title"))}</h2>
        <div class="pres-sum">{parrafos(it.get("summary"))}</div>
        {more}
      </div>
    </{tag}></li>'''


def cat_nombre(c):
    return CAT_OTROS[1] if c == CAT_OTROS[0] else PRES_CAT[c]


def pf_grupo(dim, titulo, opciones):
    """Un grupo de filtros (botones en escritorio y lista desplegable en el celular)."""
    tid = f"pf-t-{dim}"
    btns = f'<button type="button" data-valor="" aria-pressed="true">Todos</button>' + "".join(
        f'<button type="button" data-valor="{v}" aria-pressed="false">{esc(n)}</button>' for v, n in opciones)
    opts = '<option value="">Todos</option>' + "".join(f'<option value="{v}">{esc(n)}</option>' for v, n in opciones)
    return f'''<div class="pf-grupo" data-dim="{dim}">
        <p class="pres-filtros-t" id="{tid}">{titulo}</p>
        <div class="pf-btns" role="group" aria-labelledby="{tid}">{btns}</div>
        <label class="pf-sel"><span>{titulo}</span><select>{opts}</select></label>
      </div>'''


def pres_filtros(items):
    """Filtros por servicio y por sector (solo en el navegador, sin direcciones nuevas). Ocultos sin JavaScript.
    Cada filtro muestra solo las opciones que tienen presentaciones; «Otros» va al final."""
    cats = [(s["slug"], PRES_CAT[s["slug"]]) for s in SERVICIOS if any(i["cat"] == s["slug"] for i in items)]
    if any(i["cat"] == CAT_OTROS[0] for i in items):
        cats.append(CAT_OTROS)
    secs = [(v, n) for v, n in SECTORES if any(i["sector"] == v for i in items)]
    grupos = ""
    if cats:
        grupos += pf_grupo("cat", "Servicio", cats)
    if secs:
        grupos += pf_grupo("sector", "Sector", secs)
    if not grupos:
        return ""
    return f'''<div class="pres-filtros" data-pres-filtros hidden>
      <div class="pf-grupos">{grupos}</div>
      <p class="pf-count" aria-live="polite" data-pf-count></p>
    </div>'''


def render_presentacion(it):
    slides = pres_slides(it)
    n = len(slides)
    figs = ""
    for i, s in enumerate(slides, 1):
        lazy = "" if i == 1 else ' loading="lazy"'
        figs += (f'<figure class="slide"><img src="{esc(s)}" alt="Diapositiva {i} de {n}: {esc(it.get("title"))}"'
                 f'{wh(s)}{lazy} draggable="false"></figure>')
    flechas = ('<button type="button" data-prev aria-label="Diapositiva anterior">←</button>'
               f'<span data-count aria-live="polite">1 / {n}</span>'
               '<button type="button" data-next aria-label="Diapositiva siguiente">→</button>') if n > 1 else ""
    # «Ampliar»: muestra la diapositiva ocupando toda la ventana (no descarga nada)
    nav = (f'<div class="slides-nav">{flechas}'
           f'<button type="button" class="slides-zoom" data-zoom aria-pressed="false" aria-label="Ampliar">'
           f'{icon("zoom")}<span>Ampliar</span></button></div>')
    body = markdown.markdown(it.get("body") or "", extensions=["extra", "sane_lists"])
    texto = f'<div class="prose pres-body">{body}</div>' if body.strip() else ""
    cat = (f'<a class="pres-cat-link" href="/servicios/{it["cat"]}/">{esc(PRES_CAT[it["cat"]])}</a>'
           if it["cat"] in SERVICE_NAMES else "")
    content = f'''
<div class="page-head pres-head">
  <div class="wrap">
    {cat}
    <h1>{esc(it.get("title"))}</h1>
    <div class="pres-sum">{parrafos(it.get("summary"))}</div>
  </div>
</div>
<section class="pres-view">
  <div class="wrap">
    <div class="slides" data-slides>
      <div class="slides-track" tabindex="0" role="region" aria-label="Diapositivas de la presentación">{figs}</div>
      {nav}
    </div>
    {texto}
    {aviso_legal("La información contenida en esta presentación")}
    <a class="back" href="/presentaciones/">← Ver todas las presentaciones</a>
  </div>
</section>'''
    render(it["url"], content, it["seo_title"], it["seo_desc"],
           nav="presentaciones", og_image=it.get("image") or slides[0], og_type="article",
           lastmod=max_fecha(it["date"]))


def build_presentaciones(items):
    cfg = PRESENTACIONES
    items = prep_presentaciones(items)
    if items:
        listing = (pres_filtros(items) + '<ul class="pres-list" data-pres-list>'
                   + "".join(pres_card(i) for i in items) + "</ul>")
    else:
        listing = empty_box(cfg["empty"])
    content = f'''
<div class="page-head pres-head">
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
    render("/presentaciones/", content, f'{cfg["h1"]} | Viple Consultores', cfg["intro"], nav="presentaciones",
           noindex=not items, lastmod=max_fecha(LISTADOS_LASTMOD, *(i["date"] for i in items)))
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
      <br><a href="/gestion-legal/" style="color:var(--navy)">Ver «¿Tu equipo odia a Legal?»</a> · <a href="/novedades/" style="color:var(--navy)">Ver novedades</a></p>
    </div>
    <div class="posts">{cards}</div>
  </div>
</section>'''


# ---------- Construcción ----------

def service_ld(slug, body):
    """Nodo Service de cada página de servicio, con el título y la descripción visibles del hero."""
    m = re.search(r'<section class="svc-hero[^"]*">.*?<h1>(.*?)</h1>\s*<p>(.*?)</p>', body, re.S)
    if not m:
        return ""
    limpio = lambda t: html.unescape(re.sub(r"<[^>]+>", "", t)).strip()
    ld = {"@context": "https://schema.org", "@type": "Service",
          "@id": f"{SITE_URL}/servicios/{slug}/#service",
          "name": limpio(m.group(1)), "description": limpio(m.group(2)),
          "url": f"{SITE_URL}/servicios/{slug}/",
          "serviceType": SERVICE_NAMES.get(slug, ""),
          "provider": {"@type": ["Organization", "LegalService"], "@id": ORG_ID,
                       "name": "Viple Consultores", "url": SITE_URL + "/"},
          "areaServed": {"@type": "Country", "name": "Perú"}}
    return f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'


def main():
    # En Windows/OneDrive alguna carpeta puede quedar bloqueada: se borra lo posible y se sobrescribe el resto
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT / "assets", OUT / "assets", dirs_exist_ok=True)
    shutil.copytree(ROOT / "admin", OUT / "admin", dirs_exist_ok=True)
    # Redirecciones 301 de Netlify (direcciones antiguas → nuevas)
    shutil.copy2(ROOT / "_redirects", OUT / "_redirects")

    ideas = load_items("notas", base=IDEAS["base"])
    novedades = load_items("novedades")
    publicadas, total_preguntas = load_preguntas()
    PUBLICADAS[:] = publicadas
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
        body = fill_services(body)
        meta["title"] = fill_services(meta.get("title", "Viple Consultores")).replace("&amp;", "&")
        # Fecha de última modificación: la guardada en la página, o la de las preguntas que muestra
        lastmod = meta.get("lastmod")
        head_extra = ""
        if url == "/":
            lastmod = max_fecha(lastmod, *(q["fecha"] for q in destacadas_portada()))
        m = re.fullmatch(r"/servicios/([a-z0-9-]+)/", url)
        if m:
            slug = m.group(1)
            lastmod = max_fecha(lastmod, *(q["fecha"] for q in publicadas if q["servicio_asociado"] == slug))
            head_extra = service_ld(slug, body)
        if not lastmod and url != "/404.html":
            print(f"  ! Sin fecha de última modificación (se omite lastmod): {url}")
        render(url, body, meta.get("title", "Viple Consultores"), meta.get("description", ""),
               nav=meta.get("nav", ""), logo=meta.get("logo", "cuadrado"),
               og_image=meta.get("og_image", "/assets/img/logo-cuadrado.png"),
               head_extra=head_extra, lastmod=lastmod)

    build_editorial(IDEAS, ideas)
    build_preguntas(publicadas)
    build_novedades(novedades)
    build_presentaciones(load_items("presentaciones"))

    urls = ""
    for u, lm in SITEMAP:
        urls += f"<url><loc>{SITE_URL}{u}</loc>" + (f"<lastmod>{lm}</lastmod>" if lm else "") + "</url>"
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>',
        encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nDisallow: /admin/\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")

    print(f"Sitio generado en _site/ - {len(SITEMAP)} paginas en el sitemap - "
          f"{len(ideas)} articulos - {len(publicadas)} de {total_preguntas} preguntas publicadas - {len(novedades)} novedades")


if __name__ == "__main__":
    main()
