# 00_CONTEXT — Contexto canónico de la plataforma

Este documento es la **fuente única de verdad** del repositorio.

Regla: **todo prompt en `PROMPTS/` debe referenciar este archivo** antes de pedir trabajo.

---

## Qué es este repositorio

Una plantilla base para una “AI Agency” enfocada en construir **Dashboards Administrativos profesionales** en **Django SSR** (Templates) con **HTMX**.

Este repo incluye un `PROJECT_BASE/` listo para clonar y convertir en un producto real.

---

## Filosofía del proyecto (no negociable)

- **Server-Driven UI**: Django Templates + HTMX. No SPA.
- **Estabilidad sobre magia**: primero un kit UI/CRUD consistente; después (en fases futuras) automatización declarativa.
- **Contrato explícito**: los templates reutilizables consumen un “context contract” (dicts/keys concretos). No lógica compleja en templates.
- **Cambios mínimos**: evitar refactors amplios; preferir cambios localizados y verificables.
- **Seguridad por defecto**: secretos fuera del repositorio; sin credenciales por defecto en producción.
- **Reutilización real**: componentes/partials reutilizables (CRUD kit, modales, export).

---

## Stack y decisiones técnicas

- **Backend**: Django 5.x (SSR).
- **UI**: Bootstrap 5 + CSS modular propio (tokens/utility CSS existente).
- **Interacción**: HTMX (hx-get/hx-post, partial swaps, HX-Trigger).
- **DB**: PostgreSQL (docker-compose como camino principal).
	- SQLite es **posible** solo si se configura explícitamente por env (no es el default).
- **Redis**: presente en docker-compose para **uso futuro** (cache, cola, rate limiting, locks). No es requisito funcional hoy.
- **Exportaciones**: server-side (CSV/XLSX/PDF) a partir del queryset filtrado/ordenado.
- **Contenedores**: Docker + docker-compose para reproducibilidad.

---

## Componentes “core” ya estables

- **CRUD Kit Enterprise V1**: `templates/crud/*` + `static/js/crud.js`.
- **Modal System (HTMX)**: `templates/partials/modals/*` + `static/js/modals.js`.
- **Export engine**: `PROJECT_BASE/apps/core/services/exporting.py`.
- **Reference app**: `PROJECT_BASE/apps/crud_example/` (patrón de referencia, no “framework”).

---

## Reglas para agentes IA (cómo deben comportarse)

- Antes de tocar código o docs, **leer**:
	- `PROMPTS/00_CONTEXT.md`
	- los archivos relevantes del área a modificar
- **Respetar el scope** del paso actual.
	- Si un paso dice “design only” o “docs only”, no implementar código.
- No modificar el CRUD Kit, modales base o tokens CSS salvo que el usuario lo pida explícitamente.
- No introducir:
	- SPA, Node.js, bundlers, frameworks JS
	- automatización/“magic” de CRUD prematura
	- nuevas páginas o UI no solicitadas
- Entregables:
	- cambios concretos y verificables
	- sin promesas de features no implementadas
	- documentación coherente con el estado real del repo

---

## Glosario mínimo

- **CRUD Kit**: templates + JS que renderizan listado/tabla con filtros, paginación y acciones.
- **Context contract**: keys requeridas por los templates (`crud_urls`, `columns`, `items`, `current_filters`, `page_obj`, `qs`, etc.).
- **OOB swap**: actualización HTMX “out-of-band” para refrescar `#crud-table` sin recargar layout.
