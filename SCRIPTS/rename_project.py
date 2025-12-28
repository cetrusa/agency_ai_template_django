#!/usr/bin/env python
"""Renombra referencias del proyecto base."""

from pathlib import Path
import sys

OLD_NAME = "config"
NEW_NAME = sys.argv[1] if len(sys.argv) > 1 else "config"

if NEW_NAME == OLD_NAME:
    print("[i] No hay cambios que aplicar.")
    sys.exit(0)

ROOT = Path(__file__).resolve().parents[1] / "PROJECT_BASE"

replacements = {
    OLD_NAME: NEW_NAME,
    OLD_NAME.capitalize(): NEW_NAME.capitalize(),
}

for path in ROOT.rglob("*.*"):
    text = path.read_text(encoding="utf-8")
    original = text
    for old, new in replacements.items():
        text = text.replace(old, new)
    if text != original:
        path.write_text(text, encoding="utf-8")
        print(f"[+] Actualizado {path.relative_to(ROOT)}")

print("[✓] Renombrado completado. Verifica settings y rutas manualmente.")
