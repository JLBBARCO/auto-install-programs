#!/bin/bash

# --- Função para detectar o gestor de pacotes ---
detect_manager() {
    if command -v apt &> /dev/null; then echo "apt"
    elif command -v dnf &> /dev/null; then echo "dnf"
    elif command -v pacman &> /dev/null; then echo "pacman"
    else echo "unknown"; fi
}

MANAGER=$(detect_manager)

install_pkg() {
    local NAME=$1
    local PKG_NAME=$2
    echo "------------------------------------------"
    echo "Installing: $NAME..."

    case $MANAGER in
        "apt") sudo apt install -y "$PKG_NAME" ;;
        "dnf") sudo dnf install -y "$PKG_NAME" ;;
        "pacman") sudo pacman -S --noconfirm "$PKG_NAME" ;;
    esac

    sleep 2
}

if [ "$MANAGER" == "unknown" ]; then exit 1; fi

# Atualização inicial
case $MANAGER in
    "apt") sudo apt update ;;
    "dnf") sudo dnf check-update ;;
    "pacman") sudo pacman -Sy ;;
esac

# Lista de Programas (Nomes comuns em Linux)
install_pkg "Visual Studio Code" "code"
install_pkg "Git" "git"
install_pkg "Python 3" "python3"
install_pkg "Node.js" "nodejs"
install_pkg "Docker" "docker.io"
install_pkg "Gimp" "gimp"
install_pkg "Blender" "blender"
install_pkg "VirtualBox" "virtualbox"
install_pkg "Arduino IDE" "arduino"
install_pkg "Raspberry Pi" "raspberrypi-imager"

echo "Configured Development!"