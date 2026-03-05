#!/bin/bash

# --- Função de Verificação do Homebrew ---
if ! command -v brew &> /dev/null; then
    echo "Instalando Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

echo "Installing development tools..."
echo ""

# Lista de Apps de Interface (Casks)
CASKS=(
    visual-studio-code arduino-ide microsoft-teams gimp 
    github mysql-workbench xampp docker virtualbox 
    figma blender
)

for app in "${CASKS[@]}"; do
    echo "Installing $app..."
    brew install --cask "$app" --quiet
    sleep 2  # <--- O Sleep aqui dá um respiro ao processador entre apps
done

# Lista de Ferramentas de Linha de Comando (Formulae)
FORMULAE=(git python@3.12 node)

for tool in "${FORMULAE[@]}"; do
    echo "Installing $tool..."
    brew install "$tool" --quiet
    sleep 2  # <--- O Sleep aqui evita picos de processamento
done

echo "Development setup complete!"