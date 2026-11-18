"""Verifica el JSON-LD y los metadatos del sitio generado en _site/ (después de python build.py).

Uso:  python verificar_schema.py            → revisa todas las páginas
      python verificar_schema.py --antes DIR → además compara el HTML visible con otra copia de _site

Comprueba en cada página: un solo bloque JSON-LD con JSON válido y @graph; que todo @id referenciado
exista en el mismo @graph; que no haya valores vacíos, «undefined», «null» ni etiquetas HTML; que el
nombre y la descripción del nodo de página coincidan con <title> y la meta description; y que las fechas
de preguntas y artículos coincidan con las fechas visibles (<time>). No lo ejecuta Netlify.
"""
import html
import json
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent / "_site"
errores, n = [], 0


def recorrer(v, ruta, encontrado):
    if isinstance(v, dict):
        for k, x in v.items():
            recorrer(x, f"{ruta}.{k}", encontrado)
    elif isinstance(v, list):
        for i, x in enumerate(v):
            recorrer(x, f"{ruta}[{i}]", encontrado)
    else:
        if v is None or (isinstance(v, str) and (not v.strip() or v.strip() in ("undefined", "null", "None")
                                                 or re.search(r"<[a-zA-Z/][^>]*>", v) or "{{" in v)):
            encontrado.append(f"{ruta} = {v!r}")


def ids_y_refs(v, defs, refs):
    if isinstance(v, dict):
        if "@id" in v:
            (refs if set(v) == {"@id"} else defs).add(v["@id"])
        for x in v.values():
            ids_y_refs(x, defs, refs)
    elif isinstance(v, list):
        for x in v:
            ids_y_refs(x, defs, refs)


def visible(h):
    h = re.sub(r"<head>.*?</head>", "", h, flags=re.S)
    h = re.sub(r'<script type="application/ld\+json">.*?</script>', "", h, flags=re.S)
    return re.sub(r"\s+", " ", h)


for f in sorted(SITE.rglob("*.html")):
    rel = "/" + f.relative_to(SITE).as_posix()
    if rel.startswith("/admin/"):
        continue
    n += 1
    h = f.read_text(encoding="utf-8")
    bloques = re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
    if len(bloques) != 1:
        errores.append(f"{rel}: {len(bloques)} bloques JSON-LD (debe haber 1)")
        continue
    try:
        data = json.loads(bloques[0])
    except Exception as e:
        errores.append(f"{rel}: JSON inválido ({e})")
        continue
    if "@graph" not in data:
        errores.append(f"{rel}: sin @graph")
        continue
    malos = []
    recorrer(data, "", malos)
    errores += [f"{rel}: valor no válido {m}" for m in malos]
    defs, refs = set(), set()
    ids_y_refs(data, defs, refs)
    errores += [f"{rel}: @id referenciado sin definir: {r}" for r in sorted(refs - defs)]
    tipos = {"Organization", "Person", "WebSite"}
    presentes = {t for g in data["@graph"] for t in ([g["@type"]] if isinstance(g["@type"], str) else g["@type"])}
    errores += [f"{rel}: falta nodo global {t}" for t in tipos - presentes]
    pagina = next((g for g in data["@graph"] if str(g.get("@id", "")).endswith("#webpage")), None)
    if not pagina:
        errores.append(f"{rel}: sin nodo de página (#webpage)")
        continue
    title = html.unescape(re.search(r"<title>(.*?)</title>", h, re.S).group(1))
    desc = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', h).group(1))
    if pagina.get("name") != title:
        errores.append(f"{rel}: name ≠ <title> ({pagina.get('name')!r} / {title!r})")
    if desc and pagina.get("description") != desc:
        errores.append(f"{rel}: description ≠ meta description")
    canon = re.search(r'<link rel="canonical" href="([^"]+)"', h).group(1)
    if pagina.get("url") != canon:
        errores.append(f"{rel}: url ≠ canonical ({pagina.get('url')} / {canon})")
    tiempos = set(re.findall(r'<time datetime="([^"]+)"', visible(h)))
    for g in data["@graph"]:
        for k in ("datePublished", "dateModified"):
            if k in g and g[k] not in tiempos:
                errores.append(f"{rel}: {g.get('@type')}.{k} = {g[k]} no coincide con ninguna fecha visible {sorted(tiempos)}")
    for k in ("og:image:width", "og:image:alt"):
        if f'property="{k}"' not in h:
            errores.append(f"{rel}: falta {k}")
    if 'name="twitter:card"' not in h:
        errores.append(f"{rel}: falta twitter:card")

if "--antes" in sys.argv:
    antes = Path(sys.argv[sys.argv.index("--antes") + 1])
    for f in sorted(SITE.rglob("*.html")):
        rel = f.relative_to(SITE)
        if rel.as_posix().startswith("admin/"):
            continue
        a = antes / rel
        if not a.exists():
            errores.append(f"/{rel.as_posix()}: no existe en la copia anterior")
        elif visible(a.read_text(encoding="utf-8")) != visible(f.read_text(encoding="utf-8")):
            errores.append(f"/{rel.as_posix()}: CAMBIÓ el HTML visible")
    print("Comparación del HTML visible con", antes)

print(f"{n} páginas revisadas.")
print("\n".join(errores) if errores else "Sin errores.")
sys.exit(1 if errores else 0)
