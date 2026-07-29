# Cátedra de la Hispanidad — Sitio web «Atlas vivo»

Sitio completo, responsive y accesible para la **Cátedra de la Hispanidad** (Universidad Rey Juan Carlos), construido en HTML + CSS + JavaScript sin dependencias, y pensado para **adaptarse a WordPress**.

## Cómo verlo

Con Python instalado:

```bash
python -m http.server 8765 --directory web
```

y abrir <http://localhost:8765>. (Abrir los archivos con doble clic también funciona, pero los parámetros de URL de los filtros y del buscador requieren servidor.)

## Estructura

```
web/
├── index.html                 Portada (hero + atlas, buscador, agenda, revista…)
├── la-catedra.html            Quiénes somos, campo de estudio, misión, objetivos
├── equipo.html / persona.html Equipo con filtros · plantilla de ficha personal
├── investigacion.html         8 áreas temáticas y líneas
├── proyectos.html / proyecto.html
├── actividades.html / actividad.html   Agenda con lista + calendario · detalle con inscripción e .ics
├── publicaciones.html         Hub: convocatoria editorial, normas, comité
├── revista.html / revista-numero-01.html / publicacion.html
├── repositorio.html           Buscador + filtros + fondo bibliográfico
├── multimedia.html            Mosaico con lightbox accesible y vídeo
├── premios.html · convenios.html · contacto.html
├── buscar.html                Página de resultados (lee ?q=)
├── 404.html · aviso-legal · privacidad · cookies · accesibilidad
├── robots.txt · sitemap.xml
├── build.ps1                  Ensambla cabecera/pie desde _partials/ (equivale a get_header/get_footer)
├── _partials/                 header.html · footer.html · head-common.html
└── assets/
    ├── css/styles.css         Tokens de diseño + componentes (ver abajo)
    ├── js/data.js             CONTENIDO EDITABLE: navegación, índice de búsqueda, agenda
    ├── js/main.js             Comportamiento (menús, buscador, filtros, lightbox, calendario…)
    └── img/                   Recursos reales de /recursos (el vídeo de 400 MB se enlaza desde ../recursos)
```

## Dónde se edita cada cosa

| Quiero cambiar… | Archivo |
|---|---|
| Menús (mega menú, menú móvil) | `assets/js/data.js` → `CH_NAV` |
| Resultados del buscador global | `assets/js/data.js` → `CH_INDEX` |
| Agenda y calendario | `assets/js/data.js` → `CH_EVENTS` (fechas ISO `AAAA-MM-DD`) |
| Colores, tipografías, espaciado | `assets/css/styles.css` → bloque `:root` (tokens `--color-*`, `--text-*`, `--s-*`) |
| Cabecera o pie de todas las páginas | `_partials/header.html` / `footer.html`, después ejecutar `build.ps1`* |
| Textos de una página | El propio `.html` (sin lorem ipsum: todo el texto es real y sustituible) |

\* `build.ps1` solo afecta a páginas que aún contengan los marcadores `<!--@HEADER-->`; las ya ensambladas se editan directamente o restaurando el marcador.

**Todo lo demostrativo está señalado** con la etiqueta dorada discontinua «Contenido demostrativo / editable». No hay nombres de investigadores inventados: las fichas de persona son plantillas neutras. No se han inventado cifras, DOI, ISSN ni financiación (aparecen como «en tramitación» o «se publicará cuando exista»).

## Adaptación a WordPress

El sitio está organizado exactamente como un tema de WordPress:

1. **Tema.** `_partials/header.html` → `header.php`; `_partials/footer.html` → `footer.php`; cada página → una plantilla (`front-page.php`, `page-la-catedra.php`, `archive-proyecto.php`, `single-proyecto.php`…). `styles.css` se encola tal cual; `main.js` con `defer`.
2. **Custom Post Types** (con ACF/Pods, siguiendo los modelos del brief §16): `persona`, `area`, `proyecto`, `actividad`, `numero_revista`, `publicacion`, `premio`, `convenio`, `multimedia`, `spotlight`. Las relaciones (persona↔proyecto↔publicación↔actividad) son campos de relación bidireccionales; las páginas de detalle ya muestran esos bloques «vinculado a».
3. **Datos dinámicos.** `CH_NAV`, `CH_INDEX` y `CH_EVENTS` se generan desde WP con `wp_localize_script` (o la REST API): los menús desde `wp_nav_menu`, el índice de búsqueda desde una consulta a todos los CPT, la agenda desde el CPT `actividad`. El buscador cliente puede sustituirse por SearchWP/Relevanssi manteniendo la misma interfaz.
4. **Formularios.** Los formularios (contacto, inscripción, boletín) validan en cliente; en WP se conectan a Gravity Forms/WPForms/Contact Form 7 conservando etiquetas y mensajes de error.
5. **URLs.** Los enlaces permanentes del sitemap (`/investigacion/proyectos/[slug]`, `/revista/[numero]`…) se configuran en Ajustes → Enlaces permanentes + slugs de CPT.
6. **Rendimiento.** Servir las fuentes localmente (plugin OMGF o descarga manual), convertir las imágenes a WebP/AVIF (el HTML ya declara `width/height`, `loading="lazy"` y `fetchpriority` en el LCP) y subir el vídeo a un streaming (YouTube privado/Vimeo) en lugar del MP4 de 400 MB.
7. **Idiomas.** Estructura preparada para ES/EN (selector en cabecera): con WPML o Polylang, añadir `hreflang` y mantener al usuario en la página equivalente.

## Identidad «Atlas vivo»

- Paleta: marfil `#F4F0E7` dominante, tinta `#111`, carmín `#A62035` (acciones e identidad), azul Atlántico `#103D50` (investigación/institucional), oro `#B48A3C` solo como acento (premios, numeraciones).
- Tipografías (Google Fonts, abiertas): **Archivo** (titulares/UI), **Source Serif 4** (lectura/citas), **IBM Plex Mono** (metadatos).
- Retícula de 12 columnas (6 tableta / 4 móvil), líneas divisorias de 1 px, numeraciones editoriales, radios 0–6 px.
- Red de nodos: canvas ligero en el hero (se desactiva con `prefers-reduced-motion` y en móvil) + diagrama SVG de las 8 áreas conectado al acordeón.
- Accesibilidad: salto al contenido, foco visible, diálogos con Escape y foco gestionado, `aria-expanded/pressed/current`, áreas táctiles ≥ 44 px, formularios con errores asociados, `[hidden]` fiable, contraste AA.
