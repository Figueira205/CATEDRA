#!/bin/sh
# Restaura una copia creada por copia_seguridad.sh.  SOBRESCRIBE los datos actuales.
#
# Uso:  ./scripts/restaurar_copia.sh copias/2026-10-01_0330
set -eu
CARPETA="${1:?Indica la carpeta de la copia, p. ej. copias/2026-10-01_0330}"
set -a; . ./.env; set +a

printf "Se van a SUSTITUIR la base de datos y los archivos por la copia %s. Escribe SI para continuar: " "$CARPETA"
read -r respuesta
[ "$respuesta" = "SI" ] || { echo "Cancelado."; exit 1; }

docker compose stop web
docker compose exec -T db pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists < "$CARPETA/catedra.dump"
[ -f "$CARPETA/umami.dump" ] && docker compose exec -T db pg_restore -U "$POSTGRES_USER" -d umami --clean --if-exists < "$CARPETA/umami.dump"
docker compose run --rm --no-deps --entrypoint "" web sh -c "rm -rf /app/media/* /app/privado/* && tar -C /app -xzf -" < "$CARPETA/archivos.tar.gz"
docker compose start web
echo "Restauración completada."
