# How To Use

## 1. Preparación
- Clona este repositorio dentro de tu workspace.
- Copia `PROJECT_BASE/.env.example` a `PROJECT_BASE/.env` y completa valores reales (sin placeholders).
- Instala dependencias listadas en `PROJECT_BASE/requirements.txt` o usa los contenedores.

Notas importantes:
- El proyecto está optimizado para correr con `docker-compose` (PostgreSQL incluido).
- `PROJECT_BASE/.env` no debe subirse al repo (se ignora por `.gitignore`).

## 2. Guiar a la IA
- Escoge el prompt adecuado en la carpeta `PROMPTS` según el rol que estés emulando.
- Antes de usar cualquier prompt, lee `PROMPTS/00_CONTEXT.md` (contexto canónico y reglas no negociables).
- Ajusta el contexto con información del cliente, métricas y restricciones reales.

## 3. Crear el proyecto
- Ejecuta `SCRIPTS/create_project.sh` para generar un nuevo paquete basado en `PROJECT_BASE` (en macOS/Linux).
- En Windows, replica los pasos manualmente siguiendo `SCRIPTS/first_run.md`.

## 4. Personalizar
- Usa `SCRIPTS/rename_project.py` para actualizar nombres de módulos, apps y settings.
- Agrega tus apps dentro de `PROJECT_BASE/apps` y plantillas en `PROJECT_BASE/templates`.

## 5. Ejecutar
- `docker-compose up --build` levanta toda la pila (web + db + worker si lo configuras).
- `python manage.py runserver` funciona para pruebas rápidas fuera de contenedor.

### Redis (presente pero reservado)

Redis está incluido en `PROJECT_BASE/docker-compose.yml` por estándar de plataforma, pero **no es un requisito funcional hoy**.

¿Para qué se reserva?
- Cache (por ejemplo, `django-redis`) para queries costosas o data de sesiones.
- Cola de trabajos (Celery/RQ) para tareas largas (exportaciones masivas, OCR, scraping, IA, etc.).
- Rate limiting, locks distribuidos y deduplicación de jobs.

¿Por qué está presente aunque no se use?
- Para que el entorno base sea reproducible y esté listo para crecer sin rediseñar la infraestructura.
- Para evitar que cada proyecto “reinvente” la pila cuando llegue el momento.

Si en tu proyecto aún no lo necesitas:
- Puedes dejarlo levantado sin usarlo (costo local mínimo).
- O puedes comentar el servicio `redis` y el `depends_on` en `docker-compose.yml` (cuando estés creando tu proyecto derivado).

### Cómo encajan CRUD + Modales + Export

Esta plantilla usa SSR + HTMX con un contrato de contexto simple:

- **CRUD List Page**: `templates/crud/list.html`
	- Renderiza layout + toolbar + filtros.
	- La tabla vive en `#crud-table` y se carga por HTMX.

- **CRUD Table Partial**: `templates/crud/_table.html`
	- Soporta ordenamiento y paginación vía HTMX.
	- Acciones por fila usan `templates/crud/_row_actions.html`.

- **Modales HTMX**: `templates/partials/modals/*` + `static/js/modals.js`
	- Los botones abren un modal con `hx-get` a un endpoint.
	- Los forms postean con `hx-post`.
	- En éxito, el backend dispara `HX-Trigger: {"modalClose": true}` y refresca tabla (por evento u OOB swap según el flujo).

- **Exportaciones Server-Side**: `PROJECT_BASE/apps/core/services/exporting.py`
	- CSV/XLSX/PDF se generan desde el queryset filtrado/ordenado.
	- El dropdown “Exportar” preserva el querystring (filtros/orden).

## 6. Scaffolding CRUD (Copilot-first)

Objetivo: crear un nuevo CRUD **en <10 minutos** usando Copilot y una `CrudConfig` como fuente de verdad, sin auto-discovery ni magia.

Guía paso a paso completa: `TUTORIAL_CRUD.md`.

### Estructura canónica (por app)

Dentro de `PROJECT_BASE/apps/<app_slug>/`:

