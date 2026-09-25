from django.conf import settings
from wagtail.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from cuentas.views import mi_cuenta
from sitio import views as sitio_views

urlpatterns = [
    path("admin/", include(wagtailadmin_urls)),
    path("documentos/", include(wagtaildocs_urls)),
    path("cuenta/", include("allauth.urls")),
    path("mi-cuenta/", mi_cuenta, name="mi_cuenta"),
    path("compras/", include("compras.urls")),
    path("formacion/", include("formacion.urls")),
    path("buscar/", sitio_views.buscar, name="buscar"),
    path("buscar/indice.json", sitio_views.indice_busqueda, name="indice_busqueda"),
    path("boletin/alta/", sitio_views.suscribirse, name="suscribirse"),
    path("boletin/confirmar/<str:token>/", sitio_views.confirmar_suscripcion, name="confirmar_suscripcion"),
    path("boletin/baja/<str:token>/", sitio_views.baja_suscripcion, name="baja_suscripcion"),
    path("sitemap.xml", sitemap),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Wagtail sirve el resto de URLs (páginas). Debe ir siempre al final.
urlpatterns += [path("", include(wagtail_urls))]
