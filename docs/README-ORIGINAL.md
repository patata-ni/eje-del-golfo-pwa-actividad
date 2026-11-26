# Transportes EJE del Golfo · Proyecto DevOps

**Integrantes:** Tania Gonzalez y Alondra Aimee Garcia Gomez.

Sistema web Laravel 12 y MySQL para consulta de rutas y salidas, autenticación de clientes, administración de operaciones de transporte, inventario y mantenimiento de unidades. Se conserva el proyecto proporcionado y se añaden migraciones reproducibles, validación por roles, pruebas y entrega continua.

## Enlaces

- Repositorio: https://github.com/patata-ni/eje-del-golfo-devops
- Pruebas: https://eje-web-pruebas.up.railway.app
- Preproducción: https://eje-web-preproduccion.up.railway.app
- Pipeline: https://github.com/patata-ni/eje-del-golfo-devops/actions/workflows/deploy.yml
- Versión de cada ambiente: agregar `/version` a su URL.

Los enlaces son los destinos configurados. El informe de entrega registra qué ejecución y versión se comprobaron realmente; no debe inferirse un despliegue exitoso sólo por existir la configuración.

## Organización

| Carpeta o archivo | Función |
|---|---|
| app/Models | Tablas y relaciones de transporte |
| app/Http/Controllers | Lógica de clientes, administración y taller |
| app/Http/Middleware | Control de acceso por rol |
| resources/views | Pantallas Blade |
| public/css y public/images | Diseño e imágenes originales |
| database/migrations | Instalación reproducible de tablas y relaciones |
| database/seeders | Roles y cuentas/datos de revisión habilitados por variables |
| tests/Feature | Pruebas Laravel de autenticación y operaciones |
| tests/browser | Pruebas Playwright sobre la interfaz real |
| Dockerfile | Artefacto de aplicación con PHP, Apache y frontend |
| .github/workflows/deploy.yml | Integración, construcción y entrega a Railway |
| docs | Proceso CD, rúbrica, reproducción e incidencias |

## Reproducción

Consulta [REVISION-Y-CAMBIOS](docs/REVISION-Y-CAMBIOS.md) para los requisitos y comandos locales. Las credenciales de revisión se entregan por separado y no se incorporan al código ni a la imagen.

## Ramas

- main: versión que se entrega automáticamente a pruebas y preproducción.
- develop: integración sin despliegue público.
- feature/*: funcionalidades propuestas por PR.
- codex/*: cambios asistidos, con los mismos controles de validación.

Se protege main/develop mediante PR y controles automáticos. La aprobación de otra cuenta debe configurarse según la disponibilidad del equipo; no se afirma que una revisión humana ocurrió si no está registrada.

## Pipeline

Windows y Linux validan las pruebas de Laravel y la interfaz. Linux añade Firefox, WebKit y móvil emulado. Después se construye una imagen Docker, se ejecuta con MySQL real y se prueba antes de publicarla por digest. Railway recibe ese digest en pruebas; sólo tras verificar la revisión y superar los casos remotos se promueve el mismo digest a preproducción y se comprueba de nuevo. Los reportes se entregan como artefactos de Actions.

Documentación: [PROCESO-CD](docs/PROCESO-CD.md), [MATRIZ-RUBRICA](docs/MATRIZ-RUBRICA.md) y [PROBLEMAS-Y-SOLUCIONES](docs/PROBLEMAS-Y-SOLUCIONES.md).

## Alcance y límites

El boleto es imprimible; no se ha añadido un procesador de pagos ni persistencia de reservas de asientos. Google OAuth, mapas y clima requieren configuración de sus proveedores. Las pruebas móviles emuladas no sustituyen un dispositivo físico. La entrega llega a preproducción; una liberación a producción requiere una decisión posterior.

El SQL original con registros, contraseñas y sesiones no se publica. Se importa de manera privada en bases nuevas de Railway; las sesiones y cachés previas se excluyen y se crean accesos nuevos de revisión. La estructura necesaria para instalar se representa con migraciones.
