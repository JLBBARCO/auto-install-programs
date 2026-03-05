#!/bin/bash

# --- Função para detectar o gestor de pacotes ---
detect_manager() {
    if command -v apt &> /dev/null; then echo "apt"
    elif command -v dnf &> /dev/null; then echo "dnf"
    elif command -v pacman &> /dev/null; then echo "pacman"
    else echo "unknown"; fi
}

MANAGER=$(detect_manager)
GPU_INFO=$(lspci | grep -i vga)

echo "------------------------------------------"
echo "Hardware: $GPU_INFO"
echo "Manager: $MANAGER"
echo "------------------------------------------"

install_nvidia() {
    echo "Configuring drivers NVIDIA..."
    case $MANAGER in
        "apt")
            # Método oficial para Debian/Ubuntu/Mint
            sudo ubuntu-drivers autoinstall || sudo apt install -y nvidia-driver-535
            ;;
        "dnf")
            # Requer repositório RPM Fusion no Fedora
            sudo dnf install -y akmod-nvidia
            ;;
        "pacman")
            sudo pacman -S --noconfirm nvidia nvidia-utils
            ;;
    esac

    sleep 2
}

install_amd() {
    echo "Configuring drivers AMD (Mesa/Vulkan)..."
    case $MANAGER in
        "apt") sudo apt install -y mesa-vulkan-drivers xserver-xorg-video-amdgpu ;;
        "dnf") sudo dnf install -y mesa-dri-drivers ;;
        "pacman") sudo pacman -S --noconfirm mesa lib32-mesa xf86-video-amdgpu ;;
    esac

    sleep 2
}

install_intel() {
    echo "Configuring drivers Intel..."
    case $MANAGER in
        "apt") sudo apt install -y intel-media-va-driver-non-free ;;
        "dnf") sudo dnf install -y intel-media-driver ;;
        "pacman") sudo pacman -S --noconfirm intel-media-driver ;;
    esac

    sleep 2
}

# --- Lógica de Execução baseada no Hardware ---

if [[ "$MANAGER" == "unknown" ]]; then
    echo "Error: Linux distribution not supported for automatic installation."
    exit 1
fi

if echo "$GPU_INFO" | grep -iq "NVIDIA"; then
    install_nvidia
elif echo "$GPU_INFO" | grep -iq "AMD"; then
    install_amd
elif echo "$GPU_INFO" | grep -iq "Intel"; then
    install_intel
else
    echo "No known GPUs detected for proprietary drivers."
fi

# --- Instalação de utilitários universais via Flatpak (se disponível) ---
if command -v flatpak &> /dev/null; then
    echo "Installing monitoring utilities via Flatpak..."
    # NVTop é excelente para ver o uso da GPU no terminal (funciona para todas as GPUs)
    flatpak install -y flathub io.github.sylveon.Gvnvtop 2>/dev/null
fi

echo "------------------------------------------"
echo "Process completed. RESTART the system to apply the drivers."