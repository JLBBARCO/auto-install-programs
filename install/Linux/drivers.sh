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
echo "Gestor: $MANAGER"
echo "------------------------------------------"

install_nvidia() {
    echo "Configurando drivers NVIDIA..."
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
}

install_amd() {
    echo "Configurando drivers AMD (Mesa/Vulkan)..."
    case $MANAGER in
        "apt") sudo apt install -y mesa-vulkan-drivers xserver-xorg-video-amdgpu ;;
        "dnf") sudo dnf install -y mesa-dri-drivers ;;
        "pacman") sudo pacman -S --noconfirm mesa lib32-mesa xf86-video-amdgpu ;;
    esac
}

install_intel() {
    echo "Configurando drivers Intel..."
    case $MANAGER in
        "apt") sudo apt install -y intel-media-va-driver-non-free ;;
        "dnf") sudo dnf install -y intel-media-driver ;;
        "pacman") sudo pacman -S --noconfirm intel-media-driver ;;
    esac
}

# --- Lógica de Execução baseada no Hardware ---

if [[ "$MANAGER" == "unknown" ]]; then
    echo "Erro: Distribuição Linux não suportada para instalação automática."
    exit 1
fi

if echo "$GPU_INFO" | grep -iq "NVIDIA"; then
    install_nvidia
elif echo "$GPU_INFO" | grep -iq "AMD"; then
    install_amd
elif echo "$GPU_INFO" | grep -iq "Intel"; then
    install_intel
else
    echo "Nenhuma GPU conhecida detectada para drivers proprietários."
fi

# --- Instalação de utilitários universais via Flatpak (se disponível) ---
if command -v flatpak &> /dev/null; then
    echo "Instalando utilitários de monitorização via Flatpak..."
    # NVTop é excelente para ver o uso da GPU no terminal (funciona para todas as GPUs)
    flatpak install -y flathub io.github.sylveon.Gvnvtop 2>/dev/null
fi

echo "------------------------------------------"
echo "Processo concluído. REINICIE o sistema para aplicar os drivers."