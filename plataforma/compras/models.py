from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models import Q
from wagtail.admin.panels import FieldPanel, MultiFieldPanel


class AlmacenPrivado(FileSystemStorage):
    """Archivos de pago: fuera de MEDIA_ROOT y sin URL pública.

    Solo salen por la vista de descarga, que comprueba la compra. `url()`
    devuelve un ancla inofensiva para que el panel muestre que hay archivo
    sin revelar ninguna ruta (FileSystemStorage usaría MEDIA_URL por defecto).
    """

    def url(self, name):
        return "#archivo-privado"


def almacen_privado():
    """Se usa como callable para que la ruta no quede escrita en las migraciones."""
    return AlmacenPrivado(location=settings.PRIVATE_MEDIA_ROOT)


PRECIO_MINIMO = Decimal("0.50")  # mínimo que acepta Stripe en euros


class Acceso(models.TextChoices):
    LIBRE = "libre", "Libre: cualquier visitante"
    REGISTRO = "registro", "Gratuito para usuarios registrados"
    PAGO = "pago", "De pago"


class Producto(models.Model):
    """Añade «acceso y precio» a una página (publicación, clase…).

    Cualquier tipo de página que herede de aquí se puede comprar con Stripe
    y aparece en «Mi cuenta» del estudiante cuando la ha pagado.
    """

    acceso = models.CharField("acceso", max_length=10, choices=Acceso.choices, default=Acceso.LIBRE)
    precio = models.DecimalField(
        "precio (€, IVA incluido)", max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Solo para contenidos de pago.",
    )

    producto_panels = [
        MultiFieldPanel([FieldPanel("acceso"), FieldPanel("precio")], heading="Acceso y precio"),
    ]

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        if self.acceso == Acceso.PAGO:
            if self.precio is None or self.precio < PRECIO_MINIMO:
                raise ValidationError({"precio": f"Un contenido de pago necesita un precio de al menos {PRECIO_MINIMO} €."})
        else:
            self.precio = None

    @property
    def es_de_pago(self):
        return self.acceso == Acceso.PAGO

    def usuario_tiene_acceso(self, user):
        if self.acceso == Acceso.LIBRE:
            return True
        if not user.is_authenticated:
            return False
        if self.acceso == Acceso.REGISTRO or user.is_superuser:
            return True
        return Compra.objects.filter(usuario=user, pagina_id=self.pk, estado=Compra.Estado.PAGADA).exists()


class Compra(models.Model):
    """Registro de cada compra. Es la «fuente de verdad» del acceso a contenidos de pago.

    No se borra nunca (obligaciones contables): si un usuario pide la baja,
    se anonimiza su cuenta, pero la compra se conserva.
    """

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente de pago"
        PAGADA = "pagada", "Pagada"
        REEMBOLSADA = "reembolsada", "Reembolsada"
        CADUCADA = "caducada", "Caducada sin pagar"

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="compras")
    pagina = models.ForeignKey("wagtailcore.Page", on_delete=models.PROTECT, related_name="+", verbose_name="contenido")
    concepto = models.CharField(max_length=255, help_text="Título del contenido en el momento de la compra.")
    importe = models.DecimalField(max_digits=8, decimal_places=2)
    moneda = models.CharField(max_length=3, default="eur")
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.PENDIENTE, db_index=True)
    stripe_session_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, db_index=True)
    creada = models.DateTimeField(auto_now_add=True)
    pagada_en = models.DateTimeField(null=True, blank=True)
    actualizada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "compra"
        verbose_name_plural = "compras"
        ordering = ["-creada"]
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "pagina"], condition=Q(estado="pagada"),
                name="una_compra_pagada_por_contenido",
            ),
        ]

    def __str__(self):
        return f"{self.concepto} · {self.usuario} · {self.get_estado_display()}"
