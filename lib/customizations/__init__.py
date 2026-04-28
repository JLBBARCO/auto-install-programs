import os
import re
import sys
import winreg
try:
    from lib import log
except ModuleNotFoundError:
    from lib import log


def _resource_path(relative_path: str) -> str:
    """Return absolute path for data files, honoring PyInstaller bundles."""
    if os.path.isabs(relative_path):
        return relative_path

    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        if os.path.exists(os.path.join(project_root, relative_path)):
            base = project_root
        else:
            base = os.getcwd()
    return os.path.join(base, relative_path)


REG_PATHS = {
    "HKCU_RUN": (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
    "HKLM_RUN": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
    "HKLM_WOW64": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
}


APPROVED_PATHS = {
    "HKCU_RUN": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
    "HKLM_RUN": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
    "HKLM_WOW64": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run32",
}


LEGACY_WHITELIST_TERMS = {
    "onedrive": {"microsoftonedrive"},
    "nearby": {"nearbyshare"},
    "camo": {"camostudio"},
    "msedge": {"microsoftedgeautolaunch"},
    "nvidia": {"nvbackend", "nvcontainer", "nvidiageforceexperience", "nvidiaapp"},
    "nvinitialize": {"nvcontainer"},
    "igfxpers": {"persistence"},
    "igfxhk": {"hotkeyscmds"},
    "intelgraphics": {"intelgraphicscommandcenter"},
    "amd": {"radeonsoftware"},
    "radeon": {"radeonsoftware"},
    "lively": {"livelywpf"},
    "pcmanager": {"microsoftpcmanager"},
}


def _normalize_startup_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def _load_whitelist_terms(whitelist_path: str):
    resolved = _resource_path(whitelist_path)
    if not os.path.exists(resolved):
        raise FileNotFoundError(f"Whitelist not found: {resolved}")

    whitelist = set()
    with open(resolved, 'r', encoding='utf-8') as whitelist_file:
        for raw_line in whitelist_file:
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue

            normalized = _normalize_startup_name(line)
            if not normalized:
                continue

            whitelist.add(normalized)
            whitelist.update(LEGACY_WHITELIST_TERMS.get(normalized, set()))

    return whitelist, resolved


def _is_whitelisted(entry_name: str, whitelist_terms) -> bool:
    return _normalize_startup_name(entry_name) in whitelist_terms


def disable_startup_programs(whitelist_path="install/windows/white_list.txt"):
    """Disable startup entries that are not present in the local whitelist."""
    try:
        whitelist_terms, resolved = _load_whitelist_terms(whitelist_path)
    except Exception as error:
        return f"Startup disable aborted. {error}"

    if not whitelist_terms:
        return f"Startup disable aborted. Whitelist is empty: {resolved}"

    disabled_count = 0
    preserved_count = 0
    disabled_value = b'\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    for label, (root, path) in REG_PATHS.items():
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as run_key:
                entry_names = []
                index = 0
                while True:
                    try:
                        name, _, _ = winreg.EnumValue(run_key, index)
                        entry_names.append(name)
                        index += 1
                    except OSError:
                        break

                app_root = winreg.HKEY_CURRENT_USER if "HKCU" in label else winreg.HKEY_LOCAL_MACHINE
                app_path = APPROVED_PATHS[label]

                with winreg.CreateKey(app_root, app_path) as approved_key:
                    for name in entry_names:
                        if _is_whitelisted(name, whitelist_terms):
                            preserved_count += 1
                            log.log(f'Preserved startup entry [{label}]: {name}', level="INFO")
                            continue

                        winreg.SetValueEx(approved_key, name, 0, winreg.REG_BINARY, disabled_value)
                        log.log(f'Disabled startup entry [{label}]: {name}', level="INFO")
                        disabled_count += 1
        except Exception as error:
            log.log(f"Skipping {label}, key not found or inaccessible: {error}", level="INFO")

    return (
        f"Scan complete. {disabled_count} startup entries were disabled and "
        f"{preserved_count} whitelist entries were preserved from {resolved}."
    )


def save_startup_keys(output_path="programs.log"):
    """Save the current startup registry state for audit/debugging."""
    try:
        lines = []
        for label, (root, path) in REG_PATHS.items():
            try:
                with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as key:
                    count = winreg.QueryInfoKey(key)[1]
                    for index in range(count):
                        name, value, _ = winreg.EnumValue(key, index)
                        lines.append(f"{label}::{name}::{value}")
            except Exception:
                lines.append(f"{label}::(inaccessible)")

        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write("\n".join(lines))
        return f"Startup keys saved to {output_path}."
    except Exception as error:
        return f"Error saving keys: {error}"


def enable_startup_whitelist(whitelist_path="install/windows/white_list.txt"):
    try:
        whitelist_terms, resolved = _load_whitelist_terms(whitelist_path)
        if not whitelist_terms:
            return f"Whitelist is empty; nothing to re-enable: {resolved}"

        activated_count = 0
        enabled_value = b'\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

        for label, (root, path) in REG_PATHS.items():
            try:
                with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as run_key:
                    app_root = winreg.HKEY_CURRENT_USER if "HKCU" in label else winreg.HKEY_LOCAL_MACHINE
                    app_path = APPROVED_PATHS[label]

                    with winreg.CreateKey(app_root, app_path) as approved_key:
                        index = 0
                        while True:
                            try:
                                name, _, _ = winreg.EnumValue(run_key, index)
                                if _is_whitelisted(name, whitelist_terms):
                                    winreg.SetValueEx(approved_key, name, 0, winreg.REG_BINARY, enabled_value)
                                    log.log(f'Re-enabled from whitelist: {name}', level="INFO")
                                    activated_count += 1
                                index += 1
                            except OSError:
                                break
            except Exception:
                continue

        return f"Success: {activated_count} startup entries re-enabled from {resolved}."
    except Exception as error:
        return f"Error in whitelist: {error}"