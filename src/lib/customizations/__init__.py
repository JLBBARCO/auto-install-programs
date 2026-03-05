from src.lib.externalLibs import sys, os, winreg
from src.lib import log


def _resource_path(relative_path: str) -> str:
    """Return absolute path for data files, honoring PyInstaller bundles.

    This duplicates the helper from ``installations`` to avoid a circular
    dependency; the behaviour must remain identical between modules.
    """
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = os.getcwd()
    return os.path.join(base, relative_path)

# Caminhos expandidos para cobrir programas de terceiros (Machine e User)
REG_PATHS = {
    "HKCU_RUN": (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
    "HKLM_RUN": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
    "HKLM_WOW64": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run")
}

# Caminhos correspondentes onde o Windows guarda o status de "Aprovado/Desativado"
APPROVED_PATHS = {
    "HKCU_RUN": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
    "HKLM_RUN": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
    "HKLM_WOW64": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run32" # Note o Run32 para WOW64
}

def dark_mode():
    keyPath = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, keyPath, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, 0)
        return "Dark mode applied successfully."
    except Exception as error:
        return f"Failed to apply dark mode. Error: {error}"

def disable_startup_programs():
    """Varre chaves de usuário e máquina para desativar programas de terceiros."""
    disabled_count = 0
    # Valor binário que o Windows usa para "Desativado" no Gerenciador de Tarefas
    # O prefixo \x03 indica desativação manual pelo usuário
    disabled_value = b'\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    for label, (root, path) in REG_PATHS.items():
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as run_key:
                # Coleta os nomes de todas as entradas primeiro
                entry_names = []
                i = 0
                while True:
                    try:
                        name, _, _ = winreg.EnumValue(run_key, i)
                        entry_names.append(name)
                        i += 1
                    except OSError:
                        break
                
                # Tenta abrir a chave de aprovação correspondente (HKCU ou HKLM)
                app_root = winreg.HKEY_CURRENT_USER if "HKCU" in label else winreg.HKEY_LOCAL_MACHINE
                app_path = APPROVED_PATHS[label]
                
                try:
                    with winreg.OpenKey(app_root, app_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_READ) as approved_key:
                        for name in entry_names:
                            winreg.SetValueEx(approved_key, name, 0, winreg.REG_BINARY, disabled_value)
                            log.log(f'Disabled startup entry [{label}]: {name}', level="INFO")
                            disabled_count += 1
                except Exception as e:
                    log.log(f"Could not access Approved key for {label}: {e}", level="WARNING")
        except Exception as e:
            log.log(f"Skipping {label}, key not found or inaccessible: {e}", level="INFO")

    return f"Scan complete. {disabled_count} third-party startup entries were set to disabled."

def save_startup_keys(output_path="programs.log"):
    """Salva o estado de todas as chaves de inicialização monitoradas."""
    try:
        lines = []
        for label, (root, path) in REG_PATHS.items():
            try:
                with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as key:
                    count = winreg.QueryInfoKey(key)[1]
                    for i in range(count):
                        name, value, _ = winreg.EnumValue(key, i)
                        lines.append(f"{label}::{name}::{value}")
            except Exception:
                lines.append(f"{label}::(inaccessible)")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        return f"Startup keys saved to {output_path}."
    except Exception as e:
        return f"Error saving keys: {e}"

def enable_startup_whitelist(whitelist_path="install/white_list.txt"):
    # When running from a bundled executable the whitelist may live inside the
    # PyInstaller temporary folder.  Resolve the real path first so we can
    # actually open the file.
    # resolve the path through our helper so that the file is reachable when
    # the app is frozen and the whitelist lives inside the bundle.
    whitelist_path = _resource_path(whitelist_path)

    if not os.path.exists(whitelist_path):
        return f"Whitelist não encontrada: {whitelist_path}"

    try:
        with open(whitelist_path, 'r', encoding='utf-8') as f:
            # Lê a lista e limpa espaços
            whitelist = [line.strip().lower() for line in f if line.strip()]
        
        activated_count = 0
        enabled_value = b'\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

        for label, (root, path) in REG_PATHS.items():
            try:
                with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as run_key:
                    app_root = winreg.HKEY_CURRENT_USER if "HKCU" in label else winreg.HKEY_LOCAL_MACHINE
                    app_path = APPROVED_PATHS[label]
                    
                    with winreg.OpenKey(app_root, app_path, 0, winreg.KEY_SET_VALUE) as app_key:
                        i = 0
                        while True:
                            try:
                                name, _, _ = winreg.EnumValue(run_key, i)
                                # BUSCA PARCIAL: Verifica se o nome no registo contém algum termo da whitelist
                                if any(term in name.lower() for term in whitelist):
                                    winreg.SetValueEx(app_key, name, 0, winreg.REG_BINARY, enabled_value)
                                    log.log(f'Reativado da whitelist: {name}', level="INFO")
                                    activated_count += 1
                                i += 1
                            except OSError:
                                break
            except Exception:
                continue
        return f"Sucesso: {activated_count} programas reativados."
    except Exception as e:
        return f"Erro na whitelist: {e}"