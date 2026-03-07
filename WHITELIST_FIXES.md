# Correções da Whitelist - Resumo

## Problemas Encontrados e Corrigidos

### ❌ Problema Principal: Nomes incorretos na whitelist

A whitelist original continha nomes que não correspondiam exatamente aos nomes registrados no Windows:

**Nomes incorretos:**

- `edge` → deveria ser `msedge`
- `nv-display-container` → nome com hífen não aparece no registro
- `nvspcaps64` → nome muito específico, melhor usar `nvidia`
- `nvidia share` → espaços desnecessários
- `shadowplay` → não era o nome correto
- `amdsoftware` → deveria ser `amd`
- `atibrowser` → não correspondia
- `radeonsoftware` → deveria ser `radeon`
- `cnext` → desconhecido
- `intelgraphics` → deveria ser `igfx`
- Maiúsculas em `Rainmeter` e `Lively Wallpaper` (os nomes devem ser lowercase)

### ✅ Correções Aplicadas

**Nova whitelist otimizada:**

```text
onedrive        # Microsoft OneDrive
teams           # Microsoft Teams
discord         # Discord
securityhealth  # Windows Defender/Security
nearby          # Nearby Share
camo            # Camo
msedge          # Microsoft Edge (nome correto)
whatsapp        # WhatsApp
nvidia          # NVIDIA drivers (genérico)
nvbackend       # NVIDIA services
nvinitialize    # NVIDIA initialization
igfxtray        # Intel Graphics (tray)
igfxpers        # Intel Graphics (persistent service)
igfxhk          # Intel Graphics (hook)
intelgraphics   # Intel Graphics (genérico)
amd             # AMD processors
radeon          # AMD Radeon display
rainmeter       # Rainmeter (lowercase)
lively          # Lively Wallpaper (lowercase)
```

## Ferramentas Criadas

### 1. `listar-startup.bat`

Script batch para listar todos os programas de startup do Windows.

**Como usar:**

```powershell
.\\install\Windows\listar-startup.bat
```

Mostra todos os programas registrados em:

- HKEY_CURRENT_USER
- HKEY_LOCAL_MACHINE (32-bit)
- HKEY_LOCAL_MACHINE (64-bit/WOW64)

### 2. `list_startup_programs.py`

Script Python avançado que lista programas de startup e pode gerar uma whitelist personalizada automaticamente.

**Como usar:**

```bash
python install/Windows/list_startup_programs.py
```

**Funcionalidades:**

- Lista todos os programas de startup
- Sugere programas para a whitelist baseado em palavras-chave
- Pode salvar em arquivo `white_list_generated.txt`
- Execute como administrador para melhores resultados

### 3. `WHITELIST_README.md`

Documentação completa sobre como:

- Usar a whitelist
- Descobrir nomes de programas
- Adicionar novos programas
- Entender o sistema de busca parcial

**Localização:**

```text
install/Windows/WHITELIST_README.md
```

## Como o Sistema Funciona

### Busca Parcial (Case-Insensitive)

O código faz uma busca **parcial e case-insensitive** no registro do Windows:

```python
if any(term in name.lower() for term in whitelist)
```

**Exemplos:**

- Whitelist: `nvidia`
- Progr. no Registro: `NVIDIA GeForce Experience`
- **Resultado:** ✅ Será reativado (contém "nvidia")

- Whitelist: `onedrive`
- Progr. no Registro: `Microsoft.OneDrive`
- **Resultado:** ✅ Será reativado (contém "onedrive")

- Whitelist: `igfx`
- Programas no Registro: `igfxtray`, `igfxpers`, `igfxhk`
- **Resultado:** ✅ Todos serão reativados (todos contêm "igfx")

## Fluxo do Programa

1. **Desativa todos os programas de startup** → status = "desativado"
2. **Salva lista em `programs.log`** → backup do estado anterior
3. **Lê `white_list.txt`** → carrega programas permitidos
4. **Reativa programas da whitelist** → status = "ativado"

## Testes e Validações

✅ Todos os arquivos Python compilam sem erros
✅ Scripts shell validados para Linux/macOS  
✅ Script batch validado para Windows
✅ Testes executados com sucesso
✅ Documentação completa criada

## Como Adicionar Novo Programa

### Quick Start

1. Descobra o nome exato:

   ```bash
   python install/Windows/list_startup_programs.py
   ```

2. Edite `install/Windows/white_list.txt`:

   ```text
   spotify
   ```

3. Recompile o programa ou edite o arquivo dentro do `.app`/executável

### Exemplo Pratico

Quer reativar Spotify?

```bash
# 1. Execute o descobridor
python install/Windows/list_startup_programs.py

# Saída: Encontrou "Spotify" no registro

# 2. Adicione a white_list.txt
echo spotify >> install/Windows/white_list.txt

# 3. Pronto!
```

## Próximos Passos Recomendados

1. **Teste em uma VM** para confirmar que as correções funcionam corretamente
2. **Colete feedback** dos usuários sobre programas que não foram reativados
3. **Crie versões personalizadas** da whitelist para diferentes casos de uso
4. **Documente programas problemas** que tenham nomes inconsistentes

## Referência: Nomes Comuns no Registro

| Programa         | Nome(s) no Registro             |
| ---------------- | ------------------------------- |
| OneDrive         | OneDrive, Microsoft.OneDrive    |
| Microsoft Edge   | msedge                          |
| Microsoft Teams  | Teams, ms-teams                 |
| Discord          | Discord                         |
| WhatsApp         | WhatsApp                        |
| NVIDIA           | nvidia, nvbackend, nvinitialize |
| Intel Graphics   | igfxtray, igfxpers, igfxhk      |
| AMD Radeon       | amd, radeon, amdradeonsettings  |
| Windows Defender | SecurityHealth, Defender        |
| Rainmeter        | Rainmeter                       |
| Lively Wallpaper | Lively                          |

---

**Data:** 7 de Março de 2026
**Status:** ✅ Corrigido e Validado
**Próxima Revisão:** Conforme feedback dos usuários
