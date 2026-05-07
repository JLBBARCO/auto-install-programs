#!/usr/bin/env bash
owner="JLBBARCO"
repo="programs-manager"
# Branch of this script file. Set via AIP_BRANCH when you need to override the current copy.
ScriptBranch="${AIP_BRANCH:-develop}"

OS_TYPE=$(uname -s)
INSTALL_ROOT="${HOME}/.auto-install-programs"
mkdir -p "$INSTALL_ROOT"

if [ "$OS_TYPE" == "Linux" ]; then
    ASSET_PATTERN="Auto-Install-Programs-linux.tar.gz"
    BINARY_NAME="Auto Install Programs/Auto Install Programs"
else
    ASSET_PATTERN="Auto-Install-Programs-macos.tar.gz"
    BINARY_NAME="Auto Install Programs.app/Contents/MacOS/Auto Install Programs" # Ajuste conforme sua estrutura de Mac
fi

# Busca e baixa apenas se não existir
if [ ! -f "$INSTALL_ROOT/$BINARY_NAME" ]; then
    echo "[programs-manager] Baixando binário nativo para $OS_TYPE..."

    # Try to pick prerelease when the script comes from the develop branch
    URL=""
    if [ "$ScriptBranch" = "develop" ]; then
        RELEASES_JSON=$(curl -s "https://api.github.com/repos/$owner/$repo/releases")
        URL=$(echo "$RELEASES_JSON" | sed 's/},/},\n/g' | grep -A5 '"prerelease": true' | grep 'browser_download_url' | grep "$ASSET_PATTERN" | head -n1 | cut -d '"' -f4)
    fi

    if [ -z "$URL" ]; then
        URL=$(curl -s "https://api.github.com/repos/$owner/$repo/releases/latest" | grep "browser_download_url" | grep "$ASSET_PATTERN" | cut -d '"' -f 4)
    fi

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