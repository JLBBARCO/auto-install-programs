"""
Testes unitários e de integração para Programs Manager
Execute com: pytest test/test_modules.py -v
"""
import pytest
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# Testes do módulo system
# ============================================================================
class TestSystemModule:
    """Testes do módulo lib.system"""
    
    def test_nameso_returns_string(self):
        """Testa se nameSO retorna uma string"""
        from lib import system
        result = system.nameSO()
        assert isinstance(result, str), "nameSO deve retornar uma string"
        assert len(result) > 0, "nameSO não deve retornar string vazia"
    
    def test_nameso_valid_os(self):
        """Testa se nameSO retorna um SO válido"""
        from lib import system
        result = system.nameSO()
        valid_systems = ["Windows", "Linux", "Darwin", "macOS"]
        assert any(so in result for so in valid_systems), \
            f"SO retornado '{result}' não é válido"


# ============================================================================
# Testes do módulo log
# ============================================================================
class TestLogModule:
    """Testes do módulo lib.log"""
    
    def test_get_log_file_path_returns_string(self):
        """Testa se get_log_file_path retorna uma string"""
        from lib import log
        result = log.get_log_file_path()
        assert isinstance(result, str), "get_log_file_path deve retornar string"
        assert len(result) > 0, "Caminho do log não pode estar vazio"
    
    def test_log_function_doesnt_crash(self):
        """Testa se a função log não lança exceção"""
        from lib import log
        try:
            log.log("Teste de mensagem", level="INFO")
            log.log("Teste de aviso", level="WARNING")
            log.log("Teste de erro", level="ERROR")
            assert True, "Log executado sem erros"
        except Exception as e:
            pytest.fail(f"Log lançou exceção: {e}")


# ============================================================================
# Testes do módulo json
# ============================================================================
class TestJsonModule:
    """Testes do módulo lib.json"""
    
    def test_read_json_returns_dict(self):
        """Testa se read_json retorna um dicionário"""
        from lib import json as json_lib
        result = json_lib.read_json("essentials")
        # Pode ser vazio se arquivo não existe, mas deve ser dict
        assert isinstance(result, dict), "read_json deve retornar dicionário"
    
    def test_read_json_structure(self):
        """Testa estrutura do JSON lido"""
        from lib import json as json_lib
        result = json_lib.read_json("essentials")
        if result:  # Se arquivo existe
            # Deve ter a chave 'programs' ou estar vazio
            assert "programs" in result or result == {}, \
                "JSON deve ter 'programs' ou estar vazio"
    
    def test_get_log_file_path_returns_string(self):
        """Testa se o caminho do arquivo de log é válido"""
        from lib import log
        path = log.get_log_file_path()
        assert isinstance(path, str), "Caminho deve ser string"
        assert len(path) > 0, "Caminho não pode estar vazio"

    def test_user_data_file_path_windows_downloads_folder(self, monkeypatch):
        """Em Windows, user_install/user_uninstall devem ir para Downloads/Programs Manager."""
        import os
        from lib import json as json_lib

        monkeypatch.setattr(os.path, "expanduser", lambda _path: r"C:\Users\Reginaldo")

        target = json_lib._user_data_file_path("user_install")
        expected = os.path.join(r"C:\Users\Reginaldo", "Downloads", "Programs Manager", "user_install.json")
        assert target == expected

    def test_user_data_file_path_linux_downloads_folder(self, monkeypatch):
        """No Linux, user_install/user_uninstall devem ir para ~/Downloads/Programs Manager."""
        import os
        from lib import json as json_lib

        monkeypatch.setattr(os.path, "expanduser", lambda _path: "/home/reginaldo")

        target = json_lib._user_data_file_path("user_uninstall")
        expected = os.path.join("/home/reginaldo", "Downloads", "Programs Manager", "user_uninstall.json")
        assert target == expected

    def test_user_data_file_path_macos_downloads_folder(self, monkeypatch):
        """No macOS, user_install/user_uninstall devem ir para ~/Downloads/Programs Manager."""
        import os
        from lib import json as json_lib

        monkeypatch.setattr(os.path, "expanduser", lambda _path: "/Users/reginaldo")

        target = json_lib._user_data_file_path("user_install")
        expected = os.path.join("/Users/reginaldo", "Downloads", "Programs Manager", "user_install.json")
        assert target == expected

    def test_user_data_file_path_non_user_file_uses_default_resource_path(self, monkeypatch):
        """Arquivos fora de user_install/user_uninstall mantêm comportamento padrão."""
        from lib import json as json_lib

        monkeypatch.setattr(json_lib, "_resource_path", lambda rel: f"BASE/{rel}")

        target = json_lib._user_data_file_path("essentials")
        assert target == "BASE/essentials.json"