- `models.py` (modelo(s) del CRUD)
- `forms.py` (ModelForm(s) usados por modales)
- `crud_config.py` (única fuente de verdad declarativa)
- `views.py` (list/table + create/edit/delete + export)
- `urls.py` (rutas estables)
- `apps.py` (registro explícito en `ready()` llamando `register()`)
- `migrations/`

### Contrato de querystring (para TODO CRUD)

Estos parámetros deben ser los “deep-links” reproducibles del CRUD:

- `q`: búsqueda (texto)
- filtros: uno por cada `FilterDef.name` declarado (ej. `status`, etc.)
- `sort`: key de columna (debe coincidir con `ColumnDef.key`)
- `dir`: `asc` | `desc`
- `page`: paginación

Regla de oro:

- list/table/export deben parsear igual (`config.parse_params(request)`)
- list/table/export deben filtrar/ordenar igual (`config.queryset_for_list(request=request, params=params)`)
- export ignora paginación (exporta “todo lo que matchea”), pero respeta filtros + ordering

### Naming conventions

- `CRUD_SLUG_<ENTITY> = "<app_slug>.<plural_snake>"`
	- Regla: **siempre plural** y siempre `snake_case`.
	- Ejemplos: `items`, `invoices`, `purchase_orders`.
- Clase config: `<Entity>CrudConfig`
- Permisos declarativos (Django perms del modelo):
	- `permission_list = "<app_label>.view_<model>"`
	- `permission_create = "<app_label>.add_<model>"`
	- `permission_edit = "<app_label>.change_<model>"`
	- `permission_delete = "<app_label>.delete_<model>"`
- Permiso de export: por defecto hereda `permission_list` (`can_export = can_list`).

### URLs estándar (no cambiar)

Mantener estos `name=` porque el UI del kit asume esta forma:

- `list`: `/`
- `table`: `/table/`
- `create`: `/create/`
- `edit`: `/<int:id>/edit/`
- `delete`: `/<int:id>/delete/`
- `export_csv`: `/export/csv/`
- `export_xlsx`: `/export/xlsx/`
- `export_pdf`: `/export/pdf/`

### Pasos mínimos (checklist)

1) Crear modelo en `models.py`
2) Crear `ModelForm` en `forms.py`
3) Declarar `<Entity>CrudConfig` en `crud_config.py` + `register()`
4) Registrar en `apps.py` (en `ready()` llamar `register()`)
5) Crear `urls.py` con rutas estándar
6) Crear `views.py`:
	 - list/table: `build_list_context(config, request, crud_urls)` + `config.can_list()`
	 - exports: **usar `queryset_for_list()`** + metadata `export_*` con fallback
7) Agregar la app a `INSTALLED_APPS` + `makemigrations/migrate`

### Prompt canónico para Copilot

"""Actúa como Platform Engineer. Genera el skeleton completo de un CRUD SSR+HTMX usando el framework declarativo existente.

Reglas estrictas:
- No tocar templates del kit, no crear UI nueva.
- No tocar el motor de export.
- No auto-discovery: registro explícito en `apps.py` (`ready()` llama a `register()`).
- List/table deben usar `build_list_context()`.
- Exports deben usar `config.parse_params()` + `config.queryset_for_list(request=request, params=params)` (sin paginar) y leer `export_*` desde la config.

INPUT:
- app_slug: <app_slug>
- entity: <EntityName>
- model: <ModelName>
- fields: <lista de campos>
- list_columns: <orden + labels + order_by>
- search_fields: <...>
- filters: <...>
- exports: formats + export_fields + headers

OUTPUT:
- apps/<app_slug>/crud_config.py
- apps/<app_slug>/views.py
- apps/<app_slug>/urls.py
- apps/<app_slug>/forms.py
- apps/<app_slug>/apps.py
Incluye al final un "Manual test checklist"."""

## 7. Documentar
- Toda decisión clave debe registrarse en `PROMPTS/06_DOCUMENTATION.md` o en un archivo derivado.
- Decisiones de plataforma y “por qué” viven en `PLATFORM_DECISIONS.md`.
