import hashlib
import hmac
import json
import shutil
import tempfile
import time
from decimal import Decimal
from unittest import mock

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase, override_settings
from django.urls import reverse

from biblioteca.models import PublicacionPage
from sitio.pruebas import crear_arbol, crear_usuario

from . import servicios
from .models import Compra

SECRETO = "whsec_prueba"
_privado = tempfile.mkdtemp(prefix="catedra-privado-")


def firmar(payload: bytes, secreto=SECRETO):
    t = int(time.time())
    firma = hmac.new(secreto.encode(), f"{t}.".encode() + payload, hashlib.sha256).hexdigest()
    return f"t={t},v1={firma}"


def evento(tipo, objeto):
    return json.dumps({"id": "evt_1", "object": "event", "type": tipo, "data": {"object": objeto}}).encode()


@override_settings(PRIVATE_MEDIA_ROOT=_privado, STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET=SECRETO,
                   SITIO_URL="http://testserver")
class BaseCompras(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(_privado, ignore_errors=True)

    def setUp(self):
        self.p = crear_arbol()
        self.libro = self.p["libro"]
        self.usuario = crear_usuario()

    def compra(self, estado=Compra.Estado.PENDIENTE, sesion="cs_test_1", usuario=None):
        return Compra.objects.create(usuario=usuario or self.usuario, pagina=self.libro, concepto=self.libro.title,
                                     importe=self.libro.precio, estado=estado, stripe_session_id=sesion)


class AccesoTests(BaseCompras):
    def test_libre_para_todos(self):
        from django.contrib.auth.models import AnonymousUser
        self.assertTrue(self.p["libre"].usuario_tiene_acceso(AnonymousUser()))

    def test_pago_sin_compra_no_da_acceso(self):
        self.assertFalse(self.libro.usuario_tiene_acceso(self.usuario))

    def test_solo_compra_pagada_da_acceso(self):
        self.compra(Compra.Estado.PENDIENTE)
        self.assertFalse(self.libro.usuario_tiene_acceso(self.usuario))
        Compra.objects.update(estado=Compra.Estado.PAGADA)
        self.assertTrue(self.libro.usuario_tiene_acceso(self.usuario))

    def test_reembolsada_pierde_acceso(self):
        self.compra(Compra.Estado.REEMBOLSADA)
        self.assertFalse(self.libro.usuario_tiene_acceso(self.usuario))

    def test_contenido_de_pago_necesita_precio(self):
        pub = PublicacionPage(title="Sin precio", acceso="pago", precio=None)
        with self.assertRaises(ValidationError):
            pub.clean()

    def test_no_puede_haber_dos_compras_pagadas_del_mismo_contenido(self):
        self.compra(Compra.Estado.PAGADA, sesion="cs_a")
        with self.assertRaises(IntegrityError):
            self.compra(Compra.Estado.PAGADA, sesion="cs_b")


class ComprarTests(BaseCompras):
    def test_anonimo_va_al_login(self):
        r = self.client.post(reverse("compras:comprar", args=[self.libro.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/cuenta/login/", r["Location"])

    def test_get_no_permitido(self):
        self.client.force_login(self.usuario)
        r = self.client.get(reverse("compras:comprar", args=[self.libro.pk]))
        self.assertEqual(r.status_code, 405)

    @mock.patch("stripe.checkout.Session.create")
    def test_crea_sesion_de_stripe_y_redirige(self, crear):
        crear.return_value = mock.Mock(id="cs_test_nueva", url="https://checkout.stripe.com/c/pay/cs_test_nueva")
        self.client.force_login(self.usuario)
        r = self.client.post(reverse("compras:comprar", args=[self.libro.pk]))
        self.assertEqual(r["Location"], "https://checkout.stripe.com/c/pay/cs_test_nueva")
        compra = Compra.objects.get()
        self.assertEqual(compra.estado, Compra.Estado.PENDIENTE)
        self.assertEqual(compra.stripe_session_id, "cs_test_nueva")
        kwargs = crear.call_args.kwargs
        self.assertEqual(kwargs["line_items"][0]["price_data"]["unit_amount"], 1250)
        self.assertEqual(kwargs["line_items"][0]["price_data"]["product_data"]["name"], "Cátedra · Libro de pago")
        self.assertEqual(kwargs["metadata"]["compra_id"], str(compra.pk))
        self.assertEqual(kwargs["customer_email"], self.usuario.email)
        self.assertTrue(kwargs["success_url"].endswith("?session_id={CHECKOUT_SESSION_ID}"))

    @mock.patch("stripe.checkout.Session.create", side_effect=__import__("stripe").APIConnectionError("sin red"))
    def test_error_de_stripe_no_deja_compra_pendiente(self, _):
        self.client.force_login(self.usuario)
        r = self.client.post(reverse("compras:comprar", args=[self.libro.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Compra.objects.get().estado, Compra.Estado.CADUCADA)

    def test_si_ya_lo_tiene_no_cobra_otra_vez(self):
        self.compra(Compra.Estado.PAGADA)
        self.client.force_login(self.usuario)
        with mock.patch("stripe.checkout.Session.create") as crear:
            self.client.post(reverse("compras:comprar", args=[self.libro.pk]))
        crear.assert_not_called()

    @override_settings(STRIPE_SECRET_KEY="")
    def test_sin_stripe_configurado_avisa(self):
        self.client.force_login(self.usuario)
        r = self.client.post(reverse("compras:comprar", args=[self.libro.pk]), follow=True)
        self.assertContains(r, "Los pagos todavía no están disponibles")


class WebhookTests(BaseCompras):
    url = reverse("compras:webhook")

    def enviar(self, payload, firma=None):
        return self.client.post(self.url, data=payload, content_type="application/json",
                                HTTP_STRIPE_SIGNATURE=firma or firmar(payload))

    def test_firma_invalida_rechazada(self):
        self.compra()
        payload = evento("checkout.session.completed", {"id": "cs_test_1", "payment_status": "paid"})
        r = self.enviar(payload, firma=firmar(payload, secreto="otro"))
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Compra.objects.get().estado, Compra.Estado.PENDIENTE)

    def test_pago_completado_marca_pagada(self):
        self.compra()
        payload = evento("checkout.session.completed",
                         {"id": "cs_test_1", "payment_status": "paid", "payment_intent": "pi_1", "status": "complete"})
        self.assertEqual(self.enviar(payload).status_code, 200)
        compra = Compra.objects.get()
        self.assertEqual(compra.estado, Compra.Estado.PAGADA)
        self.assertEqual(compra.stripe_payment_intent, "pi_1")
        self.assertIsNotNone(compra.pagada_en)

    def test_es_idempotente(self):
        self.compra()
        payload = evento("checkout.session.completed", {"id": "cs_test_1", "payment_status": "paid", "payment_intent": "pi_1"})
        self.enviar(payload)
        primera = Compra.objects.get().pagada_en
        self.enviar(payload)
        self.assertEqual(Compra.objects.get().pagada_en, primera)

    def test_pago_pendiente_no_da_acceso(self):
        self.compra()
        self.enviar(evento("checkout.session.completed", {"id": "cs_test_1", "payment_status": "unpaid"}))
        self.assertEqual(Compra.objects.get().estado, Compra.Estado.PENDIENTE)

    def test_pago_asincrono_confirmado(self):
        self.compra()
        self.enviar(evento("checkout.session.async_payment_succeeded", {"id": "cs_test_1", "payment_status": "paid"}))
        self.assertEqual(Compra.objects.get().estado, Compra.Estado.PAGADA)

    def test_sesion_caducada(self):
        self.compra()
        self.enviar(evento("checkout.session.expired", {"id": "cs_test_1", "status": "expired", "payment_status": "unpaid"}))
        self.assertEqual(Compra.objects.get().estado, Compra.Estado.CADUCADA)

    def test_sesion_de_otro_negocio_se_ignora(self):
        r = self.enviar(evento("checkout.session.completed", {"id": "cs_de_otra_empresa", "payment_status": "paid"}))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Compra.objects.exists())

    def test_reembolso_total_quita_acceso(self):
        c = self.compra(Compra.Estado.PAGADA)
        Compra.objects.filter(pk=c.pk).update(stripe_payment_intent="pi_9")
        self.enviar(evento("charge.refunded", {"id": "ch_1", "payment_intent": "pi_9", "refunded": True}))
        self.assertEqual(Compra.objects.get().estado, Compra.Estado.REEMBOLSADA)

    def test_reembolso_parcial_mantiene_acceso(self):
        c = self.compra(Compra.Estado.PAGADA)
        Compra.objects.filter(pk=c.pk).update(stripe_payment_intent="pi_9")
        self.enviar(evento("charge.refunded", {"id": "ch_1", "payment_intent": "pi_9", "refunded": False}))
        self.assertEqual(Compra.objects.get().estado, Compra.Estado.PAGADA)

    def test_pago_duplicado_no_rompe(self):
        self.compra(Compra.Estado.PAGADA, sesion="cs_a")
        self.compra(Compra.Estado.PENDIENTE, sesion="cs_b")
        r = self.enviar(evento("checkout.session.completed", {"id": "cs_b", "payment_status": "paid", "payment_intent": "pi_b"}))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Compra.objects.get(stripe_session_id="cs_b").estado, Compra.Estado.PENDIENTE)
        self.assertEqual(Compra.objects.get(stripe_session_id="cs_b").stripe_payment_intent, "pi_b")

    @override_settings(STRIPE_WEBHOOK_SECRET="")
    def test_sin_secreto_configurado(self):
        self.assertEqual(self.enviar(evento("checkout.session.completed", {"id": "x"})).status_code, 503)


class ExitoTests(BaseCompras):
    @mock.patch("compras.servicios.recuperar_sesion")
    def test_confirma_al_volver_de_stripe(self, recuperar):
        self.compra()
        recuperar.return_value = {"id": "cs_test_1", "payment_status": "paid", "payment_intent": "pi_1"}
        self.client.force_login(self.usuario)
        r = self.client.get(reverse("compras:exito") + "?session_id=cs_test_1")
        self.assertContains(r, "Ya es tuyo")
        self.assertEqual(Compra.objects.get().estado, Compra.Estado.PAGADA)

    def test_no_se_ve_la_compra_de_otro(self):
        self.compra(usuario=crear_usuario("otra@catedra.test"))
        self.client.force_login(self.usuario)
        r = self.client.get(reverse("compras:exito") + "?session_id=cs_test_1")
        self.assertEqual(r.status_code, 404)


class DescargaTests(BaseCompras):
    def url(self, pagina):
        return reverse("compras:descargar", args=[pagina.pk])

    def test_libre_se_descarga_sin_cuenta(self):
        r = self.client.get(self.url(self.p["libre"]))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Cache-Control"], "private, no-store")

    def test_de_pago_anonimo_va_al_login(self):
        r = self.client.get(self.url(self.libro))
        self.assertIn("/cuenta/login/", r["Location"])

    def test_de_pago_sin_compra_no_descarga(self):
        self.client.force_login(self.usuario)
        r = self.client.get(self.url(self.libro))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r["Location"], self.libro.url)

    def test_de_pago_con_compra_descarga(self):
        self.compra(Compra.Estado.PAGADA)
        self.client.force_login(self.usuario)
        r = self.client.get(self.url(self.libro))
        self.assertEqual(r.status_code, 200)
        self.assertIn('filename="libro-de-pago.pdf"', r["Content-Disposition"])
        self.assertEqual(b"".join(r.streaming_content), b"%PDF-1.4 contenido de prueba")

    def test_el_archivo_no_tiene_url_publica(self):
        self.assertEqual(self.libro.archivo.url, "#archivo-privado")
        self.assertNotIn("/media/", self.client.get(self.libro.url).content.decode())

    def test_pagina_despublicada_no_descarga(self):
        self.compra(Compra.Estado.PAGADA)
        self.libro.unpublish()
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(self.url(self.libro)).status_code, 404)


class PaginaProductoTests(BaseCompras):
    def test_anonimo_ve_precio_y_acceder(self):
        r = self.client.get(self.libro.url)
        self.assertContains(r, "12,50 €")
        self.assertContains(r, "Acceder para adquirir")
        self.assertNotContains(r, reverse("compras:descargar", args=[self.libro.pk]))

    def test_con_compra_ve_descargar(self):
        self.compra(Compra.Estado.PAGADA)
        self.client.force_login(self.usuario)
        r = self.client.get(self.libro.url)
        self.assertContains(r, reverse("compras:descargar", args=[self.libro.pk]))

    def test_mi_cuenta_lista_lo_comprado(self):
        self.compra(Compra.Estado.PAGADA)
        self.client.force_login(self.usuario)
        r = self.client.get(reverse("mi_cuenta"))
        self.assertContains(r, "Libro de pago")
        self.assertContains(r, "12,50 €")


class ServiciosTests(BaseCompras):
    def test_importe_en_centimos_sin_errores_de_redondeo(self):
        self.libro.precio = Decimal("19.99")
        with mock.patch("stripe.checkout.Session.create") as crear:
            crear.return_value = mock.Mock(id="cs_x", url="https://checkout.stripe.com/x")
            servicios.crear_sesion_pago(self.usuario, self.libro)
        self.assertEqual(crear.call_args.kwargs["line_items"][0]["price_data"]["unit_amount"], 1999)
