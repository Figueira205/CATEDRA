from django.urls import path

from . import views

app_name = "formacion"

urlpatterns = [
    path("directo/<int:page_id>/", views.entrar_directo, name="entrar_directo"),
    path("video/<int:page_id>/", views.video_embed, name="video_embed"),
]
