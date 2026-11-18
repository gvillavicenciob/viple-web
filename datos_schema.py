"""Datos globales de schema.org (JSON-LD) e imagen para redes sociales de vipleconsultores.com.

Fuente única: build.py incluye estos tres nodos (organización, Gabriel y sitio web) en el @graph de
TODAS las páginas. Cambia aquí cualquier dato de la organización o de Gabriel; no los copies en plantillas.
Regla: solo datos que existen y se ven en la web (sin precios, horarios, reseñas ni perfiles inventados).
"""

SITE_URL = "https://vipleconsultores.com"
ORG_ID = SITE_URL + "/#organization"
PERSONA_ID = SITE_URL + "/#gabriel"
WEBSITE_ID = SITE_URL + "/#website"
IDIOMA = "es-PE"

ORGANIZACION = {
    "@type": ["Organization", "LegalService"],
    "@id": ORG_ID,
    "name": "Viple Consultores",
    "alternateName": "Viple Consultores · Legal & Compliance",
    "url": SITE_URL + "/",
    "logo": SITE_URL + "/assets/img/logo-cuadrado.png",
    "image": SITE_URL + "/assets/img/logo-cuadrado.png",
    "description": ("Asesoría legal en Lima para pequeñas y medianas empresas y personas: contratos, estructura "
                    "societaria, protección de datos personales, prácticas comerciales y reclamos."),
    "email": "gabriel@vipleconsultores.com",
    "telephone": "+51 907 498 580",
    "address": {"@type": "PostalAddress", "addressLocality": "Lima", "addressCountry": "PE"},
    "areaServed": [{"@type": "City", "name": "Lima"}, {"@type": "Country", "name": "Perú"}],
    "knowsAbout": ["Protección de datos personales", "Ley 29733 de Protección de Datos Personales",
                   "Derecho societario", "Contratos comerciales", "Protección al consumidor",
                   "Prácticas comerciales", "Constitución de asociaciones civiles", "Gestión legal para empresas"],
    "founder": {"@id": PERSONA_ID},
    "contactPoint": {"@type": "ContactPoint", "contactType": "customer service",
                     "email": "gabriel@vipleconsultores.com", "telephone": "+51907498580",
                     "availableLanguage": ["es"]},
    # Perfiles oficiales. Cuando exista el perfil de Google Business, agrega aquí su URL
    # (por ejemplo "https://maps.google.com/?cid=…" o el enlace «Compartir» del perfil).
    "sameAs": ["https://www.linkedin.com/company/viple-consultores/"],
}

PERSONA = {
    "@type": "Person",
    "@id": PERSONA_ID,
    "name": "Gabriel Villavicencio Bedoya",
    "jobTitle": "Fundador de Viple Consultores",
    "description": "Abogado en Perú",  # firma visible en cada respuesta de «¿Tienes preguntas?»
    "url": SITE_URL + "/#quien-soy",
    "image": SITE_URL + "/assets/img/gabriel.jpg",
    "worksFor": {"@id": ORG_ID},
    "alumniOf": [{"@type": "CollegeOrUniversity", "name": "Universidad de Lima"},
                 {"@type": "CollegeOrUniversity", "name": "Georgetown University Law Center"}],
    "hasCredential": [
        {"@type": "EducationalOccupationalCredential", "credentialCategory": "degree",
         "name": "Maestría en Leyes (LL.M.)",
         "recognizedBy": {"@type": "CollegeOrUniversity", "name": "Georgetown University Law Center"}},
        {"@type": "EducationalOccupationalCredential", "credentialCategory": "certification",
         "name": "Legal Project Practitioner",
         "recognizedBy": {"@type": "Organization", "name": "International Institute of Legal Project Management"}},
    ],
    "knowsAbout": ["Protección de datos personales", "Derecho corporativo", "Contratos", "Protección al consumidor",
                   "Legal design", "Gestión de proyectos legales"],
    "sameAs": ["https://www.linkedin.com/in/gabriel-villavicencio-bedoya/"],
}

SITIO_WEB = {
    "@type": "WebSite",
    "@id": WEBSITE_ID,
    "name": "Viple Consultores",
    "url": SITE_URL + "/",
    "inLanguage": IDIOMA,
    "publisher": {"@id": ORG_ID},
}

NODOS_GLOBALES = [ORGANIZACION, PERSONA, SITIO_WEB]

# Imagen para redes sociales (og:image) cuando la página no define una propia.
# Cuando tengas la imagen de 1200×630, súbela (p. ej. /assets/img/social-viple.jpg) y cambia solo "src":
# el ancho y el alto se leen del archivo al construir el sitio.
IMAGEN_SOCIAL = {
    "src": "/assets/img/logo-cuadrado.png",
    "alt": "Viple Consultores · Legal & Compliance",
}

# Resumen de /llms.txt (texto literal)
LLMS_RESUMEN = "Asesoría legal en Lima para pequeñas y medianas empresas y personas. Parte de tu equipo."
