# 📋 Exemplos de Saída do Sistema de Testes

## Exemplo 1: Execução no Windows (PowerShell)

```powershell
PS C:\Users\user\Downloads\programs-manager> .\test\run_tests.ps1

╔════════════════════════════════════════════════════════════════╗
║     Programs Manager - Sistema Automático de Testes           ║
╚════════════════════════════════════════════════════════════════╝

[*] Testando disponibilidade do Python...
[OK] Python 3.12.10 encontrado

[*] Executando testes automáticos...

[*] Iniciando testes do Programs Manager...

[OK] Testes concluídos!
  Total: 21
  Passou: 4
  Falhou: 0
  Pulado: 17

[OK] Relatórios gerados:
  Texto: test\test_report.txt
  JSON:  test\test_report.json
  HTML:  test\test_report.html
```

---

## Exemplo 2: Execução no Linux/macOS (Bash)

```bash
$ bash test/run_tests.sh

╔════════════════════════════════════════════════════════════════╗
║     Programs Manager - Sistema Automático de Testes           ║
╚════════════════════════════════════════════════════════════════╝

[*] Testando disponibilidade do Python...
[OK] Python 3.12.10 encontrado

[*] Executando testes automáticos...

[*] Iniciando testes do Programs Manager...

[OK] Testes concluídos!
  Total: 21
  Passou: 4
  Falhou: 0
  Pulado: 17

[OK] Relatórios gerados:
  Texto: test/test_report.txt
  JSON:  test/test_report.json
  HTML:  test/test_report.html
```

---

## Exemplo 3: Relatório em Texto Completo

```
================================================================================
RELATÓRIO DE TESTES - PROGRAMS MANAGER
================================================================================

Data: 2026-05-02 17:23:15
Duração: 0.22 segundos

RESUMO:
-------
Total de testes: 21
✓ Passou: 4
✗ Falhou: 0
⊘ Pulado: 17
Taxa de sucesso: 19.0%

================================================================================
DETALHES DOS TESTES:
================================================================================

✓ PASSED:
--------------------------------------------------------------------------------

  Módulo: lib.system
  Função: nameSO
  Mensagem: Sistema operacional detectado: Windows


  Módulo: lib.json
  Função: read_json
  Mensagem: JSON lido com sucesso. Keys: ['name', 'description', 'programs']


  Módulo: lib.log
  Função: get_log_file_path
  Mensagem: Caminho do log: C:\Users\user\Downloads\programs-manager\log.log


  Módulo: lib.customizations
  Função: _normalize_startup_name
  Mensagem: Nome normalizado: testprogram


⊘ SKIPPED:
--------------------------------------------------------------------------------

  Módulo: lib.json
  Função: write_json
  Mensagem: Função requer argumentos específicos ou interação do sistema

  [... mais 16 testes pulados ...]

================================================================================
FIM DO RELATÓRIO
================================================================================
```

---

## Exemplo 4: Relatório em JSON (Amostra)

```json
{
  "timestamp": "2026-05-02T17:23:15.861331",
  "duration_seconds": 0.216699,
  "summary": {
    "total": 21,
    "passed": 4,
    "failed": 0,
    "skipped": 17,
    "success_rate": 19.047619047619047
  },
  "results": [
    {
      "module": "lib.system",
      "function": "nameSO",
      "status": "PASSED",
      "error": null,
      "message": "Sistema operacional detectado: Windows",
      "timestamp": "2026-05-02T17:23:15.644632"
    },
    {
      "module": "lib.json",
      "function": "read_json",
      "status": "PASSED",
      "error": null,
      "message": "JSON lido com sucesso. Keys: ['name', 'description', 'programs']",
      "timestamp": "2026-05-02T17:23:15.711172"
    },
    {
      "module": "lib.json",
      "function": "write_json",
      "status": "SKIPPED",
      "error": null,
      "message": "Função requer argumentos específicos ou interação do sistema",
      "timestamp": "2026-05-02T17:23:15.711172"
    }
  ]
}
```

---

## Exemplo 5: Execução com Pytest

