@echo off
SETLOCAL

echo =========================================
echo  Agency AI Platform - RESET DATABASE
echo =========================================
echo.
echo Este script eliminara la base de datos local (SQLite) para reiniciar el Setup Wizard.
echo.
echo [ADVERTENCIA] Se perderan todos los usuarios y configuraciones.
echo Asegurate de detener el servidor (Ctrl+C) antes de continuar.
echo.
pause

pushd "%~dp0..\PROJECT_BASE"

if exist "db.sqlite3" (
    echo [INFO] Eliminando db.sqlite3...
    del /F /Q "db.sqlite3"
    if exist "db.sqlite3" (
        echo [ERROR] No se pudo eliminar el archivo. El servidor podria estar usandolo.
        echo Deten 'python manage.py runserver' e intenta de nuevo.
        pause
        exit /b 1
    )
) else (
    echo [INFO] No se encontro db.sqlite3, se creara una nueva.
)

echo [INFO] Aplicando migraciones...
python manage.py migrate

echo.
echo [EXITO] Base de datos reseteada.
echo.
echo 1. Ejecuta: python manage.py runserver
echo 2. Ve a: http://127.0.0.1:8000/
echo.
pause
popd
