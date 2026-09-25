"""Monta el sitio inicial: árbol de páginas, grupos de permisos y contenido real de la web estática.

Uso:  python manage.py preparar_sitio [--web RUTA]

Es idempotente: si la portada ya existe, no toca las páginas (solo revisa los grupos).
Las secciones sin contenido todavía (Biblioteca, Formación, Novedades) se crean
ocultas del menú: basta con marcar «Mostrar en menús» en el panel cuando estén listas.
"""
import uuid
from pathlib import Path

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.images import get_image_model
from wagtail.models import Page, Site

from biblioteca.models import BibliotecaPage
from formacion.models import FormacionPage
from sitio.models import (
    ActividadesPage, CampoContacto, ContactoPage, GaleriaPage, HomePage, NovedadesPage, PaginaSimple,
)

ETIQUETAS_PERMITIDAS = {"p", "h2", "h3", "h4", "ul", "ol", "li", "a", "strong", "b", "em", "i", "br"}


def html_limpio(nodos):
    """Convierte nodos HTML en texto enriquecido de Wagtail (solo etiquetas básicas)."""
    partes = []
    for nodo in nodos:
        if getattr(nodo, "name", None) is None:
            continue
        if nodo.select_one(".tag--demo") or "tag--demo" in (nodo.get("class") or []):
            continue  # etiquetas «contenido demostrativo» de la maqueta
        copia = BeautifulSoup(str(nodo), "html.parser")
        for etiqueta in copia.find_all(True):
            if etiqueta.name not in ETIQUETAS_PERMITIDAS:
                etiqueta.unwrap()
            else:
                href = etiqueta.get("href") if etiqueta.name == "a" else None
                etiqueta.attrs = {}
                if href and not href.endswith(".html") and "#" not in href:
                    etiqueta["href"] = href
                elif etiqueta.name == "a":
                    etiqueta.unwrap()
        partes.append(str(copia).strip())
    return "\n".join(p for p in partes if p)


def bloque_texto(html):
    return {"type": "texto", "value": html, "id": str(uuid.uuid4())}


def bloque_titulo(texto):
    return {"type": "titulo", "value": texto, "id": str(uuid.uuid4())}


