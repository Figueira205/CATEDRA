"""Utilidades compartidas por los tests: árbol de páginas mínimo y usuarios."""
from datetime import timedelta
from decimal import Decimal

from allauth.account.models import EmailAddress
from django.core.files.base import ContentFile
from django.utils import timezone
from wagtail.models import Page, Site

from biblioteca.models import BibliotecaPage, PublicacionPage
from cuentas.models import Usuario
from formacion.models import ClasePage, FormacionPage
from sitio.models import HomePage


def crear_arbol():
    """Portada + Biblioteca con un libro de pago + Formación con una clase de pago y un directo abierto."""
    raiz = Page.get_first_root_node()
    inicio = HomePage(title="Inicio", slug="inicio-pruebas")
    raiz.add_child(instance=inicio)
    Site.objects.all().delete()
    Site.objects.create(hostname="testserver", port=80, root_page=inicio, is_default_site=True)

    biblioteca = BibliotecaPage(title="Biblioteca", slug="biblioteca")
    inicio.add_child(instance=biblioteca)
    libro = PublicacionPage(title="Libro de pago", slug="libro-de-pago", acceso="pago", precio=Decimal("12.50"))
    libro.archivo.save("libro.pdf", ContentFile(b"%PDF-1.4 contenido de prueba"), save=False)
    biblioteca.add_child(instance=libro)
    libre = PublicacionPage(title="Artículo libre", slug="articulo-libre", acceso="libre")
    libre.archivo.save("articulo.pdf", ContentFile(b"%PDF-1.4 libre"), save=False)
    biblioteca.add_child(instance=libre)

    formacion = FormacionPage(title="Formación", slug="formacion-pruebas")
    inicio.add_child(instance=formacion)
    clase = ClasePage(title="Clase exclusiva", slug="clase-exclusiva", acceso="pago", precio=Decimal("30.00"),
                      video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    formacion.add_child(instance=clase)
    directo = ClasePage(title="Directo abierto", slug="directo-abierto", acceso="libre", modalidad="directo",
                        fecha=timezone.now() - timedelta(minutes=5), duracion_minutos=60,
                        enlace_directo="https://zoom.us/j/123456")
    formacion.add_child(instance=directo)
    return {"inicio": inicio, "libro": libro, "libre": libre, "clase": clase, "directo": directo}


def crear_usuario(email="estudiante@catedra.test", **extra):
    usuario = Usuario.objects.create_user(email=email, password="clave-de-prueba-123", **extra)
    EmailAddress.objects.create(user=usuario, email=email, verified=True, primary=True)
    return usuario
