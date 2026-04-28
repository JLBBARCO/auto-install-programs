#!/bin/bash

# Detectar se estamos em um sistema de arquivos Windows montado
# Detect if we're on a mounted Windows file system
CURRENT_PATH=$(pwd)
if [[ $CURRENT_PATH == /mnt/* ]]; then
    echo "============================================"
    echo "WARNING: Windows file system detected"
    echo "============================================"
    echo ""
    echo "You are running the script in $CURRENT_PATH"
    echo ""
    echo "PyInstaller cannot set executable permissions"
    echo "on Windows file systems mounted in WSL."
    echo ""
    echo "Use one of the following options:"
    echo ""
    echo "OPTION 1 (Recommended for Windows): Native Windows build"
    echo "  Run in Windows PowerShell:"
    echo "    .\\build.bat"
    echo "  This will create a .exe executable for Windows."
    echo ""
    echo "OPTION 2: Linux build on Linux file system"
    echo "  Run in WSL:"
    echo "    chmod +x build-wsl.sh"
    echo "    ./build-wsl.sh"
    echo "  This will copy the project to /home, build it,"
    echo "  and copy the result back."
    echo ""
    echo "OPTION 3: Ignore the warning and try anyway"
    echo "  Press Enter to continue (may fail)..."
    echo "  Or press Ctrl+C to cancel."
    read -r
    echo ""
fi

echo "Cleaning old builds..."
rm -rf dist build
rm -f "Auto Install Programs.spec"

echo "Checking and installing required dependencies..."

# Verificar se pip está instalado
if ! python3 -m pip --version &> /dev/null; then
    echo "============================================"
    echo "pip not found!"
    echo "============================================"
    echo ""
    echo "To continue, you need to install pip."
    echo "Run in Windows PowerShell:"
    echo ""
    echo "  .\\install-wsl-deps.bat"
    echo ""
    echo "After installing pip, run this script again."
    echo ""
    echo "Try installing pip3 manually:"
    exit 1
fi

echo "✓ pip found"
echo ""

# Install packages globally with --break-system-packages
echo "Installing/updating dependencies..."
python3 -m pip install --upgrade pip --break-system-packages --quiet
python3 -m pip install pyinstaller customtkinter psutil --break-system-packages --quiet

echo "✓ Dependencies installed"
echo ""
echo "Starting build with PyInstaller..."
python3 -m PyInstaller --noconfirm --onedir --windowed \
    --name "Auto Install Programs" \
    --add-data "src:src" \
    --add-data "install:install" \
    --collect-all customtkinter \
    --collect-all psutil \
    "main.py"

echo ""
if [ -d "dist/Auto Install Programs" ]; then
    echo "============================================"
    echo "Build completed!"
    echo "============================================"
    echo ""
    echo "Executable is at: dist/Auto Install Programs/"
    echo ""
else
    echo "============================================"
    echo "Build failed!"
    echo "============================================"
    echo ""
    echo "Check the errors above for more details."
    echo "Consider using build-wsl.sh or build.bat"
    echo ""
    exit 1
fi