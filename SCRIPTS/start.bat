@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo =========================================
echo  Agency AI Platform - START
echo =========================================

:: 1. Verificar Docker
docker info >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [INFO] Docker no está activo. Intentando iniciar Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo [INFO] Esperando a que Docker inicie...
    timeout /t 15 >nul
)

:: 2. Verificar nuevamente Docker
docker info >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker no está disponible. Abortando.
    echo Asegúrate de que Docker Desktop esté instalado y corriendo.
    pause
    exit /b 1
)

echo [OK] Docker activo.

:: 3. Moverse a PROJECT_BASE
pushd "%~dp0..\PROJECT_BASE" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] No se pudo acceder a PROJECT_BASE.
    pause
    exit /b 1
)

:: 4. Levantar servicios base (db + web)
echo [INFO] Construyendo y levantando servicios (db, web)...
docker compose up --build -d web db

IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Error levantando contenedores.
    popd
    pause
    exit /b 1
)

:: 5. Esperar que BD este lista
echo [INFO] Esperando a que la base de datos este lista...
timeout /t 5 /nobreak >nul

:: 6. Ejecutar migraciones
echo [INFO] Ejecutando migraciones...
docker compose exec web python manage.py migrate
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fallo en migraciones.
    popd
    pause
    exit /b 1
)

:: 7. Bootstrap de desarrollo
echo [INFO] Bootstrap de desarrollo (empresa + usuario demo)...
docker compose exec web python manage.py bootstrap_dev --noinput --with_samples --samples 10

:: 8. Mostrar estado
echo.
echo =========================================
echo  Contenedores activos:
echo =========================================
docker compose ps

echo.
echo =========================================
echo  PROYECTO LEVANTADO
echo =========================================
echo.
echo  URL:  http://localhost:8000
echo.
echo  Credenciales: ver output de bootstrap_dev arriba
echo.
echo  Comandos utiles:
echo    docker compose ps          - Ver estado
echo    docker compose logs -f web - Ver logs
echo    stop.bat                   - Detener proyecto
echo.
echo =========================================

popd
pause
ENDLOCAL
