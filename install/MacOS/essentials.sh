if ! command -v brew &> /dev/null; then
    echo "Instalando Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

#!/bin/bash
echo "Iniciando atualização de aplicações instaladas..."
brew upgrade --quiet
echo "Atualização concluída."
echo ""

install() {
    NAME=$1
    ID=$2
    echo "Instalando $NAME..."
    # No macOS, a maioria das apps essenciais são 'casks' (GUI)
    brew install --cask $ID --quiet
    if [ $? -eq 0 ]; then
        echo "[SUCCESS] $NAME instalado com sucesso!"
    else
        echo "[INFO/ERROR] Falha ou $NAME já está presente."
    fi
    echo ""
}

# Lista de Programas Adaptada para macOS
install "Google Chrome" "google-chrome"
install "Mozilla Firefox" "firefox"
install "VLC" "vlc"
install "The Unarchiver" "the-unarchiver" # Substituto do WinRAR no Mac
install "WhatsApp" "whatsapp"
install "Telegram" "telegram"
install "Spotify" "spotify"
install "Google Drive" "google-drive"
install "Cloudflare Warp" "cloudflare-warp"
install "Adobe Acrobat Reader" "adobe-acrobat-reader"