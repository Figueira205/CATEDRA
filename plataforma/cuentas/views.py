from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from compras.models import Compra


@login_required
def mi_cuenta(request):
    """Espacio del estudiante: sus libros, sus clases y sus datos."""
    compras = (Compra.objects.filter(usuario=request.user, estado=Compra.Estado.PAGADA)
               .select_related("pagina").order_by("-pagada_en"))
    libros, clases = [], []
    for c in compras:
        pagina = c.pagina.specific
        tipo = pagina.specific_class.__name__
        if tipo == "PublicacionPage":
            libros.append((c, pagina))
        elif tipo == "ClasePage":
            clases.append((c, pagina))
    return render(request, "cuentas/mi_cuenta.html", {
        "libros": libros,
        "clases": clases,
        "historial": Compra.objects.filter(usuario=request.user).exclude(estado=Compra.Estado.PENDIENTE).select_related("pagina")[:50],
    })
