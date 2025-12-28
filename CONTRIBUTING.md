# Contributing

Este repositorio es una plantilla base y un set de prompts para un flujo de trabajo asistido por IA. Priorizamos consistencia, seguridad y cambios pequeños.

## Flujo de trabajo

- Ramas
  - `feature/<tema-corto>`: nuevas capacidades (siempre con alcance explícito)
  - `fix/<tema-corto>`: correcciones
  - `chore/<tema-corto>`: mantenimiento (docs, tooling, refactors menores)

- Commits
  - Convención sugerida (tipo Conventional Commits, versión simple):
    - `feat: ...`
    - `fix: ...`
    - `docs: ...`
    - `chore: ...`
    - `refactor: ...`
    - `test: ...`
  - Reglas:
    - Un commit = una intención
    - Mensajes en presente y claros (evitar “WIP”)

## Pull Request checklist

Antes de abrir PR, confirma:

- `python PROJECT_BASE/manage.py check` pasa
- Migraciones consistentes (si aplica): `python PROJECT_BASE/manage.py makemigrations --check --dry-run`
- Estilo/linters del repo (si están configurados) sin nuevos warnings relevantes
- Docs actualizadas si cambias comportamiento (README/HOW_TO_USE/PLATFORM_DECISIONS)
- No se introducen credenciales en el repo (`.env` debe seguir ignorado)

## Reglas para modificar el framework CRUD (apps/core/crud)

Cambios en el motor declarativo son “alto impacto”. Reglas:

- Mantener compatibilidad hacia atrás (no romper contracts del kit)
- No modificar templates del CRUD kit a menos que el PR sea exclusivamente de UI (y esté aprobado)
- No duplicar lógica entre list/table/export: todo debe fluir por `CrudConfig` cuando aplique
- Cambios deben ser:
  - explícitos (sin auto-discovery)
  - mínimos (MVP primero)
  - testeables (al menos `manage.py check` + smoke manual)

## Reglas para modificar prompts (PROMPTS/*)

- `PROMPTS/00_CONTEXT.md` es canónico: si hay conflicto, prevalece
- No prometer features no implementadas en `PROJECT_BASE`
- Mantener prompts “copilot-first”: instrucciones claras, duras y verificables
- Evitar ambigüedad: siempre declarar hard rules y “out of scope”

## Seguridad

- Prohibido subir:
  - `.env`, llaves, tokens, secretos
  - credenciales por defecto en modo producción
- Cualquier comando de bootstrap debe ser **DEBUG-only** y fallar en `DEBUG=False`.
