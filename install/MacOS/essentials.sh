if ! command -v brew &> /dev/null; then
    echo "Instalando Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

#!/bin/bash
echo "Starting update of installed applications..."
brew upgrade --quiet
echo "Update complete."
echo ""

install() {
    NAME=$1
    ID=$2
    echo "Installing $NAME..."
    # No macOS, a maioria das apps essenciais são 'casks' (GUI)
    brew install --cask $ID --quiet
    
    # Adicionado sistema de sleep para reduzir carga no CPU
    sleep 2

    if [ $? -eq 0 ]; then
        echo "[SUCCESS] $NAME Installed successfully!"
    else
        echo "[INFO/ERROR] Failure or $NAME is already present."
    fi
    echo ""
}

# Lista de Programas Adaptada para macOS
install "Free Download Manager" ""
install "Google Chrome" "google-chrome"
install "Mozilla Firefox" "firefox"
install "VLC" "vlc"
install "The Unarchiver" "the-unarchiver"
install "WhatsApp" "whatsapp"
install "Telegram" "telegram"
install "Spotify" "spotify"
install "Google Drive" "google-drive"
install "Cloudflare Warp" "cloudflare-warp"
install "Adobe Acrobat Reader" "adobe-acrobat-reader"
install "Passwords Manager" "passwords-manager"