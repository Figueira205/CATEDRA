# Seguridad y protección de datos

Objetivo: seguridad sólida y proporcionada para una web con cuentas y pagos, sin llegar al nivel bancario.

## Qué está implementado

### Pagos
- **Stripe Checkout:** la tarjeta se introduce en la página de Stripe. Nuestro servidor nunca ve ni guarda datos
  de tarjeta, así que el cumplimiento de PCI DSS se reduce al mínimo (SAQ A).
- **Webhook firmado:** solo se aceptan avisos de Stripe con firma válida (`STRIPE_WEBHOOK_SECRET`).
- **Idempotente:** un aviso repetido no duplica compras; una restricción en la base de datos impide dos compras
  pagadas del mismo contenido por la misma persona.
- **Reembolsos:** un reembolso total en Stripe retira el acceso automáticamente.
- Las compras **no se borran nunca** (obligación contable): si alguien pide la baja, se anonimiza su cuenta.

### Cuentas
- Contraseñas con **Argon2** (algoritmo recomendado actualmente), mínimo 10 caracteres, sin contraseñas comunes.
- **Verificación de correo obligatoria** antes de poder entrar.
- **Límite de intentos** de inicio de sesión, registro y recuperación de contraseña (contra fuerza bruta).
- No se revela si un correo está registrado (contra enumeración de usuarios).
- **Verificación en dos pasos obligatoria** para todo el que pueda entrar al panel. Los estudiantes pueden activarla
  si quieren desde «Mi cuenta».

### Contenidos de pago
- Los libros se guardan **fuera de la carpeta pública** y sin URL directa: solo salen por la vista de descarga,
  que comprueba el acceso en cada petición (`Cache-Control: private, no-store`).
- Caddy bloquea `/media/documents/`: los documentos del panel también pasan siempre por Django.
- El enlace de las clases en directo nunca aparece en el HTML.

### Servidor y navegador
- **HTTPS** obligatorio, con renovación automática del certificado y **HSTS** de un año.
- **Content-Security-Policy** estricta: solo se ejecuta JavaScript servido por la propia web (sin scripts en línea).
- Cookies de sesión `Secure`, `HttpOnly` y `SameSite=Lax`; protección CSRF en todos los formularios.
- `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Cross-Origin-Opener-Policy`, `Permissions-Policy`.
- La base de datos no está expuesta a internet (solo la ven los contenedores).
- Secretos solo en `.env` (permisos 600), nunca en Git.

## Revisión antes de abrir al público

- [ ] `DJANGO_DEBUG=False` y `DJANGO_SECRET_KEY` generada (no la del ejemplo).
- [ ] `docker compose exec web python manage.py check --deploy` sin avisos importantes.
- [ ] Stripe en modo real: webhook creado en modo real y compra de prueba reembolsada correctamente.
- [ ] Contraseña de Umami cambiada.
- [ ] SSH solo con clave, sin root; `ufw` activo; `unattended-upgrades` activo.
- [ ] Copia de seguridad automática funcionando **y restaurada al menos una vez**.
- [ ] Todo el personal con 2FA y códigos de recuperación guardados.
- [ ] Textos legales revisados (ver abajo).
- [ ] Prueba en <https://securityheaders.com> y <https://www.ssllabs.com/ssltest/> (objetivo: A o superior).

## Mantenimiento

| Frecuencia | Tarea |
|---|---|
| Automática | Actualizaciones de seguridad del sistema (unattended-upgrades), certificados HTTPS, copias diarias |
| Mensual | `git pull` + `docker compose up -d --build` con dependencias revisadas; mirar `docker compose logs` |
| Trimestral | Actualizar versiones de `requirements.txt` dentro de su rama (ej. Django 5.2.x), ejecutar tests, desplegar |
| Anual | Restaurar una copia de prueba; revisar quién tiene acceso al panel; revisar textos legales |
| Abril 2028 | Fin del soporte de Django 5.2: migrar a la siguiente versión LTS |

## Protección de datos (RGPD / LOPDGDD)

**Pendiente de revisión jurídica.** Los textos legales importados de la web estática son provisionales:

- **Aviso legal (LSSI):** debe identificar al **titular real del sitio y de las ventas: Inversiones Dafegobe**
  (razón social, NIF, domicilio, registro mercantil), no solo a la Cátedra.
- **Política de privacidad:** responsable del tratamiento, finalidades (cuenta, compras, boletín, contacto),
  bases jurídicas, plazos de conservación (compras: obligaciones fiscales), derechos y cómo ejercerlos.
- **Encargados del tratamiento** que deben figurar: Stripe (pagos), el proveedor del VPS (alojamiento),
  Brevo u otro (envío de correos), Backblaze (copias), Zoom/YouTube/Vimeo (clases).
- **Cookies:** la web solo usa cookies técnicas (sesión, CSRF). Umami no usa cookies. YouTube se incrusta en modo
  «sin cookies» (`youtube-nocookie.com`). Si se añade cualquier otra herramienta, revisar el banner.
- **Condiciones de venta:** necesarias antes de vender. Para contenido digital, informar de que al descargarlo
  o acceder se pierde el derecho de desistimiento de 14 días y recoger ese consentimiento.
- **Boletín:** doble confirmación (implementada) y baja en un clic en cada envío.
- Registro de actividades de tratamiento y, si procede, contrato con cada encargado.
