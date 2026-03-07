#!/bin/bash
set -e

echo "Limpando builds antigos..."
rm -rf dist build
rm -f "Auto Install Programs.spec"

echo "Instalando dependencias necessarias..."
python3 -m pip install --upgrade pip
python3 -m pip install pyinstaller customtkinter

echo "Iniciando o Build com PyInstaller..."
python3 -m PyInstaller --noconfirm --onedir --windowed \
    --name "Auto Install Programs" \
    --add-data "src:src" \
    --add-data "install:install" \
    --collect-all customtkinter \
    "main.py"

echo ""
if [ -d "dist/Auto Install Programs" ]; then
    echo "============================================"
    echo "Build concluido com sucesso!"
    echo "============================================"
    echo ""
    echo "O executavel esta em: dist/Auto Install Programs/"
    echo ""
else
    echo "============================================"
    echo "Build falhou!"
    echo "============================================"
    echo ""
    exit 1
fi
