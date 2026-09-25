import shutil
import tempfile
from datetime import timedelta

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from compras.models import Compra
from sitio.pruebas import crear_arbol, crear_usuario

from .models import Asistencia, ClasePage, Visualizacion, url_incrustada

_privado = tempfile.mkdtemp(prefix="catedra-privado-")


@override_settings(PRIVATE_MEDIA_ROOT=_privado)
class FormacionTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(_privado, ignore_errors=True)

    def setUp(self):
        self.p = crear_arbol()
        self.usuario = crear_usuario()

    def test_url_incrustada(self):
        self.assertEqual(url_incrustada("https://youtu.be/dQw4w9WgXcQ"), "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ?rel=0")
        self.assertEqual(url_incrustada("https://vimeo.com/123456"), "https://player.vimeo.com/video/123456?dnt=1")
        self.assertEqual(url_incrustada("https://ejemplo.com/video"), "")

    def test_video_de_pago_oculto_sin_compra(self):
        self.client.force_login(self.usuario)
        r = self.client.get(self.p["clase"].url)
        self.assertNotContains(r, "youtube-nocookie.com")
        self.assertFalse(Visualizacion.objects.exists())

    def test_video_visible_y_contado_con_compra(self):
        clase = self.p["clase"]
        Compra.objects.create(usuario=self.usuario, pagina=clase, concepto=clase.title, importe=clase.precio,
                              estado=Compra.Estado.PAGADA)
        self.client.force_login(self.usuario)
        r = self.client.get(clase.url)
        self.assertContains(r, "youtube-nocookie.com/embed/dQw4w9WgXcQ")
        self.assertEqual(Visualizacion.objects.filter(clase=clase, usuario=self.usuario).count(), 1)

    def test_enlace_del_directo_nunca_aparece_en_la_pagina(self):
        r = self.client.get(self.p["directo"].url)
        self.assertNotContains(r, "zoom.us")
        self.assertContains(r, reverse("formacion:entrar_directo", args=[self.p["directo"].pk]))

    def test_entrar_al_directo_registra_asistencia(self):
        self.client.force_login(self.usuario)
        url = reverse("formacion:entrar_directo", args=[self.p["directo"].pk])
        r = self.client.get(url)
        self.assertEqual(r["Location"], "https://zoom.us/j/123456")
        self.client.get(url)  # volver a entrar no duplica
        self.assertEqual(Asistencia.objects.filter(usuario=self.usuario).count(), 1)

    def test_asistencia_anonima_en_directo_abierto(self):
        url = reverse("formacion:entrar_directo", args=[self.p["directo"].pk])
        self.client.get(url)
        self.client.get(url)
        self.assertEqual(Asistencia.objects.filter(usuario__isnull=True).count(), 2)

    def test_directo_cerrado_no_redirige(self):
        ClasePage.objects.filter(pk=self.p["directo"].pk).update(fecha=timezone.now() + timedelta(days=2))
        r = self.client.get(reverse("formacion:entrar_directo", args=[self.p["directo"].pk]))
        self.assertEqual(r["Location"], self.p["directo"].url)
        self.assertFalse(Asistencia.objects.exists())

    def test_estadisticas_solo_con_permiso(self):
        self.client.force_login(self.usuario)
        self.assertNotEqual(self.client.get(reverse("estadisticas_formacion")).status_code, 200)
