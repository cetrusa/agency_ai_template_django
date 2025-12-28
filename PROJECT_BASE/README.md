# PROJECT_BASE

Plantilla Django SSR (Templates) + HTMX para dashboards administrativos.

## Qué incluye (implementado)

- UI base con Bootstrap 5 + estilos/tokens del proyecto.
- CRUD Kit Enterprise V1 (listado + tabla partial con filtros/orden/paginación).
- Sistema de modales reusable (HTMX) para formularios y confirmaciones.
- Export engine server-side (CSV/XLSX/PDF).
- docker-compose con PostgreSQL y Redis (Redis reservado para uso futuro).

## Qué NO incluye todavía (intencional)

- Automatización CRUD declarativa (tipo Backpack). Se diseña primero, se implementa después.
- Multi-tenant y RBAC empresarial.
- Background workers (Celery/RQ) y colas.

## Uso

Consulta:
- `PROMPTS/00_CONTEXT.md` para filosofía y reglas.
- `HOW_TO_USE.md` para levantar el entorno.
- `PLATFORM_DECISIONS.md` para decisiones explícitas.
