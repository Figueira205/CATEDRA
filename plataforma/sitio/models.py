import json
import secrets
from datetime import timedelta
from datetime import timezone as dt_timezone

from django.core.paginator import Paginator
from django.db import models
from django.utils import timezone
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.search import index

from .blocks import CuerpoBlock, ElementoGaleriaBlock


# --------------------------------------------------------------------- Portada
class HomePage(Page):
    hero_antetitulo = models.CharField("antetítulo", max_length=120, blank=True,
                                       default="Cátedra universitaria · Investigación · Cultura · Pensamiento")
    hero_titulo = models.CharField("título", max_length=120, default="Una conversación académica")
    hero_titulo_destacado = models.CharField("final del título (en cursiva)", max_length=60, blank=True, default="entre orillas")
    hero_entradilla = models.TextField("entradilla", blank=True)
    destacado = models.ForeignKey(
        "wagtailcore.Page", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
        verbose_name="contenido en foco", help_text="Actividad, clase o publicación que aparece junto al título.",
    )
    presentacion_titulo = models.CharField("título", max_length=160, blank=True)
    presentacion_texto = RichTextField("texto", blank=True, features=["bold", "italic", "link"])
    presentacion_imagen = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+", verbose_name="imagen")
    presentacion_cita = models.CharField("cita", max_length=255, blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel([FieldPanel("hero_antetitulo"), FieldPanel("hero_titulo"), FieldPanel("hero_titulo_destacado"),
                         FieldPanel("hero_entradilla"), FieldPanel("destacado")], heading="Cabecera"),
        MultiFieldPanel([FieldPanel("presentacion_titulo"), FieldPanel("presentacion_texto"),
                         FieldPanel("presentacion_imagen"), FieldPanel("presentacion_cita")], heading="Presentación"),
    ]
    parent_page_types = ["wagtailcore.Page"]
    max_count = 1

    class Meta:
        verbose_name = "portada"

    def get_context(self, request, *args, **kwargs):
        from biblioteca.models import PublicacionPage

        ctx = super().get_context(request, *args, **kwargs)
        ctx["proximas_actividades"] = ActividadPage.objects.live().filter(fecha_inicio__gte=timezone.now()).order_by("fecha_inicio")[:4]
        ctx["ultimas_publicaciones"] = PublicacionPage.objects.live().order_by("-fecha_publicacion", "-first_published_at")[:4]
        galeria = GaleriaPage.objects.live().first()
        ctx["galeria"] = galeria
        ctx["galeria_elementos"] = list(galeria.elementos)[:5] if galeria else []
        ctx["ultimas_novedades"] = NovedadPage.objects.live().order_by("-fecha")[:3]
        return ctx


# ------------------------------------------------------------- Página de texto
class PaginaSimple(Page):
    """Página de contenido libre: La Cátedra, aviso legal, privacidad…"""

    antetitulo = models.CharField(max_length=120, blank=True)
    entradilla = models.TextField(blank=True)
    cuerpo = StreamField(CuerpoBlock(), blank=True, use_json_field=True)

    content_panels = Page.content_panels + [FieldPanel("antetitulo"), FieldPanel("entradilla"), FieldPanel("cuerpo")]
    search_fields = Page.search_fields + [index.SearchField("entradilla"), index.SearchField("cuerpo")]

    class Meta:
        verbose_name = "página de contenido"
        verbose_name_plural = "páginas de contenido"


# ------------------------------------------------------------------ Actividades
class ActividadesPage(Page):
    antetitulo = models.CharField(max_length=120, blank=True, default="Agenda")
    entradilla = models.TextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("antetitulo"), FieldPanel("entradilla")]
    subpage_types = ["sitio.ActividadPage"]
    max_count = 1

    class Meta:
        verbose_name = "agenda de actividades"

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        todas = ActividadPage.objects.child_of(self).live()
        ahora = timezone.now()
        ctx["proximas"] = todas.filter(fecha_inicio__gte=ahora).order_by("fecha_inicio")
        ctx["celebradas"] = Paginator(todas.filter(fecha_inicio__lt=ahora).order_by("-fecha_inicio"), 12).get_page(request.GET.get("pagina"))
        return ctx


