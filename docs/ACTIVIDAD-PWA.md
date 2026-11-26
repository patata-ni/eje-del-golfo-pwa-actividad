# EJE del Golfo — Actividad PWA

Autores: Tania Gonzalez y Alondra Aimee Garcia Gomez.

Esta entrega es una copia independiente del repositorio `patata-ni/eje-del-golfo-devops`, revisión `771701a34d64e3b162adf9ad06eaae1d176f9b55`. Conserva el sistema Laravel 12 y sus imágenes. Añade una bitácora autónoma en `public/pwa`, accesible mediante un enlace desde los paneles de la copia. La publicación estática corresponde a esta bitácora; el sistema Laravel requiere PHP 8.2+, Composer y una base MySQL independiente.

## Caso de uso

Personal de taller u operaciones registra una incidencia por unidad, su prioridad, descripción, fotografía y ubicación. Puede registrar y consultar reportes sin cobertura, marcarlos como atendidos y exportar la bitácora con evidencias en JSON. Los datos permanecen en el dispositivo; no se afirma sincronización con el backend ni envío automático a la empresa. Las unidades y rutas de práctica están identificadas como demostración.

## Requisitos y evidencia

| Requisito | Implementación | Cómo comprobarlo |
|---|---|---|
| Manifest e instalación | `public/pwa/manifest.json`, iconos PNG 192/512 y maskable, metadatos de color, idioma, ámbito y acceso directo | DevTools → Application → Manifest; menú Instalar o botón cuando el navegador emita `beforeinstallprompt` |
| Splash nativa | Nombre, icono de 512, background_color y theme_color | Instalar y abrir en Android compatible. La pantalla se genera por el sistema; no se simula con una imagen |
| App Shell responsiva y CSR | `index.html`, `app.css` y router de fragmentos en `app.js` | Navegar Resumen, Nueva incidencia, Mis incidencias, Rutas y Aplicación en escritorio y móvil |
| Ciclo del Service Worker | `sw.js`: install con precaché, activate con limpieza acotada, claim | Application → Service Workers. La actualización espera el cierre de las ventanas para proteger formularios abiertos |
| Caché estática y dinámica | Cache First para shell; Stale While Revalidate para `catalogo.json` | Application → Cache Storage; consultar Rutas tras desconectar la red |
| Persistencia asíncrona | IndexedDB `eje-golfo-pwa-actividad`, stores `incidencias` y `catalogos` | Crear incidencia, recargar y consultar sin conexión; abrir IndexedDB en DevTools |
| Cámara | `navigator.mediaDevices.getUserMedia`, captura a Blob, liberación de pistas | Nueva incidencia → Abrir cámara → Capturar. La carga de imagen es una alternativa |
| Geolocalización | `navigator.geolocation.getCurrentPosition`, coordenadas y precisión | Nueva incidencia → Obtener ubicación. Si se deniega, el registro sigue disponible |
| Notificación opcional | Notifications y `registration.showNotification` | Aplicación → Activar notificación de guardado. Es local, no Web Push |
| HTTPS y Git | Repositorio independiente y workflow `pwa-pages.yml` | Revisar enlace publicado y ejecución de Actions; consultar historial real de commits |

## Ejecución local

Para la PWA autónoma, desde la raíz del proyecto: `python -m http.server 8765 --directory public/pwa`. Abrir `http://localhost:8765/`. HTTPS o localhost son necesarios para Service Worker y cámara. No abrir index.html con file://.

Para Laravel: seguir `docs/README-ORIGINAL.md` y `docs/REVISION-Y-CAMBIOS.md`, instalar dependencias y usar una base nueva `ejegolfo_pwa_actividad`. No reutilizar las variables ni credenciales del proyecto original. La PWA se encuentra en `/pwa/index.html` en ese servidor.

## Pruebas

`python scripts/validate-pwa.py` valida PNG, dimensiones, manifiesto y archivos. `node --check` valida los módulos JavaScript. Las pruebas `tests/pwa/bitacora.spec.mjs` verifican guardado y cambios con recarga offline, eliminación, cámara y ubicación simuladas, permisos denegados, escape de HTML, exportación y ancho móvil. Ejecutar `npm ci`, `npx playwright install chromium` y `npx playwright test --config playwright-pwa.config.mjs`. El workflow ejecuta estas pruebas antes de desplegar. Los permisos y la instalación final deben comprobarse también en un teléfono real.

Las pruebas de cámara en CI utilizan un MediaStream sintético generado por canvas y entregado mediante un reemplazo de getUserMedia, porque el servidor de pruebas no tiene cámara física. La captura en canvas, el Blob, el almacenamiento y la recarga se ejercitan realmente. La ubicación usa coordenadas ficticias del navegador de pruebas; no se captura la ubicación personal de las autoras.

## Prueba manual para exposición

1. Abrir la PWA por HTTPS, esperar el mensaje de disponibilidad offline y visitar Rutas.
2. Crear una incidencia y adjuntar foto y ubicación autorizando los permisos.
3. Activar Offline en DevTools → Network; recargar la aplicación.
4. Comprobar que la interfaz, el catálogo y el reporte siguen visibles. Crear un segundo reporte offline.
5. Marcar un reporte como atendido, recargar y comprobar que el estado persiste.
6. Volver a conectar, exportar la bitácora y abrir el archivo JSON.
7. Instalar desde el navegador compatible y abrir desde el icono del dispositivo.

## Límites

GitHub Pages ejecuta la PWA estática; no ejecuta Laravel, PHP ni MySQL. Los reportes son locales por diseño y no equivalen a incidencias guardadas en el servidor original. La cámara y geolocalización requieren dispositivo, permisos y disponibilidad; GPS puede funcionar sin red, pero no se garantiza obtener posición sin cobertura. IndexedDB puede ser eliminado por el usuario o por el navegador. No se altera el original ni sus despliegues. Los commits nuevos reflejan el trabajo realizado en esta actividad, sin fechas simuladas.
