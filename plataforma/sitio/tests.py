import shutil
import tempfile

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from biblioteca.models import BibliotecaPage

from .models import Suscriptor
from .pruebas import crear_arbol

_privado = tempfile.mkdtemp(prefix="catedra-privado-")


@override_settings(PRIVATE_MEDIA_ROOT=_privado)
class SitioTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(_privado, ignore_errors=True)

    def setUp(self):
        self.p = crear_arbol()

    def test_portada(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Libro de pago")  # bloque «Desde la Biblioteca»

    def test_cabeceras_de_seguridad(self):
        r = self.client.get("/")
        csp = r["Content-Security-Policy"]
        script_src = csp.split("script-src")[1].split(";")[0]
        self.assertIn("'self'", script_src)
        self.assertNotIn("unsafe-inline", script_src)
        self.assertEqual(r["X-Content-Type-Options"], "nosniff")
        self.assertEqual(r["X-Frame-Options"], "SAMEORIGIN")

    def test_menu_solo_secciones_marcadas(self):
        BibliotecaPage.objects.update(show_in_menus=True)
        r = self.client.get("/")
        self.assertIn(b'"label": "Biblioteca"', r.content)
        self.assertNotIn(b"Formaci\\u00f3n", r.content.split(b'id="ch-menu"')[1][:500])

    def test_buscador(self):
        r = self.client.get(reverse("buscar") + "?q=libro")
        self.assertContains(r, "Libro de pago")

    def test_indice_json(self):
        datos = self.client.get(reverse("indice_busqueda")).json()
        tipos = {d["t"]: d["type"] for d in datos}
        self.assertEqual(tipos["Libro de pago"], "publicacion")
        self.assertEqual(tipos["Clase exclusiva"], "clase")

    def test_boletin_doble_confirmacion(self):
        r = self.client.post(reverse("suscribirse"), {"email": "Lector@Correo.es", "consentimiento": "on", "volver": "/"})
        self.assertEqual(r.status_code, 302)
        sus = Suscriptor.objects.get()
        self.assertEqual(sus.email, "lector@correo.es")
        self.assertFalse(sus.confirmado)
        self.assertIn(sus.token, mail.outbox[0].body)
        self.client.get(reverse("confirmar_suscripcion", args=[sus.token]))
        sus.refresh_from_db()
        self.assertTrue(sus.confirmado)

    def test_boletin_sin_consentimiento(self):
        self.client.post(reverse("suscribirse"), {"email": "a@b.es", "volver": "/"})
        self.assertFalse(Suscriptor.objects.exists())

    def test_boletin_trampa_para_robots(self):
        self.client.post(reverse("suscribirse"), {"email": "a@b.es", "consentimiento": "on", "web": "spam"})
        self.assertFalse(Suscriptor.objects.exists())

    def test_boletin_no_redirige_fuera(self):
        r = self.client.post(reverse("suscribirse"), {"email": "a@b.es", "consentimiento": "on", "volver": "//malo.com"})
        self.assertTrue(r["Location"].startswith("/#"))

    def test_baja(self):
        sus = Suscriptor.objects.create(email="x@y.es", confirmado=True)
        self.client.post(reverse("baja_suscripcion", args=[sus.token]))
        self.assertFalse(Suscriptor.objects.exists())

    def test_robots_y_sitemap(self):
        self.assertContains(self.client.get("/robots.txt"), "Disallow: /admin/")
        self.assertEqual(self.client.get("/sitemap.xml").status_code, 200)
