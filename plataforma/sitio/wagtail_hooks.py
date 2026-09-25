from wagtail import hooks
from wagtail.admin.viewsets.model import ModelViewSet

from .models import Suscriptor


class SuscriptorViewSet(ModelViewSet):
    model = Suscriptor
    icon = "mail"
    menu_label = "Boletín"
    add_to_admin_menu = True
    menu_order = 310
    copy_view_enabled = False
    list_display = ["email", "nombre", "confirmado", "creado"]
    list_filter = ["confirmado"]
    search_fields = ["email", "nombre"]
    list_export = ["email", "nombre", "confirmado", "creado", "confirmado_en"]
    export_filename = "suscriptores-boletin"
    form_fields = ["email", "nombre", "confirmado"]


@hooks.register("register_admin_viewset")
def registrar_suscriptores():
    return SuscriptorViewSet("boletin")
