from django.conf import settings
from wagtail.models import Site


#: Sub-apartados fijos para secciones cuyo contenido no sale completo del
#: árbol de páginas (anclas dentro de la misma página, o enlaces a otras
#: páginas reales del sitio que no están pensadas como hijas en el árbol).
#: Si el texto empieza por «#» se añade detrás de la URL de la sección
#: (ancla); si empieza por «/» se usa tal cual (enlace a otra página). Si en
#: el futuro alguna de estas páginas pasa a tener hijas reales marcadas
#: «Mostrar en menús», ese slug puede quitarse de aquí y volverá a
#: generarse solo. La Cátedra se quitó a propósito (2026-10-06, pedido del
#: usuario): al ser todo una misma página, no quería desplegable ahí.
SUBMENU_ANCLAS = {
    "actividades": [
        ["Agenda completa", ""],
        ["Próximas actividades", "#proximas"],
        ["Vista de calendario", "#calendario"],
        ["Actividades celebradas", "#celebradas"],
    ],
    "biblioteca": [
        ["Últimas publicaciones", ""],
        ["Revista de la Cátedra", "?tipo=revista"],
        ["Contenido digital (clases)", "/formacion/"],
        ["Galería", "/galeria/"],
    ],
}


def _menu(request):
    """Menú principal a partir del árbol de páginas.

    Aparecen las hijas de la portada con «Mostrar en menús» marcado; su
    desplegable, las nietas marcadas igual. Así los editores gestionan el
    menú desde el panel, sin tocar código. Algunas secciones (La Cátedra,
    Actividades) no tienen hijas reales porque su contenido vive en una
    sola página con anclas: para esas, SUBMENU_ANCLAS aporta el desplegable.
    """
    site = Site.find_for_request(request)
    if site is None:
        return []
    menu = []
    for seccion in site.root_page.get_children().live().in_menu().specific():
        hijas = seccion.get_children().live().in_menu()[:8]
        entrada = {"label": seccion.title, "url": seccion.url}
        if hijas:
            entrada["items"] = [["Ver todo", seccion.url]] + [[h.title, h.url] for h in hijas]
        elif seccion.slug in SUBMENU_ANCLAS:
            entrada["items"] = [
                [texto, destino if destino.startswith("/") else seccion.url + destino]
                for texto, destino in SUBMENU_ANCLAS[seccion.slug]
            ]
        menu.append(entrada)
    return menu


PAGINAS_LEGALES = ["aviso-legal", "privacidad", "cookies", "accesibilidad"]


def _legales(request):
    site = Site.find_for_request(request)
    if site is None:
        return []
    paginas = {p.slug: p for p in site.root_page.get_descendants().live().filter(slug__in=PAGINAS_LEGALES)}
    return [paginas[s] for s in PAGINAS_LEGALES if s in paginas]


def sitio(request):
    return {
        "menu_principal": _menu(request),
        "paginas_legales": _legales(request),
        "UMAMI_SCRIPT_URL": settings.UMAMI_SCRIPT_URL,
        "UMAMI_WEBSITE_ID": settings.UMAMI_WEBSITE_ID,
    }
