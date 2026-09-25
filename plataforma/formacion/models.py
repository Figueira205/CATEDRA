import re
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index

from compras.models import Producto

_YOUTUBE = re.compile(r"(?:youtube\.com/(?:watch\?v=|embed/|live/|shorts/)|youtu\.be/)([\w-]{11})")
_VIMEO = re.compile(r"vimeo\.com/(?:video/)?(\d+)")


def url_incrustada(url):
    """Convierte un enlace de YouTube o Vimeo en su reproductor incrustable (YouTube sin cookies)."""
    if not url:
        return ""
    if m := _YOUTUBE.search(url):
        return f"https://www.youtube-nocookie.com/embed/{m.group(1)}?rel=0"
    if m := _VIMEO.search(url):
        return f"https://player.vimeo.com/video/{m.group(1)}?dnt=1"
    return ""


class FormacionPage(Page):
    """Portada de Formación: clases abiertas y exclusivas."""

    antetitulo = models.CharField(max_length=80, blank=True, default="Formación")
    entradilla = RichTextField(blank=True, features=["bold", "italic", "link"])

    content_panels = Page.content_panels + [FieldPanel("antetitulo"), FieldPanel("entradilla")]
    subpage_types = ["formacion.ClasePage"]
    max_count = 1

    class Meta:
        verbose_name = "portada de Formación"

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        clases = ClasePage.objects.child_of(self).live()
        ahora = timezone.now()
        ctx["proximos_directos"] = clases.filter(modalidad=ClasePage.Modalidad.DIRECTO, fecha__gte=ahora).order_by("fecha")
        ctx["clases"] = clases.exclude(modalidad=ClasePage.Modalidad.DIRECTO, fecha__gte=ahora).order_by("-fecha", "-first_published_at")
        return ctx


class ClasePage(Producto, Page):
    """Una clase: grabada (vídeo) o en directo (Zoom/YouTube Live, que luego se graba)."""

    class Modalidad(models.TextChoices):
        GRABADA = "grabada", "Grabada"
        DIRECTO = "directo", "En directo"

    modalidad = models.CharField(max_length=10, choices=Modalidad.choices, default=Modalidad.GRABADA)
    fecha = models.DateTimeField("fecha y hora", null=True, blank=True, help_text="Obligatoria para clases en directo.")
    duracion_minutos = models.PositiveIntegerField("duración (minutos)", null=True, blank=True)
    docente = models.CharField(max_length=255, blank=True)
    imagen = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    resumen = models.TextField(max_length=400, blank=True)
    descripcion = RichTextField("descripción", blank=True)
    video_url = models.URLField(
        "vídeo (YouTube o Vimeo)", blank=True,
        help_text="Enlace a la grabación. Solo se muestra a quien tiene acceso.",
    )
    enlace_directo = models.URLField(
        "enlace de la sesión en directo", blank=True,
        help_text="Zoom, Meet o YouTube Live. No se publica: se entrega a quien tiene acceso y se registra su asistencia.",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel([FieldPanel("modalidad"), FieldPanel("fecha"), FieldPanel("duracion_minutos"), FieldPanel("docente")], heading="Datos de la clase"),
        FieldPanel("imagen"),
        FieldPanel("resumen"),
        FieldPanel("descripcion"),
        MultiFieldPanel([FieldPanel("video_url"), FieldPanel("enlace_directo")], heading="Vídeo y directo"),
    ] + Producto.producto_panels

    search_fields = Page.search_fields + [
        index.SearchField("resumen"),
        index.SearchField("descripcion"),
        index.SearchField("docente"),
    ]
    parent_page_types = ["formacion.FormacionPage"]
    subpage_types = []

    class Meta:
        verbose_name = "clase"
        verbose_name_plural = "clases"

    def clean(self):
        super().clean()
        if self.modalidad == self.Modalidad.DIRECTO and not self.fecha:
            raise ValidationError({"fecha": "Una clase en directo necesita fecha y hora."})

    @property
    def video_incrustado(self):
        return url_incrustada(self.video_url)

    @property
    def directo_abierto(self):
        """El enlace se entrega desde 30 min antes hasta el final previsto (+30 min)."""
        if self.modalidad != self.Modalidad.DIRECTO or not self.fecha or not self.enlace_directo:
            return False
        ahora = timezone.now()
        fin = self.fecha + timedelta(minutes=(self.duracion_minutos or 120) + 30)
        return self.fecha - timedelta(minutes=30) <= ahora <= fin

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        acceso = self.usuario_tiene_acceso(request.user)
        ctx["tiene_acceso"] = acceso
        if acceso and self.video_url and not getattr(request, "is_preview", False):
            Visualizacion.objects.create(clase=self, usuario=request.user if request.user.is_authenticated else None)
        return ctx


class Visualizacion(models.Model):
    """Cada vez que alguien con acceso abre una clase con vídeo. Alimenta «clases más vistas»."""

    clase = models.ForeignKey(ClasePage, on_delete=models.CASCADE, related_name="visualizaciones")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    fecha = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "visualización"
        verbose_name_plural = "visualizaciones"


class Asistencia(models.Model):
    """Registro de asistencia a una clase en directo (al pulsar «Entrar al directo»).

    En directos abiertos se admite asistencia anónima (usuario vacío): cuenta
    para el total, pero no se puede asociar a una persona.
    """

    clase = models.ForeignKey(ClasePage, on_delete=models.CASCADE, related_name="asistencias")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="asistencias")
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "asistencia"
        verbose_name_plural = "asistencias"
        constraints = [
            models.UniqueConstraint(fields=["clase", "usuario"], condition=Q(usuario__isnull=False), name="una_asistencia_por_clase"),
        ]
