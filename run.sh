#!/usr/bin/env bash
owner="JLBBARCO"
repo="programs-manager"

# When this script is fetched from the 'beta' branch it should use the
# latest prerelease artifact; when fetched from 'main' it should use the
# latest stable release. Set here according to file branch.
SCRIPT_BRANCH="${AIP_BRANCH:-${SCRIPT_BRANCH:-main}}"
SCRIPT_BRANCH="$(printf '%s' "$SCRIPT_BRANCH" | tr '[:upper:]' '[:lower:]' | xargs)"

OS_TYPE=$(uname -s)
INSTALL_ROOT="${HOME}/.programs-manager"
mkdir -p "$INSTALL_ROOT"

if [ "$OS_TYPE" == "Linux" ]; then
    ASSET_PATTERN="programs-manager-linux.tar.gz"
    BINARY_NAME="Programs Manager/Programs Manager"
else
    ASSET_PATTERN="programs-manager-macos.tar.gz"
    BINARY_NAME="Programs Manager.app/Contents/MacOS/Programs Manager"
fi

resolve_local_build() {
    local source_path
    source_path="${BASH_SOURCE[0]}"

    if [ -z "$source_path" ] || [ ! -f "$source_path" ]; then
        return 1
    fi

    local script_dir
    script_dir="$(cd "$(dirname "$source_path")" && pwd)"

    for candidate_dir in dist build; do
        local search_root="${script_dir}/${candidate_dir}"
        if [ -d "$search_root" ]; then
            local found_exe
            found_exe="$(find "$search_root" -type f \( -name "Programs Manager" -o -name "Programs Manager.exe" \) 2>/dev/null | sort -r | head -n 1)"
            if [ -n "$found_exe" ]; then
                printf '%s\n' "$found_exe"
                return 0
            fi
        fi
    done

    return 1
}

LOCAL_BUILD_PATH="$(resolve_local_build 2>/dev/null || true)"
if [ -n "$LOCAL_BUILD_PATH" ]; then
    echo "[programs-manager] Build local encontrado: $LOCAL_BUILD_PATH"
    exec "$LOCAL_BUILD_PATH"
fi

# Busca e baixa apenas se não existir
if [ ! -x "$INSTALL_ROOT/$BINARY_NAME" ]; then
    echo "[programs-manager] Baixando binário nativo para $OS_TYPE..."

    if [ "$SCRIPT_BRANCH" = "beta" ]; then
        # Find most recent prerelease using Python when available.
        if command -v python3 >/dev/null 2>&1; then
            URL=$(python3 - "$owner" "$repo" "$ASSET_PATTERN" <<'PY'
import json
import sys
import urllib.request

owner, repo, asset_pattern = sys.argv[1:4]
api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"

with urllib.request.urlopen(api_url) as response:
    releases = json.load(response)

prereleases = [release for release in releases if release.get("prerelease")]
prereleases.sort(key=lambda release: release.get("published_at") or "", reverse=True)

for release in prereleases:
    for asset in release.get("assets", []):
        if asset.get("name") == asset_pattern:
            print(asset.get("browser_download_url", ""))
            raise SystemExit(0)

raise SystemExit(1)
PY
)
        else
            URL=$(curl -fsSL "https://api.github.com/repos/$owner/$repo/releases" | grep -A20 "\"prerelease\": true" | grep "browser_download_url" | grep "$ASSET_PATTERN" | head -n1 | cut -d '"' -f 4)
        fi

        if [ -z "$URL" ]; then
            echo "[programs-manager] Nenhum prerelease encontrado; usando a última release estável..."
            URL=$(curl -fsSL "https://api.github.com/repos/$owner/$repo/releases/latest" | grep "browser_download_url" | grep "$ASSET_PATTERN" | cut -d '"' -f 4)
        fi
    else
        URL=$(curl -fsSL "https://api.github.com/repos/$owner/$repo/releases/latest" | grep "browser_download_url" | grep "$ASSET_PATTERN" | cut -d '"' -f 4)
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
exec "$INSTALL_ROOT/$BINARY_NAME"