class Command(BaseCommand):
    help = "Crea la estructura inicial del sitio a partir de la web estática."

    def add_arguments(self, parser):
        parser.add_argument("--web", default=str(Path(settings.BASE_DIR).parent / "web"),
                            help="Carpeta de la web estática (por defecto ../web).")

    def handle(self, *args, **opts):
        self.web = Path(opts["web"])
        with transaction.atomic():
            self.grupos()
            if HomePage.objects.exists():
                self.stdout.write("La portada ya existe: no se modifican las páginas.")
                return
            self.paginas()
        self.stdout.write(self.style.SUCCESS("Sitio preparado."))

    # ------------------------------------------------------------ utilidades
    def sopa(self, nombre):
        ruta = self.web / nombre
        if not ruta.exists():
            self.stdout.write(self.style.WARNING(f"No se encuentra {ruta}; se omite su contenido."))
            return None
        return BeautifulSoup(ruta.read_text(encoding="utf-8"), "html.parser")

    def imagen(self, nombre, titulo):
        Image = get_image_model()
        existente = Image.objects.filter(title=titulo).first()
        if existente:
            return existente
        ruta = self.web / "assets" / "img" / nombre
        if not ruta.exists():
            return None
        with ruta.open("rb") as f:
            img = Image(title=titulo)
            img.file.save(nombre, ImageFile(f, name=nombre), save=False)
            img.save()
        return img

    # ------------------------------------------------------------ grupos
    def grupos(self):
        """Wagtail crea «Editors» y «Moderators»: se adaptan a la Cátedra.

        - Colaboradores: redactan y proponen; un editor aprueba y publica.
        - Editores: redactan, publican y ven estadísticas de Formación.
        """
        for viejo, nuevo in (("Editors", "Colaboradores"), ("Moderators", "Editores")):
            Group.objects.filter(name=viejo).update(name=nuevo)
        editores, _ = Group.objects.get_or_create(name="Editores")
        editores.permissions.add(*Permission.objects.filter(
            content_type__app_label="formacion", codename__in=["view_asistencia", "view_visualizacion"]))
        Group.objects.get_or_create(name="Colaboradores")

    # ------------------------------------------------------------ páginas
    def paginas(self):
        raiz = Page.get_first_root_node()
        # Wagtail trae una página de bienvenida por defecto: se sustituye.
        bienvenida = Page.objects.filter(depth=2, content_type__model="page").first()
        if bienvenida:
            bienvenida.slug = "bienvenida-wagtail"
            bienvenida.save_revision().publish()

        inicio = self.portada()
        raiz.add_child(instance=inicio)
        inicio.save_revision().publish()
        Site.objects.update_or_create(is_default_site=True, defaults={
            "hostname": "localhost", "port": 80, "root_page": inicio, "site_name": "Cátedra de la Hispanidad"})
        if bienvenida:
            bienvenida.delete()

        def hija(pagina, menu=True, padre=inicio):
            pagina.show_in_menus = menu
            padre.add_child(instance=pagina)
            pagina.save_revision().publish()
            return pagina

        hija(self.la_catedra())
        hija(ActividadesPage(title="Actividades", slug="actividades",
                             entradilla="Seminarios, conferencias, jornadas y la Cátedra de octubre. Acceso libre."))
        hija(BibliotecaPage(title="Biblioteca", slug="biblioteca",
                            entradilla="<p>La revista de la Cátedra, publicaciones en abierto y libros.</p>"), menu=False)
        hija(FormacionPage(title="Formación", slug="formacion",
                           entradilla="<p>Clases abiertas y exclusivas, en directo y grabadas.</p>"), menu=False)
        galeria = hija(self.galeria())
        hija(NovedadesPage(title="Novedades", slug="novedades"), menu=False)
        hija(self.contacto())
        for nombre, slug in (("aviso-legal.html", "aviso-legal"), ("privacidad.html", "privacidad"),
                             ("cookies.html", "cookies"), ("accesibilidad.html", "accesibilidad")):
            hija(self.legal(nombre, slug), menu=False)

        self.stdout.write(f"Páginas creadas bajo «{inicio.title}». Galería con {len(galeria.elementos)} imágenes.")

    def portada(self):
        s = self.sopa("index.html")
        inicio = HomePage(title="Inicio", slug="inicio")
        if s:
            lead = s.select_one(".hero__lead")
            inicio.hero_entradilla = lead.get_text(" ", strip=True) if lead else ""
            sec = s.select_one("#t-presentacion")
            if sec:
                inicio.presentacion_titulo = sec.get_text(strip=True).rstrip(".")
                bloque = sec.find_parent("section")
                inicio.presentacion_texto = html_limpio(bloque.select(".col-6 > p.lead, .col-6 > div.prose > p"))
                cita = bloque.select_one("blockquote p")
                inicio.presentacion_cita = cita.get_text(strip=True).strip("«»") if cita else ""
        inicio.presentacion_imagen = self.imagen("estudiantes.png", "Comunidad universitaria en el campus")
        return inicio

    def la_catedra(self):
        s = self.sopa("la-catedra.html")
        pagina = PaginaSimple(title="La Cátedra", slug="la-catedra", antetitulo="Quiénes somos")
        cuerpo = []
        if s:
            lead = s.select_one(".page-hero .lead")
            pagina.entradilla = lead.get_text(" ", strip=True) if lead else ""
            for seccion in s.select("main section[id]"):
                titulo = seccion.select_one("h2")
                prosa = seccion.select(".prose > *")
                if not prosa:
                    continue
                if titulo:
                    cuerpo.append(bloque_titulo(titulo.get_text(strip=True)))
                cuerpo.append(bloque_texto(html_limpio(prosa)))
        pagina.cuerpo = cuerpo
        return pagina

    def galeria(self):
        s = self.sopa("multimedia.html")
        g = GaleriaPage(title="Galería", slug="galeria", antetitulo="Galería · Archivo",
                        entradilla="Fotografías y documentos gráficos de la Cátedra.")
        elementos = []
        if s:
            for boton in s.select("#galeria [data-lightbox]"):
                ruta = boton["data-lightbox"]
                if not ruta.startswith("assets/img/"):
                    continue
                contenedor = boton.find_parent(attrs={"data-tipo": True})
                tipo = contenedor["data-tipo"] if contenedor else "foto"
                titulo = boton.select_one(".mosaic__cap .t")
                titulo = titulo.get_text(strip=True) if titulo else boton.get("data-caption", "")
                img = self.imagen(Path(ruta).name, boton.get("data-caption") or titulo)
                if img:
                    elementos.append({"type": "elemento", "id": str(uuid.uuid4()), "value": {
                        "imagen": img.pk, "titulo": titulo[:120],
                        "tipo": "documento" if tipo == "documento" else "foto",
                        "descripcion": (boton.get("data-caption") or "")[:255],
                    }})
        g.elementos = elementos
        return g

    def contacto(self):
        c = ContactoPage(
            title="Contacto", slug="contacto",
            entradilla="<p>Escríbenos para dudas, colaboraciones o prensa.</p>",
            gracias="<p>Gracias por escribirnos. Te responderemos lo antes posible.</p>",
            to_address="catedra.hispanidad@urjc.es", from_address="", subject="Nuevo mensaje desde la web",
        )
        c.form_fields = [
            CampoContacto(sort_order=0, label="Nombre", field_type="singleline", required=True),
            CampoContacto(sort_order=1, label="Correo electrónico", field_type="email", required=True),
            CampoContacto(sort_order=2, label="Motivo", field_type="dropdown", required=True,
                          choices="Información general\nColaboración\nPrensa\nCompras y acceso a contenidos"),
            CampoContacto(sort_order=3, label="Mensaje", field_type="multiline", required=True),
        ]
        return c

    def legal(self, nombre, slug):
        s = self.sopa(nombre)
        titulo = slug.replace("-", " ").capitalize()
        pagina = PaginaSimple(title=titulo, slug=slug, antetitulo="Legal")
        if s:
            h1 = s.select_one("main h1")
            pagina.title = h1.get_text(strip=True) if h1 else titulo
            prosa = s.select("main .prose > *")
            pagina.cuerpo = [bloque_texto(html_limpio(prosa))] if prosa else []
            aviso = s.select_one("main .tag--demo")
            if aviso:
                pagina.search_description = f"PENDIENTE DE REVISIÓN: {aviso.get_text(strip=True)}"[:255]
        return pagina
