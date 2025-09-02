#!/bin/bash
set -e

# Go to script directory
cd "$(dirname "$0")"

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

NEEDS_INSTALL=0

# If marker missing, mark for install
if [ ! -f ".deps_installed" ]; then
    NEEDS_INSTALL=1
fi

# Check Flask presence
if ! pip show Flask >/dev/null 2>&1; then
    NEEDS_INSTALL=1
fi

if [ "$NEEDS_INSTALL" -eq 1 ]; then
    echo "[*] Installing dependencies..."
    # Pillow first (binary wheel)
    pip install "Pillow==10.4.0" --only-binary :all:
    # Install the rest from requirements.txt
    pip install -r requirements.txt
    echo "Dependencies installed" > .deps_installed
else
    echo "[*] Dependencies already installed. Skipping pip install."
fi

# Start Flask app
echo "[*] Starting Flask app..."
python run.py
