from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_POST
from wagtail.models import Page

from .forms import SuscripcionForm
from .models import Suscriptor

TIPOS = {
    "publicacionpage": "publicacion", "clasepage": "clase", "actividadpage": "actividad",
    "novedadpage": "novedad", "galeriapage": "galeria",
}


def buscar(request):
    q = request.GET.get("q", "").strip()
    resultados = Page.objects.live().public().exclude(depth__lte=1).search(q) if q else Page.objects.none()
    pagina = Paginator(resultados, 20).get_page(request.GET.get("pagina"))
    return render(request, "sitio/buscar.html", {"q": q, "resultados": pagina})


@cache_page(60 * 10)
def indice_busqueda(request):
    """Índice ligero para el buscador rápido (Ctrl + K): título, tipo, URL y resumen."""
    datos = []
    for p in Page.objects.live().public().exclude(depth__lte=1).specific().iterator():
        datos.append({
            "t": p.title,
            "type": TIPOS.get(p.specific_class.__name__.lower(), "pagina"),
            "url": p.url,
            "d": (getattr(p, "resumen", "") or getattr(p, "entradilla", "") or p.search_description or "")[:160],
        })
    return JsonResponse(datos, safe=False)


@require_POST
def suscribirse(request):
    form = SuscripcionForm(request.POST)
    volver = request.POST.get("volver") or "/"
    if not volver.startswith("/") or volver.startswith("//"):
        volver = "/"
    if not form.is_valid():
        messages.error(request, "Revisa el correo y acepta la política de privacidad para suscribirte.")
        return redirect(volver + "#boletin")
    email = form.cleaned_data["email"].lower()
    sus, _ = Suscriptor.objects.get_or_create(email=email, defaults={"nombre": form.cleaned_data["nombre"]})
    if not sus.confirmado:
        enlace = settings.SITIO_URL + reverse("confirmar_suscripcion", args=[sus.token])
        send_mail(
            "Confirma tu suscripción al boletín de la Cátedra de la Hispanidad",
            render_to_string("sitio/correo_confirmar_suscripcion.txt", {"suscriptor": sus, "enlace": enlace}),
            None, [email],
        )
    # Mismo mensaje exista o no el correo: no se revela quién está suscrito.
    messages.success(request, "Te hemos enviado un correo para confirmar la suscripción.")
    return redirect(volver + "#boletin")


def confirmar_suscripcion(request, token):
    sus = get_object_or_404(Suscriptor, token=token)
    if not sus.confirmado:
        sus.confirmado = True
        sus.confirmado_en = timezone.now()
        sus.save(update_fields=["confirmado", "confirmado_en"])
    return render(request, "sitio/suscripcion.html", {"suscriptor": sus, "baja": False})


def baja_suscripcion(request, token):
    sus = get_object_or_404(Suscriptor, token=token)
    if request.method == "POST":
        sus.delete()
        return render(request, "sitio/suscripcion.html", {"baja": True, "hecho": True})
    return render(request, "sitio/suscripcion.html", {"suscriptor": sus, "baja": True})
