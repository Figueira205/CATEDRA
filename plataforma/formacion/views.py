from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import get_object_or_404, redirect

from .models import Asistencia, ClasePage


def entrar_directo(request, page_id):
    """Registra la asistencia y redirige al enlace del directo (que nunca se publica en la página)."""
    clase = get_object_or_404(ClasePage.objects.live(), pk=page_id)
    if not clase.usuario_tiene_acceso(request.user):
        if not request.user.is_authenticated:
            return redirect_to_login(clase.url)
        messages.info(request, "Necesitas acceso a esta clase para entrar al directo.")
        return redirect(clase.url)
    if not clase.directo_abierto:
        messages.info(request, "El acceso al directo se abre 30 minutos antes del inicio.")
        return redirect(clase.url)
    if request.user.is_authenticated:
        Asistencia.objects.get_or_create(clase=clase, usuario=request.user)
    else:
        Asistencia.objects.create(clase=clase)
    return redirect(clase.enlace_directo)
