#!/bin/sh
# Antes de arrancar: aplica migraciones pendientes y prepara la caché.
set -e
python manage.py migrate --noinput
python manage.py createcachetable
exec "$@"
