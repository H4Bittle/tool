@echo off
cd /d "%~dp0"

REM Create venv if not exists
if not exist "venv" (
    echo [*] Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

set NEEDS_INSTALL=0

REM If marker missing, or Flask not installed, (re)install deps
if not exist ".deps_installed" set NEEDS_INSTALL=1

REM Check Flask presence inside venv
pip show Flask >nul 2>&1 || set NEEDS_INSTALL=1

if %NEEDS_INSTALL%==1 (
    echo [*] Installing dependencies...
    pip install "Pillow==10.4.0" --only-binary :all:
    pip install -r requirements.txt
    echo Dependencies installed> .deps_installed
) else (
    echo [*] Dependencies already installed. Skipping pip install.
)

echo [*] Starting Flask app...
python run.py

pause
