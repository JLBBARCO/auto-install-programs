import subprocess, os, re, sys, ctypes, winreg, urllib.request
from pathlib import Path
from lib import system, log, json
from .bios_shortcur import bios_shortcut
from .dark_mode import dark_mode
from .finalize_notifications import finalize_notification
from .vision_cursor_black import vision_cursor_black
from .video_drivers import video_drivers


REG_PATHS = {
    "HKEY_CURRENT_USER": (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
    "HKEY_LOCAL_MACHINE (32-bit)": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
    "HKEY_LOCAL_MACHINE (64-bit/WOW64)": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
}
APPROVED_PATHS = {
    "HKEY_CURRENT_USER": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
    "HKEY_LOCAL_MACHINE (32-bit)": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
    "HKEY_LOCAL_MACHINE (64-bit/WOW64)": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run32",
}
LEGACY_WHITELIST_TERMS = {
    'microsoftonedrive': {'onedrive'},
    'microsoftedgeautolaunch': {'msedge'},
    'microsoftpcmanager': {'microsoftpcmanager'},
    'nvidiageforceexperience': {'nvidia'},
    'nvcontainer': {'nvidia'},
    'nvbackend': {'nvidia'},
    'nvinitialize': {'nvidia'},
    'igfxtray': {'intelgraphics'},
    'igfxpers': {'intelgraphics'},
    'igfxhk': {'intelgraphics'},
    'hotkeyscmds': {'intelgraphics'},
    'persistence': {'intelgraphics'},
    'radeonsoftware': {'radeon'},
    'livelywpf': {'lively'},
    'camostudio': {'camo'},
}


def _normalize_startup_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def _load_whitelist_terms(whitelist_content=None):
    """Parse whitelist content and return set of normalized terms."""
    if whitelist_content is None:
        whitelist_content = json.read_external_json('initialization_whitelist')

    if not whitelist_content:
        return set()

    if isinstance(whitelist_content, dict):
        entries = (
            whitelist_content.get('data')
            or whitelist_content.get('whitelist')
            or whitelist_content.get('items')
            or []
        )
    elif isinstance(whitelist_content, (list, tuple, set)):
        entries = whitelist_content
    else:
        entries = str(whitelist_content).splitlines()

    whitelist = set()
    for raw_line in entries:
        line = str(raw_line).strip()
        if not line or line.startswith('#'):
            continue

        normalized = _normalize_startup_name(line)
        if not normalized:
            continue

        whitelist.add(normalized)
        whitelist.update(LEGACY_WHITELIST_TERMS.get(normalized, set()))

    return whitelist


def _is_whitelisted(entry_name: str, whitelist_terms) -> bool:
    return _normalize_startup_name(entry_name) in whitelist_terms


def disable_startup_programs():
    """Disable startup entries that are not present in the GitHub whitelist."""
    try:
        whitelist_terms = _load_whitelist_terms()
    except Exception as error:
        return f"Startup disable aborted. Failed to load initialization whitelist: {error}"

    if not whitelist_terms:
        return "Startup disable aborted. Whitelist is empty."

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
        f"{preserved_count} whitelist entries were preserved."
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


def enable_startup_whitelist():
    """Re-enable whitelisted startup entries from GitHub."""
    try:
        whitelist_terms = _load_whitelist_terms()
    except Exception as error:
        return f"Whitelist re-enable failed. Error: {error}"

    if not whitelist_terms:
        return "Whitelist is empty; nothing to re-enable."

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

    return f"Success: {activated_count} startup entries re-enabled from whitelist."


def essentials_programs_whitelist():
    pass


def _filter_install_output(output: str) -> str:
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    clean = ansi_escape.sub('', output)
    lines = clean.splitlines()
    kept_lines = []
    removed_count = 0
    progress_re = re.compile(r'\b\d{1,3}%\b')

    for line in lines:
        if progress_re.search(line) and len(line.strip()) < 120:
            removed_count += 1
            continue
        if len(line.strip()) > 0 and set(line.strip()) <= set('.-') and len(line.strip()) < 40:
            removed_count += 1
            continue
        kept_lines.append(line)

    if removed_count:
        kept_lines.append(f"[{removed_count} progress updates suppressed]")

    return "\n".join(kept_lines).strip()


def _restart_windows_explorer() -> None:
    if system.nameSO() != 'Windows':
        return

    try:
        subprocess.run(
            ["taskkill", "/f", "/im", "explorer.exe"],
            capture_output=True,
            text=True,
            shell=False,
        )
    except Exception:
        pass

    try:
        subprocess.Popen(
            ["explorer.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False,
        )
        log.log('Windows Explorer restarted to apply system changes.', 'INFO')
    except Exception as error:
        log.log(f'Failed to restart Windows Explorer: {error}', 'ERROR')


def _normalize_function_name(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', '', value.casefold())


def _resolve_function(func_name: str):
    direct_function = globals().get(func_name)
    if callable(direct_function):
        return direct_function

    normalized_name = _normalize_function_name(func_name)
    if not normalized_name:
        return None

    for name, candidate in globals().items():
        if callable(candidate) and _normalize_function_name(name) == normalized_name:
            return candidate

    return None


def functions(functions_list):
    try:
        for item in functions_list:
            func_name = item.get('id') if isinstance(item, dict) else item
            if not func_name:
                continue

            display_name = item.get('name', func_name) if isinstance(item, dict) else func_name

            func = _resolve_function(func_name)
            if callable(func):
                func()
                log.log(f"Executed function: {display_name}", 'INFO')
            else:
                log.log(f"Function not found: {display_name} ({func_name})", 'WARNING')
        _restart_windows_explorer()
    except Exception as error:
        log.log(f"Error executing functions: {error}", 'ERROR')

