if ! command -v brew &> /dev/null; then
    echo "Instalando Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

#!/bin/bash
echo "Installing screen tools and support..."

# O AnyDesk está disponível via Cask
echo "Installing AnyDesk..."
brew install --cask anydesk --quiet

# Adicionado sistema de sleep para reduzir carga no CPU
sleep 2

# Alternativa ao Spacedesk para Mac (Monitor extra)
# Muitas vezes usa-se o AirServer ou Luna Display, mas não são gratuitos.
# Instalando o AnyDesk como ferramenta principal de acesso.

echo "Process completed."