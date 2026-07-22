#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
    echo "ERROR: No existe .venv. Ejecuta ./setup_unix.sh."
    exit 1
fi

if [ ! -f .env ]; then
    echo "ERROR: No existe .env. Copia .env.example como .env."
    exit 1
fi

.venv/bin/python main.py
