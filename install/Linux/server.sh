#!/bin/bash

# --- Função para detectar o gestor de pacotes ---
detect_manager() {
    if command -v apt &> /dev/null; then echo "apt"
    elif command -v dnf &> /dev/null; then echo "dnf"
    elif command -v pacman &> /dev/null; then echo "pacman"
    else echo "unknown"; fi
}

MANAGER=$(detect_manager)

# --- Função de Instalação Robusta ---
install_pkg() {
    local NAME=$1
    local PKG_NAME=$2
    echo "------------------------------------------"
    echo "Configurando Servidor: $NAME..."

    case $MANAGER in
        "apt") sudo apt install -y "$PKG_NAME" ;;
        "dnf") sudo dnf install -y "$PKG_NAME" ;;
        "pacman") sudo pacman -S --noconfirm "$PKG_NAME" ;;
    esac
}

if [ "$MANAGER" == "unknown" ]; then
    echo "Erro: Gestor de pacotes não identificado."
    exit 1
fi

echo "Iniciando Setup de Servidor [$MANAGER]..."

# 1. Atualização de Segurança
case $MANAGER in
    "apt") sudo apt update && sudo apt upgrade -y ;;
    "dnf") sudo dnf upgrade -y ;;
    "pacman") sudo pacman -Syu --noconfirm ;;
esac

# 2. Ferramentas de Administração e Rede
install_pkg "SSH Server" "openssh-server"
install_pkg "Vim (Editor)" "vim"
install_pkg "Curl & Wget" "curl wget"
install_pkg "HTOP (Monitorização)" "htop"
install_pkg "Net-Tools (Rede)" "net-tools"
install_pkg "Git" "git"

# 3. Web Server & Stack Base (Nginx é o padrão moderno para servidores)
install_pkg "Nginx" "nginx"

# 4. Docker (Essencial para servidores modernos)
# Nota: Em algumas distros o pacote chama-se docker.io ou docker
if [ "$MANAGER" == "apt" ]; then
    install_pkg "Docker" "docker.io"
else
    install_pkg "Docker" "docker"
fi

# 5. Segurança (Firewall)
if [ "$MANAGER" == "apt" ]; then
    install_pkg "UFW Firewall" "ufw"
    sudo ufw allow 22/tcp  # Garante que não trava o SSH
    sudo ufw --force enable
elif [ "$MANAGER" == "dnf" ]; then
    install_pkg "Firewalld" "firewalld"
    sudo systemctl enable --now firewalld
fi

echo "------------------------------------------"
echo "Setup do Servidor Finalizado!"
echo "Sugestão: Configure as chaves SSH e altere as portas padrão."