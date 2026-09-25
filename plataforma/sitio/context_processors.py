from django.conf import settings
from wagtail.models import Site


def _menu(request):
    """Menú principal a partir del árbol de páginas.

    Aparecen las hijas de la portada con «Mostrar en menús» marcado; su
    desplegable, las nietas marcadas igual. Así los editores gestionan el
    menú desde el panel, sin tocar código.
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
