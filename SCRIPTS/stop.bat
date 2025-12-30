@echo off
SETLOCAL

echo =========================================
echo  Agency AI Platform - STOP
echo =========================================

:: Navegar al directorio del proyecto (relativo al script)
pushd "%~dp0..\PROJECT_BASE" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] No se pudo acceder a PROJECT_BASE.
    pause
    exit /b 1
)

docker info >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [WARN] Docker no está activo. Nada que detener.
    pause
    exit /b 0
)

echo [INFO] Deteniendo contenedores...
docker compose down

IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Ocurrió un problema al detener los contenedores.
    pause
    exit /b 1
)

echo.
echo [OK] Proyecto detenido correctamente.
echo =========================================

pause
ENDLOCAL
