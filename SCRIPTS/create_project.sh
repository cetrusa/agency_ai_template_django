#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME=${1:-dashboard_project}
TARGET_DIR=${2:-$PROJECT_NAME}

if [ -d "$TARGET_DIR" ]; then
  echo "[!] El directorio $TARGET_DIR ya existe" >&2
  exit 1
fi

cp -R ../PROJECT_BASE "$TARGET_DIR"
cd "$TARGET_DIR"
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate

echo "[+] Proyecto $PROJECT_NAME listo en $TARGET_DIR"
