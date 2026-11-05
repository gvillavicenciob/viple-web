"""
Construye el sitio de Viple Consultores en la carpeta _site/.

- Envuelve cada página de src/pages/ con la plantilla común src/layout.html
  (encabezado, menú y pie de página).
- Genera las páginas de Notas y Novedades a partir de los artículos guardados
  por el panel de administración (/admin) en content/notas y content/novedades.

Netlify ejecuta este archivo automáticamente en cada publicación.
Para probarlo en tu computadora:  python build.py
"""
import html
import json
import re
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "_site"
SITE_URL = "https://vipleconsultores.com"
DEFAULT_AUTHOR = "Gabriel Villavicencio Bedoya"

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

COLLECTIONS = {
    "notas": {
        "nav": "notas",
        "eyebrow": "Notas",
        "h1": "Notas y artículos",
        "intro": "Análisis y reflexiones prácticas sobre temas legales para empresas.",
        "item_label": "Nota",
        "empty": "Todavía no hay notas publicadas. Vuelve pronto.",
    },
    "novedades": {
        "nav": "novedades",
        "eyebrow": "Novedades",
        "h1": "Novedades normativas y asuntos de interés",
        "intro": "Nuevas normas, cambios regulatorios y temas de actualidad relevantes para tu empresa.",
        "item_label": "Novedad",
        "empty": "Todavía no hay novedades publicadas. Vuelve pronto.",
    },
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


def brand(logo):
    if logo == "ninguno":
        return '<a class="brand none" href="/" tabindex="-1" aria-hidden="true"></a>'
    return ('<a class="brand" href="/" aria-label="Viple Consultores – Inicio">'
            '<img src="/assets/img/logo-cuadrado.png" alt="Viple Consultores · Legal &amp; Compliance" '
            'width="500" height="500"></a>')


def render(url, content, title, description, nav="", logo="cuadrado", og_image="/assets/img/logo-cuadrado.png"):
    page = LAYOUT
    for key, val in {
        "{{title}}": esc(title),
        "{{description}}": esc(description),
        "{{url}}": url,
        "{{og_image}}": og_image,
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


# ---------- Artículos (Notas / Novedades) ----------

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
        items.append(data)
    items.sort(key=lambda d: (d["date"], d["slug"]), reverse=True)
    return items


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


def build_collection(name, items):
    cfg = COLLECTIONS[name]
    filters = ""
    if name == "novedades":
        cats = sorted({i.get("category") for i in items if i.get("category")})
        if len(cats) > 1:
            filters = ('<div class="filters" role="group" aria-label="Filtrar por categoría">'
                       '<button data-cat="todas" aria-pressed="true">Todas</button>'
                       + "".join(f'<button data-cat="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in cats)
                       + "</div>")
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
        tags = item.get("tags") or []
        tags_html = ('<div class="meta" style="margin-top:28px">'
                     + "".join(f'<span class="pill" style="background:var(--sage)">{esc(t)}</span>' for t in tags)
                     + "</div>") if tags else ""
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
    {tags_html}
    <div class="author-line">{photo}<div><strong>{esc(author)}</strong>Viple Consultores · Legal &amp; Compliance</div></div>
    <a class="back" href="/{name}/">← Ver todas las {cfg["eyebrow"].lower()}</a>
  </article>
</section>'''
        render(item["url"], content, f'{item.get("title")} | Viple Consultores',
               item.get("summary") or cfg["intro"], nav=cfg["nav"],
               og_image=item.get("image") or "/assets/img/logo-cuadrado.png")


def latest_block(all_items):
    if not all_items:
        return ""
    cards = "".join(card(i) for i in all_items[:3])
    return f'''<section style="background:var(--sage-light)">
  <div class="wrap">
    <div class="section-head reveal">
      <h2>Notas y novedades</h2>
      <p>Lo último publicado: análisis prácticos, nuevas normas y asuntos de interés para tu empresa.
      <br><a href="/notas/" style="color:var(--navy)">Ver notas</a> · <a href="/novedades/" style="color:var(--navy)">Ver novedades</a></p>
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

    collections = {name: load_items(name) for name in COLLECTIONS}
    everything = sorted(collections["notas"] + collections["novedades"],
                        key=lambda d: d["date"], reverse=True)

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

    for name, items in collections.items():
        build_collection(name, items)

    urls = "".join(f"<url><loc>{SITE_URL}{u}</loc></url>" for u in SITEMAP)
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>',
        encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nDisallow: /admin/\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")

    print(f"Sitio generado en _site/ · {len(SITEMAP)} páginas · "
          f"{len(collections['notas'])} notas · {len(collections['novedades'])} novedades")


if __name__ == "__main__":
    main()
