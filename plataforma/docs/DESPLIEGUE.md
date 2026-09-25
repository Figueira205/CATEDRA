# Despliegue en el VPS

Guía para poner la plataforma en un VPS (probada con la configuración de Docker de este repositorio).
Tiempo aproximado: 1–2 horas la primera vez.

## 0. Qué hace falta contratar

| Servicio | Recomendación | Coste aproximado |
|---|---|---|
| VPS | Hostinger KVM 2 (2 vCPU, 8 GB RAM) con **Ubuntu 24.04** | ~9 €/mes |
| Dominio | El que decida la Cátedra | ~10–15 €/año |
| Correo saliente | Brevo (plan gratuito, 300 correos/día) | 0 € |
| Copias externas | Backblaze B2 | ~1–2 €/mes |
| Pagos | Stripe (cuenta de la empresa) | Comisión por venta |

## 1. Preparar el servidor

Conéctate por SSH como root (Hostinger da la IP y la contraseña en su panel) y ejecuta, **de uno en uno**:

```bash
apt update && apt upgrade -y
adduser catedra                      # usuario de trabajo (no usar root a diario)
usermod -aG sudo catedra
```

Acceso por clave SSH en lugar de contraseña (desde tu ordenador):

```bash
ssh-copy-id catedra@IP_DEL_VPS
```

Ya dentro como `catedra`, desactiva el acceso por contraseña y el de root:

```bash
sudo sed -i 's/^#\?PasswordAuthentication .*/PasswordAuthentication no/; s/^#\?PermitRootLogin .*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh
```

> Antes de cerrar la sesión, comprueba en **otra** ventana que puedes entrar con la clave. Si no, revierte el cambio.

Cortafuegos y actualizaciones automáticas de seguridad:

```bash
sudo ufw allow OpenSSH && sudo ufw allow 80 && sudo ufw allow 443
sudo ufw enable
sudo apt install -y unattended-upgrades fail2ban
```

Docker:

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker catedra      # cerrar sesión y volver a entrar
```

## 2. Dominio

En el proveedor del dominio, crea registros **A** que apunten a la IP del VPS:

| Nombre | Tipo | Valor |
|---|---|---|
| `@` | A | IP del VPS |
| `www` | A | IP del VPS |
| `estadisticas` | A | IP del VPS |

## 3. Código y configuración

```bash
sudo mkdir -p /opt/catedra && sudo chown catedra: /opt/catedra
git clone https://github.com/Figueira205/CATEDRA.git /opt/catedra
cd /opt/catedra/plataforma
cp .env.example .env
nano .env
```

Rellena **todos** los valores. Para generar claves aleatorias:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Usa claves generadas así para `DJANGO_SECRET_KEY`, `POSTGRES_PASSWORD`, `UMAMI_DB_PASSWORD` y `UMAMI_APP_SECRET`
(solo letras, números, `-` y `_`: otros símbolos rompen la URL de la base de datos).

```bash
chmod 600 .env                       # solo lo puede leer el usuario catedra
```

## 4. Arrancar

```bash
docker compose up -d --build
docker compose ps                    # los cuatro servicios en «Up» / «healthy»
```

Caddy pide los certificados HTTPS automáticamente la primera vez (tarda unos segundos).

Crear el contenido inicial y el primer administrador:

```bash
docker compose run --rm -v /opt/catedra/web:/web:ro web python manage.py preparar_sitio --web /web
docker compose exec web python manage.py createsuperuser
```

Entra en `https://TU_DOMINIO/admin/`. El panel te pedirá activar la **verificación en dos pasos**
(Google Authenticator, Microsoft Authenticator o similar) antes de dejarte pasar.

En el panel: **Configuración → Sitios**: cambia el nombre de host `localhost` por tu dominio.

## 5. Stripe

1. En el panel de Stripe de la empresa → Desarrolladores → **Webhooks** → Añadir destino:
   - URL: `https://TU_DOMINIO/compras/stripe/webhook/`
   - Eventos: `checkout.session.completed`, `checkout.session.async_payment_succeeded`,
     `checkout.session.expired`, `charge.refunded`
2. Copia el **secreto de firma** (`whsec_…`) en `.env` → `STRIPE_WEBHOOK_SECRET`.
3. Copia la **clave secreta** en `.env` → `STRIPE_SECRET_KEY`. Empieza con la de **prueba** (`sk_test_…`),
   haz una compra con la tarjeta `4242 4242 4242 4242` y, cuando todo funcione, cámbiala por la real (`sk_live_…`)
   y repite el paso 1 en modo real.
4. Aplica los cambios: `docker compose up -d`

Las ventas aparecen en Stripe como «Cátedra · título», separadas del resto de negocios de la empresa.
Stripe envía la factura al comprador. **Consultad con la gestoría** el IVA (libros electrónicos 4 %, formación)
y si hay que configurar Stripe Tax.

## 6. Analítica (Umami)

1. Entra en `https://estadisticas.TU_DOMINIO` con `admin` / `umami` y **cambia la contraseña al momento**.
2. Añade el sitio web con tu dominio y copia su *Website ID* en `.env` → `UMAMI_WEBSITE_ID`.
3. `UMAMI_SCRIPT_URL=https://estadisticas.TU_DOMINIO/script.js` y `docker compose up -d`.

Umami muestra visitas por país, región y ciudad sin cookies (no hace falta banner de consentimiento para ella).

## 7. Copias de seguridad

```bash
sudo apt install -y rclone
rclone config                        # crea un remoto «b2» con los datos de Backblaze
echo 'RCLONE_DESTINO=b2:catedra-copias' >> .env
./scripts/copia_seguridad.sh         # primera copia a mano: comprueba que termina bien
crontab -e                           # y añade:
# 30 3 * * * cd /opt/catedra/plataforma && ./scripts/copia_seguridad.sh >> /home/catedra/copias.log 2>&1
```

**Prueba a restaurar una copia al menos una vez** (en otro servidor o en local): una copia que nunca se ha
restaurado no está comprobada. Restaurar: `./scripts/restaurar_copia.sh copias/AAAA-MM-DD_HHMM`.

## 8. Actualizar la web

```bash
cd /opt/catedra && git pull
cd plataforma && docker compose up -d --build
```

Las migraciones se aplican solas al arrancar. Si algo falla, vuelve a la versión anterior con
`git checkout <commit-anterior>` y `docker compose up -d --build`.

## 9. Comandos útiles

| Para… | Comando |
|---|---|
| Ver registros | `docker compose logs -f web` |
| Reiniciar la web | `docker compose restart web` |
| Consola de Django | `docker compose exec web python manage.py shell` |
| Espacio en disco | `df -h` y `docker system df` |
| Limpiar imágenes viejas | `docker image prune -f` |
