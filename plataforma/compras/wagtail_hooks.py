from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.utils import timezone
from wagtail import hooks
from wagtail.admin.ui.components import Component
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.permission_policies import ModelPermissionPolicy
from wagtail.permissions import register_permission_policy

from .models import Compra


class SoloLectura(ModelPermissionPolicy):
    """Las compras solo las crea y modifica Stripe: en el panel únicamente se consultan."""

    PROHIBIDAS = {"add", "change", "delete"}

    def user_has_permission(self, user, action):
        return action not in self.PROHIBIDAS and super().user_has_permission(user, action)

    def user_has_any_permission(self, user, actions):
        return any(self.user_has_permission(user, a) for a in actions)

    def user_has_permission_for_instance(self, user, action, instance):
        return self.user_has_permission(user, action)


class CompraViewSet(ModelViewSet):
    model = Compra
    icon = "tag"
    menu_label = "Compras"
    add_to_admin_menu = True
    menu_order = 300
    inspect_view_enabled = True
    copy_view_enabled = False
    list_display = ["concepto", "usuario", "importe", "estado", "pagada_en", "creada"]
    list_filter = ["estado", "creada"]
    list_export = ["creada", "pagada_en", "concepto", "usuario", "importe", "moneda", "estado", "stripe_payment_intent"]
    export_filename = "compras-catedra"
    form_fields = ["estado"]
    inspect_view_fields = ["concepto", "pagina", "usuario", "importe", "moneda", "estado", "creada", "pagada_en",
                           "stripe_session_id", "stripe_payment_intent"]


register_permission_policy(Compra, SoloLectura(Compra))


@hooks.register("register_admin_viewset")
def registrar_compras():
    # Nombre distinto del namespace público «compras» (compras/urls.py).
    return CompraViewSet("compras_admin", url_prefix="compras")


class ResumenPanel(Component):
    """Cifras clave en la pantalla de inicio del panel (solo para quien puede ver compras)."""

    name = "resumen_catedra"
    order = 50
    template_name = "compras/admin/resumen_panel.html"

    def __init__(self, request):
        self.request = request

    def get_context_data(self, parent_context):
        from sitio.models import Suscriptor

        hace_30 = timezone.now() - timedelta(days=30)
        pagadas = Compra.objects.filter(estado=Compra.Estado.PAGADA)
        ventas_30 = pagadas.filter(pagada_en__gte=hace_30).aggregate(n=Count("id"), total=Sum("importe"))
        return {
            "ventas_30": ventas_30["n"],
            "ingresos_30": ventas_30["total"] or 0,
            "ventas_total": pagadas.count(),
            "usuarios": get_user_model().objects.filter(is_active=True, is_staff=False).count(),
            "usuarios_30": get_user_model().objects.filter(date_joined__gte=hace_30, is_staff=False).count(),
            "suscriptores": Suscriptor.objects.filter(confirmado=True).count(),
        }


@hooks.register("construct_homepage_panels")
def panel_resumen(request, panels):
    if request.user.has_perm("compras.view_compra"):
        panels.insert(0, ResumenPanel(request))