class ActividadPage(Page):
    class Tipo(models.TextChoices):
        CATEDRA = "catedra", "Cátedra"
        SEMINARIO = "seminario", "Seminario"
        CONFERENCIA = "conferencia", "Conferencia"
        JORNADA = "jornada", "Jornada o congreso"
        CURSO = "curso", "Curso"
        PREMIO = "premio", "Premio o convocatoria"
        OTRA = "otra", "Otra"

    class Modalidad(models.TextChoices):
        PRESENCIAL = "presencial", "Presencial"
        ONLINE = "online", "En línea"
        HIBRIDA = "hibrida", "Híbrida"

    tipo = models.CharField(max_length=12, choices=Tipo.choices, default=Tipo.SEMINARIO)
    modalidad = models.CharField(max_length=12, choices=Modalidad.choices, default=Modalidad.PRESENCIAL)
    fecha_inicio = models.DateTimeField("inicio")
    fecha_fin = models.DateTimeField("fin", null=True, blank=True)
    lugar = models.CharField(max_length=255, blank=True)
    imagen = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    resumen = models.TextField(max_length=400, blank=True)
    cuerpo = StreamField(CuerpoBlock(), blank=True, use_json_field=True)
    enlace_inscripcion = models.URLField("enlace de inscripción", blank=True, help_text="Opcional. La cátedra es de acceso libre.")

    content_panels = Page.content_panels + [
        MultiFieldPanel([FieldPanel("tipo"), FieldPanel("modalidad"),
                         FieldRowPanel([FieldPanel("fecha_inicio"), FieldPanel("fecha_fin")]),
                         FieldPanel("lugar"), FieldPanel("enlace_inscripcion")], heading="Datos"),
        FieldPanel("imagen"),
        FieldPanel("resumen"),
        FieldPanel("cuerpo"),
    ]
    search_fields = Page.search_fields + [index.SearchField("resumen"), index.SearchField("lugar"), index.SearchField("cuerpo")]
    parent_page_types = ["sitio.ActividadesPage"]
    subpage_types = []

    class Meta:
        verbose_name = "actividad"
        verbose_name_plural = "actividades"

    @property
    def ics(self):
        """Datos para el botón «Añadir al calendario» (main.js genera el .ics)."""
        fmt = "%Y%m%dT%H%M%SZ"
        fin = self.fecha_fin or self.fecha_inicio + timedelta(hours=2)
        return {
            "start": self.fecha_inicio.astimezone(dt_timezone.utc).strftime(fmt),
            "end": fin.astimezone(dt_timezone.utc).strftime(fmt),
            "title": self.title, "place": self.lugar, "desc": self.resumen,
        }

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        ctx["ics_json"] = json.dumps(self.ics, ensure_ascii=False)
        return ctx


# --------------------------------------------------------------- Novedades (blog)
class NovedadesPage(Page):
    antetitulo = models.CharField(max_length=120, blank=True, default="Novedades")
    entradilla = models.TextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("antetitulo"), FieldPanel("entradilla")]
    subpage_types = ["sitio.NovedadPage"]
    max_count = 1

    class Meta:
        verbose_name = "portada de novedades (blog)"

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        ctx["novedades"] = Paginator(NovedadPage.objects.child_of(self).live().order_by("-fecha"), 12).get_page(request.GET.get("pagina"))
        return ctx


