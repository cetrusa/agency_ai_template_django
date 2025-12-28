"""Django settings for the base dashboard template.

Principios:
- Server-Driven UI (Templates) + HTMX
- Sin Node.js / sin bundlers / sin SPA
- Static assets simples (CSS tokens + CSS modular + JS mínimo)

Nota: este archivo es deliberadamente "monolítico" para facilitar clonación.
Si en el futuro se desea, puede dividirse en settings/base.py, settings/dev.py, etc.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Permite cargar variables desde .env en desarrollo/plantilla.
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"

ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",") if h.strip()]


INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 1st party apps
    "apps.dashboard",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Templates reutilizables a nivel proyecto (no por app).
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# Database (plantilla lista para docker-compose).
# En proyectos reales se recomienda ajustar parámetros (pooling, timeouts, etc.).
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DJANGO_DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.getenv("POSTGRES_DB", os.getenv("DJANGO_DB_NAME", "dashboard")),
        "USER": os.getenv("POSTGRES_USER", os.getenv("DJANGO_DB_USER", "user")),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", os.getenv("DJANGO_DB_PASSWORD", "password")),
        "HOST": os.getenv("DJANGO_DB_HOST", "db"),
        "PORT": os.getenv("DJANGO_DB_PORT", "5432"),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es"
TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"
# En modo plantilla/desarrollo: los assets viven en /static.
STATICFILES_DIRS = [BASE_DIR / "static"]
# En producción (o dentro del contenedor) se puede ejecutar collectstatic.
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Seguridad mínima para plantilla; endurecer en proyectos reales.
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()
]
