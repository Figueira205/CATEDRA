"""Producción (VPS detrás de Caddy con HTTPS)."""
from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False

# Caddy termina TLS y reenvía la petición: confiar en su cabecera.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("DJANGO_HSTS_SECONDS", default=60 * 60 * 24 * 365)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = False  # activar solo cuando el dominio definitivo esté estable

SILENCED_SYSTEM_CHECKS = [
    "security.W019",  # X_FRAME_OPTIONS=SAMEORIGIN: la vista previa de Wagtail usa un iframe del mismo origen
    "security.W021",  # HSTS preload: difícil de revertir; activar cuando el dominio definitivo esté estable
]

CONN_MAX_AGE = 60

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "cache_django",
    }
}
