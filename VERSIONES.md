# Versiones del sitio vipleconsultores.com

## 1. Versión Una Puerta (publicada hasta noviembre de 2026; antes llamada «Versión Acuarela»)

### Respaldo

| Elemento | Valor |
|---|---|
| Etiqueta git anotada | `version-una-puerta` (en GitHub) |
| Rama de respaldo | `version-una-puerta` (en GitHub; **no se modifica nunca**) |
| Commit | `f7a79fa` (último de `main` antes de la Versión Dos Puertas) |
| Deploy de Netlify en producción | `6af78faf3d2059f73fa26854` (13 nov 2026, construido desde `9be7058`; `f7a79fa` solo añadió una pregunta sin respuesta, con `[skip netlify]`, que no se ve en la web) |
| Enlace permanente al deploy | https://6af78faf3d2059f73fa26854--resplendent-sfogliatella-e4a742.netlify.app |

### Home Page (/), bloques en orden

1. **Hero**: H1 «Asesoría legal alineada con la operación real de tu negocio» + «Parte de tu equipo», ilustración en acuarela (`/assets/img/portada-ilustracion.jpg`) y dos tarjetas de ruta: «Quiero explorar los servicios» (/servicios/) y «Quiero saber qué hacer en mi situación» (/preguntas/).
2. **«Lo que podemos hacer por ti»** con el subtítulo «Nuestros servicios»: 7 tarjetas de servicio (desde `content/servicios.json`).
3. **«¿Tienes preguntas?»**: hasta 5 preguntas destacadas y publicadas (se oculta si no hay).
4. **Novedades** (`#novedades`, se oculta si no hay ninguna).
5. **«Hola, soy Gabriel»** (`#quien-soy`): 4 párrafos, LinkedIn, foto con nombre y cargo, «Formación» (4 puntos) y botones «Conversemos» y «Ver servicios».

### Menú principal

Inicio · Nuestros servicios ▾ (Ver todos los servicios + 7 servicios) · ¿Tienes preguntas? · ¿Tu equipo odia a Legal? · Criterios de autoridades ▾ (Ver todos + 3 subsecciones) · Presentaciones especiales · **Conversemos** (botón).

### Footer

