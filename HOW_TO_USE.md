# Guía de Uso y Despliegue

Esta guía detalla paso a paso cómo configurar, ejecutar y administrar la plataforma **Agency AI Dashboard**.

---

## 1. Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

*   **Git**: Para clonar el repositorio.
*   **Docker Desktop**: Recomendado para ejecutar la base de datos y servicios auxiliares (Redis).
*   **Python 3.10+**: Si planeas ejecutar el backend localmente (fuera de Docker).
*   **VS Code (Opcional)**: Recomendado con extensiones de Python y Django.

---

## 2. Instalación Inicial

### Paso 1: Clonar el Repositorio
```bash
git clone <url-del-repo>
cd AI_DJANGO_DASHBOARD_AGENCY_V1
```

### Paso 2: Configurar Variables de Entorno
Copia el archivo de ejemplo y configura tus credenciales locales.
```bash
cd PROJECT_BASE
cp .env.example .env
# En Windows: copy .env.example .env
```
> **Nota:** Revisa el archivo `.env`. Para desarrollo local rápido sin Docker, puedes cambiar `DJANGO_DB_ENGINE` a `django.db.backends.sqlite3`.

### Paso 3: Entorno Virtual (Solo ejecución local)
Si no vas a usar Docker para el contenedor web, crea un entorno virtual:
```bash
# En la raíz del proyecto
python -m venv .venv
# Activar en Windows
.venv\Scripts\activate
# Activar en Mac/Linux
source .venv/bin/activate

# Instalar dependencias
pip install -r PROJECT_BASE/requirements.txt
```

---

## 3. Inicialización de Base de Datos y Superusuario

La plataforma incluye un comando automatizado para configurar el entorno de desarrollo rápidamente.

### Opción A: Comando Automático (Recomendado)
Este comando crea las migraciones, las aplica, y genera una **Organización Demo** y un **Superusuario**.

```bash
cd PROJECT_BASE
python manage.py migrate
python manage.py bootstrap_dev --with-samples
```

**¿Qué hace este comando?**
1.  Crea una organización llamada "Demo Agency".
2.  Crea un superusuario (admin) con credenciales por defecto.
3.  Genera datos de prueba (si usas `--with-samples`).
4.  Imprime en consola el **Email** y **Password** generados. **¡Guárdalos!**

### Opción B: Creación Manual de Superusuario
Si prefieres hacerlo manualmente:
```bash
cd PROJECT_BASE
python manage.py migrate
python manage.py createsuperuser
```
Sigue las instrucciones en pantalla para definir email y contraseña.

---

## 4. Ejecutar el Proyecto

### Modo A: Docker (Full Stack)
Levanta la base de datos (PostgreSQL), Redis y el servidor Web.
```bash
# Desde la raíz del proyecto (donde está docker-compose.yml dentro de PROJECT_BASE)
cd PROJECT_BASE
docker-compose up --build
```
*   Accede a: `http://localhost:8000`

### Modo B: Híbrido (DB en Docker, Web Local)
Ideal para desarrollo rápido (debugging, hot-reload).

1.  Levanta solo la base de datos:
    ```bash
    cd PROJECT_BASE
    docker-compose up -d db
    ```
2.  Ejecuta el servidor Django localmente:
    ```bash
    # Asegúrate de tener el venv activado
    cd PROJECT_BASE
    python manage.py runserver
    ```
*   Accede a: `http://127.0.0.1:8000`

### Modo C: SQLite (Sin Docker)
Si no tienes Docker instalado, edita `.env` y asegura:
```ini
DJANGO_DB_ENGINE=django.db.backends.sqlite3
```
Luego ejecuta:
```bash
cd PROJECT_BASE
python manage.py migrate
python manage.py runserver
```

---

## 5. Primeros Pasos en la Plataforma

1.  **Login:** Ve a `/accounts/login/` e ingresa con las credenciales generadas en el paso 3.
2.  **Configuración de Empresa:**
    *   Navega a **Empresa** en el menú lateral.
    *   Haz clic en "Editar Configuración".
    *   Sube tu logo, define los colores de marca y redes sociales.
3.  **Gestión de Usuarios:**
    *   Ve a **Usuarios** para invitar miembros a tu organización.
4.  **Dashboard:**
    *   Revisa los KPIs y gráficos de ejemplo en la página de inicio.

---

## 6. Scripts de Utilidad

En la carpeta `SCRIPTS/` encontrarás herramientas útiles:

*   `start.bat`: Inicia el entorno Docker (Windows).
*   `stop.bat`: Detiene todos los contenedores del proyecto de forma segura.
*   `create_project.sh`: (Linux/Mac) Scaffolding para iniciar un proyecto limpio basado en este template.

---

## 7. Solución de Problemas Comunes

**Error: "Connection refused" a la base de datos**
*   Asegúrate de que el contenedor `db` esté corriendo (`docker ps`).
*   Verifica que las credenciales en `.env` coincidan con `docker-compose.yml`.

**Error: "Relation does not exist"**
*   Faltan aplicar migraciones. Ejecuta `python manage.py migrate`.

**Olvide mi contraseña de admin**
*   Ejecuta: `python manage.py changepassword <tu_email>`

---

## 8. Arquitectura y Desarrollo

### Estructura de Apps
*   `apps/core`: Lógica base, modelos globales (`GlobalConfig`), utilidades CRUD.
*   `apps/dashboard`: Vista principal y widgets.
*   `apps/organization_admin`: Gestión de la configuración de la empresa.
*   `apps/users_admin`: Gestión de usuarios y roles.
*   `apps/crud_example`: Ejemplo canónico de implementación CRUD.

### Crear un nuevo CRUD
Consulta `TUTORIAL_CRUD.md` para una guía detallada sobre cómo crear nuevos módulos usando el motor declarativo `CrudConfig`.


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