class NovedadPage(Page):
    fecha = models.DateField(default=timezone.localdate)
    autoria = models.CharField("autoría", max_length=255, blank=True)
    imagen = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    resumen = models.TextField(max_length=400, blank=True)
    cuerpo = StreamField(CuerpoBlock(), blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldRowPanel([FieldPanel("fecha"), FieldPanel("autoria")]),
        FieldPanel("imagen"), FieldPanel("resumen"), FieldPanel("cuerpo"),
    ]
    search_fields = Page.search_fields + [index.SearchField("resumen"), index.SearchField("cuerpo"), index.SearchField("autoria")]
    parent_page_types = ["sitio.NovedadesPage"]
    subpage_types = []

    class Meta:
        verbose_name = "novedad"
        verbose_name_plural = "novedades"


# ---------------------------------------------------------------------- Galería
class GaleriaPage(Page):
    antetitulo = models.CharField(max_length=120, blank=True, default="Galería")
    entradilla = models.TextField(blank=True)
    elementos = StreamField([("elemento", ElementoGaleriaBlock())], blank=True, use_json_field=True)

    content_panels = Page.content_panels + [FieldPanel("antetitulo"), FieldPanel("entradilla"), FieldPanel("elementos")]

    class Meta:
        verbose_name = "galería"
        verbose_name_plural = "galerías"


# --------------------------------------------------------------------- Contacto
class CampoContacto(AbstractFormField):
    page = ParentalKey("ContactoPage", on_delete=models.CASCADE, related_name="form_fields")


class ContactoPage(AbstractEmailForm):
    """Formulario editable desde el panel; los mensajes quedan guardados y se envían por correo."""

    antetitulo = models.CharField(max_length=120, blank=True, default="Contacto")
    entradilla = RichTextField(blank=True, features=["bold", "italic", "link"])
    gracias = RichTextField("mensaje tras enviar", blank=True, features=["bold", "italic", "link"])

    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel("antetitulo"),
        FieldPanel("entradilla"),
        InlinePanel("form_fields", label="Campos del formulario"),
        FieldPanel("gracias"),
        MultiFieldPanel([FieldRowPanel([FieldPanel("from_address"), FieldPanel("to_address")]), FieldPanel("subject")],
                        heading="Aviso por correo"),
    ]
    max_count = 1

    class Meta:
        verbose_name = "página de contacto"


# ---------------------------------------------------------------------- Boletín
class Suscriptor(models.Model):
    """Suscripción al boletín con doble confirmación (RGPD)."""

    email = models.EmailField("correo electrónico", unique=True)
    nombre = models.CharField(max_length=120, blank=True)
    confirmado = models.BooleanField(default=False)
    token = models.CharField(max_length=64, unique=True, default=secrets.token_urlsafe, editable=False)
    creado = models.DateTimeField(auto_now_add=True)
    confirmado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "suscriptor del boletín"
        verbose_name_plural = "suscriptores del boletín"
        ordering = ["-creado"]

    def __str__(self):
        return self.email


# ------------------------------------------------------------ Ajustes generales
@register_setting(icon="cog")
class ConfiguracionSitio(BaseSiteSetting):
    correo_contacto = models.EmailField(blank=True, default="catedra.hispanidad@urjc.es")
    direccion = models.CharField("dirección", max_length=255, blank=True, default="Universidad Rey Juan Carlos · Madrid, España")
    descripcion_pie = models.TextField(
        "descripción en el pie", blank=True,
        default="Espacio universitario de investigación, enseñanza y divulgación sobre las realidades históricas, "
                "culturales, jurídicas y sociales del mundo hispánico.",
    )
    x = models.URLField("X (Twitter)", blank=True)
    youtube = models.URLField("YouTube", blank=True)
    instagram = models.URLField("Instagram", blank=True)
    linkedin = models.URLField("LinkedIn", blank=True)

    panels = [
        MultiFieldPanel([FieldPanel("correo_contacto"), FieldPanel("direccion"), FieldPanel("descripcion_pie")], heading="Datos generales"),
        MultiFieldPanel([FieldPanel("x"), FieldPanel("youtube"), FieldPanel("instagram"), FieldPanel("linkedin")], heading="Redes sociales"),
    ]

    class Meta:
        verbose_name = "configuración del sitio"
