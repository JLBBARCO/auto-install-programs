if ! command -v brew &> /dev/null; then
    echo "Instalando Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

#!/bin/bash
echo "Instalando ferramentas de ecrã e suporte..."

# O AnyDesk está disponível via Cask
brew install --cask anydesk --quiet

# Alternativa ao Spacedesk para Mac (Monitor extra)
# Muitas vezes usa-se o AirServer ou Luna Display, mas não são gratuitos.
# Instalando o AnyDesk como ferramenta principal de acesso.

echo "Processo concluído."