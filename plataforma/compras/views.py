import logging
import mimetypes
from pathlib import Path

import stripe
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.http import FileResponse, Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from wagtail.models import Page

from . import servicios
from .models import Compra, Producto

log = logging.getLogger(__name__)


def _producto_publicado(page_id):
    pagina = get_object_or_404(Page.objects.live().specific(), pk=page_id)
    if not isinstance(pagina, Producto):
        raise Http404
    return pagina


@login_required
@require_POST
def comprar(request, page_id):
    pagina = _producto_publicado(page_id)
    if not pagina.es_de_pago:
        return redirect(pagina.url)
    if pagina.usuario_tiene_acceso(request.user):
        messages.info(request, "Ya tienes acceso a este contenido.")
        return redirect(pagina.url)
    try:
        url = servicios.crear_sesion_pago(request.user, pagina)
    except servicios.PagosNoConfigurados:
        log.error("Intento de compra sin Stripe configurado.")
        messages.error(request, "Los pagos todavía no están disponibles. Inténtalo más adelante.")
        return redirect(pagina.url)
    except stripe.StripeError:
        log.exception("Error de Stripe al crear la sesión de pago.")
        messages.error(request, "No hemos podido iniciar el pago. Inténtalo de nuevo en unos minutos.")
        return redirect(pagina.url)
    return redirect(url, permanent=False)


@login_required
def exito(request):
    session_id = request.GET.get("session_id", "")
    compra = get_object_or_404(Compra, stripe_session_id=session_id, usuario=request.user)
    if compra.estado == Compra.Estado.PENDIENTE:
        try:
            compra = servicios.confirmar_sesion(servicios.recuperar_sesion(session_id)) or compra
        except (stripe.StripeError, servicios.PagosNoConfigurados):
            log.exception("No se pudo confirmar la sesión %s desde la página de éxito.", session_id)
    return render(request, "compras/exito.html", {"compra": compra, "pagina": compra.pagina.specific})


@csrf_exempt
@require_POST
def webhook(request):
    try:
        evento = servicios.verificar_webhook(request.body, request.headers.get("Stripe-Signature", ""))
    except (ValueError, stripe.SignatureVerificationError):
        log.warning("Webhook de Stripe con firma no válida.")
        return HttpResponseBadRequest("firma no válida")
    except servicios.PagosNoConfigurados:
        log.error("Webhook recibido sin STRIPE_WEBHOOK_SECRET configurado.")
        return HttpResponse(status=503)
    servicios.procesar_evento(evento)
    return HttpResponse(status=200)


def descargar(request, page_id):
    """Entrega el archivo de una publicación solo a quien tiene acceso."""
    pagina = _producto_publicado(page_id)
    archivo = getattr(pagina, "archivo", None)
    if not archivo:
        raise Http404
    if not pagina.usuario_tiene_acceso(request.user):
        if not request.user.is_authenticated:
            return redirect_to_login(pagina.url)
        messages.info(request, "Necesitas adquirir este contenido para descargarlo.")
        return redirect(pagina.url)
    nombre = f"{pagina.slug}{Path(archivo.name).suffix.lower()}"
    tipo, _ = mimetypes.guess_type(nombre)
    respuesta = FileResponse(archivo.open("rb"), as_attachment=True, filename=nombre, content_type=tipo or "application/octet-stream")
    respuesta["Cache-Control"] = "private, no-store"
    respuesta["X-Robots-Tag"] = "noindex"
    return respuesta
