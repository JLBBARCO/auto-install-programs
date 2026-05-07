#!/usr/bin/env bash
owner="JLBBARCO"
repo="programs-manager"

OS_TYPE=$(uname -s)
INSTALL_ROOT="${HOME}/.auto-install-programs"
mkdir -p "$INSTALL_ROOT"

if [ "$OS_TYPE" == "Linux" ]; then
    ASSET_PATTERN="Auto-Install-Programs-linux.tar.gz"
    BINARY_NAME="Programs Manager/Programs Manager"
else
    ASSET_PATTERN="Auto-Install-Programs-macos.tar.gz"
    BINARY_NAME="Programs Manager.app/Contents/MacOS/Programs Manager"
fi

# Busca e baixa apenas se não existir
if [ ! -f "$INSTALL_ROOT/$BINARY_NAME" ]; then
    echo "[programs-manager] Baixando binário nativo para $OS_TYPE..."

    URL=$(curl -s "https://api.github.com/repos/$owner/$repo/releases/latest" | grep "browser_download_url" | grep "$ASSET_PATTERN" | cut -d '"' -f 4)

    if [ -z "$URL" ]; then
        echo "[programs-manager] Erro: não foi possível localizar o asset para $ASSET_PATTERN"
        exit 1
    fi

    curl -L "$URL" -o "$INSTALL_ROOT/temp.tar.gz"
    tar -xzf "$INSTALL_ROOT/temp.tar.gz" -C "$INSTALL_ROOT"
    rm -f "$INSTALL_ROOT/temp.tar.gz"
fi

# Executa
"$INSTALL_ROOT/$BINARY_NAME"