# Cómo publicar y administrar vipleconsultores.com

## Qué hay en esta carpeta

| Carpeta / archivo | Para qué sirve |
|---|---|
| `src/pages/` | El texto de cada página (inicio, servicios, quién soy, contacto). Se puede editar a mano. |
| `src/layout.html` | Encabezado, menú y pie de página comunes a todas las páginas. |
| `assets/` | Estilos, logos, foto e imágenes subidas desde el panel. |
| `admin/` | El panel de administración (`/admin`). |
| `content/notas`, `content/dudas`, `content/novedades` | Lo que crees desde el panel en «Ideas y análisis», «Te ayudamos con tus dudas» y «Novedades» (se llenan solos). |
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
3. Elige **Ideas y análisis**, **Te ayudamos con tus dudas** o **Novedades** → **Nueva**. Llena los campos y pulsa **Publicar**.
4. En 1–2 minutos el artículo aparece en el sitio.
   Para editar o borrar, abre el artículo en el panel y usa **Publicar** o **Borrar entrada**.

## Cambios a mano después (textos de páginas)

1. En GitHub, abre el archivo (por ejemplo `src/pages/contacto.html`).
2. Ícono del lápiz ✏️ → cambia el texto → **Commit changes**.
3. Netlify publica el cambio solo, en 1–2 minutos.

Ya no tienes que arrastrar carpetas a Netlify: todo cambio en GitHub se publica automáticamente.
