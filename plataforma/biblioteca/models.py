from django.core.paginator import Paginator
from django.core.validators import FileExtensionValidator
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index

from compras.models import Acceso, Producto, almacen_privado


class BibliotecaPage(Page):
    """Portada de la Biblioteca: revista, publicaciones en abierto y libros a la venta."""

    antetitulo = models.CharField(max_length=80, blank=True, default="Biblioteca")
    entradilla = RichTextField(blank=True, features=["bold", "italic", "link"])

    content_panels = Page.content_panels + [FieldPanel("antetitulo"), FieldPanel("entradilla")]
    subpage_types = ["biblioteca.PublicacionPage"]
    max_count = 1

    class Meta:
        verbose_name = "portada de la Biblioteca"

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        qs = PublicacionPage.objects.child_of(self).live().order_by("-fecha_publicacion", "-first_published_at")
        tipo = request.GET.get("tipo", "")
        if tipo in PublicacionPage.Tipo.values:
            qs = qs.filter(tipo=tipo)
        acceso = request.GET.get("acceso", "")
        if acceso in Acceso.values:
            qs = qs.filter(acceso=acceso)
        ctx["publicaciones"] = Paginator(qs, 24).get_page(request.GET.get("pagina"))
        ctx["tipos"] = PublicacionPage.Tipo.choices
        ctx["tipo_activo"] = tipo
        ctx["acceso_activo"] = acceso
        return ctx


class PublicacionPage(Producto, Page):
    """Libro, artículo, número de revista o documento. Puede ser libre, para registrados o de pago."""

    class Tipo(models.TextChoices):
        LIBRO = "libro", "Libro"
        REVISTA = "revista", "Número de revista"
        ARTICULO = "articulo", "Artículo"
        DOCUMENTO = "documento", "Documento de trabajo"

    tipo = models.CharField(max_length=12, choices=Tipo.choices, default=Tipo.LIBRO)
    autoria = models.CharField("autoría", max_length=255, blank=True)
    fecha_publicacion = models.DateField("fecha de publicación", null=True, blank=True)
    portada = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    resumen = models.TextField(max_length=400, blank=True, help_text="Una o dos frases para las tarjetas y el buscador.")
    sinopsis = RichTextField(blank=True)
    isbn = models.CharField("ISBN / ISSN", max_length=32, blank=True)
    doi = models.CharField("DOI", max_length=128, blank=True)
    paginas = models.PositiveIntegerField("n.º de páginas", null=True, blank=True)
    archivo = models.FileField(
        "archivo (PDF o EPUB)", storage=almacen_privado, upload_to="publicaciones/", blank=True,
        validators=[FileExtensionValidator(["pdf", "epub"])],
        help_text="Se guarda en una zona privada: solo se descarga si el usuario tiene acceso.",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel([FieldPanel("tipo"), FieldPanel("autoria"), FieldPanel("fecha_publicacion")], heading="Ficha"),
        FieldPanel("portada"),
        FieldPanel("resumen"),
        FieldPanel("sinopsis"),
        MultiFieldPanel([FieldPanel("isbn"), FieldPanel("doi"), FieldPanel("paginas")], heading="Datos bibliográficos"),
        FieldPanel("archivo"),
    ] + Producto.producto_panels

    search_fields = Page.search_fields + [
        index.SearchField("autoria"),
        index.SearchField("resumen"),
        index.SearchField("sinopsis"),
        index.FilterField("tipo"),
    ]
    parent_page_types = ["biblioteca.BibliotecaPage"]
    subpage_types = []

    class Meta:
        verbose_name = "publicación"
        verbose_name_plural = "publicaciones"

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        ctx["tiene_acceso"] = self.usuario_tiene_acceso(request.user)
        return ctx
