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
    "label": "Cómo mejorar el trabajo legal",
    "h1": "Cómo mejorar el trabajo legal en tu negocio",
    "intro": ("Reflexiones sobre Legal Ops, inteligencia artificial, gestión del conocimiento "
              "y nuevas formas de organizar el trabajo legal en empresas y firmas de abogados"),
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
            '<img src="/assets/img/logo-cuadrado.png" alt="Viple Consultores · Legal &amp; Compliance" '
            'width="500" height="500"></a>')


# ---------- Servicios (fuente única: content/servicios.json) ----------

SERVICIOS = json.loads((ROOT / "content" / "servicios.json").read_text(encoding="utf-8"))["servicios"]


def svc_menu():
    return "\n".join(f'              <li><a href="/servicios/{s["slug"]}/">{esc(s["name"])}</a></li>'
                     for s in SERVICIOS)


def svc_panels():
    rows = "".join(f'''<a class="svc-panel" href="/servicios/{s["slug"]}/">
        <span class="num">{i:02d}</span>
        <div class="svc-txt"><h3>{esc(s["name"])}</h3><span>{esc(s["summary"])}</span></div>
        <span class="more">Ver servicio →</span>
      </a>''' for i, s in enumerate(SERVICIOS, 1))
    return f'<div class="svc-panels">{rows}</div>'


def fill_services(text):
    text = text.replace("{{svc_panels}}", svc_panels())
    for s in SERVICIOS:
        text = text.replace("{{svc:" + s["slug"] + "}}", esc(s["name"]))
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
    <div class="eyebrow">{cfg["label"]}</div>
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
      <h2>Te ayudamos con tus dudas</h2>
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


def pres_card(it):
    destino = it.get("file") or it.get("link") or ""
    img = (f'<img src="{esc(it["image"])}" alt="" loading="lazy">' if it.get("image") else ICONO_PRES)
    ext = destino.rsplit(".", 1)[-1].lower() if it.get("file") and "." in destino else ""
    accion = {"pdf": "Ver presentación (PDF)", "ppt": "Descargar presentación", "pptx": "Descargar presentación"}.get(ext, "Ver presentación")
    tag, attrs, more = "div", "", ""
    if destino:
        tag = "a"
        attrs = f' href="{esc(destino)}" target="_blank" rel="noopener"'
        more = f'<span class="pres-more">{accion} <span aria-hidden="true">→</span></span>'
    return f'''<li><{tag} class="pres-card"{attrs}>
      <div class="pres-img">{img}</div>
      <div class="pres-txt">
        <h3>{esc(it.get("title"))}</h3>
        <p>{esc(it.get("summary"))}</p>
        {more}
      </div>
    </{tag}></li>'''


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
      <br><a href="/notas/" style="color:var(--navy)">Ver «Cómo mejorar el trabajo legal»</a> · <a href="/novedades/" style="color:var(--navy)">Ver novedades</a></p>
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
