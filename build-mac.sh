#!/bin/bash
set -e

echo "Cleaning old builds..."
rm -rf dist build
rm -f "Programs Manager.spec"

echo "Installing required dependencies..."
python -m pip install --upgrade pip
python -m pip install pyinstaller customtkinter psutil

echo "Starting build with PyInstaller..."
python -m PyInstaller --noconfirm --onedir --windowed \
    --name "Programs Manager" \
    --add-data "src:src" \
    --add-data "install:install" \
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
