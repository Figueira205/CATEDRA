# Plataforma de la Cátedra de la Hispanidad

Web con gestor de contenidos, cuentas de estudiantes y venta de libros y clases.
Sustituirá a la web estática de `../web/` cuando se despliegue en el VPS.

| Pieza | Tecnología | Para qué |
|---|---|---|
| Aplicación | **Django 5.2 LTS** (Python 3.13) | Base: seguridad, usuarios, base de datos |
| Gestor de contenidos | **Wagtail 8** | Panel en `/admin/` para profesores y editores |
| Cuentas | **django-allauth** | Registro, verificación de correo, contraseñas, 2FA |
| Pagos | **Stripe Checkout** | La tarjeta se introduce en Stripe, nunca en nuestro servidor |
| Base de datos | PostgreSQL 17 (SQLite en local) | |
| Servidor | Docker + Caddy (HTTPS automático) + Gunicorn | |
| Analítica | Umami (autoalojado, sin cookies) | Visitas por país y región |

Guías:
- [docs/DESPLIEGUE.md](docs/DESPLIEGUE.md): poner la web en el VPS, paso a paso.
- [docs/MANUAL-EDITORES.md](docs/MANUAL-EDITORES.md): para profesores y editores (sin tecnicismos).
- [docs/SEGURIDAD.md](docs/SEGURIDAD.md): qué protege la plataforma y lista de revisión.

## Puesta en marcha en local (Windows, macOS o Linux)

```bash
cd plataforma
python -m venv .venv
.venv/Scripts/activate            # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
cp .env.example .env              # y en .env: DJANGO_SECRET_KEY=<clave>, DJANGO_DEBUG=True, SITIO_URL=http://localhost:8000
python manage.py migrate
python manage.py preparar_sitio   # crea las páginas con el contenido de ../web
python manage.py createsuperuser
python manage.py runserver
```

- Web: <http://localhost:8000> · Panel: <http://localhost:8000/admin/>
- Los correos (verificación de cuenta, boletín) se imprimen en la consola.
- En local no se exige 2FA para entrar al panel (`CATEDRA_2FA_OBLIGATORIO_PERSONAL=False` por defecto en `settings/dev.py`).

### Probar pagos en local

1. En [Stripe](https://dashboard.stripe.com/test/apikeys), modo prueba: copia la clave `sk_test_…` en `.env` como `STRIPE_SECRET_KEY`.
2. Instala la [CLI de Stripe](https://docs.stripe.com/stripe-cli) y reenvía los eventos:
   `stripe listen --forward-to localhost:8000/compras/stripe/webhook/`
   Copia el `whsec_…` que muestra en `.env` como `STRIPE_WEBHOOK_SECRET`.
3. Compra con la tarjeta de prueba `4242 4242 4242 4242`, cualquier fecha futura y cualquier CVC.

### Tests

```bash
python manage.py test
```

Cubren el flujo de compra, el webhook de Stripe (firmas, duplicados, reembolsos), las descargas protegidas,
la asistencia a directos, la 2FA del personal, el boletín y las cabeceras de seguridad. Se ejecutan también
en GitHub en cada envío (`.github/workflows/tests.yml`).

## Estructura

```
plataforma/
├── catedra/settings/   base.py (común) · dev.py (local) · production.py (VPS)
├── cuentas/            Usuario (login por correo), 2FA obligatoria para el personal, «Mi cuenta»
├── sitio/              Portada, páginas, actividades, novedades (blog), galería, contacto, boletín, buscador
├── biblioteca/         Publicaciones: libres, para registrados o de pago
├── formacion/          Clases grabadas y en directo; visualizaciones y asistencia
├── compras/            Producto (acceso y precio), Compra, Stripe, descargas protegidas, panel de ventas
├── templates/          Plantilla base, errores, pantallas de cuenta
├── static/catedra/     Diseño «Atlas vivo» (mismo CSS/JS que la web estática) + plataforma.css
├── docker/             entrypoint, Caddyfile, inicialización de PostgreSQL
└── scripts/            copia_seguridad.sh · restaurar_copia.sh
```

### Cómo encajan las piezas

- **Menú:** se genera solo. Aparecen las páginas hijas de la portada con «Mostrar en menús» marcado
  (pestaña *Promoción* en el panel). Así se añade o quita una sección sin tocar código.
- **Contenido de pago:** cualquier tipo de página que herede de `compras.models.Producto` gana los campos
  *acceso* (libre / registrados / pago) y *precio*, y se puede comprar. Hoy lo hacen `PublicacionPage` y `ClasePage`.
- **Acceso:** `Producto.usuario_tiene_acceso(user)` es la única comprobación; la usan las páginas, la descarga y los directos.
- **Compra:** `compras/servicios.py` crea la sesión de Stripe y la confirma (webhook + página de retorno, idempotente).
- **Archivos de pago:** se guardan en `PRIVATE_MEDIA_ROOT`, fuera de `/media/`. Solo salen por `/compras/descargar/<id>/`.
- **Directos:** el enlace de Zoom/Meet nunca aparece en el HTML: `/formacion/directo/<id>/` registra la asistencia y redirige.
- **Estadísticas:** «Estadísticas» en el panel (clases más vistas, asistentes); visitas por país/región en Umami.

## Convenciones

- Código y comentarios en español; nombres de Django/Wagtail en su forma original (`get_context`, `Page`…).
- Configuración solo por variables de entorno (`.env`); **nunca** secretos en el código ni en Git.
- Versiones acotadas en `requirements.txt`: actualizar a propósito, ejecutar los tests y desplegar.
