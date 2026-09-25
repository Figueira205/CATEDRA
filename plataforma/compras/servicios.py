"""Integración con Stripe.

Flujo:
1. `crear_sesion_pago` crea una Compra «pendiente» y una sesión de Stripe
   Checkout. El estudiante paga en la página de Stripe: los datos de la
   tarjeta nunca pasan por nuestro servidor.
2. Stripe avisa por webhook (firmado) y `confirmar_sesion` marca la compra
   como pagada. La página de «pago realizado» también llama a
   `confirmar_sesion` para no depender del retraso del webhook. Es
   idempotente: se puede llamar varias veces sin efectos duplicados.
"""
import logging

import stripe
from django.conf import settings
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone

from .models import Compra

log = logging.getLogger(__name__)


class PagosNoConfigurados(Exception):
    pass


def _stripe():
    if not settings.STRIPE_SECRET_KEY:
        raise PagosNoConfigurados("Falta STRIPE_SECRET_KEY en la configuración.")
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


def crear_sesion_pago(usuario, pagina):
    """Devuelve la URL de Stripe Checkout para comprar `pagina` (una página Producto)."""
    s = _stripe()
    compra = Compra.objects.create(
        usuario=usuario, pagina=pagina, concepto=pagina.title[:255],
        importe=pagina.precio, moneda=settings.STRIPE_MONEDA,
    )
    metadatos = {
        "negocio": "catedra",
        "compra_id": str(compra.pk),
        "pagina_id": str(pagina.pk),
        "usuario_id": str(usuario.pk),
    }
    exito = settings.SITIO_URL + reverse("compras:exito") + "?session_id={CHECKOUT_SESSION_ID}"
    try:
        sesion = _crear_checkout(s, usuario, pagina, compra, metadatos, exito)
    except Exception:
        compra.estado = Compra.Estado.CADUCADA
        compra.save(update_fields=["estado", "actualizada"])
        raise
    compra.stripe_session_id = sesion.id
    compra.save(update_fields=["stripe_session_id", "actualizada"])
    return sesion.url


def _crear_checkout(s, usuario, pagina, compra, metadatos, exito):
    return s.checkout.Session.create(
        mode="payment",
        locale="es",
        customer_email=usuario.email,
        client_reference_id=str(compra.pk),
        line_items=[{
            "quantity": 1,
            "price_data": {
                "currency": settings.STRIPE_MONEDA,
                "unit_amount": int(pagina.precio * 100),
                "product_data": {"name": f"{settings.STRIPE_PREFIJO_PRODUCTO} · {pagina.title}"[:250]},
            },
        }],
        metadata=metadatos,
        payment_intent_data={"metadata": metadatos, "description": f"{settings.STRIPE_PREFIJO_PRODUCTO} · {pagina.title}"[:250]},
        invoice_creation={"enabled": True},  # Stripe genera la factura y la envía al comprador
        success_url=exito,
        cancel_url=settings.SITIO_URL + pagina.url,
        idempotency_key=f"catedra-compra-{compra.pk}",
    )


def _a_dict(obj):
    """Los objetos de stripe-python ≥ 12 no son diccionarios: se convierten aquí."""
    return obj.to_dict() if hasattr(obj, "to_dict") else obj


def recuperar_sesion(session_id):
    return _a_dict(_stripe().checkout.Session.retrieve(session_id))


def confirmar_sesion(sesion):
    """Aplica el estado de una sesión de Checkout a su Compra. Devuelve la Compra o None."""
    sesion = _a_dict(sesion)
    compra = Compra.objects.filter(stripe_session_id=sesion["id"]).first()
    if compra is None:
        # Sesiones de otros negocios de la empresa comparten cuenta de Stripe: se ignoran.
        log.info("Sesión de Stripe %s sin compra asociada; se ignora.", sesion["id"])
        return None

    if sesion.get("payment_status") == "paid" and compra.estado in (Compra.Estado.PENDIENTE, Compra.Estado.CADUCADA):
        compra.estado = Compra.Estado.PAGADA
        compra.pagada_en = timezone.now()
        compra.stripe_payment_intent = sesion.get("payment_intent") or ""
        try:
            with transaction.atomic():
                compra.save(update_fields=["estado", "pagada_en", "stripe_payment_intent", "actualizada"])
        except IntegrityError:
            # Ya tenía otra compra pagada del mismo contenido (pagó dos veces).
            # Se deja constancia para revisarlo y, si procede, reembolsar.
            log.warning("Pago duplicado: compra %s (usuario %s, contenido %s).", compra.pk, compra.usuario_id, compra.pagina_id)
            Compra.objects.filter(pk=compra.pk).update(stripe_payment_intent=compra.stripe_payment_intent)
            compra.refresh_from_db()
    elif sesion.get("status") == "expired" and compra.estado == Compra.Estado.PENDIENTE:
        compra.estado = Compra.Estado.CADUCADA
        compra.save(update_fields=["estado", "actualizada"])
    return compra


def procesar_evento(evento):
    """Procesa un evento de webhook ya verificado."""
    evento = _a_dict(evento)
    tipo = evento["type"]
    objeto = evento["data"]["object"]
    if tipo in ("checkout.session.completed", "checkout.session.async_payment_succeeded", "checkout.session.expired"):
        confirmar_sesion(objeto)
    elif tipo == "charge.refunded":
        intento = objeto.get("payment_intent")
        if intento and objeto.get("refunded"):  # reembolso total
            n = Compra.objects.filter(stripe_payment_intent=intento, estado=Compra.Estado.PAGADA).update(
                estado=Compra.Estado.REEMBOLSADA, actualizada=timezone.now(),
            )
            if n:
                log.info("Compra con pago %s marcada como reembolsada.", intento)


def verificar_webhook(payload, firma):
    """Comprueba la firma de Stripe. Lanza ValueError / SignatureVerificationError si no es válida."""
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise PagosNoConfigurados("Falta STRIPE_WEBHOOK_SECRET en la configuración.")
    return stripe.Webhook.construct_event(payload, firma, settings.STRIPE_WEBHOOK_SECRET)
