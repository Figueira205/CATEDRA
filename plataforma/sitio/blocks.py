"""Bloques de contenido que los editores combinan libremente en páginas y noticias."""
from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock


class ImagenBlock(blocks.StructBlock):
    imagen = ImageChooserBlock()
    pie = blocks.CharBlock(required=False, max_length=255)

    class Meta:
        icon = "image"
        label = "Imagen"
        template = "sitio/bloques/imagen.html"


class CitaBlock(blocks.StructBlock):
    texto = blocks.TextBlock()
    autoria = blocks.CharBlock(required=False, label="Autoría")

    class Meta:
        icon = "openquote"
        label = "Cita"
        template = "sitio/bloques/cita.html"


class DocumentoBlock(blocks.StructBlock):
    documento = DocumentChooserBlock()
    titulo = blocks.CharBlock(required=False, help_text="Si se deja vacío, se usa el título del documento.")

    class Meta:
        icon = "doc-full"
        label = "Documento descargable"
        template = "sitio/bloques/documento.html"


class BotonBlock(blocks.StructBlock):
    texto = blocks.CharBlock(max_length=80)
    pagina = blocks.PageChooserBlock(required=False)
    url = blocks.URLBlock(required=False, help_text="Solo si no se elige una página.")

    class Meta:
        icon = "link"
        label = "Botón"
        template = "sitio/bloques/boton.html"


class CuerpoBlock(blocks.StreamBlock):
    titulo = blocks.CharBlock(form_classname="title", icon="title", label="Subtítulo", template="sitio/bloques/titulo.html")
    texto = blocks.RichTextBlock(
        features=["bold", "italic", "link", "ol", "ul", "h3", "h4", "document-link"],
        label="Texto", template="sitio/bloques/texto.html",
    )
    imagen = ImagenBlock()
    cita = CitaBlock()
    video = EmbedBlock(label="Vídeo (YouTube o Vimeo)", template="sitio/bloques/video.html")
    documento = DocumentoBlock()
    boton = BotonBlock()


class ElementoGaleriaBlock(blocks.StructBlock):
    imagen = ImageChooserBlock()
    titulo = blocks.CharBlock(max_length=120)
    tipo = blocks.ChoiceBlock(choices=[("foto", "Fotografía"), ("documento", "Documento gráfico")], default="foto")
    descripcion = blocks.CharBlock(required=False, max_length=255, label="Descripción")

    class Meta:
        icon = "image"
        label = "Imagen de la galería"
