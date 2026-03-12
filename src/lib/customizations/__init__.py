import sys, os
import subprocess
import urllib.request
import winreg
try:
    from src.lib import log
except ModuleNotFoundError:
    from lib import log


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


def disable_mouse_precision():
    key_path = r"Control Panel\Mouse"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "MouseSpeed", 0, winreg.REG_SZ, "0")
            winreg.SetValueEx(key, "MouseThreshold1", 0, winreg.REG_SZ, "0")
            winreg.SetValueEx(key, "MouseThreshold2", 0, winreg.REG_SZ, "0")

        subprocess.run("rundll32 user32.dll,UpdatePerUserSystemParameters", shell=True, capture_output=True, text=True)
        return "Mouse precision (Enhance pointer precision) disabled successfully."
    except Exception as error:
        return f"Failed to disable mouse precision. Error: {error}"


def configure_power_behavior():
    """Apply AC/DC behavior:
    - On battery: best energy efficiency
    - Plugged in: best performance
    - Battery saver starts immediately when unplugged
    """
    commands = [
        # CPU policy tuned for efficiency on battery and performance on AC.
        "powercfg /setdcvalueindex scheme_current SUB_PROCESSOR PROCTHROTTLEMAX 50",
        "powercfg /setdcvalueindex scheme_current SUB_PROCESSOR PROCTHROTTLEMIN 5",
        "powercfg /setacvalueindex scheme_current SUB_PROCESSOR PROCTHROTTLEMAX 100",
        "powercfg /setacvalueindex scheme_current SUB_PROCESSOR PROCTHROTTLEMIN 100",
        # Start battery saver as soon as device disconnects from AC.
        "powercfg /setdcvalueindex scheme_current SUB_ENERGYSAVER ESBATTTHRESHOLD 100",
        "powercfg /setactive scheme_current",
    ]

    errors = []
    for command in commands:
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        if process.returncode != 0:
            error_output = (process.stdout or "") + ("\n" + process.stderr if process.stderr else "")
            errors.append(f"{command} -> {error_output.strip()}")

    if errors:
        return "Power behavior applied with warnings: " + " | ".join(errors)
    return "Power behavior configured: battery=best efficiency, plugged=best performance, battery saver at unplug."

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

def enable_startup_whitelist(whitelist_path="install/windows/white_list.txt"):
    try:
        whitelist = []
        if str(whitelist_path).startswith(('http://', 'https://')):
            try:
                with urllib.request.urlopen(whitelist_path, timeout=15) as response:
                    text = response.read().decode('utf-8', errors='ignore')
                    whitelist = [line.strip().lower() for line in text.splitlines() if line.strip()]
                log.log(f"Whitelist loaded from remote source: {whitelist_path}", level="INFO")
            except Exception as remote_error:
                log.log(f"Failed to load remote whitelist ({whitelist_path}): {remote_error}", level="WARNING")
                fallback_candidates = [
                    "install/windows/white_list.txt",
                    "white_list.txt",
                ]
                for fallback in fallback_candidates:
                    resolved = _resource_path(fallback)
                    if not os.path.exists(resolved):
                        continue
                    with open(resolved, 'r', encoding='utf-8') as f:
                        whitelist = [line.strip().lower() for line in f if line.strip()]
                    log.log(f"Whitelist loaded from local fallback: {resolved}", level="INFO")
                    break
        else:
            # When running from a bundled executable the whitelist may live inside
            # the PyInstaller temporary folder.
            resolved = _resource_path(whitelist_path)
            if not os.path.exists(resolved):
                return f"Whitelist not found: {resolved}"
            with open(resolved, 'r', encoding='utf-8') as f:
                whitelist = [line.strip().lower() for line in f if line.strip()]

        if not whitelist:
            return "Whitelist is empty; nothing to re-enable."
        
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
                                    log.log(f'Re-enabled from whitelist: {name}', level="INFO")
                                    activated_count += 1
                                i += 1
                            except OSError:
                                break
            except Exception:
                continue
        return f"Success: {activated_count} programs re-enabled."
    except Exception as e:
        return f"Error in whitelist: {e}"