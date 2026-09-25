from datetime import timedelta

from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils import timezone
from django.views.generic import TemplateView
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.views.generic.base import WagtailAdminTemplateMixin

from .models import ClasePage

PERMISO = "formacion.view_asistencia"


class _ConMigas(WagtailAdminTemplateMixin):
    """Añade el título de la vista a las migas de pan (cabecera del panel)."""

    def get_breadcrumbs_items(self):
        return self.breadcrumbs_items + [{"url": "", "label": self.get_page_title()}]


class EstadisticasView(_ConMigas, TemplateView):
    """Clases más vistas y asistencia a directos. Las visitas por país/región están en Umami."""

    page_title = "Estadísticas de Formación"
    header_icon = "view"
    template_name = "formacion/admin/estadisticas.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm(PERMISO):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hace_30 = timezone.now() - timedelta(days=30)
        ctx["clases"] = (
            ClasePage.objects.annotate(
                vistas=Count("visualizaciones", distinct=True),
                vistas_30=Count("visualizaciones", filter=Q(visualizaciones__fecha__gte=hace_30), distinct=True),
                personas=Count("visualizaciones__usuario", distinct=True),
                asistentes=Count("asistencias", distinct=True),
            ).order_by("-vistas", "-asistentes", "title")
        )
        return ctx


class AsistentesView(_ConMigas, TemplateView):
    header_icon = "group"
    template_name = "formacion/admin/asistentes.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm(PERMISO):
            raise PermissionDenied
        self.clase = get_object_or_404(ClasePage, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_page_title(self):
        return f"Asistentes · {self.clase.title}"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["clase"] = self.clase
        ctx["asistencias"] = self.clase.asistencias.select_related("usuario").order_by("fecha")
        ctx["anonimas"] = self.clase.asistencias.filter(usuario__isnull=True).count()
        return ctx


@hooks.register("register_admin_urls")
def urls_estadisticas():
    return [
        path("estadisticas-formacion/", EstadisticasView.as_view(), name="estadisticas_formacion"),
        path("estadisticas-formacion/<int:pk>/asistentes/", AsistentesView.as_view(), name="asistentes_clase"),
    ]


class MenuEstadisticas(MenuItem):
    def is_shown(self, request):
        return request.user.has_perm(PERMISO)


@hooks.register("register_admin_menu_item")
def menu_estadisticas():
    return MenuEstadisticas("Estadísticas", reverse("estadisticas_formacion"), icon_name="view", order=320)


@hooks.register("register_permissions")
def permisos_estadisticas():
    return Permission.objects.filter(content_type__app_label="formacion", codename__in=["view_asistencia", "view_visualizacion"])
