# Cómo publicar y administrar vipleconsultores.com

## Qué hay en esta carpeta

| Carpeta / archivo | Para qué sirve |
|---|---|
| `src/pages/` | El texto de cada página (inicio, servicios, quién soy, contacto). Se puede editar a mano. |
| `src/layout.html` | Encabezado, menú y pie de página comunes a todas las páginas. |
| `assets/` | Estilos, logos, foto e imágenes subidas desde el panel. |
| `admin/` | El panel de administración (`/admin`). |
| `content/preguntas`, `content/notas`, `content/novedades`, `content/presentaciones` | Lo que crees desde el panel en «¿Tienes preguntas?» (/preguntas/), «¿Tu equipo odia a Legal?» (/gestion-legal/), «Novedades» y «Presentaciones especiales» (se llenan solos). |
| `_redirects` | Redirecciones 301 de Netlify (por ejemplo /dudas/ → /preguntas/ y /notas/ → /gestion-legal/). Se copia a `_site/` en cada build. |
| `content/servicios.json` | Nombres y descripciones breves de los seis servicios (menú, portada y /servicios/). |
| `build.py`, `netlify.toml`, `requirements.txt` | Instrucciones para que Netlify arme el sitio. No hace falta tocarlos. |
| `_site/` | El sitio ya armado, generado automáticamente. **No subirlo a GitHub.** |

## ¿Por qué hace falta GitHub?

Cuando guardas un artículo en `/admin`, el panel necesita un lugar donde guardarlo
para que Netlify vuelva a publicar el sitio con ese artículo. Ese lugar es un
repositorio de GitHub (gratuito). Con arrastrar la carpeta a Netlify, el sitio se ve,
pero el panel no puede guardar nada.

## Paso a paso (una sola vez, ~20 minutos)

### 1. Crea una cuenta en GitHub
1. Entra a https://github.com/signup y crea una cuenta gratuita. Anota tu **nombre de usuario**.

### 2. Pon tu usuario en la configuración del panel
1. Abre `admin/config.yml` con el Bloc de notas o VS Code.
2. Cambia `TU-USUARIO-GITHUB` por tu nombre de usuario. Ejemplo: `repo: gabrielvb/viple-web`
3. Guarda.

### 3. Crea el repositorio y sube los archivos
1. En GitHub, botón **+** (arriba a la derecha) → **New repository**.
2. Nombre: `viple-web`. Elige **Private**. No marques ninguna casilla. **Create repository**.
3. En la página siguiente, haz clic en **uploading an existing file**.
4. Abre la carpeta `viple-web` en tu computadora, selecciona **todo menos la carpeta `_site`**
   y arrástralo a la página de GitHub.
5. Abajo, **Commit changes**.

### 4. Conecta Netlify con GitHub
1. En https://app.netlify.com abre tu sitio.
2. **Site configuration** → **Build & deploy** → **Continuous deployment** → **Link repository**.
3. Elige **GitHub**, autoriza el acceso y selecciona `viple-web`.
4. Revisa que diga: Branch `main`, Build command `pip install -r requirements.txt && python3 build.py`,
   Publish directory `_site` (se llenan solos gracias a `netlify.toml`). **Deploy**.
5. Espera 1–2 minutos y revisa https://vipleconsultores.com. Tu dominio no cambia.

### 5. Activa el inicio de sesión del panel
1. En GitHub: foto de perfil → **Settings** → **Developer settings** → **OAuth Apps** → **New OAuth App**.
   - Application name: `Viple CMS`
   - Homepage URL: `https://vipleconsultores.com`
   - Authorization callback URL: `https://api.netlify.com/auth/done`
   - **Register application**.
2. Copia el **Client ID**. Luego **Generate a new client secret** y copia el secreto.
3. En Netlify: **Site configuration** → **Access & security** → **OAuth** →
   **Install provider** → **GitHub** → pega Client ID y Client Secret → **Install**.

### 6. Úsalo
1. Entra a https://vipleconsultores.com/admin
2. **Iniciar sesión con GitHub**.
3. Elige **¿Tu equipo odia a Legal?**, **¿Tienes preguntas?** o **Novedades** → **Nueva**. Llena los campos, pulsa **Guardar**, revisa la vista previa y luego **Publicar → Publicar ahora**.
4. En 1–2 minutos el artículo aparece en el sitio.
   Para editar o borrar, abre el artículo en el panel y usa **Publicar** o **Borrar entrada**.

## Cambios a mano después (textos de páginas)

1. En GitHub, abre el archivo (por ejemplo `src/pages/contacto.html`).
2. Ícono del lápiz ✏️ → cambia el texto → **Commit changes**.
3. Netlify publica el cambio solo, en 1–2 minutos.

Ya no tienes que arrastrar carpetas a Netlify: todo cambio en GitHub se publica automáticamente.

## «¿Tienes preguntas?» desde el panel

Cada pregunta es una entrada de la colección **¿Tienes preguntas?** (`content/preguntas/<slug>.json`). Es la fuente única: de ahí salen el índice /preguntas/ (acordeón por servicio), la página de cada respuesta (/preguntas/<slug>/), la lista de la portada y las «Preguntas relacionadas» de cada servicio.

