@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: No existe .venv. Ejecuta setup_windows.cmd.
    exit /b 1
)

if not exist ".env" (
    echo ERROR: No existe .env. Copia .env.example como .env.
    exit /b 1
)

.venv\Scripts\python.exe main.py
endlocal
