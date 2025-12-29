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

:: 3. Levantar servicios base (db + web)
echo [INFO] Levantando servicios base (db, web)...
docker compose up -d db web

IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Error levantando contenedores.
    pause
    exit /b 1
)

:: 4. Mostrar estado
echo.
echo =========================================
echo  Contenedores activos:
echo =========================================
docker compose ps

echo.
echo [OK] Proyecto levantado correctamente.
echo Accede a: http://localhost:8000
echo =========================================

pause
ENDLOCAL
