if ! command -v brew &> /dev/null; then
    echo "Instalando Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

#!/bin/bash
echo "Instalando ferramentas de desenvolvimento..."
echo ""

# Apps de Interface (Casks)
brew install --cask visual-studio-code --quiet
brew install --cask arduino-ide --quiet
brew install --cask microsoft-teams --quiet
brew install --cask gimp --quiet
brew install --cask github --quiet
brew install --cask mysql-workbench --quiet
brew install --cask xampp --quiet
brew install --cask docker --quiet
brew install --cask virtualbox --quiet
brew install --cask figma --quiet
brew install --cask blender --quiet

# Ferramentas de Linha de Comando (Formulae)
brew install git --quiet
brew install python@3.12 --quiet
brew install node --quiet

echo "Setup de desenvolvimento finalizado!"