```bash
$ pytest test/test_modules.py -v

============================= test session starts ==============================
platform win32 -- Python 3.12.10, pytest-7.x.x, ...
plugins: ...
collected 15 items

test/test_modules.py::TestSystemModule::test_nameso_returns_string PASSED [ 6%]
test/test_modules.py::TestSystemModule::test_nameso_valid_os PASSED     [13%]
test/test_modules.py::TestLogModule::test_get_log_file_path_returns_string PASSED [20%]
test/test_modules.py::TestLogModule::test_log_function_doesnt_crash PASSED [26%]
test/test_modules.py::TestJsonModule::test_read_json_returns_dict PASSED [33%]
test/test_modules.py::TestJsonModule::test_read_json_structure PASSED  [40%]
test/test_modules.py::TestCustomizationsModule::test_normalize_startup_name_function_exists PASSED [46%]
test/test_modules.py::TestCustomizationsModule::test_normalize_startup_name_returns_string PASSED [53%]
test/test_modules.py::TestSingleInstanceModule::test_module_imports_successfully PASSED [60%]
test/test_modules.py::TestIntegration::test_all_modules_import PASSED   [66%]
test/test_modules.py::TestIntegration::test_system_and_log_integration PASSED [73%]
test/test_modules.py::TestParametrized::test_log_with_different_levels[INFO] PASSED [80%]
test/test_modules.py::TestParametrized::test_log_with_different_levels[WARNING] PASSED [86%]
test/test_modules.py::TestParametrized::test_log_with_different_levels[ERROR] PASSED [93%]
test/test_modules.py::TestParametrized::test_log_with_different_levels[DEBUG] PASSED [100%]

============================== 15 passed in 0.23s ==============================
```

---

## Exemplo 6: Abrir Relatório HTML

O arquivo `test_report.html` pode ser aberto em qualquer navegador:

```
1. Windows:
   - Duplo clique em test\test_report.html
   - Ou: .\test\run_tests.ps1 report

2. Linux/macOS:
   - open test/test_report.html
   - firefox test/test_report.html
   - google-chrome test/test_report.html
```

### Visualização esperada:

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  🧪 Relatório de Testes                            │
│  Programs Manager - Sistema Automático de Testes   │
│  2026-05-02T17:23:15                               │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┬──────────────┬──────────────┐    │
│  │ Total de     │ ✓ Passou     │ ✗ Falhou     │    │
│  │ Testes       │              │              │    │
│  │    21        │      4       │      0       │    │
│  └──────────────┴──────────────┴──────────────┘    │
│                                                     │
│  Taxa de Sucesso: 19.0%                            │
│                                                     │
├─────────────────────────────────────────────────────┤
│  ✓ PASSED (4 testes)                               │
│  ├─ lib.system.nameSO                              │
│  ├─ lib.json.read_json                             │
│  ├─ lib.log.get_log_file_path                      │
│  └─ lib.customizations._normalize_startup_name     │
│                                                     │
│  ⊘ SKIPPED (17 testes)                             │
│  ├─ lib.json.write_json                            │
│  ├─ lib.json.append_programs                       │
│  └─ [... mais 15 ...]                              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Exemplo 7: Adicionar Novo Teste

### Antes (estado atual):

```python
modules_to_test = [
    ("lib.system", ["nameSO"]),
    ("lib.json", ["read_json", ...]),
    # ...
]
```

### Depois (com novo módulo):

```python
modules_to_test = [
    ("lib.system", ["nameSO"]),
    ("lib.json", ["read_json", ...]),
    ("lib.meu_novo_modulo", ["funcao1", "funcao2"]),  # ← Adicionado
    # ...
]
```

### Resultado na próxima execução:

```
Total de testes: 23  (era 21)
Passou: 5+        (pode aumentar)
Pulado: 18+       (pode aumentar)
```

---

## Exemplo 8: Erro em um Teste

Se um teste falhar, o relatório mostra:

```
✗ FAILED:
  Módulo: lib.json
  Função: read_json
  Erro: FileNotFoundError: essentials.json not found

  Stack Trace:
  Traceback (most recent call last):
    File "test/run_tests.py", line 87, in test_function
      output = func()
    File "lib/json/__init__.py", line 45, in read_json
      with open(filepath) as f:
  FileNotFoundError: essentials.json not found
```

---

## Dicas de Uso

### 1. **Acompanhar progresso em tempo real**

```bash
# Terminal deixado aberto durante execução
watch -n 5 "cat test/test_report.txt"
```

### 2. **Compartilhar resultados**

```bash
# Copiar relatório para compartilhar
cp test/test_report.html ~/Desktop/results.html
```

### 3. **Automatizar com CI/CD**

```yaml
- name: Run Tests
  run: python test/run_tests.py

- name: Upload Report
  uses: actions/upload-artifact@v4
  with:
    name: test-report
    path: test/test_report.*
```

### 4. **Filtrar apenas testes que falharam**

```bash
# Usando grep
grep "✗ FAILED" test/test_report.txt

# Usando jq (para JSON)
cat test/test_report.json | jq '.results[] | select(.status=="FAILED")'
```

---

**Sistema de testes completo e pronto para usar! 🚀**
