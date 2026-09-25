"""Desarrollo local: DEBUG activo, correos en consola, SQLite por defecto."""
from .base import *  # noqa: F401,F403
from .base import env

DEBUG = env.bool("DJANGO_DEBUG", default=True)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
# En local no se exige 2FA al personal, salvo que se active en .env.
CATEDRA_2FA_OBLIGATORIO_PERSONAL = env.bool("CATEDRA_2FA_OBLIGATORIO_PERSONAL", default=False)
STORAGES["staticfiles"] = {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}  # noqa: F405
