# AI Django Dashboard Agency v1

Repositorio base para coordinar un flujo de trabajo asistido por IA orientado a construir **Dashboards Administrativos SSR** con **Django Templates + HTMX**.

Este repo incluye un `PROJECT_BASE/` listo para clonar, con:
- CRUD Kit Enterprise V1 (listado/tabla con filtros, orden y paginación)
- Sistema de modales reusable (HTMX)
- Export engine server-side (CSV/XLSX/PDF)

## Contenido
- **PROMPTS**: instrucciones curadas para cada rol del equipo asistido por IA.
- **PROJECT_BASE**: boilerplate inicial para un proyecto Django dockerizado.
- **SCRIPTS**: utilidades para clonar, renombrar y ejecutar la primera vez el proyecto.

## Cómo empezar
1. Lee `AGENCY_MANIFEST.md` para entender las reglas de colaboración.
2. Lee `PROMPTS/00_CONTEXT.md` (contexto canónico y reglas no negociables).
3. Revisa `HOW_TO_USE.md` para levantar el entorno y entender cómo encajan CRUD/modales/export.
4. Lee `PLATFORM_DECISIONS.md` para entender por qué el repo está diseñado así.
5. Sigue los pasos descritos en `SCRIPTS/first_run.md` para levantar el entorno local.

## Contribuir

- Guía de contribución: `CONTRIBUTING.md`
- Notas de release/cambios: `CHANGELOG.md`

## Onboarding DEV (sin UI)

En desarrollo (`DJANGO_DEBUG=1`) puedes bootstrapear datos demo con:

- `python PROJECT_BASE/manage.py bootstrap_dev --noinput --with-samples`

Esto crea una organización demo, un usuario dev, permisos para `crud_example.Item` y (opcional) items de ejemplo. **En `DEBUG=False` el comando se bloquea.**
