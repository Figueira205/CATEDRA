#!/bin/sh
# Solo se ejecuta la primera vez que se crea el volumen de PostgreSQL:
# crea una base de datos y un usuario separados para Umami (analítica).
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<SQL
CREATE USER umami WITH PASSWORD '${UMAMI_DB_PASSWORD}';
CREATE DATABASE umami OWNER umami;
SQL