# ============================================================================
# Testes do módulo customizations
# ============================================================================
class TestCustomizationsModule:
    """Testes do módulo lib.customizations"""
    
    def test_normalize_startup_name_function_exists(self):
        """Testa se a função _normalize_startup_name existe e é chamável"""
        from lib import customizations
        assert hasattr(customizations, '_normalize_startup_name'), \
            "Função _normalize_startup_name deve existir"
        assert callable(customizations._normalize_startup_name), \
            "_normalize_startup_name deve ser callable"
    
    def test_normalize_startup_name_returns_string(self):
        """Testa se _normalize_startup_name retorna uma string normalizada"""
        from lib import customizations
        result = customizations._normalize_startup_name("Test Program Name")
        assert isinstance(result, str), "_normalize_startup_name deve retornar string"
        assert len(result) > 0, "String normalizada não pode estar vazia"


# ============================================================================
# Testes do módulo install.single_instance
# ============================================================================
class TestSingleInstanceModule:
    """Testes do módulo lib.install.single_instance"""
    
    def test_module_imports_successfully(self):
        """Testa se o módulo de single_instance importa sem erros"""
        try:
            from lib.install import single_instance
            assert hasattr(single_instance, 'acquire_installation_lock'), \
                "Função acquire_installation_lock não encontrada"
            assert hasattr(single_instance, 'release_installation_lock'), \
                "Função release_installation_lock não encontrada"
            assert hasattr(single_instance, 'is_installation_cancelled'), \
                "Função is_installation_cancelled não encontrada"
        except ImportError as e:
            pytest.fail(f"Falha ao importar single_instance: {e}")


# ============================================================================
# Testes de Integração
# ============================================================================
class TestIntegration:
    """Testes de integração entre módulos"""
    
    @pytest.mark.integration
    def test_all_modules_import(self):
        """Testa se todos os módulos principais importam sem erros"""
        modules = [
            "lib.system",
            "lib.json",
            "lib.log",
            "lib.customizations",
            "lib.install.single_instance",
        ]
        
        for module_name in modules:
            try:
                __import__(module_name)
            except ImportError as e:
                pytest.fail(f"Falha ao importar {module_name}: {e}")
    
    @pytest.mark.integration
    def test_system_and_log_integration(self):
        """Testa integração entre system e log"""
        from lib import system, log
        
        so_name = system.nameSO()
        log.log(f"Sistema detectado: {so_name}")
        
        # Se chegou aqui sem erro, está funcionando
        assert so_name is not None, "SO não foi detectado"

    def test_run_pipeline_order(self, monkeypatch):
        """Testa se a ordem do Run segue update -> uninstall -> install -> categorias."""
        from main import App
        from types import SimpleNamespace
        from lib import install as install_module
        from lib import uninstall as uninstall_module
        from lib.install import single_instance
        from lib import log

        events: list[str] = []

        def record(event_name: str):
            events.append(event_name)

        class DummyApp:
            def _start_log_bridge(self):
                record("bridge")

            def _selected_installations(self):
                def run_category(selected_programs):
                    record(f"category:{selected_programs[0]['id']}")

                return [
                    (SimpleNamespace(key="essentials"), run_category),
                ]

        monkeypatch.setattr(install_module, "update", lambda: record("update"))
        monkeypatch.setattr(uninstall_module, "user", lambda entries=None: record(f"uninstall:{len(entries or [])}"))
        monkeypatch.setattr(install_module, "user", lambda entries=None: record(f"install:{len(entries or [])}"))
        monkeypatch.setattr(single_instance, "is_installation_cancelled", lambda: False)
        monkeypatch.setattr(log, "log", lambda *args, **kwargs: None)
        monkeypatch.setattr("main.time.sleep", lambda _seconds: None)

        App._run_selected_installations(
            DummyApp(),
            {
                "user_uninstall": [{"name": "Remove Me", "id": "remove.me"}],
                "user_install": [{"name": "Add Me", "id": "add.me"}],
                "essentials": [{"name": "Core App", "id": "core.app"}],
            },
        )

        assert events == [
            "bridge",
            "update",
            "uninstall:1",
            "install:1",
            "category:core.app",
        ]


# ============================================================================
# Fixtures para testes
# ============================================================================
@pytest.fixture
def system_name():
    """Fixture que fornece o nome do sistema"""
    from lib import system
    return system.nameSO()


@pytest.fixture
def log_file_path():
    """Fixture que fornece o caminho do arquivo de log"""
    from lib import log
    return log.get_log_file_path()


# ============================================================================
# Testes parametrizados
# ============================================================================
class TestParametrized:
    """Testes parametrizados para validar múltiplos inputs"""
    
    @pytest.mark.parametrize("level", ["INFO", "WARNING", "ERROR", "DEBUG"])
    def test_log_with_different_levels(self, level):
        """Testa log com diferentes níveis"""
        from lib import log
        try:
            log.log(f"Teste com nível {level}", level=level)
            assert True, f"Log com nível {level} executado com sucesso"
        except Exception as e:
            pytest.fail(f"Log falhou com nível {level}: {e}")


# ============================================================================
# Testes com markers
# ============================================================================
class TestMarkers:
    """Testes com markers customizados"""
    
    @pytest.mark.slow
    def test_slow_operation(self):
        """Teste que leva tempo para executar"""
        import time
        time.sleep(0.1)  # Simula operação lenta
        assert True
    
    @pytest.mark.unit
    def test_unit_operation(self):
        """Teste unitário rápido"""
        from lib import system
        assert system.nameSO() is not None
