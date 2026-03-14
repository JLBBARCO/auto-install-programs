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

install_formulae() {
    NAME=$1
    ID=$2
    echo "Installing $NAME..."
    brew install $ID --quiet
    
    # Adicionado sistema de sleep para reduzir carga no CPU
    sleep 2

    if [ $? -eq 0 ]; then
        echo "[SUCCESS] $NAME Installed successfully!"
    else
        echo "[INFO/ERROR] Failure or $NAME is already present."
    fi
    echo ""
}

# Lista de Apps de Desenvolvimento (Casks)
install "Visual Studio Code" "visual-studio-code"
install "Arduino IDE" "arduino-ide"
install "Microsoft Teams" "microsoft-teams"
install "GIMP" "gimp"
install "GitHub Desktop" "github"
install "MySQL Workbench" "mysql-workbench"
install "XAMPP" "xampp"
install "Docker" "docker"
install "VirtualBox" "virtualbox"
install "Figma" "figma"
install "Blender" "blender"
install "Raspberry Pi Imager" "raspberry-pi-imager"

# Lista de Ferramentas de Linha de Comando (Formulae)
install_formulae "Git" "git"
install_formulae "Python 3.12" "python@3.12"
install_formulae "Node.js" "node"