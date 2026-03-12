#!/bin/bash
set -e

echo "Cleaning old builds..."
rm -rf dist build
rm -f "Auto Install Programs.spec"

echo "Installing required dependencies..."
python -m pip install --upgrade pip
python -m pip install pyinstaller customtkinter psutil

echo "Starting build with PyInstaller..."
python -m PyInstaller --noconfirm --onedir --windowed \
    --name "Auto Install Programs" \
    --add-data "src:src" \
    --collect-all customtkinter \
    --collect-all psutil \
    "main.py"

echo ""
if [ -d "dist/Auto Install Programs" ]; then
    echo "============================================"
    echo "Build completed successfully!"
    echo "============================================"
    echo ""
    echo "Executable is at: dist/Auto Install Programs/"
    echo ""
else
    echo "============================================"
    echo "Build failed!"
    echo "============================================"
    echo ""
    exit 1
fi
