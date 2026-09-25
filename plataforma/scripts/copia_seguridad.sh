#!/bin/sh
# Copia de seguridad diaria: base de datos + archivos subidos + archivos de pago.
#
# Uso en el VPS (desde la carpeta plataforma/):   ./scripts/copia_seguridad.sh
# Programarla a las 3:30 cada noche:               crontab -e
#   30 3 * * * cd /opt/catedra/plataforma && ./scripts/copia_seguridad.sh >> /var/log/catedra-copias.log 2>&1
#
# Si RCLONE_DESTINO está definido (ej. "b2:catedra-copias"), se sube además
# fuera del servidor. Sin copia externa, perder el VPS es perderlo todo.
set -eu

DESTINO_LOCAL="${DESTINO_LOCAL:-./copias}"
DIAS="${DIAS_A_CONSERVAR:-14}"
FECHA=$(date +%Y-%m-%d_%H%M)
CARPETA="$DESTINO_LOCAL/$FECHA"
mkdir -p "$CARPETA"

# Variables POSTGRES_* desde .env
set -a; . ./.env; set +a

echo "[$(date)] Copia $FECHA"
docker compose exec -T db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom > "$CARPETA/catedra.dump"
docker compose exec -T db pg_dump -U "$POSTGRES_USER" -d umami --format=custom > "$CARPETA/umami.dump"
docker compose exec -T web tar -C /app -czf - media privado > "$CARPETA/archivos.tar.gz"

# Comprobación mínima: los archivos no pueden estar vacíos.
for f in catedra.dump archivos.tar.gz; do
  [ -s "$CARPETA/$f" ] || { echo "ERROR: $f vacío"; exit 1; }
done

if [ -n "${RCLONE_DESTINO:-}" ]; then
  rclone copy "$CARPETA" "$RCLONE_DESTINO/$FECHA"
  echo "Subida a $RCLONE_DESTINO/$FECHA"
fi

find "$DESTINO_LOCAL" -mindepth 1 -maxdepth 1 -type d -mtime +"$DIAS" -exec rm -rf {} +
echo "[$(date)] Copia terminada: $(du -sh "$CARPETA" | cut -f1)"
