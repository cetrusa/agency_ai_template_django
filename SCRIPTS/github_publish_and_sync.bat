@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM =============================================================
REM Sync Git -> GitHub (solo git)
REM - Inicializa repo local si falta
REM - Configura/actualiza remote origin
REM - add/commit (si hay cambios)
REM - pull --rebase (si existe main remota)
REM - push a main
REM
REM Uso:
REM   SCRIPTS\github_publish_and_sync.bat
REM   SCRIPTS\github_publish_and_sync.bat "mensaje commit"
REM   SCRIPTS\github_publish_and_sync.bat "mensaje" "https://github.com/OWNER/REPO.git"
REM =============================================================

set "DEFAULT_REMOTE_URL=https://github.com/cetrusa/agency_ai_template_django.git"

REM Si se ejecuta con doble click, mantenemos la ventana abierta.
set "PAUSE_ON_EXIT=0"
if "%~1"=="" set "PAUSE_ON_EXIT=1"

REM 1) Ir a raíz del proyecto
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%" || goto :END
for %%I in (.) do set "CURRENT_FOLDER_NAME=%%~nxI"
if /I "%CURRENT_FOLDER_NAME%"=="SCRIPTS" cd ..

REM 2) Verificar git
where git >nul 2>&1
if errorlevel 1 (
  echo [ERROR] El comando 'git' no se encuentra. Instala Git for Windows y agrega al PATH.
  goto :END
)

REM 3) Preparar argumentos
set "COMMIT_MSG=%~1"
set "REMOTE_URL=%~2"

REM Permitir ejecutar: bat https://github.com/... (sin mensaje)
if not "%COMMIT_MSG%"=="" (
  set "PFX=%COMMIT_MSG:~0,4%"
  if /I "!PFX!"=="http" (
    set "REMOTE_URL=%COMMIT_MSG%"
    set "COMMIT_MSG="
  )
)

if "%REMOTE_URL%"=="" set "REMOTE_URL=%DEFAULT_REMOTE_URL%"

REM 4) Inicializar git si hace falta
if not exist ".git" (
  echo [INFO] Inicializando repositorio Git local...
  git init
  if errorlevel 1 (
    echo [ERROR] Fallo git init.
    goto :END
  )
)

REM Asegurar rama main
git branch -M main >nul 2>&1

REM 5) Configurar remote origin
git remote get-url origin >nul 2>&1
if errorlevel 1 (
  echo [INFO] Agregando remote origin: %REMOTE_URL%
  git remote add origin "%REMOTE_URL%"
) else (
  echo [INFO] Actualizando remote origin: %REMOTE_URL%
  git remote set-url origin "%REMOTE_URL%" >nul 2>&1
)

REM 6) Add / Commit
echo [INFO] Agregando cambios...
git add -A

git diff --cached --quiet
if errorlevel 1 (
  if "%COMMIT_MSG%"=="" (
    for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"`) do set "TS=%%i"
    set "COMMIT_MSG=chore: sync !TS!"
  )
  echo [INFO] Commit: "!COMMIT_MSG!"
  git commit -m "!COMMIT_MSG!"
  if errorlevel 1 (
    echo [ERROR] Fallo el commit.
    goto :END
  )
) else (
  echo [INFO] No hay cambios para commitear.
)

REM 7) Pull rebase si el remoto ya tiene main
echo [INFO] Sincronizando con remoto...
git ls-remote --heads origin main >nul 2>&1
if not errorlevel 1 (
  git pull origin main --rebase
)

REM 8) Push
git push -u origin main
if errorlevel 1 (
  echo [ERROR] Fallo el push. Verifica autenticacion/conflictos.
  goto :END
)

echo.
echo [EXITO] Proyecto sincronizado en:
echo         https://github.com/cetrusa/agency_ai_template_django

:END
if "%PAUSE_ON_EXIT%"=="1" (
  echo.
  echo Presiona cualquier tecla para salir...
  pause >nul
)

endlocal
exit /b 0