| Campo | Para qué sirve |
|---|---|
| Pregunta | Título grande (H1) de la página; se muestra completa. |
| Dirección (slug) | La página será /preguntas/<slug>/. No cambiarla después de publicar. |
| Servicio asociado | Grupo del acordeón y página de servicio donde aparece. |
| Respuesta | Párrafos, listas y enlaces (se puede pegar desde Word). |
| Título SEO / Descripción SEO | Pestaña del navegador y Google (~60 y ~155 caracteres). |
| Publicada | Solo las publicadas **y completas** aparecen en la web. |
| Destacada en la portada | La portada muestra hasta 5 destacadas **y** publicadas (destacar no publica). |
| Orden dentro del servicio / Orden en la portada | Orden de menor a mayor. |
| Fecha de actualización | Fecha real del último cambio de la respuesta; se ve en la página y va al sitemap. |

**Publicar una respuesta**
1. Abre la pregunta (las 14 iniciales ya existen como borradores, sin respuesta).
2. Escribe o pega la **Respuesta**, completa **Título SEO**, **Descripción SEO** y **Fecha de actualización**.
3. Marca **Publicada** y pulsa **Guardar**: se genera una vista previa gratuita. Revísala.
4. **Publicar → Publicar ahora**: Netlify reconstruye el sitio (un build, 15 créditos) y la pregunta aparece en su página, en el índice, en su servicio y, si está destacada, en la portada.

Si una pregunta está marcada como publicada pero le falta la respuesta, un dato SEO o la fecha, la web **no** la muestra (el build lo avisa en el registro de Netlify).

**Noindex automático**: /preguntas/, /gestion-legal/, /novedades/ y /presentaciones/ llevan `noindex` y quedan fuera del sitemap mientras no tengan nada publicado. Se retira solo en el build que publica el primer contenido.

**Cambiar el nombre o la descripción de un servicio**: entra a **Nuestros servicios**. El cambio se aplica a la vez en el menú, la portada, /servicios/ y la página del servicio.

**Fecha de los cambios hechos a mano**: si cambias el texto de una página de `src/pages/`, actualiza también `"lastmod"` (AAAA-MM-DD) en su primera línea. Esa fecha va al sitemap; el build nunca usa su propia fecha.

## «Presentaciones especiales» desde el panel

Las presentaciones se muestran como diapositivas en imagen dentro de la web, con botones para avanzar y retroceder. No se ofrece ningún archivo para descargar. Cada una tiene su página en /presentaciones/<slug>/ con su propio título SEO, metadescripción y canonical.

1. Exporta las diapositivas como JPG (PowerPoint: **Archivo → Exportar → Cambiar el tipo de archivo → JPEG**; Canva: **Compartir → Descargar → JPG**).
2. **Renombra las imágenes** con un nombre propio de la presentación (`inmobiliarias-01.jpg`, `inmobiliarias-02.jpg`…). Todas se guardan en la misma carpeta: si dos presentaciones usan `1.jpg`, una reemplaza a la otra. El build avisa si detecta imágenes compartidas.
3. En `/admin` abre **Presentaciones especiales → Nueva Presentación**.
4. **Título visible (H1)** y **Resumen (tarjeta y encabezado)**. Haz clic en **Dirección (slug)**: se propone a partir del título (o pulsa **Generar desde el título**); puedes acortarla. Después de guardar no cambia aunque cambies el título.
5. **Categoría (servicio)**: alimenta los filtros del catálogo (solo se muestran las categorías con presentaciones; los filtros no crean páginas nuevas).
6. **Diapositivas**: **Add diapositiva** y sube cada imagen en orden. Opcional, pero recomendado: **Contenido de la presentación en texto** (los puntos principales de las diapositivas, unas 150–300 palabras, sin repetir el resumen; Google no lee las imágenes) e **Imagen de portada** (se ve completa, en 16:9).
7. **Título SEO** (se propone el título visible; ~50–60 caracteres) y **Metadescripción** (~140–160). Los contadores son orientativos. Vacíos: se usan el título visible y el inicio del resumen.
8. Pulsa **Guardar**. Queda como borrador: no se publica (ver la sección siguiente).

Presentaciones antiguas sin slug: su dirección se forma con el nombre del archivo sin tildes (no cambia con el título).

## Flujo editorial: revisar antes de publicar (sin gastar créditos)

El panel está en modo editorial. **Guardar** no publica nada: crea una rama y un pull request en GitHub, y Netlify genera una vista previa gratuita (deploy preview). Solo **Publicar → Publicar ahora** lleva el cambio a la web y hace un despliegue a producción (15 créditos del plan Free).

1. Guarda la entrada. Arriba aparece **Estado: Borrador**.
2. Espera 1–3 minutos y pulsa **Ver vista previa** (o revisa *Deploys* en Netlify). La dirección es `https://deploy-preview-<número>--resplendent-sfogliatella-e4a742.netlify.app`.
3. Si algo no te gusta, corrige y vuelve a **Guardar**: la vista previa se actualiza sin costo.
4. Cuando esté bien, cambia el estado a **Listo** y pulsa **Publicar → Publicar ahora**.
5. Para publicar varias entradas con un solo despliegue: en Netlify pon *Build settings → Build status → Stopped builds*, publica todo desde el panel, vuelve a activar las compilaciones y pulsa *Deploys → Trigger deploy → Deploy site*.

## Ver la web en tu computadora (sin Netlify)

En PowerShell, desde esta carpeta:

```
python build.py
python -m http.server 8000 --directory _site
```

Abre http://localhost:8000/. Después de cada cambio vuelve a correr `python build.py` y recarga el navegador.
