from allauth.mfa.utils import is_mfa_enabled
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect


class DobleFactorObligatorioMiddleware:
    """Exige verificación en dos pasos (2FA) al personal antes de entrar al panel.

    Afecta a quien puede entrar al panel (profesores y administración); un
    estudiante no tiene ese permiso. Se puede desactivar en local con
    CATEDRA_2FA_OBLIGATORIO_PERSONAL=False.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if (
            settings.CATEDRA_2FA_OBLIGATORIO_PERSONAL
            and request.path.startswith("/admin/")
            and user is not None
            and user.is_authenticated
            and user.has_perm("wagtailadmin.access_admin")
            and not is_mfa_enabled(user)
        ):
            messages.warning(
                request,
                "Para entrar al panel de gestión debes activar primero la verificación en dos pasos.",
            )
            return redirect("mfa_activate_totp")
        return self.get_response(request)
