from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect

from .models import Asistencia, ClasePage, Visualizacion


def video_embed(request, page_id):
    """Entrega el enlace del vídeo grabado solo si hay acceso, por fetch (no va en el HTML servido).

    Así «Ver código fuente» nunca muestra el enlace a quien no ha pagado, y
    cada entrega queda registrada igual que una visualización real.
    """
    clase = get_object_or_404(ClasePage.objects.live(), pk=page_id)
    if not clase.usuario_tiene_acceso(request.user):
        return JsonResponse({"error": "sin_acceso"}, status=403)
    if not clase.video_incrustado:
        return JsonResponse({"error": "sin_video"}, status=404)
    Visualizacion.objects.create(clase=clase, usuario=request.user if request.user.is_authenticated else None)
    return JsonResponse({"embed_url": clase.video_incrustado})


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
