@echo off
setlocal EnableExtensions

REM Guardar snapshot del proyecto en Git (init/add/commit) y opcional push.
REM Uso (recomendado):
REM   SCRIPTS\github_publish_and_sync.bat "Mensaje de commit" "https://github.com/ORG/REPO.git"
REM Ejemplos:
REM   SCRIPTS\github_publish_and_sync.bat
REM   SCRIPTS\github_publish_and_sync.bat "Punto estable: limpieza maestro + aliases"
REM   SCRIPTS\github_publish_and_sync.bat "Punto estable" "https://github.com/cetrusa/pareto.git"

cd /d "%~dp0"
rem Si estamos en la carpeta SCRIPTS, subir un nivel al root del proyecto
for %%I in (.) do if /I "%%~nxI"=="SCRIPTS" cd ..

where git >nul 2>nul
if errorlevel 1 (
  echo ERROR: Git no esta instalado o no esta en PATH.
  echo Instala Git for Windows y reintenta.
  exit /b 1
)

REM 1) Inicializar repo si no existe
if not exist ".git" (
  echo Inicializando repositorio Git...
  git init
  if errorlevel 1 exit /b 1
) else (
  echo Repo Git ya existe.
)

REM 1b) Limpieza del indice (no borra archivos del disco)
REM - Saca del repo artefactos locales/no funcionales (DBs/backups) y carpeta archive_unused
if exist "archive_unused\" (
  git rm -r --cached "archive_unused" >nul 2>nul
)

for /f "delims=" %%f in ('git ls-files "*.db" "*.sqlite" "*.sqlite3" 2^>nul') do (
  git rm --cached "%%f" >nul 2>nul
)
for /f "delims=" %%f in ('git ls-files "*.db.*" "*.backup_*" "*.bak" 2^>nul') do (
  git rm --cached "%%f" >nul 2>nul
)

REM Estos ya estan en .gitignore, pero si quedaron trackeados, los removemos del indice.
git ls-files --error-unmatch "installation_complete.txt" >nul 2>nul && git rm --cached "installation_complete.txt" >nul 2>nul
git ls-files --error-unmatch "py_compile_err.txt" >nul 2>nul && git rm --cached "py_compile_err.txt" >nul 2>nul
git ls-files --error-unmatch "error_log.txt" >nul 2>nul && git rm --cached "error_log.txt" >nul 2>nul

REM 2) Preparar argumentos
REM - Arg1: mensaje (opcional)
REM - Arg2: remoto origin (opcional)
set "ARG1=%~1"
set "ARG2=%~2"

set "MSG=%ARG1%"
set "REMOTE_URL=%ARG2%"

REM Si el usuario pasó solo una URL como primer argumento, tratarlo como REMOTE y autogenerar mensaje.
if not "%ARG1%"=="" (
  set "PFX=%ARG1:~0,4%"
  if /i "%PFX%"=="http" (
    set "REMOTE_URL=%ARG1%"
    set "MSG="
  )
)

if "%MSG%"=="" (
  for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"`) do set "TS=%%i"
  set "MSG=Backup: %TS%"
)

REM 3) Stage + commit
echo Agregando cambios...
git add -A
if errorlevel 1 exit /b 1

git diff --cached --quiet
if not errorlevel 1 (
  echo No hay cambios para commitear.
  goto :PUSH_OPTIONAL
)

echo Creando commit: "%MSG%"
git commit -m "%MSG%"
if errorlevel 1 exit /b 1

:PUSH_OPTIONAL
REM 4) Configurar remoto si se proporciono URL
if not "%REMOTE_URL%"=="" (
  git remote add origin "%REMOTE_URL%" 2>nul
  if errorlevel 1 (
    git remote set-url origin "%REMOTE_URL%" >nul 2>nul
  )
)

REM 5) Push si existe origin
set "HAS_ORIGIN=0"
for /f "delims=" %%r in ('git remote 2^>nul') do (
  if /i "%%r"=="origin" set "HAS_ORIGIN=1"
)

if "%HAS_ORIGIN%"=="1" (
  echo Haciendo push a origin - rama actual ...
  git push -u origin HEAD
)

:END
echo Listo.
endlocal
exit /b 0
