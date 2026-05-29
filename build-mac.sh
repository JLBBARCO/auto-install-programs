#!/bin/bash
set -e

echo "Cleaning old builds..."
rm -rf dist build
rm -f "Programs Manager.spec"

echo "Installing required dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "Starting build with PyInstaller..."

python3 -m PyInstaller --noconfirm --onedir --windowed \
    --name "Programs Manager" \
    --add-data "lib:lib" \
    --collect-all customtkinter \
    --collect-all psutil \
    "main.py"

echo ""
if [ -d "dist/Programs Manager" ]; then
    echo "============================================"
    echo "Build completed successfully!"
    echo "============================================"
    echo ""
    echo "Executable is at: dist/Programs Manager/"
    echo ""
else
    echo "============================================"
    echo "Build failed!"
    echo "============================================"
    echo ""
    exit 1
fi
