# EJE del Golfo · Actividad PWA

**Tania Gonzalez y Alondra Aimee Garcia Gomez**

Copia independiente de [EJE del Golfo DevOps](https://github.com/patata-ni/eje-del-golfo-devops), con una PWA de registro y seguimiento de incidencias de unidades. El repositorio original y sus ambientes no se modifican.

- Aplicación: https://patata-ni.github.io/eje-del-golfo-pwa-actividad/
- Código: https://github.com/patata-ni/eje-del-golfo-pwa-actividad
- Pruebas y despliegue: https://github.com/patata-ni/eje-del-golfo-pwa-actividad/actions
- [Guía de requisitos y exposición](docs/ACTIVIDAD-PWA.md)

La **bitácora PWA** permite registrar incidencias, adjuntar fotografía desde la cámara, obtener ubicación, consultar reportes sin internet, cambiar su estado y exportar los datos con evidencias. Se instala desde un navegador compatible. Utiliza App Shell con CSR, Service Worker, caché estática y dinámica, e IndexedDB.

## Ejecutar la PWA

Desde la raíz: `python -m http.server 8765 --directory public/pwa`; abrir `http://localhost:8765/`. Para publicar, el workflow de GitHub Pages ejecuta las validaciones y pruebas de navegador antes de desplegar `public/pwa` mediante HTTPS.

## Estructura

| Ruta | Contenido |
|---|---|
| `public/pwa` | Aplicación PWA autónoma y recursos locales |
| `public/pwa/icons` | Iconos PNG de 192/512 px y maskable |
| `tests/pwa` | Pruebas de persistencia offline, cámara, ubicación, exportación y móvil |
| `scripts/validate-pwa.py` | Validación del manifiesto, iconos y recursos |
| `.github/workflows/pwa-pages.yml` | Pruebas y despliegue de esta actividad |
| `app`, `resources`, `routes`, `database` | Sistema Laravel conservado en la copia |

## Comprobación

`python scripts/validate-pwa.py`

`npm ci && npx playwright install chromium && npx playwright test --config playwright-pwa.config.mjs`

## Alcance

La publicación en Pages ejecuta la bitácora estática, no PHP ni MySQL. Los datos se guardan localmente; no se sincronizan ni se envían a la empresa. El catálogo muestra rutas y unidades de demostración. La cámara y ubicación solicitan permisos al usarse. Las notificaciones de guardado son locales y opcionales.

El sistema Laravel permanece en el repositorio y contiene enlaces a `/pwa/index.html` desde sus paneles. Para ejecutarlo se necesitan PHP 8.2+, Composer y MySQL en una base independiente `ejegolfo_pwa_actividad`. Consultar [documentación del sistema original](docs/README-ORIGINAL.md) y [reproducción Laravel](docs/REVISION-Y-CAMBIOS.md). Los documentos de DevOps originales describen el proyecto de origen; la guía de esta actividad es `docs/ACTIVIDAD-PWA.md`.
