# White List - Programas de Startup Permitidos

Este arquivo contém a lista de chaves de startup que devem permanecer ativas no Windows.

## Como funciona

1. O aplicativo desativa somente os itens que nao estao na whitelist
2. Depois, pode reativar explicitamente os programas que estao na whitelist
3. A busca e normalizada e exata

## Formato

- Uma chave por linha
- Use nomes normalizados: apenas letras e numeros, sem espacos, pontos ou hifens
- Comentarios iniciados com `#` sao ignorados
- Linhas vazias sao ignoradas

Exemplo:

```text
microsoftonedrive
discord
nvidiageforceexperience
rainmeter
```

## Como descobrir nomes de programas

### Opção 1: Usar o script helper (Windows)

Execute `listar-startup.bat` no PowerShell como administrador:

```powershell
.\\listar-startup.bat
```

Isso mostrará todos os programas registrados no startup.

### Opção 2: Verificar o Registro manualmente

Abra `regedit` e navegue para:

- `HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`
- `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`
- `HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run` (64-bit)

Os nomes das entradas (não dos valores) são os que você deve adicionar.

### Opção 3: PowerShell

```powershell
# User startup
Get-ItemProperty "HKCU:\\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

# System startup 32-bit
Get-ItemProperty "HKLM:\\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

# System startup 64-bit
Get-ItemProperty "HKLM:\\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"
```

## Programas recomendados

- **Microsoft**: `microsoftonedrive`, `microsoftedgeautolaunch`, `microsoftpcmanager`
- **NVIDIA**: `nvidiageforceexperience`, `nvbackend`, `nvcontainer`, `nvidiaapp`
- **Intel Graphics**: `igfxtray`, `persistence`, `hotkeyscmds`
- **AMD**: `radeonsoftware`
- **Seguranca**: `securityhealth`
- **Comunicacao**: `discord`, `whatsapp`
- **Utilitarios**: `rainmeter`, `livelywpf`, `camostudio`

## Como a comparacao funciona

O codigo normaliza o nome da whitelist e o nome do registro antes de comparar.

| Entrada na Whitelist      | Programas que serao reativados |
| ------------------------- | ------------------------------ |
| `microsoftonedrive`       | Microsoft.OneDrive             |
| `nvidiageforceexperience` | NVIDIA GeForce Experience      |
| `hotkeyscmds`             | HotKeysCmds                    |
| `microsoftpcmanager`      | Microsoft PC Manager           |

## Adicionando novos programas

1. Descubra o nome exato usando uma das opções acima
2. Abra `white_list.txt` em um editor de texto (Notepad, VS Code, etc)
3. Adicione uma nova linha com o nome normalizado da chave
4. Salve o arquivo
5. Execute o programa novamente e reative a whitelist

### Exemplo

Se você quer reativar "Spotify" e seu nome no registro é "Spotify", adicione:

```text
spotify
```

Se o nome for "SpotifyHelper", normalize antes de salvar:

```text
spotifyhelper
```

## Notas Importantes

- **Normalizacao**: "Microsoft.OneDrive" vira `microsoftonedrive`
- **Sem correspondencia parcial**: termos curtos como `edge` nao reativam tudo que contenha esse trecho
- **Mais seguro**: isso reduz ativacoes acidentais

## Programas conhecidos do Windows

| Programa         | Nomes tipicos no Registro                |
| ---------------- | ---------------------------------------- |
| OneDrive         | `Microsoft.OneDrive`                     |
| Microsoft Edge   | `MicrosoftEdgeAutoLaunch`                |
| Windows Security | `SecurityHealth`                         |
| Intel Graphics   | `IgfxTray`, `Persistence`, `HotKeysCmds` |
| AMD              | `RadeonSoftware`                         |
| PC Manager       | `Microsoft PC Manager`                   |

## Troubleshooting

### Programa não está sendo reativado

1. Verifique o nome exato usando `listar-startup.bat`
2. Confirme que está escrito corretamente (sem espaços extras)
3. Normalize o nome antes de salvar na whitelist
4. Execute o programa como administrador

### Programa inesperado nao foi reativado

Verifique o nome exato no registro e normalize o valor antes de salvar.

## Editar depois da compilação

Depois que o programa foi compilado com PyInstaller:

**Windows**:

```text
dist/Auto Install Programs/install/Windows/white_list.txt
```

**Linux**:

```text
dist/Auto Install Programs/install/Windows/white_list.txt
```

**macOS**:

```text
dist/Auto Install Programs/open dist/Auto\ Install\ Programs.app/Contents/Resources/install/Windows/white_list.txt
```

Você pode editar o arquivo e executar o programa novamente.
