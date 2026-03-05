#!/bin/bash

MANAGER=$(if command -v apt &> /dev/null; then echo "apt"; elif command -v dnf &> /dev/null; then echo "dnf"; else echo "pacman"; fi)

install_pkg() {
    echo "Instalando: $1..."
    case $MANAGER in
        "apt") sudo apt install -y "$2" ;;
        "dnf") sudo dnf install -y "$2" ;;
        "pacman") sudo pacman -S --noconfirm "$2" ;;
    esac
}

# Atualizar repositórios
[ "$MANAGER" == "apt" ] && sudo apt update

# Programas de Ecrã/Remoto
install_pkg "AnyDesk" "anydesk"
install_pkg "Git" "git" # Necessário para clonar drivers se preciso
install_pkg "VNC Server" "tightvncserver" # Alternativa comum ao Spacedesk no Linux

echo "Configuração de ecrã finalizada!"