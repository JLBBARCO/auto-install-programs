#!/usr/bin/env bash
OS_TYPE=$(uname -s)
INSTALL_ROOT="${HOME}/.auto-install-programs"
mkdir -p "$INSTALL_ROOT"

if [ "$OS_TYPE" == "Linux" ]; then
    ASSET_PATTERN="linux.tar.gz"
    BINARY_NAME="Auto Install Programs"
else
    ASSET_PATTERN="macos.tar.gz"
    BINARY_NAME="Auto Install Programs.app/Contents/MacOS/Auto Install Programs" # Ajuste conforme sua estrutura de Mac
fi

# Busca e baixa apenas se não existir
if [ ! -f "$INSTALL_ROOT/$BINARY_NAME" ]; then
    echo "[auto-programs] Baixando binário nativo para $OS_TYPE..."
    URL=$(curl -s https://api.github.com/repos/JLBBARCO/auto-programs/releases/latest | grep "browser_download_url" | grep "$ASSET_PATTERN" | cut -d '"' -f 4)
    curl -L "$URL" -o "$INSTALL_ROOT/temp.tar.gz"
    tar -xzf "$INSTALL_ROOT/temp.tar.gz" -C "$INSTALL_ROOT"
fi

# Executa
"$INSTALL_ROOT/$BINARY_NAME"