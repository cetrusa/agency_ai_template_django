# Changelog

Este proyecto sigue un esquema simple de versionado semántico: `vMAJOR.MINOR.PATCH`.

## v1.0.0

### Incluido

- **Organization Admin Redesign**: Transformación del módulo de organización en un panel de configuración global (Branding, Colores, Contacto, Redes Sociales).
- **GlobalConfig Model**: Implementación de modelo Singleton para gestión centralizada de la configuración de la instancia.
- **UI Improvements**: Mejoras en Login (iconos, toggle password) y Dashboard.
- Django SSR (Templates) + HTMX como base (sin SPA, sin Node)
- CRUD Kit Enterprise V1 (list + table partial) con filtros/orden/paginación
- Modales HTMX reutilizables (forms + confirm)
- Export engine server-side: CSV / XLSX / PDF
- CRUD declarativo (v1.0): `CrudConfig` como fuente de verdad
  - List/table via engine declarativo
  - Forms + metadata de modales declarativas
  - Permisos declarativos (basado en Django perms; export hereda de list)
  - Exports declarativos via `CrudConfig` reutilizando el motor de export
- Base org-ready (mono-DB): `Organization` + `Membership` (sin UI de switching)
- Comando de onboarding DEV: `python manage.py bootstrap_dev` (solo `DEBUG=True`)
- Documentación de plataforma: prompts, decisiones y guía de scaffolding

### Excluido (intencional)

- Generadores / CLI / scaffolding automático
- UI de multi-tenant (selector de org) y RBAC avanzado
- Row-level permissions
- Workers/colas (Celery/RQ) como parte funcional (Redis está reservado)
- API/SPA/bundlers

### Upgrade notes

- No aplica (primera versión).

## Guía de tags

- Formato: `vMAJOR.MINOR.PATCH`
- Cuándo incrementar:
  - MAJOR: cambios incompatibles (breaking)
  - MINOR: nuevas features compatibles
  - PATCH: fixes compatibles y cambios docs/tooling
