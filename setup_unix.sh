#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"

if command -v python3.12 >/dev/null 2>&1; then
    PYTHON_COMMAND="python3.12"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_COMMAND="python3"
else
    echo "ERROR: No se encontró Python."
    exit 1
fi

"$PYTHON_COMMAND" -c \
'import sys; raise SystemExit(0 if (3, 10) <= sys.version_info[:2] < (4, 0) else 1)' \
|| {
    echo "ERROR: Se requiere Python 3.10 o superior. Se recomienda Python 3.12."
    exit 1
}

"$PYTHON_COMMAND" -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check

if [ ! -f .env ]; then
    cp .env.example .env
fi

echo "Instalación completada."
echo "Abre .env y agrega tu OPENROUTER_API_KEY."
