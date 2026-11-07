"""
Construye el sitio de Viple Consultores en la carpeta _site/.

- Envuelve cada página de src/pages/ con la plantilla común src/layout.html
  (encabezado, menú y pie de página).
- Genera las secciones «Ideas y análisis» (content/notas), «Te ayudamos con
  tus dudas» (content/dudas) y
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
    "label": "Ideas y análisis",
    "h1": "Ideas para repensar cómo trabajamos en lo legal",
    "intro": ("Reflexiones sobre Legal Ops, inteligencia artificial, gestión del conocimiento "
              "y nuevas formas de organizar el trabajo legal en empresas y firmas de abogados"),
    "empty": "Muy pronto publicaremos los primeros artículos.",
    "nav": "notas",
    "featured_label": "Artículo destacado",
    "more": "Leer artículo →",
    "related": "Otros artículos",
}

# Sección «Te ayudamos con tus dudas» (se guarda en content/dudas, mismo formato editorial)
DUDAS = {
    "name": "dudas",
    "label": "Te ayudamos con tus dudas",
    "h1": "Respuestas claras a las dudas legales de tu negocio",
    "intro": "Explicamos en lenguaje sencillo temas legales frecuentes en la operación diaria de las empresas",
    "empty": "Muy pronto publicaremos las primeras respuestas.",
    "nav": "dudas",
    "featured_label": "Destacado",
    "more": "Leer respuesta →",
    "related": "Otras dudas",
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


def brand(logo):
    if logo == "ninguno":
        return '<a class="brand none" href="/" tabindex="-1" aria-hidden="true"></a>'
    return ('<a class="brand" href="/" aria-label="Viple Consultores – Inicio">'
            '<img src="/assets/img/logo-cuadrado.png" alt="Viple Consultores · Legal &amp; Compliance" '
            'width="500" height="500"></a>')


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


# ---------- Bloque «lo último» del inicio ----------

def latest_block(all_items):
    if not all_items:
        return ""
    cards = "".join(card(i) for i in all_items[:3])
    return f'''<section style="background:var(--sage-light)">
  <div class="wrap">
    <div class="section-head reveal">
      <h2>Ideas, análisis y novedades</h2>
      <p>Lo último publicado: reflexiones prácticas, nuevas normas y asuntos de interés para tu empresa.
      <br><a href="/notas/" style="color:var(--navy)">Ver ideas y análisis</a> · <a href="/novedades/" style="color:var(--navy)">Ver novedades</a></p>
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
    dudas = load_items("dudas")
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
        render(url, body, meta.get("title", "Viple Consultores"), meta.get("description", ""),
               nav=meta.get("nav", ""), logo=meta.get("logo", "cuadrado"),
               og_image=meta.get("og_image", "/assets/img/logo-cuadrado.png"))

    build_editorial(IDEAS, ideas)
    build_editorial(DUDAS, dudas)
    build_novedades(novedades)

    urls = "".join(f"<url><loc>{SITE_URL}{u}</loc></url>" for u in SITEMAP)
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>',
        encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nDisallow: /admin/\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")

    print(f"Sitio generado en _site/ · {len(SITEMAP)} páginas · "
          f"{len(ideas)} ideas y análisis · {len(dudas)} dudas · {len(novedades)} novedades")


if __name__ == "__main__":
    main()