Logo y texto · «Sitio»: Inicio, Nuestros servicios, ¿Tienes preguntas?, ¿Tu equipo odia a Legal?, Criterios de autoridades, Presentaciones especiales, Novedades (solo si hay), Quién soy (/#quien-soy), Conversemos · «Contacto»: correo, teléfono, LinkedIn.

### Páginas

/, /servicios/, las 7 páginas /servicios/<servicio>/ (estructura-empresarial, constitucion-asociaciones, protegemos-tu-inversion, contratos, proteccion-de-datos, reclamos-y-denuncias, herramientas-legales), /contacto/, /preguntas/ y cada pregunta publicada, /gestion-legal/, /presentaciones/ y cada presentación, /criterios-de-autoridades/ y sus 3 subsecciones, /404.html. Redirecciones 301: /quien-soy/ → /#quien-soy, /novedades/ → /#novedades, /dudas/ → /preguntas/, /notas/ → /gestion-legal/.

## 2. Procedimiento «Vuelve a la Versión Una Puerta»

**Opción rápida (sin gastar créditos de build, reversible):**
Netlify → proyecto `resplendent-sfogliatella-e4a742` → **Deploys** → abrir el deploy `6af78faf3d2059f73fa26854` (o el último deploy de producción anterior al merge de la Versión Dos Puertas) → **Publish deploy**. Ojo: Netlify deja la publicación automática bloqueada en ese deploy («locked») hasta que se pulse *Unlock* / *Start auto publishing*.

**Opción definitiva en Git:**
1. En `main`, revertir el merge de `version-dos-puertas`:
   `git revert -m 1 <commit-del-merge>` → revisar en local → push a `main` (un despliegue, 15 créditos, con confirmación).
2. O restaurar el contenido desde la etiqueta:
   `git checkout main && git checkout version-una-puerta -- .` (y quitar los archivos nuevos que no existían en la etiqueta), commit y push.
3. **Nunca** usar `git push --force` sobre `main` sin confirmación expresa de Gabriel.

## 3. Versión Dos Puertas

Rama `version-dos-puertas` (creada desde `main` con este archivo). Publicada el 18 nov 2026: merge `351a56e` en `main`, deploy de Netlify `6afce96dbea49a0bcf5af1ca`. Para volver a la Versión Una Puerta en Git: `git revert -m 1 351a56e`.

### Home Page (/), bloques en orden

1. **Franja celeste a todo el ancho**, pegada al menú: H1 «Asesoría legal clara para tu negocio y para tus decisiones personales» y, a la derecha, la acuarela `portada-equipo.jpg` al alto de la franja y pegada al borde derecho. (`portada-ilustracion.jpg`, la acuarela de la Versión Una Puerta, se conserva en el repo.)
2. **Dos «puertas»**: **Empresas** (azul oscuro, /empresas/, «Para operar, contratar o crecer») y **Personas** (azul medio, /personas/, «Antes de firmar, invertir o reclamar»), con etiquetas y enlace.
3. **«Hola, soy Gabriel»** + «y trabajaré directamente contigo» (`#quien-soy`): párrafos 1 y 4 centrados en la altura de la foto; bajo la foto, nombre, cargo y LinkedIn; «Formación» completa a la altura del nombre; sin botones.
4. **«¿Tienes preguntas?»**: 4 preguntas elegidas (`{{faq:slug,…}}`).
5. Novedades (solo si hay alguna publicada).
6. **Cierre**: «¿Qué estás evaluando?» + «Conversemos» (WhatsApp solo en /contacto/).

### /empresas/ y /personas/

- Franja azul con el H1 y la acuarela a la derecha (`empresas-equipo.jpg`, `personas-cercania.jpg`).
- /empresas/: «¿En qué momento está tu empresa?» (3 tarjetas), franja verde punteada hacia Herramientas legales, «Cómo trabajo contigo» (3 pasos), preguntas y cierre.
- /personas/: H1 «Decisiones personales con acompañamiento legal», «¿Cómo te puedo ayudar?» (4 tarjetas), «Cómo trabajo contigo», preguntas y cierre.
- /personas/contratos/ y /personas/reclamos/ usan la plantilla de servicio con «Cómo trabajo contigo» (mismos 3 pasos que /personas/).

### Menú principal

Inicio · **Empresas ▾** (Ver todo + 5 servicios) · **Personas ▾** (Ver todo, Contratos, Reclamos como consumidor, Protegemos tu inversión, Constitución de asociaciones) · ¿Tienes preguntas? · Criterios de autoridades ▾ · Presentaciones especiales · **Conversemos**. Sin «Quién soy» (está en la portada).

### Footer

Inicio, Empresas, Personas, ¿Tienes preguntas?, Criterios de autoridades, Presentaciones especiales, Novedades (si hay), Quién soy (/#quien-soy), Conversemos.

### Otros cambios

- Nuevas páginas en el sitemap con JSON-LD Service vinculado a `#organization`; nodo Person de Gabriel (`founder`) en la portada.
- /servicios/: dos grupos, «Para empresas» y «Para personas» (lista `GRUPOS` en build.py); «Anterior / Siguiente» de cada servicio recorre solo su grupo.
- Todo el sitio en primera persona singular (servicios, contacto, resúmenes y cinco respuestas de «¿Tienes preguntas?»). Los nombres «Estructuramos tu negocio» y «Protegemos tu inversión» se mantienen.
- «¿Tu equipo odia a Legal?» pasó a llamarse «¿Legal frena tu operación?» (/gestion-legal/); por ahora sin enlace en el menú ni en el pie.
- En computadora los párrafos van justificados; en el celular, a la izquierda.
- CSS nuevo al final de `site.css`, bloques «VERSIÓN DOS PUERTAS» y ajustes posteriores.
