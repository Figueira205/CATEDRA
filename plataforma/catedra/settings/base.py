"""
Configuración común a todos los entornos.

Todo lo que cambia entre entornos (claves, base de datos, dominios, Stripe…)
se lee de variables de entorno o de un archivo `.env` (ver `.env.example`).
Nunca se escriben secretos en este archivo.
"""
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

# URL pública del sitio, sin barra final (se usa en correos y en Stripe).
SITIO_URL = env("SITIO_URL", default="http://localhost:8000").rstrip("/")
WAGTAILADMIN_BASE_URL = SITIO_URL
WAGTAIL_SITE_NAME = "Cátedra de la Hispanidad"

INSTALLED_APPS = [
    # Proyecto
    "cuentas",
    "sitio",
    "biblioteca",
    "formacion",
    "compras",
    # Wagtail
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.contrib.sitemaps",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
    # Cuentas
    "allauth",
    "allauth.account",
    "allauth.mfa",
    # Django
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "cuentas.middleware.DobleFactorObligatorioMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "catedra.urls"
WSGI_APPLICATION = "catedra.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
                "sitio.context_processors.sitio",
            ],
        },
    },
]

# Base de datos: SQLite si no se indica otra cosa (desarrollo rápido);
# en producción DATABASE_URL apunta a PostgreSQL.
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------- Usuarios
AUTH_USER_MODEL = "cuentas.Usuario"
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
# Argon2 es el algoritmo recomendado; PBKDF2 queda para contraseñas antiguas.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "mi_cuenta"
WAGTAILADMIN_LOGIN_URL = "account_login"  # el panel usa el mismo login (con 2FA)

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_CONFIRM_EMAIL_ON_GET = False
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SESSION_REMEMBER = None  # el usuario elige «recordarme»
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = False
ACCOUNT_PREVENT_ENUMERATION = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Cátedra de la Hispanidad] "
# Límites de intentos (protección contra fuerza bruta). Formato de allauth.
ACCOUNT_RATE_LIMITS = {
    "login_failed": "10/m/ip,5/5m/key",
    "signup": "20/h/ip",
    "reset_password": "20/m/ip,5/m/key",
    "confirm_email": "1/3m/key",
}
MFA_SUPPORTED_TYPES = ["totp", "recovery_codes"]
MFA_TOTP_ISSUER = "Cátedra de la Hispanidad"

# Personal (is_staff) debe tener 2FA activado para entrar al panel.
CATEDRA_2FA_OBLIGATORIO_PERSONAL = env.bool("CATEDRA_2FA_OBLIGATORIO_PERSONAL", default=True)

# ---------------------------------------------------------------- Idioma
LANGUAGE_CODE = "es"
TIME_ZONE = "Europe/Madrid"
USE_I18N = True
USE_TZ = True
WAGTAIL_I18N_ENABLED = False
WAGTAILADMIN_PERMITTED_LANGUAGES = [("es", "Español")]

# ---------------------------------------------------------------- Archivos
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = env.path("MEDIA_ROOT", default=BASE_DIR / "media")
# Archivos de pago (libros, materiales): FUERA de MEDIA_ROOT, nunca servidos
# directamente por el servidor web. Solo salen por la vista de descarga,
# que comprueba la compra.
PRIVATE_MEDIA_ROOT = env.path("PRIVATE_MEDIA_ROOT", default=BASE_DIR / "privado")

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
WAGTAILDOCS_SERVE_METHOD = "serve_view"
WAGTAILDOCS_EXTENSIONS = ["pdf", "epub", "docx", "xlsx", "pptx", "odt", "txt", "zip"]
WAGTAILIMAGES_EXTENSIONS = ["gif", "jpg", "jpeg", "png", "webp", "avif"]

WAGTAILSEARCH_BACKENDS = {"default": {"BACKEND": "wagtail.search.backends.database"}}

# ---------------------------------------------------------------- Correo
# En desarrollo se imprimen en consola; en producción, SMTP (Brevo, Resend…).
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="Cátedra de la Hispanidad <no-responder@localhost>")
SERVER_EMAIL = DEFAULT_FROM_EMAIL
WAGTAILADMIN_NOTIFICATION_FROM_EMAIL = DEFAULT_FROM_EMAIL
ADMINS = [("Administración", a) for a in env.list("DJANGO_ADMINS", default=[])]

# ---------------------------------------------------------------- Stripe
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="")
STRIPE_MONEDA = "eur"
# Prefijo en Stripe para separar la Cátedra de otros negocios de la empresa.
STRIPE_PREFIJO_PRODUCTO = env("STRIPE_PREFIJO_PRODUCTO", default="Cátedra")

# ---------------------------------------------------------------- Analítica
# Umami (autoalojado, sin cookies). Vacío = no se carga el script.
UMAMI_SCRIPT_URL = env("UMAMI_SCRIPT_URL", default="")
UMAMI_WEBSITE_ID = env("UMAMI_WEBSITE_ID", default="")

# ---------------------------------------------------------------- Seguridad
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
X_FRAME_OPTIONS = "SAMEORIGIN"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

_umami_origen = "/".join(UMAMI_SCRIPT_URL.split("/")[:3]) if UMAMI_SCRIPT_URL else None
CONTENT_SECURITY_POLICY = {
    # El panel de Wagtail (protegido con 2FA) usa scripts en línea: queda fuera.
    "EXCLUDE_URL_PREFIXES": ["/admin/"],
    "DIRECTIVES": {
        "default-src": ["'self'"],
        # Sin 'unsafe-inline': solo se ejecuta JavaScript servido por nosotros.
        "script-src": ["'self'"] + ([_umami_origen] if _umami_origen else []),
        "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
        "font-src": ["'self'", "https://fonts.gstatic.com", "data:"],
        "img-src": ["'self'", "data:", "blob:", "https://i.ytimg.com", "https://i.vimeocdn.com"],
        "frame-src": [
            "https://www.youtube-nocookie.com", "https://www.youtube.com",
            "https://player.vimeo.com",
        ],
        "connect-src": ["'self'"] + ([_umami_origen] if _umami_origen else []),
        "form-action": ["'self'", "https://checkout.stripe.com"],
        "frame-ancestors": ["'self'"],
        "base-uri": ["'self'"],
        "object-src": ["'none'"],
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.security": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        # Tareas en segundo plano de Wagtail: muy verbosas en INFO.
        "django_tasks": {"level": "WARNING"},
        "wagtail": {"level": "WARNING"},
    },
}
