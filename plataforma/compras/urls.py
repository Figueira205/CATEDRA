from django.urls import path

from . import views

app_name = "compras"

urlpatterns = [
    path("comprar/<int:page_id>/", views.comprar, name="comprar"),
    path("pago-realizado/", views.exito, name="exito"),
    path("descargar/<int:page_id>/", views.descargar, name="descargar"),
    path("stripe/webhook/", views.webhook, name="webhook"),
]
