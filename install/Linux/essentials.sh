#!/bin/bash

# --- Função para detectar o gestor de pacotes ---
detect_manager() {
    if command -v apt &> /dev/null; then
        echo "apt"
    elif command -v dnf &> /dev/null; then
        echo "dnf"
    elif command -v pacman &> /dev/null; then
        echo "pacman"
    else
        echo "unknown"
    fi
}

MANAGER=$(detect_manager)

# --- Função de Instalação ---
install_pkg() {
    local NAME=$1
    local PKG_NAME=$2

    echo "------------------------------------------"
    echo "Installing: $NAME..."

    case $MANAGER in
        "apt")
            sudo apt install -y "$PKG_NAME"
            ;;
        "dnf")
            sudo dnf install -y "$PKG_NAME"
            ;;
        "pacman")
            sudo pacman -S --noconfirm "$PKG_NAME"
            ;;
        *)
            echo "[ERROR] Package manager not supported for $NAME"
            return 1
            ;;
    esac

    if [ $? -eq 0 ]; then
        echo "[SUCCESS] $NAME installed correctly!"
    else
        echo "[ERROR] Error installing $NAME."
    fi

    sleep 2
}

# --- Início do Script ---
if [ "$MANAGER" == "unknown" ]; then
    echo "Error: A supported package manager could not be found. (APT, DNF or PACMAN)."
    exit 1
fi

echo "Manager detected: $MANAGER"
echo "Updating repositories..."

case $MANAGER in
    "apt") sudo apt update ;;
    "dnf") sudo dnf check-update ;;
    "pacman") sudo pacman -Sy ;;
esac

# --- Lista de Programas ---
# Nota: Os nomes dos pacotes no Linux podem variar ligeiramente do Windows.
# Ajustei para os nomes mais comuns no Ubuntu/Mint.

install_pkg "Free Download Manager" ""
install_pkg "Google Chrome" "google-chrome-stable"
install_pkg "Mozilla Firefox" "firefox"
install_pkg "VLC" "vlc"
install_pkg "WhatsApp (Desktop)" "whatsapp-for-linux"
install_pkg "Telegram" "telegram-desktop"
install_pkg "Spotify" "spotify-client"
install_pkg "Git" "git"
install_pkg "Curl" "curl"
install_pkg "Passwords Manager" "passwords-manager"

echo "------------------------------------------"
echo "Process completed!"