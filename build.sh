#!/bin/bash

# Detectar se estamos em um sistema de arquivos Windows montado
CURRENT_PATH=$(pwd)
if [[ $CURRENT_PATH == /mnt/* ]]; then
    echo "============================================"
    echo "⚠ AVISO: Sistema de arquivos Windows detectado"
    echo "============================================"
    echo ""
    echo "Você está executando o script em $CURRENT_PATH"
    echo ""
    echo "O PyInstaller não consegue definir permissões executáveis"
    echo "em sistemas de arquivos Windows montados no WSL."
    echo ""
    echo "Use uma das seguintes opções:"
    echo ""
    echo "OPÇÃO 1 (Recomendado para Windows): Build nativo no Windows"
    echo "  Execute no PowerShell do Windows:"
    echo "    .\\build.bat"
    echo "  Isso criará um executável .exe para Windows."
    echo ""
    echo "OPÇÃO 2: Build Linux no sistema de arquivos Linux"
    echo "  Execute no WSL:"
    echo "    chmod +x build-wsl.sh"
    echo "    ./build-wsl.sh"
    echo "  Isso copiará o projeto para /home, fará o build,"
    echo "  e copiará o resultado de volta."
    echo ""
    echo "OPÇÃO 3: Ignorar o aviso e tentar mesmo assim"
    echo "  Pressione Enter para continuar (pode falhar)..."
    echo "  Ou pressione Ctrl+C para cancelar."
    read -r
    echo ""
fi

echo "Limpando builds antigos..."
rm -rf dist build
rm -f "Auto Install Programs.spec"

echo "Verificando e instalando dependencias necessarias..."

# Verificar se pip está instalado
if ! python3 -m pip --version &> /dev/null; then
    echo "============================================"
    echo "pip não encontrado!"
    echo "============================================"
    echo ""
    echo "Para continuar, você precisa instalar pip."
    echo "Execute no PowerShell do Windows:"
    echo ""
    echo "  .\\install-wsl-deps.bat"
    echo ""
    echo "Após instalar pip, execute este script novamente."
    echo ""
    exit 1
fi

echo "✓ pip encontrado"
echo ""

# Instalar pacotes globalmente com --break-system-packages
echo "Instalando/atualizando dependencias..."
python3 -m pip install --upgrade pip --break-system-packages --quiet
python3 -m pip install pyinstaller customtkinter --break-system-packages --quiet

echo "✓ Dependências instaladas"
echo ""
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
    echo "Build concluído!"
    echo "============================================"
    echo ""
    echo "O executável está em: dist/Auto Install Programs/"
    echo ""
else
    echo "============================================"
    echo "Build falhou!"
    echo "============================================"
    echo ""
    echo "Veja os erros acima para mais detalhes."
    echo "Considere usar build-wsl.sh ou build.bat"
    echo ""
    exit 1
fi