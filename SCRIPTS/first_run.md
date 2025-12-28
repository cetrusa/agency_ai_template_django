# First Run Guide

1. Dirígete a `PROJECT_BASE`.
2. Crea un entorno virtual: `python -m venv .venv`.
3. Activa el entorno (`.venv\Scripts\activate` en Windows, `source .venv/bin/activate` en Unix).
4. Instala dependencias: `pip install -r requirements.txt`.
5. Copia `.env.example` a `.env` y ajusta credenciales.
6. Ejecuta migraciones iniciales: `python manage.py migrate`.
7. Crea superusuario: `python manage.py createsuperuser`.
8. Levanta el servidor: `python manage.py runserver 0.0.0.0:8000`.
9. Para usar contenedores: `docker-compose up --build`.
10. Documenta cualquier problema en `PROMPTS/06_DOCUMENTATION.md`.
