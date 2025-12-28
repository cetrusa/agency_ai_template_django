# PLATFORM_DECISIONS

Este archivo hace explícitas decisiones que el repositorio ya aplica en la práctica.

Regla: este documento **no es un roadmap**. No promete features no implementadas.

---

## Decisiones principales (y por qué)

### 1) HTMX + Templates (no SPA)

**Decisión**: UI server-driven con Django Templates + HTMX.

**Por qué**:
- Mantener una base SSR simple, audit-able y fácil de heredar.
- Evitar complejidad de build tooling (Node/bundlers) en una plantilla de agencia.
- Interactividad incremental: filtros, paginación, modales y refresh parcial sin SPA.

**Consecuencia**:
- El “contrato” entre backend y templates es explícito (context dicts).
- La lógica de UI debe permanecer en el servidor; JS solo para wiring mínimo.

---

### 2) Mono-DB ahora (multi-tenant después)

**Decisión**: una base de datos por proyecto (modelo mono-DB) como punto de partida.

**Por qué**:
- Simplifica onboarding, migraciones y observabilidad.
- Permite construir primero el producto y el kit UI con estabilidad.

**Consecuencia**:
- Multi-tenant y reglas de scoping se diseñan como “plug-in” futuro (queryset scoping + policies), sin romper el kit.

---

### 3) CRUD Kit antes de automatización declarativa

**Decisión**: estabilizar primero un CRUD Kit reusable (UI + contratos) y una app de referencia.

**Por qué**:
- La automatización declarativa sin una UI estable termina generando “magia frágil”.
- Un kit reusable reduce decisiones repetitivas y fija patrones (filtros, paginación, modales, export).

**Consecuencia**:
- La automatización (tipo Backpack-like `CrudConfig`) se diseña primero y se implementa después.

---

### 4) Exportaciones 100% server-side

**Decisión**: CSV/XLSX/PDF se generan en el servidor desde el queryset filtrado/ordenado.

**Por qué**:
- Consistencia: lo que ves en el listado coincide con lo que exportas.
- Seguridad: autorización y scoping viven en el servidor.
- Evita duplicar lógica de filtros/formatos en el cliente.

**Consecuencia**:
- Export engine es un servicio reusable.
- En el futuro, exportaciones masivas pueden ir a background jobs (Redis + worker), pero hoy son síncronas.

---

### 5) Redis incluido pero reservado

**Decisión**: Redis está en docker-compose como dependencia de plataforma, aunque el código no lo use todavía.

**Por qué**:
- Preparar el “suelo” para cache, colas y locks distribuidos.
- Evitar rediseños de infraestructura en etapas tempranas.

**Consecuencia**:
- No debe asumirse Redis como requisito funcional hoy.

---

## Lo que intencionalmente NO está incluido todavía

- Automatización CRUD declarativa (framework tipo Backpack) — diseño primero, implementación después.
- Multi-tenant completo (orgs/tenants, scoping global, aislamiento fuerte).
- RBAC/ABAC empresarial completo (policies por módulo, auditoría, delegación).
- Background workers (Celery/RQ) y orquestación de tareas.
- WebSockets / real-time.
- Una API pública completa (DRF está disponible como opción, pero no se promete como feature lista).

---

## Reglas de alcance (anti-deriva)

- No introducir SPA/Node/bundlers en el core.
- No refactorizar el CRUD Kit “porque sí”. Primero estabilizar contratos; luego evolucionar.
- Documentación siempre debe reflejar el estado real del repo (sin promesas).
