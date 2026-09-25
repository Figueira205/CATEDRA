from django.contrib.auth.models import Permission
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from sitio.pruebas import crear_usuario

from .models import Usuario


class UsuarioTests(TestCase):
    def test_login_por_correo_sin_nombre_de_usuario(self):
        u = Usuario.objects.create_user(email="Alguien@Ejemplo.ES", password="x")
        self.assertEqual(u.email, "Alguien@ejemplo.es")
        self.assertIsNone(Usuario.username)

    def test_contrasenas_con_argon2(self):
        u = Usuario.objects.create_user(email="a@b.es", password="clave-larga-segura-1")
        self.assertTrue(u.password.startswith("argon2"))

    def test_registro_exige_verificar_el_correo(self):
        r = self.client.post(reverse("account_signup"), {
            "email": "nuevo@catedra.test", "password1": "una-clave-muy-larga-7", "password2": "una-clave-muy-larga-7"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        r = self.client.get(reverse("mi_cuenta"))
        self.assertEqual(r.status_code, 302)  # sin verificar, no hay sesión

    def test_mi_cuenta_requiere_login(self):
        r = self.client.get(reverse("mi_cuenta"))
        self.assertIn(reverse("account_login"), r["Location"])


@override_settings(CATEDRA_2FA_OBLIGATORIO_PERSONAL=True)
class DobleFactorTests(TestCase):
    def setUp(self):
        self.profesor = crear_usuario("profe@catedra.test")
        self.profesor.user_permissions.add(Permission.objects.get(codename="access_admin"))

    def test_panel_exige_2fa(self):
        self.client.force_login(self.profesor)
        r = self.client.get("/admin/")
        self.assertEqual(r["Location"], reverse("mfa_activate_totp"))

    def test_estudiante_no_afectado_fuera_del_panel(self):
        self.client.force_login(crear_usuario())
        self.assertEqual(self.client.get(reverse("mi_cuenta")).status_code, 200)

    @override_settings(CATEDRA_2FA_OBLIGATORIO_PERSONAL=False)
    def test_desactivable_en_local(self):
        self.client.force_login(self.profesor)
        self.assertEqual(self.client.get("/admin/").status_code, 200)
