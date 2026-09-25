# Imagen de producción de la plataforma de la Cátedra.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_SETTINGS_MODULE=catedra.settings.production

# libjpeg/zlib/webp: procesado de imágenes de Wagtail. postgresql-client: copias de seguridad.
RUN apt-get update \
 && apt-get install -y --no-install-recommends libjpeg62-turbo zlib1g libwebp7 postgresql-client \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Estáticos dentro de la imagen (los sirve WhiteNoise). La clave es solo para este paso.
RUN DJANGO_SECRET_KEY=solo-para-collectstatic python manage.py collectstatic --noinput \
 && useradd --system --uid 1000 --create-home catedra \
 && mkdir -p /app/media /app/privado \
 && chown -R catedra:catedra /app/media /app/privado \
 && chmod +x /app/docker/entrypoint.sh

USER catedra
EXPOSE 8000
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["gunicorn", "catedra.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "--access-logfile", "-"]
