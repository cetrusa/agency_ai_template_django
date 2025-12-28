# How To Use

## 1. Preparación
- Clona este repositorio dentro de tu workspace.
- Copia `PROJECT_BASE/.env.example` a `.env` y actualiza llaves.
- Instala dependencias listadas en `PROJECT_BASE/requirements.txt` o usa los contenedores.

## 2. Guiar a la IA
- Escoge el prompt adecuado en la carpeta `PROMPTS` según el rol que estés emulando.
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

## 6. Documentar
- Toda decisión clave debe registrarse en `PROMPTS/06_DOCUMENTATION.md` o en un archivo derivado.
